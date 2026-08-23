#!/usr/bin/env python3
"""Verify examples/00-warp-default-agents against warp-server's canonical seeds.

examples/00-warp-default-agents is a snapshot: it copies the product's
default agents (names, roles, descriptions, models, prompts) into files
by hand. `scripts/validate_factory_files.py` catches schema drift in that
tree, but it has no idea the tree is supposed to mirror anything, so it never
catches the snapshot going stale when the product's seed changes. This script
does that second check: it reconstructs each of the five default agents from
warp-server's own source and diffs the result against the committed tree.

The canonical sources, all under warp-server's
`logic/factorysource/defaults/`:
  - `seeds.go`      the five agents' roles, descriptions, and default models.
  - `prompts.go`     the appendix-rendering rule this script reimplements
                     (see `integration_skill_appendix` below) and the
                     go:embed paths for the prompt templates.
  - `prompts/*.md`   the prompt template bodies.

warp-server is private, so this is a local, on-demand check for Warp
maintainers, not a CI step.

Usage:
    python3 verify_default_agents.py --warp-server /path/to/warp-server
    python3 verify_default_agents.py --ref <sha>   # fetches via `gh api`

Exit codes:
    0  reconstructed the default agents and found no divergence.
    1  reconstructed the default agents and found at least one divergence.
    2  could not reconstruct the default agents (source unavailable). Not a pass.
"""
from __future__ import annotations

import argparse
import base64
import json
import re
import subprocess
import sys
from pathlib import Path

# The warp-server commit this example's prompts/descriptions/models were
# snapshotted from.
PINNED_REF = "d7295cefa21526eabb9ae7b007cf78706a8b3ec1"
DEFAULT_REPO = "warpdotdev/warp-server"
DEFAULTS_ROOT = "logic/factorysource/defaults"

# Role -> (enums.<Value>AgentType in seeds.go, this example's agent directory,
# the frontmatter agentType, the embedded prompt template file).
ROLES = [
    ("Foreman", "foreman", "FOREMAN", "foreman.md"),
    ("Triage", "triage", "TRIAGE", "triage.md"),
    ("Spec", "spec", "SPEC", "spec.md"),
    ("Implement", "implement", "IMPLEMENT", "implement.md"),
    ("Review", "review", "REVIEW", "review.md"),
]

# This script only reconstructs the one composition
# examples/00-warp-default-agents documents: GitHub code forge, a tracker
# declared (the appendix line never names which one), Slack communications.
# A tree rendered for a different composition needs a different appendix and
# is out of scope here.
FORGE_SKILL_DIR = "github"
HAS_TRACKER = True
COMMUNICATIONS_IS_SLACK = True


class SourceUnavailable(Exception):
    """Raised when a canonical source file cannot be read at all."""


def read_local(warp_server_root: Path, rel_path: str) -> str:
    path = warp_server_root / rel_path
    try:
        return path.read_text()
    except OSError as exc:
        raise SourceUnavailable(f"could not read {path}: {exc}") from exc


def read_via_gh(repo: str, ref: str, rel_path: str) -> str:
    # The ref goes in the query string, not as a -f/-F flag: gh api switches
    # from GET to POST as soon as any -f/-F is present, which 404s against
    # this GET-only endpoint.
    api_path = f"repos/{repo}/contents/{rel_path}?ref={ref}"
    try:
        proc = subprocess.run(
            ["gh", "api", api_path],
            capture_output=True,
            text=True,
        )
    except FileNotFoundError as exc:
        raise SourceUnavailable("`gh` CLI not found on PATH") from exc
    if proc.returncode != 0:
        raise SourceUnavailable(
            f"gh api {api_path} (ref={ref}) failed: {proc.stderr.strip() or '(no stderr)'}"
        )
    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise SourceUnavailable(f"unexpected non-JSON response for {rel_path}: {exc}") from exc
    content = payload.get("content")
    if content is None or payload.get("encoding") != "base64":
        raise SourceUnavailable(f"unexpected response shape for {rel_path}: {payload!r}")
    return base64.b64decode(content).decode("utf-8")


