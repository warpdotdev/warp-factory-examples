# 06: Common automations

A catalog of standing automations attached to one maintenance agent.
Nothing here waits for a human request: CI failures, schedules, pushes,
and Slack reactions each start a scoped job that ends in a report, an
issue, or a pull request.

## What it demonstrates

- Four trigger shapes on one agent, each a different way for work to
  start without a human ask: an event's outcome, a schedule, a code
  change, and a chat reaction. See the tree below for each one's filters.
- One agent behind all of them: each automation's body states the job, so
  the agent prompt stays small.
- The `integrations` list declares Slack, which the reaction trigger needs.

## Tree

```
factory.yaml
agents/
  maintainer/agent.md     FOREMAN, does whatever the trigger asks
automations/
  ci-failure-triage/          github/workflow_run_completed, failures on main
  weekly-dependency-audit/    schedule/cron_fired, Mondays 09:00 UTC
  docs-drift-on-push/         github/push, main, api/**
  slack-reaction-intake/      slack/reaction_added, :ticket: in one channel
runners/
  linux-standard.yaml     4 vCPU / 8 GB, ubuntu:24.04
```

## Make it yours

1. Replace `acme/api-service` in `factory.yaml` and both GitHub
   automations.
2. Connect Slack to your Warp team, replace `your-intake-channel` with the
   channel to watch, and change `emojis` to the reaction your team uses.
3. Adjust the cron, the watched `paths`, and the workflow filters to your
   repository. Cron is always UTC, so convert your intended local time
   first. `workflow_run_completed` also filters by `workflows` when you
   only care about specific ones.
4. Split automations across agents as they grow: an automation's `agent:`
   field routes to any declared agent, and each automation can also
   override `model` and `runner`.
