# core/annona_client.py
# DeepAiUG v1.16.0 (bozza, giro 1) - Client per Annona
# ============================================================================
#
# Annona 0.1.3 (Akaion, Apache-2.0) decide DOVE può girare ogni passo
# (placement: placed / held / redacted) e lo scrive in un registro a catena
# (ledger.jsonl). Il demone (`annona run`) espone un'API HTTP FastAPI su
# 127.0.0.1:7070, senza token per chi chiama da localhost senza Origin.
#
# Che cosa espone davvero Annona 0.1.3 (runner/kernel_api.py, local_api.py):
#   GET  /health                       {"status": "ok", "service": "annona"}
#   GET  /api/kernel/status            policy attiva? quante decisioni / held
#   GET  /api/kernel/policy            classi, substrati, regole, redazione
#   GET  /api/kernel/substrates        substrati e se rispondono (?probe=)
#   GET  /api/kernel/ledger            ultime decisioni (?limit, held, run_id)
#   GET  /api/kernel/ledger/verify     controllo della catena
#   POST /api/kernel/ask               ESEGUE un passo nel perimetro: Annona
#                                      classifica, decide, (redige), chiama il
#                                      modello e registra. Risposta + decisioni.
#   POST /api/kernel/ask/{run_id}/cancel
#
# Che cosa NON espone via HTTP (0.1.3):
#   - una decisione senza esecuzione ("dove andrebbe questo testo?");
#   - una scrittura nel registro da parte di un programma esterno.
#   Queste due cose esistono solo come libreria Python dentro Annona
#   (PolicyClassifier.classify_text, PlacementDecisionEngine.place,
#   Ledger.record) o come CLI (`annona policy test <classe>`).
#   Qui decide() e record() sono quindi solo INTERFACCIA: sollevano
#   AnnonaUnsupported. Le alternative sono nella SPEC (§5).
#
# Non ancora collegato all'interfaccia: vedi docs/SPEC_v1.16.0_hybrid.md
# ============================================================================

from __future__ import annotations

import ipaddress
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse

import requests

DEFAULT_ANNONA_URL = "http://127.0.0.1:7070"
DEFAULT_TIMEOUT = 10.0
ASK_TIMEOUT = 180.0  # /ask è sincrono e chiama un modello: può durare decine di secondi

CLASSES = ("public", "internal", "restricted")
OUTCOMES_PERMITTED = ("placed", "redacted")


# ── Eccezioni ────────────────────────────────────────────────────────────────


class AnnonaError(Exception):
    """Errore generico di Annona."""


class AnnonaUnavailable(AnnonaError):
    """Il demone non risponde, o non ha un executor / una policy."""


class AnnonaUnsupported(AnnonaError):
    """Operazione che Annona 0.1.3 non espone via HTTP."""


class AnnonaNotLocal(AnnonaError):
    """L'indirizzo non è di loopback: l'API di Annona non ha autenticazione."""


# ── Tipi ─────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class Placement:
    """La decisione di Annona per un passo."""

    outcome: str            # placed | held | redacted | queued | brief | none
    klass: str = ""         # public | internal | restricted
    substrate: str = ""
    rule_id: str = ""
    reason: str = ""
    candidates: Tuple[str, ...] = ()

    @property
    def permitted(self) -> bool:
        return self.outcome in OUTCOMES_PERMITTED

    @classmethod
    def from_json(cls, data: Optional[Dict[str, Any]]) -> Optional["Placement"]:
        if not data:
            return None
        return cls(
            outcome=str(data.get("outcome", "none")),
            klass=str(data.get("class", data.get("klass", ""))),
            substrate=str(data.get("substrate", "") or ""),
            rule_id=str(data.get("rule_id", "") or ""),
            reason=str(data.get("reason", "") or ""),
            candidates=tuple(data.get("candidates") or ()),
        )


@dataclass(frozen=True)
class LedgerVerification:
    ok: bool
    entries: int = 0
    problem: str = ""
    empty: bool = False


@dataclass(frozen=True)
class AskResult:
    """Risultato di /api/kernel/ask.

    ``egress`` (il testo uscito verso il modello, parola per parola) è escluso
    dal repr: può contenere dati, e non deve finire nei log.
    """

    response: str
    placement: Optional[Placement]
    enforced: bool
    decisions: List[Dict[str, Any]] = field(default_factory=list)
    egress: List[Dict[str, Any]] = field(default_factory=list, repr=False)
    cancelled: bool = False

    @property
    def held(self) -> bool:
        """True se il passo è rimasto fermo.

        Annona 0.1.3 risponde 200 anche quando il passo è held: l'esito vero
        sta solo nel placement (prova 5 del 23/10/2026).
        """
        return self.placement is not None and not self.placement.permitted


# ── Client ───────────────────────────────────────────────────────────────────


def _is_loopback_url(url: str) -> bool:
    host = (urlparse(url).hostname or "").strip("[]").lower()
    if host == "localhost":
        return True
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return False


