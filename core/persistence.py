# core/persistence.py
# DeepAiUG v1.14.0 - Persistenza conversazioni + KB Metadata
# ============================================================================

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

from config import (
    CONVERSATIONS_DIR,
    DEFAULT_CHUNK_SIZE,
    DEFAULT_CHUNK_OVERLAP,
    DEFAULT_TOP_K_RESULTS,
)


KB_METADATA_DEFAULT = {
    "includi_in_kb": False,
    "rilevanza": 1,
    "tipo": [],
    "note": "",
}


def get_kb_metadata(conversation_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Estrae kb_metadata da una conversazione con default sicuri.
    Garantisce retrocompatibilità con chat salvate prima di v1.14.0.
    """
    raw = conversation_data.get("kb_metadata")
    if not raw:
        return dict(KB_METADATA_DEFAULT)
    return {
        "includi_in_kb": raw.get("includi_in_kb", False),
        "rilevanza": raw.get("rilevanza", 1),
        "tipo": raw.get("tipo", []),
        "note": raw.get("note", ""),
    }


def ensure_conversations_dir():
    """Crea la directory conversations se non esiste."""
    CONVERSATIONS_DIR.mkdir(exist_ok=True)


def get_conversation_filename(conversation_id: str) -> Path:
    """
    Genera il percorso del file per una conversazione.
    
    Args:
        conversation_id: ID della conversazione
        
    Returns:
        Path del file JSON
    """
    return CONVERSATIONS_DIR / f"conv_{conversation_id}.json"


def save_conversation(
    conversation_id: str,
    created_at: str,
    messages: List[Dict[str, Any]],
    model: str,
    provider: str,
    tokens_estimate: int,
    kb_settings: Dict[str, Any] = None,
    socratic_history: List[Dict[str, Any]] = None,  # v1.9.0
    kb_metadata: Dict[str, Any] = None,  # v1.14.0
) -> bool:
    """
    Salva una conversazione su file.

    Args:
        conversation_id: ID univoco conversazione
        created_at: Timestamp creazione
        messages: Lista messaggi
        model: Modello usato
        provider: Provider/connection type
        tokens_estimate: Stima token usati
        kb_settings: Impostazioni Knowledge Base (opzionale)
        socratic_history: Esplorazioni socratiche serializzate (v1.9.0, opzionale)
        kb_metadata: Metadati per inclusione nella KB epistemica (v1.14.0, opzionale)

    Returns:
        True se salvato con successo
    """
    try:
        ensure_conversations_dir()

        conversation_data = {
            "conversation_id": conversation_id,
            "created_at": created_at,
            "last_updated": datetime.now().isoformat(),
            "model": model,
            "provider": provider,
            "messages": messages,
            "stats": {
                "total_messages": len(messages),
                "tokens_estimate": tokens_estimate
            },
            "knowledge_base": kb_settings or {},
            "socratic_history": socratic_history or [],  # v1.9.0
            "kb_metadata": kb_metadata or dict(KB_METADATA_DEFAULT),  # v1.14.0
        }
        
        filename = get_conversation_filename(conversation_id)
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(conversation_data, f, indent=2, ensure_ascii=False)
        
        return True
        
    except Exception as e:
        print(f"❌ Errore salvataggio conversazione: {e}")
        return False


def update_conversation_kb_metadata(
    conversation_id: str, kb_metadata: Dict[str, Any]
) -> bool:
    """
    Aggiorna solo il campo kb_metadata di una conversazione salvata (v1.14.0).
    Evita di riscrivere l'intera struttura tramite save_conversation.
    """
    try:
        filename = get_conversation_filename(conversation_id)
        if not filename.exists():
            return False
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
        data["kb_metadata"] = kb_metadata
        data["last_updated"] = datetime.now().isoformat()
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"❌ Errore aggiornamento kb_metadata: {e}")
        return False


def load_conversation(conversation_id: str) -> Optional[Dict[str, Any]]:
    """
    Carica una conversazione da file.
    
    Args:
        conversation_id: ID della conversazione
        
    Returns:
        Dizionario con dati conversazione o None se non trovata
    """
    try:
        filename = get_conversation_filename(conversation_id)
        if not filename.exists():
            return None
        
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
            
    except Exception as e:
        print(f"❌ Errore caricamento conversazione: {e}")
        return None


def list_saved_conversations() -> List[Dict[str, Any]]:
    """
    Elenca tutte le conversazioni salvate.
    
    Returns:
        Lista di dizionari con info conversazioni (id, created_at, model, etc.)
        ordinata per last_updated decrescente
    """
    try:
        ensure_conversations_dir()
        conversations = []
        
        for file_path in CONVERSATIONS_DIR.glob("conv_*.json"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                sensitivity = conversation_has_sensitive_content(data)
                conversations.append({
                    "id": data.get("conversation_id"),
                    "created_at": data.get("created_at"),
                    "last_updated": data.get("last_updated"),
                    "model": data.get("model"),
                    "provider": data.get("provider"),
                    "message_count": data.get("stats", {}).get("total_messages", 0),
                    "is_sensitive": sensitivity["is_sensitive"],
                    "reason": sensitivity["reason"],
                    "has_wiki": sensitivity["has_wiki"],
                    "has_folder": sensitivity["has_folder"],
                    "has_documents": sensitivity["has_documents"],
                    "kb_folder_path": data.get("knowledge_base", {}).get("kb_folder_path", ""),
                    "kb_metadata": get_kb_metadata(data),  # v1.14.0
                })
            except Exception:
                continue
        
        # Ordina per data aggiornamento
        conversations.sort(key=lambda x: x.get("last_updated", ""), reverse=True)
        return conversations
        
    except Exception:
        return []


def delete_conversation(conversation_id: str) -> bool:
    """
    Elimina una conversazione salvata.
    
    Args:
        conversation_id: ID della conversazione
        
    Returns:
        True se eliminata con successo
    """
    try:
        filename = get_conversation_filename(conversation_id)
        if filename.exists():
            filename.unlink()
            return True
    except Exception as e:
        print(f"❌ Errore eliminazione conversazione: {e}")
    return False


def get_conversation_preview(conversation_id: str, max_messages: int = 3) -> str:
    """
    Genera una preview testuale di una conversazione.
    
    Args:
        conversation_id: ID della conversazione
        max_messages: Numero massimo di messaggi da includere
        
    Returns:
        Stringa con preview o messaggio di errore
    """
    try:
        data = load_conversation(conversation_id)
        if not data:
            return "Non trovata"
        
        messages = data.get("messages", [])[:max_messages]
        lines = []
        
        for msg in messages:
            role = "👤" if msg["role"] == "user" else "🤖"
            content = msg["content"]
            if len(content) > 50:
                content = content[:50] + "..."
            lines.append(f"{role}: {content}")
        
        return "\n".join(lines) if lines else "Vuota"
        
    except Exception:
        return "Errore"


def extract_kb_settings(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Estrae impostazioni Knowledge Base da dati conversazione.

    Args:
        data: Dati conversazione caricati

    Returns:
        Dizionario con impostazioni KB
    """
    kb_settings = data.get("knowledge_base", {})

    return {
        "use_knowledge_base": kb_settings.get("use_knowledge_base", False),
        "kb_folder_path": kb_settings.get("kb_folder_path", ""),
        "kb_extensions": kb_settings.get("kb_extensions", [".md", ".txt", ".html"]),
        "kb_recursive": kb_settings.get("kb_recursive", True),
        "kb_chunk_size": kb_settings.get("kb_chunk_size", DEFAULT_CHUNK_SIZE),
        "kb_chunk_overlap": kb_settings.get("kb_chunk_overlap", DEFAULT_CHUNK_OVERLAP),
        "rag_top_k": kb_settings.get("rag_top_k", DEFAULT_TOP_K_RESULTS),
    }


def conversation_has_sensitive_content(conversation_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Verifica se la conversazione contiene contenuti sensibili per la privacy.

    Distingue il tipo di Knowledge Base tramite euristica:
    - kb_folder_path non vuoto → cartella locale (📁)
    - kb_folder_path vuoto con KB attiva → wiki MediaWiki/DokuWiki (📚)

    Args:
        conversation_data: Dati conversazione (JSON caricato)

    Returns:
        Dict con chiavi: has_documents, has_knowledge_base, has_wiki,
        has_folder, has_sources, is_sensitive, reason
    """
    kb_data = conversation_data.get("knowledge_base", {})
    has_kb = kb_data.get("use_knowledge_base", False)

    # Distinguish wiki from local folder via kb_folder_path heuristic:
    # wiki adapters don't set kb_folder_path, local folder adapter does
    kb_folder_path = kb_data.get("kb_folder_path", "")
    has_folder = has_kb and bool(kb_folder_path)
    has_wiki = has_kb and not kb_folder_path

    has_docs = False
    has_sources = False
    for msg in conversation_data.get("messages", []):
        if not has_docs and msg.get("attachments"):
            has_docs = True
        if not has_sources and msg.get("sources"):
            has_sources = True
        if has_docs and has_sources:
            break  # no need to scan further

    is_sensitive = has_kb or has_docs or has_sources

    # Build human-readable reason with specific labels
    parts: list[str] = []
    if has_wiki:
        parts.append("KB Wiki")
    if has_folder:
        parts.append("Cartella locale")
    if has_docs:
        parts.append("File allegati")
    if has_sources and not has_kb:
        parts.append("Fonti RAG")
    reason = " + ".join(parts) if parts else ""

    return {
        "has_documents": has_docs,
        "has_knowledge_base": has_kb,
        "has_wiki": has_wiki,
        "has_folder": has_folder,
        "has_sources": has_sources,
        "is_sensitive": is_sensitive,
        "reason": reason,
    }
