# 01: Single-repo quickstart

The smallest useful factory: one repository, one intake path, one
deliverable. A maintainer labels an issue `factory-ready`; the foreman
routes it to the implementation agent; the implementation agent opens a
pull request; a human reviews and merges.

## What it demonstrates

- The minimal required tree: `factory.yaml` plus at least one agent, where
  exactly one agent is the `FOREMAN` (alias `MAIN`).
- Path-based naming: an agent's or automation's name is its directory, and
  a runner's name is its file name. No `name:` fields.
- `agentDefaults` inheritance: both agents inherit `model` and `runner` from
  `factory.yaml` and declare neither.
- One event-driven automation with a `(provider, event)` filter.
- One Linux runner whose image, not `setupCommands`, provides the toolchain.
  See "Runner" below.

## Tree

```
factory.yaml
agents/
  foreman/agent.md        FOREMAN, routes work and reports back
  implementer/agent.md    IMPLEMENT, turns an issue into a PR
automations/
  issue-labeled/automation.md   github/issue_labeled, filtered to factory-ready
runners/
  linux-small.yaml        2 vCPU / 4 GB, node:22-bookworm-slim
```

## Runner

One small runner, 2 vCPU / 4 GB, on `node:22-bookworm-slim`. It demonstrates
two rules:

- Every Linux runner must declare `platform.linux.dockerImage`, and that
  image is where the toolchain comes from. An image that already has your
  language beats installing it in `setupCommands` on every run.
- Linux instance shapes must be powers of two.

Swap the image for whatever your repository builds with.

## Make it yours

1. Replace `acme/api-service` in `factory.yaml` and
   `automations/issue-labeled/automation.md` with a repository your Warp
   team's GitHub installation can reach.
2. Adjust `alias`; it becomes the factory's @-mention handle.
3. Swap the runner's `dockerImage` for your stack, and optionally change
   `agentDefaults.model` (any Warp Agent model ID).

## Register it

Create a factory in Warp, choose a GitHub-backed definition, and point it at
your fork of this directory. The registered root is the directory containing
`factory.yaml`, not necessarily the repository root. Pushes to the
production branch sync the definition after the `warp/factory-config` check
passes.
