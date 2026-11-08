# ui/conversation_reset.py
# DeepAiUG v1.16.1 — L'azzeramento della conversazione, in un posto solo.
# ============================================================================
# Lo usano «🔄 Nuova» (app.py) e «🔄 Reset e usa Cloud» del dialogo privacy
# (ui/privacy_warning.py). Fino alla 1.16.0 il dialogo aveva una sua copia, più
# corta: restavano la memoria dei dati tolti, i riquadri «Cosa ha visto il
# modello», la cache e lo storico socratici, la mappa e i contatori.
# ============================================================================

from datetime import datetime

import streamlit as st


def reset_conversation() -> None:
    """Azzera la conversazione corrente e tutto quello che la sessione ne ricorda."""
    # import qui: ui.privacy_warning importa questo modulo e viceversa
    from core.conversation import generate_conversation_id
    from core.persistence import KB_METADATA_DEFAULT
    from ui.file_upload import clear_pending_files
    from ui.privacy_warning import reset_privacy_flags
    from ui.socratic.buttons import clear_socratic_cache
    from ui.socratic.history import SocraticHistory

    st.session_state["messages"] = []
    st.session_state["conversation_id"] = generate_conversation_id()
    st.session_state["conversation_created_at"] = datetime.now().isoformat()
    st.session_state["total_tokens_estimate"] = 0
    # v1.14.0 - Reset KB metadata
    st.session_state["kb_metadata"] = dict(KB_METADATA_DEFAULT)
    # v1.14.2 - Reset vault_used
    st.session_state["vault_used"] = False
    # v1.16.0 - Reset metadati del guard
    st.session_state.pop("pii_guard", None)
    st.session_state["pii_removed"] = 0
    st.session_state["egress_views"] = {}  # P9: solo sessione
    st.session_state.pop("_pii_memory", None)  # giro 7b: la memoria dei valori tolti si azzera
    # v1.5.0 - Pulisci anche file pending e flag privacy
    clear_pending_files()
    reset_privacy_flags()
    # v1.6.1 - Pulisci cache socratica
    clear_socratic_cache()
    # v1.9.0 - Pulisci storico socratico
    SocraticHistory.clear_history()
    # v1.10.0 - Reset mappa sessione
    st.session_state["session_map_data"] = None
    st.session_state["n_domande_sessione"] = 0
    st.session_state["nudge_mostrato"] = False
