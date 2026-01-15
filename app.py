# app.py
# Datapizza v1.5.0 - Entry Point
# ============================================================================
# Interfaccia Streamlit modulare per LLM con UI Frontier-Style

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
)
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
from ui.styles import (
    THEME_LOCAL, 
    THEME_CLOUD, 
    FIXED_INPUT_CSS, 
    CHAT_COLUMN_CSS,
    FIXED_TOP_BAR_CSS,
    TOGGLE_SWITCH_CSS
)

from ui.file_upload import (
    render_file_upload_widget,
    enrich_prompt_with_files,
    is_vision_model,
    store_pending_files,
    get_pending_files,
    clear_pending_files,
)

from ui.privacy_warning import (
    check_privacy_risk,
    render_privacy_dialog,
    handle_privacy_action,
    render_privacy_warning_banner,
    reset_privacy_flags,
    should_show_privacy_dialog,
)

# ============================================================================
# PAGE CONFIG
# ============================================================================

st.set_page_config(
    page_title="Datapizza Chat",
    page_icon="🍕",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
        # File upload
        "pending_files": [],
        "pending_has_images": False,
        "pending_warning": None,
        # Privacy tracking
        "documents_uploaded_this_session": False,
        "uploaded_files_history": [],
        "privacy_acknowledged_for_cloud": False,
        "show_privacy_dialog": False,
        # Sidebar view
        "sidebar_view": "Chats",
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

initialize_session_state()

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def add_message(role: str, content: str, model: str = None, sources: list = None, attachments: list = None):
    message = create_message(role, content, model, sources)
    if attachments:
        message["attachments"] = attachments
    st.session_state["messages"].append(message)
    st.session_state["total_tokens_estimate"] += estimate_tokens(content)
    if st.session_state.get("auto_save_enabled", True):
        _save_current_conversation()

def _save_current_conversation():
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
        }
    )

def reset_conversation():
    st.session_state["messages"] = []
    st.session_state["conversation_id"] = generate_conversation_id()
    st.session_state["conversation_created_at"] = datetime.now().isoformat()
    st.session_state["total_tokens_estimate"] = 0
    clear_pending_files()
    reset_privacy_flags()

# ============================================================================
# LAYOUT & SIDEBAR
# ============================================================================

# Sidebar Header & Toggle
with st.sidebar:
    st.markdown("### 🍕 Datapizza")
    st.radio(
        "Menu",
        ["Chats", "Settings"],
        key="sidebar_view",
        horizontal=True,
        label_visibility="collapsed"
    )
    # st.session_state["sidebar_view"] = view
    st.markdown("---")

# Main Content Area
if st.session_state.get("sidebar_view") == "Chats":
    with st.sidebar:
        render_conversations_manager()
else:
    with st.sidebar:
        st.markdown("### ⚙️ Settings")
        render_llm_config()
        conn_type = st.session_state.get("connection_type", "Local (Ollama)")
        render_knowledge_base_config(conn_type)
        render_export_section()

# Main Layout
col_chat = st.container()

# ============================================================================
# RIGHT COLUMN (CONFIG)
# ============================================================================

# THEME & STYLES (Dynamic)
# Inject basic CSS
st.markdown(MAIN_CSS, unsafe_allow_html=True)

# Select Theme (Logic remains)
if st.session_state.get("connection_type") == "Cloud provider":
    st.markdown(THEME_CLOUD, unsafe_allow_html=True)
else:
    st.markdown(THEME_LOCAL, unsafe_allow_html=True)

# Inject Layout CSS
st.markdown(FIXED_INPUT_CSS, unsafe_allow_html=True)
# FIXED_RIGHT_COLUMN_CSS removed from styles.py will be handled there
st.markdown(CHAT_COLUMN_CSS, unsafe_allow_html=True)
st.markdown(TOGGLE_SWITCH_CSS, unsafe_allow_html=True)

# PRIVACY CHECKS
if st.session_state.get("show_privacy_dialog", False):
    st.title("🔐 Conferma Privacy Richiesta")
    can_proceed, action = render_privacy_dialog()
    if can_proceed and action:
        handle_privacy_action(action)
    st.stop()

