# tests/test_annona_gateway.py
# DeepAiUG v1.16.0 (giro 5, P8) — Il gateway sperimentale di Annona.
# ============================================================================
# Annona FINTA (sessione HTTP finta), nessun demone vero, dati inventati.
# I test dell'app scrivono le conversazioni in tmp_path.
# ============================================================================

import json

import pytest
from streamlit.testing.v1 import AppTest

from core.annona_bridge import AnnonaGatewayBlocked, gateway_ask
from core.annona_client import AnnonaClient
from tests.fakes_http import FakeResponse, FakeSession, connection_refused

ASK_OK = {
    "response": "Ecco l'offerta per Ferrolago Srl.",
    "placement": {"class": "internal", "outcome": "redacted", "substrate": "cloud-finto",
                  "rule_id": "r-internal", "reason": "dati personali tolti"},
    "enforced": True,
    "decisions": [{"seq": 7, "kind": "egress", "outcome": "redacted"}],
    "egress": [{"kind": "redacted", "text": "Scrivi un'offerta per [ORG_1]"}],
    "cancelled": False,
}
ASK_HELD = dict(ASK_OK, response="", egress=[], placement={
    "class": "restricted", "outcome": "held", "substrate": "",
    "reason": "nessun substrato permesso per restricted"})


def _client(ask):
    return AnnonaClient(session=FakeSession({("post", "/api/kernel/ask"): ask}))


# --- gateway_ask ---------------------------------------------------------------------

def test_gateway_ok():
    session = FakeSession({("post", "/api/kernel/ask"): FakeResponse(200, ASK_OK)})
    r = gateway_ask(AnnonaClient(session=session), "Scrivi un'offerta per Ferrolago Srl")
    assert r.text == ASK_OK["response"]
    assert r.summary == {"class": "internal", "outcome": "redacted",
                         "substrate": "cloud-finto", "rule_id": "r-internal"}
    assert r.egress_text == "Scrivi un'offerta per [ORG_1]"
    assert "egress_text" not in repr(r)
    body = session.calls[0]["json"]
    assert body["max_iterations"] == 1 and body["escalate"] is False


def test_gateway_held_blocks_with_reason():
    with pytest.raises(AnnonaGatewayBlocked, match="nessun substrato permesso per restricted"):
        gateway_ask(_client(FakeResponse(200, ASK_HELD)), "x")


@pytest.mark.parametrize("ask", [connection_refused(), FakeResponse(503, {}), FakeResponse(404, {})])
def test_gateway_down_blocks(ask):
    with pytest.raises(AnnonaGatewayBlocked, match="non risponde"):
        gateway_ask(_client(ask), "x")


def test_gateway_error_blocks():
    with pytest.raises(AnnonaGatewayBlocked, match="errore"):
        gateway_ask(_client(FakeResponse(500, {})), "x")


def test_gateway_cancelled_blocks():
    with pytest.raises(AnnonaGatewayBlocked, match="annullato"):
        gateway_ask(_client(FakeResponse(200, dict(ASK_OK, cancelled=True))), "x")


# --- l'app intera ----------------------------------------------------------------------

DOMANDA = "Scrivi un'offerta per Ferrolago Srl"


@pytest.fixture
def gateway_app(monkeypatch, tmp_path):
    import config.hybrid_settings as hs
    import core.annona_bridge as bridge
    import core.llm_client as llm

    monkeypatch.setattr("core.persistence.CONVERSATIONS_DIR", tmp_path)
    monkeypatch.setattr("ui.sidebar.llm_config.load_api_key", lambda *a, **k: "", raising=False)
    monkeypatch.setattr(hs, "load_hybrid_settings", lambda *a, **k: hs.parse_hybrid_settings(
        {"annona": {"enabled": True, "mode": "gateway"}}))
    state = {"ask": FakeResponse(200, ASK_OK), "raw_calls": 0}

    def make_client(settings, timeout=3.0):
        routes = {
            ("post", "/api/kernel/ask"): state["ask"],
            ("get", "/health"): FakeResponse(200, {"status": "ok"}),
            ("get", "/api/kernel/status"): FakeResponse(200, {"enforcing": True}),
            ("get", "/api/kernel/ledger"): FakeResponse(200, {"entries": []}),
            ("get", "/api/kernel/ledger/verify"): FakeResponse(200, {"ok": True, "empty": True}),
        }
        return AnnonaClient(session=FakeSession(routes))

    monkeypatch.setattr(bridge, "make_client", make_client)

    class Cloud:
        def invoke(self, x):
            state["raw_calls"] += 1
            return type("R", (), {"text": "no"})()

        def stream_invoke(self, x):
            state["raw_calls"] += 1
            yield type("C", (), {"text": "non deve arrivare"})()

    monkeypatch.setattr(llm, "_create_raw_client", lambda *a, **k: Cloud())

    def run(connection="Cloud provider"):
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

    return run, state, tmp_path


