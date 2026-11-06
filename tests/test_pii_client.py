# tests/test_pii_client.py
# DeepAiUG v1.16.0 (giro 1) — Test del client rizzo-pii con il servizio SIMULATO.
# Tutti i dati sono inventati (Mario Rossi, codice fiscale e IBAN finti).
# ============================================================================

import unittest

import requests

from core.pii_client import (
    AnonymizedText,
    PIIClient,
    PIIMappingDisabled,
    PIINotLocal,
    PIIServiceError,
    PIIServiceUnavailable,
    StreamRestorer,
    restore_placeholders,
)
from tests.fakes_http import FakeResponse, FakeSession, connection_refused

# Dati inventati
NOME = "Mario Rossi"
CF = "RSSMRA80A01H501U"
IBAN = "IT60X0542811101000000123456"
TESTO = f"{NOME}, codice fiscale {CF}, IBAN {IBAN}, chiede un preventivo per 200 flange."
ANON = "[FULLNAME_1], codice fiscale [CF_1], IBAN [IBAN_1], chiede un preventivo per 200 flange."
MAPPING = {"[FULLNAME_1]": NOME, "[CF_1]": CF, "[IBAN_1]": IBAN}

HEALTH_OK = {
    "status": "ok", "model_loaded": True, "model": "rizzo-pii-0.3B",
    "model_version": "x", "app_version": "2.0.0", "device": "cpu",
    "tags": 25, "excluded_tags": [], "mapping_enabled": True,
}


def analyze_ok(mapping_enabled=True):
    return FakeResponse(200, {
        "anonymized_text": ANON,
        "mapping": MAPPING if mapping_enabled else {},
        "mapping_enabled": mapping_enabled,
        "n_entities": 3,
        "by_label": {"FULLNAME": 1, "CF": 1, "IBAN": 1},
    })


class TestLoopbackOnly(unittest.TestCase):
    def test_default_url_ok(self):
        PIIClient(session=FakeSession())

    def test_localhost_and_ipv6_ok(self):
        PIIClient("http://localhost:5005", session=FakeSession())
        PIIClient("http://[::1]:5005", session=FakeSession())

    def test_remote_refused(self):
        for url in ("http://192.168.1.10:5005", "https://pii.example.com", "http://0.0.0.0:5005"):
            with self.assertRaises(PIINotLocal, msg=url):
                PIIClient(url, session=FakeSession())


class TestHealth(unittest.TestCase):
    def test_ready(self):
        s = FakeSession({("get", "/health"): FakeResponse(200, HEALTH_OK)})
        h = PIIClient(session=s).health()
        self.assertTrue(h.ready)
        self.assertEqual(h.app_version, "2.0.0")
        self.assertTrue(PIIClient(session=s).is_ready())

    def test_loading_503_is_not_ready(self):
        body = dict(HEALTH_OK, status="loading", model_loaded=False)
        s = FakeSession({("get", "/health"): FakeResponse(503, body)})
        self.assertFalse(PIIClient(session=s).health().ready)

    def test_down(self):
        s = FakeSession({("get", "/health"): connection_refused()})
        with self.assertRaises(PIIServiceUnavailable):
            PIIClient(session=s).health()
        self.assertFalse(PIIClient(session=s).is_ready())

    def test_timeout(self):
        s = FakeSession({("get", "/health"): requests.Timeout("lento")})
        self.assertFalse(PIIClient(session=s).is_ready())


class TestAnonymize(unittest.TestCase):
    def test_ok_and_payload(self):
        s = FakeSession({("post", "/analyze"): analyze_ok()})
        out = PIIClient(session=s).anonymize(TESTO)
        self.assertEqual(out.text, ANON)
        self.assertEqual(out.n_entities, 3)
        self.assertTrue(out.changed)
        sent = s.calls[0]["json"]
        self.assertEqual(sent["text"], TESTO)
        self.assertTrue(sent["include_mapping"])
        self.assertNotIn("exclude_tags", sent)

    def test_exclude_tags_forwarded(self):
        s = FakeSession({("post", "/analyze"): analyze_ok()})
        PIIClient(session=s).anonymize(TESTO, exclude_tags=["AMOUNT"])
        self.assertEqual(s.calls[0]["json"]["exclude_tags"], ["AMOUNT"])

    def test_no_values_in_anonymized_text(self):
        s = FakeSession({("post", "/analyze"): analyze_ok()})
        out = PIIClient(session=s).anonymize(TESTO)
        for v in (NOME, CF, IBAN):
            self.assertNotIn(v, out.text)

    def test_repr_hides_mapping(self):
        s = FakeSession({("post", "/analyze"): analyze_ok()})
        out = PIIClient(session=s).anonymize(TESTO)
        for v in (NOME, CF, IBAN):
            self.assertNotIn(v, repr(out))

    def test_empty_text_no_call(self):
        s = FakeSession()
        out = PIIClient(session=s).anonymize("   ")
        self.assertEqual(s.calls, [])
        self.assertFalse(out.changed)

    def test_down_raises(self):
        s = FakeSession({("post", "/analyze"): connection_refused()})
        with self.assertRaises(PIIServiceUnavailable):
            PIIClient(session=s).anonymize(TESTO)

    def test_model_loading_raises_unavailable(self):
        s = FakeSession({("post", "/analyze"): FakeResponse(503, {"error": "loading"})})
        with self.assertRaises(PIIServiceUnavailable):
            PIIClient(session=s).anonymize(TESTO)

    def test_http_error(self):
        s = FakeSession({("post", "/analyze"): FakeResponse(400, {"error": "x"})})
        with self.assertRaises(PIIServiceError):
            PIIClient(session=s).anonymize(TESTO)

    def test_bad_json(self):
        s = FakeSession({("post", "/analyze"): FakeResponse(200, raw="<html>")})
        with self.assertRaises(PIIServiceError):
            PIIClient(session=s).anonymize(TESTO)

    def test_missing_anonymized_text(self):
        s = FakeSession({("post", "/analyze"): FakeResponse(200, {"mapping": {}})})
        with self.assertRaises(PIIServiceError):
            PIIClient(session=s).anonymize(TESTO)

    def test_mapping_disabled_raises(self):
        s = FakeSession({("post", "/analyze"): analyze_ok(mapping_enabled=False)})
        with self.assertRaises(PIIMappingDisabled):
            PIIClient(session=s).anonymize(TESTO)

    def test_mapping_disabled_allowed_if_not_required(self):
        s = FakeSession({("post", "/analyze"): analyze_ok(mapping_enabled=False)})
        out = PIIClient(session=s).anonymize(TESTO, require_mapping=False)
        self.assertEqual(out.text, ANON)
        self.assertEqual(out.mapping, {})


