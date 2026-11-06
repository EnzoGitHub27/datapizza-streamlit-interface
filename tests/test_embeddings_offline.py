# tests/test_embeddings_offline.py
# DeepAiUG v1.16.0 (giro 6) — Il modello degli embedding già sul disco si
# carica senza rete; si va su huggingface.co solo se manca.
# ============================================================================
# Caricamento simulato: nessun modello vero, nessuna rete.
# ============================================================================

import pytest

from rag import embeddings
from rag.embeddings import load_sentence_transformer, model_in_cache

NAME = "intfloat/multilingual-e5-small"


class FakeST:
    calls = []

    def __init__(self, name, device=None, local_files_only=False):
        FakeST.calls.append({"name": name, "device": device, "local_files_only": local_files_only})
        if local_files_only and FakeST.fail_offline:
            raise OSError("file mancante nella cache")

    fail_offline = False


@pytest.fixture(autouse=True)
def reset():
    FakeST.calls = []
    FakeST.fail_offline = False


def _cache(monkeypatch, present):
    import huggingface_hub

    monkeypatch.setattr(huggingface_hub, "try_to_load_from_cache",
                        lambda repo, f, **k: f"/cache/{repo}/{f}" if present else None)


def test_cached_model_loads_without_network(monkeypatch, capsys):
    _cache(monkeypatch, True)
    model, source = load_sentence_transformer(NAME, "cpu", factory=FakeST)
    assert source == "cache"
    assert FakeST.calls == [{"name": NAME, "device": "cpu", "local_files_only": True}]
    assert "huggingface.co" not in capsys.readouterr().out  # nessuna riga: nessuna rete


def test_missing_model_downloads_once_with_a_line(monkeypatch, capsys):
    _cache(monkeypatch, False)
    model, source = load_sentence_transformer(NAME, "cpu", factory=FakeST)
    assert source == "rete"
    assert FakeST.calls == [{"name": NAME, "device": "cpu", "local_files_only": False}]
    out = capsys.readouterr().out
    assert "primo uso" in out and "huggingface.co" in out


def test_incomplete_cache_falls_back_to_network(monkeypatch, capsys):
    _cache(monkeypatch, True)
    FakeST.fail_offline = True
    model, source = load_sentence_transformer(NAME, "cpu", factory=FakeST)
    assert source == "rete"
    assert [c["local_files_only"] for c in FakeST.calls] == [True, False]
    assert "cache incompleta" in capsys.readouterr().out


def test_local_folder_counts_as_cached(tmp_path):
    assert model_in_cache(str(tmp_path))


def test_cache_check_error_means_not_cached(monkeypatch):
    import huggingface_hub

    def boom(*a, **k):
        raise RuntimeError("x")

    monkeypatch.setattr(huggingface_hub, "try_to_load_from_cache", boom)
    assert model_in_cache(NAME) is False


def test_helper_uses_the_loader(monkeypatch):
    import sentence_transformers

    _cache(monkeypatch, True)
    monkeypatch.setattr(sentence_transformers, "SentenceTransformer", FakeST)
    monkeypatch.setattr(embeddings, "select_device", lambda: ("cpu", "test"))
    helper = embeddings._EmbeddingsHelper(NAME)
    assert helper.source == "cache" and FakeST.calls[0]["local_files_only"] is True
