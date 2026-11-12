# 01: Single-repo quickstart

This example is the smallest factory that does useful work. When a maintainer
labels a GitHub issue `factory-ready`, the foreman routes it to an
implementation agent, which opens a pull request. A human reviews and merges
the pull request.

## What this example shows

- A factory needs only `factory.yaml` and at least one agent. Exactly one
  agent must be the foreman (`agentType: FOREMAN`, alias `MAIN`).
- Resources are named by their paths. An agent's or automation's name is its
  directory name, and a runner's name is its file name, so none of them need a
  `name` field.
- Both agents inherit `model` and `runner` from `agentDefaults` in
  `factory.yaml`, so neither agent declares them.
- One automation starts work from an event. Its trigger names a provider and
  an event (GitHub's `issue_labeled`) and filters to issues labeled
  `factory-ready`.
- One Linux runner gets its toolchain from its Docker image rather than from
  `setupCommands`. See [Runner configuration](#runner-configuration).

## Directory structure

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

## Runner configuration

This example uses one runner with 2 vCPUs, 4 GB of memory, and the
`node:22-bookworm-slim` image. It illustrates two rules for Linux runners:

- Every Linux runner must declare `platform.linux.dockerImage`. The image
  provides the toolchain, so choose one that already includes your language
  instead of installing it with `setupCommands` on every run.
- Linux instance shapes must be powers of two.

To use a different toolchain, replace the image with one that your repository
builds with.

## Use this example

1. Copy the entire `01-single-repo-quickstart` directory into your own GitHub
   repository. You can place it at the repository root or in a subdirectory.
2. Complete the [Customize the example](#customize-the-example) checklist
   below. It explains which placeholders to replace and any additional setup
   required.
3. Commit and push the example files to GitHub.
4. Create a factory in Warp using a
   [GitHub-backed definition](https://docs.warp.dev/factories/factory-as-code/#where-the-definition-lives).
   Specify your repository, branch, and the directory containing `factory.yaml`.

After setup, Warp syncs changes pushed to the configured branch once the
`warp/factory-config` check passes.

## Customize the example

1. Replace `acme/api-service` in `factory.yaml` and
   `automations/issue-labeled/automation.md` with a repository that your Warp
   team's GitHub installation can access.
2. Set `alias` to the handle that people use to @-mention the foreman.
3. Replace the runner's `dockerImage` with an image for your stack.
4. Optionally, change `agentDefaults.model` to any Warp Agent model ID.
