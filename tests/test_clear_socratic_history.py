# tests/test_clear_socratic_history.py
# DeepAiUG v1.16.1 — voce 22 del giro 8: «🗑️ Cancella storico» funziona.
# ============================================================================
# Fino alla 1.16.0 il bottone scriveva in session_state la chiave della
# casella «Conferma cancellazione» dopo che il widget era già stato creato:
# StreamlitAPIException. E la cancellazione non chiedeva il salvataggio
# (_socratic_save_needed): sul disco lo storico restava. Dati inventati,
# conversazioni in tmp_path.
# ============================================================================

import json
from datetime import datetime

import pytest
from streamlit.testing.v1 import AppTest

from ui.socratic.history import SocraticExploration

CONV_ID = "20261108_090000"


def _exploration():
    return SocraticExploration(
        timestamp=datetime(2026, 11, 8, 9, 5), button_type="alternatives",
        original_question="Come organizzo la settimana?", ai_response_snippet="Così.",
        socratic_result="Prova anche al contrario.", session_id=CONV_ID, msg_index=1,
    )


@pytest.fixture
def app(monkeypatch, tmp_path):
    monkeypatch.setattr("core.persistence.CONVERSATIONS_DIR", tmp_path)
    at = AppTest.from_file("app.py", default_timeout=120)
    at.session_state["connection_type"] = "Local (Ollama)"
    at.session_state["models_local"] = ["modello-finto"]
    at.session_state["socratic_mode"] = "standard"
    at.session_state["conversation_id"] = CONV_ID
    at.session_state["messages"] = [
        {"role": "user", "content": "Come organizzo la settimana?", "timestamp": "2026-11-08T09:00:00"},
        {"role": "assistant", "content": "Così.", "timestamp": "2026-11-08T09:00:05",
         "model": "modello-finto", "provider": "Local (Ollama)"},
    ]
    at.session_state["socratic_history"] = [_exploration(), _exploration()]
    at.run()
    assert not at.exception, at.exception
    return at, tmp_path


def _clear(at):
    next(c for c in at.sidebar.checkbox if c.label == "Conferma cancellazione").check().run()
    assert not at.exception, at.exception
    next(b for b in at.sidebar.button if b.label == "🗑️ Cancella storico").click().run()
    return at


def test_clear_history_no_exception(app):
    at, _ = app
    at = _clear(at)
    assert not at.exception, at.exception
    assert at.session_state["socratic_history"] == []


def test_clear_history_is_saved(app):
    at, tmp_path = app
    at = _clear(at)
    assert not at.exception, at.exception
    saved = json.loads((tmp_path / f"conv_{CONV_ID}.json").read_text(encoding="utf-8"))
    assert saved["socratic_history"] == []
    assert len(saved["messages"]) == 2


def test_confirm_box_unchecked_after_clear(app):
    at, _ = app
    at = _clear(at)
    at.session_state["socratic_history"] = [_exploration()]
    at.run()
    assert not at.exception, at.exception
    box = next(c for c in at.sidebar.checkbox if c.label == "Conferma cancellazione")
    assert box.value is False
