# ui/sidebar/llm_config.py
# Datapizza v1.4.0 - Sidebar: Configurazione LLM
# ============================================================================

import streamlit as st
from typing import Tuple, Optional

from config import CLOUD_PROVIDERS
from config.settings import load_api_key, save_api_key_to_file
from core import get_local_ollama_models


def render_llm_config() -> Tuple[str, str, str, str, str, str, float, int]:
    """
    Renderizza la sezione configurazione LLM nella sidebar.
    
    Returns:
        Tupla con:
        - connection_type: Tipo connessione
        - provider: Provider cloud (se applicabile)
        - api_key: API key
        - model: Nome modello
        - base_url: URL base
        - system_prompt: System prompt
        - temperature: Temperatura
        - max_messages: Max messaggi in context
    """
    st.sidebar.header("⚙️ Configurazione")
    
    # Tipo connessione
    connection_type = st.sidebar.selectbox(
        "Tipo connessione", 
        ["Local (Ollama)", "Remote host", "Cloud provider"], 
        index=0
    )
    st.session_state["connection_type"] = connection_type
    
    # Blocco Cloud se Knowledge Base attiva (PRIVACY)
    if st.session_state.get("use_knowledge_base") and connection_type == "Cloud provider":
        st.sidebar.error("🔒 **Cloud bloccato**: Knowledge Base attiva. I tuoi documenti rimangono privati!")
        st.sidebar.info("Disattiva Knowledge Base o usa Local/Remote")
        connection_type = "Local (Ollama)"
        st.session_state["connection_type"] = connection_type
    
    # Variabili default
    base_url = "http://localhost:11434/v1"
    api_key = ""
    provider = None
    model = ""
    
    # ========== LOCAL (OLLAMA) ==========
    if connection_type == "Local (Ollama)":
        st.sidebar.markdown("### 🖥️ Locale")
        base_url = st.sidebar.text_input("Base URL", value=base_url)
        
        col_r, col_c = st.sidebar.columns([3, 1])
        with col_r:
            if st.button("🔄 Aggiorna", use_container_width=True):
                st.session_state["models_local"] = get_local_ollama_models()
        
        models_local = st.session_state.get("models_local", get_local_ollama_models())
        if not st.session_state.get("models_local"):
            st.session_state["models_local"] = models_local
        
        with col_c:
            if models_local:
                st.metric("", len(models_local))
        
        if models_local:
            prev = st.session_state.get("model_select")
            idx = models_local.index(prev) if prev in models_local else 0
            model = st.sidebar.selectbox("Modello", models_local, index=idx, key="model_select")
        else:
            model = st.sidebar.text_input("Modello", value="llama3.2")
    
    # ========== REMOTE HOST ==========
    elif connection_type == "Remote host":
        st.sidebar.markdown("### 🌐 Remote")
        hosts_text = st.sidebar.text_area(
            "Host", 
            value="http://192.168.1.10:11434/v1", 
            height=60
        )
        hosts = [h.strip() for h in hosts_text.splitlines() if h.strip()] or [base_url]
        base_url = st.sidebar.selectbox("Host", hosts)
        api_key = st.sidebar.text_input("API Key", type="password")
        model = st.sidebar.text_input("Modello", value="llama3.2")
    
    # ========== CLOUD PROVIDER ==========
    else:
        st.sidebar.markdown("### ☁️ Cloud")
        provider = st.sidebar.selectbox(
            "Provider", 
            list(CLOUD_PROVIDERS.keys())
        )
        
        config = CLOUD_PROVIDERS.get(provider, CLOUD_PROVIDERS["Custom"])
        pk = config["key_name"]
        ev = config["env_var"]
        dm = config["default_model"]
        db = config["base_url"]
        
        existing_key = load_api_key(pk, ev)
        if existing_key:
            st.sidebar.success("✅ Key trovata")
            api_key = existing_key
        else:
            api_key = st.sidebar.text_input("API Key", type="password")
            if api_key and st.sidebar.button("💾 Salva"):
                save_api_key_to_file(pk, api_key)
                st.rerun()
        
        model = st.sidebar.text_input("Modello", value=dm)
        base_url = db
    
    # Salva modello corrente
    st.session_state["current_model"] = model
    
    # ========== PARAMETRI LLM ==========
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🎛️ Parametri")
    
    system_prompt = st.sidebar.text_area(
        "System Prompt", 
        value="Sei un assistente utile. Rispondi in modo chiaro e preciso.", 
        height=80
    )
    
    temperature = st.sidebar.slider(
        "Temperature", 
        0.0, 2.0, 0.7, 0.1
    )
    
    max_messages = st.sidebar.slider(
        "Max messaggi", 
        10, 100, 50, 10
    )
    
    return (
        connection_type, 
        provider, 
        api_key, 
        model, 
        base_url, 
        system_prompt, 
        temperature, 
        max_messages
    )
