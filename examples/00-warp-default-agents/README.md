# 00: Warp's default agents

This example reproduces the five agents Warp creates for every new factory,
as of 2026-08-20: the same role descriptions, default models, and prompts
the setup wizard seeds, verbatim, as files.

Read it to see the agents and prompts you already have, or copy it when you
want the stock agents as files you can edit and version. The tree applies
as committed once the placeholder repository is replaced, but it declares
no automations, so nothing triggers it.

## The default agents

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

Every frontmatter `description` and `model` above is the product default.
The wizard names seeded agents "<Factory name> Foreman Agent" and so on; in
a file-based definition the directory is the name, so this tree uses the
role names.

## Integration skills

The `## Selected integration skills` section at the end of each prompt is
generated per factory by the wizard from your connected integrations: the
tracker line appears only when a tracker (Linear or Jira) is declared, and
the communications line appears only on the foreman and only when Slack is
declared. This tree renders GitHub, a tracker, and Slack to match its
`integrations` list.

## What this example doesn't reproduce

The default seed also includes the integration skills the prompts reference
(`github`, `slack`, `linear`/`jira`, `code-review`, `ui-verification`),
default automations (mirrored in
[`02-sdlc-issue-to-pr`](../02-sdlc-issue-to-pr)), and five default scorers.
That content is managed by the product and evolves with it.

## Runner

One 4 vCPU / 8 GB `ubuntu:24.04` runner, because a definition must name a
runner in `agentDefaults` when it sets no `environmentId`.

## Make it yours

1. Replace `acme/api-service` in `factory.yaml`.
2. Match `integrations` to what your team connects, and adjust each prompt's
   `## Selected integration skills` section to the same composition.
3. Change models per agent freely. The defaults above are a starting point,
   and the product's own defaults change over time as models improve.
