# tests/test_pii_guard.py
# DeepAiUG v1.16.0 (giro 4, P6) — GuardedClient: verso fuori casa solo testo
# anonimizzato, risposta ripristinata in locale.
# ============================================================================
# rizzo-pii FINTO (sostituisce i valori inventati qui sotto con segnaposto
# numerati, come /analyze) e client cloud FINTO che registra ciò che riceve.
# Nessuna chiamata di rete. Tutti i dati sono inventati.
# ============================================================================

import re
from types import SimpleNamespace

import pytest
import requests

from core.pii_client import PIIClient
from core.pii_guard import GuardedClient, GuardedResponse, PIIGuardBlocked
from tests.fakes_http import FakeResponse, connection_refused

# valori inventati → tipo
FAKE_PII = {
    "Mario Rossi": "FULLNAME",
    "Lucia D'Angelo": "FULLNAME",
    "RSSMRA80A01H501U": "CF",
    "IT60X0542811101000000123456": "IBAN",
    "Ferrolago Srl": "ORG",
}
VALUES = list(FAKE_PII)


class FakeRizzo:
    """Sessione HTTP finta di rizzo-pii: /analyze anonimizza davvero."""

    def __init__(self, down=False, mapping_enabled=True, status=200):
        self.down = down
        self.mapping_enabled = mapping_enabled
        self.status = status
        self.calls = []

    def get(self, url, **kw):  # /health, non usato dal guard
        return FakeResponse(200, {"model_loaded": True})

    def post(self, url, json=None, **kw):
        self.calls.append(json)
        if self.down:
            raise connection_refused()
        if self.status != 200:
            return FakeResponse(self.status, {"error": "x"})
        text = json["text"].strip()
        mapping, counters = {}, {}
        # in ordine di apparizione, come rizzo-pii
        found = sorted(
            ((m.start(), v) for v in VALUES for m in re.finditer(re.escape(v), text)),
        )
        seen = {}
        for _, value in found:
            if value in seen:
                continue
            label = FAKE_PII[value]
            counters[label] = counters.get(label, 0) + 1
            seen[value] = f"[{label}_{counters[label]}]"
        for value, ph in seen.items():
            text = text.replace(value, ph)
            mapping[ph] = value
        return FakeResponse(200, {
            "anonymized_text": text,
            "mapping": mapping if self.mapping_enabled else {},
            "mapping_enabled": self.mapping_enabled,
            "n_entities": len(mapping),
            "by_label": counters,
        })


class FakeCloud:
    """Client cloud finto: registra system prompt e input, risponde a copione."""

    def __init__(self, reply="", chunks=None, raises=None):
        self.reply = reply
        self.chunks = chunks
        self.raises = raises
        self.sent = []  # (system_prompt, input)

    def factory(self, system_prompt):
        cloud = self

        class _Client:
            def invoke(self, llm_input):
                cloud.sent.append((system_prompt, llm_input))
                if cloud.raises:
                    raise cloud.raises
                return SimpleNamespace(text=cloud.reply)

            def stream_invoke(self, llm_input):
                cloud.sent.append((system_prompt, llm_input))
                for c in cloud.chunks or []:
                    yield SimpleNamespace(text=c)

        return _Client()

    def all_sent_text(self):
        out = []
        for sp, inp in self.sent:
            out.append(sp)
            if isinstance(inp, str):
                out.append(inp)
            else:
                out.extend(getattr(b, "content", "") for b in inp)
        return "\n".join(out)


def _guard(cloud, rizzo=None, system_prompt="Sei un assistente.", counted=None):
    return GuardedClient(
        client_factory=cloud.factory,
        system_prompt=system_prompt,
        pii=PIIClient(session=rizzo or FakeRizzo()),
        on_anonymized=(counted.append if counted is not None else None),
    )


def _no_values(text):
    return not any(v in text for v in VALUES)


# --- invoke -------------------------------------------------------------------

def test_invoke_sends_only_placeholders_and_restores():
    cloud = FakeCloud(reply="Ho scritto a [FULLNAME_1] (CF [CF_1]).")
    counted = []
    g = _guard(cloud, counted=counted)
    res = g.invoke("Scrivi a Mario Rossi, CF RSSMRA80A01H501U, IBAN IT60X0542811101000000123456.")

    assert _no_values(cloud.all_sent_text())
    assert "[FULLNAME_1]" in cloud.sent[0][1] and "[IBAN_1]" in cloud.sent[0][1]
    assert isinstance(res, GuardedResponse)
    assert res.text == "Ho scritto a Mario Rossi (CF RSSMRA80A01H501U)."
    assert res.content == res.text
    assert res.pii_removed == 3 and counted == [3]


