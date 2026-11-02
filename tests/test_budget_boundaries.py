"""Invalid numeric limits must stop an evaluation before any transport call."""
import copy
import contextlib
import io
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "evals"))
import run


def config():
    return {"max_calls": 2, "max_generated_tokens": 100, "max_seconds": 5,
            "max_tokens": 20, "judge_max_tokens": 20, "model": "fictional",
            "judge": "fictional-judge", "rates": {"evaluated": [0.4, 1.6], "judge": [1, 5]},
            "budget_usd": 5}


class BudgetBoundaryTests(unittest.TestCase):
    def test_nonfinite_or_nonpositive_money_and_time_are_rejected(self):
        for field in ("budget_usd", "max_seconds"):
            for value in (float("nan"), float("inf"), -float("inf"), 0, -1, True, "5", None):
                with self.subTest(field=field, value=repr(value)), self.assertRaises(ValueError):
                    run.Budget({**config(), field: value})

    def test_call_and_token_caps_are_positive_exact_integers(self):
        for field in ("max_calls", "max_generated_tokens", "max_tokens", "judge_max_tokens"):
            for value in (0, -1, True, 1.5, "10", None):
                with self.subTest(field=field, value=repr(value)), self.assertRaises(ValueError):
                    run.Budget({**config(), field: value})

    def test_nonfinite_negative_or_malformed_rates_are_rejected(self):
        for rates in ([float("nan"), 1], [1, float("inf")], [-1, 1], [True, 1], [1], "free"):
            value = config()
            value["rates"]["evaluated"] = rates
            with self.subTest(rates=repr(rates)), self.assertRaises(ValueError):
                run.Budget(value)

    def test_resumed_spend_cannot_turn_accounting_into_nan_or_negative(self):
        for value in (float("nan"), float("inf"), -1, True, "0.1"):
            receipt = {"nominal_usd": value, "reserved_usd": 1, "max_tokens": 20}
            with self.subTest(value=repr(value)), self.assertRaises(ValueError):
                run.Budget(config(), [receipt])

    def test_valid_observed_spend_is_retained_and_blocks_another_call(self):
        receipt = {"nominal_usd": 7, "reserved_usd": 1, "max_tokens": 20}
        original = copy.deepcopy(receipt)
        budget = run.Budget(config(), [receipt])
        self.assertEqual(budget.spent, 7)
        with tempfile.TemporaryDirectory() as directory, patch.object(run, "call") as call:
            with self.assertRaises(run.BudgetExceeded):
                budget.invoke("evaluated", "fictional", "fictional", Path(directory) / "call.json")
            call.assert_not_called()
        self.assertEqual(receipt, original)

    def test_valid_free_rate_control_can_execute_fake_transport(self):
        value = config()
        value["rates"] = {"evaluated": [0, 0], "judge": [0, 0]}
        result = {"model": "fictional", "text": "fictional output", "input_tokens": 3,
                  "output_tokens": 2, "complete": True, "requested_model_match": True}
        with tempfile.TemporaryDirectory() as directory, patch.object(run, "call", return_value=result) as call:
            budget = run.Budget(value)
            self.assertEqual(budget.invoke("evaluated", "fictional", "fictional", Path(directory) / "call.json"), "fictional output")
            self.assertEqual(budget.spent, 0)
            self.assertEqual(call.call_count, 1)

    def test_cli_refuses_nonfinite_budget_before_creating_a_record(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(run, "call") as call:
            with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as stopped:
                run.main(["--offline-smoke", "--budget-usd", "nan", "--output-root", directory, "--run-id", "fictional"])
            self.assertEqual(stopped.exception.code, 2)
            self.assertEqual(list(Path(directory).iterdir()), [])
            call.assert_not_called()

    def test_invalid_provider_usage_is_preserved_but_not_counted_as_spend(self):
        for name in ("input_tokens", "output_tokens"):
            for value in (-1, True, None):
                result = {"model": "fictional", "text": "fictional output", "input_tokens": 3,
                          "output_tokens": 2, "complete": True, "requested_model_match": True}
                result[name] = value
                with self.subTest(name=name, value=repr(value)), tempfile.TemporaryDirectory() as directory, patch.object(run, "call", return_value=result):
                    path = Path(directory) / "call.json"
                    budget = run.Budget(config())
                    with self.assertRaises(run.ProviderError):
                        budget.invoke("evaluated", "fictional", "fictional", path)
                    import json
                    receipt = json.loads(path.read_text())
                    self.assertEqual(receipt["result"][name], value)
                    self.assertIsNone(receipt["nominal_usd"])
                    self.assertGreaterEqual(budget.spent, 0)


if __name__ == "__main__":
    unittest.main()
