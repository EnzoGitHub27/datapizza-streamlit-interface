# ui/sidebar/knowledge_base.py
# DeepAiUG v1.4.1 - Sidebar: Configurazione Knowledge Base Multi-Tipo
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
    Renderizza la sezione Knowledge Base nella sidebar.
    Supporta: Cartella Locale, MediaWiki, DokuWiki.
    
    Args:
        connection_type: Tipo connessione corrente (per privacy check)
    """
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📚 Knowledge Base")
    
    # Toggle principale
    use_kb = st.sidebar.checkbox(
        "🔍 Usa Knowledge Base",
        value=st.session_state.get("use_knowledge_base", False),
        help="Cerca nei documenti prima di rispondere"
    )
    st.session_state["use_knowledge_base"] = use_kb
    
    if not use_kb:
        return
    
    # Avviso privacy
    if connection_type == "Cloud provider":
        st.sidebar.error("🔒 Cloud provider bloccato per privacy!")
    else:
        st.sidebar.success("🔒 Privacy OK - Dati locali")
    
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
    st.sidebar.markdown("#### 📁 Sorgente Documenti")
    
    if mode == "fixed" and available_sources:
        # Modalità fissa: usa la sorgente predefinita
        default_id = sources_config.get("default_source", sources_config.get("default_wiki"))
        source = next((s for s in available_sources if s["id"] == default_id), available_sources[0])
        st.sidebar.info(f"{source.get('icon', '📄')} **{source['name']}** (fisso)")
        _render_source_config(source, sources_config)
    
    elif mode == "selectable" and available_sources:
        # Modalità selezionabile: mostra dropdown con tutte le sorgenti
        _render_source_selector(available_sources, sources_config)
    
    else:
        # Modalità custom: permette scelta libera del tipo
        _render_custom_source_selector()
    
    # Statistiche Knowledge Base
    _render_kb_stats()


def _render_source_selector(sources: list, config: dict):
    """
    Renderizza selettore sorgenti con raggruppamento per tipo.
    """
    # Crea opzioni con icone
    source_options = []
    source_map = {}
    
    for source in sources:
        icon = source.get("icon", _get_type_icon(source.get("type", "local")))
        label = f"{icon} {source['name']}"
        source_options.append(label)
        source_map[label] = source
    
    # Aggiungi opzione custom se modalità lo permette
    if config.get("mode") == "custom" or not sources:
        source_options.append("➕ Configura manualmente...")
    
    selected_label = st.sidebar.selectbox(
        "Seleziona sorgente",
        source_options,
        help="Scegli una sorgente dalla configurazione"
    )
    
    if selected_label == "➕ Configura manualmente...":
        _render_custom_source_selector()
    else:
        source = source_map[selected_label]
        if source.get("description"):
            st.sidebar.caption(source["description"])
        _render_source_config(source, config)


def _render_custom_source_selector():
    """
    Renderizza selettore per configurazione manuale.
    """
    # Selezione tipo
    type_options = []
    for type_id, type_info in WIKI_TYPES.items():
        icon = type_info.get("icon", "📄")
        name = type_info.get("name", type_id)
        type_options.append(f"{icon} {name}")
    
    selected_type_label = st.sidebar.selectbox(
        "Tipo sorgente",
        type_options,
        help="Seleziona il tipo di sorgente documenti"
    )
    
    # Estrai tipo dall'etichetta
    type_ids = list(WIKI_TYPES.keys())
    selected_idx = type_options.index(selected_type_label)
    source_type = type_ids[selected_idx]
    
    # Verifica disponibilità
    if not is_source_type_available(source_type):
        missing_pkg = get_missing_package(source_type)
        st.sidebar.error(f"❌ Pacchetto `{missing_pkg}` non installato")
        st.sidebar.code(f"pip install {missing_pkg}", language="bash")
        return
    
    # Renderizza config specifica per tipo
    if source_type == "local":
        _render_local_folder_config()
    elif source_type == "mediawiki":
        _render_mediawiki_custom_config()
    elif source_type == "dokuwiki":
        _render_dokuwiki_custom_config()


def _render_source_config(source: dict, config: dict):
    """
    Renderizza configurazione per una sorgente dal file YAML.
    """
    source_type = source.get("type", "mediawiki")
    
    # Verifica disponibilità
    if not is_source_type_available(source_type):
        missing_pkg = get_missing_package(source_type)
        st.sidebar.error(f"❌ Pacchetto `{missing_pkg}` non installato")
        st.sidebar.code(f"pip install {missing_pkg}", language="bash")
        return
    
    # Ottieni config completa
    source_id = source["id"]
    adapter_config = get_source_adapter_config(
        source_id, config, 
        config.get("global_settings", {})
    )
    
    # Per tipo "local" mostra campi configurazione
    if source_type == "local":
        _render_local_folder_from_yaml(source, adapter_config)
        return
    
    # Mostra info ultimo sync se disponibile (solo per wiki)
    _show_last_sync_info(source_type, adapter_config)
    
    # Parametri Chunking
    _render_chunking_params(key_prefix=f"src_{source_id}")
    
    # Pulsante sincronizzazione
    button_label = "🔄 Sincronizza"
    
    if st.sidebar.button(button_label, use_container_width=True, type="primary"):
        _sync_source(source_type, adapter_config)


def _render_local_folder_from_yaml(source: dict, adapter_config: dict):
    """
    Renderizza configurazione per cartella locale da YAML.
    Permette di modificare il percorso preconfigurato.
    """
    source_id = source["id"]
    
    # Percorso dal YAML come default
    yaml_path = adapter_config.get("folder_path", "")
    session_key = f"kb_folder_path_{source_id}"
    
    # Usa il valore in session_state se già impostato, altrimenti usa YAML
    current_path = st.session_state.get(session_key, yaml_path)
    
    folder_path = st.sidebar.text_input(
        "Percorso cartella",
        value=current_path,
        placeholder="/path/to/documents",
        help="Percorso assoluto alla cartella con i documenti",
        key=f"input_{session_key}"
    )
    st.session_state[session_key] = folder_path
    st.session_state["kb_folder_path"] = folder_path  # Per compatibilità
    
    # Estensioni dal YAML o default
    yaml_extensions = adapter_config.get("extensions", [".md", ".txt", ".html"])
    ext_key = f"kb_extensions_{source_id}"
    saved_ext = st.session_state.get(ext_key, yaml_extensions)
    
    st.sidebar.markdown("**Formati file:**")
    col_ext1, col_ext2 = st.sidebar.columns(2)
    
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
    st.session_state["kb_extensions"] = extensions  # Per compatibilità
    
    # Ricorsivo
    yaml_recursive = adapter_config.get("recursive", True)
    recursive = st.sidebar.checkbox(
        "📂 Includi sottocartelle", 
        value=st.session_state.get(f"kb_recursive_{source_id}", yaml_recursive),
        key=f"recursive_{source_id}"
    )
    st.session_state[f"kb_recursive_{source_id}"] = recursive
    st.session_state["kb_recursive"] = recursive  # Per compatibilità
    
    # Parametri Chunking
    _render_chunking_params(key_prefix=f"local_{source_id}")
    
    # Pulsante indicizzazione
    if st.sidebar.button("🔄 Indicizza Documenti", use_container_width=True, type="primary"):
        if folder_path and Path(folder_path).exists():
            final_config = {
                "folder_path": folder_path,
                "extensions": extensions,
                "recursive": recursive
            }
            _sync_source("local", final_config)
        else:
            st.sidebar.error("❌ Percorso cartella non valido")


def _render_local_folder_config():
    """Renderizza configurazione per cartella locale (custom)."""
    folder_path = st.sidebar.text_input(
        "Percorso cartella",
        value=st.session_state.get("kb_folder_path", ""),
        placeholder="/path/to/documents",
        help="Percorso assoluto alla cartella con i documenti"
    )
    st.session_state["kb_folder_path"] = folder_path
    
    # Selezione estensioni
    st.sidebar.markdown("**Formati file:**")
    col_ext1, col_ext2 = st.sidebar.columns(2)
    
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
    
    recursive = st.sidebar.checkbox(
        "📂 Includi sottocartelle", 
        value=st.session_state.get("kb_recursive", True),
        key="recursive_check"
    )
    st.session_state["kb_recursive"] = recursive
    
    # Parametri Chunking
    _render_chunking_params(key_prefix="local")
    
    # Pulsante indicizzazione
    if st.sidebar.button("🔄 Indicizza Documenti", use_container_width=True, type="primary"):
        if folder_path and Path(folder_path).exists():
            adapter_config = {
                "folder_path": folder_path,
                "extensions": extensions,
                "recursive": recursive
            }
            _sync_source("local", adapter_config)
        else:
            st.sidebar.error("❌ Percorso cartella non valido")


def _render_mediawiki_custom_config():
    """Renderizza configurazione custom per MediaWiki."""
    st.sidebar.markdown("**URL Wiki:**")
    custom_url = st.sidebar.text_input(
        "URL MediaWiki",
        value=st.session_state.get("mw_custom_url", ""),
        placeholder="https://wiki.example.com",
        help="URL base della wiki MediaWiki"
    )
    st.session_state["mw_custom_url"] = custom_url
    
    api_path = st.sidebar.text_input(
        "API Path",
        value=st.session_state.get("mw_api_path", "/w/api.php"),
        help="Percorso endpoint API (default: /w/api.php)"
    )
    st.session_state["mw_api_path"] = api_path
    
    # Opzioni avanzate
    with st.sidebar.expander("⚙️ Opzioni avanzate", expanded=False):
        mw_namespace = st.number_input(
            "Namespace", value=0, min_value=0,
            help="0 = Main (articoli normali)"
        )
        mw_max_pages = st.number_input(
            "Max pagine", value=0, min_value=0,
            help="0 = tutte le pagine"
        )
        mw_auth = st.checkbox("Richiede autenticazione")
        
        if mw_auth:
            mw_user = st.text_input("Username")
            mw_pass = st.text_input("Password", type="password")
        else:
            mw_user = ""
            mw_pass = ""
    
    # Parametri Chunking
    _render_chunking_params(key_prefix="mw_custom")
    
    # Pulsante sincronizzazione
    if st.sidebar.button("🔄 Sincronizza Wiki", use_container_width=True, type="primary"):
        if custom_url:
            adapter_config = {
                "url": custom_url,
                "api_path": api_path,
                "namespaces": [mw_namespace],
                "max_pages": mw_max_pages,
                "requires_auth": mw_auth,
                "username": mw_user,
                "password": mw_pass,
            }
            _sync_source("mediawiki", adapter_config)
        else:
            st.sidebar.error("❌ Specifica un URL wiki valido")


def _render_dokuwiki_custom_config():
    """Renderizza configurazione custom per DokuWiki."""
    st.sidebar.markdown("**URL Wiki:**")
    custom_url = st.sidebar.text_input(
        "URL DokuWiki",
        value=st.session_state.get("dw_custom_url", ""),
        placeholder="https://docs.example.com",
        help="URL base della wiki DokuWiki"
    )
    st.session_state["dw_custom_url"] = custom_url
    
    # Opzioni avanzate
    with st.sidebar.expander("⚙️ Opzioni avanzate", expanded=False):
        dw_namespace = st.text_input(
            "Namespace (opzionale)",
            value="",
            help="Lascia vuoto per tutti i namespace"
        )
        dw_max_pages = st.number_input(
            "Max pagine", value=0, min_value=0,
            help="0 = tutte le pagine", key="dw_max"
        )
        dw_auth = st.checkbox("Richiede autenticazione", key="dw_auth")
        
        if dw_auth:
            dw_user = st.text_input("Username", key="dw_user")
            dw_pass = st.text_input("Password", type="password", key="dw_pass")
        else:
            dw_user = ""
            dw_pass = ""
    
    # Parametri Chunking
    _render_chunking_params(key_prefix="dw_custom")
    
    # Pulsante sincronizzazione
    if st.sidebar.button("🔄 Sincronizza DokuWiki", use_container_width=True, type="primary"):
        if custom_url:
            adapter_config = {
                "url": custom_url,
                "namespaces": [dw_namespace] if dw_namespace else [],
                "max_pages": dw_max_pages,
                "requires_auth": dw_auth,
                "username": dw_user,
                "password": dw_pass,
            }
            _sync_source("dokuwiki", adapter_config)
        else:
            st.sidebar.error("❌ Specifica un URL wiki valido")


def _sync_source(source_type: str, config: dict):
    """
    Sincronizza una sorgente creando l'adapter appropriato.
    """
    kb_manager: KnowledgeBaseManager = st.session_state["kb_manager"]
    
    # Aggiorna parametri chunking
    kb_manager.chunker = TextChunker(
        chunk_size=st.session_state.get("kb_chunk_size", DEFAULT_CHUNK_SIZE),
        chunk_overlap=st.session_state.get("kb_chunk_overlap", DEFAULT_CHUNK_OVERLAP)
    )
    
    # Crea adapter in base al tipo
    if source_type == "local":
        adapter = LocalFolderAdapter(config)
    elif source_type == "mediawiki":
        adapter = MediaWikiAdapter(config)
    elif source_type == "dokuwiki":
        adapter = DokuWikiAdapter(config)
    else:
        st.sidebar.error(f"❌ Tipo sorgente non supportato: {source_type}")
        return
    
    kb_manager.set_adapter(adapter)
    
    # Indicizza
    with st.spinner("🔄 Sincronizzazione in corso..."):
        if kb_manager.index_documents():
            st.sidebar.success("✅ Indicizzazione completata!")
        else:
            st.sidebar.error("❌ Errore indicizzazione")


def _show_last_sync_info(source_type: str, config: dict):
    """Mostra info ultimo sync se disponibile."""
    if source_type == "local":
        return
    
    try:
        if source_type == "mediawiki":
            adapter = MediaWikiAdapter(config)
        elif source_type == "dokuwiki":
            adapter = DokuWikiAdapter(config)
        else:
            return
        
        last_sync = adapter.get_last_sync_info()
        if last_sync:
            sync_time = datetime.fromisoformat(last_sync.get("timestamp", ""))
            st.sidebar.caption(f"🕐 Ultimo sync: {sync_time.strftime('%d/%m/%Y %H:%M')}")
            st.sidebar.caption(f"📄 Pagine: {last_sync.get('loaded_pages', 'N/A')}")
    except:
        pass


def _render_chunking_params(key_prefix: str):
    """Renderizza parametri di chunking."""
    with st.sidebar.expander("⚙️ Parametri Chunking", expanded=False):
        st.caption("Controlla come i documenti vengono suddivisi")
        
        chunk_size = st.slider(
            "Dimensione chunk (caratteri)",
            min_value=200,
            max_value=3000,
            value=st.session_state.get("kb_chunk_size", DEFAULT_CHUNK_SIZE),
            step=100,
            key=f"{key_prefix}_chunk_size",
            help="Dimensione massima di ogni chunk"
        )
        st.session_state["kb_chunk_size"] = chunk_size
        
        chunk_overlap = st.slider(
            "Overlap (caratteri)",
            min_value=0,
            max_value=500,
            value=st.session_state.get("kb_chunk_overlap", DEFAULT_CHUNK_OVERLAP),
            step=50,
            key=f"{key_prefix}_chunk_overlap",
            help="Sovrapposizione tra chunk consecutivi"
        )
        st.session_state["kb_chunk_overlap"] = chunk_overlap
        
        st.caption(f"📊 Ratio overlap: {chunk_overlap/chunk_size*100:.0f}%")


def _render_kb_stats():
    """Renderizza statistiche Knowledge Base."""
    kb_manager: KnowledgeBaseManager = st.session_state.get("kb_manager")
    
    if kb_manager and kb_manager.is_indexed():
        stats = kb_manager.get_stats()
        st.sidebar.markdown("#### 📊 Statistiche")
        
        col_s1, col_s2 = st.sidebar.columns(2)
        col_s1.metric("📄 Documenti", stats.get("document_count", 0))
        col_s2.metric("📦 Chunks", stats.get("chunk_count", 0))
        
        if stats.get("last_indexed"):
            try:
                dt = datetime.fromisoformat(stats["last_indexed"])
                st.sidebar.caption(f"🕐 Ultimo update: {dt.strftime('%d/%m %H:%M')}")
            except:
                pass
        
        if stats.get("using_chromadb"):
            st.sidebar.caption("💾 Storage: ChromaDB (persistente)")
        else:
            st.sidebar.caption("⚠️ Storage: Memoria (temporaneo)")
        
        # Parametri RAG
        st.sidebar.markdown("#### ⚙️ Parametri RAG")
        top_k = st.sidebar.slider(
            "Documenti per query", 
            1, 10, 
            st.session_state.get("rag_top_k", DEFAULT_TOP_K_RESULTS)
        )
        st.session_state["rag_top_k"] = top_k
    else:
        st.sidebar.info("💡 Configura una sorgente e sincronizza per iniziare")


def _get_type_icon(source_type: str) -> str:
    """Ritorna icona per tipo sorgente."""
    type_info = WIKI_TYPES.get(source_type, {})
    return type_info.get("icon", "📄")
