# Streamlit UI per LLM con Conversazioni Multi-Turno e Memoria
# Versione 1.1.0 - Interfaccia con Memoria Conversazionale
# Gilles DeepAiUG - Gennaio 2025
# 
# Novità v1.1.0:
# - Conversazioni multi-turno con memoria completa
# - Interfaccia chat-style con bolle messaggi
# - Session state persistente
# - Gestione cronologia conversazioni
# - Pulsante reset conversazione
# - Statistiche conversazione (messaggi, token stimati)

import os
import subprocess
import streamlit as st
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime
from typing import List, Dict, Any

# Import datapizza clients
from datapizza.clients import ClientFactory
from datapizza.clients.factory import Provider
from datapizza.clients.openai_like import OpenAILikeClient

# ============================================================================
# COSTANTI
# ============================================================================

DEFAULT_MAX_MESSAGES = 50
DEFAULT_MAX_TOKENS_ESTIMATE = 8000

USER_MESSAGE_COLOR = "#E3F2FD"
ASSISTANT_MESSAGE_COLOR = "#F5F5F5"
USER_MESSAGE_COLOR_DARK = "#1E3A5F"
ASSISTANT_MESSAGE_COLOR_DARK = "#2D2D2D"

# ============================================================================
# FUNZIONI API KEYS
# ============================================================================

def load_api_key(provider_name: str, env_var_name: str) -> str:
    """Carica API key da env o file secrets."""
    load_dotenv()
    api_key = os.getenv(env_var_name)
    
    if api_key:
        return api_key
    
    base_dir = Path(__file__).parent
    key_file = base_dir / "secrets" / f"{provider_name}_key.txt"
    
    if key_file.exists():
        try:
            with open(key_file, "r", encoding="utf-8") as f:
                api_key = f.read().strip()
            if api_key:
                return api_key
        except Exception as e:
            st.warning(f"Errore lettura {key_file}: {e}")
    
    return ""


def save_api_key_to_file(provider_name: str, api_key: str) -> bool:
    """Salva API key in file secrets."""
    try:
        base_dir = Path(__file__).parent
        secrets_dir = base_dir / "secrets"
        secrets_dir.mkdir(exist_ok=True)
        
        key_file = secrets_dir / f"{provider_name}_key.txt"
        with open(key_file, "w", encoding="utf-8") as f:
            f.write(api_key)
        return True
    except Exception as e:
        st.error(f"Errore salvataggio chiave: {e}")
        return False

# ============================================================================
# FUNZIONI OLLAMA
# ============================================================================

def get_local_ollama_models():
    """Recupera lista modelli Ollama."""
    try:
        proc = subprocess.run(
            ["ollama", "list"], 
            capture_output=True, 
            text=True, 
            check=True,
            timeout=5
        )
        lines = proc.stdout.splitlines()
        models = []
        
        for line in lines:
            s = line.strip()
            if not s or s.upper().startswith("NAME") or set(s) <= set("- "):
                continue
            parts = s.split()
            if parts:
                models.append(parts[0])
        
        return models
    except Exception:
        return []

# ============================================================================
# FUNZIONI CLIENT
# ============================================================================

def create_client(connection_type: str, provider: str, api_key: str, 
                 model: str, system_prompt: str, base_url: str, temperature: float):
    """Crea client LLM."""
    
    if connection_type == "Cloud provider":
        if provider == "OpenAI":
            return ClientFactory.create(
                provider=Provider.OPENAI,
                api_key=api_key,
                model=model,
                temperature=temperature,
                system_prompt=system_prompt
            )
        elif provider == "Anthropic (Claude)":
            return ClientFactory.create(
                provider=Provider.ANTHROPIC,
                api_key=api_key,
                model=model,
                temperature=temperature,
                system_prompt=system_prompt
            )
        elif provider == "Google Gemini":
            return ClientFactory.create(
                provider=Provider.GOOGLE,
                api_key=api_key,
                model=model,
                temperature=temperature,
                system_prompt=system_prompt
            )
        else:
            return OpenAILikeClient(
                api_key=api_key,
                model=model,
                system_prompt=system_prompt,
                base_url=base_url,
                temperature=temperature
            )
    else:
        return OpenAILikeClient(
            api_key=api_key or "ollama",
            model=model,
            system_prompt=system_prompt,
            base_url=base_url,
            temperature=temperature
        )

