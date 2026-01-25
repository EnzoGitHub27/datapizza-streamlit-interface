# app.py
# Datapizza v1.5.0 - Entry Point
# ============================================================================
# Interfaccia Streamlit modulare per LLM con:
# - Ollama locale / Remote / Cloud providers
# - Knowledge Base RAG (LocalFolder + MediaWiki + DokuWiki)
# - Export conversazioni (MD, JSON, TXT, PDF)
# - Persistenza conversazioni
# - 🆕 File Upload in Chat (Privacy-First)
# - 🆕 Privacy Warning per passaggio Local→Cloud con documenti
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

# ============================================================================
# PAGE CONFIG
# ============================================================================

st.set_page_config(
    page_title="Datapizza Chat",
    page_icon="🍕",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
        # 🆕 v1.5.0 - Privacy tracking
        "documents_uploaded_this_session": False,
        "uploaded_files_history": [],
        "privacy_acknowledged_for_cloud": False,
        "show_privacy_dialog": False,
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
        }
    )

def reset_conversation():
    """Resetta la conversazione corrente."""
    st.session_state["messages"] = []
    st.session_state["conversation_id"] = generate_conversation_id()
    st.session_state["conversation_created_at"] = datetime.now().isoformat()
    st.session_state["total_tokens_estimate"] = 0
    # 🆕 v1.5.0 - Pulisci anche file pending e flag privacy
    clear_pending_files()
    reset_privacy_flags()

# ============================================================================
# SIDEBAR
# ============================================================================

# LLM Configuration
(
    connection_type,
    provider,
    api_key,
    model,
    base_url,
    system_prompt,
    temperature,
    max_messages
) = render_llm_config()

# Knowledge Base Configuration
render_knowledge_base_config(connection_type)

# Conversations Manager
render_conversations_manager()

# Export Section
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
    st.title(f"🍕 Datapizza Chat → {provider} `{VERSION}`")
elif connection_type == "Remote host":
    st.title(f"🍕 Datapizza Chat → Remote `{VERSION}`")
else:
    st.title(f"🍕 Datapizza Chat → Ollama `{VERSION}`")

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
    st.info(f"✨ **Novità {VERSION}**: File Upload + Privacy-First Cloud Protection!")

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
# CHAT AREA
# ============================================================================

st.subheader("💬 Conversazione")

if not messages:
    if st.session_state.get("use_knowledge_base"):
        st.info("👋 Knowledge Base attiva! Fai una domanda sui tuoi documenti.")
    else:
        st.info("👋 Inizia una conversazione!")
else:
    for idx, msg in enumerate(messages):
        render_chat_message(msg, idx)

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
            
            st.rerun()
            
        except Exception as e:
            st.error(f"❌ Errore: {e}")

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
c1, c2, _ = st.columns([2, 8, 2])
c1.caption("🤖 DeepAiUG by Gilles")
c2.caption(f"{VERSION} - File Upload + Privacy-First | DeepAiUG © 2025")

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
