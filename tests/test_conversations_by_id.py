# tests/test_conversations_by_id.py
# DeepAiUG v1.16.1 — voce 23 del giro 8: Carica ed Elimina per identificativo.
# ============================================================================
# La selezione «Carica» della sidebar usava l'etichetta (data, modello, numero
# di messaggi) come valore: con due conversazioni con la stessa etichetta si
# caricava o si ELIMINAVA sempre la prima. Ora il valore è l'identificativo,
# l'etichetta serve solo da mostrare. Conversazioni inventate in tmp_path.
# ============================================================================

import json

import pytest
from streamlit.testing.v1 import AppTest

from tests.test_kb_chat_indexer import _make_chat


def _save(conv_dir, chat_id, text):
    chat = _make_chat(chat_id, includi_in_kb=False)
    chat["messages"][0]["content"] = text
    chat["last_updated"] = "2026-11-08T10:00:00"  # stessa data, modello e messaggi
    (conv_dir / f"conv_{chat_id}.json").write_text(json.dumps(chat, ensure_ascii=False), encoding="utf-8")


@pytest.fixture
def twins(monkeypatch, tmp_path):
    conv_dir = tmp_path / "conversations"
    conv_dir.mkdir()
    monkeypatch.setattr("core.persistence.CONVERSATIONS_DIR", conv_dir)
    monkeypatch.setattr("core.kb_chat_indexer.CHAT_KB_PERSIST_PATH", str(tmp_path / "chat_kb_vs"))
    monkeypatch.setattr("core.kb_chat_indexer.CHAT_KB_META_FILE", tmp_path / "chat_kb_meta.json")
    _save(conv_dir, "20261108_100000", "la prima")
    _save(conv_dir, "20261108_100001", "la seconda")
    at = AppTest.from_file("app.py", default_timeout=120)
    at.session_state["connection_type"] = "Local (Ollama)"
    at.session_state["models_local"] = ["modello-finto"]
    at.session_state["auto_save_enabled"] = False
    at.run()
    assert not at.exception, at.exception
    return at, conv_dir


def _carica(at):
    return next(s for s in at.sidebar.selectbox if s.label == "Carica")


def _labels(sb):
    return [sb.format_func(o) for o in sb.options]


def _pick_second(at):
    sb = _carica(at)
    labels = _labels(sb)
    real = [l for l in labels if l != "-- Seleziona --"]
    assert len(real) == 2 and real[0] == real[1], "le due etichette dovevano essere uguali"
    # la seconda voce della lista (indice 2: dopo «-- Seleziona --»)
    sb.set_value(sb.options[2]).run()
    assert not at.exception, at.exception
    return at


def _second_id(at):
    from core import list_saved_conversations

    return [c["id"] for c in list_saved_conversations()][1]


def test_delete_removes_the_chosen_one(twins):
    at, conv_dir = twins
    target = _second_id(at)
    other = ({"20261108_100000", "20261108_100001"} - {target}).pop()
    _pick_second(at)
    next(b for b in at.sidebar.button if b.label == "🗑️ Elimina").click().run()
    assert not at.exception, at.exception
    at.button(key="confirm_delete").click().run()
    assert not at.exception, at.exception
    assert not (conv_dir / f"conv_{target}.json").exists(), "doveva sparire quella scelta"
    assert (conv_dir / f"conv_{other}.json").exists(), "l'altra doveva restare"


def test_load_loads_the_chosen_one(twins):
    at, _ = twins
    target = _second_id(at)
    _pick_second(at)
    next(b for b in at.sidebar.button if b.label == "📂 Carica").click().run()
    assert not at.exception, at.exception
    assert at.session_state["conversation_id"] == target
