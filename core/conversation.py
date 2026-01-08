# core/conversation.py
# Datapizza v1.4.0 - Gestione conversazione in memoria
# ============================================================================

from datetime import datetime
from typing import Dict, Any, List, Optional


def create_message(
    role: str, 
    content: str, 
    model: str = None, 
    sources: List[str] = None
) -> Dict[str, Any]:
    """
    Crea un nuovo messaggio strutturato.
    
    Args:
        role: "user" o "assistant"
        content: Contenuto del messaggio
        model: Nome modello (per risposte assistant)
        sources: Lista fonti RAG (opzionale)
        
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
    
    if sources:
        message["sources"] = sources
    
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
    
    return [
        {"role": msg["role"], "content": msg["content"]} 
        for msg in messages
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
