# tests/test_reasoning.py
# DeepAiUG v1.16.2 (giro 10) — 🧠 il ragionamento del modello.
# Per Local (Ollama) e Remote host ogni chiamata porta `reasoning_effort`;
# per il cloud (OpenAI, Anthropic, Gemini, Custom) niente in più. Una risposta
# vuota non lascia la chat muta. Client e rizzo-pii FINTI, nessuna rete;
# conversazioni in tmp_path.
# ============================================================================

from types import SimpleNamespace

import pytest
from streamlit.testing.v1 import AppTest

from core.llm_client import (
    EMPTY_ANSWER_MESSAGE,
    REASONING_LEVELS,
    ReasoningOpenAILikeClient,
    create_client,
    reasoning_effort_for,
)
from core.pii_client import PIIClient
from core.pii_guard import GuardedClient
from tests.test_gateway_side_calls import MAP_REPLY, VIE
from tests.test_pii_guard import FakeRizzo

LAN = "http://192.168.1.227:11434/v1"
FUORI = "http://ollama-pubblico.example:11434/v1"


class FakeCompletions:
    """Il chat.completions di openai, finto: registra gli argomenti."""

    def __init__(self, text="Risposta finta"):
        self.calls = []
        self.text = text

    def create(self, **kwargs):
        self.calls.append(kwargs)
        if kwargs.get("stream"):
            return iter([
                SimpleNamespace(
                    usage=None,
                    choices=[SimpleNamespace(
                        delta=SimpleNamespace(content=self.text, tool_calls=None),
                        finish_reason="stop",
                    )],
                ),
            ])
        return SimpleNamespace(
            id="x",
            usage=None,
            choices=[SimpleNamespace(
                message=SimpleNamespace(content=self.text, tool_calls=None, reasoning_content=None),
                finish_reason="stop",
            )],
        )


def _wire(client, completions):
    """Mette il chat.completions finto al posto di quello vero (nessuna rete)."""
    fake_openai = SimpleNamespace(chat=SimpleNamespace(completions=completions))
    client.client = fake_openai
    client._get_client = lambda: fake_openai
    return client


def _calls_of(client, stream=True):
    completions = FakeCompletions()
    _wire(client, completions)
    if stream:
        list(client.stream_invoke("Quanto fa 6 per 7?"))
    else:
        client.invoke("Quanto fa 6 per 7?")
    return completions.calls


# --- i livelli -----------------------------------------------------------------

def test_levels_map_to_reasoning_effort():
    assert REASONING_LEVELS == {"Spento": "none", "Basso": "low", "Medio": "medium", "Alto": "high"}
    for ct in ("Local (Ollama)", "Remote host"):
        assert reasoning_effort_for(ct, None) == "none"  # Spento è il predefinito
        assert reasoning_effort_for(ct, "Alto") == "high"
        assert reasoning_effort_for(ct, "boh") == "none"


def test_cloud_gets_no_reasoning_effort():
    for level in [None, *REASONING_LEVELS]:
        assert reasoning_effort_for("Cloud provider", level) is None


# --- Local e Remote host: il parametro arriva fino a chat.completions.create ----

@pytest.mark.parametrize("ct,url", [("Local (Ollama)", "http://localhost:11434/v1"),
                                    ("Remote host", LAN)])
@pytest.mark.parametrize("level", list(REASONING_LEVELS))
@pytest.mark.parametrize("stream", [True, False])
def test_in_house_request_has_reasoning_effort(ct, url, level, stream):
    effort = reasoning_effort_for(ct, level)
    c = create_client(ct, "", "", "qwen3.6:35b-a3b", "sp", url, 0.7, reasoning_effort=effort)
    assert isinstance(c, ReasoningOpenAILikeClient)
    calls = _calls_of(c, stream=stream)
    assert len(calls) == 1
    assert calls[0]["reasoning_effort"] == REASONING_LEVELS[level]
    assert calls[0]["model"] == "qwen3.6:35b-a3b"


def test_caller_value_wins():
    c = create_client("Remote host", "", "", "m", "sp", LAN, 0.7, reasoning_effort="none")
    completions = FakeCompletions()
    _wire(c, completions)
    c.invoke("x", reasoning_effort="high")
    assert completions.calls[0]["reasoning_effort"] == "high"


def test_without_reasoning_effort_the_client_is_the_old_one():
    from datapizza.clients.openai_like import OpenAILikeClient

    c = create_client("Local (Ollama)", "", "", "m", "sp", "http://localhost:11434/v1", 0.7)
    assert type(c) is OpenAILikeClient
    assert "reasoning_effort" not in _calls_of(c)[0]


