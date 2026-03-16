# app.py
# DeepAiUG v1.9.0 - Entry Point
# ============================================================================
# Interfaccia Streamlit modulare per LLM con:
# - Ollama locale / Remote / Cloud providers
# - Knowledge Base RAG (LocalFolder + MediaWiki + DokuWiki)
# - Export conversazioni (MD, JSON, TXT, PDF)
# - Persistenza conversazioni
# - v1.5.0: File Upload in Chat (Privacy-First)
# - v1.5.0: Privacy Warning per passaggio Local→Cloud con documenti
# - v1.6.0: Streaming responses
# - v1.6.1: Bottoni socratici (Genera alternative)
# - v1.8.0: UI Socratica completa (Confuta, Rifletti, Toggle Mode)
# ============================================================================

from datetime import datetime
import streamlit as st

# ============================================================================
# CONFIG & CONSTANTS
# ============================================================================

from config import (
    VERSION,
    DEFAULT_CHUNK_SIZE,
    DEFAULT_CHUNK_OVERLAP,
    DEFAULT_TOP_K_RESULTS,
    DEFAULT_SOCRATIC_MODE,  # v1.8.0
    DEFAULT_SESSION_MAP_MODE,           # v1.10.0
    SESSION_MAP_NUDGE_THRESHOLD,        # v1.10.0
    SESSION_MAP_PROGRESSIVE_VISIBLE_AFTER,  # v1.10.0
    APP_TITLE,              # v1.10.0 - Branding
    APP_ICON,               # v1.10.0 - Branding
    APP_SUBTITLE,           # v1.10.0 - Branding
    NEWS_BANNER_ENABLED,    # v1.10.0 - Branding
    NEWS_BANNER_TEXT,        # v1.10.0 - Branding
    NEWS_BANNER_VERSION,    # v1.10.0 - Branding
)

# ============================================================================
# CORE
# ============================================================================

from core import (
    create_client,
    get_local_ollama_models,
    save_conversation,
    generate_conversation_id,
    get_conversation_history,
    create_message,
    estimate_tokens,
    KB_METADATA_DEFAULT,
    search_chat_kb,
    reindex_all_chat_kb,
    get_kb_chat_stats,
)

# 🆕 v1.5.0 - File processors
from core.file_processors import get_attachment_names

# ============================================================================
# RAG
# ============================================================================

from rag import KnowledgeBaseManager

# ============================================================================
# EXPORT
# ============================================================================

from export import (
    get_messages_for_export,
    export_to_markdown,
    export_to_json,
    export_to_txt,
)

# ============================================================================
# UI
# ============================================================================

from ui import (
    MAIN_CSS,
    render_chat_message,
    render_llm_config,
    render_knowledge_base_config,
    render_conversations_manager,
    render_export_section,
    render_export_preview,
)
from ui.sidebar.kb_panel import render_kb_panel
from ui.sidebar import render_socratic_mode_settings

# 🆕 v1.5.0 - File upload widget
from ui.file_upload import (
    render_file_upload_widget,
    enrich_prompt_with_files,
    is_vision_model,
    store_pending_files,
    get_pending_files,
    clear_pending_files,
)

# 🆕 v1.5.0 - Privacy warning dialog
from ui.privacy_warning import (
    check_privacy_risk,
    render_privacy_dialog,
    handle_privacy_action,
    render_privacy_warning_banner,
    reset_privacy_flags,
    should_show_privacy_dialog,
)

# 🆕 v1.6.1 - Socratic module
# 🆕 v1.9.0 - Aggiunto render_socratic_history_sidebar, SocraticHistory
from ui.socratic import clear_socratic_cache, render_socratic_history_sidebar, SocraticHistory

# 🆕 v1.10.0 - Session Map (F2)
from ui.socratic import SessionMapAnalyzer, get_nudge_text
from ui.sidebar.session_map_widget import (
    render_session_map_settings,
    render_session_map_display,
    render_nudge_sidebar,
    render_generate_map_button,
)

# v1.11.1 - Matrix Theme
from ui.style import inject_matrix_style

# ============================================================================
# PAGE CONFIG
# ============================================================================

st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

# v1.11.1 - Matrix Theme
inject_matrix_style()

# Inject CSS
st.markdown(MAIN_CSS, unsafe_allow_html=True)

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