class AnnonaClient:
    """Client HTTP per il demone di Annona (`annona run`).

    Args:
        base_url: default 127.0.0.1:7070. Deve essere di loopback.
        timeout: secondi per le letture.
        session: oggetto con .get/.post come requests (per i test).
    """

    def __init__(
        self,
        base_url: str = DEFAULT_ANNONA_URL,
        timeout: float = DEFAULT_TIMEOUT,
        session: Any = None,
    ):
        if not _is_loopback_url(base_url):
            raise AnnonaNotLocal(
                f"Annona deve girare su questo computer (loopback), non su {base_url!r}"
            )
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._http = session or requests.Session()

    # -- trasporto ----------------------------------------------------------

    def _request(self, method: str, path: str, *, timeout: Optional[float] = None,
                 **kwargs) -> Any:
        url = f"{self.base_url}{path}"
        try:
            resp = getattr(self._http, method)(url, timeout=timeout or self.timeout, **kwargs)
        except requests.RequestException as exc:
            raise AnnonaUnavailable(f"Annona non risponde: {type(exc).__name__}") from exc
        if resp.status_code in (404, 409, 503):
            # 404 = nessuna policy; 409 = configurazione che rifiuta di partire;
            # 503 = demone senza executor. In tutti e tre i casi non si decide.
            raise AnnonaUnavailable(f"Annona {path}: HTTP {resp.status_code}")
        if resp.status_code != 200:
            raise AnnonaError(f"Annona {path}: HTTP {resp.status_code}")
        try:
            return resp.json()
        except ValueError as exc:
            raise AnnonaError(f"Annona {path}: risposta non JSON") from exc

    # -- letture ------------------------------------------------------------

    def health(self) -> Dict[str, Any]:
        return self._request("get", "/health")

    def is_up(self) -> bool:
        """True se il demone risponde. Non solleva."""
        try:
            return self.health().get("status") == "ok"
        except AnnonaError:
            return False

    def status(self) -> Dict[str, Any]:
        """Se una policy è in vigore (``enforcing``) e i contatori."""
        return self._request("get", "/api/kernel/status")

    def is_enforcing(self) -> bool:
        """True se il demone risponde E ha una policy valida. Non solleva."""
        try:
            return bool(self.status().get("enforcing"))
        except AnnonaError:
            return False

    def policy(self) -> Dict[str, Any]:
        return self._request("get", "/api/kernel/policy")

    def substrates(self, probe: bool = False) -> List[Dict[str, Any]]:
        data = self._request("get", "/api/kernel/substrates",
                             params={"probe": str(probe).lower()})
        return list(data.get("substrates") or [])

    def ledger(self, limit: int = 60, held: bool = False, run_id: str = "") -> List[Dict[str, Any]]:
        params: Dict[str, Any] = {"limit": limit, "held": str(held).lower()}
        if run_id:
            params["run_id"] = run_id
        data = self._request("get", "/api/kernel/ledger", params=params)
        return list(data.get("entries") or [])

    def verify_ledger(self) -> LedgerVerification:
        data = self._request("get", "/api/kernel/ledger/verify")
        return LedgerVerification(
            ok=bool(data.get("ok")),
            entries=int(data.get("entries", 0) or 0),
            problem=str(data.get("problem", "") or ""),
            empty=bool(data.get("empty", False)),
        )

    # -- esecuzione nel perimetro (modalità "gateway") ------------------------

    def ask(
        self,
        prompt: str,
        *,
        run_id: str = "",
        max_iterations: int = 1,
        escalate: bool = False,
        timeout: float = ASK_TIMEOUT,
    ) -> AskResult:
        """Fa eseguire a Annona un passo intero: decide, redige, chiama, registra.

        È l'unica via HTTP per ottenere una decisione E una voce nel registro.
        Il modello lo chiama Annona, con i substrati della SUA policy: non i
        client dell'Interface. ``max_iterations=1`` perché l'Interface non usa
        strumenti (con gli strumenti la redazione di Annona 0.1.3 gira a vuoto).

        Raises:
            AnnonaUnavailable: demone giù, senza executor o senza policy.
            AnnonaError: risposta non valida.
        """
        if not prompt or not prompt.strip():
            raise ValueError("prompt vuoto")
        body: Dict[str, Any] = {
            "prompt": prompt,
            "max_iterations": max_iterations,
            "escalate": escalate,
        }
        if run_id:
            body["run_id"] = run_id
        data = self._request("post", "/api/kernel/ask", json=body, timeout=timeout)
        return AskResult(
            response=str(data.get("response", "") or ""),
            placement=Placement.from_json(data.get("placement")),
            enforced=bool(data.get("enforced", False)),
            decisions=list(data.get("decisions") or []),
            egress=list(data.get("egress") or []),
            cancelled=bool(data.get("cancelled", False)),
        )

    def cancel(self, run_id: str) -> bool:
        data = self._request("post", f"/api/kernel/ask/{run_id}/cancel")
        return bool(data.get("cancelled", False))

    # -- interfaccia senza implementazione HTTP in Annona 0.1.3 -----------------

    def decide(self, text: str, *, destination: str, tools: bool = False) -> Placement:
        """Dove può girare un passo con questo testo, verso questa destinazione?

        È la domanda che l'Interface vorrebbe fare PRIMA di chiamare il suo
        client (destination = "local" | "remote" | "cloud"). Annona 0.1.3
        non la espone via HTTP: vedi SPEC §5 per le tre strade.
        """
        raise AnnonaUnsupported(
            "Annona 0.1.3 non espone via HTTP una decisione senza esecuzione "
            "(serve la libreria in-process o un endpoint nuovo: SPEC §5)"
        )

    def record(self, *, kind: str, outcome: str, klass: str, substrate: str,
               payload_digest: str = "", detail: Optional[Dict[str, Any]] = None) -> str:
        """Scrive una voce nel registro di Annona per un passo fatto dall'Interface.

        Annona 0.1.3 non lo permette via HTTP (il registro lo scrive solo il
        suo perimetro): vedi SPEC §5.
        """
        raise AnnonaUnsupported(
            "Annona 0.1.3 non accetta voci di registro da programmi esterni via HTTP (SPEC §5)"
        )
