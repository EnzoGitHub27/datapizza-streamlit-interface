# tests/test_annona_panel.py
# DeepAiUG v1.16.0 (giro 5, P7) — Le letture di Annona nella sidebar.
# ============================================================================
# Annona FINTA (sessione HTTP finta), nessun demone vero, dati inventati.
# I test dell'app scrivono le conversazioni in tmp_path.
# ============================================================================

import pytest
from streamlit.testing.v1 import AppTest

from core.annona_bridge import clean_ledger_entry, read_state
from core.annona_client import AnnonaClient
from tests.fakes_http import FakeResponse, FakeSession, connection_refused

SEGRETO = "Mario Rossi RSSMRA80A01H501U"  # non deve mai comparire

ENTRIES = [
    {"seq": 41, "kind": "egress", "class": "internal", "outcome": "redacted",
     "substrate": "cloud-finto", "rule_id": "r-internal", "reason": "dati personali tolti",
     "payload_digest": "ab" * 32, "detail": {"text": SEGRETO}, "prompt": SEGRETO},
    {"seq": 42, "kind": "egress", "class": "restricted", "outcome": "held",
     "substrate": "", "reason": "nessun substrato permesso"},
]


def routes(up=True, enforcing=True, verify_ok=True, ledger=ENTRIES):
    if not up:
        return {("get", "/health"): connection_refused()}
    r = {
        ("get", "/health"): FakeResponse(200, {"status": "ok", "service": "annona"}),
        ("get", "/api/kernel/status"): FakeResponse(200, (
            {"enforcing": True, "rules": 3, "substrates": 2, "decisions": 42, "held": 1}
            if enforcing else {"enforcing": False, "reason": "no policy file"})),
        ("get", "/api/kernel/ledger"): FakeResponse(200, {"entries": ledger}),
        ("get", "/api/kernel/ledger/verify"): FakeResponse(200, (
            {"ok": True, "entries": 42, "problem": "", "empty": False} if verify_ok
            else {"ok": False, "entries": 42, "problem": "hash mismatch at seq 17", "empty": False})),
    }
    return r


def _client(**kw):
    return AnnonaClient(session=FakeSession(routes(**kw)))


# --- read_state ------------------------------------------------------------------------

def test_state_up_with_chain_ok():
    s = read_state(_client())
    assert s.up and s.enforcing and s.verification.ok
    assert [e["seq"] for e in s.entries] == [41, 42]


def test_state_entries_never_carry_text():
    s = read_state(_client())
    for e in s.entries:
        assert set(e) <= {"seq", "ts", "kind", "class", "outcome", "substrate", "rule_id", "reason"}
        assert SEGRETO not in str(e)


def test_state_down_does_not_raise():
    s = read_state(_client(up=False))
    assert not s.up and "non risponde" in s.problem


def test_state_without_policy():
    s = read_state(_client(enforcing=False))
    assert s.up and not s.enforcing and "senza policy" in s.problem


def test_state_broken_chain():
    s = read_state(_client(verify_ok=False))
    assert not s.verification.ok and "hash mismatch" in s.verification.problem


def test_clean_entry_truncates_reason_and_maps_klass():
    e = clean_ledger_entry({"seq": 1, "klass": "public", "reason": "x" * 500, "text": SEGRETO})
    assert e["class"] == "public" and len(e["reason"]) == 160 and "text" not in e


# --- il pannello ---------------------------------------------------------------------

def _panel(monkeypatch, enabled=True, mode="read", **kw):
    from config.hybrid_settings import parse_hybrid_settings

    import core.annona_bridge as bridge

    monkeypatch.setattr(bridge, "make_client", lambda settings, timeout=3.0: _client(**kw))
    hybrid = parse_hybrid_settings({"annona": {"enabled": enabled, "mode": mode}})

    def script(hybrid):
        from ui.sidebar.annona_panel import render_annona_panel

        render_annona_panel(hybrid)

    at = AppTest.from_function(script, args=(hybrid,))
    at.run()
    assert not at.exception, at.exception
    return at


def _all_text(at):
    parts = [m.value for m in at.sidebar.markdown] + [c.value for c in at.sidebar.caption]
    parts += [x.value for x in at.sidebar.success] + [x.value for x in at.sidebar.warning]
    parts += [x.value for x in at.sidebar.error]
    return "\n".join(parts)


def test_panel_hidden_when_disabled(monkeypatch):
    at = _panel(monkeypatch, enabled=False)
    assert len(at.sidebar.expander) == 0


def test_panel_up(monkeypatch):
    text = _all_text(_panel(monkeypatch))
    assert "Annona attiva" in text and "Catena del registro integra" in text
    assert "#41" in text and "redacted" in text and "cloud-finto" in text
    assert "dati personali tolti" in text
    assert SEGRETO not in text


def test_panel_broken_chain(monkeypatch):
    at = _panel(monkeypatch, verify_ok=False)
    assert any("ROTTA" in e.value for e in at.sidebar.error)


def test_panel_down_says_so_and_app_goes_on(monkeypatch):
    text = _all_text(_panel(monkeypatch, up=False))
    assert "non risponde" in text and "L'app procede" in text


def test_panel_no_policy(monkeypatch):
    assert "senza policy" in _all_text(_panel(monkeypatch, enabled=True, enforcing=False))


# --- decisione 6: «non registrato in Annona» --------------------------------------------

@pytest.fixture
def app_cloud(monkeypatch, tmp_path):
    import config.hybrid_settings as hs
    import core.annona_bridge as bridge
    import core.llm_client as llm

    monkeypatch.setattr("core.persistence.CONVERSATIONS_DIR", tmp_path)
    monkeypatch.setattr("ui.sidebar.llm_config.load_api_key", lambda *a, **k: "", raising=False)
    monkeypatch.setattr(bridge, "make_client", lambda settings, timeout=3.0: _client(up=False))

    class Cloud:
        def invoke(self, x):
            return type("R", (), {"text": "ok"})()

        def stream_invoke(self, x):
            yield type("C", (), {"text": "Risposta finta"})()

    monkeypatch.setattr(llm, "_create_raw_client", lambda *a, **k: Cloud())

    def run(hybrid_raw, connection="Cloud provider"):
        monkeypatch.setattr(hs, "load_hybrid_settings", lambda *a, **k: hs.parse_hybrid_settings(hybrid_raw))
        at = AppTest.from_file("app.py", default_timeout=120)
        at.session_state["connection_type"] = connection
        at.run()
        keys = [t for t in at.sidebar.text_input if "API Key" in t.label]
        if keys:
            keys[0].set_value("sk-finta-per-test").run()
        at.text_area[0].set_value("Domanda di prova")
        at.button(key="FormSubmitter:msg_form-🚀 Invia").click().run()
        assert not at.exception, at.exception
        return at

    return run


def test_outside_send_marked_not_recorded(app_cloud):
    at = app_cloud({"annona": {"enabled": True, "mode": "read"}})
    [a] = [m for m in at.session_state["messages"] if m["role"] == "assistant"]
    assert a["annona_recorded"] is False
    assert any("non registrato in Annona" in c.value for c in at.caption)


def test_no_mark_without_annona(app_cloud):
    at = app_cloud({})
    [a] = [m for m in at.session_state["messages"] if m["role"] == "assistant"]
    assert "annona_recorded" not in a
    assert not any("non registrato in Annona" in c.value for c in at.caption)
