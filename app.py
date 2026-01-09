# app.py
# Datapizza v1.4.0 - Entry Point
# ============================================================================
# Interfaccia Streamlit modulare per LLM con:
# - Ollama locale / Remote / Cloud providers
# - Knowledge Base RAG (LocalFolder + MediaWiki)
# - Export conversazioni (MD, JSON, TXT, PDF)
# - Persistenza conversazioni
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
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

initialize_session_state()

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def add_message(role: str, content: str, model: str = None, sources: list = None):
    """Aggiunge un messaggio alla conversazione e salva."""
    message = create_message(role, content, model, sources)
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
# MAIN - TITLE AND INFO
# ============================================================================

if connection_type == "Cloud provider":
    st.title(f"🍕 Datapizza Chat → {provider} `{VERSION}`")
elif connection_type == "Remote host":
    st.title(f"🍕 Datapizza Chat → Remote `{VERSION}`")
else:
    st.title(f"🍕 Datapizza Chat → Ollama `{VERSION}`")

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
    st.info(f"✨ **Novità {VERSION}**: Architettura modulare + MediaWiki RAG!")

# ============================================================================
# CONNECTION INDICATOR
# ============================================================================

if connection_type == "Local (Ollama)":
    st.success("💻 **Locale** - Privacy totale")
elif connection_type == "Remote host":
    st.info("🌐 **Remote** - Rete locale")
else:
    st.warning("☁️ **Cloud** - Dati esterni (KB disabilitata)")

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
# INPUT AREA
# ============================================================================

st.subheader("✍️ Messaggio")

with st.form("msg_form", clear_on_submit=True):
    placeholder = (
        "Chiedi qualcosa sui tuoi documenti..." 
        if st.session_state.get("use_knowledge_base") 
        else "Scrivi..."
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

# Reset button
_, col_reset, _ = st.columns([2, 2, 6])
with col_reset:
    if st.button("🔄 Nuova", use_container_width=True):
        reset_conversation()
        st.rerun()

# ============================================================================
# MESSAGE SUBMISSION WITH RAG
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
            # Add user message
            add_message("user", user_input.strip())
            
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
                        st.info(f"📎 Trovati {len(sources)} documenti rilevanti")
            
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
            
            # Build prompt with RAG context
            if context_text:
                # System prompt enriched with context
                rag_system = f"""{system_prompt}

IMPORTANTE: Usa le seguenti informazioni dalla Knowledge Base per rispondere. 
Se la risposta non è presente nei documenti, dillo chiaramente.
Cita sempre le fonti quando usi informazioni dai documenti.

--- DOCUMENTI RILEVANTI ---
{context_text}
--- FINE DOCUMENTI ---"""
                
                full_prompt = f"{rag_system}\n\nUtente: {user_input.strip()}\n\nAssistente:"
            else:
                # Normal prompt with history
                context = ""
                for msg in history[:-1]:
                    role_label = "Utente" if msg["role"] == "user" else "AI"
                    context += f"{role_label}: {msg['content']}\n\n"
                full_prompt = (
                    f"{context}Utente: {user_input.strip()}\n\nAI:" 
                    if context 
                    else user_input.strip()
                )
            
            # Invoke LLM
            with st.spinner(f"🤖 {model} sta pensando..."):
                response = client.invoke(full_prompt)
                response_text = getattr(response, "text", str(response))
            
            # Add response with sources
            add_message(
                "assistant", 
                response_text, 
                model=model, 
                sources=sources if sources else None
            )
            st.rerun()
            
        except Exception as e:
            st.error(f"❌ Errore: {e}")

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
c1, c2, _ = st.columns([2, 8, 2])
c1.caption("🍕 Datapizza AI")
c2.caption(f"{VERSION} - Modular Architecture + Multi-Wiki RAG | DeepAiUG © 2025")

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
