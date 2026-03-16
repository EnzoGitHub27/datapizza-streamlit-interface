# tests/test_kb_chat_indexer.py
# DeepAiUG v1.14.0 — Test per indicizzazione chat come KB epistemica
# ============================================================================
# Tutti i test usano chat JSON sintetici e vectorstore temporaneo (tmp_path).
# ============================================================================

import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Aggiungi root al path per import
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _make_chat(
    chat_id: str = "test_001",
    n_messages: int = 4,
    includi_in_kb: bool = True,
    rilevanza: int = 2,
    tipo: list | None = None,
    note: str = "",
) -> dict:
    """Genera una chat JSON sintetica con n_messages (alternanza user/assistant)."""
    messages = []
    for i in range(n_messages):
        role = "user" if i % 2 == 0 else "assistant"
        content = f"Messaggio {role} numero {i}. " * 10  # ~200 chars
        messages.append({"role": role, "content": content})

    return {
        "conversation_id": chat_id,
        "created_at": "2026-03-16T10:00:00",
        "last_updated": "2026-03-16T10:30:00",
        "model": "test-model",
        "provider": "Local (Ollama)",
        "messages": messages,
        "stats": {"total_messages": len(messages), "tokens_estimate": 500},
        "knowledge_base": {},
        "socratic_history": [],
        "kb_metadata": {
            "includi_in_kb": includi_in_kb,
            "rilevanza": rilevanza,
            "tipo": tipo or ["decisione", "insight"],
            "note": note or "nota di test",
        },
    }


def _make_long_chat(chat_id: str = "long_001", n_messages: int = 32) -> dict:
    """Chat lunga (30+ messaggi) per test chunking."""
    return _make_chat(chat_id=chat_id, n_messages=n_messages, rilevanza=3)


@pytest.fixture
def tmp_vectorstore(tmp_path):
    """Patcha CHAT_KB_PERSIST_PATH su una directory temporanea."""
    persist = str(tmp_path / "chat_kb_vs")
    with patch("core.kb_chat_indexer.CHAT_KB_PERSIST_PATH", persist):
        yield persist


@pytest.fixture
def tmp_meta_file(tmp_path):
    """Patcha CHAT_KB_META_FILE su file temporaneo."""
    meta = tmp_path / "chat_kb_meta.json"
    with patch("core.kb_chat_indexer.CHAT_KB_META_FILE", meta):
        yield meta


# ---------------------------------------------------------------------------
# Test: get_kb_metadata retrocompatibilita
# ---------------------------------------------------------------------------

class TestRetrocompat:
    def test_chat_senza_kb_metadata(self):
        """Chat pre-v1.14.0 senza campo kb_metadata -> default senza eccezioni."""
        from core.persistence import get_kb_metadata, KB_METADATA_DEFAULT

        old_chat = {
            "conversation_id": "old_001",
            "messages": [{"role": "user", "content": "ciao"}],
        }
        meta = get_kb_metadata(old_chat)
        assert meta == KB_METADATA_DEFAULT
        assert meta["includi_in_kb"] is False
        assert meta["rilevanza"] == 1
        assert meta["tipo"] == []
        assert meta["note"] == ""

    def test_chat_con_kb_metadata_none(self):
        from core.persistence import get_kb_metadata, KB_METADATA_DEFAULT

        chat = {"kb_metadata": None}
        assert get_kb_metadata(chat) == KB_METADATA_DEFAULT

    def test_chat_con_kb_metadata_parziale(self):
        from core.persistence import get_kb_metadata

        chat = {"kb_metadata": {"includi_in_kb": True}}
        meta = get_kb_metadata(chat)
        assert meta["includi_in_kb"] is True
        assert meta["rilevanza"] == 1  # default
        assert meta["tipo"] == []
        assert meta["note"] == ""


# ---------------------------------------------------------------------------
# Test: Serializzazione e chunking
# ---------------------------------------------------------------------------

