# ui/privacy_warning.py
# DeepAiUG v1.5.0 - Privacy Warning Dialog
# ============================================================================
#
# Gestisce gli avvisi di privacy quando l'utente tenta di passare a un
# Cloud provider dopo aver caricato documenti nella sessione.
#
# Filosofia Privacy-First:
# - I documenti caricati localmente non devono mai finire su cloud
# - La cronologia può contenere informazioni estratte dai documenti
# - L'utente deve essere consapevole dei rischi e decidere esplicitamente
#
# ============================================================================

import streamlit as st
from typing import Tuple, Optional


def check_privacy_risk() -> bool:
    """
    Verifica se esiste un rischio privacy nella sessione corrente.
    
    Returns:
        True se ci sono documenti caricati E non è stato già dato consenso
    """
    docs_uploaded = st.session_state.get("documents_uploaded_this_session", False)
    privacy_acknowledged = st.session_state.get("privacy_acknowledged_for_cloud", False)
    
    return docs_uploaded and not privacy_acknowledged


def get_uploaded_files_summary() -> str:
    """
    Genera un riepilogo dei file caricati nella sessione.
    
    Returns:
        Stringa con elenco file o messaggio vuoto
    """
    files_history = st.session_state.get("uploaded_files_history", [])
    
    if not files_history:
        return ""
    
    return ", ".join(files_history[:5]) + ("..." if len(files_history) > 5 else "")


def render_privacy_warning_banner():
    """
    Mostra un banner di warning quando si è su Cloud con documenti in memoria.
    
    Da usare nell'area principale dell'app per ricordare all'utente
    che la sessione contiene dati potenzialmente sensibili.
    """
    if not st.session_state.get("documents_uploaded_this_session", False):
        return
    
    if st.session_state.get("connection_type") != "Cloud provider":
        return
    
    files_summary = get_uploaded_files_summary()
    
    st.warning(
        f"⚠️ **Sessione con documenti in memoria**\n\n"
        f"File caricati: {files_summary}\n\n"
        f"La cronologia potrebbe contenere informazioni estratte da questi documenti."
    )


