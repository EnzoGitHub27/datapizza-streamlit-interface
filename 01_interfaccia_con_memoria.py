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
# - Auto-scroll ai messaggi recenti

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

# Limiti memoria conversazione
DEFAULT_MAX_MESSAGES = 50
DEFAULT_MAX_TOKENS_ESTIMATE = 8000

# Stili messaggi
USER_MESSAGE_COLOR = "#E3F2FD"  # Blu chiaro
ASSISTANT_MESSAGE_COLOR = "#F5F5F5"  # Grigio chiaro
USER_MESSAGE_COLOR_DARK = "#1E3A5F"  # Blu scuro per dark mode
ASSISTANT_MESSAGE_COLOR_DARK = "#2D2D2D"  # Grigio scuro per dark mode

# ============================================================================
# FUNZIONI DI UTILITÀ PER GESTIONE API KEYS
# ============================================================================

def load_api_key(provider_name: str, env_var_name: str) -> str:
    """
    Carica la API key per un provider specifico.
    Prima cerca nelle variabili d'ambiente, poi nei file secrets.
    """
    load_dotenv()
    api_key = os.getenv(env_var_name)
    
    if api_key:
        return api_key
    
    base_dir = Path(__file__).parent
    secrets_dir = base_dir / "secrets"
    key_file = secrets_dir / f"{provider_name}_key.txt"
    
    if key_file.exists():
        try:
            with open(key_file, "r", encoding="utf-8") as f:
                api_key = f.read().strip()
            if api_key:
                return api_key
        except Exception as e:
            st.warning(f"Errore durante la lettura di {key_file}: {e}")
    
    return ""


def save_api_key_to_file(provider_name: str, api_key: str) -> bool:
    """Salva una API key nel file secrets/{provider}_key.txt"""
    try:
        base_dir = Path(__file__).parent
        secrets_dir = base_dir / "secrets"
        secrets_dir.mkdir(exist_ok=True)
        
        key_file = secrets_dir / f"{provider_name}_key.txt"
        with open(key_file, "w", encoding="utf-8") as f:
            f.write(api_key)
        return True
    except Exception as e:
        st.error(f"Errore durante il salvataggio della chiave: {e}")
        return False


# ============================================================================
# FUNZIONI PER GESTIONE MODELLI OLLAMA
# ============================================================================

def get_local_ollama_models():
    """Restituisce una lista di nomi modelli Ollama trovati."""
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
    except subprocess.TimeoutExpired:
        st.warning("Timeout durante il recupero dei modelli Ollama")
        return []
    except FileNotFoundError:
        st.warning("Ollama non trovato nel PATH")
        return []
    except Exception as e:
        st.warning(f"Errore recupero modelli Ollama: {e}")
        return []


# ============================================================================
# FUNZIONE PER CREARE CLIENT (Factory Pattern)
# ============================================================================

def create_client(connection_type: str, provider: str, api_key: str, 
                 model: str, system_prompt: str, base_url: str, temperature: float):
    """Crea e ritorna un client LLM appropriato."""
    
    if connection_type == "Cloud provider":
        try:
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
            
            elif provider == "Custom Cloud":
                return OpenAILikeClient(
                    api_key=api_key,
                    model=model,
                    system_prompt=system_prompt,
                    base_url=base_url,
                    temperature=temperature
                )
        
        except Exception as e:
            st.error(f"Errore nella creazione del client cloud: {e}")
            raise
    
    elif connection_type == "Local (Ollama)":
        return OpenAILikeClient(
            api_key="ollama",
            model=model,
            system_prompt=system_prompt,
            base_url=base_url,
            temperature=temperature
        )
    
    else:  # Remote host
        return OpenAILikeClient(
            api_key=api_key or "dummy",
            model=model,
            system_prompt=system_prompt,
            base_url=base_url,
            temperature=temperature
        )