# ============================================================================
# FUNZIONI CONVERSAZIONE
# ============================================================================

def initialize_conversation():
    """Inizializza stato conversazione."""
    if "messages" not in st.session_state:
        st.session_state["messages"] = []
    if "conversation_id" not in st.session_state:
        st.session_state["conversation_id"] = datetime.now().strftime("%Y%m%d_%H%M%S")
    if "total_tokens_estimate" not in st.session_state:
        st.session_state["total_tokens_estimate"] = 0


def add_message(role: str, content: str, model: str = None):
    """Aggiunge messaggio alla cronologia."""
    message = {
        "role": role,
        "content": content,
        "timestamp": datetime.now().isoformat(),
    }
    
    if role == "assistant" and model:
        message["model"] = model
    
    st.session_state["messages"].append(message)
    st.session_state["total_tokens_estimate"] += len(content) // 4


def get_conversation_history(max_messages: int = None) -> List[Dict[str, str]]:
    """Ritorna cronologia per LLM."""
    messages = st.session_state.get("messages", [])
    
    if max_messages and len(messages) > max_messages:
        messages = messages[-max_messages:]
    
    return [{"role": msg["role"], "content": msg["content"]} for msg in messages]


def reset_conversation():
    """Resetta conversazione."""
    st.session_state["messages"] = []
    st.session_state["conversation_id"] = datetime.now().strftime("%Y%m%d_%H%M%S")
    st.session_state["total_tokens_estimate"] = 0


def estimate_tokens_in_conversation() -> int:
    """Stima token totali."""
    return st.session_state.get("total_tokens_estimate", 0)

# ============================================================================
# RENDERING MESSAGGI - VERSIONE PULITA
# ============================================================================

def render_chat_message(message: Dict[str, Any], index: int):
    """Renderizza messaggio chat."""
    role = message["role"]
    content = message["content"]
    timestamp = message.get("timestamp", "")
    model_used = message.get("model", "")
    
    # Formatta timestamp
    time_str = ""
    if timestamp:
        try:
            dt = datetime.fromisoformat(timestamp)
            time_str = dt.strftime("%H:%M:%S")
        except:
            pass
    
    # Configurazione visiva
    if role == "user":
        avatar = "👤"
        label = "Tu"
        col_config = [3, 7, 0.5]
        bubble_class = "user-bubble"
    else:
        avatar = "🤖"
        label = f"AI{f' ({model_used})' if model_used else ''}"
        col_config = [0.5, 7, 3]
        bubble_class = "assistant-bubble"
    
    # Layout
    cols = st.columns(col_config)
    
    with cols[1]:
        st.caption(f"{avatar} **{label}** • {time_str}")
        
        st.markdown(f'<div class="{bubble_class}">', unsafe_allow_html=True)
        st.write(content)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.write("")

# ============================================================================
# CONFIGURAZIONE STREAMLIT
# ============================================================================

st.set_page_config(
    page_title="Datapizza → LLM Chat v1.1.0", 
    layout="wide",
    initial_sidebar_state="expanded"
)

initialize_conversation()

# ============================================================================
# STILI CSS - UNA SOLA VOLTA
# ============================================================================

st.markdown("""
<style>
.user-bubble {
    background-color: #E3F2FD !important;
    padding: 0.75rem 1rem !important;
    border-radius: 12px !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1) !important;
    margin-bottom: 0.5rem !important;
    color: #1a1a1a !important;
}

.assistant-bubble {
    background-color: #F5F5F5 !important;
    padding: 0.75rem 1rem !important;
    border-radius: 12px !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1) !important;
    margin-bottom: 0.5rem !important;
    color: #1a1a1a !important;
}

@media (prefers-color-scheme: dark) {
    .user-bubble {
        background-color: #1E3A5F !important;
        color: #E8E8E8 !important;
    }
    .assistant-bubble {
        background-color: #2D2D2D !important;
        color: #E8E8E8 !important;
    }
}
</style>
""", unsafe_allow_html=True)

# ============================================================================
# SIDEBAR
# ============================================================================

st.sidebar.header("⚙️ Configurazione")

connection_type = st.sidebar.selectbox(
    "Tipo connessione",
    ["Local (Ollama)", "Remote host", "Cloud provider"],
    index=0
)

