# ui/sidebar/knowledge_base.py
# Datapizza v1.4.1 - Sidebar: Configurazione Knowledge Base (Refactored for Layout Agnosticism)
# ============================================================================

from pathlib import Path
from datetime import datetime
import streamlit as st

from config import (
    DEFAULT_CHUNK_SIZE,
    DEFAULT_CHUNK_OVERLAP,
    DEFAULT_TOP_K_RESULTS,
    WIKI_TYPES,
)
from config.settings import (
    load_wiki_config,
    get_available_sources,
    get_source_adapter_config,
    is_source_type_available,
    get_missing_package,
)
from rag import (
    KnowledgeBaseManager,
    TextChunker,
    LocalFolderAdapter,
    MediaWikiAdapter,
    DokuWikiAdapter,
)


def render_knowledge_base_config(connection_type: str):
    """
    Renderizza la sezione Knowledge Base (Layout Agnostic).
    Supporta: Cartella Locale, MediaWiki, DokuWiki.
    
    Args:
        connection_type: Tipo connessione corrente (per privacy check)
    """
    st.markdown("---")
    st.markdown("### 📚 Knowledge Base")
    
    # Toggle principale
    use_kb = st.checkbox(
        "🔍 Usa Knowledge Base",
        value=st.session_state.get("use_knowledge_base", False),
        help="Cerca nei documenti prima di rispondere"
    )
    st.session_state["use_knowledge_base"] = use_kb
    
    if not use_kb:
        return
    
    # Avviso privacy
    if connection_type == "Cloud provider":
        st.error("🔒 Cloud provider bloccato per privacy!")
    else:
        st.success("🔒 Privacy OK - Dati locali")
    
    # Carica config sorgenti
    sources_config = load_wiki_config()
    
    # Determina modalità
    if sources_config:
        mode = sources_config.get("mode", "selectable")
        available_sources = get_available_sources(sources_config)
    else:
        mode = "custom"
        available_sources = []
    
    # ========== SELEZIONE TIPO SORGENTE ==========
    st.markdown("#### 📁 Sorgente Documenti")
    
    if mode == "fixed" and available_sources:
        # Modalità fissa
        default_id = sources_config.get("default_source", sources_config.get("default_wiki"))
        source = next((s for s in available_sources if s["id"] == default_id), available_sources[0])
        st.info(f"{source.get('icon', '📄')} **{source['name']}** (fisso)")
        _render_source_config(source, sources_config)
    
    elif mode == "selectable" and available_sources:
        # Modalità selezionabile
        _render_source_selector(available_sources, sources_config)
    
    else:
        # Modalità custom
        _render_custom_source_selector()
    
    # Statistiche Knowledge Base
    _render_kb_stats()


def _render_source_selector(sources: list, config: dict):
    """Renderizza selettore sorgenti."""
    source_options = []
    source_map = {}
    
    for source in sources:
        icon = source.get("icon", _get_type_icon(source.get("type", "local")))
        label = f"{icon} {source['name']}"
        source_options.append(label)
        source_map[label] = source
    
    if config.get("mode") == "custom" or not sources:
        source_options.append("➕ Configura manualmente...")
    
    selected_label = st.selectbox(
        "Seleziona sorgente",
        source_options,
        help="Scegli una sorgente dalla configurazione"
    )
    
    if selected_label == "➕ Configura manualmente...":
        _render_custom_source_selector()
    else:
        source = source_map[selected_label]
        if source.get("description"):
            st.caption(source["description"])
        _render_source_config(source, config)


def _render_custom_source_selector():
    """Renderizza selettore per configurazione manuale."""
    type_options = []
    for type_id, type_info in WIKI_TYPES.items():
        icon = type_info.get("icon", "📄")
        name = type_info.get("name", type_id)
        type_options.append(f"{icon} {name}")
    
    selected_type_label = st.selectbox(
        "Tipo sorgente",
        type_options,
        help="Seleziona il tipo di sorgente documenti"
    )
    
    type_ids = list(WIKI_TYPES.keys())
    selected_idx = type_options.index(selected_type_label)
    source_type = type_ids[selected_idx]
    
    if not is_source_type_available(source_type):
        missing_pkg = get_missing_package(source_type)
        st.error(f"❌ Pacchetto `{missing_pkg}` non installato")
        st.code(f"pip install {missing_pkg}", language="bash")
        return
    
    if source_type == "local":
        _render_local_folder_config()
    elif source_type == "mediawiki":
        _render_mediawiki_custom_config()
    elif source_type == "dokuwiki":
        _render_dokuwiki_custom_config()


