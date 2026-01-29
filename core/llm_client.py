# core/llm_client.py
# Datapizza v1.4.0 - Client LLM
# ============================================================================

import subprocess
from typing import List, Any

import requests

from datapizza.clients import ClientFactory
from datapizza.clients.factory import Provider
from datapizza.clients.openai_like import OpenAILikeClient


def get_local_ollama_models() -> List[str]:
    """
    Recupera lista modelli Ollama installati localmente.
    
    Esegue 'ollama list' e parsa l'output.
    
    Returns:
        Lista di nomi modelli disponibili
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
            # Salta righe vuote, header e separatori
            if not s or s.upper().startswith("NAME") or set(s) <= set("- "):
                continue
            parts = s.split()
            if parts:
                models.append(parts[0])
        
        return models

    except Exception:
        return []


def get_remote_ollama_models(base_url: str) -> List[str]:
    """
    Recupera lista modelli Ollama da server remoto via API HTTP.

    Chiama l'endpoint /api/tags del server Ollama remoto per ottenere
    la lista dei modelli disponibili.

    Args:
        base_url: URL completo del server (es. "http://192.168.1.10:11434/v1")

    Returns:
        Lista di nomi modelli disponibili sul server remoto
    """
    try:
        # Rimuovi /v1 se presente, aggiungi /api/tags
        api_url = base_url.replace("/v1", "").rstrip("/") + "/api/tags"

        response = requests.get(api_url, timeout=10)
        response.raise_for_status()

        data = response.json()
        models = []

        # L'API Ollama ritorna: {"models": [{"name": "llama3.2:latest", ...}, ...]}
        for model_info in data.get("models", []):
            model_name = model_info.get("name", "")
            if model_name:
                models.append(model_name)

        return models

    except Exception as e:
        print(f"⚠️ Errore recupero modelli remoti da {base_url}: {e}")
        return []


def create_client(
    connection_type: str, 
    provider: str, 
    api_key: str, 
    model: str, 
    system_prompt: str, 
    base_url: str, 
    temperature: float
) -> Any:
    """
    Crea client LLM in base alla configurazione.
    
    Supporta:
    - Cloud provider (OpenAI, Anthropic, Google)
    - Remote host (OpenAI-like API)
    - Local Ollama
    
    Args:
        connection_type: "Cloud provider" | "Remote host" | "Local (Ollama)"
        provider: Nome provider cloud (se applicabile)
        api_key: API key
        model: Nome modello
        system_prompt: System prompt
        base_url: URL base per API
        temperature: Temperatura generazione
        
    Returns:
        Client LLM configurato
    """
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
            # Custom provider
            return OpenAILikeClient(
                api_key=api_key, 
                model=model, 
                system_prompt=system_prompt, 
                base_url=base_url, 
                temperature=temperature
            )
    else:
        # Local (Ollama) o Remote host
        return OpenAILikeClient(
            api_key=api_key or "ollama", 
            model=model, 
            system_prompt=system_prompt, 
            base_url=base_url, 
            temperature=temperature
        )
