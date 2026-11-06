# tests/test_pii_badge.py
# DeepAiUG v1.16.0 (giro 5, P9) — Il badge «🛡️ N dati tolti prima dell'invio»
# e il riquadro «cosa ha visto il modello», solo nella sessione corrente.
# ============================================================================
# rizzo-pii, cloud e Annona FINTI; conversazioni in tmp_path; dati inventati.
# ============================================================================

import json

import pytest
from streamlit.testing.v1 import AppTest

from tests.test_pii_guard import FakeRizzo

DOMANDA = "Prepara la lettera per Mario Rossi, CF RSSMRA80A01H501U"
SEGNAPOSTO = "[FULLNAME_1]"


@pytest.fixture
def app_run(monkeypatch, tmp_path):
    import config.hybrid_settings as hs
    import core.llm_client as llm
    import core.pii_client as pc

    monkeypatch.setattr("core.persistence.CONVERSATIONS_DIR", tmp_path)
    monkeypatch.setattr("ui.sidebar.llm_config.load_api_key", lambda *a, **k: "", raising=False)
    real = pc.PIIClient
    monkeypatch.setattr(pc, "PIIClient", lambda url, timeout=30: real(url, timeout, session=FakeRizzo()))
    sent = []

    class Cloud:
        def invoke(self, x):
            return type("R", (), {"text": "ok"})()

        def stream_invoke(self, x):
            sent.append(x)
            yield type("C", (), {"text": f"Gentile {SEGNAPOSTO}, ecco la lettera."})()

    monkeypatch.setattr(llm, "_create_raw_client", lambda *a, **k: Cloud())

    def run(hybrid_raw, connection="Cloud provider"):
        monkeypatch.setattr(hs, "load_hybrid_settings", lambda *a, **k: hs.parse_hybrid_settings(hybrid_raw))
        at = AppTest.from_file("app.py", default_timeout=120)
        at.session_state["connection_type"] = connection
        at.run()
        keys = [t for t in at.sidebar.text_input if "API Key" in t.label]
        if keys:
            keys[0].set_value("sk-finta-per-test").run()
        at.text_area[0].set_value(DOMANDA)
        at.button(key="FormSubmitter:msg_form-🚀 Invia").click().run()
        assert not at.exception, at.exception
        return at

    return run, sent, tmp_path


def _badges(at):
    return [c.value for c in at.caption if "prima dell'invio" in c.value]


def _egress_boxes(at):
    return [e for e in at.expander if "Cosa ha visto il modello" in e.label]


def test_badge_and_box_with_guard(app_run):
    run, sent, conv_dir = app_run
    at = run({"pii": {"enabled": True}})

    assert "Mario Rossi" not in str(sent) and SEGNAPOSTO in str(sent)
    [a] = [m for m in at.session_state["messages"] if m["role"] == "assistant"]
    assert a["content"] == "Gentile Mario Rossi, ecco la lettera."  # ripristinato in locale
    assert a["pii_removed"] == 2
    assert _badges(at) == ["🛡️ 2 dati tolti prima dell'invio"]

    [box] = _egress_boxes(at)
    shown = " ".join(t.value for t in box.text)
    assert SEGNAPOSTO in shown and "[CF_1]" in shown
    assert "Mario Rossi" not in shown and "RSSMRA80A01H501U" not in shown

    # il file salvato: il conteggio sì; testo inviato, segnaposto e tabella no
    [f] = list(conv_dir.glob("conv_*.json"))
    raw = f.read_text(encoding="utf-8")
    data = json.loads(raw)
    assert data["pii_guard"] is True and data["pii_removed"] == 2
    assert data["messages"][1]["pii_removed"] == 2
    assert SEGNAPOSTO not in raw and "[CF_1]" not in raw
    assert "egress" not in raw and "mapping" not in raw


def test_badge_survives_rerun_box_is_session_only(app_run):
    run, _, _ = app_run
    at = run({"pii": {"enabled": True}})
    at.run()
    assert _badges(at) and _egress_boxes(at)  # stessa sessione: tutti e due

    # nuova sessione con la stessa conversazione (come ricaricarla): solo il badge
    msgs = at.session_state["messages"]

    def script(msgs):
        from ui.chat import render_chat_message

        for i, m in enumerate(msgs):
            render_chat_message(m, i, None, messages_list=msgs, socratic_mode="fast")

    fresh = AppTest.from_function(script, args=(msgs,))
    fresh.run()
    assert _badges(fresh) == ["🛡️ 2 dati tolti prima dell'invio"]
    assert _egress_boxes(fresh) == []


def test_no_badge_with_hybrid_off(app_run):
    run, sent, conv_dir = app_run
    at = run({})
    [a] = [m for m in at.session_state["messages"] if m["role"] == "assistant"]
    assert "pii_removed" not in a
    assert _badges(at) == [] and _egress_boxes(at) == []
    data = json.loads(next(conv_dir.glob("conv_*.json")).read_text(encoding="utf-8"))
    assert "pii_guard" not in data


def test_no_badge_in_house_even_with_guard_on(app_run):
    run, _, _ = app_run
    at = run({"pii": {"enabled": True}}, connection="Local (Ollama)")
    assert _badges(at) == [] and _egress_boxes(at) == []


def test_gateway_box_shows_annona_egress(monkeypatch, app_run):
    import core.annona_bridge as bridge
    from core.annona_client import AnnonaClient
    from tests.fakes_http import FakeResponse, FakeSession
    from tests.test_annona_gateway import ASK_OK

    run, _, conv_dir = app_run
    monkeypatch.setattr(bridge, "make_client", lambda settings, timeout=3.0: AnnonaClient(
        session=FakeSession({("post", "/api/kernel/ask"): FakeResponse(200, ASK_OK),
                             ("get", "/health"): FakeResponse(200, {"status": "ok"}),
                             ("get", "/api/kernel/status"): FakeResponse(200, {"enforcing": False})})))
    at = run({"annona": {"enabled": True, "mode": "gateway"}})
    [box] = _egress_boxes(at)
    assert "[ORG_1]" in " ".join(t.value for t in box.text)
    assert "[ORG_1]" not in next(conv_dir.glob("conv_*.json")).read_text(encoding="utf-8")
