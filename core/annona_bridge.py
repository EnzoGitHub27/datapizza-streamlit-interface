# core/annona_bridge.py
# DeepAiUG v1.16.0 (giro 5, P7-P8) - Annona dentro l'Interface
# ============================================================================
# Due usi, entrambi opzionali e spenti per default (hybrid.annona):
#
#   mode "read"    (P7) — la sidebar legge stato, registro e verifica della
#                  catena. Annona non vede i messaggi dell'Interface: un invio
#                  fuori casa con il solo rizzo-pii NON è registrato in Annona
#                  (decisione 6), e il messaggio lo dice.
#   mode "gateway" (P8, sperimentale) — per le destinazioni fuori casa
#                  l'Interface chiama POST /api/kernel/ask al posto del suo
#                  client: decide, redige, chiama il modello e registra Annona.
#                  Si perdono lo streaming, la scelta del modello dell'Interface
#                  e le sue chiavi (i substrati e le chiavi stanno nella policy
#                  di Annona). Annona giù o passo «held» → niente parte.
#
# Del registro si mostrano solo campi di decisione (classe, esito, substrato,
# regola, motivo): mai il testo, il digest o i dettagli del passo.
# ============================================================================

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .annona_client import (
    AnnonaClient,
    AnnonaError,
    AnnonaUnavailable,
    LedgerVerification,
    Placement,
)

READ_TIMEOUT = 3.0  # la sidebar non deve bloccare l'app se Annona è giù

# i soli campi del registro che la sidebar può mostrare
LEDGER_FIELDS = ("seq", "ts", "kind", "class", "outcome", "substrate", "rule_id", "reason")

GATEWAY_LOSSES = (
    "niente streaming (la risposta arriva tutta insieme)",
    "il modello lo sceglie la policy di Annona, non la sidebar",
    "le chiavi dei fornitori stanno nella policy di Annona, non nell'Interface",
)


class AnnonaGatewayBlocked(Exception):
    """Il passo non è partito (Annona giù, senza policy, o «held»). Messaggio per l'utente."""


class AnnonaGatewayEmpty(AnnonaGatewayBlocked):
    """Il passo è partito ma Annona non ha prodotto testo (giro 7b).

    Caso tipico: Annona 0.1.3 offre sempre gli strumenti al modello (``/ask``
    non ha un campo per toglierli, e il profilo «read-nothing» li nega senza
    toglierli); un modello piccolo prova uno strumento, Annona lo trattiene
    (``tool_call`` «held») e la risposta resta vuota."""


def held_tools(decisions: List[Dict[str, Any]]) -> List[str]:
    """I nomi degli strumenti che il modello ha tentato e Annona ha trattenuto.
    Solo il nome (lettere, cifre, «_», «-»): mai percorsi o argomenti."""
    names: List[str] = []
    for d in decisions or []:
        if not isinstance(d, dict) or d.get("kind") != "tool_call" or d.get("outcome") != "held":
            continue
        detail = d.get("detail") if isinstance(d.get("detail"), dict) else {}
        name = str(detail.get("tool", "") or "")
        if name and re.fullmatch(r"[\w\-]{1,40}", name) and name not in names:
            names.append(name)
    return names

def make_client(settings: Any, timeout: float = READ_TIMEOUT) -> AnnonaClient:
    """AnnonaClient dalla sezione hybrid.annona (solo loopback)."""
    return AnnonaClient(settings.url, timeout=timeout)


# ── P7: letture per la sidebar ──────────────────────────────────────────────


@dataclass
class AnnonaState:
    up: bool = False
    enforcing: bool = False
    status: Dict[str, Any] = field(default_factory=dict)
    entries: List[Dict[str, Any]] = field(default_factory=list)
    verification: Optional[LedgerVerification] = None
    problem: str = ""


