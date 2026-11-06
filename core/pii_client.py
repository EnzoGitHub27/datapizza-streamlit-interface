# core/pii_client.py
# DeepAiUG v1.16.0 (bozza, giro 1) - Client per rizzo-pii
# ============================================================================
#
# rizzo-pii (Simone Rizzo, codice MIT) è un servizio LOCALE che trova i dati
# personali in un testo italiano e li sostituisce con segnaposto tipati
# ([FULLNAME_1], [CF_1], [IBAN_1]...). La tabella segnaposto → valore resta
# sul computer: il ripristino lo fa questo modulo, in memoria, perché
# rizzo-pii 2.0.0 non ha un endpoint di ripristino (lo fa la sua UI in JS).
#
# API usate (rizzo-pii 2.0.0, src/app/app.py):
#   GET  /health    200 = modello caricato; 503 = server su, modello no
#   POST /analyze   {"text", "include_mapping", "exclude_tags"?}
#                   → {"anonymized_text", "mapping", "mapping_enabled",
#                      "n_entities", "by_label", ...}
#
# Regole di questo modulo:
# - si parla SOLO con un indirizzo di loopback: a rizzo-pii parte il testo
#   in chiaro, e il servizio non ha autenticazione;
# - il testo e la tabella non finiscono mai nei log né nei repr;
# - ogni guasto diventa un'eccezione esplicita: chi chiama decide (per il
#   cloud la SPEC dice "blocca e avvisa", mai "manda in chiaro").
#
# Non ancora collegato all'interfaccia: vedi docs/SPEC_v1.16.0_hybrid.md
# ============================================================================

from __future__ import annotations

import ipaddress
import re
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Mapping, Optional
from urllib.parse import urlparse

import requests

DEFAULT_PII_URL = "http://127.0.0.1:5005"
DEFAULT_TIMEOUT = 30.0  # il modello gira sul processore: un prompt lungo richiede secondi

# Lunghezza massima di un segnaposto "aperto" da trattenere nello streaming
_MAX_PLACEHOLDER_LEN = 64


# ── Eccezioni ────────────────────────────────────────────────────────────────


class PIIServiceError(Exception):
    """Errore generico del servizio rizzo-pii."""


class PIIServiceUnavailable(PIIServiceError):
    """Il servizio non risponde, va in timeout o il modello non è caricato."""


class PIIMappingDisabled(PIIServiceError):
    """rizzo-pii è in modalità definitiva: non restituisce la tabella.

    Senza tabella i segnaposto nella risposta non si possono rimettere.
    """


class PIINotLocal(PIIServiceError):
    """L'indirizzo configurato non è di loopback: il testo in chiaro uscirebbe."""


# ── Tipi ─────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class PIIHealth:
    """Lo stato di rizzo-pii, da GET /health."""

    ready: bool
    model: str = ""
    model_version: str = ""
    app_version: str = ""
    device: str = ""
    mapping_enabled: bool = True
    excluded_tags: tuple = ()


@dataclass(frozen=True)
class AnonymizedText:
    """Il testo pulito e la tabella per rimettere i valori.

    ``mapping`` è escluso dal repr: un log o un traceback non devono
    mostrarne i valori.
    """

    text: str
    mapping: Dict[str, str] = field(default_factory=dict, repr=False)
    by_label: Dict[str, int] = field(default_factory=dict)
    n_entities: int = 0

    @property
    def changed(self) -> bool:
        return self.n_entities > 0

    def restore(self, text: str) -> str:
        """Rimette i valori veri nei segnaposto di ``text`` (in locale)."""
        return restore_placeholders(text, self.mapping)

    def stream_restorer(self) -> "StreamRestorer":
        return StreamRestorer(self.mapping)


# ── Ripristino dei segnaposto ────────────────────────────────────────────────


