# Streamlit UI per inviare prompt a modelli LLM (Locali, Remote, Cloud) tramite Datapizza AI
# Versione 1.0.0 - Interfaccia dinamica completa per LLM
# Gilles DeepAiUG - Dicembre 2025
# 
# Supporta:
# - Modelli locali (Ollama)
# - Host remoti
# - Provider Cloud (OpenAI, Anthropic, Google Gemini, altri)
# - Gestione robusta delle API keys (variabili ambiente + file secrets)
# - Upload file con anteprima

import os
import subprocess
import streamlit as st
from pathlib import Path
from dotenv import load_dotenv

# Import datapizza clients
from datapizza.clients import ClientFactory
from datapizza.clients.factory import Provider
from datapizza.clients.openai_like import OpenAILikeClient

# ============================================================================
# FUNZIONI DI UTILITÀ PER GESTIONE API KEYS
# ============================================================================

def load_api_key(provider_name: str, env_var_name: str) -> str:
    """
    Carica la API key per un provider specifico.
    Prima cerca nelle variabili d'ambiente, poi nei file secrets.
    
    Args:
        provider_name: Nome del provider (es. "openai", "anthropic", "google")
        env_var_name: Nome della variabile d'ambiente (es. "OPENAI_API_KEY")
    
    Returns:
        API key come stringa, o stringa vuota se non trovata
    """
    # Carica .env se presente
    load_dotenv()
    
    # Prova prima con variabile d'ambiente
    api_key = os.getenv(env_var_name)
    
    if api_key:
        return api_key
    
    # Se non trovata, cerca nel file secrets/{provider}_key.txt
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
    """
    Salva una API key nel file secrets/{provider}_key.txt
    
    Args:
        provider_name: Nome del provider
        api_key: API key da salvare
    
    Returns:
        True se salvato con successo, False altrimenti
    """
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
    """
    Restituisce una lista di nomi modelli trovati eseguendo `ollama list`.
    """
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
            if not s:
                continue
            # Ignora intestazioni e separatori
            if s.upper().startswith("NAME") or set(s) <= set("- "):
                continue
            # Il primo token è il nome del modello
            parts = s.split()
            if parts:
                models.append(parts[0])
        
        return models
    except subprocess.TimeoutExpired:
        st.warning("Timeout durante il recupero dei modelli Ollama")
        return []
    except FileNotFoundError:
        st.warning("Ollama non trovato. Assicurati che sia installato e nel PATH.")
        return []
    except Exception as e:
        st.warning(f"Errore durante il recupero dei modelli Ollama: {e}")
        return []


# ============================================================================
# FUNZIONE PER CREARE CLIENT (Factory Pattern)
# ============================================================================

def create_client(connection_type: str, provider: str, api_key: str, 
                 model: str, system_prompt: str, base_url: str, temperature: float):
    """
    Crea e ritorna un client LLM appropriato basato sul tipo di connessione.
    
    Args:
        connection_type: "Local (Ollama)", "Remote host", o "Cloud provider"
        provider: Provider cloud (es. "OpenAI", "Anthropic", "Google Gemini")
        api_key: API key per il provider
        model: Nome del modello
        system_prompt: System prompt da utilizzare
        base_url: URL base per l'API
        temperature: Temperatura per la generazione
    
    Returns:
        Client configurato
    """
    
    if connection_type == "Cloud provider":
        # Usa ClientFactory per provider cloud
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
                # Usa OpenAILikeClient per provider custom
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
        # Usa OpenAILikeClient per Ollama (compatibile con API OpenAI)
        return OpenAILikeClient(
            api_key="ollama",  # Ollama non richiede una vera API key
            model=model,
            system_prompt=system_prompt,
            base_url=base_url,
            temperature=temperature
        )
    
    else:  # Remote host
        # Usa OpenAILikeClient per host remoti
        return OpenAILikeClient(
            api_key=api_key or "dummy",
            model=model,
            system_prompt=system_prompt,
            base_url=base_url,
            temperature=temperature
        )


# ============================================================================
# CONFIGURAZIONE STREAMLIT
# ============================================================================

st.set_page_config(
    page_title="Datapizza → LLM Interface (Streamlit)", 
    layout="wide",
    initial_sidebar_state="expanded"
)

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

