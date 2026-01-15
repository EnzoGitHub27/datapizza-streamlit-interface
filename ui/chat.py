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
        # Spinge tutto a destra: colonna vuota grande a sinistra, poi il messaggio
        col_config = [2, 10] 
        bubble_class = "user-bubble"
        align = "right"
    else:
        avatar = "🤖"
        label = f"AI{f' ({model_used})' if model_used else ''}"
        # Tutto a sinistra: messaggio, poi vuoto a destra
        col_config = [10, 2]
        bubble_class = "assistant-bubble"
        align = "left"
    
    # Render message
    cols = st.columns(col_config)
    
    # Se è user, usiamo la seconda colonna (quella larga a destra)
    # Se è assistant, usiamo la prima colonna (quella larga a sinistra)
    target_col_idx = 1 if role == "user" else 0
    
    with cols[target_col_idx]:
        # Header (Avatar + Nome) al di fuori della bolla
        st.markdown(
            f'<div style="text-align: {align}; font-size: 0.8em; opacity: 0.7; margin-bottom: 4px;">{avatar} <b>{label}</b> • {time_str}</div>', 
            unsafe_allow_html=True
        )

        # Costruiamo il contenuto HTML interno alla bolla
        import html
        
        # 1. Allegati
        attachments_html = ""
        if attachments and role == "user":
            att_list = ", ".join([html.escape(a) for a in attachments])
            attachments_html = f'<div style="margin-bottom: 8px; font-weight: bold;">📎 {att_list}</div><hr style="margin: 5px 0; border-color: rgba(255,255,255,0.2);">'
            
        # 2. Contenuto Messaggio (Basic escaping + Text to HTML)
        # Semplice conversione newline -> <br> 
        # Nota: perdiamo parzialmente il markdown complesso qui per favorire la UI "blob".
        # Per ora escape basic per evitare rotture HTML.
        msg_content_html = html.escape(content).replace("\n", "<br>")
        
        # Tentativo basic di preservare bold manuale (**text**) se presente, 
        # ri-iniettando i tag b dopo l'escape.
        # (Molto semplice, potrebbe non coprire tutto, ma aiuta visivamente)
        # msg_content_html = msg_content_html.replace("**", "<b>").replace("**", "</b>") # Troppo rischioso fare replace a coppie senza regex
        
        # 3. Fonti (RAG)
        sources_html = ""
        if sources:
            src_items = "".join([f"<li>{html.escape(s)}</li>" for s in sources])
            sources_html = f"""
            <hr style="margin: 10px 0; opacity: 0.3;">
            <details style="font-size: 0.9em; cursor: pointer;">
                <summary>📚 Fonti ({len(sources)})</summary>
                <ul style="margin-top: 5px; padding-left: 20px; list-style-type: disc;">
                    {src_items}
                </ul>
            </details>
            """

        # Assemblaggio bolla finale
        # IMPORTANTE: Niente indentazione nell'HTML per evitare che Markdown lo interpreti come code block!
        full_bubble_html = f"""
<div class="{bubble_class}">
{attachments_html}
<div style="white-space: pre-wrap;">{msg_content_html}</div>
{sources_html}
</div>
"""
        st.markdown(full_bubble_html, unsafe_allow_html=True)


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