def test_gateway_answers_via_annona(gateway_app):
    run, state, conv_dir = gateway_app
    at = run()
    assert state["raw_calls"] == 0  # il client dell'Interface non è stato usato
    [a] = [m for m in at.session_state["messages"] if m["role"] == "assistant"]
    assert a["content"] == ASK_OK["response"]
    assert a["model"] == "annona:cloud-finto" and a["annona_gateway"] is True
    assert any("SPERIMENTALE" in w.value for w in at.warning)  # etichetta visibile
    assert any("via Annona (sperimentale)" in c.value for c in at.caption)
    [f] = list(conv_dir.glob("conv_*.json"))
    assert "[ORG_1]" not in f.read_text(encoding="utf-8")  # egress non salvato


def test_app_gateway_held_blocks(gateway_app):
    run, state, _ = gateway_app
    state["ask"] = FakeResponse(200, ASK_HELD)
    at = run()
    [q] = [m for m in at.session_state["messages"] if m["role"] == "user"]
    assert q["send_status"] == "non_inviata" and "held" in q["send_error"]
    assert not [m for m in at.session_state["messages"] if m["role"] == "assistant"]
    assert state["raw_calls"] == 0


def test_app_gateway_down_blocks(gateway_app):
    run, state, _ = gateway_app
    state["ask"] = connection_refused()
    at = run()
    [q] = [m for m in at.session_state["messages"] if m["role"] == "user"]
    assert q["send_status"] == "non_inviata" and "non risponde" in q["send_error"]
    assert state["raw_calls"] == 0


def test_gateway_not_used_in_house(gateway_app):
    run, state, _ = gateway_app
    at = run(connection="Local (Ollama)")
    assert state["raw_calls"] == 1  # Ollama locale: il client di sempre
    assert not any("SPERIMENTALE" in w.value for w in at.warning)


# --- giro 7b: il gateway che non resta muto ----------------------------------------------

TOOL_HELD = {"seq": 9, "kind": "tool_call", "outcome": "held", "class": "internal",
             "substrate": "local", "detail": {"tool": "explorer", "reason": "nessuna regola",
                                              "paths": ["/home/finto/segreto.txt"]}}
ASK_EMPTY_TOOL = dict(ASK_OK, response="", egress=[], decisions=[TOOL_HELD])
ASK_EMPTY = dict(ASK_OK, response="  ", egress=[], decisions=[])


def test_gateway_empty_with_held_tool_says_so():
    from core.annona_bridge import AnnonaGatewayEmpty

    with pytest.raises(AnnonaGatewayEmpty) as exc:
        gateway_ask(_client(FakeResponse(200, ASK_EMPTY_TOOL)), "x")
    msg = str(exc.value)
    assert "non ha prodotto testo" in msg and "«explorer»" in msg and "fermato" in msg
    assert "segreto" not in msg and "/home" not in msg  # mai percorsi o argomenti


def test_gateway_empty_without_tool():
    from core.annona_bridge import AnnonaGatewayEmpty

    with pytest.raises(AnnonaGatewayEmpty) as exc:
        gateway_ask(_client(FakeResponse(200, ASK_EMPTY)), "x")
    assert "non ha prodotto testo" in str(exc.value) and "strumento" not in str(exc.value)


def test_gateway_full_answer_unchanged_even_with_held_tool():
    r = gateway_ask(_client(FakeResponse(200, dict(ASK_OK, decisions=[TOOL_HELD]))), "x")
    assert r.text == ASK_OK["response"]


def test_held_tools_ignores_cleared_and_bad_names():
    from core.annona_bridge import held_tools

    decisions = [TOOL_HELD, dict(TOOL_HELD, outcome="cleared", detail={"tool": "reader"}),
                 dict(TOOL_HELD, detail={"tool": "rm -rf /"}), {"kind": "egress", "outcome": "held"},
                 TOOL_HELD]
    assert held_tools(decisions) == ["explorer"]


def test_app_gateway_empty_answer_not_silent(gateway_app):
    run, state, conv_dir = gateway_app
    state["ask"] = FakeResponse(200, ASK_EMPTY_TOOL)
    at = run()
    msgs = at.session_state["messages"]
    assert [m["role"] for m in msgs] == ["user"]  # nessuna bolla vuota
    assert msgs[0]["send_status"] == "senza_risposta" and "explorer" in msgs[0]["send_error"]
    assert any("Senza risposta" in w.value and "explorer" in w.value for w in at.warning)
    assert state["raw_calls"] == 0
    assert "segreto" not in next(conv_dir.glob("conv_*.json")).read_text(encoding="utf-8")