def render_privacy_dialog() -> Tuple[bool, Optional[str]]:
    """
    Renderizza il dialog di conferma privacy.
    
    Chiamare questa funzione quando l'utente tenta di passare a Cloud
    e ci sono documenti nella sessione.
    
    Returns:
        Tuple:
        - can_proceed: True se l'utente può procedere con Cloud
        - action: "reset" | "proceed" | None (se ancora in attesa di decisione)
    """
    files_summary = get_uploaded_files_summary()
    
    st.markdown("---")
    
    # Container per il dialog
    with st.container():
        st.markdown(
            """
            <div style="
                background-color: #FFF3CD; 
                border: 2px solid #FFC107; 
                border-radius: 10px; 
                padding: 20px;
                margin: 10px 0;
            ">
            <h3 style="color: #856404; margin-top: 0;">⚠️ ATTENZIONE - Documenti in memoria</h3>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        st.markdown(
            f"""
            Durante questa sessione sono stati caricati **documenti**:
            
            > 📄 {files_summary}
            
            La **cronologia della chat** potrebbe contenere informazioni estratte 
            da questi documenti (risposte dell'AI, citazioni, riassunti).
            
            Passando a un **Cloud provider**, queste informazioni verrebbero 
            inviate a server esterni.
            """
        )
        
        st.markdown("### Scegli come procedere:")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(
                """
                **🔄 Reset Chat** *(consigliato)*
                
                Cancella la cronologia e riparti 
                con una chat pulita.
                
                ✅ Massima sicurezza
                """
            )
            reset_clicked = st.button(
                "🔄 Reset e usa Cloud",
                key="privacy_reset_btn",
                type="primary",
                use_container_width=True
            )
        
        with col2:
            st.markdown(
                """
                **✅ Procedi comunque**
                
                Conferma che i documenti non 
                contenevano dati sensibili.
                
                ⚠️ A tuo rischio
                """
            )
            
            # Checkbox obbligatoria
            confirmed = st.checkbox(
                "Confermo: i documenti non contenevano dati riservati",
                key="privacy_confirm_checkbox"
            )
            
            proceed_clicked = st.button(
                "✅ Procedi con Cloud",
                key="privacy_proceed_btn",
                disabled=not confirmed,
                use_container_width=True
            )
        
        st.markdown("---")
        
        # Gestisci le azioni
        if reset_clicked:
            return True, "reset"
        
        if proceed_clicked and confirmed:
            return True, "proceed"
        
        # Opzione per tornare indietro
        if st.button("↩️ Torna a Local/Remote", key="privacy_back_btn"):
            return True, "back"
        
        return False, None


def handle_privacy_action(action: str):
    """
    Esegue l'azione scelta dall'utente nel dialog privacy.
    
    Args:
        action: "reset" | "proceed" | "back"
    """
    if action == "reset":
        # Reset completo della chat
        from core import generate_conversation_id
        from datetime import datetime
        
        st.session_state["messages"] = []
        st.session_state["conversation_id"] = generate_conversation_id()
        st.session_state["conversation_created_at"] = datetime.now().isoformat()
        st.session_state["total_tokens_estimate"] = 0
        
        # Reset flags privacy
        st.session_state["documents_uploaded_this_session"] = False
        st.session_state["uploaded_files_history"] = []
        st.session_state["privacy_acknowledged_for_cloud"] = False
        
        # Mantieni Cloud provider selezionato
        st.session_state["connection_type"] = "Cloud provider"
        
        st.success("✅ Chat resettata! Ora puoi usare Cloud provider in sicurezza.")
        st.rerun()
    
    elif action == "proceed":
        # Utente ha confermato - salva il consenso
        st.session_state["privacy_acknowledged_for_cloud"] = True
        st.info("✅ Hai confermato. Puoi procedere con Cloud provider.")
        st.rerun()
    
    elif action == "back":
        # Torna a Local
        st.session_state["connection_type"] = "Local (Ollama)"
        st.session_state["privacy_dialog_shown"] = False
        st.rerun()


def mark_documents_uploaded(filenames: list):
    """
    Segna che sono stati caricati documenti nella sessione.
    
    Chiamare questa funzione ogni volta che vengono processati
    file nell'upload widget.
    
    Args:
        filenames: Lista dei nomi file caricati
    """
    if not filenames:
        return
    
    st.session_state["documents_uploaded_this_session"] = True
    
    # Mantieni storico dei file (per mostrare nel warning)
    history = st.session_state.get("uploaded_files_history", [])
    for name in filenames:
        if name not in history:
            history.append(name)
    st.session_state["uploaded_files_history"] = history
    
    # Resetta il consenso precedente (nuovi documenti = nuovo rischio)
    st.session_state["privacy_acknowledged_for_cloud"] = False


def reset_privacy_flags():
    """
    Resetta tutti i flag di privacy.
    
    Chiamare quando si fa reset della conversazione.
    """
    st.session_state["documents_uploaded_this_session"] = False
    st.session_state["uploaded_files_history"] = []
    st.session_state["privacy_acknowledged_for_cloud"] = False
    st.session_state["privacy_dialog_shown"] = False


def should_show_privacy_dialog(new_connection_type: str) -> bool:
    """
    Determina se mostrare il dialog di privacy.
    
    Args:
        new_connection_type: Il tipo di connessione selezionato
        
    Returns:
        True se bisogna mostrare il dialog
    """
    # Solo se si sta passando a Cloud
    if new_connection_type != "Cloud provider":
        return False
    
    # Solo se ci sono documenti caricati
    if not st.session_state.get("documents_uploaded_this_session", False):
        return False
    
    # Non mostrare se già dato consenso
    if st.session_state.get("privacy_acknowledged_for_cloud", False):
        return False
    
    return True
