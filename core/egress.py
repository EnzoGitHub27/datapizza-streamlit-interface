# core/egress.py
# DeepAiUG v1.16.0 (giro 3, P2) - Dove va davvero il testo
# ============================================================================
# Una regola sola, per i blocchi di KB, KB Chat, upload e immagini (e, dal
# giro 4, per il guard di rizzo-pii): conta la destinazione reale, non
# l'etichetta di `connection_type`.
#
#   Cloud provider OpenAI / Anthropic / Google  → fuori casa, sempre
#   tutto il resto: classify_url(base_url)
#       loopback, private (LAN, Tailscale)      → in casa
#       public, link_local, invalid             → fuori casa (nel dubbio, si blocca)
#
# Quindi un Remote host su IP pubblico conta come il cloud, e un cloud
# «Custom» su localhost (es. LM Studio) come in casa. Vedi SPEC §3.1.
# ============================================================================

from typing import Any, Dict, Optional

from .url_validator import classify_url

# Gli stessi di app.py (H1c) e di create_client: i client cloud a URL fisso
FIXED_CLOUD_PROVIDERS = ("OpenAI", "Anthropic (Claude)", "Google Gemini")

INSIDE_CATEGORIES = ("loopback", "private")


def classify_destination(
    connection_type: str,
    provider: Optional[str],
    base_url: Optional[str],
) -> Dict[str, Any]:
    """
    Restituisce dove va il testo:

    - outside: True se esce di casa (cloud, IP pubblico, URL dubbio)
    - category: "cloud" per i provider cloud fissi, altrimenti la categoria
      di classify_url ("loopback", "private", "public", "link_local", "invalid")
    - host: il nome dell'host ("" se non c'è)
    - reason: spiegazione breve

    Non solleva mai eccezioni: classify_url degrada già in "invalid".
    """
    if connection_type == "Cloud provider" and provider in FIXED_CLOUD_PROVIDERS:
        return {
            "outside": True,
            "category": "cloud",
            "host": "",
            "reason": f"{provider}: fornitore cloud",
        }

    info = classify_url(base_url)
    category = info["category"]
    return {
        "outside": category not in INSIDE_CATEGORIES,
        "category": category,
        "host": info.get("hostname", ""),
        "reason": info.get("reason", ""),
    }


def outside_label(destination: Dict[str, Any]) -> str:
    """Nome breve della destinazione fuori casa, per i messaggi della UI."""
    if destination.get("category") == "cloud":
        return "Cloud provider"
    host = destination.get("host") or "host sconosciuto"
    if destination.get("category") == "public":
        return f"host esterno ({host})"
    return f"destinazione non verificabile ({host})"