def _build_pattern(keys: Iterable[str]) -> Optional[re.Pattern]:
    """Una regex sola per tutti i segnaposto della tabella.

    Stessa logica del reverse() di rizzo-pii 2.0.0:
    - una passata sola sul testo originale (un valore che contiene per caso
      il nome di un altro segnaposto non viene ri-sostituito);
    - parentesi tutto-o-niente: ``[CF_1]`` oppure ``CF_1`` nudo con confine
      di parola Unicode; ``[CF_12]`` con solo CF_1 in tabella NON matcha
      (un segnaposto rimasto si vede, un valore sbagliato no).
    """
    alts = []
    # Le chiavi più lunghe prima: a parità di posizione vince la più specifica
    for ph in sorted(keys, key=len, reverse=True):
        inner = ph[1:-1] if ph.startswith("[") and ph.endswith("]") else ph
        if not inner:
            continue
        esc = re.escape(inner)
        alts.append(rf"\[\s*{esc}\s*\]|(?<!\w){esc}(?!\w)")
    if not alts:
        return None
    return re.compile("|".join(alts))


def _inner(placeholder_match: str) -> str:
    return placeholder_match.strip("[] \t\r\n")


def restore_placeholders(text: str, mapping: Mapping[str, str]) -> str:
    """Sostituisce i segnaposto con i valori della tabella, in una passata."""
    if not text or not mapping:
        return text
    by_inner = {
        (ph[1:-1] if ph.startswith("[") and ph.endswith("]") else ph): val
        for ph, val in mapping.items()
    }
    pattern = _build_pattern(mapping.keys())
    if pattern is None:
        return text
    return pattern.sub(lambda m: by_inner.get(_inner(m.group(0)), m.group(0)), text)


class StreamRestorer:
    """Ripristino durante lo streaming, a pezzi.

    Un segnaposto può arrivare spezzato fra due pezzi ("[FULLN" + "AME_1]").
    Il restorer trattiene la coda che potrebbe essere l'inizio di un
    segnaposto ed emette solo testo sicuro, già ripristinato. Alla fine
    ``flush()`` restituisce quello che resta.

    Uso:  for delta in pezzi: out += r.push(delta);  out += r.flush()
    """

    def __init__(self, mapping: Mapping[str, str]):
        self._mapping = dict(mapping)
        self._inners = [
            (ph[1:-1] if ph.startswith("[") and ph.endswith("]") else ph)
            for ph in self._mapping
        ]
        self._buf = ""

    def _hold_from(self, buf: str) -> int:
        """Indice da cui trattenere la coda (len(buf) = niente da trattenere)."""
        last_open = buf.rfind("[")
        if last_open != -1 and "]" not in buf[last_open:] \
                and len(buf) - last_open <= _MAX_PLACEHOLDER_LEN:
            return last_open
        m = re.search(r"\w+$", buf)
        if m:
            tok = m.group(0)
            # tok può essere l'inizio di un segnaposto nudo, o un segnaposto
            # intero che potrebbe continuare (CF_1 → CF_12)
            if any(i.startswith(tok) or tok.startswith(i) for i in self._inners):
                return m.start()
        return len(buf)

    def push(self, delta: str) -> str:
        if not self._mapping:
            return delta
        self._buf += delta
        cut = self._hold_from(self._buf)
        ready, self._buf = self._buf[:cut], self._buf[cut:]
        return restore_placeholders(ready, self._mapping)

    def flush(self) -> str:
        rest, self._buf = self._buf, ""
        return restore_placeholders(rest, self._mapping)


# ── Client ───────────────────────────────────────────────────────────────────


def _is_loopback_url(url: str) -> bool:
    host = (urlparse(url).hostname or "").strip("[]").lower()
    if host == "localhost":
        return True
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return False


