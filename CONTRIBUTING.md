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
  show those fields in README snippets instead. Managed secret names may
  appear only when the example's README tells the reader to create them
  first.
- Placeholders are `acme/*` repositories by default. A placeholder outside
  that list is allowed only when it cannot be mistaken for a working value
  (e.g. a name like `your-intake-channel`) and the example README's "Make
  it yours" checklist names it directly. Every placeholder, and every
  other prerequisite the committed files cannot satisfy on their own
  (connecting an integration, creating a secret, resolving a Linear team
  name), must appear in that checklist.
- Keep prompts short and pedagogical. Teach the shape of a good stage prompt
  (role, non-responsibilities, input, output, procedure) rather than
  shipping a production prompt library.
- One concept per example. If a new example mostly repeats an existing one,
  extend the existing README instead.
<!-- terminology-allow-begin -->
- Match the product's terminology; the
  [docs](https://docs.warp.dev/factories/) are the source of truth.
  - The five agents Warp creates are **the default agents** (a team of
    default agents, with a **foreman**). Not a "roster", not an "agent set".
  - The built-in harness is **the Warp Agent harness**. The name "Oz"
    appears only as the `oz` CLI binary in shell commands and the literal
    `type: oz` schema value in YAML. Do not use it in prose.
  - **Warp Factories** is the product and is always written in full. An
    individual **factory** is a lowercase common noun. Verbatim product
    strings are quoted as they ship even when they break the rule (the
    setup wizard renders "<Factory name> Foreman Agent").
  - Files copied verbatim from elsewhere are exempt; see below.
<!-- terminology-allow-end -->

## Before opening a PR

Validate every example:

```bash
for ex in examples/*/; do python3 scripts/validate_factory_files.py "$ex" || break; done
```

Check the repository conventions:

```bash
python3 scripts/check_conventions.py
```

This checks the ground rules a script can check: runner references, scorer
agent names, one foreman per example, `examples/` links, and the
terminology rules. Prose that must name a banned term can fence itself off
with `<!-- terminology-allow-begin -->` / `<!-- terminology-allow-end -->`.

CI runs both checks on every PR. CI also fails when the server's schema
version moves past `v1alpha1`; that means the examples need a version-bump
PR, not a workaround.

If you change [`examples/00-warp-default-agents`](examples/00-warp-default-agents),
also run `scripts/verify_default_agents.py` to confirm the tree still
matches the product's default agents.

`scripts/validate_factory_files.py` is a copy of the validator bundled with
Warp's `factory-files` skill. Update it by re-copying it from a current
Warp build, not by editing it here.

## Optional: confirm an example applies

If your Warp team can register a GitHub-backed definition, copy the example
into a real repository, work through its "Make it yours" checklist, register
a factory pointing at it, and fire a cheap trigger. Not required to open a
PR; note in the PR description whether you did it.
