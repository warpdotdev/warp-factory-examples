# 06: Common automations

This example is a factory with one maintenance agent that starts work without
waiting for a human request. CI failures, schedules, pushes, and Slack
reactions each start a scoped job that ends in a report, an issue, or a pull
request.

## What this example shows

- One agent handles work triggered by CI failures, a weekly schedule, code
  pushes, and Slack reactions. The directory structure below shows each
  trigger's filters.
- Each automation's message states the job, so the agent prompt stays small.
- The `integrations` list declares Slack, which the reaction trigger needs.

## Directory structure

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

## Customize the example

1. Replace `acme/api-service` in `factory.yaml` and both GitHub automations
   (`ci-failure-triage` and `docs-drift-on-push`).
2. Connect Slack to your Warp team.
3. Replace `your-intake-channel` in `slack-reaction-intake` with the channel
   to watch.
4. Change `emojis` in `slack-reaction-intake` to the reaction your team uses.
5. Adjust the cron schedule in `weekly-dependency-audit`. Cron is always UTC,
   so convert your intended local time first.
6. Adjust the watched `paths` in `docs-drift-on-push` to match your repository.
7. Adjust the workflow filters in `ci-failure-triage`. The
   `workflow_run_completed` event also filters by `workflows` if you care only
   about specific ones.
8. Optionally, split automations across agents as they grow. An automation's
   `agent:` field routes to any declared agent, and each automation can also
   override `model` and `runner`.
