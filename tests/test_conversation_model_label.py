# tests/test_conversation_model_label.py
# DeepAiUG v1.15.4 — La testata della conversazione dice chi ha risposto
# davvero, non che cosa c'è nella sidebar al momento del salvataggio.
# ============================================================================
# Conversazioni inventate, cartella conversazioni in tmp_path.
# ============================================================================

import io
import json
import zipfile
from unittest.mock import patch

import pytest

from core.conversation import conversation_models, create_message

LOCAL = "Local (Ollama)"
CLOUD = "Cloud provider"


def _user(text="domanda"):
    return {"role": "user", "content": text, "timestamp": "2026-11-06T10:00:00"}


def _assistant(model, provider=None, text="risposta"):
    m = {"role": "assistant", "content": text, "timestamp": "2026-11-06T10:00:05", "model": model}
    if provider:
        m["provider"] = provider
    return m


@pytest.fixture
def conv_dir(tmp_path):
    d = tmp_path / "conversations"
    d.mkdir()
    with patch("core.persistence.CONVERSATIONS_DIR", d):
        yield d


# --- create_message --------------------------------------------------------

def test_create_message_records_provider_for_assistant():
    m = create_message("assistant", "ciao", model="llama3.2:3b", provider=LOCAL)
    assert m["model"] == "llama3.2:3b" and m["provider"] == LOCAL


def test_create_message_user_has_no_model_or_provider():
    m = create_message("user", "ciao", model="llama3.2:3b", provider=LOCAL)
    assert "model" not in m and "provider" not in m


# --- conversation_models ---------------------------------------------------

def test_one_model_beats_sidebar():
    msgs = [_user(), _assistant("llama3.2:3b", LOCAL), _user("migliora il programma")]
    got = conversation_models(msgs, "gpt-4o-mini", CLOUD)  # sidebar cambiata dopo
    assert got == {"model": "llama3.2:3b", "provider": LOCAL, "models_used": ["llama3.2:3b"]}


def test_two_models_last_wins_and_list_in_order():
    msgs = [
        _user(), _assistant("llama3.2:3b", LOCAL),
        _user(), _assistant("gpt-4o-mini", CLOUD),
        _user(), _assistant("llama3.2:3b", LOCAL),
    ]
    got = conversation_models(msgs, "qwen2.5:7b", LOCAL)
    assert got["model"] == "llama3.2:3b" and got["provider"] == LOCAL
    assert got["models_used"] == ["llama3.2:3b", "gpt-4o-mini"]


def test_no_answers_keeps_sidebar():
    got = conversation_models([_user()], "gpt-4o-mini", CLOUD)
    assert got == {"model": "gpt-4o-mini", "provider": CLOUD, "models_used": []}


def test_old_message_without_provider_and_different_header():
    """Il caso di Gilles: risposta llama3.2:3b, testata gpt-4o-mini / Cloud."""
    got = conversation_models([_user(), _assistant("llama3.2:3b")], "gpt-4o-mini", CLOUD)
    assert got["model"] == "llama3.2:3b"
    assert got["provider"] == ""  # meglio vuoto che «Cloud provider»


def test_old_message_without_provider_same_model_uses_header():
    got = conversation_models([_user(), _assistant("llama3.2:3b")], "llama3.2:3b", LOCAL)
    assert got["provider"] == LOCAL


# --- salvataggio ------------------------------------------------------------

def _save(messages, model, provider):
    from core.persistence import save_conversation

    answered = conversation_models(messages, model, provider)
    assert save_conversation(
        conversation_id="20261106_100000", created_at="2026-11-06T10:00:00",
        messages=messages, model=answered["model"], provider=answered["provider"],
        tokens_estimate=0, models_used=answered["models_used"],
    )


def _read(conv_dir):
    return json.loads((conv_dir / "conv_20261106_100000.json").read_text(encoding="utf-8"))


def test_save_header_from_last_answer_without_models_used(conv_dir):
    _save([_user(), _assistant("llama3.2:3b", LOCAL)], "gpt-4o-mini", CLOUD)
    data = _read(conv_dir)
    assert data["model"] == "llama3.2:3b" and data["provider"] == LOCAL
    assert "models_used" not in data  # un modello solo: niente campo


def test_save_models_used_with_two_models(conv_dir):
    msgs = [_user(), _assistant("llama3.2:3b", LOCAL), _user(), _assistant("gpt-4o-mini", CLOUD)]
    _save(msgs, "gpt-4o-mini", CLOUD)
    data = _read(conv_dir)
    assert data["model"] == "gpt-4o-mini"
    assert data["models_used"] == ["llama3.2:3b", "gpt-4o-mini"]


def test_save_without_answers_keeps_sidebar(conv_dir):
    _save([_user()], "gpt-4o-mini", CLOUD)
    data = _read(conv_dir)
    assert data["model"] == "gpt-4o-mini" and data["provider"] == CLOUD


# --- chat vecchie: lista, pannello KB, export ------------------------------

def _write_old_file(conv_dir):
    """File come lo scriveva la 1.15.3: testata dalla sidebar, messaggi senza provider."""
    data = {
        "conversation_id": "20261106_090000",
        "created_at": "2026-11-06T09:00:00",
        "last_updated": "2026-11-06T09:10:00",
        "model": "gpt-4o-mini",
        "provider": CLOUD,
        "messages": [_user("scrivi una classe"), _assistant("llama3.2:3b"), _user("migliorala")],
        "stats": {"total_messages": 3, "tokens_estimate": 10},
    }
    path = conv_dir / "conv_20261106_090000.json"
    text = json.dumps(data, ensure_ascii=False)
    path.write_text(text, encoding="utf-8")
    return path, text


def test_list_uses_messages_and_does_not_rewrite_file(conv_dir):
    from core.persistence import list_saved_conversations

    path, before = _write_old_file(conv_dir)
    [conv] = list_saved_conversations()
    assert conv["model"] == "llama3.2:3b"
    assert conv["provider"] == ""
    assert conv["models_used"] == ["llama3.2:3b"]
    assert path.read_text(encoding="utf-8") == before  # nessuna riscrittura


def test_list_falls_back_to_header_without_answers(conv_dir):
    from core.persistence import list_saved_conversations

    (conv_dir / "conv_20261106_080000.json").write_text(json.dumps({
        "conversation_id": "20261106_080000", "last_updated": "2026-11-06T08:00:00",
        "model": "qwen2.5:7b", "provider": LOCAL, "messages": [_user()],
    }), encoding="utf-8")
    [conv] = list_saved_conversations()
    assert conv["model"] == "qwen2.5:7b" and conv["provider"] == LOCAL


def test_batch_export_uses_messages(conv_dir):
    from core.persistence import list_saved_conversations
    from export.exporters import create_batch_export_zip

    _write_old_file(conv_dir)
    data = create_batch_export_zip(list_saved_conversations(), "JSON")
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        exported = json.loads(z.read(z.namelist()[0]))
    assert exported["conversation"]["model"] == "llama3.2:3b"
    assert exported["conversation"]["provider"] == ""