def test_system_prompt_and_prompt_share_numbering():
    """Una sola chiamata a rizzo-pii: stessa persona, stesso segnaposto."""
    rizzo = FakeRizzo()
    cloud = FakeCloud(reply="ok")
    g = _guard(cloud, rizzo, system_prompt="Rispondi come assistente di Lucia D'Angelo.")
    g.invoke("Prepara un preventivo per Mario Rossi da parte di Lucia D'Angelo.")

    assert len(rizzo.calls) == 1  # una chiamata, non due
    sp, prompt = cloud.sent[0]
    assert sp == "Rispondi come assistente di [FULLNAME_1]."
    assert prompt == "Prepara un preventivo per [FULLNAME_2] da parte di [FULLNAME_1]."
    assert _no_values(cloud.all_sent_text())


def test_apostrophe_name_restored():
    cloud = FakeCloud(reply="Gentile [FULLNAME_1], ecco il preventivo per [ORG_1].")
    res = _guard(cloud).invoke("Scrivi a Lucia D'Angelo di Ferrolago Srl.")
    assert res.text == "Gentile Lucia D'Angelo, ecco il preventivo per Ferrolago Srl."
    assert _no_values(cloud.all_sent_text())


def test_text_blocks_anonymized():
    from datapizza.type import TextBlock

    cloud = FakeCloud(reply="ok")
    _guard(cloud).invoke([TextBlock(content="Dati di Mario Rossi")])
    sent = cloud.sent[0][1]
    assert isinstance(sent, list) and sent[0].content == "Dati di [FULLNAME_1]"


def test_media_block_blocked_without_calls():
    from datapizza.type import Media, MediaBlock, TextBlock

    rizzo, cloud = FakeRizzo(), FakeCloud(reply="ok")
    media = MediaBlock(media=Media(media_type="image", source_type="base64", source="AAAA", extension="png"))
    with pytest.raises(PIIGuardBlocked, match="immagini"):
        _guard(cloud, rizzo).invoke([TextBlock(content="guarda"), media])
    assert cloud.sent == [] and rizzo.calls == []


# --- guasti: zero chiamate al cloud ------------------------------------------

@pytest.mark.parametrize(
    "rizzo, match",
    [
        (FakeRizzo(down=True), "non risponde"),
        (FakeRizzo(status=503), "non risponde"),
        (FakeRizzo(mapping_enabled=False), "modalità definitiva"),
        (FakeRizzo(status=500), "errore"),
    ],
)
def test_service_down_zero_cloud_calls(rizzo, match):
    cloud = FakeCloud(reply="non deve arrivare")
    g = _guard(cloud, rizzo)
    with pytest.raises(PIIGuardBlocked, match=match) as exc:
        g.invoke("Scrivi a Mario Rossi")
    assert cloud.sent == []
    assert _no_values(str(exc.value))  # nessun dato nel messaggio d'errore


def test_stream_service_down_zero_cloud_calls():
    cloud = FakeCloud(chunks=["x"])
    stream = _guard(cloud, FakeRizzo(down=True)).stream_invoke("Scrivi a Mario Rossi")
    with pytest.raises(PIIGuardBlocked):
        next(stream)
    assert cloud.sent == []


def test_timeout_is_down():
    class Slow(FakeRizzo):
        def post(self, url, json=None, **kw):
            raise requests.Timeout("lento")

    cloud = FakeCloud(reply="x")
    with pytest.raises(PIIGuardBlocked, match="non risponde"):
        _guard(cloud, Slow()).invoke("Mario Rossi")
    assert cloud.sent == []


def test_separator_in_user_text_blocks():
    from core.pii_guard import _SEP_MARK

    cloud = FakeCloud(reply="x")
    with pytest.raises(PIIGuardBlocked):
        _guard(cloud).invoke(f"testo con {_SEP_MARK} dentro")
    assert cloud.sent == []


# --- streaming ----------------------------------------------------------------

def _cumulative(pieces):
    out, acc = [], ""
    for p in pieces:
        acc += p
        out.append(acc)
    return out


def _app_deltas(stream):
    """Come app.py: delta calcolati su .text cumulativo."""
    text, previous = "", ""
    for chunk in stream:
        current = chunk.text
        new = current[len(previous):]
        assert current.startswith(previous), "il .text deve essere cumulativo"
        assert "[" not in new or "]" in new  # niente segnaposto a metà
        text += new
        previous = current
    return text


@pytest.mark.parametrize("split", [1, 2, 3, 7])
def test_stream_restored_piece_by_piece(split):
    reply = "Caro [FULLNAME_1], il CF [CF_1] di [FULLNAME_2] è registrato."
    pieces = [reply[i:i + split] for i in range(0, len(reply), split)]
    cloud = FakeCloud(chunks=_cumulative(pieces))
    stream = _guard(cloud).stream_invoke(
        "Scrivi a Mario Rossi del CF RSSMRA80A01H501U di Lucia D'Angelo"
    )
    text = _app_deltas(stream)
    assert text == "Caro Mario Rossi, il CF RSSMRA80A01H501U di Lucia D'Angelo è registrato."
    assert _no_values(cloud.all_sent_text())


