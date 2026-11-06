# core/conversation.py
# DeepAiUG v1.4.0 - Gestione conversazione in memoria
# ============================================================================

import re
from datetime import datetime
from typing import Dict, Any, List, Optional

# v1.16.0 (decisione 11) — una domanda che non ha avuto risposta resta in chat
# con l'errore accanto, anche dopo il rerun e ricaricando la conversazione.
SEND_NOT_SENT = "non_inviata"   # non è partita (client, rete, connessione)
SEND_REJECTED = "rifiutata"     # partita, il fornitore ha risposto con un errore
SEND_EMPTY = "senza_risposta"   # partita, ma nessun testo (gateway di Annona, giro 7b)

# nomi di eccezione che dicono «non è partita»
_NOT_SENT_ERRORS = (
    "APIConnectionError", "ConnectError", "ConnectionError", "ConnectTimeout",
    "BlockedURLError", "NewConnectionError", "MaxRetryError",
)

# chiavi e token da non salvare mai nel messaggio d'errore
_SECRET_PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9_\-*]{6,}"),
    re.compile(r"AIza[0-9A-Za-z_\-]{10,}"),
    re.compile(r"(?i)(api[_-]?key|token|authorization|bearer)([\"'\s:=]+)[^\s\"',}]+"),
]


def create_message(
    role: str, 
    content: str, 
    model: str = None, 
    sources: List[str] = None,
    provider: str = None,  # v1.15.4
) -> Dict[str, Any]:
    """
    Crea un nuovo messaggio strutturato.
    
    Args:
        role: "user" o "assistant"
        content: Contenuto del messaggio
        model: Nome modello (per risposte assistant)
        sources: Lista fonti RAG (opzionale)
        provider: Tipo di connessione che ha risposto (v1.15.4, per assistant)
        
    Returns:
        Dizionario messaggio
    """
    message = {
        "role": role,
        "content": content,
        "timestamp": datetime.now().isoformat(),
    }
    
    if role == "assistant" and model:
        message["model"] = model
    if role == "assistant" and provider:
        message["provider"] = provider
    
    if sources:
        message["sources"] = sources
    
    return message


def redact_secrets(text: str) -> str:
    """Toglie da un messaggio d'errore ciò che somiglia a una chiave o a un token."""
    out = text or ""
    for pat in _SECRET_PATTERNS:
        if pat.groups >= 2:
            out = pat.sub(lambda m: f"{m.group(1)}{m.group(2)}[nascosto]", out)
        else:
            out = pat.sub("[chiave nascosta]", out)
    return out


def classify_send_error(exc: BaseException, stream_started: bool) -> str:
    """«non_inviata» se la richiesta non è partita, «rifiutata» se il fornitore ha detto no."""
    if not stream_started:
        return SEND_NOT_SENT
    names = {type(exc).__name__} | {c.__name__ for c in type(exc).__mro__}
    if names & set(_NOT_SENT_ERRORS):
        return SEND_NOT_SENT
    return SEND_REJECTED


def mark_send_failed(message: Dict[str, Any], status: str, error: BaseException) -> Dict[str, Any]:
    """Segna la domanda come non inviata o rifiutata, con l'errore (senza chiavi)."""
    detail = redact_secrets(f"{type(error).__name__}: {error}")
    message["send_status"] = status
    message["send_error"] = detail[:300]
    return message


def get_conversation_history(
    messages: List[Dict[str, Any]], 
    max_messages: int = None
) -> List[Dict[str, str]]:
    """
    Estrae cronologia conversazione per il prompt LLM.
    
    Args:
        messages: Lista messaggi completa
        max_messages: Limite messaggi (opzionale)
        
    Returns:
        Lista di {role, content} per il prompt
    """
    if max_messages and len(messages) > max_messages:
        messages = messages[-max_messages:]
    
    # v1.16.0 — le domande non inviate o rifiutate non tornano al modello
    return [
        {"role": msg["role"], "content": msg["content"]} 
        for msg in messages
        if not msg.get("send_status")
    ]


