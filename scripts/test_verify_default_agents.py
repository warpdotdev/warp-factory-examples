#!/usr/bin/env python3
"""Regression tests for verify_default_agents.py.

Run with:
    python3 scripts/test_verify_default_agents.py

These exercise the script as a subprocess (its actual interface), against
throwaway git repositories built as fixtures -- no network access and no
dependency on a real warp-server checkout.
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify_default_agents as vdr  # noqa: E402

SCRIPT = Path(__file__).resolve().parent / "verify_default_agents.py"


def make_seeds_go(foreman_model: str) -> str:
    # Mirrors the shape of warp-server's seeds.go. warp-server declares these
    # inside SeedRoster(); the identifier is irrelevant here because the
    # parser anchors on each entry's Role: field, never on the name.
    return f'''package defaults

var defaultAgents = []SeedAgent{{
\t{{
\t\tName:        "X Foreman Agent",
\t\tRole:        enums.ForemanAgentType,
\t\tDescription: "Orchestrates the factory workflow and dispatches each gated step.",
\t\tModel:       "{foreman_model}",
\t\tPrompt:      foremanPrompt,
\t}},
\t{{
\t\tName:        "X Triage Agent",
\t\tRole:        enums.TriageAgentType,
\t\tDescription: "Triages requests and establishes task state.",
\t\tModel:       "grok-4-5-high",
\t\tPrompt:      triagePrompt,
\t}},
\t{{
\t\tName:        "X Spec Agent",
\t\tRole:        enums.SpecAgentType,
\t\tDescription: "Writes and drives approval of specifications.",
\t\tModel:       "gpt-5-6-sol-high",
\t\tPrompt:      specPrompt,
\t}},
\t{{
\t\tName:        "X Implement Agent",
\t\tRole:        enums.ImplementAgentType,
\t\tDescription: "Implements, validates, and updates code changes.",
\t\tModel:       "auto-genius",
\t\tPrompt:      implementPrompt,
\t}},
\t{{
\t\tName:        "X Review Agent",
\t\tRole:        enums.ReviewAgentType,
\t\tDescription: "Reviews factory pull requests and routes findings to rework or human resolution.",
\t\tModel:       "gpt-5-6-terra-high",
\t\tPrompt:      reviewPrompt,
\t}},
}}
'''


PROMPT_TEMPLATES = {
    "foreman.md": "# Foreman\n\nOrchestrate the factory.\n",
    "triage.md": "# Triage\n\nTriage requests.\n",
    "spec.md": "# Spec\n\nWrite specs.\n",
    "implement.md": "# Implementation\n\nImplement the change.\n",
    "review.md": "# Review\n\nReview the change.\n",
}


def write_warp_server_fixture(root: Path, foreman_model: str) -> str:
    """Writes a minimal defaults tree and commits it. Returns the commit SHA."""
    defaults = root / vdr.DEFAULTS_ROOT
    (defaults / "prompts").mkdir(parents=True)
    (defaults / "seeds.go").write_text(make_seeds_go(foreman_model))
    for name, body in PROMPT_TEMPLATES.items():
        (defaults / "prompts" / name).write_text(body)
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    subprocess.run(["git", "add", "-A"], cwd=root, check=True)
    subprocess.run(
        ["git", "-c", "user.email=test@example.com", "-c", "user.name=test",
         "commit", "-q", "-m", "seed"],
        cwd=root,
        check=True,
    )
    sha = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=root, capture_output=True, text=True, check=True
    ).stdout.strip()
    return sha


def write_matching_example(root: Path, seeds_go: str) -> None:
    """Writes an examples/00-style tree that matches `seeds_go` and
    PROMPT_TEMPLATES exactly, by construction (via the module's own render
    helpers), so tests can isolate the ref-pinning behavior from the
    content-diffing behavior."""
    seeds = vdr.parse_seeds(seeds_go)
    for role_prefix, dirname, agent_type, template_file in vdr.ROLES:
        description, model = seeds[role_prefix]
        body = vdr.render_expected_prompt(
            PROMPT_TEMPLATES[template_file], is_foreman=(dirname == "foreman")
        )
        agent_dir = root / "agents" / dirname
        agent_dir.mkdir(parents=True)
        (agent_dir / "agent.md").write_text(
            f"---\ndescription: {description}\nagentType: {agent_type}\nmodel: {model}\n---\n{body}\n"
        )


def run_script(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args], capture_output=True, text=True
    )


class VerifyDefaultAgentsTest(unittest.TestCase):
    def test_matching_checkout_and_tree_passes(self):
        with tempfile.TemporaryDirectory() as ws, tempfile.TemporaryDirectory() as ex:
            ws_root, ex_root = Path(ws), Path(ex) / "00"
            sha = write_warp_server_fixture(ws_root, foreman_model="claude-5-opus-high")
            write_matching_example(ex_root, make_seeds_go("claude-5-opus-high"))

            result = run_script("--warp-server", str(ws_root), "--example", str(ex_root), "--ref", sha)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("OK", result.stdout)
            self.assertIn(sha, result.stdout)

    def test_diverged_tree_at_the_right_commit_fails_with_diagnostics(self):
        with tempfile.TemporaryDirectory() as ws, tempfile.TemporaryDirectory() as ex:
            ws_root, ex_root = Path(ws), Path(ex) / "00"
            sha = write_warp_server_fixture(ws_root, foreman_model="claude-5-opus-high")
            write_matching_example(ex_root, make_seeds_go("claude-5-opus-high"))
            # Mutate the tree only -- the checkout is still at the right commit.
            agent_path = ex_root / "agents" / "foreman" / "agent.md"
            agent_path.write_text(agent_path.read_text().replace("claude-5-opus-high", "claude-4-opus"))

            result = run_script("--warp-server", str(ws_root), "--example", str(ex_root), "--ref", sha)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("DIVERGED", result.stdout)
            self.assertIn("foreman", result.stdout)

    def test_checkout_on_the_wrong_commit_is_not_verified_even_if_tree_matches_it(self):
        """Regression: a local checkout that isn't on the requested ref must
        never be certified as a match, even when the example tree happens to
        agree with whatever that checkout currently contains."""
        with tempfile.TemporaryDirectory() as ws, tempfile.TemporaryDirectory() as ex:
            ws_root, ex_root = Path(ws), Path(ex) / "00"
            # The checkout has moved on to a different model than the pinned
            # ref names, and the tree was (wrongly) updated to match it.
            changed_seeds_go = make_seeds_go("claude-9000-opus")
            actual_head = write_warp_server_fixture(ws_root, foreman_model="claude-9000-opus")
            write_matching_example(ex_root, changed_seeds_go)
            pinned_ref = "0" * 40  # deliberately not actual_head

            result = run_script(
                "--warp-server", str(ws_root), "--example", str(ex_root), "--ref", pinned_ref
            )
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            self.assertIn("NOT VERIFIED", result.stderr)
            self.assertIn(actual_head, result.stderr)
            self.assertIn(pinned_ref, result.stderr)
            # Must not claim a pass anywhere in stdout.
            self.assertNotIn("OK", result.stdout)

    def test_non_git_directory_is_not_verified(self):
        with tempfile.TemporaryDirectory() as ws, tempfile.TemporaryDirectory() as ex:
            ws_root, ex_root = Path(ws), Path(ex) / "00"
            defaults = ws_root / vdr.DEFAULTS_ROOT / "prompts"
            defaults.mkdir(parents=True)
            (ws_root / vdr.DEFAULTS_ROOT / "seeds.go").write_text(make_seeds_go("claude-5-opus-high"))
            for name, body in PROMPT_TEMPLATES.items():
                (defaults / name).write_text(body)
            write_matching_example(ex_root, make_seeds_go("claude-5-opus-high"))
            # No `git init` -- ws_root is a plain directory, not a checkout.

            result = run_script("--warp-server", str(ws_root), "--example", str(ex_root))
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            self.assertIn("NOT VERIFIED", result.stderr)


if __name__ == "__main__":
    unittest.main()