def clean_ledger_entry(entry: Dict[str, Any]) -> Dict[str, Any]:
    """Solo i campi di decisione; il motivo accorciato. Mai testo né dettagli."""
    out = {k: entry[k] for k in LEDGER_FIELDS if k in entry and entry[k] not in (None, "")}
    if "class" not in out and entry.get("klass"):
        out["class"] = entry["klass"]
    if "reason" in out:
        out["reason"] = str(out["reason"])[:160]
    return out


def read_state(client: AnnonaClient, limit: int = 8) -> AnnonaState:
    """Stato, ultime decisioni e verifica. Non solleva: i guasti finiscono in .problem."""
    state = AnnonaState()
    try:
        state.up = client.health().get("status") == "ok"
    except AnnonaError as exc:
        state.problem = f"Annona non risponde ({type(exc).__name__})"
        return state
    if not state.up:
        state.problem = "Annona risponde ma non dice «ok»"
        return state

    try:
        state.status = client.status() or {}
        state.enforcing = bool(state.status.get("enforcing"))
    except AnnonaError as exc:
        state.problem = f"stato non leggibile ({type(exc).__name__})"
        return state
    if not state.enforcing:
        reason = str(state.status.get("reason", "") or "nessuna policy in vigore")
        state.problem = f"senza policy: {reason[:120]}"
        return state

    try:
        state.entries = [clean_ledger_entry(e) for e in client.ledger(limit=limit)]
    except AnnonaError as exc:
        state.problem = f"registro non leggibile ({type(exc).__name__})"
    try:
        state.verification = client.verify_ledger()
    except AnnonaError as exc:
        state.problem = state.problem or f"verifica non riuscita ({type(exc).__name__})"
    return state


# ── P8: il gateway sperimentale ─────────────────────────────────────────────


@dataclass
class GatewayResult:
    text: str
    placement: Optional[Placement]
    egress_text: str = field(default="", repr=False)  # solo per la sessione corrente

    @property
    def summary(self) -> Dict[str, str]:
        p = self.placement
        if p is None:
            return {}
        return {k: v for k, v in (
            ("class", p.klass), ("outcome", p.outcome),
            ("substrate", p.substrate), ("rule_id", p.rule_id),
        ) if v}


def gateway_ask(client: AnnonaClient, prompt: str) -> GatewayResult:
    """Fa eseguire il passo ad Annona (max_iterations=1, nessuno strumento)."""
    try:
        result = client.ask(prompt, max_iterations=1, escalate=False)
    except AnnonaUnavailable as exc:
        raise AnnonaGatewayBlocked(
            "🧭 Annona non risponde o non ha una policy: con il gateway acceso il "
            "messaggio non è stato inviato."
        ) from exc
    except AnnonaError as exc:
        raise AnnonaGatewayBlocked(
            f"🧭 Annona ha risposto con un errore ({type(exc).__name__}): il messaggio non è stato inviato."
        ) from exc

    if result.cancelled:
        raise AnnonaGatewayBlocked("🧭 Il passo è stato annullato in Annona: nessuna risposta.")
    if result.held:
        reason = result.placement.reason if result.placement else ""
        raise AnnonaGatewayBlocked(
            f"🧭 Annona ha trattenuto il passo (held): {reason or 'nessun substrato permesso'}"
        )
    if not (result.response or "").strip():
        tools = held_tools(result.decisions)
        if tools:
            raise AnnonaGatewayEmpty(
                "🧭 Annona non ha prodotto testo: il modello ha tentato "
                + ("lo strumento " if len(tools) == 1 else "gli strumenti ")
                + ", ".join(f"«{t}»" for t in tools)
                + ", che Annona ha fermato. Il gateway di Annona 0.1.3 offre sempre gli "
                "strumenti al modello: prova un modello più grande o la strada senza gateway."
            )
        raise AnnonaGatewayEmpty("🧭 Annona non ha prodotto testo: nessuna risposta dal modello.")
    egress = "\n\n".join(
        str(e.get("text", "")) for e in result.egress if isinstance(e, dict) and e.get("text")
    )
    return GatewayResult(text=result.response, placement=result.placement, egress_text=egress)
