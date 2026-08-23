#!/usr/bin/env python3
"""Check this repository's own conventions, which the schema can't.

`validate_factory_files.py` asks warp-server whether a tree is a valid
Factory definition. That is the important check, and this script deliberately
does not duplicate any of it. This one checks the things that are true of
*this repository* rather than of the format:

Structure
  - every `runner:` reference resolves to a runner file in the same example
  - every Scorer's `agents:` entry names an agent directory that exists
  - every example has exactly one FOREMAN (or its MAIN alias)
  - every `examples/<name>` path named in Markdown actually exists, so a
    renumbering can't leave dangling links behind

Terminology (see CONTRIBUTING.md)
  - "roster" and "agent set" are not product terms; the five agents are
    "the default agents"
  - "Oz" appears only as the `oz` CLI binary in commands and the literal
    `type: oz` schema value, never in prose
  - "Warp Factories" is the product, written in full; an individual "factory"
    is lowercase; a bare capitalized "Factory" is never a proper noun

Files listed in VENDORED are exempt from the terminology rules: they are
verbatim copies of upstream files, and this repository's rule is to update
them by re-copying rather than editing.

Prose that has to name a banned term in order to ban it (CONTRIBUTING's own
terminology section, for instance) can fence itself off:

    <!-- terminology-allow-begin -->
    ...prose naming "roster", "Oz", or a bare "Factory"...
    <!-- terminology-allow-end -->

The fence is an HTML comment, so it does not render. Keep the fenced region
as small as the exception requires.

Exit codes:
    0  no problems found
    1  at least one problem found
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

DEFAULT_ROOT = Path(__file__).resolve().parent.parent

# Verbatim copies of upstream files. Exempt from terminology rules; see
# CONTRIBUTING.md ("Before opening a PR").
VENDORED = {"scripts/validate_factory_files.py"}

# This checker and its tests have to name the banned terms in order to ban
# them and to prove the rules fire, so they are exempt from the terminology
# rules. Nothing else should be added here: use the terminology-allow fence.
SELF_REFERENTIAL = {
    "scripts/check_conventions.py",
    "scripts/test_check_conventions.py",
}

# Verbatim product strings quoted as they ship. The docs' terminology rule
# says to quote these even when they break the capitalization rule.
VERBATIM_PRODUCT_STRINGS = ("<Factory name>",)

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)


def frontmatter_of(path: Path) -> dict[str, str]:
    match = FRONTMATTER_RE.match(path.read_text())
    if not match:
        return {}
    fields: dict[str, str] = {}
    for line in match.group(1).splitlines():
        # Only top-level scalars matter here; nested blocks are ignored.
        if line.startswith((" ", "\t")) or ":" not in line:
            continue
        key, _, value = line.partition(":")
        fields[key.strip()] = value.strip()
    return fields


def example_dirs(root: Path) -> list[Path]:
    examples = root / "examples"
    if not examples.is_dir():
        return []
    return sorted(d for d in examples.iterdir() if (d / "factory.yaml").is_file())


def check_structure(root: Path, problems: list[str]) -> None:
    for example in example_dirs(root):
        rel = example.relative_to(root)
        runners = {p.stem for p in (example / "runners").glob("*.yaml")}
        agents = {p.name for p in (example / "agents").iterdir() if p.is_dir()} if (
            example / "agents"
        ).is_dir() else set()

        # runner: references resolve.
        for path in list(example.rglob("*.yaml")) + list(example.rglob("*.md")):
            if path.name.endswith(".yaml") and path.parent.name == "runners":
                continue
            for match in re.finditer(r"^\s*runner:\s*(\S+)\s*$", path.read_text(), re.M):
                name = match.group(1).strip("\"'")
                if name in ("null", "~"):
                    continue
                if name not in runners:
                    problems.append(
                        f"{path.relative_to(root)}: runner {name!r} has no "
                        f"runners/{name}.yaml (have: {sorted(runners) or 'none'})"
                    )

        # Scorer agents: entries resolve.
        for scorer in (example / "scorers").glob("*/scorer.md"):
            body = scorer.read_text()
            block = re.search(r"^agents:\n((?:\s*-\s*\S+\n)+)", body, re.M)
            if not block:
                continue
            for name in re.findall(r"-\s*(\S+)", block.group(1)):
                if name not in agents:
                    problems.append(
                        f"{scorer.relative_to(root)}: scores agent {name!r}, "
                        f"which is not an agent directory (have: {sorted(agents)})"
                    )

        # Exactly one foreman.
        foremen = [
            d for d in sorted(agents)
            if frontmatter_of(example / "agents" / d / "agent.md").get("agentType")
            in ("FOREMAN", "MAIN")
        ]
        if len(foremen) != 1:
            problems.append(
                f"{rel}: expected exactly one FOREMAN/MAIN agent, found "
                f"{len(foremen)} ({foremen or 'none'})"
            )


def markdown_files(root: Path) -> list[Path]:
    return [
        p
        for p in root.rglob("*.md")
        if ".git" not in p.parts and "node_modules" not in p.parts
    ]


def check_example_links(root: Path, problems: list[str]) -> None:
    known = {d.name for d in example_dirs(root)}
    for path in markdown_files(root):
        for match in re.finditer(r"examples/([0-9]{2}-[a-z0-9-]+)", path.read_text()):
            name = match.group(1)
            if name not in known:
                problems.append(
                    f"{path.relative_to(root)}: references examples/{name}, "
                    f"which does not exist"
                )


def checkable_text_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for pattern in ("*.md", "*.yaml", "*.yml", "*.py"):
        for path in root.rglob(pattern):
            if ".git" in path.parts or "node_modules" in path.parts:
                continue
            if str(path.relative_to(root)) in VENDORED:
                continue
            files.append(path)
    return files


def check_terminology(root: Path, problems: list[str]) -> None:
    for path in checkable_text_files(root):
        rel = path.relative_to(root)
        if str(rel) in SELF_REFERENTIAL:
            continue
        allowed = False
        for lineno, line in enumerate(path.read_text().splitlines(), start=1):
            where = f"{rel}:{lineno}"
            if "terminology-allow-begin" in line:
                allowed = True
                continue
            if "terminology-allow-end" in line:
                allowed = False
                continue
            if allowed:
                continue

            if re.search(r"\broster\b", line, re.I):
                problems.append(
                    f'{where}: says "roster"; the product term is "the default agents"'
                )
            if re.search(r"\bagent set\b", line, re.I):
                problems.append(
                    f'{where}: says "agent set"; the product term is "the default agents"'
                )

            # "Oz" is allowed only as the `oz` CLI binary or the type: oz value.
            for match in re.finditer(r"\bOz\b", line):
                problems.append(
                    f'{where}: says "Oz"; use "the Warp Agent harness" '
                    f"(the `oz` CLI binary and `type: oz` stay lowercase)"
                )
                break
            if re.search(r"\boz\b", line) and not re.search(
                r"(`|\$ |^\s*[-*]?\s*)oz [a-z]|type:\s*oz|`oz`|oz\.warp\.dev", line
            ):
                problems.append(
                    f'{where}: bare "oz" outside a command or the type: oz value'
                )

            # Bare capitalized "Factory" is never a proper noun.
            if any(s in line for s in VERBATIM_PRODUCT_STRINGS):
                continue
            for match in re.finditer(r"\bFactory\b", line):
                start = match.start()
                if line[:start].rstrip().endswith("Warp"):
                    continue  # "Warp Factory ..." is caught by the Factories rule below
                if start == 0 or line[:start].strip() in ("#", "##", "###", "-", "*"):
                    continue  # sentence-initial capitals are positional
                problems.append(
                    f'{where}: bare "Factory"; write "Warp Factories" for the '
                    f'product or lowercase "factory" for an instance'
                )
                break
            if re.search(r"\bWarp Factory\b", line):
                problems.append(
                    f'{where}: "Warp Factory"; the product is "Warp Factories", '
                    f"always written in full"
                )


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument(
        "--root",
        default=None,
        help="Repository root to check (default: this script's repository).",
    )
    args = parser.parse_args(argv)
    root = Path(args.root).resolve() if args.root else DEFAULT_ROOT

    problems: list[str] = []
    check_structure(root, problems)
    check_example_links(root, problems)
    check_terminology(root, problems)

    if problems:
        print(f"{len(problems)} problem(s):")
        for problem in problems:
            print(f"  - {problem}")
        return 1
    print("Conventions OK: structure, example links, and terminology.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