# ============================================================================
# FIXED TOP BAR
# ============================================================================

with st.container():
    st.markdown('<span id="top-bar-anchor"></span>', unsafe_allow_html=True)
    st.markdown(FIXED_TOP_BAR_CSS, unsafe_allow_html=True)
    
    # Header & Stats content
    model = st.session_state.get("current_model", "")
    messages = st.session_state.get("messages", [])
    user_msgs = len([m for m in messages if m["role"] == "user"])
    tokens = st.session_state.get("total_tokens_estimate", 0)
    cid = st.session_state.get("conversation_id", "N/A")[-8:]
    
    # Theme-based status
    if st.session_state.get("connection_type") == "Cloud provider":
        status_label = "☁️ CLOUD MODE"
        status_class = "connection-status"
    else:
        status_label = "🔒 SAFE MODE (LOCAL)"
        status_class = "connection-status"

    top_bar_html = f"""
    <div style="display: flex; justify-content: space-between; align-items: center; width: 100%;">
        <div style="display: flex; align-items: center; gap: 20px;">
            <div style="display: flex; flex-direction: column;">
                <h3 style="margin: 0; font-size: 1.2rem;">Datapizza Chat</h3>
                <p style="margin: 0; opacity: 0.7; font-size: 0.8rem;">{model} • {VERSION}</p>
            </div>
            <div class="{status_class}">
                {status_label}
            </div>
        </div>
        <div class="stats-container">
            <div class="stat-item">
                <div class="stat-value">{len(messages)}</div>
                <div class="stat-label">Messaggi</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">{user_msgs}</div>
                <div class="stat-label">Domande</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">{tokens:,}</div>
                <div class="stat-label">Token</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">#{cid}</div>
                <div class="stat-label">ID</div>
            </div>
        </div>
    </div>
    """
    st.markdown(top_bar_html, unsafe_allow_html=True)

