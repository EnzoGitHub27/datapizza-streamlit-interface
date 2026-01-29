# ui/sidebar/llm_config.py
# Datapizza v1.5.0 - Sidebar: Configurazione LLM
# ============================================================================
# 🆕 v1.5.0: Aggiunto controllo privacy per passaggio a Cloud con documenti
# ============================================================================

import streamlit as st
from typing import Tuple, Optional

from config import CLOUD_PROVIDERS
from config.settings import (
    load_api_key,
    save_api_key_to_file,
    load_security_settings,
    should_show_saved_api_keys,
    get_api_key_message
)
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
    # 🆕 v1.5.0: Controlla se mostrare warning privacy
    current_connection = st.session_state.get("connection_type", "Local (Ollama)")
    
    connection_type = st.sidebar.selectbox(
        "Tipo connessione", 
        ["Local (Ollama)", "Remote host", "Cloud provider"], 
        index=["Local (Ollama)", "Remote host", "Cloud provider"].index(current_connection)
    )
    
    # 🆕 v1.5.0: Rileva cambio verso Cloud con documenti in memoria
    docs_uploaded = st.session_state.get("documents_uploaded_this_session", False)
    privacy_acknowledged = st.session_state.get("privacy_acknowledged_for_cloud", False)
    
    if connection_type == "Cloud provider" and docs_uploaded and not privacy_acknowledged:
        # Segnala che serve il dialog di privacy (gestito in app.py)
        st.session_state["show_privacy_dialog"] = True
        st.sidebar.warning(
            "⚠️ **Documenti in memoria!**\n\n"
            "Conferma richiesta prima di usare Cloud."
        )
    else:
        st.session_state["show_privacy_dialog"] = False
    
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

        # Carica configurazione YAML
        from config.settings import (
            load_remote_servers_config,
            get_remote_server_mode,
            get_available_remote_servers,
            get_remote_servers_settings
        )
        from core import get_remote_ollama_models

        remote_config = load_remote_servers_config()
        mode = get_remote_server_mode(remote_config)

        selected_server_url = None

        # MODE: FIXED (solo server default, no scelta)
        if mode == "fixed" and remote_config:
            servers = get_available_remote_servers(remote_config)
            default_id = remote_config.get("default_server")
            default_server = next((s for s in servers if s["id"] == default_id), servers[0] if servers else None)

            if default_server:
                st.sidebar.info(f"{default_server['icon']} {default_server['name']}")
                if default_server.get("description"):
                    st.sidebar.caption(default_server["description"])
                selected_server_url = f"http://{default_server['host']}:{default_server['port']}/v1"
            else:
                st.sidebar.error("⚠️ Nessun server configurato in remote_servers.yaml")
                selected_server_url = "http://localhost:11434/v1"

        # MODE: SELECTABLE (solo lista, no manuale)
        elif mode == "selectable" and remote_config:
            servers = get_available_remote_servers(remote_config)

            if servers:
                server_options = [f"{s['icon']} {s['name']}" for s in servers]
                selected_idx = st.sidebar.selectbox(
                    "Server",
                    range(len(servers)),
                    format_func=lambda i: server_options[i]
                )
                selected_server = servers[selected_idx]
                if selected_server.get("description"):
                    st.sidebar.caption(selected_server["description"])
                selected_server_url = f"http://{selected_server['host']}:{selected_server['port']}/v1"
            else:
                st.sidebar.error("⚠️ Nessun server configurato in remote_servers.yaml")
                selected_server_url = "http://localhost:11434/v1"

        # MODE: CUSTOM_ALLOWED (lista + manuale) o legacy (no yaml)
        else:
            options = []
            server_map = {}

            # Se esiste YAML, aggiungi server configurati
            if remote_config:
                servers = get_available_remote_servers(remote_config)
                for s in servers:
                    label = f"{s['icon']} {s['name']}"
                    url = f"http://{s['host']}:{s['port']}/v1"
                    options.append(label)
                    server_map[label] = (url, s.get("description", ""))

            # Aggiungi opzione manuale
            manual_option = "✏️ Inserisci manualmente..."
            options.append(manual_option)

            # Se non ci sono server YAML, default a manuale
            if not options[:-1]:
                selected_option = manual_option
            else:
                selected_option = st.sidebar.selectbox("Server", options)

            # Se manuale, mostra text_input
            if selected_option == manual_option:
                selected_server_url = st.sidebar.text_input(
                    "Host",
                    value="http://192.168.1.10:11434/v1"
                )
            else:
                selected_server_url, description = server_map[selected_option]
                # Mostra descrizione se disponibile
                if description:
                    st.sidebar.caption(description)

        base_url = selected_server_url
        api_key = st.sidebar.text_input("API Key (opzionale)", type="password", value="")

        # Bottone refresh modelli + dropdown
        settings = get_remote_servers_settings(remote_config) if remote_config else {"show_refresh_button": True}

        if settings.get("show_refresh_button", True):
            col_r, col_c = st.sidebar.columns([3, 1])
            with col_r:
                if st.button("🔄 Aggiorna modelli", use_container_width=True, key="refresh_remote"):
                    with st.spinner("Recupero modelli..."):
                        st.session_state["models_remote"] = get_remote_ollama_models(base_url)

            models_remote = st.session_state.get("models_remote", [])

            with col_c:
                if models_remote:
                    st.metric("", len(models_remote))

            if models_remote:
                prev = st.session_state.get("model_select_remote")
                idx = models_remote.index(prev) if prev in models_remote else 0
                model = st.sidebar.selectbox("Modello", models_remote, index=idx, key="model_select_remote")
            else:
                model = st.sidebar.text_input("Modello", value="llama3.2")
        else:
            # Nessun bottone refresh, solo text_input
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

        # Carica impostazioni sicurezza
        security_config = load_security_settings()
        show_keys = should_show_saved_api_keys(security_config)

        # Se esiste una key salvata
        if existing_key:
            # Se le key NON devono essere visibili (default sicuro)
            if not show_keys:
                # Mostra solo messaggio, non la key
                message = get_api_key_message(security_config, key_visible=False)
                st.sidebar.success(message)

                # Flag per permettere cambio key
                change_key_flag = f"change_key_{pk}"
                if change_key_flag not in st.session_state:
                    st.session_state[change_key_flag] = False

                # Bottone per usare altra key
                if not st.session_state[change_key_flag]:
                    if st.sidebar.button("🔄 Usa altra key", key=f"btn_change_{pk}"):
                        st.session_state[change_key_flag] = True
                        st.rerun()
                    # Usa la key esistente
                    api_key = existing_key
                else:
                    # Modalità cambio key: mostra input
                    api_key = st.sidebar.text_input("Nuova API Key", type="password", key=f"new_key_{pk}")
                    col1, col2 = st.sidebar.columns(2)
                    with col1:
                        if st.button("💾 Salva", key=f"save_new_{pk}"):
                            if api_key:
                                save_api_key_to_file(pk, api_key)
                                st.session_state[change_key_flag] = False
                                st.sidebar.success("Key aggiornata!")
                                st.rerun()
                    with col2:
                        if st.button("❌ Annulla", key=f"cancel_new_{pk}"):
                            st.session_state[change_key_flag] = False
                            api_key = existing_key
                            st.rerun()

            # Se le key DEVONO essere visibili (configurato dal sistemista)
            else:
                message = get_api_key_message(security_config, key_visible=True)
                st.sidebar.success(message)

                # Usa session_state per permettere modifica
                session_key = f"api_key_{pk}"
                if session_key not in st.session_state:
                    st.session_state[session_key] = existing_key

                api_key = st.sidebar.text_input(
                    "API Key",
                    type="password",
                    value=st.session_state[session_key],
                    key=f"input_api_key_{pk}"
                )

                # Aggiorna session_state se modificato
                if api_key != st.session_state[session_key]:
                    st.session_state[session_key] = api_key

                # Bottone per salvare modifiche
                if st.sidebar.button("💾 Salva modifiche"):
                    save_api_key_to_file(pk, api_key)
                    st.sidebar.success("Key aggiornata!")
                    st.rerun()
        else:
            # Nessuna key esistente, input vuoto
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