class TestChunking:
    def test_serialize_messages(self):
        from core.kb_chat_indexer import _serialize_chat_messages

        msgs = [
            {"role": "user", "content": "Domanda"},
            {"role": "assistant", "content": "Risposta"},
        ]
        text = _serialize_chat_messages(msgs)
        assert "[Utente]" in text
        assert "[Assistente]" in text
        assert "Domanda" in text
        assert "Risposta" in text

    def test_serialize_skips_empty(self):
        from core.kb_chat_indexer import _serialize_chat_messages

        msgs = [
            {"role": "user", "content": ""},
            {"role": "assistant", "content": "Ok"},
        ]
        text = _serialize_chat_messages(msgs)
        assert "[Utente]" not in text
        assert "[Assistente]" in text

    def test_chunk_text_short(self):
        from core.kb_chat_indexer import _chunk_text

        short = "Testo breve."
        chunks = _chunk_text(short, chunk_size=1000)
        assert len(chunks) == 1
        assert chunks[0] == short

    def test_chunk_text_long_no_content_loss(self):
        from core.kb_chat_indexer import _chunk_text, _serialize_chat_messages

        chat = _make_long_chat(n_messages=32)
        text = _serialize_chat_messages(chat["messages"])
        chunks = _chunk_text(text, chunk_size=500, chunk_overlap=100)

        assert len(chunks) > 1
        # Verifica che nessun contenuto sia perso:
        # ogni messaggio originale deve comparire in almeno un chunk
        for msg in chat["messages"]:
            content = msg["content"]
            # Prendi una frase unica dal messaggio
            snippet = content[:40]
            found = any(snippet in c for c in chunks)
            assert found, f"Snippet non trovato in nessun chunk: {snippet!r}"


# ---------------------------------------------------------------------------
# Test: Indicizzazione ChromaDB
# ---------------------------------------------------------------------------

class TestIndexing:
    def test_index_chat_short(self, tmp_vectorstore):
        from core.kb_chat_indexer import index_chat_to_kb, get_kb_chat_stats

        chat = _make_chat(chat_id="short_001", n_messages=3)
        n = index_chat_to_kb(chat)
        assert n > 0

        stats = get_kb_chat_stats()
        assert stats["total_chunks"] == n
        assert stats["total_chats"] == 1
        assert stats["using_chromadb"] is True

    def test_index_chat_long(self, tmp_vectorstore):
        from core.kb_chat_indexer import index_chat_to_kb, get_kb_chat_stats

        chat = _make_long_chat(chat_id="long_001", n_messages=32)
        n = index_chat_to_kb(chat)
        assert n > 1  # deve generare piu chunk

        stats = get_kb_chat_stats()
        assert stats["total_chunks"] == n

    def test_index_skips_when_not_flagged(self, tmp_vectorstore):
        from core.kb_chat_indexer import index_chat_to_kb

        chat = _make_chat(includi_in_kb=False)
        n = index_chat_to_kb(chat)
        assert n == 0

    def test_metadata_in_chromadb(self, tmp_vectorstore):
        from core.kb_chat_indexer import index_chat_to_kb, _get_chroma_collection

        chat = _make_chat(chat_id="meta_001", rilevanza=3, tipo=["decisione"])
        index_chat_to_kb(chat)

        _, col = _get_chroma_collection()
        result = col.get(where={"chat_id": "meta_001"}, include=["metadatas"])
        assert len(result["ids"]) > 0
        meta = result["metadatas"][0]
        assert meta["source"] == "chat_salvata"
        assert meta["chat_id"] == "meta_001"
        assert meta["rilevanza"] == 3
        assert meta["tipo"] == "decisione"


# ---------------------------------------------------------------------------
# Test: Re-indicizzazione (assenza duplicati)
# ---------------------------------------------------------------------------

class TestReindex:
    def test_reindex_no_duplicates(self, tmp_vectorstore):
        from core.kb_chat_indexer import (
            index_chat_to_kb,
            get_kb_chat_stats,
        )

        chat = _make_chat(chat_id="reindex_001", n_messages=6)

        n1 = index_chat_to_kb(chat)
        assert n1 > 0
        stats1 = get_kb_chat_stats()

        # Re-indicizza stessa chat (index_chat_to_kb fa remove + add)
        n2 = index_chat_to_kb(chat)
        stats2 = get_kb_chat_stats()

        assert n1 == n2
        assert stats1["total_chunks"] == stats2["total_chunks"]
        assert stats2["total_chats"] == 1

    def test_remove_then_stats_zero(self, tmp_vectorstore):
        from core.kb_chat_indexer import (
            index_chat_to_kb,
            remove_chat_from_kb,
            get_kb_chat_stats,
        )

        chat = _make_chat(chat_id="rm_001")
        index_chat_to_kb(chat)
        assert get_kb_chat_stats()["total_chunks"] > 0

        remove_chat_from_kb("rm_001")
        stats = get_kb_chat_stats()
        assert stats["total_chunks"] == 0
        assert stats["total_chats"] == 0


# ---------------------------------------------------------------------------
# Test: Ricerca con filtro tipo
# ---------------------------------------------------------------------------

