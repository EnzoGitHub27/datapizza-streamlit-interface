# ui/sidebar/conversations.py
# Datapizza v1.5.0 - Sidebar: Gestione conversazioni salvate
# ============================================================================

from pathlib import Path
import streamlit as st
import json

from config import DEFAULT_CHUNK_SIZE, DEFAULT_CHUNK_OVERLAP
from core import (
    list_saved_conversations,
    load_conversation,
    delete_conversation,
    extract_kb_settings,
    generate_conversation_id
)
from export import export_to_markdown
from rag import KnowledgeBaseManager, TextChunker, LocalFolderAdapter
from datetime import datetime

# Import clear_pending_files / reset_privacy from app logic duplication/shared? 
# To avoid circular imports, we just manipulate session state directly where possible or re-implement small helpers.

def render_conversations_manager():
    """Renderizza la sezione gestione conversazioni nella sidebar stile ChatGPT."""
    
    # "New Chat" button at the top
    def new_chat_callback():
        _reset_conversation()

    st.sidebar.button("➕ Nuova chat", use_container_width=True, type="primary", on_click=new_chat_callback)
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🕒 Cronologia")
    
    # Lista conversazioni salvate
    saved_conversations = list_saved_conversations()
    
    if not saved_conversations:
        st.sidebar.caption("Nessuna conversazione recente")
        return
    
    current_id = st.session_state.get("conversation_id")
    
    # Display list
    for conv in saved_conversations:
        c_id = conv["id"]
        c_model = conv.get("model", "Unknown")
        c_msgs = conv.get("message_count", 0)
        c_date = conv.get("last_updated", "")[:10]
        
        # Label generation
        label = f"{c_date} • {c_model}"
        if len(label) > 25:
            label = label[:24] + "..."
            
        # Layout: [ Button (Main) ] [ Menu (Dots) ]
        col_main, col_menu = st.sidebar.columns([0.85, 0.15])
        
        is_active = (c_id == current_id)
        btn_type = "secondary" if not is_active else "primary"
        
        # Main Button to Load
        with col_main:
            st.button(
                label, 
                key=f"load_{c_id}", 
                use_container_width=True, 
                type=btn_type, 
                help=f"{c_model} - {c_msgs} msgs",
                on_click=_load_conversation,
                args=(c_id,)
            )
        
        # Menu (3 dots)
        with col_menu:
            with st.popover("⋮", use_container_width=True):
                st.markdown(f"**Chat ID**: `{c_id[:8]}`")
                
                # Delete
                def delete_callback(cid, active):
                    delete_conversation(cid)
                    if active:
                        _reset_conversation()

                st.button(
                    "🗑️ Elimina", 
                    key=f"del_{c_id}", 
                    use_container_width=True,
                    on_click=delete_callback,
                    args=(c_id, is_active)
                )
                
                # Share (Download MD)
                conv_data = load_conversation(c_id)
                if conv_data:
                    metadata = {
                        "conversation_id": c_id,
                        # Use .get with defaults to avoid KeyErrors
                        "created_at": conv_data.get("created_at", datetime.now().isoformat()),
                        "model": conv_data.get("model", "Unknown"),
                        "provider": conv_data.get("provider", "Unknown"),
                    }
                    # FIX: Pass metadata to export_to_markdown
                    md_text = export_to_markdown(conv_data.get("messages", []), metadata)
                    
                    st.download_button(
                        label="📥 Share (MD)",
                        data=md_text,
                        file_name=f"chat_{c_id[:8]}.md",
                        mime="text/markdown",
                        key=f"share_{c_id}",
                        use_container_width=True
                    )


def _reset_conversation():
    """Resetta la sessione per una nuova conversazione."""
    st.session_state["messages"] = []
    st.session_state["conversation_id"] = generate_conversation_id()
    st.session_state["conversation_created_at"] = datetime.now().isoformat()
    st.session_state["total_tokens_estimate"] = 0
    # Reset file logic
    st.session_state["pending_files"] = []
    st.session_state["pending_has_images"] = False
    st.session_state["pending_warning"] = None
    st.session_state["privacy_acknowledged_for_cloud"] = False
    st.session_state["show_privacy_dialog"] = False


def _load_conversation(conversation_id: str):
    """
    Carica una conversazione e ripristina le impostazioni KB.
    """
    data = load_conversation(conversation_id)
    if not data:
        st.sidebar.error("❌ Errore caricamento")
        return
    
    # Ripristina dati conversazione
    st.session_state["conversation_id"] = data.get("conversation_id")
    st.session_state["conversation_created_at"] = data.get("created_at")
    st.session_state["messages"] = data.get("messages", [])
    st.session_state["total_tokens_estimate"] = data.get("stats", {}).get("tokens_estimate", 0)
    
    # Helper to clean lists
    st.session_state["pending_files"] = [] 
    
    # Ripristina impostazioni Knowledge Base
    kb_settings = extract_kb_settings(data)
    
    st.session_state["use_knowledge_base"] = kb_settings["use_knowledge_base"]
    st.session_state["kb_folder_path"] = kb_settings["kb_folder_path"]
    st.session_state["kb_extensions"] = kb_settings["kb_extensions"]
    st.session_state["kb_recursive"] = kb_settings["kb_recursive"]
    st.session_state["kb_chunk_size"] = kb_settings["kb_chunk_size"]
    st.session_state["kb_chunk_overlap"] = kb_settings["kb_chunk_overlap"]
    st.session_state["rag_top_k"] = kb_settings["rag_top_k"]
    
    # Ricarica KB se era attiva
    if kb_settings["use_knowledge_base"]:
        folder_path = kb_settings["kb_folder_path"]
        if folder_path and Path(folder_path).exists():
            kb_manager: KnowledgeBaseManager = st.session_state.get("kb_manager")
            if kb_manager:
                # Riconfigura chunker
                kb_manager.chunker = TextChunker(
                    chunk_size=kb_settings["kb_chunk_size"],
                    chunk_overlap=kb_settings["kb_chunk_overlap"]
                )
                # Riconfigura adapter
                adapter = LocalFolderAdapter({
                    "folder_path": folder_path,
                    "extensions": kb_settings["kb_extensions"],
                    "recursive": kb_settings["kb_recursive"]
                })
                kb_manager.set_adapter(adapter)
                # Re-indicizza (force index reload)
                kb_manager.index_documents()