# ============================================================================
# FUNZIONI GESTIONE CONVERSAZIONE
# ============================================================================

def initialize_conversation():
    """Inizializza lo stato della conversazione se non esiste."""
    if "messages" not in st.session_state:
        st.session_state["messages"] = []
    
    if "conversation_id" not in st.session_state:
        st.session_state["conversation_id"] = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if "total_tokens_estimate" not in st.session_state:
        st.session_state["total_tokens_estimate"] = 0


def add_message(role: str, content: str, model: str = None):
    """
    Aggiunge un messaggio alla cronologia.
    
    Args:
        role: "user" o "assistant"
        content: Testo del messaggio
        model: Nome del modello usato (solo per assistant)
    """
    message = {
        "role": role,
        "content": content,
        "timestamp": datetime.now().isoformat(),
    }
    
    if role == "assistant" and model:
        message["model"] = model
    
    st.session_state["messages"].append(message)
    
    # Stima token (approssimativa: ~4 caratteri = 1 token)
    estimated_tokens = len(content) // 4
    st.session_state["total_tokens_estimate"] += estimated_tokens


def get_conversation_history(max_messages: int = None) -> List[Dict[str, str]]:
    """
    Ritorna la cronologia conversazione in formato compatibile con LLM.
    
    Args:
        max_messages: Numero massimo di messaggi da includere (None = tutti)
    
    Returns:
        Lista di dict con formato [{role: "user/assistant", content: "..."}]
    """
    messages = st.session_state.get("messages", [])
    
    if max_messages and len(messages) > max_messages:
        messages = messages[-max_messages:]
    
    # Formato semplificato per LLM (solo role e content)
    return [{"role": msg["role"], "content": msg["content"]} for msg in messages]


def reset_conversation():
    """Resetta la conversazione corrente."""
    st.session_state["messages"] = []
    st.session_state["conversation_id"] = datetime.now().strftime("%Y%m%d_%H%M%S")
    st.session_state["total_tokens_estimate"] = 0


def estimate_tokens_in_conversation() -> int:
    """Stima il numero totale di token nella conversazione."""
    return st.session_state.get("total_tokens_estimate", 0)


# ============================================================================
# FUNZIONE RENDERING MESSAGGI CHAT
# ============================================================================

def render_chat_message(message: Dict[str, Any], index: int):
    """
    Renderizza un singolo messaggio in stile chat bubble.
    
    Args:
        message: Dict con role, content, timestamp, model (opzionale)
        index: Indice del messaggio (per key univoche)
    """
    role = message["role"]
    content = message["content"]
    timestamp = message.get("timestamp", "")
    model_used = message.get("model", "")
    
    # Formatta timestamp
    if timestamp:
        try:
            dt = datetime.fromisoformat(timestamp)
            time_str = dt.strftime("%H:%M:%S")
        except:
            time_str = ""
    else:
        time_str = ""
    
    # Stile messaggio
    if role == "user":
        avatar = "👤"
        label = "Tu"
        align = "flex-end"
        bg_color = USER_MESSAGE_COLOR
        bg_color_dark = USER_MESSAGE_COLOR_DARK
    else:  # assistant
        avatar = "🤖"
        label = f"AI{f' ({model_used})' if model_used else ''}"
        align = "flex-start"
        bg_color = ASSISTANT_MESSAGE_COLOR
        bg_color_dark = ASSISTANT_MESSAGE_COLOR_DARK
    
    # HTML per chat bubble con colori testo corretti
    chat_html = f"""
    <div style="display: flex; justify-content: {align}; margin-bottom: 1rem;">
        <div class="chat-bubble chat-bubble-{index}" style="max-width: 70%; padding: 0.75rem 1rem; 
                    border-radius: 1rem; background-color: {bg_color}; 
                    box-shadow: 0 1px 2px rgba(0,0,0,0.1);">
            <div style="font-weight: 600; font-size: 0.85rem; margin-bottom: 0.25rem; 
                        opacity: 0.8; color: #333;">
                {avatar} {label} {f'<span style="font-size: 0.75rem;">• {time_str}</span>' if time_str else ''}
            </div>
            <div style="white-space: pre-wrap; word-wrap: break-word; color: #000; 
                        line-height: 1.5;">
                {content}
            </div>
        </div>
    </div>
    
    <style>
    /* Light mode - testo scuro */
    .chat-bubble {{
        color: #000 !important;
    }}
    
    /* Dark mode - testo chiaro e background scuro */
    @media (prefers-color-scheme: dark) {{
        .chat-bubble-{index} {{
            background-color: {bg_color_dark} !important;
        }}
        .chat-bubble-{index} div {{
            color: #E0E0E0 !important;
        }}
        .chat-bubble {{
            color: #E0E0E0 !important;
        }}
    }}
    </style>
    """
    
    st.markdown(chat_html, unsafe_allow_html=True)


