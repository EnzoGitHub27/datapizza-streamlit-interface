# ui/chat.py
# Datapizza v1.5.0 - Rendering Chat
# ============================================================================
# 🆕 v1.5.0: Aggiunto supporto per visualizzazione allegati nei messaggi
# ============================================================================

from datetime import datetime
from typing import Dict, Any, List

import streamlit as st


def render_chat_message(message: Dict[str, Any], index: int):
    """
    Renderizza un singolo messaggio della chat con stile bubble.
    
    Args:
        message: Dizionario con role, content, timestamp, model, sources, attachments
        index: Indice del messaggio nella conversazione
    """
    role = message["role"]
    content = message["content"]
    timestamp = message.get("timestamp", "")
    model_used = message.get("model", "")
    sources = message.get("sources", [])
    attachments = message.get("attachments", [])  # 🆕 v1.5.0
    
    # Format timestamp
    time_str = ""
    if timestamp:
        try:
            time_str = datetime.fromisoformat(timestamp).strftime("%H:%M:%S")
        except:
            pass
    
    # Configure styling based on role
    if role == "user":
        avatar, label = "👤", "Tu"
        col_config = [3, 7, 0.5]
        bubble_class = "user-bubble"
    else:
        avatar = "🤖"
        label = f"AI{f' ({model_used})' if model_used else ''}"
        col_config = [0.5, 7, 3]
        bubble_class = "assistant-bubble"
    
    # Render message
    cols = st.columns(col_config)
    with cols[1]:
        st.caption(f"{avatar} **{label}** • {time_str}")
        st.markdown(f'<div class="{bubble_class}">', unsafe_allow_html=True)
        
        # 🆕 v1.5.0 - Mostra allegati se presenti (solo per messaggi utente)
        if attachments and role == "user":
            attachments_str = ", ".join(attachments)
            st.caption(f"📎 **Allegati:** {attachments_str}")
        
        st.write(content)
        
        # Show sources if present (RAG)
        if sources:
            with st.expander(f"📎 Fonti ({len(sources)})"):
                for src in sources:
                    st.caption(f"• {src}")
        
        st.markdown('</div>', unsafe_allow_html=True)
        st.write("")


def render_chat_area(messages: List[Dict[str, Any]]):
    """
    Renderizza l'intera area chat con tutti i messaggi.
    
    Args:
        messages: Lista di messaggi della conversazione
    """
    st.subheader("💬 Conversazione")
    
    if not messages:
        if st.session_state.get("use_knowledge_base"):
            st.info("👋 Knowledge Base attiva! Fai una domanda sui tuoi documenti.")
        else:
            st.info("👋 Inizia una conversazione!")
    else:
        for idx, msg in enumerate(messages):
            render_chat_message(msg, idx)


def render_empty_state():
    """Renderizza stato vuoto della chat."""
    if st.session_state.get("use_knowledge_base"):
        st.info("👋 Knowledge Base attiva! Fai una domanda sui tuoi documenti.")
    else:
        st.info("👋 Inizia una conversazione!")
