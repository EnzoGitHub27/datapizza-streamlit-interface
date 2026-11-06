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

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .annona_client import (
    AnnonaClient,
    AnnonaError,
    LedgerVerification,
)

READ_TIMEOUT = 3.0  # la sidebar non deve bloccare l'app se Annona è giù

# i soli campi del registro che la sidebar può mostrare
LEDGER_FIELDS = ("seq", "ts", "kind", "class", "outcome", "substrate", "rule_id", "reason")

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
