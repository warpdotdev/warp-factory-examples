# 07: Self-hosted worker

This example is the quickstart topology with execution routed to a managed
self-hosted worker: Warp coordinates the factory, and repository checkouts,
commands, and the sandbox filesystem run on compute your team provides.

## What it demonstrates

- `workerHost` on `agentDefaults`: every run in this factory executes on the
  worker named `factory-worker`. Any agent or automation can override
  `workerHost` for its own runs.
- Runner and worker platforms must match. Workers run on Linux `amd64` and
  `arm64` only, so this factory's runner is `linux/x86_64`; there are no
  macOS workers.
- Worker IDs are resolved when the definition is applied, like secret names
  and model IDs, so the tree validates before the worker exists.

## Start the worker first

This tree's `workerHost` names a worker called `factory-worker`. Deploy a
worker with that ID before applying the definition; the
[self-hosting docs](https://docs.warp.dev/platform/self-hosting/) cover
starting the worker and choosing its `--worker-id`. Self-hosted execution is
an Enterprise feature and must be enabled for your team.

## Tree

```
factory.yaml              agentDefaults.workerHost: factory-worker
agents/
  foreman/agent.md        FOREMAN, routes work and reports back
  implementer/agent.md    IMPLEMENT, builds on the worker's network
automations/
  issue-labeled/automation.md   github/issue_labeled, filtered to factory-ready
runners/
  linux-worker.yaml       4 vCPU / 8 GB, linux/x86_64, ubuntu:24.04
```

## Make it yours

1. Replace `acme/api-service` in `factory.yaml` and
   `automations/issue-labeled/automation.md`.
2. Set `workerHost` to match your worker's `--worker-id`.
3. Match the runner's `arch` to the worker: `x86_64` for `amd64` hosts,
   `aarch64` for `arm64` hosts.
4. To move a stage back to Warp-hosted compute, set `workerHost: warp` on
   that agent.
