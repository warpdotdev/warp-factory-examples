# 02: Issue to PR

A standing engineering factory: work arrives from Slack, Linear, or
GitHub, and the foreman triages it, specs it when it is ambiguous,
implements it, reviews it adversarially, and hands a review-ready PR to a
human. It mirrors the default agents and default automations the product's
setup wizard creates, as files you can read and edit, and extends them
with one custom agent.

## What it demonstrates

- All five default agents (`FOREMAN`, `TRIAGE`, `SPEC`, `IMPLEMENT`,
  `REVIEW`) with per-agent `model` overrides, plus a `CUSTOM` agent for work
  the default agents don't cover. Review runs on a different model than
  implementation so the two don't share blind spots.
- Per-stage compute: three runners that differ by size, image, and
  operating system, selected per agent. See "Runners" below.
- Multi-source intake from Slack, Linear, and GitHub, plus a follow-up
  automation for closed or merged PRs. The tree below lists each
  automation's trigger.
- The `integrations` array (`slack`, `linear`) and a multi-repository scope.
- Skill scoping: factory-wide (`skills/`) and agent-scoped
  (`agents/<name>/skills/`).

## Tree

```
factory.yaml
agents/
  foreman/agent.md       FOREMAN
  triage/agent.md        TRIAGE   (model: auto-efficient)
  spec/agent.md          SPEC
  implementer/agent.md   IMPLEMENT (runner: linux-build)
    skills/testing-standards/SKILL.md
  reviewer/agent.md      REVIEW   (model: auto-genius)
  mobile-build/agent.md  CUSTOM   (runner: macos-build)
automations/
  slack-app-mentions/    slack/app_mention
  slack-dms/             slack/message_dm
  linear-agent-sessions/ linear/agent_session_created
  github-mention-assign/ github issue+PR mentioned/assigned
  github-pr-closed-or-merged/  merged → complete work items
runners/
  linux-standard.yaml    4 vCPU / 8 GB, ubuntu:24.04
  linux-build.yaml       8 vCPU / 16 GB, golang:1.24-bookworm
  macos-build.yaml       6 vCPU / 14 GB, macos/aarch64
scorers/
  task-compliance/       scores implementer runs, selfImprovement on
  review-quality/        scores reviewer runs
skills/
  repository-conventions/SKILL.md   shared by every agent
```

## Runners

Compute is a per-agent choice. This factory uses three runners because its
stages need different things:

- `linux-standard` (4 vCPU / 8 GB, `ubuntu:24.04`): the `agentDefaults`
  runner, inherited by the foreman, triage, spec, and review. These stages
  read code and write prose.
- `linux-build` (8 vCPU / 16 GB, `golang:1.24-bookworm`): implementation,
  which compiles and runs tests. The image provides the toolchain. Use
  `setupCommands` only for what the image lacks, and write them defensively:
  a setup command that exits non-zero fails the whole sandbox.
- `macos-build` (6 vCPU / 14 GB, `macos/aarch64`): the `mobile-build` agent.
  macOS sandboxes are VMs, not containers, so this runner declares no
  `dockerImage`; it takes an optional `mac.version` instead and accepts only
  a fixed set of shapes. macOS is `aarch64`-only.

Linux shapes must be powers of two. A runner named by an agent overrides the
one in `agentDefaults`.

## How GitHub intake is routed

The mention and assignment automation mirrors the wizard's seeded defaults
and watches only `acme/api-service` and `acme/webapp`. Nothing in this
example files GitHub issues or PRs directly against `acme/ios-app`, so
GitHub intake for iOS work is not wired up. Filter keys combine with AND:

- `mentioned: [warp-factory]` / `assignees: [warp-factory]`: `warp-factory`
  is Warp Factories' own GitHub identity (a product constant, not a
  placeholder). Without this key, `issue_mentioned` fires when anyone is
  @-mentioned in the repos.
- `labels: ["factory:Acme"]`: the factory's routing label,
  `factory:<alias>`. Because filters combine with AND, the label has to be
  on the issue or PR before a mention or assignment trigger can fire; a
  `@warp-factory` mention on an unlabeled item is silently dropped. Apply
  the label yourself when you open the item, or before the first mention.
  After that, the foreman keeps the label on everything it touches, so later
  mentions and assignments keep matching.

The closed-or-merged follow-up automation is scoped wider, to
`acme/api-service`, `acme/webapp`, and `acme/ios-app`: mobile-build's PRs
land in `acme/ios-app` and need the same follow-up when they are closed or
merged. The same routing label limits it to factory PRs instead of every
merge in the repository.

Widen these filters carefully. Dropping the `labels` key from the mention
triggers makes any `@warp-factory` mention start work, and dropping
`mentioned` as well would fire on every mention of anyone.

## Make it yours

1. Replace `acme/api-service`, `acme/webapp`, and `acme/ios-app` with
   repositories your installation can reach. `acme/api-service` and
   `acme/webapp` appear in `factory.yaml`, both GitHub automations, and
   (`api-service` only) the `linux-build` setup command; `acme/ios-app`
   appears in `factory.yaml`, `agents/foreman/agent.md`,
   `agents/mobile-build/agent.md`, and the `github-pr-closed-or-merged`
   automation, but not the mention automation. If you have no macOS work,
   delete `agents/mobile-build/`, `runners/macos-build.yaml`, and the
   `ios-app` entry (including from `github-pr-closed-or-merged`) together.
2. Connect Slack and Linear to your Warp team; the `integrations` list only
   declares that this factory uses them.
3. Replace the two skill stubs with your real conventions.
4. Narrow intake as needed. Filters combine with AND, and an absent field is
   a wildcard. For example, to route only one Linear team:

   ```yaml
   triggers:
     - provider: linear
       event: agent_session_created
       filter:
         teams: [Platform]
   ```

   `teams`, `projects`, and `states` take plain name lists that the server
   resolves against Linear when the definition is applied, so add them only
   after Linear is connected, or the apply will fail on the unresolved name.

## Using Jira instead of Linear

A factory can attach Linear or Jira, not both. To swap, change the
integration to `- type: jira`, replace `automations/linear-agent-sessions`
with a `jira` / `agent_session_created` trigger (filters use `project_keys`
rather than team names), and reword the triage prompt's Linear references.

## Other trigger shapes

Intake is a set of triggers, so a factory can be pointed at other event
shapes without changing its agents. For example, to review pull requests
humans open, rather than only factory PRs, route them straight to the
reviewer with the automation's `agent:` field:

```yaml
agent: reviewer
triggers:
  - provider: github
    event: pull_request_opened
    filter:
      repos: [acme/api-service]
      base_branches: [main]
      labels:
        not_in: [wip]
```

`pull_request_synchronized` fires on every push to an open PR, and
`pull_request_opened` fires for drafts too, so the opt-out label is the
practical volume control. An automation fires once per delivery even when
several of its triggers match the same event.

For recurring work with no human-facing intake, such as a dependency sweep,
see the cron automation in
[`06-common-automations`](../06-common-automations).
