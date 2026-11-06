# tests/test_egress.py
# DeepAiUG v1.16.0 (giro 3, P2) — KB, KB Chat, upload e immagini si bloccano
# sulla destinazione reale, non sull'etichetta «Cloud provider».
# ============================================================================
# Destinazioni finte: la risoluzione dei nomi è simulata, nessuna rete.
# ============================================================================

import socket

import pytest
from streamlit.testing.v1 import AppTest

from core.egress import classify_destination, outside_label

# nome finto → IP finto (documentazione e range riservati)
FAKE_DNS = {
    "ollama-pubblico.example": "8.8.4.4",   # internet pubblico (risoluzione finta)
    "nas-ufficio.lan": "192.168.1.50",           # LAN
    "mini-pc.tail-finta.ts.net": "100.101.102.103",  # Tailscale (CGNAT)
    "localhost": "127.0.0.1",
}


@pytest.fixture(autouse=True)
def fake_dns(monkeypatch):
    def resolve(host):
        if host in FAKE_DNS:
            return FAKE_DNS[host]
        try:
            socket.inet_aton(host)
            return host  # già un IP
        except OSError:
            raise socket.gaierror(f"nome finto non risolvibile: {host}")

    monkeypatch.setattr(socket, "gethostbyname", resolve)


@pytest.mark.parametrize(
    "connection_type, provider, base_url, outside, category",
    [
        # Remote host
        ("Remote host", None, "http://ollama-pubblico.example:11434/v1", True, "public"),
        ("Remote host", None, "http://nas-ufficio.lan:11434/v1", False, "private"),
        ("Remote host", None, "http://mini-pc.tail-finta.ts.net:11434/v1", False, "private"),
        ("Remote host", None, "http://1.1.1.1:11434/v1", True, "public"),
        ("Remote host", None, "http://non-esiste.invalid:11434/v1", True, "invalid"),
        ("Remote host", None, "http://169.254.169.254/latest", True, "link_local"),
        # Ollama locale
        ("Local (Ollama)", None, "http://localhost:11434/v1", False, "loopback"),
        # Cloud fisso: fuori casa senza risolvere il nome
        ("Cloud provider", "OpenAI", "https://api.openai.com/v1", True, "cloud"),
        ("Cloud provider", "Anthropic (Claude)", "http://localhost:1234/v1", True, "cloud"),
        ("Cloud provider", "Google Gemini", "", True, "cloud"),
        # Cloud «Custom»: decide l'URL
        ("Cloud provider", "Custom", "http://localhost:1234/v1", False, "loopback"),
        ("Cloud provider", "Custom", "http://nas-ufficio.lan:1234/v1", False, "private"),
        ("Cloud provider", "Custom", "https://ollama-pubblico.example/v1", True, "public"),
        ("Cloud provider", "Custom", "", True, "invalid"),  # Custom senza URL: nel dubbio fuori
    ],
)
def test_classify_destination(connection_type, provider, base_url, outside, category):
    d = classify_destination(connection_type, provider, base_url)
    assert d["outside"] is outside
    assert d["category"] == category


def test_outside_label():
    assert outside_label({"category": "cloud"}) == "Cloud provider"
    assert "ollama-pubblico.example" in outside_label(
        {"category": "public", "host": "ollama-pubblico.example"}
    )
    assert "non verificabile" in outside_label({"category": "invalid", "host": "x"})


# --- upload e immagini -------------------------------------------------------

def _upload_app(connection_type, outside):
    def script(connection_type, outside):
        from ui.file_upload import render_file_upload_widget

        render_file_upload_widget(connection_type, "llava:7b", key="up", outside=outside)

    at = AppTest.from_function(script, args=(connection_type, outside), default_timeout=30)
    at.run()
    assert not at.exception, at.exception
    return at


def _upload_disabled(at):
    return any("Upload file disabilitato" in w.value for w in at.warning)


def test_upload_blocked_for_public_remote_host():
    # il caso della lacuna 1.15.x: Remote host su internet, immagini comprese
    assert _upload_disabled(_upload_app("Remote host", outside=True))


def test_upload_allowed_for_custom_cloud_in_house():
    assert not _upload_disabled(_upload_app("Cloud provider", outside=False))


def test_upload_without_destination_keeps_label_rule():
    assert _upload_disabled(_upload_app("Cloud provider", outside=None))
    assert not _upload_disabled(_upload_app("Remote host", outside=None))


# --- KB e KB Chat: la sidebar LLM torna a Ollama locale ------------------------

def _llm_config_app(use_kb=False, use_chat_kb=False, connection_type="Cloud provider"):
    def script():
        import streamlit as st

        from ui.sidebar.llm_config import render_llm_config

        render_llm_config()
        st.write("dest:", st.session_state.get("egress_destination", {}).get("category"))

    at = AppTest.from_function(script, default_timeout=30)
    at.session_state["connection_type"] = connection_type
    at.session_state["use_knowledge_base"] = use_kb
    at.session_state["use_chat_kb"] = use_chat_kb
    at.session_state["models_local"] = ["llama3.2:3b"]
    at.run()
    assert not at.exception, at.exception
    return at


def test_kb_with_cloud_goes_back_to_local():
    at = _llm_config_app(use_kb=True)
    assert at.session_state["connection_type"] == "Local (Ollama)"
    assert any("bloccato" in e.value and "Cloud provider" in e.value for e in at.sidebar.error)
    assert at.session_state["egress_destination"]["outside"] is False


def test_chat_kb_with_cloud_goes_back_to_local():
    at = _llm_config_app(use_chat_kb=True)
    assert at.session_state["connection_type"] == "Local (Ollama)"


def test_cloud_without_kb_stays():
    at = _llm_config_app()
    assert at.session_state["connection_type"] == "Cloud provider"
    assert at.session_state["egress_destination"]["outside"] is True


def test_public_remote_host_with_kb_goes_back_to_local(monkeypatch):
    monkeypatch.setattr("config.settings.load_remote_servers_config", lambda: None)  # host manuale
    def script():
        import streamlit as st

        from ui.sidebar.llm_config import render_llm_config

        render_llm_config()

    at = AppTest.from_function(script, default_timeout=30)
    at.session_state["connection_type"] = "Remote host"
    at.session_state["use_knowledge_base"] = True
    at.session_state["models_local"] = ["llama3.2:3b"]
    at.run()
    # host manuale finto su internet
    host = [t for t in at.sidebar.text_input if t.label == "Host"]
    assert host, [t.label for t in at.sidebar.text_input]
    host[0].set_value("http://ollama-pubblico.example:11434/v1").run()
    assert not at.exception, at.exception
    assert at.session_state["connection_type"] == "Local (Ollama)"
    assert any("host esterno" in e.value for e in at.sidebar.error)


def test_lan_remote_host_with_kb_stays(monkeypatch):
    monkeypatch.setattr("config.settings.load_remote_servers_config", lambda: None)  # host manuale
    def script():
        from ui.sidebar.llm_config import render_llm_config

        render_llm_config()

    at = AppTest.from_function(script, default_timeout=30)
    at.session_state["connection_type"] = "Remote host"
    at.session_state["use_knowledge_base"] = True
    at.run()
    host = [t for t in at.sidebar.text_input if t.label == "Host"]
    assert host, [t.label for t in at.sidebar.text_input]
    host[0].set_value("http://nas-ufficio.lan:11434/v1").run()
    assert not at.exception, at.exception
    assert at.session_state["connection_type"] == "Remote host"