# ============================================================================
# CONFIGURAZIONE STREAMLIT
# ============================================================================

st.set_page_config(
    page_title="Datapizza → LLM Chat with Memory", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inizializza conversazione
initialize_conversation()

# ============================================================================
# SIDEBAR - CONFIGURAZIONE
# ============================================================================

st.sidebar.header("⚙️ Configurazione Client")

# Tipo di connessione
connection_type = st.sidebar.selectbox(
    "Tipo di connessione",
    options=["Local (Ollama)", "Remote host", "Cloud provider"],
    index=0,
    help="Scegli dove eseguire il modello LLM"
)

# Variabili
base_url = "http://localhost:11434/v1"
api_key = ""
models_local = []
provider = None
model = ""

# ============================================================================
# CONFIGURAZIONE PER MODALITÀ LOCAL (OLLAMA)
# ============================================================================

if connection_type == "Local (Ollama)":
    st.sidebar.markdown("### 🖥️ Configurazione Locale")
    
    base_url = st.sidebar.text_input(
        "Base URL Ollama", 
        value=base_url,
        help="Endpoint dell'istanza Ollama locale"
    )
    
    with st.sidebar:
        col_refresh, col_count = st.columns([3, 1])
        with col_refresh:
            if st.button("🔄 Aggiorna Modelli", use_container_width=True):
                models_local = get_local_ollama_models()
                st.session_state["models_local"] = models_local
        
        if "models_local" not in st.session_state:
            models_local = get_local_ollama_models()
            st.session_state["models_local"] = models_local
        else:
            models_local = st.session_state["models_local"]
        
        with col_count:
            if models_local:
                st.metric("Modelli", len(models_local))
    
    if models_local:
        prev = st.session_state.get("model_select", None)
        default_idx = models_local.index(prev) if (prev in models_local) else 0
        model = st.sidebar.selectbox(
            "Seleziona Modello",
            options=models_local,
            index=default_idx,
            key="model_select"
        )
    else:
        model = st.sidebar.text_input(
            "Nome Modello", 
            value="llama3.2",
            help="Inserisci manualmente il nome del modello"
        )
        st.sidebar.warning("⚠️ Nessun modello rilevato")

# ============================================================================
# CONFIGURAZIONE PER MODALITÀ REMOTE HOST
# ============================================================================

elif connection_type == "Remote host":
    st.sidebar.markdown("### 🌐 Configurazione Host Remoto")
    
    hosts_text = st.sidebar.text_area(
        "Elenco Host (uno per riga)",
        value="http://192.168.1.10:11434/v1\nhttp://192.168.1.20:11434/v1",
        height=100
    )
    
    hosts = [h.strip() for h in hosts_text.splitlines() if h.strip()]
    if not hosts:
        hosts = [base_url]
    
    base_url = st.sidebar.selectbox("Scegli Host", options=hosts, index=0)
    api_key = st.sidebar.text_input("API Key (opzionale)", value="", type="password")
    model = st.sidebar.text_input("Nome Modello", value="llama3.2")

# ============================================================================
# CONFIGURAZIONE PER MODALITÀ CLOUD PROVIDER
# ============================================================================

elif connection_type == "Cloud provider":
    st.sidebar.markdown("### ☁️ Configurazione Cloud Provider")
    
    provider = st.sidebar.selectbox(
        "Provider Cloud",
        options=["OpenAI", "Anthropic (Claude)", "Google Gemini", "Custom Cloud"],
        index=0
    )
    
    if provider == "OpenAI":
        provider_key = "openai"
        env_var = "OPENAI_API_KEY"
        default_model = "gpt-4o-mini"
        default_base_url = "https://api.openai.com/v1"
    elif provider == "Anthropic (Claude)":
        provider_key = "anthropic"
        env_var = "ANTHROPIC_API_KEY"
        default_model = "claude-sonnet-4-20250514"
        default_base_url = "https://api.anthropic.com"
    elif provider == "Google Gemini":
        provider_key = "google"
        env_var = "GOOGLE_API_KEY"
        default_model = "gemini-1.5-pro"
        default_base_url = "https://generativelanguage.googleapis.com"
    else:
        provider_key = "custom"
        env_var = "CUSTOM_API_KEY"
        default_model = ""
        default_base_url = ""
    
    existing_key = load_api_key(provider_key, env_var)
    
    if existing_key:
        st.sidebar.success(f"✅ API Key trovata per {provider}")
        show_key = st.sidebar.checkbox("Mostra/Modifica API Key", value=False)
        api_key = st.sidebar.text_input(f"{provider} API Key", value=existing_key, type="password") if show_key else existing_key
    else:
        api_key = st.sidebar.text_input(f"{provider} API Key", value="", type="password")
        if api_key and st.sidebar.button(f"💾 Salva API Key"):
            if save_api_key_to_file(provider_key, api_key):
                st.sidebar.success("✅ API Key salvata!")
                st.rerun()
    
    if provider != "Custom Cloud":
        model = st.sidebar.text_input("Modello", value=default_model)
        base_url = default_base_url
        with st.sidebar.expander("🔧 Avanzate"):
            st.text_input("Base URL", value=base_url, disabled=True)
    else:
        model = st.sidebar.text_input("Nome Modello", value="")
        base_url = st.sidebar.text_input("Base URL", value="")

# ============================================================================
# PARAMETRI COMUNI + CONFIGURAZIONE MEMORIA
# ============================================================================

st.sidebar.markdown("---")
st.sidebar.markdown("### 🎛️ Parametri Generazione")

system_prompt = st.sidebar.text_area(
    "System Prompt",
    value="Sei un assistente utile e conciso. Rispondi in modo chiaro mantenendo il contesto della conversazione.",
    height=100
)

temperature = st.sidebar.slider(
    "Temperature",
    min_value=0.0,
    max_value=2.0,
    value=0.7,
    step=0.1
)

# Configurazione memoria
st.sidebar.markdown("---")
st.sidebar.markdown("### 🧠 Configurazione Memoria")

max_messages = st.sidebar.slider(
    "Massimo messaggi in memoria",
    min_value=10,
    max_value=100,
    value=DEFAULT_MAX_MESSAGES,
    step=10,
    help="Numero massimo di messaggi da mantenere nella conversazione"
)

include_full_history = st.sidebar.checkbox(
    "Invia cronologia completa",
    value=True,
    help="Se disattivato, invia solo gli ultimi N messaggi al modello"
)

# ============================================================================
# AREA PRINCIPALE
# ============================================================================

# Titolo dinamico
version_badge = "v1.1.0"
if connection_type == "Cloud provider":
    st.title(f"🍕 Datapizza Chat → {provider} `{version_badge}`")
elif connection_type == "Remote host":
    st.title(f"🍕 Datapizza Chat → Remote `{version_badge}`")
else:
    st.title(f"🍕 Datapizza Chat → Ollama `{version_badge}`")

# Badge novità
st.info("✨ **Novità v1.1.0**: Conversazioni multi-turno con memoria! Mantieni il contesto tra i messaggi.")

# Messaggi contestuali
if connection_type == "Local (Ollama)":
    st.success("💻 **Modalità Locale** - Privacy totale, dati sul tuo computer")
elif connection_type == "Remote host":
    st.info("🌐 **Modalità Remote** - Server sulla tua rete")
else:
    st.warning("☁️ **Modalità Cloud** - Dati inviati a server esterni")

# ============================================================================
# STATISTICHE CONVERSAZIONE
# ============================================================================

col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)

