# 07: Self-hosted worker

This example adapts the quickstart factory to use a managed self-hosted
worker. Warp coordinates the factory. The worker checks out repositories,
runs commands, and provides the sandbox filesystem on your team's
infrastructure.

## What this example shows

- `workerHost` on `agentDefaults` sends every run in this factory to the
  worker named `factory-worker`. Any agent or automation can override
  `workerHost` for its own runs.
- The runner must match the worker backend's platform. This example uses the
  managed worker's Docker backend, which runs Linux containers on a
  `linux/amd64` or `linux/arm64` daemon. Its runner is `linux/x86_64`.
  The worker binary itself runs on Linux, macOS, or Windows hosts.
  The Kubernetes and Direct backends have their own requirements.
- Warp resolves worker IDs when you apply the definition, as it does secret
  names and model IDs, so the example validates before the worker exists.

## Directory structure

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

## Deploy the self-hosted worker

The `workerHost` setting in this example names a worker called
`factory-worker`. Before you apply the definition, deploy a worker with that
ID. The
[self-hosting quickstart](https://docs.warp.dev/factories/self-hosting/quickstart/)
explains how to start a worker and choose its `--worker-id`.

For the Docker, Kubernetes, and Direct backend requirements, see the
[self-hosting overview](https://docs.warp.dev/factories/self-hosting/).
Self-hosting requires an Enterprise plan and must be enabled for your team.

## Customize the example

1. [Deploy a self-hosted worker](#deploy-the-self-hosted-worker).
2. Replace `acme/api-service` in `factory.yaml` and
   `automations/issue-labeled/automation.md`.
3. Set `workerHost` in `factory.yaml` to your worker's `--worker-id`.
4. Set the runner's `arch` to match the worker's Docker daemon platform.
   Use `x86_64` for `linux/amd64` and `aarch64` for `linux/arm64`.
5. Optionally, move a stage back to Warp-hosted compute by setting
   `workerHost: warp` on that agent.
