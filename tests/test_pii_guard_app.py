# tests/test_pii_guard_app.py
# DeepAiUG v1.16.0 (giro 4, P6) — L'app intera con l'ibrido acceso e rizzo-pii
# giù: verso il cloud non parte niente, la domanda non resta in chat, il testo
# torna nella casella e l'avviso è visibile. Tutto finto, nessuna rete.
# ============================================================================

import pytest
from streamlit.testing.v1 import AppTest

from tests.test_pii_guard import FakeRizzo

DOMANDA = "Prepara la lettera per Mario Rossi, CF RSSMRA80A01H501U"


@pytest.fixture
def hybrid_on_rizzo_down(monkeypatch, tmp_path):
    import config.hybrid_settings as hs
    import core.llm_client as llm
    import core.pii_client as pc

    # le conversazioni del test in tmp_path, mai in conversations/
    monkeypatch.setattr("core.persistence.CONVERSATIONS_DIR", tmp_path)
    on = hs.parse_hybrid_settings({"pii": {"enabled": True}})
    monkeypatch.setattr(hs, "load_hybrid_settings", lambda *a, **k: on)
    real = pc.PIIClient
    monkeypatch.setattr(pc, "PIIClient", lambda url, timeout=30: real(url, timeout, session=FakeRizzo(down=True)))

    sent = []

    class Cloud:
        def __init__(self, *a, **k):
            pass

        def invoke(self, x):
            sent.append(x)

        def stream_invoke(self, x):
            sent.append(x)
            yield from ()

    monkeypatch.setattr(llm, "_create_raw_client", lambda *a, **k: Cloud())
    # niente API key salvate sul computer: la si scrive nel campo
    monkeypatch.setattr("ui.sidebar.llm_config.load_api_key", lambda *a, **k: "", raising=False)
    return sent, tmp_path


def test_blocked_send_keeps_text_and_shows_notice(hybrid_on_rizzo_down):
    sent, conv_dir = hybrid_on_rizzo_down
    at = AppTest.from_file("app.py", default_timeout=120)
    at.session_state["connection_type"] = "Cloud provider"
    at.run()
    assert not at.exception, at.exception
    keys = [t for t in at.sidebar.text_input if "API Key" in t.label]
    assert keys, [t.label for t in at.sidebar.text_input]
    keys[0].set_value("sk-finta-per-test").run()

    at.text_area[0].set_value(DOMANDA)
    at.button(key="FormSubmitter:msg_form-🚀 Invia").click().run()
    assert not at.exception, at.exception

    assert sent == []  # al cloud finto non è arrivato niente
    assert [m for m in at.session_state["messages"] if m["role"] == "user"] == []
    assert at.text_area[0].value == DOMANDA  # il testo è tornato nella casella
    assert any("rizzo-pii non risponde" in e.value for e in at.error)
    assert list(conv_dir.glob("conv_*.json")) == []  # nessun file vuoto lasciato
