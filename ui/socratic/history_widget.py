# ui/socratic/history_widget.py
# DeepAiUG v1.9.0 - Widget Storico Socratico
# ============================================================================
# Visualizza lo storico delle esplorazioni socratiche nella sidebar.
# Permette all'utente di rivedere le proprie riflessioni critiche.
# ============================================================================

import streamlit as st

from .history import SocraticHistory


# Mapping tipo bottone → emoji
BUTTON_EMOJIS: dict[str, str] = {
    "alternatives": "🔄",
    "assumptions": "🤔",
    "limits": "⚠️",
    "confute": "🎭",
    "reflect": "🪞",
}


def render_socratic_history_sidebar(socratic_mode: str = "standard") -> None:
    """
    Renderizza il widget storico socratico nella sidebar.

    Mostra conteggi, breakdown per tipo e lista delle ultime esplorazioni.
    Visibile solo in modalità "standard" o "socratic".

    Args:
        socratic_mode: Modalità socratica corrente ("fast", "standard", "socratic")
    """
    # In modalità fast, non mostrare il widget
    if socratic_mode == "fast":
        return

    history = SocraticHistory.get_session_history()
    stats = SocraticHistory.get_stats()
    total = len(history)

    # Titolo sezione
    st.sidebar.markdown("---")
    st.sidebar.subheader("📋 Esplorazioni socratiche")

    # Contatore totale
    if total == 0:
        st.sidebar.caption("Nessuna esplorazione ancora.")
        st.sidebar.caption("Usa i bottoni sotto le risposte AI!")
        return

    st.sidebar.metric("Totale", f"{total} esplorazion{'e' if total == 1 else 'i'}")

    # Breakdown per tipo (riga compatta)
    breakdown_parts = []
    for btn_type, emoji in BUTTON_EMOJIS.items():
        count = stats.get(btn_type, 0)
        if count > 0:
            breakdown_parts.append(f"{emoji} {count}")

    if breakdown_parts:
        st.sidebar.caption(" | ".join(breakdown_parts))

    # Lista ultime 10 esplorazioni (ordinate per timestamp decrescente)
    recent = sorted(history, key=lambda x: x.timestamp, reverse=True)[:10]

    with st.sidebar.expander(f"📜 Ultime {len(recent)} esplorazioni", expanded=False):
        for i, exp in enumerate(recent):
            emoji = BUTTON_EMOJIS.get(exp.button_type, "❓")
            time_str = exp.timestamp.strftime("%H:%M")
            question_snippet = exp.original_question[:50]
            if len(exp.original_question) > 50:
                question_snippet += "..."

            # Sub-expander per ogni esplorazione
            exp_label = f"{emoji} {time_str} - {question_snippet}"
            with st.expander(exp_label, expanded=False):
                st.markdown(f"**Domanda:** {exp.original_question}")
                st.markdown("---")
                st.markdown(exp.socratic_result)

    # Sezione cancellazione con conferma
    st.sidebar.markdown("")  # Spacer

    # Checkbox conferma + bottone
    confirm_key = "confirm_clear_socratic_history"
    confirm = st.sidebar.checkbox("Conferma cancellazione", key=confirm_key)

    # v1.16.1 — la cancellazione sta nel callback del bottone: gira prima che
    # i widget si ridisegnino, quindi può rimettere a False la casella (dopo,
    # Streamlit dà StreamlitAPIException), e chiede il salvataggio su disco
    st.sidebar.button(
        "🗑️ Cancella storico",
        disabled=not confirm,
        help="Seleziona 'Conferma cancellazione' prima di procedere",
        on_click=_clear_history,
        args=(confirm_key,),
    )


def _clear_history(confirm_key: str) -> None:
    """Svuota lo storico, toglie la conferma e fa salvare la conversazione."""
    SocraticHistory.clear_history()
    st.session_state[confirm_key] = False
    st.session_state["_socratic_save_needed"] = True