def estimate_tokens(text: str) -> int:
    """
    Stima approssimativa dei token in un testo.
    
    Usa la regola empirica: ~4 caratteri per token.
    
    Args:
        text: Testo da stimare
        
    Returns:
        Stima token
    """
    return len(text) // 4


def estimate_conversation_tokens(messages: List[Dict[str, Any]]) -> int:
    """
    Stima totale token di una conversazione.
    
    Args:
        messages: Lista messaggi
        
    Returns:
        Stima totale token
    """
    return sum(estimate_tokens(msg.get("content", "")) for msg in messages)


def generate_conversation_id() -> str:
    """
    Genera un nuovo ID conversazione.
    
    Returns:
        ID nel formato YYYYMMDD_HHMMSS
    """
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def build_rag_prompt(
    user_input: str,
    system_prompt: str,
    context_text: str,
    history: List[Dict[str, str]] = None
) -> str:
    """
    Costruisce il prompt completo con contesto RAG.
    
    Args:
        user_input: Domanda dell'utente
        system_prompt: System prompt base
        context_text: Contesto dai documenti
        history: Cronologia conversazione (opzionale)
        
    Returns:
        Prompt completo per l'LLM
    """
    if context_text:
        # System prompt arricchito con contesto
        rag_system = f"""{system_prompt}

IMPORTANTE: Usa le seguenti informazioni dalla Knowledge Base per rispondere. 
Se la risposta non è presente nei documenti, dillo chiaramente.
Cita sempre le fonti quando usi informazioni dai documenti.

--- DOCUMENTI RILEVANTI ---
{context_text}
--- FINE DOCUMENTI ---"""
        
        return f"{rag_system}\n\nUtente: {user_input}\n\nAssistente:"
    else:
        # Prompt normale con cronologia
        if history:
            context = ""
            for msg in history[:-1]:  # Escludi ultimo messaggio (la domanda attuale)
                role_label = "Utente" if msg["role"] == "user" else "AI"
                context += f"{role_label}: {msg['content']}\n\n"
            return f"{context}Utente: {user_input}\n\nAI:" if context else user_input
        else:
            return user_input


def format_time_from_iso(iso_timestamp: str) -> str:
    """
    Formatta un timestamp ISO in formato HH:MM:SS.
    
    Args:
        iso_timestamp: Timestamp ISO
        
    Returns:
        Stringa formattata o stringa vuota se errore
    """
    try:
        return datetime.fromisoformat(iso_timestamp).strftime("%H:%M:%S")
    except:
        return ""


def conversation_models(
    messages: List[Dict[str, Any]],
    fallback_model: str = "",
    fallback_provider: str = "",
) -> Dict[str, Any]:
    """
    Modello e provider che hanno risposto davvero (v1.15.4).

    - model/provider: quelli dell'ultima risposta dell'assistente che ha
      `model`. Se quel messaggio non ha `provider` (chat salvate prima della
      v1.15.4), il provider di ripiego si usa solo se il suo modello è lo
      stesso; altrimenti resta "" (meglio vuoto che sbagliato).
    - models_used: i modelli delle risposte, in ordine, senza doppioni.
    - Senza risposte con `model`: il ripiego (sidebar o testata del file).
    """
    used: List[str] = []
    last: Optional[Dict[str, Any]] = None
    for msg in messages or []:
        if msg.get("role") != "assistant" or not msg.get("model"):
            continue
        last = msg
        if msg["model"] not in used:
            used.append(msg["model"])

    if last is None:
        return {"model": fallback_model or "", "provider": fallback_provider or "", "models_used": []}

    provider = last.get("provider") or (
        fallback_provider if last["model"] == fallback_model else ""
    )
    return {"model": last["model"], "provider": provider or "", "models_used": used}
