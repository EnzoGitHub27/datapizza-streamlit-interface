# tests/test_cloud_error_visible.py
# DeepAiUG v1.16.0 (giro 4, decisione 11) — Un invio rifiutato o fallito lascia
# in chat l'errore accanto alla domanda, segnata «non inviata» o «rifiutata»,
# anche dopo il rerun e ricaricando la conversazione.
# ============================================================================
# Cloud FINTO, chiave finta, dati inventati. Nessuna rete.
# ============================================================================

import json

import pytest
from streamlit.testing.v1 import AppTest

from core.conversation import (
    SEND_NOT_SENT,
    SEND_REJECTED,
    classify_send_error,
    get_conversation_history,
    mark_send_failed,
    redact_secrets,
)

DOMANDA = "Scrivi un'offerta per Ferrolago Srl"


class AuthenticationError(Exception):
    """Come l'eccezione 401 dell'SDK OpenAI."""


class APIConnectionError(Exception):
    """Come l'eccezione di rete dell'SDK OpenAI."""


# --- funzioni pure ----------------------------------------------------------------

def test_classify_before_stream_is_not_sent():
    assert classify_send_error(AuthenticationError("401"), stream_started=False) == SEND_NOT_SENT


def test_classify_provider_error_is_rejected():
    assert classify_send_error(AuthenticationError("401"), stream_started=True) == SEND_REJECTED


def test_classify_connection_error_is_not_sent():
    assert classify_send_error(APIConnectionError("rete"), stream_started=True) == SEND_NOT_SENT


def test_mark_redacts_keys():
    msg = {"role": "user", "content": DOMANDA}
    mark_send_failed(msg, SEND_REJECTED, AuthenticationError("Incorrect API key provided: sk-finta1234567890"))
    assert msg["send_status"] == SEND_REJECTED
    assert "sk-finta" not in msg["send_error"] and "AuthenticationError" in msg["send_error"]


def test_redact_variants():
    assert "abcd1234" not in redact_secrets('{"api_key": "abcd1234"}')
    assert "AIzaFinta" not in redact_secrets("key AIzaFinta1234567890 rifiutata")


def test_history_skips_failed_questions():
    msgs = [
        {"role": "user", "content": "prima", "send_status": SEND_REJECTED},
        {"role": "user", "content": "seconda"},
    ]
    assert get_conversation_history(msgs) == [{"role": "user", "content": "seconda"}]


# --- rendering della bolla ---------------------------------------------------------

def _render(message):
    def script(message):
        from ui.chat import render_chat_message

        render_chat_message(message, 0, None, messages_list=[message], socratic_mode="fast")

    at = AppTest.from_function(script, args=(message,))
    at.run()
    assert not at.exception, at.exception
    return at


def test_bubble_shows_rejected():
    at = _render({"role": "user", "content": DOMANDA, "send_status": SEND_REJECTED,
                  "send_error": "AuthenticationError: 401"})
    assert any("Rifiutata" in e.value and "401" in e.value for e in at.error)


def test_bubble_shows_not_sent():
    at = _render({"role": "user", "content": DOMANDA, "send_status": SEND_NOT_SENT,
                  "send_error": "APIConnectionError: rete"})
    assert any("Non inviata" in w.value for w in at.warning)


def test_bubble_without_status_unchanged():
    at = _render({"role": "user", "content": DOMANDA})
    assert not at.error and not at.warning


# --- l'app intera ----------------------------------------------------------------------

@pytest.fixture
def fake_cloud(monkeypatch, tmp_path):
    """Cloud finto che fallisce come gli diciamo. Conversazioni in tmp_path."""
    import core.llm_client as llm

    monkeypatch.setattr("core.persistence.CONVERSATIONS_DIR", tmp_path)
    monkeypatch.setattr("ui.sidebar.llm_config.load_api_key", lambda *a, **k: "", raising=False)
    state = {"fail": None, "where": "stream", "calls": 0}

    class Cloud:
        def invoke(self, x):
            return type("R", (), {"text": "ok"})()

        def stream_invoke(self, x):
            state["calls"] += 1
            raise state["fail"]
            yield  # pragma: no cover

    def make(*a, **k):
        if state["where"] == "create":
            raise state["fail"]
        return Cloud()

    monkeypatch.setattr(llm, "_create_raw_client", make)
    return state, tmp_path


def _send(at):
    keys = [t for t in at.sidebar.text_input if "API Key" in t.label]
    keys[0].set_value("sk-finta-per-test").run()
    at.text_area[0].set_value(DOMANDA)
    at.button(key="FormSubmitter:msg_form-🚀 Invia").click().run()
    assert not at.exception, at.exception


def _app():
    at = AppTest.from_file("app.py", default_timeout=120)
    at.session_state["connection_type"] = "Cloud provider"
    at.run()
    return at


def test_rejected_send_stays_visible_and_saved(fake_cloud):
    state, conv_dir = fake_cloud
    state["fail"] = AuthenticationError("Error code: 401 - Incorrect API key provided: sk-fint*****test")
    at = _app()
    _send(at)

    [q] = [m for m in at.session_state["messages"] if m["role"] == "user"]
    assert q["content"] == DOMANDA and q["send_status"] == SEND_REJECTED
    assert any("Rifiutata" in e.value for e in at.error)  # visibile dopo il rerun

    at.run()  # un'altra interazione: l'errore resta
    assert any("Rifiutata" in e.value for e in at.error)

    [f] = list(conv_dir.glob("conv_*.json"))  # e resta nel file salvato
    saved = json.loads(f.read_text(encoding="utf-8"))["messages"][0]
    assert saved["send_status"] == SEND_REJECTED and "sk-fint" not in saved["send_error"]


def test_create_failure_is_not_sent(fake_cloud):
    state, _ = fake_cloud
    state["where"], state["fail"] = "create", ValueError("client non creato")
    at = _app()
    _send(at)
    [q] = [m for m in at.session_state["messages"] if m["role"] == "user"]
    assert q["send_status"] == SEND_NOT_SENT and state["calls"] == 0
    assert any("Non inviata" in w.value for w in at.warning)
