# tests/test_pii_session_memory.py
# DeepAiUG v1.16.0 (giro 7b) — I valori già tolti si tolgono sempre.
# ============================================================================
# Il caso della prova dei casi di Giacomo: «Limiti» rimanda al cloud il testo
# del modello, con «**Paolo**» in grassetto e «Moglie di Paolo»; rizzo-pii,
# alla seconda passata, non riconosce «Paolo». Con la memoria della sessione
# nessun valore vero esce e la numerazione resta quella del primo turno.
# rizzo-pii, cloud FINTI; conversazioni in tmp_path; dati inventati.
# ============================================================================

import re

import pytest
from streamlit.testing.v1 import AppTest

from core.pii_client import PIIClient
from core.pii_guard import GuardedClient
from core.pii_memory import PIISessionMemory
from tests.fakes_http import FakeResponse
from tests.test_pii_guard import FakeCloud


class SelectiveRizzo:
    """rizzo-pii finto che riconosce, a ogni chiamata, solo i valori dati."""

    def __init__(self, labels):
        self.labels = labels          # valore → etichetta
        self.recognize = list(labels)  # cosa riconosce alla prossima chiamata
        self.calls = []

    def get(self, url, **kw):
        return FakeResponse(200, {"model_loaded": True})

    def post(self, url, json=None, **kw):
        self.calls.append(json["text"])
        text = json["text"].strip()
        found = sorted((m.start(), v) for v in sorted(self.recognize, key=len, reverse=True)
                       for m in re.finditer(rf"(?<!\w){re.escape(v)}(?!\w)", text))
        seen, counters = {}, {}
        for _, v in found:
            if v not in seen:
                lab = self.labels[v]
                counters[lab] = counters.get(lab, 0) + 1
                seen[v] = f"[{lab}_{counters[lab]}]"
        # come rizzo-pii: i più lunghi prima
        for v in sorted(seen, key=len, reverse=True):
            text = re.sub(rf"(?<!\w){re.escape(v)}(?!\w)", seen[v], text)
        return FakeResponse(200, {"anonymized_text": text, "mapping": {p: v for v, p in seen.items()},
                                  "mapping_enabled": True, "n_entities": len(seen), "by_label": counters})


LABELS = {"Paolo Rossi": "FULLNAME", "Paolo": "FULLNAME", "Anna Bianchi": "FULLNAME",
          "Luca Verdi": "FULLNAME", "RSSMRA80A01H501U": "CF"}


def _guard(cloud, rizzo, memory):
    return GuardedClient(client_factory=cloud.factory, system_prompt="Sei un assistente.",
                         pii=PIIClient(session=rizzo), memory=memory)


def _turn1(memory, rizzo):
    cloud = FakeCloud(reply="Scrivo a [FULLNAME_1] e a [FULLNAME_2].")
    rizzo.recognize = ["Anna Bianchi", "Paolo"]
    res = _guard(cloud, rizzo, memory).invoke("Mia moglie è Anna Bianchi, mio figlio si chiama Paolo.")
    return cloud, res


def test_second_pass_covers_values_rizzo_misses():
    memory, rizzo = PIISessionMemory(), SelectiveRizzo(LABELS)
    cloud1, res1 = _turn1(memory, rizzo)
    assert res1.text == "Scrivo a Anna Bianchi e a Paolo."
    sent1 = cloud1.all_sent_text()
    ph_paolo = "[FULLNAME_2]" if "si chiama [FULLNAME_2]" in sent1 else "[FULLNAME_1]"

    # «Limiti»: il testo del modello, ripristinato; rizzo-pii non riconosce più niente
    rizzo.recognize = []
    cloud2 = FakeCloud(reply=f"Il limite riguarda {ph_paolo}.")
    risposta = "Per **Paolo** serve tempo. Moglie di Paolo: Anna Bianchi."
    res2 = _guard(cloud2, rizzo, memory).invoke(risposta)
    sent2 = cloud2.all_sent_text()
    assert "Paolo" not in sent2 and "Anna Bianchi" not in sent2  # nessun valore vero
    assert f"**{ph_paolo}**" in sent2 and f"Moglie di {ph_paolo}" in sent2  # stesso segnaposto
    assert res2.text == "Il limite riguarda Paolo."  # ripristino con la tabella unita
    assert res2.pii_removed == 2


def test_new_values_renumbered_after_known():
    memory, rizzo = PIISessionMemory(), SelectiveRizzo(LABELS)
    _turn1(memory, rizzo)  # FULLNAME_1 e FULLNAME_2 occupati
    rizzo.recognize = ["Luca Verdi"]  # rizzo-pii lo chiamerebbe [FULLNAME_1]
    cloud = FakeCloud(reply="Ciao [FULLNAME_3], saluta [FULLNAME_1].")
    res = _guard(cloud, rizzo, memory).invoke("Scrivi a Luca Verdi e ad Anna Bianchi.")
    sent = cloud.all_sent_text()
    assert "Scrivi a [FULLNAME_3] e ad [FULLNAME_1]." in sent
    assert res.text == "Ciao Luca Verdi, saluta Anna Bianchi."


