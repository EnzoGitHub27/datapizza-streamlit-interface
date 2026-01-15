# ui/sidebar/llm_config.py
# Datapizza v1.5.0 - Configurazione LLM (Refactored for Layout Agnosticism)
# ============================================================================

import streamlit as st
from typing import Tuple, Optional

from config import CLOUD_PROVIDERS
from config.settings import load_api_key, save_api_key_to_file
from core import get_local_ollama_models


def render_llm_config() -> Tuple[str, str, str, str, str, str, float, int]:
    """
    Renderizza la configurazione LLM nel contesto corrente (st).
    Non utilizza più st.sidebar hardcoded.
    """
    
    # Tipo connessione
    current_connection = st.session_state.get("connection_type", "Local (Ollama)")
    
    connection_type = st.selectbox(
        "Tipo connessione", 
        ["Local (Ollama)", "Remote host", "Cloud provider"], 
        index=["Local (Ollama)", "Remote host", "Cloud provider"].index(current_connection)
    )
    
    # Privacy checks
    docs_uploaded = st.session_state.get("documents_uploaded_this_session", False)
    privacy_acknowledged = st.session_state.get("privacy_acknowledged_for_cloud", False)
    
    if connection_type == "Cloud provider" and docs_uploaded and not privacy_acknowledged:
        st.session_state["show_privacy_dialog"] = True
        st.warning(
            "⚠️ **Documenti in memoria!**\n\n"
            "Conferma richiesta prima di usare Cloud."
        )
    else:
        st.session_state["show_privacy_dialog"] = False
    
    st.session_state["connection_type"] = connection_type
    
    # Blocco Cloud se KB attiva
    if st.session_state.get("use_knowledge_base") and connection_type == "Cloud provider":
        st.error("🔒 **Cloud bloccato** (KB attiva)")
        connection_type = "Local (Ollama)"
        st.session_state["connection_type"] = connection_type
    
    # Variabili default
    base_url = "http://localhost:11434/v1"
    api_key = ""
    provider = None
    model = ""
    
    # ========== LOCAL (OLLAMA) ==========
    if connection_type == "Local (Ollama)":
        st.markdown("### 🖥️ Locale")
        base_url = st.text_input("Base URL", value=base_url)
        
        # Auto-load logic
        if "models_local" not in st.session_state or not st.session_state["models_local"]:
            st.session_state["models_local"] = get_local_ollama_models()


        def refresh_callback():
            st.session_state["models_local"] = get_local_ollama_models()

        c1, c2 = st.columns([3, 1])
        with c1:
            st.button("🔄 Aggiorna", use_container_width=True, key="llm_refresh_local", on_click=refresh_callback)

        
        models_local = st.session_state.get("models_local", [])
        with c2:
            if models_local:
                st.caption(f"{len(models_local)} modelli")
        
        if models_local:
            prev = st.session_state.get("model_select")
            idx = models_local.index(prev) if prev in models_local else 0
            model = st.selectbox("Modello", models_local, index=idx, key="model_select")
        else:
            model = st.text_input("Modello", value="llama3.2")
    
    # ========== REMOTE HOST ==========
    elif connection_type == "Remote host":
        st.markdown("### 🌐 Remote")
        hosts = [base_url]
        base_url = st.selectbox("Host", hosts)
        api_key = st.text_input("API Key", type="password")
        model = st.text_input("Modello", value="llama3.2")
    
    # ========== CLOUD PROVIDER ==========
    else:
        st.markdown("### ☁️ Cloud")
        provider = st.selectbox("Provider", list(CLOUD_PROVIDERS.keys()))
        
        config = CLOUD_PROVIDERS.get(provider, CLOUD_PROVIDERS["Custom"])
        existing_key = load_api_key(config["key_name"], config["env_var"])
        
        if existing_key:
            st.success("✅ Key trovata")
            api_key = existing_key
        else:
            key_input_id = f"input_apikey_{provider}"
            api_key = st.text_input("API Key", type="password", key=key_input_id)
            
            def save_callback():
                val = st.session_state.get(key_input_id)
                if val:
                    save_api_key_to_file(config["key_name"], val)
            
            if api_key:
                st.button("💾 Salva", key="llm_save_key", on_click=save_callback)
        
        model = st.text_input("Modello", value=config["default_model"])
        base_url = config["base_url"]
    
    # Update Session State
    st.session_state["current_model"] = model
    
    # ========== PARAMETRI ==========
    st.markdown("---")
    st.markdown("### 🎛️ Parametri")
    
    system_prompt = st.text_area(
        "System Prompt", 
        value="Sei un assistente utile. Rispondi in modo chiaro e preciso.", 
        height=80
    )
    
    temperature = st.slider("Temperature", 0.0, 2.0, 0.7, 0.1)
    max_messages = st.slider("Max messaggi", 10, 100, 50, 10)
    
    # Expose to global session for Submit handler in a different column
    st.session_state["api_key"] = api_key
    st.session_state["base_url"] = base_url
    st.session_state["system_prompt"] = system_prompt
    st.session_state["temperature"] = temperature
    st.session_state["max_messages"] = max_messages
    st.session_state["provider"] = provider
    
    return (
        connection_type, provider, api_key, model, base_url, 
        system_prompt, temperature, max_messages
    )