with col_chat:
    st.markdown('<span id="chat-column-anchor"></span>', unsafe_allow_html=True)
    
    # KB Status
    if st.session_state.get("use_knowledge_base"):
        kb_manager = st.session_state.get("kb_manager")
        if kb_manager and kb_manager.is_indexed():
            stats = kb_manager.get_stats()
            st.caption(f"📚 **KB ATTIVA**: {stats.get('document_count', 0)} docs | {stats.get('chunk_count', 0)} chunks")
        else:
            st.warning("📚 KB attiva ma vuota")

    # Privacy Banner if Cloud
    render_privacy_warning_banner()

    # Export Preview
    if st.session_state.get("show_export_preview"):
        render_export_preview()

    # CHAT AREA
    if messages:
        for idx, msg in enumerate(messages):
            render_chat_message(msg, idx)
    else:
        if st.session_state.get("use_knowledge_base"):
            st.markdown("<div style='text-align: center; opacity: 0.5; margin-top: 50px;'>Knowledge Base attiva. Chiedi qualcosa sui tuoi documenti.</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='text-align: center; opacity: 0.5; margin-top: 50px;'>Inizia una nuova conversazione.</div>", unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom: 250px;'></div>", unsafe_allow_html=True) # Spacer increased for fixed footer

    # INPUT AREA
    # NOTE: connection_type and model might be undefined if we haven't rendered config layout yet.
    # We should render config FIRST (logically) or retrieve from session_state.
    
    conn = st.session_state.get("connection_type", "Local (Ollama)")
    mod = st.session_state.get("current_model", "")

    # WRAPPED IN CONTAINER FOR FIXED POSITIONING
    with st.container():
        st.markdown('<span id="chat-input-anchor"></span>', unsafe_allow_html=True)
        
        processed_files, has_images, upload_warning = render_file_upload_widget(
            connection_type=conn,
            current_model=mod,
            key="chat_file_upload"
        )
        store_pending_files(processed_files, has_images, upload_warning)
    
        if processed_files:
            valid_count = len([f for f in processed_files if not f.error])
            if valid_count > 0:
                st.success(f"📎 {valid_count} file pronti")
    
        with st.form("msg_form", clear_on_submit=True):
            placeholder = "Chiedi ai tuoi documenti..." if st.session_state.get("use_knowledge_base") else "Scrivi il tuo messaggio..."
            user_input = st.text_area("Messaggio", "", height=100, placeholder=placeholder, label_visibility="collapsed")
            
            col1, col2 = st.columns([2, 5])
            with col1:
                submit = st.form_submit_button("🚀 Invia", use_container_width=True, type="primary")

    # SUBMIT LOGIC
    if submit and user_input.strip():
        # Retrieve config vars from session state since rendered components are in other column
        # OR render_llm_config updates session state.
        
        # NOTE: Variables api_key, provider, base_url, system_prompt, temperature, max_messages
        # need to be retrieved from session_state because they are no longer in local scope 
        # from the function call (since I moved the function call).
        
        api_key = st.session_state.get("api_key", "")
        # ... and so on. 
        # This implies I need to update render_llm_config to STORE all these in session_state
        # OR I call it at the TOP of the script but pass a container.
        
        # Simplified: I will fetch them from session state.
        pass # Actual logic follows in next block I'm not touching


# ============================================================================
# SUBMIT LOGIC
# ============================================================================

if submit and user_input.strip():
    # Retrieve from session state
    model = st.session_state.get("current_model", "")
    connection_type = st.session_state.get("connection_type", "Local (Ollama)")
    api_key = st.session_state.get("api_key", "")
    
    if not model:
        st.error("❌ Seleziona un modello!")
    elif connection_type == "Cloud provider" and not api_key:
        st.error("❌ Inserisci API key!")
    elif connection_type == "Cloud provider" and st.session_state.get("use_knowledge_base"):
        st.error("🔒 Cloud bloccato con Knowledge Base attiva!")
    else:
        try:
            pending_files, pending_has_images, _ = get_pending_files()
            attachment_names = get_attachment_names(pending_files) if pending_files else None
            
            can_use_images = pending_has_images and is_vision_model(model)
            enriched_input, images_data = enrich_prompt_with_files(
                user_input.strip(),
                pending_files,
                include_images=can_use_images
            )
            
            add_message("user", user_input.strip(), attachments=attachment_names)
            
            context_text = ""
            sources = []
            
            if st.session_state.get("use_knowledge_base"):
                kb_manager: KnowledgeBaseManager = st.session_state.get("kb_manager")
                if kb_manager and kb_manager.is_indexed():
                    top_k = st.session_state.get("rag_top_k", DEFAULT_TOP_K_RESULTS)
                    with st.spinner("🔍 Ricerca documenti..."):
                        context_text, sources = kb_manager.get_context_for_prompt(user_input.strip(), top_k)
            
            with st.spinner("🔧 Connessione..."):
                client = create_client(
                    connection_type, 
                    st.session_state.get("provider"), 
                    api_key, 
                    model, 
                    st.session_state.get("system_prompt", ""), 
                    st.session_state.get("base_url", ""), 
                    st.session_state.get("temperature", 0.7)
                )
            
            max_messages = st.session_state.get("max_messages", 50)
            history = get_conversation_history(st.session_state.get("messages", []), max_messages)
            
            if context_text:
                rag_system = f"""{system_prompt}
IMPORTANTE: Usa le seguenti informazioni dalla Knowledge Base per rispondere.
--- DOCUMENTI RILEVANTI (KB) ---
{context_text}
--- FINE DOCUMENTI KB ---"""
                full_prompt = f"{rag_system}\n\nUtente: {enriched_input}\n\nAssistente:"
            else:
                context = ""
                for msg in history[:-1]:
                    role_label = "Utente" if msg["role"] == "user" else "AI"
                    context += f"{role_label}: {msg['content']}\n\n"
                full_prompt = f"{context}Utente: {enriched_input}\n\nAI:" if context else enriched_input
            
            with st.spinner(f"🤖 {model} sta elaborando..."):
                response = client.invoke(full_prompt)
                response_text = getattr(response, "text", str(response))
            
            add_message("assistant", response_text, model=model, sources=sources if sources else None)
            clear_pending_files()
            st.rerun()
            
        except Exception as e:
            st.error(f"❌ Errore: {e}")

# Footer
st.markdown("---")
st.caption(f"datapizza-chat {VERSION} • {datetime.now().year}")