with col_stat1:
    num_messages = len(st.session_state.get("messages", []))
    st.metric("📝 Messaggi", num_messages)

with col_stat2:
    user_messages = len([m for m in st.session_state.get("messages", []) if m["role"] == "user"])
    st.metric("👤 Tue Domande", user_messages)

with col_stat3:
    tokens_est = estimate_tokens_in_conversation()
    st.metric("🪙 Token (stima)", f"{tokens_est:,}")

with col_stat4:
    conv_id = st.session_state.get("conversation_id", "N/A")
    st.metric("🆔 ID Conversazione", conv_id[-8:])

st.markdown("---")

# ============================================================================
# AREA CHAT
# ============================================================================

st.subheader("💬 Conversazione")

# Container scrollabile per messaggi
chat_container = st.container()

with chat_container:
    messages = st.session_state.get("messages", [])
    
    if not messages:
        st.info("👋 Inizia una nuova conversazione scrivendo un messaggio qui sotto!")
    else:
        for idx, message in enumerate(messages):
            render_chat_message(message, idx)

st.markdown("---")

# ============================================================================
# INPUT UTENTE
# ============================================================================

st.subheader("✍️ Scrivi il tuo messaggio")

# Usa form per gestire Enter come invio
with st.form(key="message_form", clear_on_submit=True):
    user_input = st.text_area(
        "Messaggio",
        value="",
        height=100,
        placeholder="Scrivi qui il tuo messaggio... (Ctrl+Enter per inviare)",
        label_visibility="collapsed"
    )
    
    col_btn1, col_btn2, col_btn3 = st.columns([2, 2, 6])
    
    with col_btn1:
        submit_button = st.form_submit_button("🚀 Invia", use_container_width=True, type="primary")
    
    with col_btn2:
        # Reset conversation button fuori dal form
        pass

