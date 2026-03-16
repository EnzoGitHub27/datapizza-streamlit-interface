# core/kb_chat_indexer.py
# DeepAiUG v1.14.0 - Indicizzazione chat salvate come KB epistemica
# ============================================================================
# Gestisce la collection ChromaDB "deepaiug_chat_kb" separata dalla wiki.
# Pattern replicato da rag/vector_store.py, con metadati specifici per chat.
# ============================================================================

import hashlib
import json
import math
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

from config import KNOWLEDGE_BASE_DIR
from core.persistence import get_kb_metadata, list_saved_conversations, load_conversation

CHAT_KB_META_FILE = KNOWLEDGE_BASE_DIR / "chat_kb_meta.json"

CHAT_KB_COLLECTION = "deepaiug_chat_kb"
CHAT_KB_PERSIST_PATH = str(KNOWLEDGE_BASE_DIR / "chat_kb_vectorstore")
CHROMA_BATCH_SIZE = 500

# Separatore tra turni nella serializzazione dei messaggi
TURN_SEPARATOR = "\n\n---\n\n"

# Boost per rilevanza nel retrieval
RILEVANZA_BOOST = {1: 1.0, 2: 1.15, 3: 1.30}


def _get_chroma_collection():
    """
    Ottiene la collection ChromaDB per le chat-KB.
    Usa lo stesso pattern di SimpleVectorStore: PersistentClient + get_or_create.

    Returns:
        Tupla (client, collection) o (None, None) se ChromaDB non disponibile.
    """
    try:
        import chromadb

        Path(CHAT_KB_PERSIST_PATH).mkdir(parents=True, exist_ok=True)
        client = chromadb.PersistentClient(path=CHAT_KB_PERSIST_PATH)
        collection = client.get_or_create_collection(
            name=CHAT_KB_COLLECTION,
            metadata={"description": "Knowledge Base epistemica da chat salvate"},
        )
        return client, collection
    except ImportError:
        print("⚠️ ChromaDB non installato. Chat KB non disponibile.")
        return None, None
    except Exception as e:
        print(f"⚠️ Errore inizializzazione ChromaDB chat-KB: {e}")
        return None, None


def _serialize_chat_messages(messages: List[Dict[str, Any]]) -> str:
    """
    Serializza i messaggi di una chat in un testo unico per il chunking.
    Ogni turno include ruolo + contenuto, separati da TURN_SEPARATOR.
    """
    parts = []
    for msg in messages:
        role = msg.get("role", "unknown")
        content = msg.get("content", "")
        if not content.strip():
            continue
        role_label = "Utente" if role == "user" else "Assistente"
        parts.append(f"[{role_label}]\n{content}")
    return TURN_SEPARATOR.join(parts)