def initialize_session_state():
    """Inizializza tutte le variabili di sessione necessarie."""
    defaults = {
        "messages": [],
        "conversation_id": generate_conversation_id(),
        "conversation_created_at": datetime.now().isoformat(),
        "total_tokens_estimate": 0,
        "auto_save_enabled": True,
        "kb_manager": KnowledgeBaseManager(),
        "use_knowledge_base": False,
        "connection_type": "Local (Ollama)",
        "current_model": "",
        "models_local": [],
        "show_export_preview": False,
        # KB settings
        "kb_folder_path": "",
        "kb_extensions": [".md", ".txt"],
        "kb_recursive": True,
        "kb_chunk_size": DEFAULT_CHUNK_SIZE,
        "kb_chunk_overlap": DEFAULT_CHUNK_OVERLAP,
        "rag_top_k": DEFAULT_TOP_K_RESULTS,
        # 🆕 v1.5.0 - File upload
        "pending_files": [],
        "pending_has_images": False,
        "pending_warning": None,
        # v1.5.0 - Privacy tracking
        "documents_uploaded_this_session": False,
        "uploaded_files_history": [],
        "privacy_acknowledged_for_cloud": False,
        "show_privacy_dialog": False,
        # v1.14.0 - KB Metadata (chat come Knowledge Base epistemica)
        "kb_metadata": dict(KB_METADATA_DEFAULT),
        "use_chat_kb": False,
        "chat_kb_tipo_filter": [],
        # v1.8.0 - Socratic mode
        "socratic_mode": DEFAULT_SOCRATIC_MODE,
        # v1.10.0 - Session Map (F2)
        "session_map_mode": DEFAULT_SESSION_MAP_MODE,
        "session_map_data": None,
        "n_domande_sessione": 0,
        "nudge_mostrato": False,
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

initialize_session_state()

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def add_message(
    role: str, 
    content: str, 
    model: str = None, 
    sources: list = None,
    attachments: list = None  # 🆕 v1.5.0
):
    """
    Aggiunge un messaggio alla conversazione e salva.
    
    Args:
        role: "user" o "assistant"
        content: Contenuto del messaggio
        model: Nome modello (per assistant)
        sources: Fonti RAG (opzionale)
        attachments: Nomi file allegati (opzionale) 🆕
    """
    message = create_message(role, content, model, sources)
    
    # 🆕 v1.5.0 - Aggiungi attachments se presenti
    if attachments:
        message["attachments"] = attachments
    
    st.session_state["messages"].append(message)
    st.session_state["total_tokens_estimate"] += estimate_tokens(content)
    
    if st.session_state.get("auto_save_enabled", True):
        _save_current_conversation()

def _save_current_conversation():
    """Salva la conversazione corrente su disco."""
    save_conversation(
        conversation_id=st.session_state["conversation_id"],
        created_at=st.session_state["conversation_created_at"],
        messages=st.session_state["messages"],
        model=st.session_state.get("current_model", ""),
        provider=st.session_state.get("connection_type", ""),
        tokens_estimate=st.session_state.get("total_tokens_estimate", 0),
        kb_settings={
            "use_knowledge_base": st.session_state.get("use_knowledge_base", False),
            "kb_folder_path": st.session_state.get("kb_folder_path", ""),
            "kb_extensions": st.session_state.get("kb_extensions", []),
            "kb_recursive": st.session_state.get("kb_recursive", True),
            "kb_chunk_size": st.session_state.get("kb_chunk_size", DEFAULT_CHUNK_SIZE),
            "kb_chunk_overlap": st.session_state.get("kb_chunk_overlap", DEFAULT_CHUNK_OVERLAP),
            "rag_top_k": st.session_state.get("rag_top_k", DEFAULT_TOP_K_RESULTS),
        },
        socratic_history=SocraticHistory.to_serializable(),  # v1.9.0
        kb_metadata=st.session_state.get("kb_metadata"),  # v1.14.0
    )

def reset_conversation():
    """Resetta la conversazione corrente."""
    st.session_state["messages"] = []
    st.session_state["conversation_id"] = generate_conversation_id()
    st.session_state["conversation_created_at"] = datetime.now().isoformat()
    st.session_state["total_tokens_estimate"] = 0
    # v1.14.0 - Reset KB metadata
    st.session_state["kb_metadata"] = dict(KB_METADATA_DEFAULT)
    # 🆕 v1.5.0 - Pulisci anche file pending e flag privacy
    clear_pending_files()
    reset_privacy_flags()
    # 🆕 v1.6.1 - Pulisci cache socratica
    clear_socratic_cache()
    # 🆕 v1.9.0 - Pulisci storico socratico
    SocraticHistory.clear_history()
    # 🆕 v1.10.0 - Reset mappa sessione
    st.session_state["session_map_data"] = None
    st.session_state["n_domande_sessione"] = 0
    st.session_state["nudge_mostrato"] = False

# ============================================================================
# 🆕 v1.6.1 - SOCRATIC CLIENT HELPER
# ============================================================================

def get_socratic_client(connection_type, provider, api_key, model, base_url, temperature):
    """
    Crea un client LLM per i bottoni socratici.
    Ritorna None se non è possibile crearlo.
    """
    if not model:
        return None
    
    try:
        return create_client(
            connection_type,
            provider,
            api_key,
            model,
            "Sei un assistente che genera prospettive alternative e stimola la riflessione critica.",
            base_url,
            temperature
        )
    except Exception:
        return None

# ============================================================================
# SIDEBAR — v1.12.0 Architettura Sidebar
# ============================================================================

# 1. ⚙️ Configurazione (chiusa di default)
config_expander = st.sidebar.expander("⚙️ Configurazione", expanded=False)
(
    connection_type,
    provider,
    api_key,
    model,
    base_url,
    system_prompt,
    temperature,
    max_messages,
) = render_llm_config(container=config_expander)
render_knowledge_base_config(connection_type, container=config_expander)

# 2. 💬 Conversazione (aperta)
render_conversations_manager()

# --------------------------------------------------------------------------
# 2b–2e. KB Chat — ordine logico: flagga → aggiorna → gestisci → usa
# --------------------------------------------------------------------------

# 2b. 📚 Includi nella KB (azione sulla chat corrente)
with st.sidebar.expander("📚 Includi nella Knowledge Base", expanded=False):
    st.caption("Flagga questa conversazione per includerla nella KB alla prossima indicizzazione")

    _kb_meta = st.session_state.get("kb_metadata", dict(KB_METADATA_DEFAULT))

    _includi = st.checkbox(
        "Includi questa chat nella Knowledge Base",
        value=_kb_meta.get("includi_in_kb", False),
        key="kb_meta_includi",
    )

    _rilevanza_map = {"Bassa": 1, "Media": 2, "Alta": 3}
    _rilevanza_label = st.radio(
        "Rilevanza",
        list(_rilevanza_map.keys()),
        index=_kb_meta.get("rilevanza", 1) - 1,
        horizontal=True,
        key="kb_meta_rilevanza",
        disabled=not _includi,
    )

    _tipo_opzioni = ["decisione", "insight", "memoria_aziendale", "riferimento", "sperimentale"]
    _tipo = st.multiselect(
        "Tipo",
        _tipo_opzioni,
        default=[t for t in _kb_meta.get("tipo", []) if t in _tipo_opzioni],
        key="kb_meta_tipo",
        disabled=not _includi,
    )

    _note = st.text_input(
        "Note",
        value=_kb_meta.get("note", ""),
        key="kb_meta_note",
        disabled=not _includi,
    )

    st.session_state["kb_metadata"] = {
        "includi_in_kb": _includi,
        "rilevanza": _rilevanza_map.get(_rilevanza_label, 1),
        "tipo": _tipo if _includi else [],
        "note": _note if _includi else "",
    }

# 2c. 🔄 Aggiorna KB Chat (indicizza le flaggate)
# Avviso se la chat corrente è flaggata in session_state ma non ancora su disco
if st.session_state.get("kb_metadata", {}).get("includi_in_kb"):
    from core import load_conversation as _load_conv, get_kb_metadata as _get_kb_meta
    _disk_data = _load_conv(st.session_state.get("conversation_id", ""))
    _disk_flagged = _get_kb_meta(_disk_data).get("includi_in_kb") if _disk_data else False
    if not _disk_flagged:
        st.sidebar.warning(
            "⚠️ Hai flaggato questa chat per la KB ma non è ancora salvata su disco. "
            "Invia un messaggio (o attendi l'auto-save) prima di aggiornare."
        )

if st.sidebar.button("🔄 Aggiorna KB Chat", key="reindex_chat_kb"):
    _progress_bar = st.sidebar.progress(0, text="Avvio indicizzazione...")

    def _reindex_cb(status: str, frac: float):
        _progress_bar.progress(frac, text=status)

    _reindex_result = reindex_all_chat_kb(progress_callback=_reindex_cb)
    _progress_bar.empty()
    st.sidebar.success(
        f"✅ Indicizzate {_reindex_result['chats_indexed']} chat, "
        f"{_reindex_result['total_chunks']} chunk totali"
    )

st.sidebar.caption("Indicizza tutte le chat flaggate — fallo dopo aver salvato nuove chat")

# Stats rapide
_kb_stats = get_kb_chat_stats()
if _kb_stats.get("using_chromadb") and _kb_stats["total_chunks"] > 0:
    st.sidebar.caption(
        f"📊 {_kb_stats['total_chats']} chat · {_kb_stats['total_chunks']} chunk indicizzati"
    )

# 2d. 📚 Gestione KB (modifica/rimozione + bulk-flag)
render_kb_panel()

# 2e. ✅ Usa KB Chat (toggle retrieval)
_use_chat_kb = st.sidebar.checkbox(
    "📚 Usa KB Chat",
    value=st.session_state.get("use_chat_kb", False),
    help="Includi le chat flaggate nel retrieval RAG",
)
st.session_state["use_chat_kb"] = _use_chat_kb
st.sidebar.caption("Attiva per includere le chat indicizzate nelle risposte")

if _use_chat_kb:
    _tipo_opzioni_filter = ["decisione", "insight", "memoria_aziendale", "riferimento", "sperimentale"]
    _tipo_filter = st.sidebar.multiselect(
        "Filtra per tipo",
        _tipo_opzioni_filter,
        default=st.session_state.get("chat_kb_tipo_filter", []),
        key="chat_kb_tipo_filter_widget",
        help="Vuoto = tutti i tipi",
    )
    st.session_state["chat_kb_tipo_filter"] = _tipo_filter

# 3. 🗺️ Mappa Sessione (aperta)
session_map_mode = render_session_map_settings()
st.session_state["session_map_mode"] = session_map_mode

# Nudge mappa sessione (modalità threshold) — dentro la sezione
if (
    session_map_mode == "threshold"
    and st.session_state.get("nudge_mostrato", False)
    and st.session_state.get("session_map_data") is None
):
    nudge_text = get_nudge_text(st.session_state["n_domande_sessione"])
    if render_nudge_sidebar(nudge_text):
        socratic_client_nudge = get_socratic_client(
            connection_type, provider, api_key, model, base_url, temperature
        )
        if socratic_client_nudge is not None:
            with st.sidebar.spinner("📊 Costruendo mappa sessione..."):
                session_map = SessionMapAnalyzer.analyze(
                    st.session_state["messages"],
                    socratic_client_nudge.invoke,
                    st.session_state["conversation_id"],
                )
                if session_map is not None:
                    st.session_state["session_map_data"] = session_map
                    st.rerun()

# Bottone genera mappa su conversazione caricata (nessuna mappa, messaggi presenti, mode != off)
if (
    st.session_state.get("session_map_data") is None
    and len(st.session_state.get("messages", [])) > 0
    and session_map_mode != "off"
):
    if render_generate_map_button():
        socratic_client_gen = get_socratic_client(
            connection_type, provider, api_key, model, base_url, temperature
        )
        if socratic_client_gen is not None:
            with st.sidebar.spinner("📊 Generando mappa sessione..."):
                session_map = SessionMapAnalyzer.analyze(
                    st.session_state["messages"],
                    socratic_client_gen.invoke,
                    st.session_state["conversation_id"],
                )
                if session_map is not None:
                    st.session_state["session_map_data"] = session_map
                    st.rerun()

# Display mappa se già calcolata + bottone rigenera
if st.session_state.get("session_map_data") is not None:
    rigenera = render_session_map_display(
        st.session_state["session_map_data"],
        model_name=st.session_state.get("current_model", ""),
    )
    if rigenera:
        socratic_client_regen = get_socratic_client(
            connection_type, provider, api_key, model, base_url, temperature
        )
        if socratic_client_regen is not None:
            with st.sidebar.spinner("📊 Rigenerando mappa sessione..."):
                session_map = SessionMapAnalyzer.analyze(
                    st.session_state["messages"],
                    socratic_client_regen.invoke,
                    st.session_state["conversation_id"],
                )
                if session_map is not None:
                    st.session_state["session_map_data"] = session_map
                    st.rerun()

# 4. 🧠 Modalità Socratica (aperta)
socratic_mode = render_socratic_mode_settings()
render_socratic_history_sidebar(socratic_mode)

# 5. 📤 Export (aperta)
render_export_section()

# ============================================================================
# 🆕 v1.5.0 - PRIVACY DIALOG (se necessario)
# ============================================================================

if st.session_state.get("show_privacy_dialog", False):
    st.title("🔐 Conferma Privacy Richiesta")
    
    can_proceed, action = render_privacy_dialog()
    
    if can_proceed and action:
        handle_privacy_action(action)
    
    # Blocca il resto dell'interfaccia mentre il dialog è attivo
    st.stop()

# ============================================================================
# MAIN - TITLE AND INFO
# ============================================================================

if connection_type == "Cloud provider":
    st.title(f"{APP_ICON} {APP_TITLE} → {provider} `{VERSION}`")
elif connection_type == "Remote host":
    st.title(f"{APP_ICON} {APP_TITLE} → Remote `{VERSION}`")
else:
    st.title(f"{APP_ICON} {APP_TITLE} → Ollama `{VERSION}`")

# ============================================================================
# 🆕 v1.5.0 - PRIVACY WARNING BANNER (se su Cloud con documenti)
# ============================================================================

render_privacy_warning_banner()

# ============================================================================
# KNOWLEDGE BASE BANNER
# ============================================================================

if st.session_state.get("use_knowledge_base"):
    kb_manager: KnowledgeBaseManager = st.session_state.get("kb_manager")
    if kb_manager and kb_manager.is_indexed():
        stats = kb_manager.get_stats()
        st.success(
            f"📚 **Knowledge Base ATTIVA** - "
            f"{stats.get('document_count', 0)} documenti | "
            f"{stats.get('chunk_count', 0)} chunks"
        )
    else:
        st.warning("📚 Knowledge Base attivata ma non indicizzata. Configura una cartella nella sidebar.")
else:
    if NEWS_BANNER_ENABLED:
        st.info(f"✨ **Novità {NEWS_BANNER_VERSION}**: {NEWS_BANNER_TEXT}")

# ============================================================================
# CONNECTION INDICATOR
# ============================================================================

if connection_type == "Local (Ollama)":
    st.success("💻 **Locale** - Privacy totale")
elif connection_type == "Remote host":
    st.info("🌐 **Remote** - Rete locale")
else:
    st.warning("☁️ **Cloud** - Dati esterni (KB e Upload disabilitati)")

# ============================================================================
# STATS
# ============================================================================

messages = st.session_state.get("messages", [])
c1, c2, c3, c4 = st.columns(4)
c1.metric("📝 Messaggi", len(messages))
c2.metric("👤 Domande", len([m for m in messages if m["role"] == "user"]))
c3.metric("🪙 Token", f"{st.session_state.get('total_tokens_estimate', 0):,}")
c4.metric("🆔 ID", st.session_state.get("conversation_id", "N/A")[-8:])

# ============================================================================
# EXPORT PREVIEW (if requested)
# ============================================================================

if st.session_state.get("show_export_preview"):
    render_export_preview()

st.markdown("---")

# ============================================================================
# CHAT AREA - 🆕 v1.6.1 con supporto client socratico
# ============================================================================

st.subheader("💬 Conversazione")

# 🆕 v1.6.1 - Prepara client per bottoni socratici
socratic_client = get_socratic_client(
    connection_type, provider, api_key, model, base_url, temperature
)

if not messages:
    if st.session_state.get("use_knowledge_base"):
        st.info("👋 Knowledge Base attiva! Fai una domanda sui tuoi documenti.")
    else:
        st.info("👋 Inizia una conversazione!")
else:
    # v1.8.0 - Passa messages_list e socratic_mode a render_chat_message
    for idx, msg in enumerate(messages):
        render_chat_message(
            msg,
            idx,
            socratic_client,
            messages_list=messages,
            socratic_mode=socratic_mode
        )

# v1.9.0 - Auto-save dopo esplorazione socratica
if st.session_state.pop("_socratic_save_needed", False):
    _save_current_conversation()

st.markdown("---")

# ============================================================================
# INPUT AREA - v1.5.0 con File Upload
# ============================================================================

st.subheader("✍️ Messaggio")

# 🆕 v1.5.0 - FILE UPLOAD WIDGET (FUORI dal form!)
# Nota: st.file_uploader non funziona correttamente dentro st.form
processed_files, has_images, upload_warning = render_file_upload_widget(
    connection_type=connection_type,
    current_model=model,
    key="chat_file_upload"
)

# Salva file in session_state per uso nel submit
store_pending_files(processed_files, has_images, upload_warning)

# Riepilogo file se presenti
if processed_files:
    valid_count = len([f for f in processed_files if not f.error])
    if valid_count > 0:
        st.success(f"📎 {valid_count} file pronti per l'invio")

# ========== FORM MESSAGGIO ==========
with st.form("msg_form", clear_on_submit=True):
    placeholder = (
        "Chiedi qualcosa sui tuoi documenti..." 
        if st.session_state.get("use_knowledge_base") 
        else "Scrivi il tuo messaggio..."
    )
    user_input = st.text_area(
        "Messaggio", 
        "", 
        height=100, 
        placeholder=placeholder, 
        label_visibility="collapsed"
    )
    
    col1, col2, _ = st.columns([2, 2, 6])
    with col1:
        submit = st.form_submit_button(
            "🚀 Invia", 
            use_container_width=True, 
            type="primary"
        )

# Reset button (fuori dal form)
_, col_reset, _ = st.columns([2, 2, 6])
with col_reset:
    if st.button("🔄 Nuova", use_container_width=True):
        reset_conversation()
        st.rerun()

# ============================================================================
# MESSAGE SUBMISSION WITH RAG + FILE ATTACHMENTS (v1.5.0)
# ============================================================================

if submit and user_input.strip():
    if not model:
        st.error("❌ Seleziona un modello!")
    elif connection_type == "Cloud provider" and not api_key:
        st.error("❌ Inserisci API key!")
    elif connection_type == "Cloud provider" and st.session_state.get("use_knowledge_base"):
        st.error("🔒 Cloud bloccato con Knowledge Base attiva!")
    else:
        try:
            # 🆕 v1.5.0 - Recupera file da session_state
            pending_files, pending_has_images, _ = get_pending_files()
            
            # Lista nomi file per metadati messaggio
            attachment_names = get_attachment_names(pending_files) if pending_files else None
            
            # 🆕 Arricchisci prompt con contenuto file
            can_use_images = pending_has_images and is_vision_model(model)
            enriched_input, images_data = enrich_prompt_with_files(
                user_input.strip(),
                pending_files,
                include_images=can_use_images
            )
            
            # Add user message (mostra testo originale, non enriched)
            add_message("user", user_input.strip(), attachments=attachment_names)

            # 🆕 v1.10.0 - Incrementa contatore domande sessione
            st.session_state["n_domande_sessione"] += 1
            
            # Prepare RAG context if active
            context_text = ""
            sources = []
            
            if st.session_state.get("use_knowledge_base"):
                kb_manager: KnowledgeBaseManager = st.session_state.get("kb_manager")
                if kb_manager and kb_manager.is_indexed():
                    top_k = st.session_state.get("rag_top_k", DEFAULT_TOP_K_RESULTS)
                    with st.spinner("🔍 Ricerca documenti rilevanti..."):
                        context_text, sources = kb_manager.get_context_for_prompt(
                            user_input.strip(),
                            top_k
                        )

                    if context_text:
                        st.info(f"📎 Trovati {len(sources)} documenti KB")

            # v1.14.0 — Chat KB retrieval (merge con wiki se attivo)
            if st.session_state.get("use_chat_kb"):
                top_k_chat = st.session_state.get("rag_top_k", DEFAULT_TOP_K_RESULTS)
                _tipo_f = st.session_state.get("chat_kb_tipo_filter", []) or None
                with st.spinner("📚 Ricerca nella KB Chat..."):
                    chat_kb_results = search_chat_kb(
                        user_input.strip(), top_k=top_k_chat, tipo_filter=_tipo_f
                    )
                if chat_kb_results:
                    chat_context_parts = []
                    for j, r in enumerate(chat_kb_results, 1):
                        meta = r.get("metadata", {})
                        src = meta.get("chat_titolo", meta.get("chat_id", "chat"))
                        chat_context_parts.append(f"[Chat KB {j}: {src}]\n{r['text']}")
                        src_label = f"💬 {src}"
                        if src_label not in sources:
                            sources.append(src_label)
                    chat_context = "\n\n---\n\n".join(chat_context_parts)
                    if context_text:
                        context_text += "\n\n--- CHAT KB ---\n\n" + chat_context
                    else:
                        context_text = chat_context
                    st.info(f"📚 Trovati {len(chat_kb_results)} risultati dalla KB Chat")
            
            # Create LLM client
            with st.spinner("🔧 Connessione..."):
                client = create_client(
                    connection_type, 
                    provider, 
                    api_key, 
                    model, 
                    system_prompt, 
                    base_url, 
                    temperature
                )
            
            # Prepare prompt
            history = get_conversation_history(
                st.session_state.get("messages", []),
                max_messages
            )
            
            # Build prompt with RAG context + FILE ATTACHMENTS
            if context_text:
                # System prompt enriched with KB context
                rag_system = f"""{system_prompt}

IMPORTANTE: Usa le seguenti informazioni dalla Knowledge Base per rispondere. 
Se la risposta non è presente nei documenti, dillo chiaramente.
Cita sempre le fonti quando usi informazioni dai documenti.

--- DOCUMENTI RILEVANTI (KB) ---
{context_text}
--- FINE DOCUMENTI KB ---"""
                
                # Usa enriched_input che include anche i file allegati
                full_prompt = f"{rag_system}\n\nUtente: {enriched_input}\n\nAssistente:"
            else:
                # Normal prompt with history + file attachments
                context = ""
                for msg in history[:-1]:
                    role_label = "Utente" if msg["role"] == "user" else "AI"
                    context += f"{role_label}: {msg['content']}\n\n"
                full_prompt = (
                    f"{context}Utente: {enriched_input}\n\nAI:" 
                    if context 
                    else enriched_input
                )
            
            # Invoke LLM with streaming ✨ v1.6.0
            # 🆕 TODO: Aggiungere supporto Vision API per immagini
            # Per ora le immagini vengono preparate ma non inviate (richiede modifiche a llm_client)

            # Generator per estrarre solo il nuovo testo dai chunk
            def response_generator():
                """Yielda solo il nuovo testo incrementale dai chunk di streaming"""
                previous_text = ""
                for chunk in client.stream_invoke(full_prompt):
                    # Estrai testo dal chunk
                    current_text = getattr(chunk, "text", str(chunk))
                    if current_text:
                        # Yielda solo la differenza (nuovo testo)
                        new_text = current_text[len(previous_text):]
                        if new_text:
                            yield new_text
                            previous_text = current_text

            # Display streaming response
            with st.chat_message("assistant"):
                response_text = st.write_stream(response_generator())

            # Add response with sources to conversation
            add_message(
                "assistant",
                response_text,
                model=model,
                sources=sources if sources else None
            )
            
            # 🆕 v1.5.0 - Pulisci file pending dopo invio
            clear_pending_files()

            # 🆕 v1.10.0 - Session Map: logica post-risposta
            map_mode = st.session_state.get("session_map_mode", "off")
            n_domande = st.session_state["n_domande_sessione"]

            if map_mode == "progressive" and n_domande >= SESSION_MAP_PROGRESSIVE_VISIBLE_AFTER:
                # Modalità progressiva: aggiorna mappa dopo ogni risposta
                session_map = SessionMapAnalyzer.analyze(
                    st.session_state["messages"],
                    client.invoke,
                    st.session_state["conversation_id"],
                )
                if session_map is not None:
                    st.session_state["session_map_data"] = session_map

            elif map_mode == "threshold" and not st.session_state["nudge_mostrato"]:
                if n_domande >= SESSION_MAP_NUDGE_THRESHOLD:
                    st.session_state["nudge_mostrato"] = True

            st.rerun()
            
        except Exception as e:
            st.error(f"❌ Errore: {e}")

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
c1, c2, _ = st.columns([2, 8, 2])
c1.caption("🤖 DeepAiUG by Gilles")
c2.caption(f"{VERSION} - Socratic Mode | DeepAiUG © 2026")

# Visual indicators
if connection_type == "Cloud provider":
    # Rosso per cloud (warning: dati esterni)
    st.markdown(
        '<style>.stApp { border-top: 4px solid #ff6b6b !important; }</style>',
        unsafe_allow_html=True
    )
else:
    # Verde per Local/Remote (safe: dati locali)
    st.markdown(
        '<style>.stApp { border-top: 4px solid #4CAF50 !important; }</style>',
        unsafe_allow_html=True
    )