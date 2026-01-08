# ui/sidebar/conversations.py
# Datapizza v1.4.0 - Sidebar: Gestione conversazioni salvate
# ============================================================================

from pathlib import Path
import streamlit as st

from config import DEFAULT_CHUNK_SIZE, DEFAULT_CHUNK_OVERLAP
from core import (
    list_saved_conversations,
    load_conversation,
    delete_conversation,
    extract_kb_settings,
)
from rag import KnowledgeBaseManager, TextChunker, LocalFolderAdapter


def render_conversations_manager():
    """Renderizza la sezione gestione conversazioni nella sidebar."""
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 💾 Conversazioni")
    
    # Auto-save toggle
    auto_save = st.sidebar.checkbox(
        "Auto-save", 
        value=st.session_state.get("auto_save_enabled", True)
    )
    st.session_state["auto_save_enabled"] = auto_save
    
    # Lista conversazioni salvate
    saved_conversations = list_saved_conversations()
    
    if not saved_conversations:
        st.sidebar.info("💡 Nessuna conversazione salvata")
        return
    
    # Crea opzioni per selectbox
    conv_options = [
        (
            f"{c['last_updated'][:10]} - {c['model'][:12]} ({c['message_count']})", 
            c["id"]
        ) 
        for c in saved_conversations
    ]
    
    selected = st.sidebar.selectbox(
        "Carica", 
        [None] + [c[0] for c in conv_options], 
        format_func=lambda x: "-- Seleziona --" if x is None else x
    )
    
    if selected:
        sel_id = next((c[1] for c in conv_options if c[0] == selected), None)
        
        if sel_id:
            col_l, col_d = st.sidebar.columns(2)
            
            with col_l:
                if st.button("📂 Carica"):
                    _load_conversation(sel_id)
                    st.rerun()
            
            with col_d:
                if st.button("🗑️ Elimina"):
                    delete_conversation(sel_id)
                    st.rerun()


def _load_conversation(conversation_id: str):
    """
    Carica una conversazione e ripristina le impostazioni KB.
    
    Args:
        conversation_id: ID della conversazione da caricare
    """
    data = load_conversation(conversation_id)
    if not data:
        st.sidebar.error("❌ Errore caricamento conversazione")
        return
    
    # Ripristina dati conversazione
    st.session_state["conversation_id"] = data.get("conversation_id")
    st.session_state["conversation_created_at"] = data.get("created_at")
    st.session_state["messages"] = data.get("messages", [])
    st.session_state["total_tokens_estimate"] = data.get("stats", {}).get("tokens_estimate", 0)
    
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
                # Re-indicizza
                kb_manager.index_documents()