base_url = "http://localhost:11434/v1"
api_key = ""
models_local = []
provider = None
model = ""

# CONFIGURAZIONE LOCAL
if connection_type == "Local (Ollama)":
    st.sidebar.markdown("### 🖥️ Locale")
    base_url = st.sidebar.text_input("Base URL", value=base_url)
    
    col_r, col_c = st.sidebar.columns([3, 1])
    with col_r:
        if st.button("🔄 Aggiorna", use_container_width=True):
            models_local = get_local_ollama_models()
            st.session_state["models_local"] = models_local
    
    if "models_local" not in st.session_state:
        models_local = get_local_ollama_models()
        st.session_state["models_local"] = models_local
    else:
        models_local = st.session_state["models_local"]
    
    with col_c:
        if models_local:
            st.metric("", len(models_local))
    
    if models_local:
        prev = st.session_state.get("model_select")
        idx = models_local.index(prev) if prev in models_local else 0
        model = st.sidebar.selectbox("Modello", models_local, index=idx, key="model_select")
    else:
        model = st.sidebar.text_input("Modello", value="llama3.2")

# CONFIGURAZIONE REMOTE
elif connection_type == "Remote host":
    st.sidebar.markdown("### 🌐 Remote")
    hosts_text = st.sidebar.text_area("Host (uno per riga)", 
                                      value="http://192.168.1.10:11434/v1", height=80)
    hosts = [h.strip() for h in hosts_text.splitlines() if h.strip()]
    if not hosts:
        hosts = [base_url]
    base_url = st.sidebar.selectbox("Host", hosts)
    api_key = st.sidebar.text_input("API Key", type="password")
    model = st.sidebar.text_input("Modello", value="llama3.2")

# CONFIGURAZIONE CLOUD
else:
    st.sidebar.markdown("### ☁️ Cloud")
    provider = st.sidebar.selectbox("Provider", 
                                   ["OpenAI", "Anthropic (Claude)", "Google Gemini", "Custom Cloud"])
    
    if provider == "OpenAI":
        pk, ev, dm, db = "openai", "OPENAI_API_KEY", "gpt-4o-mini", "https://api.openai.com/v1"
    elif provider == "Anthropic (Claude)":
        pk, ev, dm, db = "anthropic", "ANTHROPIC_API_KEY", "claude-sonnet-4-20250514", "https://api.anthropic.com"
    elif provider == "Google Gemini":
        pk, ev, dm, db = "google", "GOOGLE_API_KEY", "gemini-1.5-pro", "https://generativelanguage.googleapis.com"
    else:
        pk, ev, dm, db = "custom", "CUSTOM_API_KEY", "", ""
    
    existing_key = load_api_key(pk, ev)
    
    if existing_key:
        st.sidebar.success(f"✅ Key trovata")
        show = st.sidebar.checkbox("Mostra/Modifica")
        api_key = st.sidebar.text_input("API Key", value=existing_key, type="password") if show else existing_key
    else:
        api_key = st.sidebar.text_input("API Key", type="password")
        if api_key and st.sidebar.button("💾 Salva"):
            if save_api_key_to_file(pk, api_key):
                st.sidebar.success("✅ Salvata!")
                st.rerun()
    
    if provider != "Custom Cloud":
        model = st.sidebar.text_input("Modello", value=dm)
        base_url = db
    else:
        model = st.sidebar.text_input("Modello")
        base_url = st.sidebar.text_input("Base URL")

# PARAMETRI
st.sidebar.markdown("---")
st.sidebar.markdown("### 🎛️ Parametri")

system_prompt = st.sidebar.text_area(
    "System Prompt",
    value="Sei un assistente utile. Rispondi in modo chiaro.",
    height=80
)

temperature = st.sidebar.slider("Temperature", 0.0, 2.0, 0.7, 0.1)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🧠 Memoria")

max_messages = st.sidebar.slider("Max messaggi", 10, 100, 50, 10)
include_full_history = st.sidebar.checkbox("Cronologia completa", value=True)

# ============================================================================
# MAIN
# ============================================================================

version = "v1.1.0"
if connection_type == "Cloud provider":
    st.title(f"🍕 Datapizza Chat → {provider} `{version}`")
