# tests/test_embedding_failure_keeps_kb.py
# DeepAiUG v1.16.1 — voce 16 del giro 8: un modello e5 che non si carica non
# svuota mai le KB.
# ============================================================================
# Fino alla 1.16.0, se il modello degli embedding non si caricava (anche per un
# problema passeggero), il tag diventava «chromadb_default»: la KB documentale
# e la KB Chat venivano cancellate perché «il modello è cambiato», e di nuovo
# al ritorno del modello. Dalla 1.16.1: se il modello configurato non si
# carica, la KB non si usa e non si tocca; nessun passaggio automatico a un
# altro embedding. Modello FINTO (vettori a 4 dimensioni), ChromaDB vero in
# tmp_path, chat inventate.
# ============================================================================

import pytest

from rag import embeddings


class FakeHelper:
    """Al posto di _EmbeddingsHelper: niente modello vero, niente rete."""

    fail = False

    def __init__(self, model_name):
        if FakeHelper.fail:
            raise OSError("huggingface.co non raggiungibile (finto)")
        self.model_name = model_name

    @staticmethod
    def _vec(t):
        return [float(len(t) % 7) + 1.0, float(t.count("a")) + 1.0, 1.0, float(t.count("e")) + 1.0]

    def encode_query(self, texts):
        return [self._vec(t) for t in texts]

    def encode_passages(self, texts):
        return [self._vec(t) for t in texts]


def _restart():
    """Come un riavvio dell'app: i singleton del modello si azzerano."""
    embeddings._helper_singleton = None
    embeddings._helper_init_failed = False
    embeddings._embedding_function_singleton = None


@pytest.fixture
def world(monkeypatch, tmp_path):
    import core.kb_chat_indexer as kci

    monkeypatch.setattr(embeddings, "_EmbeddingsHelper", FakeHelper)
    monkeypatch.setattr(kci, "CHAT_KB_PERSIST_PATH", str(tmp_path / "chat_kb_vs"))
    monkeypatch.setattr(kci, "CHAT_KB_META_FILE", tmp_path / "chat_kb_meta.json")
    monkeypatch.setattr("core.persistence.CONVERSATIONS_DIR", tmp_path / "conversations")
    (tmp_path / "conversations").mkdir()
    FakeHelper.fail = False
    _restart()
    yield tmp_path
    FakeHelper.fail = False
    _restart()


def _doc_store(tmp_path):
    from rag.vector_store import SimpleVectorStore

    return SimpleVectorStore(persist_path=str(tmp_path / "kb_vs"))


def _fill(tmp_path):
    from rag.models import Chunk, Document
    from core.kb_chat_indexer import index_chat_to_kb
    from tests.test_kb_chat_indexer import _make_chat

    store = _doc_store(tmp_path)
    doc = Document(str(tmp_path / "nota.md"), "testo")
    store.add_chunks([Chunk("alfa beta", doc, 0, 0, 9), Chunk("gamma delta", doc, 1, 10, 21)])
    n_chat = index_chat_to_kb(_make_chat(chat_id="chat_vera"))
    assert store.get_stats()["chunk_count"] == 2 and n_chat > 0
    return n_chat


def _chat_count():
    from core.kb_chat_indexer import get_kb_chat_stats

    return get_kb_chat_stats()["total_chunks"]


def test_failure_then_return_keeps_both_kb(world):
    n_chat = _fill(world)

    _restart()
    FakeHelper.fail = True  # il modello non si carica
    store = _doc_store(world)
    assert store.search("alfa") == []
    store.clear()          # non tocca niente
    from core.kb_chat_indexer import search_chat_kb

    assert search_chat_kb("Messaggio") == []

    _restart()
    FakeHelper.fail = False  # il modello torna
    store = _doc_store(world)
    assert store.get_stats()["chunk_count"] == 2
    assert _chat_count() == n_chat
    assert store.search("alfa"), "con il modello di nuovo a posto la KB risponde"