def resolve_git_head(root: Path) -> str:
    """Returns the checkout's current commit SHA. Raises SourceUnavailable if
    `root` is not a git checkout at all (no .git, or git itself is missing) --
    that is a NOT VERIFIED case, never a silent pass."""
    try:
        proc = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
        )
    except FileNotFoundError as exc:
        raise SourceUnavailable("`git` CLI not found on PATH") from exc
    if proc.returncode != 0:
        raise SourceUnavailable(
            f"{root} is not a git checkout (git rev-parse HEAD failed): "
            f"{proc.stderr.strip() or '(no stderr)'}"
        )
    return proc.stdout.strip()


def resolve_git_ref(root: Path, ref: str) -> str | None:
    """Best-effort resolution of `ref` to a commit SHA within `root`. Returns
    None when it doesn't resolve there (for example, a ref that only exists on
    an unfetched remote) -- that is not itself an error, since resolve_git_head
    is what actually decides whether the checkout matches."""
    proc = subprocess.run(
        ["git", "-C", str(root), "rev-parse", ref],
        capture_output=True,
        text=True,
    )
    return proc.stdout.strip() if proc.returncode == 0 else None


def make_loader(args: argparse.Namespace):
    """Returns (load, resolved_ref): `load(rel_path)` reads one canonical
    source file, and `resolved_ref` is the commit the comparison was actually
    run against -- report that, not args.ref blindly, since the two can
    differ for a local checkout that isn't on the requested ref."""
    if args.warp_server:
        root = Path(args.warp_server)
        if not (root / DEFAULTS_ROOT / "seeds.go").is_file():
            raise SourceUnavailable(f"{root / DEFAULTS_ROOT / 'seeds.go'} does not exist")
        head_sha = resolve_git_head(root)
        # A match is either a literal SHA match, or --ref resolving (within
        # this same checkout) to the same commit as HEAD -- so a branch name
        # or short SHA passed as --ref still verifies correctly.
        if head_sha != args.ref and resolve_git_ref(root, args.ref) != head_sha:
            raise SourceUnavailable(
                f"{root} is checked out at {head_sha}, not the requested ref "
                f"{args.ref!r}. A stale or ahead checkout can look identical to "
                f"the pinned commit at a glance and is never safe to certify "
                f"as a match -- check out the requested ref there, or pass "
                f"--ref to match what's actually checked out."
            )
        return (lambda rel: read_local(root, rel)), head_sha
    return (lambda rel: read_via_gh(args.repo, args.ref, rel)), args.ref


# Matches one SeedAgent{...} struct literal's Role/Description/Model fields
# in seeds.go. Order in the struct is Name, Role, Description, Model, Prompt;
# this pattern anchors on Role and reads forward, so it does not depend on
# Name's value.
SEED_AGENT_RE = re.compile(
    r'Role:\s*enums\.(\w+?)AgentType,\s*'
    r'Description:\s*"((?:[^"\\]|\\.)*)",\s*'
    r'Model:\s*"((?:[^"\\]|\\.)*)"',
    re.DOTALL,
)


def parse_seeds(seeds_go: str) -> dict[str, tuple[str, str]]:
    """Returns {role_prefix: (description, model)} e.g. {"Foreman": (...)}."""
    result: dict[str, tuple[str, str]] = {}
    for match in SEED_AGENT_RE.finditer(seeds_go):
        role, description, model = match.groups()
        result[role] = (description, model)
    return result


def render_appendix(is_foreman: bool) -> str:
    """Reimplements prompts.go's integrationSkillAppendix for this example's
    pinned composition (GitHub + tracker + Slack). If warp-server changes
    that function's rendering rules, this must be updated to match."""
    lines = ["## Selected integration skills"]
    if HAS_TRACKER:
        lines.append("- Tracker: read the skill for the tracker the work item lives in.")
    lines.append(f"- Code forge: read `.agents/skills/{FORGE_SKILL_DIR}/SKILL.md`.")
    if is_foreman and COMMUNICATIONS_IS_SLACK:
        lines.append("- Communications: read `.agents/skills/slack/SKILL.md`.")
    return "\n".join(lines)


def render_expected_prompt(template: str, is_foreman: bool) -> str:
    # Mirrors renderAgentPrompt in prompts.go: trim exactly one trailing
    # newline, then append "\n\n" + the generated appendix.
    body = template[:-1] if template.endswith("\n") else template
    return body + "\n\n" + render_appendix(is_foreman)


FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.DOTALL)


