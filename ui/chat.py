# ui/chat.py
# DeepAiUG v1.14.3 - Rendering Chat + Socratic Buttons
# ============================================================================
# 🆕 v1.5.0: Aggiunto supporto per visualizzazione allegati nei messaggi
# 🆕 v1.6.1: Aggiunto bottone "Genera alternative" (approccio socratico)
# 🆕 v1.8.0: Passaggio user_question e socratic_mode ai bottoni socratici
# 🆕 v1.9.1: Fix bubble rendering - singola st.markdown() per wrappare contenuto
# 🆕 v1.14.3: Typing indicator animato + scroll automatico durante streaming
# ============================================================================

from datetime import datetime
from typing import Dict, Any, List, Optional

import streamlit as st
from markdown_it import MarkdownIt

import streamlit.components.v1 as components

from ui.socratic import render_socratic_buttons

# Markdown-to-HTML converter (tables + fenced code blocks enabled)
_md = MarkdownIt("commonmark", {"html": True}).enable("table")


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

        # Build bubble HTML as a single block so CSS wraps the content
        bubble_parts: list[str] = []

        # v1.5.0 - Attachments line (user messages only)
        if attachments and role == "user":
            attachments_str = ", ".join(attachments)
            bubble_parts.append(
                f'<p class="bubble-attachments">📎 <strong>Allegati:</strong> {attachments_str}</p>'
            )

        # Convert markdown content to HTML
        bubble_parts.append(_md.render(content))

        inner_html = "\n".join(bubble_parts)
        st.markdown(
            f'<div class="{bubble_class}">{inner_html}</div>',
            unsafe_allow_html=True,
        )

        # Show sources if present (RAG) — kept outside bubble as native expander
        if sources:
            with st.expander(f"📎 Fonti ({len(sources)})"):
                for src in sources:
                    st.caption(f"• {src}")

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
                socratic_mode=socratic_mode,
                model_used=model_used
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


# ── v1.14.3 — Typing indicator + Auto-scroll ────────────────────────────────

def show_typing_indicator():
    """
    Mostra tre pallini animati (typing indicator) nell'area chat.
    Usa il colore teal del tema Matrix DeepAiUG.
    """
    st.markdown("""
    <div class="typing-indicator">
        <span></span><span></span><span></span>
    </div>
    """, unsafe_allow_html=True)


def inject_scroll_to_bottom():
    """
    Inietta JS che scrolla la finestra verso il basso.
    Da chiamare durante lo streaming per seguire il testo in arrivo.
    """
    components.html(
        """
        <script>
            const chatContainer = window.parent.document.querySelector(
                'section.main [data-testid="stVerticalBlock"]'
            );
            if (chatContainer) {
                chatContainer.scrollTop = chatContainer.scrollHeight;
            }
            window.parent.scrollTo(0, window.parent.document.body.scrollHeight);
        </script>
        """,
        height=0,
    )