class PIIClient:
    """Client HTTP minimo per rizzo-pii.

    Args:
        base_url: indirizzo del servizio (default 127.0.0.1:5005). Deve essere
            di loopback, altrimenti PIINotLocal.
        timeout: secondi per ogni chiamata.
        session: oggetto con .get/.post come requests (per i test).
    """

    def __init__(
        self,
        base_url: str = DEFAULT_PII_URL,
        timeout: float = DEFAULT_TIMEOUT,
        session: Any = None,
    ):
        if not _is_loopback_url(base_url):
            raise PIINotLocal(
                f"rizzo-pii deve girare su questo computer (loopback), non su {base_url!r}"
            )
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._http = session or requests.Session()

    # -- salute -----------------------------------------------------------

    def health(self) -> PIIHealth:
        """Stato del servizio. 503 = modello non caricato (ready=False).

        Raises:
            PIIServiceUnavailable: il servizio non risponde.
        """
        try:
            resp = self._http.get(f"{self.base_url}/health", timeout=self.timeout)
        except requests.RequestException as exc:
            raise PIIServiceUnavailable(f"rizzo-pii non risponde: {type(exc).__name__}") from exc
        if resp.status_code not in (200, 503):
            raise PIIServiceUnavailable(f"rizzo-pii /health: HTTP {resp.status_code}")
        try:
            body = resp.json() or {}
        except ValueError as exc:
            raise PIIServiceUnavailable("rizzo-pii /health: risposta non JSON") from exc
        return PIIHealth(
            ready=resp.status_code == 200 and bool(body.get("model_loaded")),
            model=str(body.get("model", "")),
            model_version=str(body.get("model_version", "")),
            app_version=str(body.get("app_version", "")),
            device=str(body.get("device", "")),
            mapping_enabled=bool(body.get("mapping_enabled", True)),
            excluded_tags=tuple(body.get("excluded_tags") or ()),
        )

    def is_ready(self) -> bool:
        """True se il servizio risponde e il modello è caricato. Non solleva."""
        try:
            return self.health().ready
        except PIIServiceError:
            return False

    # -- anonimizza ---------------------------------------------------------

    def anonymize(
        self,
        text: str,
        exclude_tags: Optional[List[str]] = None,
        require_mapping: bool = True,
    ) -> AnonymizedText:
        """Toglie i dati personali da ``text``.

        Nota: rizzo-pii fa ``strip()`` del testo, quindi gli spazi iniziali e
        finali non tornano.

        Args:
            exclude_tags: tag da lasciare in chiaro (es. ["AMOUNT"]).
            require_mapping: se True (default) e il server non restituisce la
                tabella, solleva PIIMappingDisabled.

        Raises:
            PIIServiceUnavailable: servizio giù, timeout, modello non caricato.
            PIIMappingDisabled: tabella assente con require_mapping=True.
            PIIServiceError: risposta non valida.
        """
        if not text or not text.strip():
            # rizzo-pii risponde 400 al testo vuoto: niente da togliere
            return AnonymizedText(text=text)

        payload: Dict[str, Any] = {"text": text, "include_mapping": True}
        if exclude_tags is not None:
            payload["exclude_tags"] = list(exclude_tags)

        try:
            resp = self._http.post(
                f"{self.base_url}/analyze", json=payload, timeout=self.timeout
            )
        except requests.RequestException as exc:
            raise PIIServiceUnavailable(f"rizzo-pii non risponde: {type(exc).__name__}") from exc

        if resp.status_code == 503:
            raise PIIServiceUnavailable("rizzo-pii: modello non ancora caricato")
        if resp.status_code != 200:
            # il messaggio d'errore di rizzo-pii non contiene il testo
            raise PIIServiceError(f"rizzo-pii /analyze: HTTP {resp.status_code}")

        try:
            body = resp.json() or {}
        except ValueError as exc:
            raise PIIServiceError("rizzo-pii /analyze: risposta non JSON") from exc

        anon = body.get("anonymized_text")
        if not isinstance(anon, str):
            raise PIIServiceError("rizzo-pii /analyze: manca anonymized_text")

        mapping = body.get("mapping") or {}
        if not isinstance(mapping, dict):
            raise PIIServiceError("rizzo-pii /analyze: mapping non valido")
        n_entities = int(body.get("n_entities", len(mapping)) or 0)

        if require_mapping and n_entities > 0 and (
            not body.get("mapping_enabled", True) or not mapping
        ):
            raise PIIMappingDisabled(
                "rizzo-pii è in modalità definitiva (mapping disattivato): "
                "i dati nella risposta non si potrebbero rimettere"
            )

        return AnonymizedText(
            text=anon,
            mapping={str(k): str(v) for k, v in mapping.items()},
            by_label={str(k): int(v) for k, v in (body.get("by_label") or {}).items()},
            n_entities=n_entities,
        )
