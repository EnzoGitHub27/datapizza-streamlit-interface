# ui/sidebar/annona_panel.py
# DeepAiUG v1.16.0 (giro 5, P7) - Le letture di Annona nella sidebar
# ============================================================================
# Visibile solo con hybrid.annona.enabled. Stato del demone, ultime decisioni
# del registro (classe, esito, substrato, motivo: mai il testo) e verifica
# della catena. Annona giù o senza policy: la sezione lo dice, l'app procede.
# Le letture si rifanno al massimo ogni CACHE_SECONDS o con «🔄 Aggiorna».
# ============================================================================

import time
from typing import Any, Optional

import streamlit as st

from core import annona_bridge

CACHE_SECONDS = 20
_CACHE_KEY = "_annona_state_cache"

_OUTCOME_ICON = {"placed": "✅", "redacted": "🛡️", "held": "⛔", "queued": "⏳"}


def _get_state(settings: Any, force: bool = False) -> annona_bridge.AnnonaState:
    cached = st.session_state.get(_CACHE_KEY)
    now = time.monotonic()
    if not force and cached and now - cached[0] < CACHE_SECONDS:
        return cached[1]
    try:
        client = annona_bridge.make_client(settings)
        state = annona_bridge.read_state(client)
    except Exception as exc:  # indirizzo non di loopback o altro: la sezione lo dice
        state = annona_bridge.AnnonaState(problem=f"configurazione non valida ({type(exc).__name__})")
    st.session_state[_CACHE_KEY] = (now, state)
    return state


def _entry_line(e: dict) -> str:
    icon = _OUTCOME_ICON.get(e.get("outcome", ""), "•")
    parts = [f"#{e['seq']}" if "seq" in e else "", e.get("class", ""), e.get("outcome", ""),
             f"→ {e['substrate']}" if e.get("substrate") else ""]
    line = f"{icon} " + " · ".join(p for p in parts if p)
    if e.get("reason"):
        line += f"  \n  _{e['reason']}_"
    return line


def render_annona_panel(hybrid: Optional[Any], container=None) -> None:
    """Sezione «🧭 Annona» della sidebar. Niente se Annona non è attivata."""
    if hybrid is None or not getattr(hybrid.annona, "enabled", False):
        return
    container = container or st.sidebar
    settings = hybrid.annona
    mode_label = "gateway (sperimentale)" if settings.mode == "gateway" else "sola lettura"

    with container.expander(f"🧭 Annona — {mode_label}", expanded=False):
        force = st.button("🔄 Aggiorna", key="annona_refresh", use_container_width=True)
        state = _get_state(settings, force=force)

        if not state.up or not state.enforcing:
            st.warning(f"🧭 {state.problem or 'Annona non disponibile'}")
            if settings.mode == "gateway":
                st.caption("Con il gateway acceso, verso fuori casa non parte niente finché Annona non risponde.")
            else:
                st.caption("L'app procede: gli invii non vengono registrati in Annona.")
            return

        s = state.status
        st.success(
            f"🧭 Annona attiva — {s.get('rules', '?')} regole, "
            f"{s.get('substrates', '?')} substrati, {s.get('decisions', '?')} decisioni "
            f"({s.get('held', 0)} held)"
        )

        v = state.verification
        if v is None:
            st.caption("🔗 Catena del registro: verifica non disponibile")
        elif v.empty:
            st.caption("🔗 Registro vuoto")
        elif v.ok:
            st.caption(f"🔗 Catena del registro integra ({v.entries} voci)")
        else:
            st.error(f"🔗 Catena del registro ROTTA: {v.problem or 'verifica fallita'}")

        if state.entries:
            st.markdown("**Ultime decisioni**")
            for e in state.entries:
                st.markdown(_entry_line(e))
        if state.problem:
            st.caption(f"⚠️ {state.problem}")

        if settings.mode == "read":
            st.caption(
                "Sola lettura: Annona non vede i messaggi dell'Interface. Gli invii "
                "fuori casa (con il solo rizzo-pii) sono segnati «non registrato in Annona»."
            )
