#!/usr/bin/env python3
"""Regression tests for the vendored server-validation helper."""
from __future__ import annotations

import contextlib
import io
import json
import tempfile
import unittest
import urllib.error
from pathlib import Path
from unittest import mock

import validate_factory_files as validator

URL = "https://validator.example/api/v1/factory-files/validate"
VALID = b'{"schema_version":"v1alpha1","diagnostics":[]}'


def http_error(code):
    return urllib.error.HTTPError(URL, code, "test response", {}, None)


class ValidatorTest(unittest.TestCase):
    def test_rejected_forwarded_token_retries_once_without_auth(self):
        for code in (401, 403):
            with self.subTest(code=code):
                response = mock.MagicMock()
                response.__enter__.return_value.read.return_value = VALID
                with mock.patch.object(
                    validator.urllib.request, "urlopen",
                    side_effect=[http_error(code), response],
                ) as request, contextlib.redirect_stderr(io.StringIO()) as warning:
                    result = validator._request_json(URL, "synthetic-token", {"files": []})
                self.assertEqual(result["diagnostics"], [])
                first, second = [call.args[0] for call in request.call_args_list]
                self.assertEqual(first.get_header("Authorization"), "Bearer synthetic-token")
                self.assertIsNone(second.get_header("Authorization"))
                self.assertEqual(first.data, second.data)
                self.assertIn("retrying without it", warning.getvalue())

    def test_other_errors_and_unauthenticated_rejection_do_not_retry(self):
        for token, error in (
            ("synthetic-token", http_error(500)),
            (None, http_error(401)),
            ("synthetic-token", OSError("unreachable")),
        ):
            with self.subTest(token=bool(token), error=type(error).__name__):
                with mock.patch.object(
                    validator.urllib.request, "urlopen", side_effect=error,
                ) as request, self.assertRaises(validator.NotValidated):
                    validator._request_json(URL, token, {"files": []})
                self.assertEqual(request.call_count, 1)

    def test_failed_retry_remains_unvalidated(self):
        for retry_error in (http_error(403), OSError("unreachable")):
            with self.subTest(error=type(retry_error).__name__):
                with mock.patch.object(
                    validator.urllib.request, "urlopen",
                    side_effect=[http_error(401), retry_error],
                ) as request, contextlib.redirect_stderr(io.StringIO()):
                    with self.assertRaises(validator.NotValidated):
                        validator._request_json(URL, "synthetic-token", {"files": []})
                self.assertEqual(request.call_count, 2)

    def test_cli_distinguishes_valid_diagnostics_and_not_validated(self):
        outcomes = (
            (validator.Outcome("v1alpha1", []), 0),
            (validator.Outcome("v1alpha1", [validator.Problem("factory.yaml", "bad")]), 1),
            (validator.NotValidated("unreachable"), 2),
        )
        for outcome, code in outcomes:
            with self.subTest(code=code):
                kwargs = {"side_effect": outcome} if isinstance(outcome, Exception) else {
                    "return_value": outcome,
                }
                with mock.patch.object(validator, "validate", **kwargs), mock.patch(
                    "sys.argv", ["validate_factory_files.py", ".", "--json"],
                ), contextlib.redirect_stdout(io.StringIO()) as output:
                    self.assertEqual(validator.main(), code)
                report = json.loads(output.getvalue())
                self.assertEqual(report["validated"], code != 2)
                if code != 2:
                    self.assertEqual(report["valid"], code == 0)
                    self.assertIn("state-dependent apply checks were not run", report["disclosure"])

    def test_collects_complete_inline_blueprint_resource_tree(self):
        root = Path(__file__).resolve().parent.parent / "examples/sdlc-issue-to-pr"
        files, problems = validator.collect_tree(root)
        expected = {"factory.yaml"}
        for pattern in (
            "agents/*/agent.md", "automations/*/automation.md",
            "runners/*.yaml", "scorers/*/scorer.md",
        ):
            expected.update(path.relative_to(root).as_posix() for path in root.glob(pattern))
        self.assertEqual(problems, [])
        self.assertEqual({file["path"] for file in files}, expected)
        self.assertIn("blueprint:\n", next(
            file["content"] for file in files if file["path"] == "factory.yaml"
        ))

    def test_resource_bytes_are_sent_verbatim(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "factory.yaml").write_text("not locally parsed\n")
            with mock.patch.object(validator, "_request_json", return_value={
                "schema_version": "v1alpha1", "diagnostics": [],
            }) as request, mock.patch.dict("os.environ", {}, clear=True):
                validator.validate(root, "https://validator.example")
            self.assertEqual(request.call_args.kwargs["payload"], {
                "files": [{"path": "factory.yaml", "content": "not locally parsed\n"}],
            })


if __name__ == "__main__":
    unittest.main()