def _chunk_text(text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[str]:
    """
    Chunking semplice del testo serializzato.
    Preferisce spezzare sui TURN_SEPARATOR, poi su doppia newline, poi su punto.
    """
    if len(text) <= chunk_size:
        return [text] if text.strip() else []

    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size

        if end >= len(text):
            chunk = text[start:].strip()
            if chunk:
                chunks.append(chunk)
            break

        # Cerca il miglior punto di split
        window = text[start:end]
        best = -1
        for sep in [TURN_SEPARATOR, "\n\n", "\n", ". ", " "]:
            pos = window.rfind(sep, len(window) // 3)
            if pos > 0:
                best = pos + len(sep)
                break

        if best <= 0:
            best = chunk_size

        chunk = text[start : start + best].strip()
        if chunk:
            chunks.append(chunk)

        start = start + best - chunk_overlap
        if start <= (start - best + chunk_overlap):
            start += 1  # safety

    return chunks


def _chunk_id(chat_id: str, chunk_index: int, text: str) -> str:
    """Genera un ID univoco e deterministico per un chunk di chat."""
    raw = f"chat_kb_{chat_id}_{chunk_index}_{text[:50]}"
    return hashlib.md5(raw.encode()).hexdigest()


# ============================================================================
# API PUBBLICA
# ============================================================================


def index_chat_to_kb(chat_json: dict) -> int:
    """
    Indicizza una singola chat nella collection deepaiug_chat_kb.

    Prerequisito: chat_json deve avere kb_metadata.includi_in_kb == True.
    Prima rimuove eventuali chunk precedenti della stessa chat (re-index pulito).

    Args:
        chat_json: Dizionario completo della chat (come da load_conversation)

    Returns:
        Numero di chunk indicizzati, 0 se skip o errore.
    """
    kb_meta = get_kb_metadata(chat_json)
    if not kb_meta.get("includi_in_kb"):
        return 0

    chat_id = chat_json.get("conversation_id", "")
    if not chat_id:
        return 0

    _, collection = _get_chroma_collection()
    if collection is None:
        return 0

    # Rimuovi chunk precedenti (re-index pulito)
    _remove_by_chat_id(collection, chat_id)

    # Serializza e chunka
    messages = chat_json.get("messages", [])
    if not messages:
        return 0

    text = _serialize_chat_messages(messages)
    if not text.strip():
        return 0

    chunks = _chunk_text(text)
    if not chunks:
        return 0

    # Metadati condivisi per tutti i chunk di questa chat
    chat_titolo = chat_json.get("titolo", chat_json.get("conversation_id", ""))
    chat_data = chat_json.get("created_at", "")
    rilevanza = kb_meta.get("rilevanza", 1)
    tipo_csv = ",".join(kb_meta.get("tipo", []))

    # Batch upsert
    total = len(chunks)
    n_batches = math.ceil(total / CHROMA_BATCH_SIZE)

    for b in range(n_batches):
        s = b * CHROMA_BATCH_SIZE
        e = min(s + CHROMA_BATCH_SIZE, total)
        batch = chunks[s:e]

        ids = [_chunk_id(chat_id, s + i, c) for i, c in enumerate(batch)]
        documents = list(batch)
        metadatas = [
            {
                "source": "chat_salvata",
                "chat_id": chat_id,
                "chat_titolo": chat_titolo,
                "rilevanza": rilevanza,
                "tipo": tipo_csv,
                "data": chat_data,
                "chunk_index": s + i,
            }
            for i in range(len(batch))
        ]

        try:
            collection.add(ids=ids, documents=documents, metadatas=metadatas)
        except Exception as exc:
            print(f"❌ Errore batch ChromaDB chat-KB: {exc}")
            return 0

    return total


def remove_chat_from_kb(chat_id: str) -> bool:
    """
    Rimuove tutti i chunk di una chat dalla collection.

    Args:
        chat_id: conversation_id della chat

    Returns:
        True se rimosso con successo (o nulla da rimuovere).
    """
    _, collection = _get_chroma_collection()
    if collection is None:
        return False
    return _remove_by_chat_id(collection, chat_id)


def _remove_by_chat_id(collection, chat_id: str) -> bool:
    """Rimuove chunk con where filter su chat_id."""
    try:
        existing = collection.get(where={"chat_id": chat_id})
        if existing and existing["ids"]:
            collection.delete(ids=existing["ids"])
        return True
    except Exception as exc:
        print(f"⚠️ Errore rimozione chat {chat_id} da KB: {exc}")
        return False


def get_kb_chat_stats() -> Dict[str, Any]:
    """
    Statistiche della collection chat-KB.

    Returns:
        Dict con total_chunks, total_chats, using_chromadb.
    """
    _, collection = _get_chroma_collection()
    if collection is None:
        return {"total_chunks": 0, "total_chats": 0, "using_chromadb": False}

    try:
        total_chunks = collection.count()
        # Conta chat distinte tramite get + set di chat_id
        all_meta = collection.get(include=["metadatas"])
        chat_ids = set()
        if all_meta and all_meta["metadatas"]:
            for m in all_meta["metadatas"]:
                cid = m.get("chat_id")
                if cid:
                    chat_ids.add(cid)
        return {
            "total_chunks": total_chunks,
            "total_chats": len(chat_ids),
            "using_chromadb": True,
        }
    except Exception as exc:
        print(f"⚠️ Errore stats chat-KB: {exc}")
        return {"total_chunks": 0, "total_chats": 0, "using_chromadb": False}


def get_chunks_per_chat() -> Dict[str, int]:
    """
    Ritorna un dizionario {chat_id: n_chunks} per tutte le chat indicizzate.
    """
    _, collection = _get_chroma_collection()
    if collection is None:
        return {}
    try:
        all_meta = collection.get(include=["metadatas"])
        counts: Dict[str, int] = {}
        if all_meta and all_meta["metadatas"]:
            for m in all_meta["metadatas"]:
                cid = m.get("chat_id", "")
                if cid:
                    counts[cid] = counts.get(cid, 0) + 1
        return counts
    except Exception:
        return {}


def load_chat_kb_meta() -> Dict[str, Any]:
    """Carica il file chat_kb_meta.json con timestamp ultima indicizzazione."""
    try:
        if CHAT_KB_META_FILE.exists():
            with open(CHAT_KB_META_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return {}


def _save_chat_kb_meta(data: Dict[str, Any]):
    """Salva il file chat_kb_meta.json."""
    try:
        CHAT_KB_META_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(CHAT_KB_META_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as exc:
        print(f"⚠️ Errore salvataggio chat_kb_meta.json: {exc}")


def search_chat_kb(
    query: str,
    top_k: int = 5,
    tipo_filter: List[str] | None = None,
) -> List[Dict[str, Any]]:
    """
    Cerca nella collection chat-KB e applica boost per rilevanza.

    Args:
        query: Testo della query
        top_k: Numero massimo risultati
        tipo_filter: Lista tipi da includere (filtro post-processing su CSV).
                     None o [] = nessun filtro.

    Returns:
        Lista di risultati con text, metadata, distance (boosted).
    """
    _, collection = _get_chroma_collection()
    if collection is None:
        return []

    try:
        count = collection.count()
        if count == 0:
            return []

        # Fetch extra results when filtering by tipo (post-processing)
        fetch_k = min(top_k * 3, count) if tipo_filter else min(top_k, count)
        results = collection.query(
            query_texts=[query],
            n_results=fetch_k,
            include=["documents", "metadatas", "distances"],
        )

        if not results or not results["documents"] or not results["documents"][0]:
            return []

        search_results = []
        for i, doc in enumerate(results["documents"][0]):
            meta = results["metadatas"][0][i] if results["metadatas"] else {}
            raw_distance = results["distances"][0][i] if results["distances"] else 1.0
            rilevanza = meta.get("rilevanza", 1)
            boost = RILEVANZA_BOOST.get(rilevanza, 1.0)
            # ChromaDB distance: lower = better. Boost riduce la distanza.
            adjusted_distance = raw_distance / boost
            search_results.append({
                "text": doc,
                "metadata": meta,
                "distance": adjusted_distance,
            })

        # Post-processing: filtro per tipo (CSV contains)
        if tipo_filter:
            filtered = []
            for r in search_results:
                tipo_csv = r["metadata"].get("tipo", "")
                tipo_set = set(t.strip() for t in tipo_csv.split(",") if t.strip())
                if tipo_set & set(tipo_filter):
                    filtered.append(r)
            search_results = filtered

        # Ri-ordina per distanza boosted (crescente = migliore)
        search_results.sort(key=lambda r: r["distance"])
        return search_results[:top_k]

    except Exception as exc:
        print(f"❌ Errore ricerca chat-KB: {exc}")
        return []


def reindex_all_chat_kb(progress_callback=None) -> Dict[str, int]:
    """
    Re-indicizza tutte le chat con includi_in_kb=True.
    Usato dal pulsante manuale nella sidebar.

    Args:
        progress_callback: Opzionale callback(status: str, progress: float)

    Returns:
        Dict con chats_indexed e total_chunks.
    """
    # Lista tutte le conversazioni salvate
    conversations = list_saved_conversations()
    kb_conversations = [
        c for c in conversations
        if c.get("kb_metadata", {}).get("includi_in_kb")
    ]

    total = len(kb_conversations)
    chats_indexed = 0
    total_chunks = 0

    if progress_callback:
        progress_callback(
            f"📚 Trovate {total} chat da indicizzare...",
            0.05 if total > 0 else 1.0,
        )

    for i, conv_info in enumerate(kb_conversations):
        chat_id = conv_info["id"]
        chat_data = load_conversation(chat_id)
        if not chat_data:
            continue

        n_chunks = index_chat_to_kb(chat_data)
        if n_chunks > 0:
            chats_indexed += 1
            total_chunks += n_chunks

        if progress_callback:
            progress_callback(
                f"📚 Chat {i + 1}/{total} — {total_chunks} chunk",
                (i + 1) / total if total > 0 else 1.0,
            )

    if progress_callback:
        progress_callback(
            f"✅ Indicizzate {chats_indexed} chat, {total_chunks} chunk totali",
            1.0,
        )

    # Salva metadati indicizzazione
    _save_chat_kb_meta({
        "last_indexed": datetime.now().isoformat(),
        "chats_indexed": chats_indexed,
        "total_chunks": total_chunks,
    })

    return {"chats_indexed": chats_indexed, "total_chunks": total_chunks}
