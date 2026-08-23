#!/usr/bin/env python3
"""Regression tests for check_conventions.py.

A checker that passes but cannot fail is worthless, so every rule here gets a
fixture that violates it and must be reported. The clean fixture guards the
other direction: the rules must not fire on correct content.

Run with:
    python3 scripts/test_check_conventions.py
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "check_conventions.py"

FOREMAN = """---
description: Routes work.
agentType: FOREMAN
---
# Foreman

Route the work.
"""

RUNNER = """description: Standard runner.
instanceShape:
  vcpus: 4
  memoryGb: 8
platform:
  os: linux
  arch: x86_64
  linux:
    dockerImage: ubuntu:24.04
"""

FACTORY = """schemaVersion: v1alpha1
name: fixture
repositories:
  - owner: acme
    name: api-service
agentDefaults:
  model: auto
  runner: linux-standard
"""


def write_clean_example(root: Path) -> Path:
    example = root / "examples" / "00-fixture"
    (example / "agents" / "foreman").mkdir(parents=True)
    (example / "runners").mkdir(parents=True)
    (example / "factory.yaml").write_text(FACTORY)
    (example / "agents" / "foreman" / "agent.md").write_text(FOREMAN)
    (example / "runners" / "linux-standard.yaml").write_text(RUNNER)
    return example


def run_checker(root: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(root)],
        capture_output=True,
        text=True,
    )


class CheckConventionsTest(unittest.TestCase):
    def test_clean_tree_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_clean_example(root)
            result = run_checker(root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("Conventions OK", result.stdout)

    def test_unresolved_runner_reference_is_caught(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            example = write_clean_example(root)
            (example / "factory.yaml").write_text(
                FACTORY.replace("runner: linux-standard", "runner: does-not-exist")
            )
            result = run_checker(root)
            self.assertEqual(result.returncode, 1, result.stdout)
            self.assertIn("does-not-exist", result.stdout)

    def test_scorer_naming_a_missing_agent_is_caught(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            example = write_clean_example(root)
            scorer = example / "scorers" / "quality"
            scorer.mkdir(parents=True)
            (scorer / "scorer.md").write_text(
                "---\nagents:\n  - ghost\nlabels:\n  - value: ok\n    score: 1\n"
                "passingScore: 1\nmodel: claude-4-5-haiku\n---\nRubric.\n"
            )
            result = run_checker(root)
            self.assertEqual(result.returncode, 1, result.stdout)
            self.assertIn("ghost", result.stdout)

    def test_missing_and_duplicate_foreman_are_caught(self):
        for agent_type, expected in (("IMPLEMENT", "found 0"), ("FOREMAN", "found 2")):
            with self.subTest(agent_type=agent_type):
                with tempfile.TemporaryDirectory() as tmp:
                    root = Path(tmp)
                    example = write_clean_example(root)
                    second = example / "agents" / "other"
                    second.mkdir(parents=True)
                    if agent_type == "IMPLEMENT":
                        # Demote the only foreman.
                        (example / "agents" / "foreman" / "agent.md").write_text(
                            FOREMAN.replace("agentType: FOREMAN", "agentType: IMPLEMENT")
                        )
                        (second / "agent.md").write_text(
                            FOREMAN.replace("agentType: FOREMAN", "agentType: REVIEW")
                        )
                    else:
                        (second / "agent.md").write_text(FOREMAN)
                    result = run_checker(root)
                    self.assertEqual(result.returncode, 1, result.stdout)
                    self.assertIn(expected, result.stdout)

    def test_dangling_example_link_is_caught(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_clean_example(root)
            (root / "README.md").write_text("See examples/99-does-not-exist for more.\n")
            result = run_checker(root)
            self.assertEqual(result.returncode, 1, result.stdout)
            self.assertIn("99-does-not-exist", result.stdout)

    def test_retired_terminology_is_caught(self):
        cases = {
            "roster": "The default agents roster is fixed.\n",
            "agent set": "This mirrors the default agent set.\n",
            "Oz": "The Oz harness runs this agent.\n",
            "Warp Factory": "# Warp Factory examples\n",
            "bare Factory": "Each Factory declares a foreman mid-sentence.\n",
        }
        for label, text in cases.items():
            with self.subTest(case=label):
                with tempfile.TemporaryDirectory() as tmp:
                    root = Path(tmp)
                    write_clean_example(root)
                    (root / "README.md").write_text(text)
                    result = run_checker(root)
                    self.assertEqual(result.returncode, 1, f"{label}: {result.stdout}")

    def test_allowed_oz_usages_do_not_fire(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_clean_example(root)
            (root / "README.md").write_text(
                "Create the secret:\n\n```bash\noz secret create claude api-key KEY\n```\n\n"
                "The harness value is `type: oz` in YAML.\n"
                "Warp Factories is the product; your factory is an instance.\n"
            )
            result = run_checker(root)
            self.assertEqual(result.returncode, 0, result.stdout)

    def test_terminology_fence_suppresses_within_its_block(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_clean_example(root)
            (root / "README.md").write_text(
                "<!-- terminology-allow-begin -->\n"
                'Never say "roster"; the term is "the default agents".\n'
                "<!-- terminology-allow-end -->\n"
            )
            self.assertEqual(run_checker(root).returncode, 0)

            # ...and stops suppressing after the fence closes.
            (root / "README.md").write_text(
                "<!-- terminology-allow-begin -->\n"
                'Never say "roster".\n'
                "<!-- terminology-allow-end -->\n"
                "The agent roster is fixed.\n"
            )
            result = run_checker(root)
            self.assertEqual(result.returncode, 1, result.stdout)
            self.assertIn("README.md:4", result.stdout)


if __name__ == "__main__":
    unittest.main()
