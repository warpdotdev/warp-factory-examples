# Warp Factories examples

Working example configurations for [Warp
Factories](https://docs.warp.dev/factories/), defined as files. Each
directory under `examples/` is a complete factory definition root: copy one,
replace the placeholders, register it, and you have a running factory.

The examples target schema version `v1alpha1`.

## The examples

- [`examples/00-warp-default-agents`](examples/00-warp-default-agents): the
  five agents Warp creates for every new factory, with their real prompts,
  descriptions, and models. Read it to see what you already have, or copy
  it when you want the stock agents as files.
- [`examples/01-single-repo-quickstart`](examples/01-single-repo-quickstart):
  the smallest tree that works. One repository, two agents, one
  labeled-issue trigger, one pull request out. Start here.
- [`examples/02-sdlc-issue-to-pr`](examples/02-sdlc-issue-to-pr): the full
  lifecycle. Intake from Slack, Linear, and GitHub; triage, spec,
  implementation, and review stages plus a custom agent; per-stage models
  and compute; scorers and skills.
- [`examples/03-multi-harness`](examples/03-multi-harness): a different
  harness per role. A foreman on the Warp Agent harness, a Claude Code
  implementer, and a Codex reviewer, with managed-secret harness auth.
- [`examples/04-code-review-only`](examples/04-code-review-only): a
  single-agent factory. One reviewer that is also the foreman, one
  pull-request trigger, advisory findings posted on the PR.
- [`examples/05-ui-verification`](examples/05-ui-verification): computer
  use in a factory. A single agent that runs the app, verifies labeled UI
  behavior in a browser, and posts visual evidence.
- [`examples/06-common-automations`](examples/06-common-automations): a
  catalog of standing automations. CI failure triage, a weekly dependency
  audit, a docs check on push, and Slack reaction intake, all on one agent.

## Using an example

1. Copy the example directory into your own repository. Each example is
   self-contained, and the registered root is the directory containing
   `factory.yaml`, which does not need to be the repository root.
2. Work through the "Make it yours" checklist in the example's README. It
   lists every placeholder you must replace. Most placeholders are
   `acme/*` repositories; a checklist entry names any other one directly,
   and everything else in the trees is real.
3. In Warp, create a factory with a GitHub-backed definition pointing at
   your repository, branch, and directory. Pushes sync the definition after
   the `warp/factory-config` check passes.

## Validating

Check that a tree is a valid factory definition:

```bash
python3 scripts/validate_factory_files.py examples/01-single-repo-quickstart
```

## Layout rules

- A resource's name is its path: `agents/<name>/agent.md`,
  `automations/<name>/automation.md`, `runners/<name>.yaml`,
  `scorers/<name>/scorer.md`. Renaming a resource means moving the file.
- Exactly one agent per factory declares `agentType: FOREMAN` (alias `MAIN`).
- `model` (shorthand for the Warp Agent harness) and `harness` are mutually
  exclusive everywhere; `agentDefaults` must declare exactly one of them.
- Declaring `secrets` or `mcpServers` on an agent or automation replaces the
  inherited list; it does not merge.
- Skills under `skills/` are available to every agent in the factory. Skills
  under `agents/<name>/skills/` are available only to that agent.

## License

[MIT](LICENSE)