# Inizializzazione variabili
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
    
    # Recupera modelli locali
    with st.sidebar:
        col_refresh, col_count = st.columns([3, 1])
        with col_refresh:
            if st.button("🔄 Aggiorna Modelli", use_container_width=True):
                models_local = get_local_ollama_models()
                st.session_state["models_local"] = models_local
        
        # Carica modelli salvati in sessione o recuperali
        if "models_local" not in st.session_state:
            models_local = get_local_ollama_models()
            st.session_state["models_local"] = models_local
        else:
            models_local = st.session_state["models_local"]
        
        with col_count:
            if models_local:
                st.metric("Modelli", len(models_local))
    
    # Selezione modello
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
        st.sidebar.warning("⚠️ Nessun modello rilevato. Assicurati che Ollama sia in esecuzione.")

# ============================================================================
# CONFIGURAZIONE PER MODALITÀ REMOTE HOST
# ============================================================================

elif connection_type == "Remote host":
    st.sidebar.markdown("### 🌐 Configurazione Host Remoto")
    
    hosts_text = st.sidebar.text_area(
        "Elenco Host (uno per riga)",
        value="http://192.168.1.151:11434/v1\nhttp://192.168.1.152:11434/v1",
        height=100,
        help="Inserisci gli endpoint dei server remoti"
    )
    
    hosts = [h.strip() for h in hosts_text.splitlines() if h.strip()]
    if not hosts:
        hosts = [base_url]
    
    base_url = st.sidebar.selectbox(
        "Scegli Host",
        options=hosts,
        index=0,
        key="remote_host_select"
    )
    
    api_key = st.sidebar.text_input(
        "API Key (opzionale)",
        value="",
        type="password",
        help="Inserisci API key se richiesta dall'host remoto"
    )
    
    model = st.sidebar.text_input(
        "Nome Modello",
        value="llama3.2",
        help="Nome del modello disponibile sull'host remoto"
    )

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
    
    # Configurazione specifica per ogni provider
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
        
    else:  # Custom Cloud
        provider_key = "custom"
        env_var = "CUSTOM_API_KEY"
        default_model = ""
        default_base_url = ""
    
    # Carica API key esistente
    existing_key = load_api_key(provider_key, env_var)
    
    # Input API key con indicatore se già presente
    if existing_key:
        st.sidebar.success(f"✅ API Key trovata per {provider}")
        show_key = st.sidebar.checkbox("Mostra/Modifica API Key", value=False)
        if show_key:
            api_key = st.sidebar.text_input(
                f"{provider} API Key",
                value=existing_key,
                type="password",
                help=f"Chiave trovata in variabile d'ambiente o file secrets/{provider_key}_key.txt"
            )
        else:
            api_key = existing_key
    else:
        api_key = st.sidebar.text_input(
            f"{provider} API Key",
            value="",
            type="password",
            help=f"Inserisci la tua API key. Verrà salvata in secrets/{provider_key}_key.txt"
        )
        
        # Pulsante per salvare la chiave
        if api_key and st.sidebar.button(f"💾 Salva API Key per {provider}"):
            if save_api_key_to_file(provider_key, api_key):
                st.sidebar.success("✅ API Key salvata con successo!")
                st.rerun()
    
    # Configurazione modello e base URL
    if provider != "Custom Cloud":
        model = st.sidebar.text_input(
            "Modello",
            value=default_model,
            help=f"Nome del modello {provider} da utilizzare"
        )
        base_url = default_base_url
        
        # Mostra base URL solo per info (non modificabile per provider standard)
        with st.sidebar.expander("🔧 Impostazioni Avanzate"):
            st.text_input(
                "Base URL (info)",
                value=base_url,
                disabled=True,
                help="URL base per le API (non modificabile per provider standard)"
            )
    else:
        model = st.sidebar.text_input("Nome Modello", value="")
        base_url = st.sidebar.text_input("Base URL", value="")

# ============================================================================
# PARAMETRI COMUNI
# ============================================================================

st.sidebar.markdown("---")
st.sidebar.markdown("### 🎛️ Parametri Generazione")

system_prompt = st.sidebar.text_area(
    "System Prompt",
    value="Sei un assistente utile e conciso.",
    height=100,
    help="Istruzioni di sistema per il modello"
)

temperature = st.sidebar.slider(
    "Temperature",
    min_value=0.0,
    max_value=2.0,
    value=0.7,
    step=0.1,
    help="Controlla la creatività delle risposte (0=deterministico, 2=molto creativo)"
)

# ============================================================================
# AREA PRINCIPALE
# ============================================================================

# Titolo dinamico
if connection_type == "Cloud provider":
    st.title(f"🍕 Datapizza → {provider} (Cloud)")
elif connection_type == "Remote host":
    st.title("🍕 Datapizza → Remote Host")
