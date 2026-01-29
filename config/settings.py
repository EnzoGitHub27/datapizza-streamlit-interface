# config/settings.py
# Datapizza v1.4.1 - Funzioni gestione configurazioni
# ============================================================================

import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv

from .constants import (
    WIKI_CONFIG_FILE,
    WIKI_CONFIG_ALT,
    REMOTE_SERVERS_CONFIG_FILE,
    REMOTE_SERVERS_CONFIG_ALT,
    SECURITY_SETTINGS_FILE,
    SECURITY_SETTINGS_ALT,
    SECRETS_DIR,
    WIKI_TYPES,
)

# ============================================================================
# YAML LOADER
# ============================================================================

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


def load_wiki_config() -> Optional[Dict[str, Any]]:
    """
    Carica configurazione sorgenti da file YAML.
    
    Cerca in ordine:
    1. wiki_sources.yaml nella root del progetto
    2. config/wiki_sources.yaml
    
    Supporta sia il vecchio formato (wikis) che il nuovo (sources).
    
    Returns:
        Dict con la configurazione o None se non trovata/errore
    """
    if not YAML_AVAILABLE:
        return None
    
    # Cerca file config
    config_path = None
    if WIKI_CONFIG_FILE.exists():
        config_path = WIKI_CONFIG_FILE
    elif WIKI_CONFIG_ALT.exists():
        config_path = WIKI_CONFIG_ALT
    
    if not config_path:
        return None
    
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        
        # Retrocompatibilità: converti vecchio formato "wikis" a "sources"
        if "wikis" in config and "sources" not in config:
            config["sources"] = {}
            for wiki_id, wiki_data in config["wikis"].items():
                # Aggiungi type: mediawiki se non presente
                if "type" not in wiki_data:
                    wiki_data["type"] = "mediawiki"
                config["sources"][wiki_id] = wiki_data
        
        return config
    except Exception as e:
        print(f"⚠️ Errore lettura config wiki: {e}")
        return None


