# tests/test_privacy_reset.py
# DeepAiUG v1.16.1 — voce 2 del giro 8: «🔄 Reset e usa Cloud» azzera come «Nuova».
# ============================================================================
# Il dialogo privacy (documenti caricati, destinazione fuori casa) ha un
# bottone di reset. Fino alla 1.16.0 azzerava solo messaggi, ID e flag privacy:
# restavano la memoria dei dati tolti (_pii_memory), i riquadri «Cosa ha visto
# il modello» (egress_views, per posizione: la chat nuova poteva mostrare quello
# della vecchia), i conteggi del guard, la cache e lo storico socratici, la
# mappa e i contatori. Ora usa reset_conversation, la stessa funzione di «Nuova».
# Dati inventati; conversazioni in tmp_path; niente rete.
# ============================================================================

from streamlit.testing.v1 import AppTest

from core.pii_memory import PIISessionMemory
from tests.test_gateway_side_calls import _existing_map

VECCHIO = "Il modello ha visto [FULLNAME_1] della chat vecchia"


def _memory_with_value():
    mem = PIISessionMemory()
    mem._by_value["Anna Bianchi"] = "[FULLNAME_1]"
    mem._by_ph["[FULLNAME_1]"] = "Anna Bianchi"
    return mem


def _old_chat_state():
    return {
        "messages": [
            {"role": "user", "content": "Scrivi ad Anna Bianchi", "timestamp": "2026-11-06T10:00:00"},
            {"role": "assistant", "content": "Fatto.", "timestamp": "2026-11-06T10:00:05",
             "model": "gpt-finto", "provider": "Cloud provider", "pii_removed": 1},
        ],
        "documents_uploaded_this_session": True,
        "uploaded_files_history": ["contratto.pdf"],
        "egress_views": {1: VECCHIO},
        "_pii_memory": _memory_with_value(),
        "pii_removed": 1,
        "pii_guard": {"enabled": True},
        "total_tokens_estimate": 1234,
        "socratic_alternatives_1": "risposta socratica in cache",
        "session_map_data": _existing_map(),
        "n_domande_sessione": 5,
        "nudge_mostrato": True,
    }


def _app(monkeypatch, tmp_path):
    monkeypatch.setattr("core.persistence.CONVERSATIONS_DIR", tmp_path)
    monkeypatch.setattr("ui.sidebar.llm_config.load_api_key", lambda *a, **k: "sk-finta", raising=False)
    at = AppTest.from_file("app.py", default_timeout=120)
    at.session_state["connection_type"] = "Cloud provider"
    for k, v in _old_chat_state().items():
        at.session_state[k] = v
    at.run()
    assert not at.exception, at.exception
    return at


def test_dialog_reset_clears_like_new(monkeypatch, tmp_path):
    at = _app(monkeypatch, tmp_path)
    assert any("Conferma Privacy" in t.value for t in at.title), "il dialogo doveva aprirsi"

    at.button(key="privacy_reset_btn").click().run()
    assert not at.exception, at.exception

    ss = at.session_state
    assert ss["messages"] == []
    assert "_pii_memory" not in ss or len(ss["_pii_memory"]) == 0
    assert not ss["egress_views"]
    assert ss["pii_removed"] == 0 and "pii_guard" not in ss
    assert ss["total_tokens_estimate"] == 0
    assert "socratic_alternatives_1" not in ss
    assert ss["session_map_data"] is None
    assert ss["n_domande_sessione"] == 0 and ss["nudge_mostrato"] is False
    assert ss["documents_uploaded_this_session"] is False


def test_dialog_reset_hides_old_egress_view():
    """Dopo il reset del dialogo, la risposta in posizione 1 della chat nuova
    non mostra il riquadro «Cosa ha visto il modello» della chat vecchia."""

    def script(vecchio):
        import streamlit as st

        from ui.chat import render_chat_message
        from ui.privacy_warning import handle_privacy_action

        if not st.session_state.get("_fatto"):
            st.session_state["egress_views"] = {1: vecchio}
            st.session_state["_fatto"] = True
            handle_privacy_action("reset")  # fa st.rerun()
        nuovi = [
            {"role": "user", "content": "Ciao", "timestamp": "2026-11-06T11:00:00"},
            {"role": "assistant", "content": "Ciao!", "timestamp": "2026-11-06T11:00:05",
             "model": "gpt-finto", "provider": "Cloud provider"},
        ]
        for i, m in enumerate(nuovi):
            render_chat_message(m, i, None, messages_list=nuovi, socratic_mode="fast")

    at = AppTest.from_function(script, args=(VECCHIO,), default_timeout=30)
    at.run()
    assert not at.exception, at.exception
    assert at.session_state["_fatto"] is True
    assert not [e for e in at.expander if "Cosa ha visto il modello" in e.label]
    assert VECCHIO not in " ".join(t.proto.body for t in at.get("text"))


def test_one_reset_function():
    import inspect

    import ui.privacy_warning as pw
    from ui.conversation_reset import reset_conversation

    src = inspect.getsource(pw.handle_privacy_action)
    assert "reset_conversation" in src
    assert 'st.session_state["messages"] = []' not in src  # niente seconda copia
    assert callable(reset_conversation)