elif connection_type == "Remote host":
    st.title(f"🍕 Datapizza Chat → Remote `{version}`")
else:
    st.title(f"🍕 Datapizza Chat → Ollama `{version}`")

st.info("✨ **Novità v1.1.0**: Conversazioni con memoria!")

if connection_type == "Local (Ollama)":
    st.success("💻 **Locale** - Privacy totale")
elif connection_type == "Remote host":
    st.info("🌐 **Remote** - Rete locale")
else:
    st.warning("☁️ **Cloud** - Dati esterni")

# STATISTICHE
c1, c2, c3, c4 = st.columns(4)
num_msg = len(st.session_state.get("messages", []))
user_msg = len([m for m in st.session_state.get("messages", []) if m["role"] == "user"])
tokens = estimate_tokens_in_conversation()
conv_id = st.session_state.get("conversation_id", "N/A")

c1.metric("📝 Messaggi", num_msg)
c2.metric("👤 Domande", user_msg)
c3.metric("🪙 Token", f"{tokens:,}")
c4.metric("🆔 ID", conv_id[-8:])

st.markdown("---")

# CHAT
st.subheader("💬 Conversazione")

chat_container = st.container()
with chat_container:
    messages = st.session_state.get("messages", [])
    if not messages:
        st.info("👋 Inizia una conversazione!")
    else:
        for idx, msg in enumerate(messages):
            render_chat_message(msg, idx)

st.markdown("---")

# INPUT
st.subheader("✍️ Messaggio")

with st.form("msg_form", clear_on_submit=True):
    user_input = st.text_area(
        "Messaggio",
        "",
        height=100,
        placeholder="Scrivi... (Ctrl+Enter per inviare)",
        label_visibility="collapsed"
    )
    
    c1, c2, _ = st.columns([2, 2, 6])
    with c1:
        submit = st.form_submit_button("🚀 Invia", use_container_width=True, type="primary")

# RESET
c1, c2, _ = st.columns([2, 2, 6])
with c2:
    if st.button("🔄 Nuova", use_container_width=True):
        if st.session_state.get("messages"):
            st.session_state["confirm_reset"] = True

if st.session_state.get("confirm_reset"):
    st.warning("⚠️ Confermi reset?")
    c1, c2, _ = st.columns([1, 1, 8])
    with c1:
        if st.button("✅ Sì", type="primary"):
            reset_conversation()
            st.session_state["confirm_reset"] = False
            st.success("✨ Reset!")
            st.rerun()
    with c2:
        if st.button("❌ No"):
            st.session_state["confirm_reset"] = False
            st.rerun()

# INVIO
if submit and user_input.strip():
    if not model:
        st.error("❌ Seleziona modello!")
    elif connection_type == "Cloud provider" and not api_key:
        st.error("❌ Inserisci API key!")
    else:
        try:
            add_message("user", user_input.strip())
            
            with st.spinner("🔧 Connessione..."):
                client = create_client(
                    connection_type, provider, api_key,
                    model, system_prompt, base_url, temperature
                )
            
            history = get_conversation_history(
                max_messages if not include_full_history else None
            )
            
            with st.spinner(f"🤖 {model} pensa..."):
                # Costruisci prompt con cronologia
                context = ""
                for msg in history[:-1]:
                    role_label = "Utente" if msg["role"] == "user" else "AI"
                    context += f"{role_label}: {msg['content']}\n\n"
                
                full_prompt = f"{context}Utente: {user_input.strip()}\n\nAI:" if context else user_input.strip()
                
                response = client.invoke(full_prompt)
                response_text = getattr(response, "text", str(response))
            
            add_message("assistant", response_text, model=model)
            st.rerun()
        
        except Exception as e:
            st.error(f"❌ Errore: {e}")

# FOOTER
st.markdown("---")
c1, c2, c3 = st.columns([2, 6, 2])
c1.caption("🍕 Datapizza AI")
c2.caption("v1.1.0 - Multi-turn | Gilles DeepAiUG © 2025")

if connection_type == "Cloud provider":
    st.markdown("""
    <style>
    .stApp { border-top: 4px solid #ff6b6b !important; }
    [data-testid="stSidebar"] { background-color: rgba(255,107,107,0.05) !important; }
    </style>
    """, unsafe_allow_html=True)