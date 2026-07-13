# core/url_validator.py
# DeepAiUG - Validatore URL per connessioni di rete (SSRF awareness)
# ============================================================================
# Modulo isolato: classifica un URL in base a dove risolve l'host.
# NON è ancora agganciato a nessun call site (create_client, adapter wiki, …).
#
# Categorie:
#   loopback   → 127.0.0.0/8, ::1 (macchina locale)
#   private    → 10/8, 172.16/12, 192.168/16 (rete locale)
#   link_local → 169.254.0.0/16 (endpoint metadati cloud — UNICA categoria bloccata)
#   public     → qualsiasi IP pubblico
#   invalid    → URL malformato, schema non http/https, host non risolvibile
# ============================================================================

import socket
import ipaddress
from urllib.parse import urlparse
from typing import Dict, Any, Tuple

ALLOWED_SCHEMES = ("http", "https")

# RFC 6598 — Carrier-Grade NAT, usato da Tailscale e altre VPN mesh.
# ipaddress non lo marca né is_private né is_global: senza questo check
# finirebbe erroneamente in "public".
CGNAT_NET = ipaddress.ip_network("100.64.0.0/10")


def classify_url(url: str) -> Dict[str, Any]:
    """
    Classifica un URL in base all'IP a cui risolve l'hostname.

    Non solleva mai eccezioni: qualsiasi errore imprevisto degrada in
    category "invalid" (un validatore che crasha bloccherebbe l'app).

    Args:
        url: URL da classificare (es. "http://192.168.1.10:11434/v1")

    Returns:
        Dizionario con:
        - category: "loopback" | "private" | "link_local" | "public" | "invalid"
        - hostname: host estratto dall'URL ("" se non estraibile)
        - resolved_ip: IP risolto, None se non risolvibile
        - reason: spiegazione breve leggibile
    """
    try:
        parsed = urlparse(url if isinstance(url, str) else "")
        hostname = parsed.hostname or ""

        if parsed.scheme not in ALLOWED_SCHEMES:
            return {
                "category": "invalid",
                "hostname": hostname,
                "resolved_ip": None,
                "reason": f"Schema '{parsed.scheme or '(nessuno)'}' non supportato: usa http o https",
            }

        if not hostname:
            return {
                "category": "invalid",
                "hostname": "",
                "resolved_ip": None,
                "reason": "Hostname mancante nell'URL",
            }

        try:
            resolved_ip = socket.gethostbyname(hostname)
        except (socket.gaierror, OSError) as e:
            return {
                "category": "invalid",
                "hostname": hostname,
                "resolved_ip": None,
                "reason": f"Impossibile risolvere '{hostname}': {e}",
            }

        ip = ipaddress.ip_address(resolved_ip)

        # Ordine importante: loopback e link_local PRIMA di private
        # (per ipaddress questi range risultano anche is_private)
        if ip.is_loopback:
            category = "loopback"
            reason = f"'{hostname}' risolve a {resolved_ip} (loopback, macchina locale)"
        elif ip.is_link_local:
            category = "link_local"
            reason = (
                f"'{hostname}' risolve a {resolved_ip} (link-local 169.254.0.0/16, "
                "range degli endpoint metadati cloud)"
            )
        elif ip in CGNAT_NET or ip.is_private:
            category = "private"
            if ip in CGNAT_NET:
                reason = (
                    f"'{hostname}' risolve a {resolved_ip} "
                    "(CGNAT/VPN mesh 100.64.0.0/10, es. Tailscale)"
                )
            else:
                reason = f"'{hostname}' risolve a {resolved_ip} (rete privata locale)"
        else:
            category = "public"
            reason = f"'{hostname}' risolve a {resolved_ip} (internet pubblico)"

        return {
            "category": category,
            "hostname": hostname,
            "resolved_ip": resolved_ip,
            "reason": reason,
        }

    except Exception as e:
        return {
            "category": "invalid",
            "hostname": "",
            "resolved_ip": None,
            "reason": f"Errore imprevisto durante la validazione: {e}",
        }


def is_blocked(url: str) -> Tuple[bool, str]:
    """
    Determina se un URL va bloccato.

    Blocca SOLO la categoria "link_local" (endpoint metadati cloud,
    es. 169.254.169.254). Loopback, private e public restano permessi:
    l'app supporta legittimamente Ollama locale e server in LAN.

    Args:
        url: URL da verificare

    Returns:
        (True, motivo) se bloccato, altrimenti (False, "")
    """
    result = classify_url(url)
    if result["category"] == "link_local":
        return True, f"URL bloccato: {result['reason']}"
    return False, ""


# ============================================================================
# Test rapidi: python core/url_validator.py
# ============================================================================

if __name__ == "__main__":
    r = classify_url("http://localhost:11434/v1")
    assert r["category"] == "loopback", f"localhost doveva essere loopback, ottenuto: {r}"

    r = classify_url("http://127.0.0.1:11434")
    assert r["category"] == "loopback", f"127.0.0.1 doveva essere loopback, ottenuto: {r}"

    r = classify_url("http://192.168.1.50:11434")
    assert r["category"] == "private", f"192.168.1.50 doveva essere private, ottenuto: {r}"

    r = classify_url("http://10.0.0.5")
    assert r["category"] == "private", f"10.0.0.5 doveva essere private, ottenuto: {r}"

    r = classify_url("http://100.64.0.5:11434/v1")
    assert r["category"] == "private", f"100.64.0.5 (CGNAT) doveva essere private, ottenuto: {r}"

    r = classify_url("http://100.100.100.100:11434")
    assert r["category"] == "private", f"100.100.100.100 (CGNAT) doveva essere private, ottenuto: {r}"

    r = classify_url("http://8.8.8.8")
    assert r["category"] == "public", f"8.8.8.8 doveva essere public, ottenuto: {r}"

    r = classify_url("http://169.254.169.254/latest/meta-data")
    assert r["category"] == "link_local", f"169.254.169.254 doveva essere link_local, ottenuto: {r}"
    blocked, motivo = is_blocked("http://169.254.169.254/latest/meta-data")
    assert blocked is True, f"169.254.169.254 doveva essere bloccato, motivo: '{motivo}'"
    assert motivo, "il motivo del blocco non deve essere vuoto"

    r = classify_url("https://api.openai.com/v1")
    assert r["category"] == "public", f"api.openai.com doveva essere public, ottenuto: {r}"

    r = classify_url("not-a-url")
    assert r["category"] == "invalid", f"'not-a-url' doveva essere invalid, ottenuto: {r}"

    r = classify_url("ftp://x")
    assert r["category"] == "invalid", f"'ftp://x' doveva essere invalid (schema non http/https), ottenuto: {r}"

    # Extra: input non-stringa e URL bloccato vs permesso non devono crashare
    r = classify_url(None)
    assert r["category"] == "invalid", f"None doveva essere invalid, ottenuto: {r}"
    assert is_blocked("http://localhost:11434/v1") == (False, ""), "loopback NON va bloccato"
    assert is_blocked("http://192.168.1.50:11434") == (False, ""), "private NON va bloccato"

    print("tutti i test OK")
