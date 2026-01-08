# ui/sidebar/knowledge_base.py
# Datapizza v1.4.0 - Sidebar: Configurazione Knowledge Base
# ============================================================================

from pathlib import Path
from datetime import datetime
import streamlit as st

from config import (
    DEFAULT_CHUNK_SIZE,
    DEFAULT_CHUNK_OVERLAP,
    DEFAULT_TOP_K_RESULTS,
)
from config.settings import (
    load_wiki_config,
    get_available_wikis,
    get_wiki_adapter_config,
)
from rag import (
    KnowledgeBaseManager,
    TextChunker,
    LocalFolderAdapter,
    MediaWikiAdapter,
)


def render_knowledge_base_config(connection_type: str):
    """
    Renderizza la sezione Knowledge Base nella sidebar.
    
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
    
    # Configurazione sorgente
    st.sidebar.markdown("#### 📁 Sorgente Documenti")
    
    # Carica config wiki se disponibile
    wiki_config = load_wiki_config()
    wiki_mode = wiki_config.get("mode", "selectable") if wiki_config else "custom"
    
    # Determina opzioni disponibili per tipo sorgente
    adapter_options = ["Cartella Locale"]
    if wiki_config:
        adapter_options.append("MediaWiki")
    else:
        adapter_options.append("MediaWiki (URL custom)")
    
    adapter_type = st.sidebar.selectbox(
        "Tipo sorgente",
        adapter_options,
        help="Seleziona il tipo di sorgente documenti"
    )
    
    # ========== CARTELLA LOCALE ==========
    if adapter_type == "Cartella Locale":
        _render_local_folder_config()
    
    # ========== MEDIAWIKI ==========
    elif "MediaWiki" in adapter_type:
        _render_mediawiki_config(wiki_config, wiki_mode)
    
    # Statistiche Knowledge Base
    _render_kb_stats()


def _render_local_folder_config():
    """Renderizza configurazione per cartella locale."""
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
            kb_manager: KnowledgeBaseManager = st.session_state["kb_manager"]
            
            # Aggiorna parametri chunking
            kb_manager.chunker = TextChunker(
                chunk_size=st.session_state.get("kb_chunk_size", DEFAULT_CHUNK_SIZE),
                chunk_overlap=st.session_state.get("kb_chunk_overlap", DEFAULT_CHUNK_OVERLAP)
            )
            
            # Configura adapter
            adapter = LocalFolderAdapter({
                "folder_path": folder_path,
                "extensions": extensions,
                "recursive": recursive
            })
            kb_manager.set_adapter(adapter)
            
            # Indicizza
            if kb_manager.index_documents():
                st.sidebar.success("✅ Indicizzazione completata!")
            else:
                st.sidebar.error("❌ Errore indicizzazione")
        else:
            st.sidebar.error("❌ Percorso cartella non valido")


def _render_mediawiki_config(wiki_config, wiki_mode):
    """Renderizza configurazione per MediaWiki."""
    st.sidebar.markdown("#### 🌐 MediaWiki")
    
    # Verifica mwclient
    try:
        import mwclient
        mwclient_ok = True
    except ImportError:
        mwclient_ok = False
        st.sidebar.error("❌ mwclient non installato")
        st.sidebar.code("pip install mwclient", language="bash")
        return
    
    selected_wiki_url = None
    selected_wiki_config = {}
    
    if wiki_config and wiki_mode in ["fixed", "selectable"]:
        available_wikis = get_available_wikis(wiki_config)
        
        if wiki_mode == "fixed":
            # Modalità fissa: usa la wiki predefinita
            default_wiki_id = wiki_config.get("default_wiki")
            if default_wiki_id and default_wiki_id in wiki_config.get("wikis", {}):
                wiki_data = wiki_config["wikis"][default_wiki_id]
                selected_wiki_url = wiki_data.get("url", "")
                selected_wiki_config = get_wiki_adapter_config(
                    default_wiki_id, wiki_config, 
                    wiki_config.get("global_settings", {})
                )
                st.sidebar.info(f"📌 Wiki: **{wiki_data.get('name', default_wiki_id)}**")
                if wiki_data.get("description"):
                    st.sidebar.caption(wiki_data["description"])
            else:
                st.sidebar.error("❌ Nessuna wiki predefinita configurata")
        
        elif wiki_mode == "selectable":
            # Modalità selezionabile
            wiki_names = [w["name"] for w in available_wikis]
            wiki_ids = [w["id"] for w in available_wikis]
            
            if wiki_names:
                selected_name = st.sidebar.selectbox(
                    "Seleziona Wiki",
                    wiki_names,
                    help="Scegli una wiki dalla configurazione"
                )
                selected_idx = wiki_names.index(selected_name)
                selected_wiki_id = wiki_ids[selected_idx]
                
                wiki_data = wiki_config["wikis"][selected_wiki_id]
                selected_wiki_url = wiki_data.get("url", "")
                selected_wiki_config = get_wiki_adapter_config(
                    selected_wiki_id, wiki_config,
                    wiki_config.get("global_settings", {})
                )
                
                if wiki_data.get("description"):
                    st.sidebar.caption(wiki_data["description"])
            else:
                st.sidebar.warning("⚠️ Nessuna wiki configurata")
    
    # Modalità custom
    if wiki_mode == "custom" or not wiki_config:
        st.sidebar.markdown("**URL Wiki:**")
        custom_url = st.sidebar.text_input(
            "URL MediaWiki",
            value=st.session_state.get("mw_custom_url", ""),
            placeholder="https://wiki.example.com",
            help="URL base della wiki MediaWiki"
        )
        st.session_state["mw_custom_url"] = custom_url
        selected_wiki_url = custom_url
        
        api_path = st.sidebar.text_input(
            "API Path",
            value=st.session_state.get("mw_api_path", "/w/api.php"),
            help="Percorso endpoint API (default: /w/api.php)"
        )
        st.session_state["mw_api_path"] = api_path
        
        # Opzioni avanzate
        with st.sidebar.expander("⚙️ Opzioni avanzate", expanded=False):
            mw_namespace = st.number_input(
                "Namespace", 
                value=0, 
                min_value=0,
                help="0 = Main (articoli normali)"
            )
            mw_max_pages = st.number_input(
                "Max pagine",
                value=0,
                min_value=0,
                help="0 = tutte le pagine"
            )
            mw_auth = st.checkbox("Richiede autenticazione")
            
            if mw_auth:
                mw_user = st.text_input("Username")
                mw_pass = st.text_input("Password", type="password")
            else:
                mw_user = ""
                mw_pass = ""
        
        selected_wiki_config = {
            "url": custom_url,
            "api_path": api_path,
            "namespaces": [mw_namespace],
            "max_pages": mw_max_pages,
            "requires_auth": mw_auth,
            "username": mw_user,
            "password": mw_pass,
        }
    
    # Mostra info ultimo sync se disponibile
    if selected_wiki_url:
        temp_adapter = MediaWikiAdapter({"url": selected_wiki_url})
        last_sync = temp_adapter.get_last_sync_info()
        
        if last_sync:
            try:
                sync_time = datetime.fromisoformat(last_sync.get("timestamp", ""))
                st.sidebar.caption(f"🕐 Ultimo sync: {sync_time.strftime('%d/%m/%Y %H:%M')}")
                st.sidebar.caption(f"📄 Pagine: {last_sync.get('loaded_pages', 'N/A')}")
            except:
                pass
    
    # Parametri Chunking
    _render_chunking_params(key_prefix="mw")
    
    # Pulsante sincronizzazione
    if st.sidebar.button("🔄 Sincronizza Wiki", use_container_width=True, type="primary"):
        if selected_wiki_url:
            kb_manager: KnowledgeBaseManager = st.session_state["kb_manager"]
            
            # Aggiorna parametri chunking
            kb_manager.chunker = TextChunker(
                chunk_size=st.session_state.get("kb_chunk_size", DEFAULT_CHUNK_SIZE),
                chunk_overlap=st.session_state.get("kb_chunk_overlap", DEFAULT_CHUNK_OVERLAP)
            )
            
            # Configura adapter MediaWiki
            adapter = MediaWikiAdapter(selected_wiki_config)
            kb_manager.set_adapter(adapter)
            
            # Sincronizza e indicizza
            with st.spinner("🔄 Sincronizzazione in corso..."):
                if kb_manager.index_documents():
                    st.sidebar.success("✅ Wiki sincronizzata e indicizzata!")
                    st.session_state["mw_last_sync"] = datetime.now().isoformat()
                else:
                    st.sidebar.error("❌ Errore sincronizzazione")
        else:
            st.sidebar.error("❌ Specifica un URL wiki valido")


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
            DEFAULT_TOP_K_RESULTS
        )
        st.session_state["rag_top_k"] = top_k
    else:
        st.sidebar.info("💡 Configura una sorgente e sincronizza per iniziare")