def get_available_sources(config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Estrae lista sorgenti disponibili dalla config.
    
    Args:
        config: Configurazione YAML caricata
        
    Returns:
        Lista di dict con info sorgente (id, name, type, icon, etc.)
    """
    sources = []
    
    # Supporta sia "sources" (nuovo) che "wikis" (vecchio)
    sources_config = config.get("sources", config.get("wikis", {}))
    
    for source_id, source_data in sources_config.items():
        source_info = {
            "id": source_id,
            "name": source_data.get("name", source_id),
            "type": source_data.get("type", "mediawiki"),  # Default per retrocompatibilità
            "icon": source_data.get("icon", _get_default_icon(source_data.get("type", "mediawiki"))),
            "description": source_data.get("description", ""),
            "url": source_data.get("url", source_data.get("folder_path", "")),
            **source_data
        }
        sources.append(source_info)
    
    return sources


def get_available_wikis(config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Retrocompatibilità: alias per get_available_sources.
    Filtra solo sorgenti di tipo wiki (mediawiki, dokuwiki).
    
    Args:
        config: Configurazione YAML caricata
        
    Returns:
        Lista di dict con info wiki
    """
    all_sources = get_available_sources(config)
    wiki_types = ["mediawiki", "dokuwiki"]
    return [s for s in all_sources if s.get("type") in wiki_types]


def get_sources_by_type(config: Dict[str, Any], source_type: str) -> List[Dict[str, Any]]:
    """
    Filtra sorgenti per tipo specifico.
    
    Args:
        config: Configurazione YAML caricata
        source_type: Tipo sorgente ("mediawiki", "dokuwiki", "local")
        
    Returns:
        Lista di dict con info sorgenti del tipo specificato
    """
    all_sources = get_available_sources(config)
    return [s for s in all_sources if s.get("type") == source_type]


def _get_default_icon(source_type: str) -> str:
    """Ritorna icona di default per tipo sorgente."""
    icons = {
        "mediawiki": "🌐",
        "dokuwiki": "📘",
        "local": "📁",
        "confluence": "📄",
        "bookstack": "📚",
    }
    return icons.get(source_type, "📄")


def get_source_adapter_config(
    source_id: str, 
    config: Dict[str, Any], 
    global_settings: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Costruisce configurazione completa per un adapter.
    
    Merge impostazioni sorgente specifiche con global_settings.
    Espande variabili ambiente per credenziali.
    
    Args:
        source_id: ID della sorgente nella config
        config: Configurazione completa YAML
        global_settings: Impostazioni globali (opzionale)
        
    Returns:
        Dict con configurazione completa per l'adapter
    """
    # Supporta sia "sources" (nuovo) che "wikis" (vecchio)
    sources = config.get("sources", config.get("wikis", {}))
    source_data = sources.get(source_id, {})
    
    if global_settings is None:
        global_settings = config.get("global_settings", {})
    
    # Merge con global settings
    adapter_config = {
        **global_settings,
        **source_data,
    }
    
    # Gestisci variabili ambiente per credenziali
    _expand_env_vars(adapter_config, "username")
    _expand_env_vars(adapter_config, "password")
    _expand_env_vars(adapter_config, "api_key")
    _expand_env_vars(adapter_config, "token")
    
    return adapter_config


def get_wiki_adapter_config(
    wiki_id: str, 
    wiki_config: Dict[str, Any], 
    global_settings: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Retrocompatibilità: alias per get_source_adapter_config.
    
    Args:
        wiki_id: ID della wiki nella config
        wiki_config: Configurazione completa YAML
        global_settings: Impostazioni globali
        
    Returns:
        Dict con configurazione completa per l'adapter
    """
    return get_source_adapter_config(wiki_id, wiki_config, global_settings)


def _expand_env_vars(config: Dict[str, Any], key: str):
    """
    Espande variabili ambiente nel valore di una chiave.
    
    Formato supportato: ${NOME_VAR}
    
    Args:
        config: Dizionario da modificare
        key: Chiave da controllare
    """
    value = config.get(key, "")
    if isinstance(value, str) and "${" in value:
        # Estrai nome variabile
        env_var = value.strip("${}")
        config[key] = os.getenv(env_var, "")


def is_source_type_available(source_type: str) -> bool:
    """
    Verifica se le dipendenze per un tipo di sorgente sono installate.
    
    Args:
        source_type: Tipo sorgente
        
    Returns:
        True se disponibile
    """
    if source_type == "local":
        return True
    
    if source_type == "mediawiki":
        try:
            import mwclient
            return True
        except ImportError:
            return False
    
    if source_type == "dokuwiki":
        try:
            import dokuwiki
            return True
        except ImportError:
            return False
    
    # Altri tipi futuri
    return False


def get_missing_package(source_type: str) -> Optional[str]:
    """
    Ritorna il nome del pacchetto mancante per un tipo di sorgente.
    
    Args:
        source_type: Tipo sorgente
        
    Returns:
        Nome pacchetto da installare o None se disponibile
    """
    type_info = WIKI_TYPES.get(source_type, {})
    package = type_info.get("package")
    
    if package and not is_source_type_available(source_type):
        return package
    return None


# ============================================================================
# API KEYS
# ============================================================================

def load_api_key(provider_name: str, env_var_name: str) -> str:
    """
    Carica API key da variabile ambiente o file secrets.
    
    Cerca in ordine:
    1. Variabile ambiente
    2. File secrets/{provider_name}_key.txt
    
    Args:
        provider_name: Nome provider (es. "openai")
        env_var_name: Nome variabile ambiente (es. "OPENAI_API_KEY")
        
    Returns:
        API key o stringa vuota se non trovata
    """
    load_dotenv()
    
    # Prima cerca in env
    api_key = os.getenv(env_var_name)
    if api_key:
        return api_key
    
    # Poi cerca in file secrets
    key_file = SECRETS_DIR / f"{provider_name}_key.txt"
    if key_file.exists():
        try:
            with open(key_file, "r", encoding="utf-8") as f:
                return f.read().strip()
        except Exception:
            pass
    
    return ""


def save_api_key_to_file(provider_name: str, api_key: str) -> bool:
    """
    Salva API key in file secrets.

    Args:
        provider_name: Nome provider
        api_key: API key da salvare

    Returns:
        True se salvato con successo
    """
    try:
        SECRETS_DIR.mkdir(exist_ok=True)
        key_file = SECRETS_DIR / f"{provider_name}_key.txt"
        with open(key_file, "w", encoding="utf-8") as f:
            f.write(api_key)
        return True
    except Exception:
        return False


# ============================================================================
# REMOTE SERVERS LOADER
# ============================================================================

def load_remote_servers_config() -> Optional[Dict[str, Any]]:
    """
    Carica configurazione server remoti da file YAML.

    Cerca in ordine:
    1. remote_servers.yaml nella root del progetto
    2. config/remote_servers.yaml

    Returns:
        Dict con la configurazione o None se non trovata/errore
    """
    if not YAML_AVAILABLE:
        return None

    # Cerca file config
    config_path = None
    if REMOTE_SERVERS_CONFIG_FILE.exists():
        config_path = REMOTE_SERVERS_CONFIG_FILE
    elif REMOTE_SERVERS_CONFIG_ALT.exists():
        config_path = REMOTE_SERVERS_CONFIG_ALT

    if not config_path:
        return None

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        return config
    except Exception as e:
        print(f"⚠️ Errore lettura config remote servers: {e}")
        return None


def get_remote_server_mode(config: Optional[Dict[str, Any]]) -> str:
    """
    Ritorna la modalità di selezione server.

    Args:
        config: Configurazione caricata da load_remote_servers_config()

    Returns:
        "fixed", "selectable", o "custom_allowed" (default se config None)
    """
    if not config:
        return "custom_allowed"  # Comportamento legacy
    return config.get("mode", "custom_allowed")


def get_available_remote_servers(config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Estrae lista server disponibili dalla config.

    Args:
        config: Configurazione caricata da load_remote_servers_config()

    Returns:
        Lista di dict con info server (id, name, icon, host, port, description)
    """
    servers = []
    servers_config = config.get("servers", {})

    for server_id, server_data in servers_config.items():
        server_info = {
            "id": server_id,
            "name": server_data.get("name", server_id),
            "icon": server_data.get("icon", "🖥️"),
            "host": server_data.get("host", "localhost"),
            "port": server_data.get("port", 11434),
            "description": server_data.get("description", ""),
            **server_data
        }
        servers.append(server_info)

    return servers


def get_default_remote_server(config: Dict[str, Any]) -> Optional[str]:
    """
    Ritorna l'ID del server predefinito.

    Args:
        config: Configurazione caricata da load_remote_servers_config()

    Returns:
        ID del server default o None
    """
    return config.get("default_server")


def get_remote_servers_settings(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ritorna le impostazioni avanzate per i server remoti.

    Args:
        config: Configurazione caricata da load_remote_servers_config()

    Returns:
        Dict con settings (connection_timeout, show_refresh_button)
    """
    return config.get("settings", {
        "connection_timeout": 10,
        "show_refresh_button": True
    })


# ============================================================================
# SECURITY SETTINGS LOADER
# ============================================================================

def load_security_settings() -> Optional[Dict[str, Any]]:
    """
    Carica impostazioni di sicurezza da file YAML.

    Cerca in ordine:
    1. security_settings.yaml nella root del progetto
    2. config/security_settings.yaml

    Returns:
        Dict con la configurazione o None se non trovata/errore
    """
    if not YAML_AVAILABLE:
        return None

    # Cerca file config
    config_path = None
    if SECURITY_SETTINGS_FILE.exists():
        config_path = SECURITY_SETTINGS_FILE
    elif SECURITY_SETTINGS_ALT.exists():
        config_path = SECURITY_SETTINGS_ALT

    if not config_path:
        return None

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        return config
    except Exception as e:
        print(f"⚠️ Errore lettura security settings: {e}")
        return None


def should_show_saved_api_keys(config: Optional[Dict[str, Any]] = None) -> bool:
    """
    Verifica se le API key salvate devono essere mostrate in chiaro.

    Args:
        config: Configurazione caricata da load_security_settings() (opzionale)

    Returns:
        True se le key devono essere visibili, False altrimenti (default: False)
    """
    if config is None:
        config = load_security_settings()

    if not config:
        return False  # Default sicuro: nascondi le key

    return config.get("cloud_api_keys", {}).get("show_saved_keys", False)


def get_api_key_message(config: Optional[Dict[str, Any]], key_visible: bool) -> str:
    """
    Ritorna il messaggio da mostrare per lo stato della API key.

    Args:
        config: Configurazione caricata da load_security_settings()
        key_visible: Se True, usa messaggio per key visibile, altrimenti nascosta

    Returns:
        Messaggio da mostrare
    """
    if not config:
        config = load_security_settings()

    if not config:
        # Default messages
        return "✅ Key salvata (visibile)" if key_visible else "✅ Key salvata (nascosta per sicurezza)"

    cloud_settings = config.get("cloud_api_keys", {})

    if key_visible:
        return cloud_settings.get("visible_message", "✅ Key salvata (visibile)")
    else:
        return cloud_settings.get("hidden_message", "✅ Key salvata (nascosta per sicurezza)")
