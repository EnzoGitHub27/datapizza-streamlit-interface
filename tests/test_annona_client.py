# tests/test_annona_client.py
# DeepAiUG v1.16.0 (giro 1) — Test del client Annona con il demone SIMULATO.
# Le risposte imitano la forma di Annona 0.1.3 (runner/kernel_api.py).
# Dati inventati.
# ============================================================================

import unittest

from core.annona_client import (
    AnnonaClient,
    AnnonaError,
    AnnonaNotLocal,
    AnnonaUnavailable,
    AnnonaUnsupported,
    Placement,
)
from tests.fakes_http import FakeResponse, FakeSession, connection_refused

CF = "RSSMRA80A01H501U"  # inventato

ASK_REDACTED = {
    "response": "Il cliente, Mario Rossi, ha chiesto un preventivo.",
    "iterations": 1,
    "tool_calls": [],
    "placement": {
        "class": "restricted", "outcome": "redacted", "substrate": "local-gpu",
        "reason": "2 identifier(s) replaced by rizzo-pii@http://127.0.0.1:5005",
    },
    "enforced": True,
    "decisions": [{"seq": 26, "kind": "egress", "outcome": "redacted", "class": "internal",
                   "substrate": "local-gpu", "payload_digest": "ab" * 32,
                   "detail": {"labels": {"CF": 1, "FULLNAME": 1}}, "hash": "cd" * 32}],
    "egress": [{"kind": "redacted", "text": "[FULLNAME_1], codice fiscale [CF_1]"}],
    "attachments": {"named": 0, "shown": 0},
    "sealed": "",
    "cancelled": False,
}

ASK_HELD = dict(ASK_REDACTED, response="", placement={
    "class": "restricted", "outcome": "held", "substrate": "",
    "reason": "no permitted substrate is available, and the rule holds rather than downgrades",
}, egress=[])


class TestLoopbackOnly(unittest.TestCase):
    def test_default_ok(self):
        AnnonaClient(session=FakeSession())

    def test_remote_refused(self):
        with self.assertRaises(AnnonaNotLocal):
            AnnonaClient("http://192.168.1.180:7070", session=FakeSession())


class TestReads(unittest.TestCase):
    def test_health(self):
        s = FakeSession({("get", "/health"): FakeResponse(200, {"status": "ok", "service": "annona"})})
        self.assertTrue(AnnonaClient(session=s).is_up())

    def test_down(self):
        s = FakeSession({("get", "/health"): connection_refused()})
        self.assertFalse(AnnonaClient(session=s).is_up())
        with self.assertRaises(AnnonaUnavailable):
            AnnonaClient(session=s).health()

    def test_enforcing(self):
        s = FakeSession({("get", "/api/kernel/status"): FakeResponse(200, {
            "enforcing": True, "substrates": 1, "rules": 3, "held": 1, "decisions": 4})})
        self.assertTrue(AnnonaClient(session=s).is_enforcing())

    def test_not_enforcing_without_policy(self):
        s = FakeSession({("get", "/api/kernel/status"): FakeResponse(200, {
            "enforcing": False, "reason": "no policy file"})})
        self.assertFalse(AnnonaClient(session=s).is_enforcing())

    def test_policy_404_is_unavailable(self):
        s = FakeSession({("get", "/api/kernel/policy"): FakeResponse(404, {"detail": "no policy"})})
        with self.assertRaises(AnnonaUnavailable):
            AnnonaClient(session=s).policy()

    def test_ledger_params(self):
        s = FakeSession({("get", "/api/kernel/ledger"): FakeResponse(200, {
            "path": "x", "total": 2, "shown": 1, "entries": [{"seq": 2, "outcome": "held"}]})})
        entries = AnnonaClient(session=s).ledger(limit=5, held=True, run_id="r1")
        self.assertEqual(entries[0]["outcome"], "held")
        self.assertEqual(s.calls[0]["params"], {"limit": 5, "held": "true", "run_id": "r1"})

    def test_verify(self):
        s = FakeSession({("get", "/api/kernel/ledger/verify"): FakeResponse(200, {
            "path": "x", "ok": True, "entries": 26, "problem": "", "empty": False})})
        v = AnnonaClient(session=s).verify_ledger()
        self.assertTrue(v.ok)
        self.assertEqual(v.entries, 26)

    def test_substrates(self):
        s = FakeSession({("get", "/api/kernel/substrates"): FakeResponse(200, {
            "probed": False, "substrates": [{"id": "local-gpu", "up": True}]})})
        subs = AnnonaClient(session=s).substrates()
        self.assertEqual(subs[0]["id"], "local-gpu")
        self.assertEqual(s.calls[0]["params"], {"probe": "false"})

    def test_bad_json(self):
        s = FakeSession({("get", "/api/kernel/status"): FakeResponse(200, raw="<html>")})
        with self.assertRaises(AnnonaError):
            AnnonaClient(session=s).status()