def parse_agent_file(content: str) -> tuple[dict[str, str], str]:
    match = FRONTMATTER_RE.match(content)
    if not match:
        raise ValueError("file does not start with a --- frontmatter block")
    frontmatter_block, body = match.groups()
    frontmatter: dict[str, str] = {}
    for line in frontmatter_block.splitlines():
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        frontmatter[key.strip()] = value.strip()
    return frontmatter, body


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument(
        "--example",
        default=None,
        help="Path to the example tree (default: examples/00-warp-default-agents "
        "relative to this repository's root).",
    )
    parser.add_argument(
        "--warp-server",
        default=None,
        help="Path to a local warp-server checkout. When given, sources are read "
        "from disk instead of fetched over the network, but only after "
        "confirming the checkout's HEAD (or --ref resolved within it) matches "
        "--ref -- a checkout on the wrong commit is reported as NOT VERIFIED "
        "(exit 2), never certified as a match. Check out --ref (or the pinned "
        "commit) there first.",
    )
    parser.add_argument(
        "--ref",
        default=PINNED_REF,
        help=f"warp-server commit SHA to fetch sources from via `gh api` when "
        f"--warp-server is not given (default: the pinned snapshot commit, "
        f"{PINNED_REF}).",
    )
    parser.add_argument(
        "--repo",
        default=DEFAULT_REPO,
        help=f"warp-server repository to fetch from via `gh api` (default: {DEFAULT_REPO}).",
    )
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    args = parser.parse_args(argv)

    repo_root = Path(__file__).resolve().parent.parent
    example_root = Path(args.example) if args.example else repo_root / "examples" / "00-warp-default-agents"

    try:
        load, resolved_ref = make_loader(args)
        seeds_go = load(f"{DEFAULTS_ROOT}/seeds.go")
        seeds = parse_seeds(seeds_go)
    except SourceUnavailable as exc:
        print(f"NOT VERIFIED: could not read canonical sources: {exc}", file=sys.stderr)
        return 2

    divergences: list[str] = []
    for role_prefix, dirname, agent_type, template_file in ROLES:
        if role_prefix not in seeds:
            divergences.append(f"{dirname}: seeds.go has no {role_prefix}AgentType entry")
            continue
        expected_description, expected_model = seeds[role_prefix]

        try:
            template = load(f"{DEFAULTS_ROOT}/prompts/{template_file}")
        except SourceUnavailable as exc:
            print(f"NOT VERIFIED: could not read canonical sources: {exc}", file=sys.stderr)
            return 2

        agent_path = example_root / "agents" / dirname / "agent.md"
        try:
            local_content = agent_path.read_text()
        except OSError as exc:
            divergences.append(f"{dirname}: could not read {agent_path}: {exc}")
            continue

        try:
            frontmatter, local_body = parse_agent_file(local_content)
        except ValueError as exc:
            divergences.append(f"{dirname}: {agent_path}: {exc}")
            continue

        if frontmatter.get("agentType") != agent_type:
            divergences.append(
                f"{dirname}: agentType is {frontmatter.get('agentType')!r}, expected {agent_type!r}"
            )
        if frontmatter.get("description") != expected_description:
            divergences.append(
                f"{dirname}: description is {frontmatter.get('description')!r}, "
                f"expected {expected_description!r} (seeds.go)"
            )
        if frontmatter.get("model") != expected_model:
            divergences.append(
                f"{dirname}: model is {frontmatter.get('model')!r}, "
                f"expected {expected_model!r} (seeds.go)"
            )

        expected_body = render_expected_prompt(template, is_foreman=(dirname == "foreman"))
        if local_body.rstrip("\n") != expected_body.rstrip("\n"):
            divergences.append(
                f"{dirname}: agent.md body does not match prompts/{template_file} "
                f"+ the rendered integration-skill appendix"
            )

    if args.json:
        print(json.dumps({"divergences": divergences, "resolved_ref": resolved_ref}, indent=2))
    elif divergences:
        print(f"DIVERGED: {len(divergences)} issue(s) found against {resolved_ref}:")
        for item in divergences:
            print(f"  - {item}")
    else:
        print(f"OK: {example_root} matches {DEFAULTS_ROOT} at {resolved_ref}.")

    return 1 if divergences else 0


if __name__ == "__main__":
    sys.exit(main())