# Pulsante reset fuori dal form (altrimenti causerebbe problemi)
col_reset1, col_reset2, _ = st.columns([2, 2, 6])
with col_reset2:
    if st.button("🔄 Nuova Conversazione", use_container_width=True):
        if st.session_state.get("messages"):
            # Conferma reset
            st.session_state["confirm_reset"] = True

# Gestione conferma reset
if st.session_state.get("confirm_reset"):
    st.warning("⚠️ Sei sicuro di voler iniziare una nuova conversazione? La cronologia attuale verrà persa.")
    col_confirm1, col_confirm2, col_confirm3 = st.columns([1, 1, 8])
    with col_confirm1:
        if st.button("✅ Sì, resetta", type="primary"):
            reset_conversation()
            st.session_state["confirm_reset"] = False
            st.success("✨ Nuova conversazione iniziata!")
            st.rerun()
    with col_confirm2:
        if st.button("❌ Annulla"):
            st.session_state["confirm_reset"] = False
            st.rerun()

# ============================================================================
# LOGICA INVIO MESSAGGIO
# ============================================================================

if submit_button and user_input.strip():
    # Validazione
    if not model:
        st.error("❌ Seleziona un modello prima di inviare!")
    elif connection_type == "Cloud provider" and not api_key:
        st.error("❌ Inserisci una API key valida!")
    else:
        try:
            # Aggiungi messaggio utente alla cronologia
            add_message("user", user_input.strip())
            
            # Crea client
            with st.spinner("🔧 Connessione al modello..."):
                client = create_client(
                    connection_type=connection_type,
                    provider=provider,
                    api_key=api_key,
                    model=model,
                    system_prompt=system_prompt,
                    base_url=base_url,
                    temperature=temperature
                )
            
            # Prepara cronologia per invio
            history_to_send = get_conversation_history(
                max_messages=max_messages if not include_full_history else None
            )
            
            # Invoca il modello con tutta la cronologia
            with st.spinner(f"🤖 {model} sta pensando..."):
                # Per modelli che supportano conversazioni, passiamo tutta la history
                # Alcuni client accettano messages come parametro
                try:
                    # Prova prima con history completa (formato chat)
                    response = client.invoke(history_to_send[-1]["content"])
                except TypeError:
                    # Fallback: usa solo ultimo messaggio
                    response = client.invoke(user_input.strip())
                
                response_text = getattr(response, "text", str(response))
            
            # Aggiungi risposta alla cronologia
            add_message("assistant", response_text, model=model)
            
            # Forza refresh per mostrare nuovo messaggio
            st.rerun()
        
        except Exception as e:
            st.error(f"❌ Errore durante l'invocazione: {e}")
            st.exception(e)