# --- Cloud e Custom: niente in più -----------------------------------------------

def test_custom_cloud_has_no_reasoning_effort():
    c = create_client("Cloud provider", "Custom", "sk-finta", "m", "sp",
                      "https://api.example.com/v1", 0.7, reasoning_effort="high")
    assert not isinstance(c, ReasoningOpenAILikeClient)
    for stream in (True, False):
        assert "reasoning_effort" not in _calls_of(c, stream=stream)[0]


@pytest.mark.parametrize("provider", ["OpenAI", "Anthropic (Claude)", "Google Gemini"])
def test_fixed_cloud_providers_are_untouched(provider, monkeypatch):
    # la fabbrica di Datapizza finta: i client cloud non si creano davvero
    made = []
    monkeypatch.setattr("core.llm_client.ClientFactory.create",
                        lambda **k: made.append(k) or SimpleNamespace(kind="cloud"))
    c = create_client("Cloud provider", provider, "sk-finta", "m", "sp", "", 0.7,
                      reasoning_effort="high")
    assert not isinstance(c, ReasoningOpenAILikeClient)
    assert made and "reasoning_effort" not in made[0]


# --- attraverso PIIGuard ----------------------------------------------------------

def _hybrid_on():
    from config.hybrid_settings import parse_hybrid_settings

    return parse_hybrid_settings({"pii": {"enabled": True}})


def test_reasoning_effort_passes_through_pii_guard(monkeypatch):
    import core.pii_client as pc

    real = pc.PIIClient
    monkeypatch.setattr(pc, "PIIClient", lambda url, timeout=30: real(url, timeout, session=FakeRizzo()))
    made = []
    import core.llm_client as llm

    real_raw = llm._create_raw_client

    def raw(*a, **k):
        c = _wire(real_raw(*a, **k), FakeCompletions("Ciao [FULLNAME_1]"))
        made.append(c)
        return c

    monkeypatch.setattr(llm, "_create_raw_client", raw)
    g = create_client("Remote host", "", "", "m", "sp", FUORI, 0.7,
                      hybrid=_hybrid_on(), reasoning_effort="low")
    assert isinstance(g, GuardedClient)

    chunks = list(g.stream_invoke("Saluta Mario Rossi"))
    sent = made[-1].client.chat.completions.calls[0]
    assert sent["reasoning_effort"] == "low"
    assert "Mario Rossi" not in str(sent["messages"])  # anonimizzato davvero
    assert chunks[-1].text == "Ciao Mario Rossi"

    g.invoke("Saluta Mario Rossi")
    assert made[-1].client.chat.completions.calls[0]["reasoning_effort"] == "low"


def test_pii_guard_forwards_extra_kwargs():
    """Il GuardedClient inoltra gli argomenti in più al client vero."""
    got = []

    class Raw:
        def invoke(self, x, *a, **k):
            got.append(k)
            return SimpleNamespace(text="ok")

        def stream_invoke(self, x, *a, **k):
            got.append(k)
            yield SimpleNamespace(text="ok")

    g = GuardedClient(client_factory=lambda sp: Raw(), system_prompt="sp",
                      pii=PIIClient("http://localhost:8000", session=FakeRizzo()))
    g.invoke("Mario Rossi", reasoning_effort="medium")
    list(g.stream_invoke("Mario Rossi", reasoning_effort="medium"))
    assert got == [{"reasoning_effort": "medium"}, {"reasoning_effort": "medium"}]


# --- la sidebar ---------------------------------------------------------------------

def _sidebar(connection_type, level=None, monkeypatch=None):
    def script():
        from ui.sidebar.llm_config import render_llm_config

        render_llm_config()

    at = AppTest.from_function(script, default_timeout=30)
    at.session_state["connection_type"] = connection_type
    at.session_state["models_local"] = ["llama3.2:3b"]
    if level:
        at.session_state["reasoning_level"] = level
    at.run()
    assert not at.exception, at.exception
    return at


def _switch(at):
    return [s for s in at.sidebar.selectbox if "Ragionamento" in s.label]


def test_sidebar_switch_for_local_default_off():
    at = _sidebar("Local (Ollama)")
    sw = _switch(at)
    assert sw and sw[0].options == ["Spento", "Basso", "Medio", "Alto"]
    assert sw[0].value == "Spento"
    assert "gpt-oss" in sw[0].help and "Qwen" in sw[0].help
    sw[0].set_value("Alto").run()
    assert at.session_state["reasoning_level"] == "Alto"


