# core/llm_client.py
# DeepAiUG v1.4.0 - Client LLM
# ============================================================================

import subprocess
from typing import List, Any

import requests

from core.url_validator import is_blocked, BlockedURLError

from datapizza.clients import ClientFactory
from datapizza.clients.factory import Provider
from datapizza.clients.openai_like import OpenAILikeClient
from datapizza.type import Media, MediaBlock


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

        # H1b: blocco SSRF verso endpoint metadati cloud (link-local)
        blocked, reason = is_blocked(api_url)
        if blocked:
            print(f"⚠️ Richiesta non eseguita verso {api_url}: {reason}")
            return []

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
    temperature: float,
    hybrid: Any = None,
    on_anonymized: Any = None,
    pii_memory: Any = None,
) -> Any:
    """
    Il punto unico verso i modelli (SPEC §3).

    Senza `hybrid`, o con `hybrid.pii.enabled` falso, o con la destinazione
    in casa: il client di sempre (_create_raw_client), identico alla 1.15.4.
    Con rizzo-pii acceso e la destinazione fuori casa (core.egress):
    GuardedClient, che anonimizza prima dell'invio e ripristina in locale.
    Con il gateway di Annona acceso, rizzo-pii spento e la destinazione fuori
    casa: GatewayBlockedClient, che non manda niente (le chiamate laterali
    non passano da Annona e andrebbero al cloud in chiaro).

    Args:
        hybrid: HybridSettings (config.hybrid_settings), opzionale
        on_anonymized: callback(n_dati_tolti), opzionale
        pii_memory: PIISessionMemory della sessione (giro 7b), opzionale
    """
    if hybrid is not None:
        from core.egress import classify_destination

        pii_on = bool(getattr(hybrid.pii, "enabled", False))
        annona = getattr(hybrid, "annona", None)
        gateway_on = bool(annona is not None and getattr(annona, "enabled", False)
                          and getattr(annona, "mode", "read") == "gateway")
        if (pii_on or gateway_on) and classify_destination(
                connection_type, provider, base_url)["outside"]:
            if not pii_on:
                # giro 5b — col gateway acceso, le chiamate che non passano da
                # Annona non vanno al cloud in chiaro: senza rizzo-pii si bloccano
                from core.pii_guard import GatewayBlockedClient

                return GatewayBlockedClient()

            from core.pii_client import PIIClient
            from core.pii_guard import GuardedClient

            def factory(clean_system_prompt: str) -> Any:
                return _create_raw_client(
                    connection_type, provider, api_key, model,
                    clean_system_prompt, base_url, temperature,
                )

            return GuardedClient(
                client_factory=factory,
                system_prompt=system_prompt,
                pii=PIIClient(hybrid.pii.url, timeout=hybrid.pii.timeout_s),
                exclude_tags=hybrid.pii.exclude_tags,
                on_anonymized=on_anonymized,
                memory=pii_memory,
            )

    return _create_raw_client(
        connection_type, provider, api_key, model, system_prompt, base_url, temperature
    )


def _create_raw_client(
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
            # H1c: blocco SSRF — base_url arbitrario verso endpoint metadati cloud
            blocked, reason = is_blocked(base_url)
            if blocked:
                raise BlockedURLError(f"🔒 Connessione bloccata per sicurezza: {reason}")
            return OpenAILikeClient(
                api_key=api_key, 
                model=model, 
                system_prompt=system_prompt, 
                base_url=base_url, 
                temperature=temperature
            )
    else:
        # Local (Ollama) o Remote host
        # H1c: blocco SSRF — base_url arbitrario verso endpoint metadati cloud
        blocked, reason = is_blocked(base_url)
        if blocked:
            raise BlockedURLError(f"🔒 Connessione bloccata per sicurezza: {reason}")
        return OpenAILikeClient(
            api_key=api_key or "ollama", 
            model=model, 
            system_prompt=system_prompt, 
            base_url=base_url, 
            temperature=temperature
        )


# ADR-0001 — Vision local-only.
# L'adapter openai_like ricostruisce il data URI come data:image/{extension};base64,...
# quindi "extension" deve essere il sottotipo MIME (jpeg, non jpg).
_MIME_TO_EXTENSION = {
    "image/png": "png",
    "image/jpeg": "jpeg",
    "image/gif": "gif",
    "image/webp": "webp",
}


def build_media_blocks(images_data: List[dict]) -> List[MediaBlock]:
    """
    Converte le immagini preparate da enrich_prompt_with_files in MediaBlock
    Datapizza da passare a stream_invoke (ADR-0001).

    Args:
        images_data: Lista di dict con chiavi "base64" e "mime_type"

    Returns:
        Lista di MediaBlock (uno per immagine)
    """
    blocks = []
    for img in images_data:
        mime = img.get("mime_type", "")
        blocks.append(MediaBlock(media=Media(
            extension=_MIME_TO_EXTENSION.get(mime, mime.split("/")[-1] or "png"),
            media_type="image",
            source_type="base64",
            source=img["base64"],
        )))
    return blocks