class TestAsk(unittest.TestCase):
    def test_redacted(self):
        s = FakeSession({("post", "/api/kernel/ask"): FakeResponse(200, ASK_REDACTED)})
        r = AnnonaClient(session=s).ask("Mario Rossi, codice fiscale " + CF, run_id="r1")
        self.assertEqual(r.placement.outcome, "redacted")
        self.assertTrue(r.placement.permitted)
        self.assertFalse(r.held)
        self.assertTrue(r.enforced)
        body = s.calls[0]["json"]
        self.assertEqual(body["max_iterations"], 1)
        self.assertEqual(body["run_id"], "r1")

    def test_held_is_detected_even_with_200(self):
        s = FakeSession({("post", "/api/kernel/ask"): FakeResponse(200, ASK_HELD)})
        r = AnnonaClient(session=s).ask("testo")
        self.assertTrue(r.held)
        self.assertFalse(r.placement.permitted)

    def test_repr_hides_egress(self):
        s = FakeSession({("post", "/api/kernel/ask"): FakeResponse(200, ASK_REDACTED)})
        r = AnnonaClient(session=s).ask("testo")
        self.assertNotIn("[CF_1]", repr(r))

    def test_no_executor_503(self):
        s = FakeSession({("post", "/api/kernel/ask"): FakeResponse(503, {"detail": "no executor"})})
        with self.assertRaises(AnnonaUnavailable):
            AnnonaClient(session=s).ask("testo")

    def test_configuration_409(self):
        s = FakeSession({("post", "/api/kernel/ask"): FakeResponse(409, {"detail": "x"})})
        with self.assertRaises(AnnonaUnavailable):
            AnnonaClient(session=s).ask("testo")

    def test_empty_prompt(self):
        with self.assertRaises(ValueError):
            AnnonaClient(session=FakeSession()).ask("  ")

    def test_long_timeout(self):
        s = FakeSession({("post", "/api/kernel/ask"): FakeResponse(200, ASK_REDACTED)})
        AnnonaClient(session=s).ask("testo")
        self.assertGreaterEqual(s.calls[0]["timeout"], 60)


class TestUnsupported(unittest.TestCase):
    def test_decide_not_available_over_http(self):
        with self.assertRaises(AnnonaUnsupported):
            AnnonaClient(session=FakeSession()).decide("testo", destination="cloud")

    def test_record_not_available_over_http(self):
        with self.assertRaises(AnnonaUnsupported):
            AnnonaClient(session=FakeSession()).record(
                kind="inference", outcome="placed", klass="public", substrate="cloud")


class TestPlacement(unittest.TestCase):
    def test_from_json_none(self):
        self.assertIsNone(Placement.from_json(None))

    def test_permitted(self):
        self.assertTrue(Placement("placed").permitted)
        self.assertTrue(Placement("redacted").permitted)
        for o in ("held", "queued", "brief", "none"):
            self.assertFalse(Placement(o).permitted, o)


if __name__ == "__main__":
    unittest.main()