def _render_source_config(source: dict, config: dict):
    """Renderizza configurazione sorgente."""
    source_type = source.get("type", "mediawiki")
    
    if not is_source_type_available(source_type):
        missing_pkg = get_missing_package(source_type)
        st.error(f"❌ Pacchetto `{missing_pkg}` non installato")
        st.code(f"pip install {missing_pkg}", language="bash")
        return
    
    source_id = source["id"]
    adapter_config = get_source_adapter_config(
        source_id, config, 
        config.get("global_settings", {})
    )
    
    if source_type == "local":
        _render_local_folder_from_yaml(source, adapter_config)
        return
    
    _show_last_sync_info(source_type, adapter_config)
    _render_chunking_params(key_prefix=f"src_{source_id}")
    
    st.button(
        "🔄 Sincronizza", 
        use_container_width=True, 
        type="primary", 
        key=f"kb_sync_source_{source_id}",
        on_click=_sync_source_callback,
        args=(source_type, adapter_config, source_id)
    )
    
    status = st.session_state.get(f"sync_result_{source_id}")
    if status == "success":
        st.success("✅ Indicizzazione completata!")
        del st.session_state[f"sync_result_{source_id}"]
    elif status == "error_generic":
        st.error("❌ Errore indicizzazione")
        del st.session_state[f"sync_result_{source_id}"]
    elif status and status.startswith("error"):
         st.error(f"❌ {status}")
         del st.session_state[f"sync_result_{source_id}"]


def _render_local_folder_from_yaml(source: dict, adapter_config: dict):
    """Renderizza configurazione locale da YAML."""
    source_id = source["id"]
    
    yaml_path = adapter_config.get("folder_path", "")
    session_key = f"kb_folder_path_{source_id}"
    current_path = st.session_state.get(session_key, yaml_path)
    
    folder_path = st.text_input(
        "Percorso cartella",
        value=current_path,
        placeholder="/path/to/documents",
        help="Percorso assoluto",
        key=f"input_{session_key}"
    )
    st.session_state[session_key] = folder_path
    st.session_state["kb_folder_path"] = folder_path
    
    yaml_extensions = adapter_config.get("extensions", [".md", ".txt", ".html"])
    ext_key = f"kb_extensions_{source_id}"
    saved_ext = st.session_state.get(ext_key, yaml_extensions)
    
    st.markdown("**Formati file:**")
    col_ext1, col_ext2 = st.columns(2)
    
    with col_ext1:
        use_md = st.checkbox(".md", value=".md" in saved_ext, key=f"ext_md_{source_id}")
        use_txt = st.checkbox(".txt", value=".txt" in saved_ext, key=f"ext_txt_{source_id}")
    with col_ext2:
        use_html = st.checkbox(".html", value=".html" in saved_ext, key=f"ext_html_{source_id}")
        use_pdf = st.checkbox(".pdf", value=".pdf" in saved_ext, key=f"ext_pdf_{source_id}")
    
    extensions = []
    if use_md: extensions.append(".md")
    if use_txt: extensions.append(".txt")
    if use_html: extensions.extend([".html", ".htm"])
    if use_pdf: extensions.append(".pdf")
    st.session_state[ext_key] = extensions
    st.session_state["kb_extensions"] = extensions
    
    yaml_recursive = adapter_config.get("recursive", True)
    recursive = st.checkbox(
        "📂 Includi sottocartelle", 
        value=st.session_state.get(f"kb_recursive_{source_id}", yaml_recursive),
        key=f"recursive_{source_id}"
    )
    st.session_state[f"kb_recursive_{source_id}"] = recursive
    st.session_state["kb_recursive"] = recursive
    
    _render_chunking_params(key_prefix=f"local_{source_id}")
    
    st.button(
        "🔄 Indicizza Documenti", 
        use_container_width=True, 
        type="primary", 
        key=f"kb_sync_local_{source_id}",
        on_click=_sync_source_callback,
        args=("local", {
            "folder_path": folder_path,
            "extensions": extensions,
            "recursive": recursive
        }, source_id)
    )

    status = st.session_state.get(f"sync_result_{source_id}")
    if status == "success":
        st.success("✅ Indicizzazione completata!")
        del st.session_state[f"sync_result_{source_id}"]
    elif status == "error_generic":
        st.error("❌ Errore indicizzazione")
        del st.session_state[f"sync_result_{source_id}"]
    elif status and status.startswith("error"):
         st.error(f"❌ {status}")
         del st.session_state[f"sync_result_{source_id}"]


