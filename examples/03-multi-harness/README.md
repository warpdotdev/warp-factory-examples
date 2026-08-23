# 03: Multi-harness

The quickstart topology with a different harness per role: a foreman on
the Warp Agent harness routes work, a Claude Code agent implements, and a
Codex agent reviews. The factory mechanics match
[`01-single-repo-quickstart`](../01-single-repo-quickstart); only the
harness configuration is new.

## What it demonstrates

- `model` and `harness`: `model: <id>` is shorthand for the Warp Agent
  harness, and the two fields are mutually exclusive everywhere.
  `agentDefaults` must declare one of them; agents may declare neither and
  inherit.
- Explicit `harness` blocks per agent: `type` (`claude`, `codex`, `gemini`,
  `oz`) and a harness-native `model`. `reasoningLevel` is set only where the
  harness's catalog defines levels; Codex models take one, current Claude
  models do not.
- Harness auth via `auth.source: managedSecret` and a named team secret.
- The reviewer runs on a different model family than the implementer, which
  reduces shared blind spots.

## Tree

```
factory.yaml                 agentDefaults.model: auto (Warp Agent harness)
agents/
  foreman/agent.md           inherits the Warp Agent default
  implementer/agent.md       harness: claude / opus, runner: linux-arm64
  reviewer/agent.md          harness: codex / gpt-5.3-codex / reasoningLevel: high
automations/
  issue-labeled/automation.md
runners/
  linux-standard.yaml        linux/x86_64
  linux-arm64.yaml           linux/aarch64
```

## Runners

Harness and compute are independent: an agent picks a harness with `harness`
and its machine with `runner`, and neither constrains the other.

Supported platforms are `linux/x86_64`, `linux/aarch64`, and `macos/aarch64`
(macOS is `aarch64`-only). When you switch a runner to `aarch64`, make sure
its `dockerImage` publishes an arm64 variant; `ubuntu:24.04` does.

## Secrets you must create first

The two harness `auth` blocks reference managed secrets by name. Before
applying this definition, create both secrets as typed harness API-key
secrets, not raw values; applying rejects a `raw_value` secret for harness
auth:

```bash
oz secret create claude api-key ANTHROPIC_API_KEY   # Anthropic API key
oz secret create codex api-key OPENAI_API_KEY       # OpenAI API key
```

Self-hosted workers can use `auth.source: workerEnvironment` instead, which
reads credentials from the worker's environment and takes no `secretName`.

## Make it yours

1. Replace `acme/api-service` in `factory.yaml` and the automation.
2. Pick your harness models: `model` inside a `harness` block uses the
   harness's own model naming, not a Warp Agent model ID.
3. Your team needs access to each harness you enable; third-party harnesses
   require a Build plan or higher.