class TestRestore(unittest.TestCase):
    def test_roundtrip(self):
        risposta = "Il cliente [FULLNAME_1] (CF [CF_1]) paga su [IBAN_1]."
        self.assertEqual(
            restore_placeholders(risposta, MAPPING),
            f"Il cliente {NOME} (CF {CF}) paga su {IBAN}.",
        )

    def test_bare_and_spaced_forms(self):
        self.assertEqual(restore_placeholders("Gentile FULLNAME_1,", MAPPING), f"Gentile {NOME},")
        self.assertEqual(restore_placeholders("[ CF_1 ]", MAPPING), CF)

    def test_invented_index_not_restored(self):
        # il modello inventa [CF_12]: deve restare visibile, non diventare CF_1
        self.assertEqual(restore_placeholders("[CF_12] e CF_12", MAPPING), "[CF_12] e CF_12")

    def test_no_word_glue(self):
        self.assertEqual(restore_placeholders("ilCF_1", MAPPING), "ilCF_1")
        self.assertEqual(restore_placeholders("CF_1è", MAPPING), "CF_1è")

    def test_single_pass_no_second_order(self):
        mapping = {"[ORG_1]": "Studio CF_2 Srl", "[CF_2]": "XXXYYY00A00A000A"}
        self.assertEqual(restore_placeholders("[ORG_1]", mapping), "Studio CF_2 Srl")

    def test_ten_vs_one(self):
        mapping = {"[FULLNAME_1]": "Mario Rossi", "[FULLNAME_10]": "Lucia Bianchi"}
        self.assertEqual(
            restore_placeholders("[FULLNAME_10] e [FULLNAME_1]", mapping),
            "Lucia Bianchi e Mario Rossi",
        )

    def test_markdown_bold(self):
        self.assertEqual(restore_placeholders("**[FULLNAME_1]**", MAPPING), f"**{NOME}**")

    def test_empty(self):
        self.assertEqual(restore_placeholders("", MAPPING), "")
        self.assertEqual(restore_placeholders("ciao [CF_1]", {}), "ciao [CF_1]")

    def test_anonymized_text_restore(self):
        a = AnonymizedText(text=ANON, mapping=MAPPING, n_entities=3)
        self.assertEqual(a.restore("Ciao [FULLNAME_1]"), f"Ciao {NOME}")


class TestStreamRestorer(unittest.TestCase):
    def _run(self, pezzi, mapping=MAPPING):
        r = StreamRestorer(mapping)
        out = "".join(r.push(p) for p in pezzi)
        return out + r.flush()

    def test_split_bracket_placeholder(self):
        self.assertEqual(self._run(["Il cliente [FULLN", "AME_1] chiede"]), f"Il cliente {NOME} chiede")

    def test_split_bare_placeholder(self):
        self.assertEqual(self._run(["Gentile FULL", "NAME_1, ecco"]), f"Gentile {NOME}, ecco")

    def test_one_char_at_a_time(self):
        risposta = "Cliente [FULLNAME_1], CF [CF_1], IBAN [IBAN_1]."
        atteso = f"Cliente {NOME}, CF {CF}, IBAN {IBAN}."
        self.assertEqual(self._run(list(risposta)), atteso)

    def test_never_emits_partial_placeholder(self):
        r = StreamRestorer(MAPPING)
        self.assertEqual(r.push("Ciao [CF"), "Ciao ")
        self.assertEqual(r.push("_1] ok"), f"{CF} ok")

    def test_unclosed_bracket_flushed(self):
        self.assertEqual(self._run(["vedi [nota"]), "vedi [nota")

    def test_no_mapping_passthrough(self):
        r = StreamRestorer({})
        self.assertEqual(r.push("[CF"), "[CF")


if __name__ == "__main__":
    unittest.main()
