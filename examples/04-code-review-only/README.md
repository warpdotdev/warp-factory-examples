# 04: Code review only

A single-agent factory: one reviewer, one trigger, no lifecycle. A pull
request opens; the factory reviews it and posts advisory findings on the
PR; a human decides what to do with them.

## What it demonstrates

- The single-agent shape: every factory needs exactly one `FOREMAN` agent,
  so in a one-agent factory that agent is the foreman and does the work
  itself.
- Automations route to the foreman when they declare no `agent:` field.
- PR-volume filters: `base_branches` scopes reviews to the default branch,
  and the `wip` label is the opt-out for authors. `pull_request_opened`
  fires for drafts too, so the prompt tells the agent to skip them.

## Tree

```
factory.yaml
agents/
  reviewer/agent.md       FOREMAN, reviews and posts findings
automations/
  pr-opened/automation.md   github/pull_request_opened, filtered to main
runners/
  linux-small.yaml        2 vCPU / 4 GB, ubuntu:24.04
```

## Make it yours

1. Replace `acme/api-service` in `factory.yaml` and
   `automations/pr-opened/automation.md`.
2. Adjust the filters: `base_branches` for your default branch, and the
   opt-out label your team uses for work in progress.
3. To review only when asked, switch the trigger to
   `pull_request_review_requested`, which filters by `reviewers` and
   `reviewer_teams`.
4. To review drafts when they are marked ready, add a second trigger with
   the `pull_request_ready` event.