def test_longest_first_and_word_boundary():
    memory, rizzo = PIISessionMemory(), SelectiveRizzo(LABELS)
    rizzo.recognize = ["Paolo Rossi", "Paolo"]
    _guard(FakeCloud(reply="ok"), rizzo, memory).invoke("Paolo Rossi e suo figlio Paolo.")
    rizzo.recognize = []
    cloud = FakeCloud(reply="ok")
    _guard(cloud, rizzo, memory).invoke("Paolo Rossi, Paolo e il Paolone del bar.")
    sent = cloud.all_sent_text()
    assert "Paolone" in sent  # confine di parola: non si tocca
    assert "Paolo " not in sent and "Paolo," not in sent
    ph_full, ph_short = memory._by_value["Paolo Rossi"], memory._by_value["Paolo"]
    assert f"{ph_full}, {ph_short} e il Paolone" in sent


def test_no_invented_association():
    """«Paolo» da solo non si copre se rizzo-pii ha tolto solo «Paolo Rossi»."""
    memory, rizzo = PIISessionMemory(), SelectiveRizzo(LABELS)
    rizzo.recognize = ["Paolo Rossi"]
    _guard(FakeCloud(reply="ok"), rizzo, memory).invoke("Scrivi a Paolo Rossi.")
    rizzo.recognize = []
    cloud = FakeCloud(reply="ok")
    _guard(cloud, rizzo, memory).invoke("Paolo ha risposto. Paolo Rossi no.")
    sent = cloud.all_sent_text()
    assert "Paolo ha risposto" in sent and "[FULLNAME_1] no." in sent


def test_existing_placeholders_untouched():
    memory, rizzo = PIISessionMemory(), SelectiveRizzo(LABELS)
    rizzo.recognize = ["Paolo"]
    _guard(FakeCloud(reply="ok"), rizzo, memory).invoke("Mio figlio Paolo.")
    rizzo.recognize = []
    cloud = FakeCloud(reply="ok")
    _guard(cloud, rizzo, memory).invoke("Il campo [CF_7] resta, Paolo no.")
    sent = cloud.all_sent_text()
    assert "[CF_7] resta, [FULLNAME_1] no." in sent


def test_memory_repr_has_no_values():
    memory, rizzo = PIISessionMemory(), SelectiveRizzo(LABELS)
    _turn1(memory, rizzo)
    assert "Paolo" not in repr(memory) and "Anna" not in str(memory)
    assert len(memory) == 2
    memory.clear()
    assert len(memory) == 0


def test_rizzo_mangles_a_mark_blocks():
    from core.pii_guard import PIIGuardBlocked

    class Mangler(SelectiveRizzo):
        def post(self, url, json=None, **kw):
            r = super().post(url, json=json, **kw)
            r._body["anonymized_text"] = r._body["anonymized_text"].replace("⟦DEEPAIUG·NOTO·1⟧", "")
            return r

    memory, rizzo = PIISessionMemory(), SelectiveRizzo(LABELS)
    _turn1(memory, rizzo)
    bad = Mangler(LABELS)
    bad.recognize = []
    cloud = FakeCloud(reply="ok")
    with pytest.raises(PIIGuardBlocked, match="non coerente"):
        _guard(cloud, bad, memory).invoke("Moglie di Paolo.")
    assert cloud.sent == []


# --- l'app intera: «Nuova» azzera, niente nei file ---------------------------------

def test_app_memory_reset_and_not_saved(monkeypatch, tmp_path):
    import config.hybrid_settings as hs
    import core.llm_client as llm
    import core.pii_client as pc

    monkeypatch.setattr("core.persistence.CONVERSATIONS_DIR", tmp_path)
    monkeypatch.setattr("ui.sidebar.llm_config.load_api_key", lambda *a, **k: "", raising=False)
    monkeypatch.setattr(hs, "load_hybrid_settings", lambda *a, **k: hs.parse_hybrid_settings({"pii": {"enabled": True}}))
    rizzo = SelectiveRizzo(LABELS)
    rizzo.recognize = ["Anna Bianchi", "Paolo"]
    real = pc.PIIClient
    monkeypatch.setattr(pc, "PIIClient", lambda url, timeout=30: real(url, timeout, session=rizzo))

    class Cloud:
        def invoke(self, x):
            return type("R", (), {"text": "ok"})()

        def stream_invoke(self, x):
            yield type("C", (), {"text": "Saluta [FULLNAME_1]."})()

    monkeypatch.setattr(llm, "_create_raw_client", lambda *a, **k: Cloud())
    at = AppTest.from_file("app.py", default_timeout=120)
    at.session_state["connection_type"] = "Cloud provider"
    at.run()
    [k for k in at.sidebar.text_input if "API Key" in k.label][0].set_value("sk-finta-per-test").run()
    at.text_area(key="msg_input").set_value("Mia moglie è Anna Bianchi, mio figlio Paolo.")
    at.button(key="FormSubmitter:msg_form-🚀 Invia").click().run()
    assert not at.exception, at.exception

    assert len(at.session_state["_pii_memory"]) == 2
    raw = next(tmp_path.glob("conv_*.json")).read_text(encoding="utf-8")
    assert "[FULLNAME_" not in raw and "_pii_memory" not in raw and "PIISessionMemory" not in raw

    at.button[[b.label for b in at.button].index("🔄 Nuova")].click().run()
    assert not at.exception, at.exception
    assert "_pii_memory" not in at.session_state or len(at.session_state["_pii_memory"]) == 0
