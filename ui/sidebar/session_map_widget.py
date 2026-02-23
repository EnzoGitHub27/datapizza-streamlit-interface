# ui/sidebar/session_map_widget.py
# DeepAiUG v1.10.0 - Widget Sidebar Mappa Sessione (F2)
# ============================================================================
# Componenti UI puri per la mappa sessione.
# Ricevono dati, non li calcolano. Lo stato vive in app.py.
# ============================================================================

import streamlit as st

from config.constants import SESSION_MAP_MODES
from ui.socratic.session_map import SessionMap


# Testo del tooltip, dalla sezione 6 di F2_MAPPA_SESSIONE_SPEC.md
_TOOLTIP_TEXT = """\
Ogni volta che fai una domanda all'AI, non stai solo cercando
una risposta. Stai anche costruendo, senza accorgertene, una
cornice invisibile che orienta le domande successive.

La Mappa Sessione rende visibile questa cornice:
• Qual è il frame implicito che stai usando?
• Come le tue domande lo hanno costruito?
• Quali corridoi non hai ancora esplorato?

Non giudica le tue scelte. Ti restituisce attrito:
ti aiuta a capire da dove stai guardando il problema,
così puoi decidere consapevolmente se continuare
a guardare da lì o cambiare prospettiva.

───────────────────────────────────
Ispirato a:
• "Sovrascopo" — Cinzia Ligas, AI Semiology (2026)
• "Vincolo teleologico" — Carmelo Quartarone, Il Teleology Gate (2026)
• "Capitale semantico" — Luciano Floridi
───────────────────────────────────
📖 Approfondisci → PHILOSOPHY.md"""


def render_session_map_settings() -> str:
    """
    Renderizza il selettore modalità mappa sessione nella sidebar.

    Returns:
        La chiave della modalità selezionata ("progressive", "threshold", "off")
    """
    st.sidebar.markdown("---")
    st.sidebar.subheader("📊 Mappa sessione")

    # Tooltip "?"
    with st.sidebar.expander("❓ Cos'è la Mappa Sessione?", expanded=False):
        st.markdown(_TOOLTIP_TEXT)

    # Radio button per le modalità
    mode_keys = list(SESSION_MAP_MODES.keys())
    mode_labels = [
        f"{SESSION_MAP_MODES[k]['icon']} {SESSION_MAP_MODES[k]['name']}"
        for k in mode_keys
    ]

    current_mode = st.session_state.get("session_map_mode", "threshold")
    current_index = mode_keys.index(current_mode) if current_mode in mode_keys else 1

    selected_label = st.sidebar.radio(
        "Modalità",
        mode_labels,
        index=current_index,
        key="session_map_mode_radio",
        label_visibility="collapsed",
    )

    selected_index = mode_labels.index(selected_label)
    return mode_keys[selected_index]


def render_nudge_sidebar(nudge_text: str) -> bool:
    """
    Renderizza il nudge nella sidebar.

    Puro UI: mostra il messaggio e il bottone.
    Restituisce True se l'utente ha premuto il bottone.

    Args:
        nudge_text: Testo del nudge da mostrare
    """
    st.sidebar.info(f"💡 {nudge_text}")
    return st.sidebar.button(
        "📊 Mostra mappa sessione",
        key="btn_show_session_map",
    )


def render_generate_map_button() -> bool:
    """
    Bottone per generare la mappa su una conversazione esistente/caricata.

    Returns:
        True se l'utente ha premuto il bottone
    """
    return st.sidebar.button("📊 Genera mappa", key="btn_genera_mappa")


def render_session_map_display(map_data: SessionMap) -> bool:
    """
    Renderizza la mappa sessione nella sidebar.

    Puro rendering: riceve i dati, non li calcola.

    Args:
        map_data: Mappa sessione già calcolata da SessionMapAnalyzer

    Returns:
        True se l'utente ha premuto "Rigenera mappa"
    """
    st.sidebar.markdown("---")
    with st.sidebar.expander("📊 Mappa della sessione", expanded=True):
        # 1. Frame dominante
        st.markdown("**Frame dominante:**")
        st.markdown(f"> {map_data.dominant_frame}")

        # 2. Connessione domande → frame
        if map_data.entries:
            st.markdown("**Domande → frame:**")
            for i, entry in enumerate(map_data.entries):
                question_short = entry.question_summary[:80]
                if len(entry.question_summary) > 80:
                    question_short += "..."
                st.markdown(
                    f"{i + 1}. *\"{question_short}\"*\n"
                    f"   → {entry.frame_contribution}"
                )

        # 3. Frame non esplorati
        if map_data.unexplored_frames:
            st.markdown("**Frame non esplorati:**")
            for frame in map_data.unexplored_frames:
                st.markdown(f"→ {frame}")

        # Timestamp
        st.caption(
            f"Mappa generata alle {map_data.created_at.strftime('%H:%M')}"
        )

    # Bottone rigenera (fuori dall'expander, visibile sempre)
    return st.sidebar.button("🔄 Rigenera mappa", key="btn_rigenera_mappa")