else:
    st.title("🍕 Datapizza → Ollama (Local)")

# Messaggio contestuale
if connection_type == "Local (Ollama)":
    st.info("💻 **Modalità Locale** - I tuoi dati rimangono sul tuo computer")
elif connection_type == "Remote host":
    st.info("🌐 **Modalità Remote** - Connessione a server remoto sulla tua rete")
else:
    st.warning("☁️ **Modalità Cloud** - I dati verranno inviati a server esterni. Presta attenzione alla privacy!")

# ============================================================================
# INDICATORE MODELLO SELEZIONATO
# ============================================================================

with st.container():
    col_info1, col_info2 = st.columns([1, 2])
    
    with col_info1:
        if model:
            origin = "locale" if (connection_type == "Local (Ollama)" and model in models_local) else "custom"
            st.metric(
                label="Modello Attivo",
                value=model,
                delta=origin
            )
        else:
            st.warning("⚠️ Nessun modello selezionato")
    
    with col_info2:
        st.caption(f"📍 **Endpoint:** `{base_url}`")
        st.caption(f"🎯 **Temperature:** {temperature} | **System Prompt:** {system_prompt[:50]}{'...' if len(system_prompt) > 50 else ''}")

st.markdown("---")

# ============================================================================
# AREA INPUT PROMPT
# ============================================================================

st.subheader("✍️ Inserisci il tuo Prompt")

default_prompt = "Spiegami in una frase perché Linux è il top."
prompt = st.text_area(
    "Prompt",
    value=default_prompt,
    height=150,
    help="Inserisci qui la tua domanda o richiesta per il modello"
)

# ============================================================================
# UPLOAD FILE
# ============================================================================

st.markdown("---")
st.subheader("📎 Allegati (opzionale)")

# Disabilita upload in cloud per privacy
if connection_type == "Cloud provider":
    st.warning("🔒 **Upload file disabilitato in modalità Cloud** per proteggere la tua privacy")
    uploaded_files = []
    embed_files = False
else:
    col_upload, col_embed = st.columns([3, 1])
    
    with col_upload:
        uploaded_files = st.file_uploader(
            "Carica file",
            type=None,
            accept_multiple_files=True,
            help="Trascina qui i file o clicca per selezionare"
        )
    
    with col_embed:
        embed_files = st.checkbox(
            "Incorpora nel prompt",
            value=True,
            help="Se attivo, il contenuto dei file di testo viene aggiunto al prompt"
        )

# Anteprima file caricati
if uploaded_files:
    st.markdown(f"**{len(uploaded_files)} file caricati:**")
    
    for idx, f in enumerate(uploaded_files):
        try:
            file_bytes = f.getvalue()
            file_size = len(file_bytes)
        except Exception:
            file_bytes = None
            file_size = 0
        
        label = f"📄 {f.name} — {file_size:,} bytes"
        
        with st.expander(label, expanded=False):
            if file_bytes is None:
                st.error("❌ Impossibile leggere il file")
                continue
            
            file_type = getattr(f, "type", "application/octet-stream")
            
            col_meta1, col_meta2 = st.columns(2)
            col_meta1.metric("Tipo", file_type)
            col_meta2.metric("Dimensione", f"{file_size:,} bytes")
            
            # Prova a mostrare anteprima testuale
            try:
                text_content = file_bytes.decode("utf-8")
                preview_length = min(len(text_content), 5000)
                preview = text_content[:preview_length]
                
                if len(text_content) > preview_length:
                    preview += f"\n\n... (mostrati {preview_length} di {len(text_content)} caratteri)"
                
                st.text_area(
                    "Anteprima contenuto",
                    value=preview,
                    height=200,
                    key=f"preview_{idx}"
                )
            except UnicodeDecodeError:
                st.info("📦 File binario - nessuna anteprima testuale disponibile")
            
            # Pulsante download
            st.download_button(
                "⬇️ Scarica file",
                data=file_bytes,
                file_name=f.name,
                key=f"download_{idx}"
            )

st.markdown("---")

# ============================================================================
# PULSANTI AZIONE
# ============================================================================

col_btn1, col_btn2, col_btn3 = st.columns([2, 2, 6])

with col_btn1:
    send_button = st.button("🚀 Invia", use_container_width=True, type="primary")

with col_btn2:
    clear_button = st.button("🗑️ Pulisci", use_container_width=True)

# ============================================================================
# LOGICA INVIO PROMPT
# ============================================================================

