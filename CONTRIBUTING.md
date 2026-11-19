# Contributing

## Ground rules for examples

- Each example is a complete, independently registerable factory root: one
  `factory.yaml`, at least one agent, exactly one `FOREMAN`.
- Every example must pass `scripts/validate_factory_files.py`. The validator
  defers state-dependent checks (model IDs, secret names, environment IDs,
  runner availability, integration availability) to the apply path, so
  passing does not mean the tree applies as committed.
- Use real Warp Agent model IDs and harness model names only. Do not commit
  fake MCP server IDs, environment IDs, or cloud provider values in YAML;
  show those fields in README snippets instead. Managed secret names and
  self-hosted worker IDs may appear only when the example's README tells
  the reader to create them first.
- Placeholders are `acme/*` repositories by default. A placeholder outside
  that list is allowed only when it cannot be mistaken for a working value
  (e.g. a name like `your-intake-channel`) and the example README's
  "Customize the example" checklist names it directly. Every placeholder,
  and every other prerequisite the committed files cannot satisfy on their own
  (connecting an integration, creating a secret, resolving a Linear team
  name), must appear in that checklist.
- Keep prompts short. Show each stage's task, boundaries, inputs, outputs,
  and procedure rather than shipping a production prompt library.
- One concept per example. If a new example mostly repeats an existing one,
  extend the existing README instead.
- Use an explicit Blueprint for a multi-stage workflow whose routing or human
  decisions are the teaching point. Define stage procedures, route conditions
  in evaluation order, and gates in `factory.yaml`. Keep execution settings
  and shared role boundaries in `agents/`. Do not add a Blueprint to a focused
  intake or review example only to match the others.
<!-- terminology-allow-begin -->
- Match the product's terminology; the
  [docs](https://docs.warp.dev/factories/) are the source of truth.
  - The five agents Warp creates are the default agents, including a
    foreman. Describe their configured responsibilities, not an AI team,
    workforce, or set of teammates. Retain shipped role names.
  - The built-in harness is **the Warp Agent harness**. The name "Oz"
    appears only as the `oz` CLI binary in shell commands and the literal
    `type: oz` schema value in YAML. Do not use it in prose.
  - **Warp Factories** is the infrastructure platform and is always written
    in full. An individual **factory** is a lowercase common noun describing
    the workflows a customer configures, not a team of agents. Verbatim product
    strings are quoted as they ship even when they break the rule (the
    setup wizard renders "<Factory name> Foreman Agent").
  - Files copied verbatim from elsewhere are exempt; see below.
<!-- terminology-allow-end -->

For copy changes, read the docs repository's
[positioning guidance](https://github.com/warpdotdev/docs/blob/main/.agents/rules/warp-positioning.md),
[glossary](https://github.com/warpdotdev/docs/blob/main/.agents/references/terminology.md),
and [writing guide](https://github.com/warpdotdev/docs/blob/main/AGENTS.md).
These govern framing, names, and voice; this repository owns its file format
and validation. Do not copy docs-site MDX conventions into examples or use
positioning as evidence of shipped behavior.

Keep generic agents and default roles lowercase and unbolded in prose and
list lead terms. Preserve proper feature names and literal interface spelling.
Quote non-clickable field labels; keep bold for clickable UI controls and
feature-list lead terms that are not agent names or field labels.

## Before opening a PR

Validate every example:

```bash
status=0
for ex in examples/*/; do
  python3 scripts/validate_factory_files.py "$ex" --server-root https://app.warp.dev || status=1
done
test "$status" -eq 0
```

Check the repository conventions:

```bash
python3 scripts/check_conventions.py
python3 scripts/test_check_conventions.py -v
python3 scripts/test_verify_default_agents.py -v
python3 scripts/test_validate_factory_files.py -v
```

This checks the ground rules a script can check: runner references, scorer
agent names, one foreman per example, the selected Blueprint examples'
top-level coverage and `agents/` layout, `examples/` links, and the
terminology rules. Prose that must name a banned term can fence itself off
with `<!-- terminology-allow-begin -->` / `<!-- terminology-allow-end -->`.

CI runs both checks on every PR. CI also fails when the server's schema
version moves past `v1alpha1`; that means the examples need a version-bump
PR, not a workaround.

If you change [`examples/warp-default-agents`](examples/warp-default-agents),
also run `scripts/verify_default_agents.py` to confirm the tree still
matches the product's default agents.

`scripts/validate_factory_files.py` is a copy of the validator bundled with
Warp's `factory-files` skill. Update it by re-copying it from a current
Warp build, not by editing it here.
Record its source checksum and require byte-for-byte equality after copying.
The copy used here has SHA-256
`c69b352f860b3cad34ba047851c5dd92e6299fa68980f4601e64a18079a25966`.
Helper unit tests use mocks; they do not validate a definition against the
server. Exit 2 from the real helper remains unvalidated and fails CI.

## Optional: confirm an example applies

If your Warp team can register a GitHub-backed definition, copy the example
into a real repository, work through its "Customize the example" checklist,
register a factory pointing at it, and fire a cheap trigger. Not required
to open a PR; note in the PR description whether you did it.