def test_stream_with_delta_chunks():
    """Un client che manda delta invece del cumulativo funziona lo stesso."""
    cloud = FakeCloud(chunks=["Ciao [FULL", "NAME_1]", "!"])
    text = _app_deltas(_guard(cloud).stream_invoke("Saluta Mario Rossi"))
    assert text == "Ciao Mario Rossi!"


def test_no_pii_text_passes_unchanged():
    cloud = FakeCloud(reply="42")
    counted = []
    res = _guard(cloud, counted=counted).invoke("Quanto fa 6 per 7?")
    assert cloud.sent[0][1] == "Quanto fa 6 per 7?"
    assert res.text == "42" and counted == [0]


def test_repr_has_no_values():
    cloud = FakeCloud(reply="[FULLNAME_1]")
    res = _guard(cloud).invoke("Mario Rossi")
    assert "Mario Rossi" not in repr(res).replace(res.text, "")
    assert "raw_text" not in repr(res) and "restore" not in repr(res)


# --- la mappa della sessione: ripristino dopo il parsing ---------------------

def test_session_map_restores_after_parsing():
    from ui.socratic.session_map import SessionMapAnalyzer

    reply = (
        "1. FRAME DOMINANTE\n"
        "\"Il cliente [FULLNAME_1] va servito per primo\"\n"
        "2. CONNESSIONE DOMANDE → FRAME\n"
        "1. Prima domanda → parte da [FULLNAME_1]\n"
        "2. Seconda domanda → aggiunge [ORG_1]\n"
        "3. FRAME NON ESPLORATI\n"
        "- E se [FULLNAME_1] non fosse il decisore?\n"
    )
    cloud = FakeCloud(reply=reply)
    g = _guard(cloud)
    messages = [
        {"role": "user", "content": "Che cosa vuole Lucia D'Angelo?"},
        {"role": "assistant", "content": "..."},
        {"role": "user", "content": "E Ferrolago Srl che c'entra?"},
    ]
    smap = SessionMapAnalyzer.analyze(messages, g.invoke, "s1")
    assert _no_values(cloud.all_sent_text())
    assert smap.dominant_frame == "Il cliente Lucia D'Angelo va servito per primo"
    assert smap.entries[0].frame_contribution == "parte da Lucia D'Angelo"
    assert smap.entries[1].frame_contribution == "aggiunge Ferrolago Srl"
    assert smap.unexplored_frames == ["E se Lucia D'Angelo non fosse il decisore?"]


# --- create_client: il guard solo se acceso e fuori casa ---------------------

def _hybrid(enabled):
    from config.hybrid_settings import parse_hybrid_settings

    return parse_hybrid_settings({"pii": {"enabled": enabled}})


def test_create_client_off_is_unchanged():
    from core.llm_client import create_client

    c = create_client("Cloud provider", "OpenAI", "sk-finta", "gpt-4o-mini", "sp", "", 0.7)
    c_off = create_client("Cloud provider", "OpenAI", "sk-finta", "gpt-4o-mini", "sp", "", 0.7,
                          hybrid=_hybrid(False))
    assert not isinstance(c, GuardedClient) and not isinstance(c_off, GuardedClient)
    assert type(c) is type(c_off)


def test_create_client_on_outside_is_guarded():
    from core.llm_client import create_client

    c = create_client("Cloud provider", "OpenAI", "sk-finta", "gpt-4o-mini", "sp", "", 0.7,
                      hybrid=_hybrid(True))
    assert isinstance(c, GuardedClient)


def test_create_client_on_inside_is_not_guarded():
    from core.llm_client import create_client

    c = create_client("Local (Ollama)", None, "", "llama3.2:3b", "sp",
                      "http://localhost:11434/v1", 0.7, hybrid=_hybrid(True))
    assert not isinstance(c, GuardedClient)


# --- metadati: conteggio, mai i valori ----------------------------------------

def test_saved_conversation_has_count_not_values(tmp_path):
    import json
    from unittest.mock import patch

    from core.persistence import save_conversation

    with patch("core.persistence.CONVERSATIONS_DIR", tmp_path):
        save_conversation("g1", "2026-11-06T10:00:00", [], "gpt-4o-mini", "Cloud provider", 0,
                          pii_guard=True, pii_removed=3)
        save_conversation("g2", "2026-11-06T10:00:00", [], "llama3.2:3b", "Local (Ollama)", 0)
    g1 = json.loads((tmp_path / "conv_g1.json").read_text(encoding="utf-8"))
    g2 = json.loads((tmp_path / "conv_g2.json").read_text(encoding="utf-8"))
    assert g1["pii_guard"] is True and g1["pii_removed"] == 3
    assert "pii_guard" not in g2 and "pii_removed" not in g2  # guard mai usato: come la 1.15.4
