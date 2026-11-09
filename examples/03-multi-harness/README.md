# 03: Multi-harness

This example uses a different harness for each role. The foreman runs on the
Warp Agent harness and routes work, a Claude Code agent implements changes,
and a Codex agent reviews them. Apart from the harness configuration, the
factory works the same way as
[`01-single-repo-quickstart`](../01-single-repo-quickstart).

## What this example shows

- `model: <id>` is shorthand for the Warp Agent harness. The `model` and
  `harness` fields are mutually exclusive everywhere. `agentDefaults` must
  declare one of them, and agents can declare neither and inherit the default.
- Each agent can declare an explicit `harness` block with a `type` (`claude`,
  `codex`, `gemini`, or `oz`) and a harness-native `model`. Set
  `reasoningLevel` only where the harness's catalog defines levels. Codex
  models take one, but current Claude models don't.
- Harness authentication uses `auth.source: managedSecret` and a named team
  secret.
- The reviewer runs on a different model family than the implementer, which
  reduces shared blind spots.

## Directory structure

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

## Runner configuration

Harness and compute are independent. An agent picks a harness with `harness`
and a machine with `runner`, and neither setting constrains the other.

The supported platforms are `linux/x86_64`, `linux/aarch64`, and
`macos/aarch64`. macOS supports only `aarch64`. When you switch a runner to
`aarch64`, make sure its `dockerImage` publishes an arm64 variant. The
`ubuntu:24.04` image does.

## Create the required secrets

The two harness `auth` blocks reference managed secrets by name. Before you
apply this definition, create both secrets as typed harness API-key secrets.
Don't create them as raw values, because applying the definition rejects a
`raw_value` secret for harness authentication.

```bash
oz secret create claude api-key ANTHROPIC_API_KEY   # Anthropic API key
oz secret create codex api-key OPENAI_API_KEY       # OpenAI API key
```

Self-hosted workers can use `auth.source: workerEnvironment` instead. It reads
credentials from the worker's environment and takes no `secretName`.

## Customize the example

1. Confirm that your team has access to each harness you enable. Third-party
   harnesses require a Build plan or higher.
2. Create the Anthropic and OpenAI API-key secrets described in
   [Create the required secrets](#create-the-required-secrets).
3. Replace `acme/api-service` in `factory.yaml` and
   `automations/issue-labeled/automation.md`.
4. Choose your harness models. The `model` field inside a `harness` block uses
   the harness's own model names, not Warp Agent model IDs.
