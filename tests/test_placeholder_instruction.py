# tests/test_placeholder_instruction.py
# DeepAiUG v1.16.0 (giro 7) — Con il guard, al system prompt si aggiunge la
# riga che spiega i segnaposto al modello: passa da rizzo-pii nella stessa
# chiamata e il ripristino non la tocca. Con l'ibrido spento non c'è.
# rizzo-pii e cloud FINTI; conversazioni in tmp_path; dati inventati.
# ============================================================================

import pytest

from config.hybrid_settings import parse_hybrid_settings
from core.llm_client import create_client
from core.pii_client import PIIClient
from core.pii_guard import _SEP_MARK, PLACEHOLDER_NOTE, GuardedClient
from tests.test_pii_guard import FakeCloud, FakeRizzo


def _guard(cloud, rizzo, system_prompt="Sei un assistente."):
    return GuardedClient(client_factory=cloud.factory, system_prompt=system_prompt,
                         pii=PIIClient(session=rizzo))


def test_note_is_in_system_prompt_with_guard():
    rizzo, cloud = FakeRizzo(), FakeCloud(reply="ok")
    _guard(cloud, rizzo).invoke("Scrivi a Mario Rossi.")
    sp, prompt = cloud.sent[0]
    assert sp.endswith(PLACEHOLDER_NOTE) and sp.startswith("Sei un assistente.")
    # una sola chiamata a rizzo-pii, con la riga dentro
    assert len(rizzo.calls) == 1
    assert PLACEHOLDER_NOTE in rizzo.calls[0]["text"].split(_SEP_MARK)[0]


def test_note_alone_when_no_system_prompt():
    rizzo, cloud = FakeRizzo(), FakeCloud(reply="ok")
    _guard(cloud, rizzo, system_prompt="").invoke("Scrivi a Mario Rossi.")
    assert cloud.sent[0][0] == PLACEHOLDER_NOTE


def test_note_in_streaming_too():
    rizzo, cloud = FakeRizzo(), FakeCloud(chunks=["Gentile ", "[FULLNAME_1]."])
    list(_guard(cloud, rizzo).stream_invoke("Scrivi a Mario Rossi."))
    assert cloud.sent[0][0].endswith(PLACEHOLDER_NOTE)


def test_restore_does_not_alter_note():
    rizzo, cloud = FakeRizzo(), FakeCloud(reply="ok")
    res = _guard(cloud, rizzo).invoke("Scrivi a Mario Rossi, CF RSSMRA80A01H501U.")
    assert res.restore(PLACEHOLDER_NOTE) == PLACEHOLDER_NOTE
    # e se il modello la ripete, torna com'è
    cloud.reply = PLACEHOLDER_NOTE
    assert _guard(cloud, FakeRizzo()).invoke("Scrivi a Mario Rossi.").text == PLACEHOLDER_NOTE


def test_note_examples_never_match_a_real_placeholder():
    assert "[FULLNAME_1]" not in PLACEHOLDER_NOTE and "_N]" in PLACEHOLDER_NOTE


def test_not_in_system_prompt_with_hybrid_off(monkeypatch):
    import core.llm_client as llm

    seen = []
    monkeypatch.setattr(llm, "_create_raw_client", lambda *a, **k: seen.append(a[4]) or object())
    create_client("Cloud provider", "OpenAI", "sk-finta", "m", "Sei un assistente.", "", 0.7,
                  hybrid=parse_hybrid_settings({}))
    create_client("Local (Ollama)", "", "", "m", "Sei un assistente.", "http://localhost:11434", 0.7,
                  hybrid=parse_hybrid_settings({"pii": {"enabled": True}}))
    assert seen == ["Sei un assistente.", "Sei un assistente."]


@pytest.mark.parametrize("via", ["bottoni socratici", "nudge", "generazione mappa", "rigenerazione mappa"])
def test_side_calls_carry_the_note(monkeypatch, tmp_path, via):
    """Bottoni socratici, nudge e mappa: client dell'app con il guard → anche loro con la riga."""
    import core.llm_client as llm
    from tests import test_gateway_side_calls as side

    sps = []
    real_raw = llm._create_raw_client

    def raw(*a, **k):
        sps.append(a[4])
        return real_raw(*a, **k)

    # riusa la fixture dell'app del giro 5b con l'ibrido acceso (senza gateway)
    gen = side.side_app.__wrapped__(monkeypatch, tmp_path)
    start, sent = gen
    cloud_factory = llm._create_raw_client
    monkeypatch.setattr(llm, "_create_raw_client", lambda *a, **k: (sps.append(a[4]), cloud_factory(*a, **k))[1])
    state, act = side.VIE[via]
    act(start({"pii": {"enabled": True}}, **state()))
    assert sent and sps and all(sp.endswith(PLACEHOLDER_NOTE) for sp in sps)