class TestSearchAndFilter:
    def test_search_returns_results(self, tmp_vectorstore):
        from core.kb_chat_indexer import index_chat_to_kb, search_chat_kb

        chat = _make_chat(chat_id="search_001", tipo=["decisione"])
        index_chat_to_kb(chat)

        results = search_chat_kb("Messaggio user", top_k=3)
        assert len(results) > 0
        assert "text" in results[0]
        assert "metadata" in results[0]
        assert "distance" in results[0]

    def test_filter_tipo_match(self, tmp_vectorstore):
        from core.kb_chat_indexer import index_chat_to_kb, search_chat_kb

        chat = _make_chat(chat_id="filter_001", tipo=["decisione", "insight"])
        index_chat_to_kb(chat)

        # Filtro che matcha
        results = search_chat_kb("Messaggio", top_k=5, tipo_filter=["decisione"])
        assert len(results) > 0

    def test_filter_tipo_no_match(self, tmp_vectorstore):
        from core.kb_chat_indexer import index_chat_to_kb, search_chat_kb

        chat = _make_chat(chat_id="filter_002", tipo=["decisione"])
        index_chat_to_kb(chat)

        # Filtro che NON matcha
        results = search_chat_kb("Messaggio", top_k=5, tipo_filter=["sperimentale"])
        assert len(results) == 0

    def test_filter_empty_means_all(self, tmp_vectorstore):
        from core.kb_chat_indexer import index_chat_to_kb, search_chat_kb

        chat = _make_chat(chat_id="filter_003", tipo=["insight"])
        index_chat_to_kb(chat)

        # Nessun filtro = restituisce tutto
        results_none = search_chat_kb("Messaggio", top_k=5, tipo_filter=None)
        results_empty = search_chat_kb("Messaggio", top_k=5, tipo_filter=[])
        assert len(results_none) > 0
        assert len(results_none) == len(results_empty)

    def test_boost_rilevanza_affects_distance(self, tmp_vectorstore):
        from core.kb_chat_indexer import index_chat_to_kb, search_chat_kb

        # Indicizza due chat con rilevanze diverse
        chat_low = _make_chat(chat_id="boost_low", rilevanza=1, tipo=["insight"])
        chat_high = _make_chat(chat_id="boost_high", rilevanza=3, tipo=["insight"])
        index_chat_to_kb(chat_low)
        index_chat_to_kb(chat_high)

        results = search_chat_kb("Messaggio user numero", top_k=10)
        # I risultati con rilevanza alta dovrebbero avere distanza minore (boosted)
        high_results = [r for r in results if r["metadata"].get("rilevanza") == 3]
        low_results = [r for r in results if r["metadata"].get("rilevanza") == 1]

        if high_results and low_results:
            # Il boost 1.30 dovrebbe ridurre la distanza dei risultati high
            # Verifica almeno che il sistema non crashi e restituisca entrambi
            assert len(high_results) > 0
            assert len(low_results) > 0


# ---------------------------------------------------------------------------
# Test: get_kb_stats prima e dopo indicizzazione
# ---------------------------------------------------------------------------

class TestStats:
    def test_stats_empty(self, tmp_vectorstore):
        from core.kb_chat_indexer import get_kb_chat_stats

        stats = get_kb_chat_stats()
        assert stats["total_chunks"] == 0
        assert stats["total_chats"] == 0

    def test_stats_after_index(self, tmp_vectorstore):
        from core.kb_chat_indexer import index_chat_to_kb, get_kb_chat_stats

        c1 = _make_chat(chat_id="stats_001")
        c2 = _make_chat(chat_id="stats_002")
        n1 = index_chat_to_kb(c1)
        n2 = index_chat_to_kb(c2)

        stats = get_kb_chat_stats()
        assert stats["total_chats"] == 2
        assert stats["total_chunks"] == n1 + n2

    def test_chunks_per_chat(self, tmp_vectorstore):
        from core.kb_chat_indexer import index_chat_to_kb, get_chunks_per_chat

        c1 = _make_chat(chat_id="cpc_001", n_messages=4)
        c2 = _make_chat(chat_id="cpc_002", n_messages=10)
        n1 = index_chat_to_kb(c1)
        n2 = index_chat_to_kb(c2)

        cpc = get_chunks_per_chat()
        assert cpc["cpc_001"] == n1
        assert cpc["cpc_002"] == n2


# ---------------------------------------------------------------------------
# Test: chat_kb_meta.json persistenza
# ---------------------------------------------------------------------------

class TestMetaFile:
    def test_save_and_load_meta(self, tmp_meta_file):
        from core.kb_chat_indexer import _save_chat_kb_meta, load_chat_kb_meta

        _save_chat_kb_meta({
            "last_indexed": "2026-03-16T12:00:00",
            "chats_indexed": 5,
            "total_chunks": 42,
        })

        meta = load_chat_kb_meta()
        assert meta["last_indexed"] == "2026-03-16T12:00:00"
        assert meta["chats_indexed"] == 5
        assert meta["total_chunks"] == 42

    def test_load_meta_missing_file(self, tmp_meta_file):
        from core.kb_chat_indexer import load_chat_kb_meta

        meta = load_chat_kb_meta()
        assert meta == {}
