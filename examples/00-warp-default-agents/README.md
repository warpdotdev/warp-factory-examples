# 00: Warp's default agents

This example contains editable configuration files for the five default
agents Warp creates for a new factory. The descriptions, models, and prompts
match Warp's defaults as of August 20, 2026.

Explore the files under `agents/` to understand each agent's role, or copy
the example to customize and version the configurations. Replace the
placeholder repository before using the example. No automations are
included, so the factory won't start work automatically.

## Default agents

The following list shows each agent's directory name, `agentType`, default
model, and description. The quoted descriptions are copied directly from
the agent configuration files.

- `foreman` (`FOREMAN`, model `claude-5-opus-high`): "Orchestrates the
  factory workflow and dispatches each gated step."
- `triage` (`TRIAGE`, model `grok-4-5-high`): "Triages requests and
  establishes task state."
- `spec` (`SPEC`, model `gpt-5-6-sol-high`): "Writes and drives approval of
  specifications."
- `implement` (`IMPLEMENT`, model `auto-genius`): "Implements, validates,
  and updates code changes."
- `review` (`REVIEW`, model `gpt-5-6-terra-high`): "Reviews factory pull
  requests and routes findings to rework or human resolution."

During setup, Warp gives agents names such as "\<Factory name> Foreman Agent."
In this example, each agent is named after its directory, such as `foreman`
or `triage`.

## What's not included

This example includes the agent configurations, but not the following
resources that Warp provides when you create a factory:

- The skills referenced by the prompts, including `github`, `slack`,
  `linear`/`jira`, `code-review`, and `ui-verification`.
- The default automations. See
  [`02-sdlc-issue-to-pr`](../02-sdlc-issue-to-pr) for an example that includes
  them.
- The five default scorers.

Warp maintains these resources, and they may change over time.

## Integration skill references

During setup, Warp adds a "Selected integration skills" section to each
agent's prompt based on the factory's connected integrations.

The tracker entry appears only when Linear or Jira is configured. The
communications entry appears only in the foreman's prompt and only when
Slack is configured.

This example includes entries for GitHub, an issue tracker, and Slack to
match its `integrations` configuration.

## Runner configuration

This example uses one runner with 4 vCPUs, 8 GB of memory, and the
`ubuntu:24.04` image. A runner is required in `agentDefaults` when no
`environmentId` is specified.

## Customize the example

1. Replace `acme/api-service` in `factory.yaml`.
2. Match `integrations` to what your team connects, and adjust each prompt's
   `## Selected integration skills` section to the same composition.
3. Change models per agent freely. The defaults above are a starting point,
   and the product's own defaults change over time as models improve.
