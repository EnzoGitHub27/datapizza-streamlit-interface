# tests/test_restore_input.py
# DeepAiUG v1.16.0 (giro 6) — Il testo rimesso nella casella dopo un blocco
# ci resta: anche dopo un'azione nella sidebar, finché l'utente non invia di
# nuovo o non la svuota lui. rizzo-pii e cloud FINTI; conversazioni in tmp_path.
# ============================================================================

import pytest
from streamlit.testing.v1 import AppTest

from tests.test_pii_guard import FakeRizzo

DOMANDA = "Prepara la lettera per Mario Rossi, CF RSSMRA80A01H501U"


@pytest.fixture
def app(monkeypatch, tmp_path):
    import config.hybrid_settings as hs
    import core.llm_client as llm
    import core.pii_client as pc

    monkeypatch.setattr("core.persistence.CONVERSATIONS_DIR", tmp_path)
    monkeypatch.setattr("ui.sidebar.llm_config.load_api_key", lambda *a, **k: "", raising=False)
    rizzo = {"down": True}
    real = pc.PIIClient
    monkeypatch.setattr(pc, "PIIClient", lambda url, timeout=30: real(
        url, timeout, session=FakeRizzo(down=rizzo["down"])))
    sent = []

    class Cloud:
        def invoke(self, x):
            return type("R", (), {"text": "ok"})()

        def stream_invoke(self, x):
            sent.append(x)
            yield type("C", (), {"text": "Risposta finta"})()

    monkeypatch.setattr(llm, "_create_raw_client", lambda *a, **k: Cloud())

    def start(hybrid_raw=None, hybrid_error=None):
        if hybrid_error:
            def broken(*a, **k):
                raise hs.HybridSettingsError(hybrid_error)
            monkeypatch.setattr(hs, "load_hybrid_settings", broken)
        else:
            monkeypatch.setattr(hs, "load_hybrid_settings",
                                lambda *a, **k: hs.parse_hybrid_settings(hybrid_raw or {}))
        at = AppTest.from_file("app.py", default_timeout=120)
        at.session_state["connection_type"] = "Cloud provider"
        at.run()
        keys = [t for t in at.sidebar.text_input if "API Key" in t.label]
        if keys:
            keys[0].set_value("sk-finta-per-test").run()
        assert not at.exception, at.exception
        return at

    return start, rizzo, sent


def _send(at, text=None):
    if text is not None:
        at.text_area(key="msg_input").set_value(text)
    at.button(key="FormSubmitter:msg_form-🚀 Invia").click().run()
    assert not at.exception, at.exception
    return at


def _sidebar_action(at):
    # un'azione qualunque nella sidebar: la temperatura
    slider = [s for s in at.sidebar.slider if "emperat" in s.label][0]
    slider.set_value(0.5).run()
    assert not at.exception, at.exception
    return at


def _box(at):
    return at.text_area(key="msg_input").value


def test_text_survives_sidebar_action_and_reruns(app):
    start, rizzo, sent = app
    at = _send(start({"pii": {"enabled": True}}), DOMANDA)
    assert _box(at) == DOMANDA
    _sidebar_action(at)
    assert _box(at) == DOMANDA  # prima del giro 6 qui la casella era vuota
    at.run()
    assert _box(at) == DOMANDA
    assert sent == []


def test_resend_after_service_back_clears_box(app):
    start, rizzo, sent = app
    at = _send(start({"pii": {"enabled": True}}), DOMANDA)
    _sidebar_action(at)
    rizzo["down"] = False
    _send(at)  # «Invia» con il testo rimasto nella casella: non parte a vuoto
    assert sent and "Mario Rossi" not in str(sent)
    assert [m["role"] for m in at.session_state["messages"]] == ["user", "assistant"]
    assert _box(at) == ""  # inviato: la casella si svuota


def test_user_can_clear_the_box(app):
    start, _, _ = app
    at = _send(start({"pii": {"enabled": True}}), DOMANDA)
    at.text_area(key="msg_input").set_value("").run()
    _sidebar_action(at)
    assert _box(at) == ""


def test_broken_hybrid_config_keeps_text(app):
    start, _, sent = app
    at = _send(start(hybrid_error="yaml rotto"), DOMANDA)
    assert sent == []
    assert any("Configurazione ibrida non valida" in e.value for e in at.error)
    _sidebar_action(at)
    assert _box(at) == DOMANDA


# --- giro 6, difetto 2: la stima dei token --------------------------------------------

def test_blocked_question_not_in_token_estimate(app):
    start, rizzo, _ = app
    at = start({"pii": {"enabled": True}})
    before = at.session_state["total_tokens_estimate"]
    _send(at, DOMANDA)
    assert at.session_state["messages"] == []
    assert at.session_state["total_tokens_estimate"] == before  # la domanda bloccata non conta
    rizzo["down"] = False
    _send(at)
    from core.conversation import estimate_tokens

    assert at.session_state["total_tokens_estimate"] == before + sum(
        estimate_tokens(m["content"]) for m in at.session_state["messages"])
