# tests/test_gateway_side_calls.py
# DeepAiUG v1.16.0 (giro 5b) — Il buco del gateway.
# ============================================================================
# Con il gateway di Annona acceso, le chiamate che non passano da Annona
# (bottoni socratici, nudge, generazione e rigenerazione della mappa, mappa
# progressiva dopo la risposta) verso fuori casa:
#   - con rizzo-pii acceso passano dal guard (al cloud vanno i segnaposto);
#   - con rizzo-pii spento si bloccano, con un messaggio chiaro, e al cloud
#     non arriva niente.
# rizzo-pii, cloud e Annona FINTI; conversazioni in tmp_path; dati inventati.
# ============================================================================

from datetime import datetime

import pytest
from streamlit.testing.v1 import AppTest

from config.hybrid_settings import parse_hybrid_settings
from core.llm_client import create_client
from core.pii_guard import GATEWAY_NEEDS_PII, GatewayBlockedClient, GatewaySideCallBlocked
from tests.test_pii_guard import FakeRizzo

NOME = "Mario Rossi"
SEGNAPOSTO = "[FULLNAME_1]"
BLOCCO = "con il gateway di annona, questa funzione verso il cloud richiede rizzo-pii"

GATEWAY_PII_OFF = {"annona": {"enabled": True, "mode": "gateway"}}
GATEWAY_PII_ON = {"annona": {"enabled": True, "mode": "gateway"}, "pii": {"enabled": True}}

MAP_REPLY = (
    "FRAME_DOMINANTE: pratico\n"
    "1. contributo uno\n"
    "2. contributo due\n"
    "FRAME_INESPLORATI: etico"
)

MESSAGES = [
    {"role": "user", "content": f"Come scrivo a {NOME} per il contratto?", "timestamp": "2026-11-06T10:00:00"},
    {"role": "assistant", "content": f"Puoi scrivere a {NOME} così.", "timestamp": "2026-11-06T10:00:05",
     "model": "gpt-finto", "provider": "Cloud provider"},
    {"role": "user", "content": "E se non risponde?", "timestamp": "2026-11-06T10:01:00"},
    {"role": "assistant", "content": "Allora richiami fra una settimana.", "timestamp": "2026-11-06T10:01:05",
     "model": "gpt-finto", "provider": "Cloud provider"},
]


# --- create_client ---------------------------------------------------------------------

def _raw(monkeypatch):
    import core.llm_client as llm

    marker = object()
    monkeypatch.setattr(llm, "_create_raw_client", lambda *a, **k: marker)
    return marker


def test_gateway_pii_off_outside_gives_blocker(monkeypatch):
    _raw(monkeypatch)
    c = create_client("Cloud provider", "OpenAI", "sk-finta", "m", "sys", "", 0.7,
                      hybrid=parse_hybrid_settings(GATEWAY_PII_OFF))
    assert isinstance(c, GatewayBlockedClient)
    with pytest.raises(GatewaySideCallBlocked, match="richiede rizzo-pii"):
        c.invoke("x")
    with pytest.raises(GatewaySideCallBlocked):
        list(c.stream_invoke("x"))


def test_gateway_pii_on_outside_gives_guard(monkeypatch):
    from core.pii_guard import GuardedClient

    _raw(monkeypatch)
    c = create_client("Cloud provider", "OpenAI", "sk-finta", "m", "sys", "", 0.7,
                      hybrid=parse_hybrid_settings(GATEWAY_PII_ON))
    assert isinstance(c, GuardedClient)


def test_gateway_in_house_gives_raw(monkeypatch):
    marker = _raw(monkeypatch)
    c = create_client("Local (Ollama)", "", "", "m", "sys", "http://localhost:11434", 0.7,
                      hybrid=parse_hybrid_settings(GATEWAY_PII_OFF))
    assert c is marker


def test_read_mode_pii_off_unchanged(monkeypatch):
    marker = _raw(monkeypatch)
    c = create_client("Cloud provider", "OpenAI", "sk-finta", "m", "sys", "", 0.7,
                      hybrid=parse_hybrid_settings({"annona": {"enabled": True, "mode": "read"}}))
    assert c is marker  # in sola lettura nulla cambia rispetto al giro 5


def test_block_message_is_fixed():
    assert "rizzo-pii" in GATEWAY_NEEDS_PII and NOME not in GATEWAY_NEEDS_PII


# --- l'app intera: le vie laterali --------------------------------------------------