def test_unavailable_is_reported(world):
    _restart()
    FakeHelper.fail = True
    assert embeddings.embedding_unavailable()
    _restart()
    FakeHelper.fail = False
    assert embeddings.embedding_unavailable() is None


def test_no_automatic_switch_to_another_embedding(world):
    _restart()
    FakeHelper.fail = True
    assert embeddings.get_active_model_tag() == embeddings.EMBEDDING_MODEL_TAG
    assert embeddings.get_embedding_function() is None
    msg = embeddings.embedding_unavailable()
    assert embeddings.EMBEDDING_MODEL_NAME in msg and "Knowledge Base" in msg


def test_indexing_refused_without_model(world):
    from rag.manager import KnowledgeBaseManager

    _fill(world)
    _restart()
    FakeHelper.fail = True

    class Adapter:
        def load_documents(self):
            from rag.models import Document
            return [Document(str(world / "nuova.md"), "testo nuovo " * 20)]

    kb = KnowledgeBaseManager()
    kb.vector_store = _doc_store(world)
    kb.set_adapter(Adapter())
    assert kb.index_documents() is False

    _restart()
    FakeHelper.fail = False
    assert _doc_store(world).get_stats()["chunk_count"] == 2  # la KB vecchia è intatta


def test_chat_kb_reindex_refused_without_model(world):
    from core.kb_chat_indexer import reindex_all_chat_kb

    n_chat = _fill(world)
    _restart()
    FakeHelper.fail = True
    result = reindex_all_chat_kb()
    assert result.get("embedding_unavailable")
    assert result["chats_indexed"] == 0

    _restart()
    FakeHelper.fail = False
    assert _chat_count() == n_chat


def test_delete_still_removes_chunks_without_model(world):
    # eliminare una conversazione non richiede il modello: i suoi pezzi vanno via lo stesso
    from core.kb_chat_indexer import remove_chat_from_kb

    _fill(world)
    _restart()
    FakeHelper.fail = True
    assert remove_chat_from_kb("chat_vera") is True

    _restart()
    FakeHelper.fail = False
    assert _chat_count() == 0


def test_model_retries_after_interval(world, monkeypatch):
    # un problema passeggero non resta fino al riavvio: si riprova dopo un po'
    _restart()
    FakeHelper.fail = True
    assert embeddings.get_embeddings_helper() is None
    FakeHelper.fail = False
    assert embeddings.get_embeddings_helper() is None  # subito no: non si riprova a ogni giro
    monkeypatch.setattr(embeddings, "_helper_retry_at", 0.0)
    assert embeddings.get_embeddings_helper() is not None


def test_app_says_it_and_chat_goes_on(world, monkeypatch):
    from streamlit.testing.v1 import AppTest

    import core.llm_client as llm

    monkeypatch.setattr("rag.vector_store.KNOWLEDGE_BASE_DIR", world)
    _restart()
    FakeHelper.fail = True
    sent = []

    class Model:
        def stream_invoke(self, x):
            sent.append(str(x))
            yield type("C", (), {"text": "risposta senza KB"})()

    monkeypatch.setattr(llm, "_create_raw_client", lambda *a, **k: Model())
    at = AppTest.from_file("app.py", default_timeout=120)
    at.session_state["connection_type"] = "Local (Ollama)"
    at.session_state["models_local"] = ["modello-finto"]
    at.session_state["use_knowledge_base"] = True
    at.session_state["use_chat_kb"] = True
    at.run()
    assert not at.exception, at.exception
    assert any("non si carica" in w.value for w in at.warning), [w.value for w in at.warning]

    at.text_area(key="msg_input").set_value("Domanda qualsiasi")
    at.button(key="FormSubmitter:msg_form-🚀 Invia").click().run()
    assert not at.exception, at.exception
    assert sent and at.session_state["messages"][-1]["content"] == "risposta senza KB"
