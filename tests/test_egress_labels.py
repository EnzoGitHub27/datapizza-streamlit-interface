# tests/test_egress_labels.py
# DeepAiUG v1.16.0 (giro 4) — Gli avvisi guardano la destinazione reale:
# dialogo privacy, avviso sulla chat caricata, icone 🔒, bordo e titolo.
# ============================================================================
# Destinazioni finte (risoluzione dei nomi simulata), dati inventati.
# ============================================================================

import socket

import pytest
from streamlit.testing.v1 import AppTest

from ui.privacy_warning import should_show_privacy_dialog

FAKE_DNS = {"ollama-pubblico.example": "8.8.4.4", "nas-ufficio.lan": "192.168.1.50"}


@pytest.fixture(autouse=True)
def fake_dns(monkeypatch):
    def resolve(host):
        if host in FAKE_DNS:
            return FAKE_DNS[host]
        if host == "localhost":
            return "127.0.0.1"
        try:
            socket.inet_aton(host)
            return host
        except OSError:
            raise socket.gaierror(host)

    monkeypatch.setattr(socket, "gethostbyname", resolve)


# --- dialogo privacy ------------------------------------------------------------

def _dialog_state(outside, docs=True, ack=False):
    def script(outside, docs, ack):
        import streamlit as st

        from ui.privacy_warning import should_show_privacy_dialog

        st.session_state["documents_uploaded_this_session"] = docs
        st.session_state["privacy_acknowledged_for_cloud"] = ack
        st.session_state["result"] = should_show_privacy_dialog("Remote host", outside=outside)

    at = AppTest.from_function(script, args=(outside, docs, ack))
    at.run()
    return at.session_state["result"]


def test_dialog_for_public_remote_host():
    assert _dialog_state(outside=True) is True


def test_no_dialog_for_lan():
    assert _dialog_state(outside=False) is False


def test_no_dialog_without_docs_or_after_consent():
    assert _dialog_state(outside=True, docs=False) is False
    assert _dialog_state(outside=True, ack=True) is False


def _dialog_app(pii_active):
    def script(pii_active):
        import streamlit as st

        from ui.privacy_warning import render_privacy_dialog

        st.session_state["uploaded_files_history"] = ["preventivo_finto.pdf"]
        render_privacy_dialog(pii_active=pii_active)

    at = AppTest.from_function(script, args=(pii_active,))
    at.run()
    assert not at.exception, at.exception
    return at


def test_dialog_with_pii_offers_anonymization():
    at = _dialog_app(pii_active=True)
    labels = [b.label for b in at.button]
    assert "🛡️ Procedi con anonimizzazione" in labels
    assert "✅ Procedi con Cloud" not in labels


def test_dialog_without_pii_is_as_before():
    labels = [b.label for b in _dialog_app(pii_active=False).button]
    assert "✅ Procedi con Cloud" in labels
    assert "🛡️ Procedi con anonimizzazione" not in labels


# --- la sidebar LLM: dialogo e avviso sulla chat caricata ------------------------

def _sidebar(host, docs=False, messages=None, pii_active=False):
    def script():
        from ui.sidebar.llm_config import render_llm_config

        render_llm_config()

    at = AppTest.from_function(script, default_timeout=30)
    at.session_state["connection_type"] = "Remote host"
    at.session_state["documents_uploaded_this_session"] = docs
    at.session_state["hybrid_pii_active"] = pii_active
    at.session_state["messages"] = messages or []
    at.run()
    [t for t in at.sidebar.text_input if t.label == "Host"][0].set_value(host).run()
    assert not at.exception, at.exception
    return at


SENSITIVE_CHAT = [
    {"role": "user", "content": "Riassumi il contratto", "attachments": ["contratto_finto.pdf"]},
    {"role": "assistant", "content": "Il contratto di Mario Rossi prevede...", "model": "llama3.2:3b"},
]


