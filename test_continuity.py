import unittest

from continuity import render


class Continuity(unittest.TestCase):
    def test_rework_result_does_not_promote_previous_delivery(self):
        text = render({"continuity": dict(version=1, state="repair", review="repair",
                      rework=dict(previous_commit="abc123", previous_review="repair",
                                  state="accepted", review="accept"))})
        self.assertIn("上次交付/审核：abc123，要求返工", text)
        self.assertIn("本次返工：审核通过", text)

    def test_only_verified_session_actions_are_offered(self):
        for focus, resume in ((False, False), (True, False), (False, True)):
            text = render({"continuity": dict(version=1, session=dict(records=True, focus=focus, resume=resume))})
            self.assertIn("--action records", text)
            self.assertEqual("--action focus" in text, focus)
            self.assertEqual("--action resume" in text, resume)
    def test_old_backend_silent(self):
        self.assertEqual(render({"result": {"task": {}}}), "")

    def test_decision_and_delivery(self):
        c = {"version": 1, "state": "decision", "decision": {
            "question": "Start?", "options": [["Wait", "No dispatch"]]}}
        self.assertIn("Wait: No dispatch", render({"result": {"continuity": c}}))
        c.update(state="awaiting_review", decision=None, delivered=True)
        result = render({"continuity": c})
        for phrase in ("已交付待审核", "独立审核：尚无结论", "合并：未登记", "尚无检查回执"):
            self.assertIn(phrase, result)
