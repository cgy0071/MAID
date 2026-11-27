import unittest

from continuity import render


class Continuity(unittest.TestCase):
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
