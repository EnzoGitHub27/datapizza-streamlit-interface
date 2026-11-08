# tests/test_hybrid_error_side_calls.py
# DeepAiUG v1.16.1 — voce 1 del giro 8: la configurazione ibrida illeggibile
# non deve aprire le altre vie.
# ============================================================================
# Se security_settings.yaml ha una sezione hybrid: che non si legge, l'app non
# sa se rizzo-pii doveva essere acceso. Fino alla 1.16.0 si bloccava solo il
# messaggio della chat; bottoni socratici, nudge, generazione e rigenerazione
# della mappa andavano al cloud in chiaro. Dalla 1.16.1 ogni chiamata verso
# fuori casa si blocca con lo stesso messaggio della chat; in casa (Ollama
# locale, LAN, Tailscale) tutto funziona come prima.
# Cloud FINTO; conversazioni in tmp_path; dati inventati.
# ============================================================================

import pytest
from streamlit.testing.v1 import AppTest

from config.hybrid_settings import HybridSettingsError
from core.llm_client import create_client
from core.pii_guard import PIIGuardBlocked
from tests.test_gateway_side_calls import MAP_REPLY, MESSAGES, VIE

ERRORE = "hybrid.pii.enabled deve essere vero o falso"
BLOCCO = "configurazione ibrida non valida"


# --- create_client ---------------------------------------------------------------------

def _raw(monkeypatch):
    import core.llm_client as llm

    marker = object()
    monkeypatch.setattr(llm, "_create_raw_client", lambda *a, **k: marker)
    return marker


def test_hybrid_error_outside_gives_blocker(monkeypatch):
    from core.pii_guard import HybridConfigBlockedClient

    _raw(monkeypatch)
    c = create_client("Cloud provider", "OpenAI", "sk-finta", "m", "sys", "", 0.7,
                      hybrid=None, hybrid_error=ERRORE)
    assert isinstance(c, HybridConfigBlockedClient)
    with pytest.raises(PIIGuardBlocked, match="Configurazione ibrida non valida"):
        c.invoke("x")
    with pytest.raises(PIIGuardBlocked, match=ERRORE):
        list(c.stream_invoke("x"))


@pytest.mark.parametrize("ct,url", [
    ("Local (Ollama)", "http://localhost:11434/v1"),
    ("Remote host", "http://192.168.1.20:11434/v1"),
    ("Remote host", "http://100.64.0.7:11434/v1"),  # Tailscale
])
def test_hybrid_error_in_house_gives_raw(monkeypatch, ct, url):
    marker = _raw(monkeypatch)
    c = create_client(ct, "", "", "m", "sys", url, 0.7, hybrid=None, hybrid_error=ERRORE)
    assert c is marker


def test_message_same_as_chat():
    from core.pii_guard import hybrid_error_message

    assert hybrid_error_message(ERRORE) == (
        f"🛡️ Configurazione ibrida non valida, messaggio non inviato: {ERRORE}"
    )


# --- l'app intera: le quattro vie ------------------------------------------------------

@pytest.fixture
def broken_app(monkeypatch, tmp_path):
    import config.hybrid_settings as hs
    import core.llm_client as llm

    monkeypatch.setattr("core.persistence.CONVERSATIONS_DIR", tmp_path)
    monkeypatch.setattr("ui.sidebar.llm_config.load_api_key", lambda *a, **k: "", raising=False)

    def broken(*a, **k):
        raise HybridSettingsError(ERRORE)

    monkeypatch.setattr(hs, "load_hybrid_settings", broken)
    sent = []

    class Model:
        def invoke(self, x):
            sent.append(str(x))
            return type("R", (), {"text": MAP_REPLY if "1." in str(x) or "domande" in str(x).lower()
                                  else "Una prospettiva alternativa"})()

        def stream_invoke(self, x):
            sent.append(str(x))
            yield type("C", (), {"text": "risposta"})()

    monkeypatch.setattr(llm, "_create_raw_client", lambda *a, **k: Model())

    def start(connection_type, **state):
        at = AppTest.from_file("app.py", default_timeout=120)
        at.session_state["connection_type"] = connection_type
        if connection_type == "Local (Ollama)":
            at.session_state["models_local"] = ["modello-finto"]
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


@pytest.mark.parametrize("via", list(VIE))
def test_side_call_blocked_outside(broken_app, via):
    start, sent = broken_app
    state, act = VIE[via]
    at = act(start("Cloud provider", **state()))
    assert sent == []  # al cloud non è arrivato niente
    assert _blocked(at), _errors(at)
    assert len(at.session_state["messages"]) == len(MESSAGES)


@pytest.mark.parametrize("via", list(VIE))
def test_side_call_works_in_house(broken_app, via):
    start, sent = broken_app
    state, act = VIE[via]
    at = act(start("Local (Ollama)", **state()))
    assert sent, "in casa la chiamata doveva partire come prima"
    assert not _blocked(at), _errors(at)