def test_sidebar_switch_hidden_for_cloud_with_note(monkeypatch):
    monkeypatch.setattr("ui.sidebar.llm_config.load_api_key", lambda *a, **k: "", raising=False)
    at = _sidebar("Cloud provider", level="Alto")
    assert not _switch(at)
    assert any("Ragionamento del modello" in c.value for c in at.sidebar.caption)
    assert at.session_state["reasoning_level"] == "Alto"  # resta nella sessione


# --- l'app: il parametro nella chat e la risposta vuota -----------------------------

@pytest.fixture
def app(monkeypatch, tmp_path):
    import config.hybrid_settings as hs
    import core.llm_client as llm

    monkeypatch.setattr("core.persistence.CONVERSATIONS_DIR", tmp_path)
    monkeypatch.setattr(hs, "load_hybrid_settings", lambda *a, **k: hs.parse_hybrid_settings({}))
    state = {"reply": "Risposta finta", "efforts": []}

    class Raw:
        def __init__(self, effort):
            self.effort = effort

        def invoke(self, x, *a, **k):
            state["efforts"].append(("invoke", self.effort))
            return SimpleNamespace(text=MAP_REPLY)

        def stream_invoke(self, x, *a, **k):
            state["efforts"].append(("stream", self.effort))
            if state["reply"]:
                yield SimpleNamespace(text=state["reply"])

    monkeypatch.setattr(llm, "_create_raw_client",
                        lambda *a, reasoning_effort=None, **k: Raw(reasoning_effort))

    def start(level=None, **extra):
        at = AppTest.from_file("app.py", default_timeout=120)
        at.session_state["connection_type"] = "Local (Ollama)"
        at.session_state["models_local"] = ["qwen3.6:35b-a3b"]
        if level:
            at.session_state["reasoning_level"] = level
        for k, v in extra.items():
            at.session_state[k] = v
        at.run()
        assert not at.exception, at.exception
        return at

    return start, state


def _send(at, text):
    at.text_area(key="msg_input").set_value(text)
    at.button(key="FormSubmitter:msg_form-🚀 Invia").click().run()
    assert not at.exception, at.exception
    return at


def test_app_chat_sends_chosen_level(app):
    start, state = app
    at = _send(start("Medio"), "Quanto fa 6 per 7?")
    assert ("stream", "medium") in state["efforts"]
    assert at.session_state["messages"][-1]["content"] == "Risposta finta"


def test_app_chat_default_is_off(app):
    start, state = app
    _send(start(), "Ciao")
    assert ("stream", "none") in state["efforts"]


def test_app_empty_answer_shows_message(app):
    start, state = app
    state["reply"] = ""
    at = _send(start("Alto"), "Quanto fa 17 per 23?")
    msgs = at.session_state["messages"]
    assert msgs[-1]["role"] == "user"  # nessuna risposta vuota in chat
    assert msgs[-1]["send_status"] == "senza_risposta"
    assert EMPTY_ANSWER_MESSAGE in msgs[-1]["send_error"]
    assert any(EMPTY_ANSWER_MESSAGE in w.value and "🧠" in w.value for w in at.warning)
    # la domanda senza risposta non torna al modello
    from core.conversation import get_conversation_history
    assert get_conversation_history(msgs) == []


@pytest.mark.parametrize("via", list(VIE))
def test_app_side_calls_send_chosen_level(app, via):
    """Bottoni socratici, nudge, generazione e rigenerazione della mappa."""
    start, state = app
    make_state, act = VIE[via]
    act(start("Alto", **make_state()))
    assert ("invoke", "high") in state["efforts"], state["efforts"]
    assert all(e == "high" for _, e in state["efforts"])


def test_app_progressive_map_sends_chosen_level(app):
    start, state = app
    from tests.test_gateway_side_calls import _msgs

    at = start("Basso", messages=_msgs(), n_domande_sessione=3, session_map_mode="progressive")
    _send(at, "Ultima domanda")
    assert ("stream", "low") in state["efforts"] and ("invoke", "low") in state["efforts"]


def test_level_survives_cloud_and_back():
    """Il valore resta nella sessione anche quando l'interruttore non si mostra."""
    def script():
        import streamlit as st

        from ui.sidebar.llm_config import render_reasoning_level

        render_reasoning_level(st.session_state["ct"])

    at = AppTest.from_function(script, default_timeout=30)
    at.session_state["ct"] = "Remote host"
    at.run()
    at.selectbox[0].set_value("Medio").run()
    at.session_state["ct"] = "Cloud provider"
    at.run()
    assert not at.selectbox and at.session_state["reasoning_level"] == "Medio"
    at.run()  # un altro giro nel cloud: il widget non c'è più
    at.session_state["ct"] = "Remote host"
    at.run()
    assert not at.exception, at.exception
    assert at.selectbox[0].value == "Medio"