def _render_local_folder_config():
    """Renderizza configurazione locale custom."""
    folder_path = st.text_input(
        "Percorso cartella",
        value=st.session_state.get("kb_folder_path", ""),
        placeholder="/path/to/documents"
    )
    st.session_state["kb_folder_path"] = folder_path
    
    st.markdown("**Formati file:**")
    col_ext1, col_ext2 = st.columns(2)
    saved_ext = st.session_state.get("kb_extensions", [".md", ".txt", ".html"])
    with col_ext1:
        use_md = st.checkbox(".md", value=".md" in saved_ext, key="ext_md")
        use_txt = st.checkbox(".txt", value=".txt" in saved_ext, key="ext_txt")
    with col_ext2:
        use_html = st.checkbox(".html", value=".html" in saved_ext, key="ext_html")
        use_pdf = st.checkbox(".pdf", value=".pdf" in saved_ext, key="ext_pdf")
    
    extensions = []
    if use_md: extensions.append(".md")
    if use_txt: extensions.append(".txt")
    if use_html: extensions.extend([".html", ".htm"])
    if use_pdf: extensions.append(".pdf")
    st.session_state["kb_extensions"] = extensions
    
    recursive = st.checkbox(
        "📂 Includi sottocartelle", 
        value=st.session_state.get("kb_recursive", True),
        key="recursive_check"
    )
    st.session_state["kb_recursive"] = recursive
    
    _render_chunking_params(key_prefix="local")
    
    st.button(
        "🔄 Indicizza Documenti", 
        use_container_width=True, 
        type="primary", 
        key="kb_sync_local_custom",
        on_click=_sync_source_callback,
        args=("local", {
            "folder_path": folder_path,
            "extensions": extensions,
            "recursive": recursive
        }, "custom_local")
    )
    
    status = st.session_state.get("sync_result_custom_local")
    if status == "success":
        st.success("✅ Indicizzazione completata!")
        del st.session_state["sync_result_custom_local"]
    elif status:
        st.error(f"❌ Errore: {status}")
        del st.session_state["sync_result_custom_local"]


def _render_mediawiki_custom_config():
    """Renderizza configurazione MediaWiki custom."""
    st.markdown("**URL Wiki:**")
    custom_url = st.text_input(
        "URL MediaWiki",
        value=st.session_state.get("mw_custom_url", ""),
        placeholder="https://wiki.example.com"
    )
    st.session_state["mw_custom_url"] = custom_url
    
    api_path = st.text_input(
        "API Path",
        value=st.session_state.get("mw_api_path", "/w/api.php")
    )
    st.session_state["mw_api_path"] = api_path
    
    with st.expander("⚙️ Opzioni avanzate", expanded=False):
        mw_namespace = st.number_input("Namespace", value=0, min_value=0)
        mw_max_pages = st.number_input("Max pagine", value=0, min_value=0)
        mw_auth = st.checkbox("Richiede autenticazione")
        
        if mw_auth:
            mw_user = st.text_input("Username")
            mw_pass = st.text_input("Password", type="password")
        else:
            mw_user, mw_pass =("", "")
    
    _render_chunking_params(key_prefix="mw_custom")
    
    st.button(
        "🔄 Sincronizza Wiki", 
        use_container_width=True, 
        type="primary", 
        key="kb_sync_mediawiki_custom",
        on_click=_sync_source_callback,
        args=("mediawiki", {
                "url": custom_url,
                "api_path": api_path,
                "namespaces": [mw_namespace],
                "max_pages": mw_max_pages,
                "requires_auth": mw_auth,
                "username": mw_user,
                "password": mw_pass,
            }, "custom_mw")
    )
    
    status = st.session_state.get("sync_result_custom_mw")
    if status == "success":
        st.success("✅ Indicizzazione completata!")
        del st.session_state["sync_result_custom_mw"]
    elif status:
        st.error(f"❌ Errore: {status}")
        del st.session_state["sync_result_custom_mw"]


def _render_dokuwiki_custom_config():
    """Renderizza configurazione DokuWiki custom."""
    st.markdown("**URL Wiki:**")
    custom_url = st.text_input(
        "URL DokuWiki",
        value=st.session_state.get("dw_custom_url", ""),
        placeholder="https://docs.example.com"
    )
    st.session_state["dw_custom_url"] = custom_url
    
    with st.expander("⚙️ Opzioni avanzate", expanded=False):
        dw_namespace = st.text_input("Namespace (opzionale)", value="")
        dw_max_pages = st.number_input("Max pagine", value=0, min_value=0, key="dw_max")
        dw_auth = st.checkbox("Richiede autenticazione", key="dw_auth")
        
        if dw_auth:
            dw_user = st.text_input("Username", key="dw_user")
            dw_pass = st.text_input("Password", type="password", key="dw_pass")
        else:
            dw_user, dw_pass = ("", "")
    
    _render_chunking_params(key_prefix="dw_custom")
    
    st.button(
        "🔄 Sincronizza DokuWiki", 
        use_container_width=True, 
        type="primary", 
        key="kb_sync_dokuwiki_custom",
        on_click=_sync_source_callback,
        args=("dokuwiki", {
                "url": custom_url,
                "namespaces": [dw_namespace] if dw_namespace else [],
                "max_pages": dw_max_pages,
                "requires_auth": dw_auth,
                "username": dw_user,
                "password": dw_pass,
            }, "custom_dw")
    )
    
    status = st.session_state.get("sync_result_custom_dw")
    if status == "success":
        st.success("✅ Indicizzazione completata!")
        del st.session_state["sync_result_custom_dw"]
    elif status:
        st.error(f"❌ Errore: {status}")
        del st.session_state["sync_result_custom_dw"]


