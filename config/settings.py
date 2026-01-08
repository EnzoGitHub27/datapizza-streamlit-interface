# config/settings.py
# Datapizza v1.4.0 - Funzioni gestione configurazioni
# ============================================================================

import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv

from .constants import (
    WIKI_CONFIG_FILE,
    WIKI_CONFIG_ALT,
    SECRETS_DIR,
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
    Carica configurazione wiki da file YAML.
    
    Cerca in ordine:
    1. wiki_sources.yaml nella root del progetto
    2. config/wiki_sources.yaml
    
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
        return config
    except Exception as e:
        print(f"⚠️ Errore lettura config wiki: {e}")
        return None


def get_available_wikis(config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Estrae lista wiki disponibili dalla config.
    
    Args:
        config: Configurazione YAML caricata
        
    Returns:
        Lista di dict con info wiki (id, name, description, url, etc.)
    """
    wikis = []
    
    wikis_config = config.get("wikis", {})
    for wiki_id, wiki_data in wikis_config.items():
        wiki_info = {
            "id": wiki_id,
            "name": wiki_data.get("name", wiki_id),
            "description": wiki_data.get("description", ""),
            "url": wiki_data.get("url", ""),
            **wiki_data  # Include tutti gli altri campi
        }
        wikis.append(wiki_info)
    
    return wikis


def get_wiki_adapter_config(
    wiki_id: str, 
    wiki_config: Dict[str, Any], 
    global_settings: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Costruisce configurazione completa per MediaWikiAdapter.
    
    Merge impostazioni wiki specifiche con global_settings.
    Espande variabili ambiente per credenziali.
    
    Args:
        wiki_id: ID della wiki nella config
        wiki_config: Configurazione completa YAML
        global_settings: Impostazioni globali da wiki_config
        
    Returns:
        Dict con configurazione completa per l'adapter
    """
    wiki_data = wiki_config.get("wikis", {}).get(wiki_id, {})
    
    # Merge con global settings
    config = {
        **global_settings,
        **wiki_data,
    }
    
    # Gestisci variabili ambiente per credenziali
    if "${" in str(config.get("username", "")):
        env_var = config["username"].strip("${}")
        config["username"] = os.getenv(env_var, "")
    
    if "${" in str(config.get("password", "")):
        env_var = config["password"].strip("${}")
        config["password"] = os.getenv(env_var, "")
    
    return config


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
