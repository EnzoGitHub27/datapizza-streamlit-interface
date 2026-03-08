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
from config.constants import VAULT_SESSION_KEY, VAULT_LAST_SYNC_KEY, VAULT_FILE_COUNT_KEY
from rag.vault import detect_vault_type, scan_vault_files
import time
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
                    if sel_entry["is_sensitive"] and is_cloud:
                        st.sidebar.error(
                            f"{sel_entry['icons']} Questa conversazione contiene "
                            f"dati locali ({sel_entry['reason']}). Non può essere "
                            "caricata con un provider cloud per motivi di privacy."
                        )
                    else:
                        # Controlla se ha vault pesante — se sì chiede conferma
                        needs_confirm = _has_heavy_kb(sel_entry["id"])
                        if needs_confirm:
                            st.session_state["pending_load_id"] = sel_entry["id"]
                            st.rerun()
                        else:
                            _load_conversation(sel_entry["id"])
                            st.rerun()

            with col_d:
                if st.button("🗑️ Elimina"):
                    delete_conversation(sel_entry["id"])
                    st.rerun()

            # Pannello conferma per vault pesanti
            pending_id = st.session_state.get("pending_load_id")
            if pending_id and pending_id == sel_entry["id"]:
                _show_load_warning(pending_id)
                col_ok, col_no = st.sidebar.columns(2)
                with col_ok:
                    if st.button("✅ Procedi", key="confirm_load"):
                        st.session_state.pop("pending_load_id", None)
                        _load_conversation(pending_id)
                        st.rerun()
                with col_no:
                    if st.button("❌ Annulla", key="cancel_load"):
                        st.session_state.pop("pending_load_id", None)
                        st.rerun()


def _get_conversation_icon(conv_info: dict, is_cloud: bool) -> str:
    """
    Genera icone da mostrare accanto alla conversazione.
    - 📚 KB Wiki, 📎 allegati
    - Vault: icona specifica (🟣 Obsidian, 🟤 LogSeq, ⬛ Notion, 📁 cartella)
    - 🔒 prefisso se is_cloud
    """
    parts: list[str] = []

    if conv_info.get("has_wiki"):
        parts.append("📚")

    if conv_info.get("has_folder"):
        # Rileva tipo vault per icona specifica
        folder_path = conv_info.get("kb_folder_path", "")
        if folder_path and Path(folder_path).exists():
            vault_info = detect_vault_type(folder_path)
            vault_type = vault_info.get("type", "folder")
            if vault_type == "obsidian":
                parts.append("🧠🟣")
            elif vault_type == "logseq":
                parts.append("🧠🟤")
            elif vault_type == "notion":
                parts.append("🧠⬛")
            else:
                parts.append("📁")
        else:
            parts.append("📁")

    if conv_info.get("has_documents"):
        parts.append("📎")

    if not parts:
        return ""

    icons = "".join(parts)
    return f"🔒{icons}" if is_cloud else icons


def _has_heavy_kb(conversation_id: str) -> bool:
    """
    Ritorna True se la conversazione ha una KB locale attiva
    con almeno 50 file — soglia per mostrare la conferma.
    """
    from core import load_conversation as _load_raw
    data = _load_raw(conversation_id)
    if not data:
        return False
    kb_settings = data.get("knowledge_base", {})
    if not kb_settings.get("use_knowledge_base", False):
        return False
    folder_path = kb_settings.get("kb_folder_path", "")
    if not folder_path or not Path(folder_path).exists():
        return False
    vault_info = detect_vault_type(folder_path)
    file_list = scan_vault_files(folder_path, vault_info)
    return len(file_list) >= 50


def _show_load_warning(conversation_id: str):
    """
    Mostra avviso informativo prima di caricare una conversazione
    con Knowledge Base attiva. Legge i metadati senza caricare
    l'intera conversazione.
    """
    from core import load_conversation as _load_raw
    data = _load_raw(conversation_id)
    if not data:
        return

    kb_settings = data.get("knowledge_base", {})
    if not kb_settings.get("use_knowledge_base", False):
        return

    folder_path = kb_settings.get("kb_folder_path", "")
    if not folder_path or not Path(folder_path).exists():
        return

    vault_info = detect_vault_type(folder_path)
    file_list = scan_vault_files(folder_path, vault_info)
    n_files = len(file_list)

    # Stima tempo: ~0.4 secondi per file (basato su benchmark reale)
    stima_sec = max(5, int(n_files * 0.4))
    if stima_sec < 60:
        stima_str = f"~{stima_sec}s"
    elif stima_sec < 300:
        minuti = stima_sec // 60
        stima_str = f"~{minuti} min"
    else:
        minuti = stima_sec // 60
        stima_str = f"~{minuti} min (operazione lunga)"

    st.sidebar.info(
        f"{vault_info['icon']} **{vault_info['label']}** — {n_files} file  \n"
        f"⏱️ Ri-indicizzazione stimata: {stima_str}"
    )


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
                # Re-indicizza con progress bar (v1.13.4 callback)
                progress_bar = st.sidebar.progress(
                    0, text="Re-indicizzazione in corso..."
                )

                def _progress_cb(*args, **kwargs):
                    # manager.py chiama con (message, float) nelle fasi iniziali
                    # vector_store.py chiama con (current, total, chunks_done, chunks_total) nel batching
                    if len(args) == 2 and isinstance(args[0], str):
                        # Fase caricamento/chunking: (messaggio, progress_float)
                        progress_bar.progress(
                            args[1],
                            text=args[0]
                        )
                    elif len(args) == 4:
                        # Fase batching ChromaDB: (current, total, chunks_done, chunks_total)
                        current, total, chunks_done, chunks_total = args
                        progress_bar.progress(
                            current / total,
                            text=f"Re-indicizzazione: {chunks_done}/{chunks_total} chunk"
                        )

                kb_manager.index_documents(progress_callback=_progress_cb)
                progress_bar.empty()

                # Aggiorna stato vault
                vault_info = detect_vault_type(folder_path)
                file_list = scan_vault_files(folder_path, vault_info)
                st.session_state[VAULT_SESSION_KEY]    = vault_info
                st.session_state[VAULT_LAST_SYNC_KEY]  = time.time()
                st.session_state[VAULT_FILE_COUNT_KEY] = len(file_list)