def _sync_source_callback(source_type, config, source_id):
    """Callback sincronizzazione (wrapper)."""
    try:
        kb_manager = st.session_state["kb_manager"]
        kb_manager.chunker = TextChunker(
            chunk_size=st.session_state.get("kb_chunk_size", DEFAULT_CHUNK_SIZE),
            chunk_overlap=st.session_state.get("kb_chunk_overlap", DEFAULT_CHUNK_OVERLAP)
        )
        
        adapter = None
        if source_type == "local":
            adapter = LocalFolderAdapter(config)
        elif source_type == "mediawiki":
            adapter = MediaWikiAdapter(config)
        elif source_type == "dokuwiki":
            adapter = DokuWikiAdapter(config)
        
        if adapter:
            kb_manager.set_adapter(adapter)
            if kb_manager.index_documents():
                st.session_state[f"sync_result_{source_id}"] = "success"
            else:
                st.session_state[f"sync_result_{source_id}"] = "error_generic"
        else:
            st.session_state[f"sync_result_{source_id}"] = "error_adapter"
            
    except Exception as e:
        st.session_state[f"sync_result_{source_id}"] = f"error: {str(e)}"

def _sync_source(source_type: str, config: dict):
    # Legacy wrapper if needed, but we will replace usages.
    pass



def _show_last_sync_info(source_type: str, config: dict):
    """Mostra info sync."""
    if source_type == "local": return
    try:
        if source_type == "mediawiki": adapter = MediaWikiAdapter(config)
        elif source_type == "dokuwiki": adapter = DokuWikiAdapter(config)
        else: return
        
        last_sync = adapter.get_last_sync_info()
        if last_sync:
            sync_time = datetime.fromisoformat(last_sync.get("timestamp", ""))
            st.caption(f"🕐 Ultimo sync: {sync_time.strftime('%d/%m %H:%M')}")
            st.caption(f"📄 Pagine: {last_sync.get('loaded_pages', 'N/A')}")
    except:
        pass


def _render_chunking_params(key_prefix: str):
    """Renderizza parametri di chunking."""
    with st.expander("⚙️ Parametri Chunking", expanded=False):
        chunk_size = st.slider(
            "Dimensione chunk",
            200, 3000, 
            st.session_state.get("kb_chunk_size", DEFAULT_CHUNK_SIZE),
            100,
            key=f"{key_prefix}_chunk_size"
        )
        st.session_state["kb_chunk_size"] = chunk_size
        
        chunk_overlap = st.slider(
            "Overlap",
            0, 500,
            st.session_state.get("kb_chunk_overlap", DEFAULT_CHUNK_OVERLAP),
            50,
            key=f"{key_prefix}_chunk_overlap"
        )
        st.session_state["kb_chunk_overlap"] = chunk_overlap


def _render_kb_stats():
    """Renderizza statistiche KB."""
    kb_manager = st.session_state.get("kb_manager")
    
    if kb_manager and kb_manager.is_indexed():
        stats = kb_manager.get_stats()
        st.markdown("#### 📊 Statistiche")
        
        c1, c2 = st.columns(2)
        c1.metric("📄 Docs", stats.get("document_count", 0))
        c2.metric("📦 Chunks", stats.get("chunk_count", 0))
        
        if stats.get("last_indexed"):
            try:
                dt = datetime.fromisoformat(stats["last_indexed"])
                st.caption(f"🕐 {dt.strftime('%d/%m %H:%M')}")
            except: pass
        
        # Parametri RAG
        st.markdown("#### ⚙️ RAG")
        top_k = st.slider(
            "Top K", 1, 10,
            st.session_state.get("rag_top_k", DEFAULT_TOP_K_RESULTS)
        )
        st.session_state["rag_top_k"] = top_k
    else:
        st.info("💡 Configura e sincronizza per iniziare")


def _get_type_icon(source_type: str) -> str:
    type_info = WIKI_TYPES.get(source_type, {})
    return type_info.get("icon", "📄")
