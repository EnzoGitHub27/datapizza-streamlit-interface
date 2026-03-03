# ui/sidebar/conversations.py
# DeepAiUG v1.4.0 - Sidebar: Gestione conversazioni salvate
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
from ui.socratic import SocraticHistory, clear_socratic_cache  # v1.9.0


def render_conversations_manager():
    """Renderizza la sezione gestione conversazioni nella sidebar."""
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 💬 Conversazione")
    
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
    
    # Detect if current provider is cloud (for lock icon + load blocking)
    is_cloud = st.session_state.get("connection_type", "") != "Local (Ollama)"

    # Build selectbox options with content-type icons
    conv_options: list[dict] = []
    for c in saved_conversations:
        icons = _get_conversation_icon(c, is_cloud)
        prefix = f"{icons} " if icons else ""
        label = f"{prefix}{c['last_updated'][:10]} - {c['model'][:12]} ({c['message_count']})"
        conv_options.append({"label": label, "id": c["id"],
                             "is_sensitive": c.get("is_sensitive", False),
                             "reason": c.get("reason", ""), "icons": icons})

    selected = st.sidebar.selectbox(
        "Carica",
        [None] + [c["label"] for c in conv_options],
        format_func=lambda x: "-- Seleziona --" if x is None else x,
    )

    if selected:
        sel_entry = next((c for c in conv_options if c["label"] == selected), None)

        if sel_entry:
            # Show sensitivity detail when selected
            if sel_entry["is_sensitive"] and sel_entry["reason"]:
                st.sidebar.caption(f"{sel_entry['icons']} {sel_entry['reason']}")

            col_l, col_d = st.sidebar.columns(2)

            with col_l:
                if st.button("📂 Carica"):
                    # Block loading sensitive conversations on cloud providers
                    if sel_entry["is_sensitive"] and is_cloud:
                        st.sidebar.error(
                            f"{sel_entry['icons']} Questa conversazione contiene "
                            f"dati locali ({sel_entry['reason']}). Non può essere "
                            "caricata con un provider cloud per motivi di privacy."
                        )
                    else:
                        _load_conversation(sel_entry["id"])
                        st.rerun()

            with col_d:
                if st.button("🗑️ Elimina"):
                    delete_conversation(sel_entry["id"])
                    st.rerun()


def _get_conversation_icon(conv_info: dict, is_cloud: bool) -> str:
    """Genera le icone da mostrare accanto alla conversazione.

    Icone per tipo di contenuto sensibile:
    - 📚 = Knowledge Base Wiki (MediaWiki/DokuWiki)
    - 📁 = Cartella documenti locale
    - 📎 = Singoli file allegati (attachments nei messaggi)
    Combinazioni possibili: 📚, 📁, 📎, 📚📎, 📁📎
    Se is_cloud è True, prependi 🔒 a ogni combinazione.

    Args:
        conv_info: Dict da list_saved_conversations() con has_wiki, has_folder, has_documents
        is_cloud: True se il provider corrente è cloud

    Returns:
        Stringa icone (es. "🔒📁📎") o stringa vuota se non sensibile
    """
    parts: list[str] = []
    if conv_info.get("has_wiki"):
        parts.append("📚")
    if conv_info.get("has_folder"):
        parts.append("📁")
    if conv_info.get("has_documents"):
        parts.append("📎")

    if not parts:
        return ""

    icons = "".join(parts)
    return f"🔒{icons}" if is_cloud else icons


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

    # v1.9.0 - Pulisci cache socratica della sessione precedente, poi ripristina
    clear_socratic_cache()
    SocraticHistory.load_from_data(data.get("socratic_history", []))

    # v1.10.0 - Reset mappa sessione (la mappa va rigenerata sulla nuova conversazione)
    st.session_state["session_map_data"] = None
    st.session_state["n_domande_sessione"] = 0
    st.session_state["nudge_mostrato"] = False

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