@pytest.fixture
def manual_host(monkeypatch):
    monkeypatch.setattr("config.settings.load_remote_servers_config", lambda: None)


def test_public_host_with_docs_asks_consent(manual_host):
    at = _sidebar("http://ollama-pubblico.example:11434/v1", docs=True)
    assert at.session_state["show_privacy_dialog"] is True


def test_lan_host_with_docs_no_consent(manual_host):
    at = _sidebar("http://nas-ufficio.lan:11434/v1", docs=True)
    assert at.session_state["show_privacy_dialog"] is False


def _loaded_chat_warnings(at):
    return [w.value for w in at.sidebar.warning if "Questa conversazione contiene" in w.value]


def test_loaded_chat_warning_on_public_host(manual_host):
    warns = _loaded_chat_warnings(_sidebar("http://ollama-pubblico.example:11434/v1", messages=SENSITIVE_CHAT))
    assert warns and "Non c'è alcun filtro" in warns[0]


def test_loaded_chat_warning_mentions_rizzo_when_active(manual_host):
    warns = _loaded_chat_warnings(
        _sidebar("http://ollama-pubblico.example:11434/v1", messages=SENSITIVE_CHAT, pii_active=True)
    )
    assert warns and "rizzo-pii" in warns[0] and "Non c'è alcun filtro" not in warns[0]


def test_no_loaded_chat_warning_on_lan(manual_host):
    assert _loaded_chat_warnings(_sidebar("http://nas-ufficio.lan:11434/v1", messages=SENSITIVE_CHAT)) == []


# --- icone 🔒 delle conversazioni -------------------------------------------------

def _outside_from_state(dest):
    def script(dest):
        import streamlit as st

        from ui.privacy_warning import destination_is_outside

        if dest is not None:
            st.session_state["egress_destination"] = dest
        st.session_state["connection_type"] = "Remote host"
        st.session_state["result"] = destination_is_outside()

    at = AppTest.from_function(script, args=(dest,))
    at.run()
    return at.session_state["result"]


def test_conversation_lock_follows_destination():
    assert _outside_from_state({"outside": True, "category": "public"}) is True
    assert _outside_from_state({"outside": False, "category": "private"}) is False
    assert _outside_from_state(None) is False  # senza destinazione: l'etichetta (Remote = no)


def test_connection_css_follows_destination():
    from ui.styles import CLOUD_INDICATOR_CSS, get_connection_indicator_css

    assert get_connection_indicator_css("Remote host", False, outside=True) == CLOUD_INDICATOR_CSS
    assert get_connection_indicator_css("Cloud provider", False, outside=False) == ""
    assert get_connection_indicator_css("Cloud provider", False) == CLOUD_INDICATOR_CSS


# --- titolo e bordo dell'app intera ------------------------------------------------

def _app(monkeypatch, tmp_path, host):
    monkeypatch.setattr("config.settings.load_remote_servers_config", lambda: None)
    monkeypatch.setattr("core.persistence.CONVERSATIONS_DIR", tmp_path)
    at = AppTest.from_file("app.py", default_timeout=120)
    at.session_state["connection_type"] = "Remote host"
    at.run()
    [t for t in at.sidebar.text_input if t.label == "Host"][0].set_value(host).run()
    assert not at.exception, at.exception
    return at


def _border(at):
    css = " ".join(m.value for m in at.markdown if "border-top" in m.value)
    return "red" if "#ff6b6b" in css else "green" if "#4CAF50" in css else "?"


def test_public_remote_host_title_and_border(monkeypatch, tmp_path):
    at = _app(monkeypatch, tmp_path, "http://ollama-pubblico.example:11434/v1")
    assert "Remote esterno ☁️" in at.title[0].value
    assert _border(at) == "red"


def test_lan_remote_host_title_and_border(monkeypatch, tmp_path):
    at = _app(monkeypatch, tmp_path, "http://nas-ufficio.lan:11434/v1")
    assert "→ Remote `" in at.title[0].value
    assert _border(at) == "green"