@pytest.fixture
def side_app(monkeypatch, tmp_path):
    import config.hybrid_settings as hs
    import core.annona_bridge as bridge
    import core.llm_client as llm
    import core.pii_client as pc
    from core.annona_client import AnnonaClient
    from tests.fakes_http import FakeResponse, FakeSession
    from tests.test_annona_gateway import ASK_OK

    monkeypatch.setattr("core.persistence.CONVERSATIONS_DIR", tmp_path)
    monkeypatch.setattr("ui.sidebar.llm_config.load_api_key", lambda *a, **k: "", raising=False)
    real = pc.PIIClient
    monkeypatch.setattr(pc, "PIIClient", lambda url, timeout=30: real(url, timeout, session=FakeRizzo()))
    monkeypatch.setattr(bridge, "make_client", lambda settings, timeout=3.0: AnnonaClient(
        session=FakeSession({
            ("post", "/api/kernel/ask"): FakeResponse(200, ASK_OK),
            ("get", "/health"): FakeResponse(200, {"status": "ok"}),
            ("get", "/api/kernel/status"): FakeResponse(200, {"enforcing": False}),
        })))
    sent = []

    class Cloud:
        def invoke(self, x):
            sent.append(str(x))
            return type("R", (), {"text": MAP_REPLY if "1." in str(x) or "domande" in str(x).lower()
                                  else f"Alternativa per {SEGNAPOSTO}"})()

        def stream_invoke(self, x):
            sent.append(str(x))
            yield type("C", (), {"text": "non deve arrivare"})()

    monkeypatch.setattr(llm, "_create_raw_client", lambda *a, **k: Cloud())

    def start(hybrid_raw, **state):
        monkeypatch.setattr(hs, "load_hybrid_settings", lambda *a, **k: parse_hybrid_settings(hybrid_raw))
        at = AppTest.from_file("app.py", default_timeout=120)
        at.session_state["connection_type"] = "Cloud provider"
        for k, v in state.items():
            at.session_state[k] = v
        at.run()
        keys = [t for t in at.sidebar.text_input if "API Key" in t.label]
        if keys:
            keys[0].set_value("sk-finta-per-test").run()
        assert not at.exception, at.exception
        return at

    return start, sent


def _errors(at):
    return [e.value for e in list(at.error) + list(at.sidebar.error)]


def _blocked(at):
    return any(BLOCCO in e.lower() for e in _errors(at))


def _msgs():
    return [dict(m) for m in MESSAGES]


def _click(at, key):
    at.button(key=key).click().run()
    assert not at.exception, at.exception
    return at


def _socratic(at):
    # il bottone mette in loading e fa rerun: nello stesso giro parte la generazione
    return _click(at, "btn_alternatives_1")


def _nudge_state():
    return {"messages": _msgs(), "n_domande_sessione": 5, "nudge_mostrato": True,
            "session_map_mode": "threshold"}


def _existing_map():
    from ui.socratic.session_map import SessionMap

    return SessionMap(entries=[], dominant_frame="pratico", unexplored_frames=[],
                      session_id="x", created_at=datetime(2026, 11, 6, 10, 0))


VIE = {
    "bottoni socratici": (lambda: {"messages": _msgs(), "socratic_mode": "standard"}, _socratic),
    "nudge": (_nudge_state, lambda at: _click(at, "btn_show_session_map")),
    "generazione mappa": (lambda: {"messages": _msgs(), "session_map_mode": "threshold"},
                          lambda at: _click(at, "btn_genera_mappa")),
    "rigenerazione mappa": (lambda: {"messages": _msgs(), "session_map_mode": "threshold",
                                     "session_map_data": _existing_map()},
                            lambda at: _click(at, "btn_rigenera_mappa")),
}


@pytest.mark.parametrize("via", list(VIE))
def test_side_call_blocked_without_pii(side_app, via):
    start, sent = side_app
    state, act = VIE[via]
    at = act(start(GATEWAY_PII_OFF, **state()))
    assert sent == []  # al cloud non è arrivato niente
    assert _blocked(at), _errors(at)
    assert len(at.session_state["messages"]) == len(MESSAGES)  # la chat non si tocca


@pytest.mark.parametrize("via", list(VIE))
def test_side_call_guarded_with_pii(side_app, via):
    start, sent = side_app
    state, act = VIE[via]
    at = act(start(GATEWAY_PII_ON, **state()))
    assert sent, "la chiamata laterale doveva partire, tramite il guard"
    assert NOME not in " ".join(sent) and SEGNAPOSTO in " ".join(sent)
    assert not _blocked(at)


def _send(at, text):
    at.text_area[0].set_value(text)
    at.button(key="FormSubmitter:msg_form-🚀 Invia").click().run()
    assert not at.exception, at.exception
    return at


def test_progressive_map_blocked_without_pii_keeps_answer(side_app):
    start, sent = side_app
    at = start(GATEWAY_PII_OFF, messages=_msgs(), n_domande_sessione=3, session_map_mode="progressive")
    at = _send(at, f"Ultima cosa per {NOME}")
    assert sent == []  # la risposta l'ha data Annona, la mappa non è partita
    roles = [m["role"] for m in at.session_state["messages"]]
    assert roles[-2:] == ["user", "assistant"]
    assert at.session_state["messages"][-1].get("annona_gateway") is True
    assert "send_status" not in at.session_state["messages"][-2]
    assert _blocked(at), _errors(at)
    assert at.session_state["session_map_data"] is None


def test_progressive_map_guarded_with_pii(side_app):
    start, sent = side_app
    at = start(GATEWAY_PII_ON, messages=_msgs(), n_domande_sessione=3, session_map_mode="progressive")
    at = _send(at, f"Ultima cosa per {NOME}")
    assert sent and NOME not in " ".join(sent) and SEGNAPOSTO in " ".join(sent)
    assert at.session_state["messages"][-1].get("annona_gateway") is True
    assert not _blocked(at)
