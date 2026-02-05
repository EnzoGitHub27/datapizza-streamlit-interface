# ui/chat.py
# DeepAiUG v1.8.0 - Rendering Chat + Socratic Buttons
# ============================================================================
# 🆕 v1.5.0: Aggiunto supporto per visualizzazione allegati nei messaggi
# 🆕 v1.6.1: Aggiunto bottone "Genera alternative" (approccio socratico)
# 🆕 v1.8.0: Passaggio user_question e socratic_mode ai bottoni socratici
# ============================================================================

from datetime import datetime
from typing import Dict, Any, List, Optional

import streamlit as st

from ui.socratic import render_socratic_buttons


def render_chat_message(
    message: Dict[str, Any],
    index: int,
    llm_client: Optional[object] = None,
    messages_list: Optional[List[Dict[str, Any]]] = None,
    socratic_mode: str = "standard"
):
    """
    Renderizza un singolo messaggio della chat con stile bubble.

    Args:
        message: Dizionario con role, content, timestamp, model, sources, attachments
        index: Indice del messaggio nella conversazione
        llm_client: Client LLM per le funzionalità socratiche (opzionale)
        messages_list: Lista completa messaggi per estrarre user_question (v1.8.0)
        socratic_mode: Modalità socratica per controllare i bottoni (v1.8.0)
    """
    role = message["role"]
    content = message["content"]
    timestamp = message.get("timestamp", "")
    model_used = message.get("model", "")
    sources = message.get("sources", [])
    attachments = message.get("attachments", [])  # v1.5.0

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

        # v1.5.0 - Mostra allegati se presenti (solo per messaggi utente)
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

        # v1.8.0 - Bottoni socratici (solo per risposte AI)
        if role == "assistant" and content:
            # v1.8.0 - Estrai user_question dal messaggio precedente
            user_question = None
            if messages_list and index > 0:
                prev_msg = messages_list[index - 1]
                if prev_msg.get("role") == "user":
                    user_question = prev_msg.get("content")

            render_socratic_buttons(
                message_content=content,
                msg_index=index,
                client=llm_client,
                user_question=user_question,
                socratic_mode=socratic_mode
            )

        st.write("")


def render_chat_area(
    messages: List[Dict[str, Any]],
    llm_client: Optional[object] = None,
    socratic_mode: str = "standard"
):
    """
    Renderizza l'intera area chat con tutti i messaggi.

    Args:
        messages: Lista di messaggi della conversazione
        llm_client: Client LLM per le funzionalità socratiche (opzionale)
        socratic_mode: Modalità socratica (v1.8.0)
    """
    st.subheader("💬 Conversazione")

    if not messages:
        if st.session_state.get("use_knowledge_base"):
            st.info("👋 Knowledge Base attiva! Fai una domanda sui tuoi documenti.")
        else:
            st.info("👋 Inizia una conversazione!")
    else:
        for idx, msg in enumerate(messages):
            render_chat_message(
                msg,
                idx,
                llm_client,
                messages_list=messages,
                socratic_mode=socratic_mode
            )


def render_empty_state():
    """Renderizza stato vuoto della chat."""
    if st.session_state.get("use_knowledge_base"):
        st.info("👋 Knowledge Base attiva! Fai una domanda sui tuoi documenti.")
    else:
        st.info("👋 Inizia una conversazione!")