if send_button:
    # Validazione
    if not model:
        st.error("❌ Seleziona o inserisci un modello prima di inviare!")
    elif connection_type == "Cloud provider" and not api_key:
        st.error("❌ Inserisci una API key valida per il provider cloud!")
    else:
        try:
            # Crea client
            with st.spinner("🔧 Inizializzazione client..."):
                client = create_client(
                    connection_type=connection_type,
                    provider=provider,
                    api_key=api_key,
                    model=model,
                    system_prompt=system_prompt,
                    base_url=base_url,
                    temperature=temperature
                )
            
            # Prepara prompt con eventuali file
            prompt_to_send = prompt
            
            if uploaded_files and embed_files:
                file_contents = []
                for f in uploaded_files:
                    try:
                        data = f.getvalue()
                        try:
                            text = data.decode("utf-8")
                            file_contents.append(f"\n--- INIZIO FILE: {f.name} ---\n{text}\n--- FINE FILE: {f.name} ---\n")
                        except UnicodeDecodeError:
                            file_contents.append(f"\n--- FILE BINARIO: {f.name} ({len(data)} bytes) ---\n")
                    except Exception as e:
                        file_contents.append(f"\n--- ERRORE LETTURA FILE: {f.name} - {e} ---\n")
                
                if file_contents:
                    prompt_to_send = prompt + "\n\n" + "\n".join(file_contents)
            
            # Invoca il modello
            with st.spinner(f"🤖 Generazione risposta con {model}..."):
                response = client.invoke(prompt_to_send)
                response_text = getattr(response, "text", str(response))
                
                # Salva in session state
                st.session_state["last_response"] = response_text
                st.session_state["last_prompt"] = prompt
                st.session_state["last_model"] = model
                
                st.success("✅ Risposta generata con successo!")
                st.rerun()
        
        except Exception as e:
            st.error(f"❌ Errore durante l'invocazione: {e}")
            st.exception(e)

# ============================================================================
# PULSANTE PULISCI
# ============================================================================

if clear_button:
    st.session_state.pop("last_response", None)
    st.session_state.pop("last_prompt", None)
    st.session_state.pop("last_model", None)
    st.rerun()

# ============================================================================
# VISUALIZZAZIONE RISPOSTA
# ============================================================================

st.markdown("---")
st.subheader("💬 Risposta del Modello")

response_text = st.session_state.get("last_response", "")

if response_text:
    # Mostra info sulla risposta
    col_resp1, col_resp2 = st.columns([1, 3])
    
    with col_resp1:
        last_model = st.session_state.get("last_model", "N/A")
        st.metric("Generata con", last_model)
    
    with col_resp2:
        char_count = len(response_text)
        word_count = len(response_text.split())
        st.caption(f"📊 **Statistiche:** {char_count:,} caratteri | {word_count:,} parole")
    
    # Area di testo con risposta
    st.text_area(
        "Risposta completa",
        value=response_text,
        height=400,
        help="La risposta generata dal modello"
    )
    
    # Pulsanti azione risposta
    col_action1, col_action2, col_action3 = st.columns([2, 2, 6])
    
    with col_action1:
        st.download_button(
            "⬇️ Salva Risposta",
            data=response_text,
            file_name="risposta_llm.txt",
            mime="text/plain",
            use_container_width=True
        )
    
    with col_action2:
        if st.button("📋 Copia negli Appunti", use_container_width=True):
            st.code(response_text, language=None)
            st.info("👆 Seleziona il testo sopra e copialo")
    
    # Mostra anche il prompt originale
    with st.expander("📝 Visualizza Prompt Originale"):
        last_prompt = st.session_state.get("last_prompt", "")
        st.text_area("Prompt inviato", value=last_prompt, height=150, disabled=True)

else:
    st.info("👈 Inserisci un prompt e premi 'Invia' per ottenere una risposta dal modello")

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.caption("🍕 Powered by Datapizza AI | Developed by Gilles DeepAiUG | Dicembre 2025")

# ============================================================================
# STILE CSS PERSONALIZZATO PER MODALITÀ CLOUD
# ============================================================================

if connection_type == "Cloud provider":
    st.markdown("""
    <style>
    /* Stile per evidenziare modalità cloud */
    .stApp {
        border-top: 4px solid #ff6b6b !important;
    }
    
    /* Evidenzia sidebar in cloud mode */
    [data-testid="stSidebar"] {
        background-color: rgba(255, 107, 107, 0.05) !important;
    }
    
    /* Dark mode adjustments */
    @media (prefers-color-scheme: dark) {
        [data-testid="stSidebar"] {
            background-color: rgba(255, 107, 107, 0.1) !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)