# ============================================================================
# FOOTER CON INFO VERSIONE
# ============================================================================

st.markdown("---")
col_footer1, col_footer2, col_footer3 = st.columns([2, 6, 2])

with col_footer1:
    st.caption(f"🍕 Datapizza AI")

with col_footer2:
    st.caption(f"v1.1.0 - Multi-turn Conversations | Gilles DeepAiUG © 2025")

with col_footer3:
    if st.button("📋 Changelog"):
        st.info("""
        **v1.1.0 Novità:**
        - ✨ Conversazioni multi-turno
        - 🧠 Memoria persistente sessione
        - 💬 Interfaccia chat-style
        - 📊 Statistiche conversazione
        - 🔄 Reset conversazione
        """)

# ============================================================================
# STILE CSS PERSONALIZZATO
# ============================================================================

# Stili globali per chat bubbles e dark mode
st.markdown("""
<style>
/* Stili globali per messaggi chat */
.chat-msg-user, .chat-msg-assistant {
    color: #1a1a1a !important;
}

.chat-header {
    color: #1a1a1a !important;
}

.chat-content {
    color: #1a1a1a !important;
}

/* Dark mode - colori adattivi */
@media (prefers-color-scheme: dark) {
    /* Background scuri per messaggi in dark mode */
    [class*="chat-msg-user"] {
        background-color: #1E3A5F !important;
    }
    
    [class*="chat-msg-assistant"] {
        background-color: #2D2D2D !important;
    }
    
    /* Testo chiaro in dark mode */
    .chat-msg-user, .chat-msg-assistant,
    .chat-header, .chat-content {
        color: #E8E8E8 !important;
    }
    
    /* Header leggermente più trasparente */
    .chat-header {
        opacity: 0.9 !important;
    }
}

/* Migliora spacing messaggi chat */
.element-container:has(div[class*="chat-msg"]) {
    margin-bottom: 0.5rem !important;
}

/* Form submit con Enter */
.stTextArea textarea {
    font-family: inherit;
}

/* Stile aggiuntivo per modalità cloud */
</style>
""", unsafe_allow_html=True)

if connection_type == "Cloud provider":
    st.markdown("""
    <style>
    .stApp {
        border-top: 4px solid #ff6b6b !important;
    }
    [data-testid="stSidebar"] {
        background-color: rgba(255, 107, 107, 0.05) !important;
    }
    @media (prefers-color-scheme: dark) {
        [data-testid="stSidebar"] {
            background-color: rgba(255, 107, 107, 0.1) !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)