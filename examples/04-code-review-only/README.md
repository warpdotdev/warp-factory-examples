# 04: Code review only

This example is a single-agent factory for code review. When someone opens a
pull request, the agent reviews it and posts advisory findings, and a human
decides what to do with them. The factory doesn't triage, specify, or
implement work.

## What this example shows

- Every factory needs exactly one `FOREMAN` agent, so in a one-agent factory
  that agent is the foreman and does the work itself.
- Automations route to the foreman when they don't declare an `agent:` field.
- Two filters limit how many pull requests get reviewed. `base_branches`
  scopes reviews to the default branch, and the `wip` label lets authors opt
  out. The `pull_request_opened` event fires for drafts too, so the prompt
  tells the agent to skip them.

## Directory structure

```
factory.yaml
agents/
  reviewer/agent.md       FOREMAN, reviews and posts findings
automations/
  pr-opened/automation.md   github/pull_request_opened, filtered to main
runners/
  linux-small.yaml        2 vCPU / 4 GB, ubuntu:24.04
```

## Customize the example

1. Replace `acme/api-service` in `factory.yaml` and
   `automations/pr-opened/automation.md`.
2. Set `base_branches` to your default branch.
3. Replace the `wip` label in `labels.not_in` with the label your team uses
   for work in progress.
4. Optionally, review only when asked. Switch the trigger to
   `pull_request_review_requested`, which filters by `reviewers` and
   `reviewer_teams`.
5. Optionally, review drafts when they are marked ready. Add a second trigger
   with the `pull_request_ready` event.
