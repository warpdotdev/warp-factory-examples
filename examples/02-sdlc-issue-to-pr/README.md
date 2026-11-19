# 02: Issue to pull request

This example is a complete engineering factory that takes requests from
Slack, Linear, and GitHub through triage, specification when needed, and
implementation. A separate agent reviews the changes before the factory
hands the pull request to a human.

The inline Blueprint in `factory.yaml` owns the workflow. The worker files
retain the default roles plus a mobile worker and their execution settings.
For the historical default-agent snapshot, see
[`00-warp-default-agents`](../00-warp-default-agents).

The stages are `intake`, `triage`, `spec`, `implement`, `mobile-build`,
`review`, `handoff`, and `completion`. Planning takes priority when explicitly
requested or when work is large or ambiguous. `spec-review` waits for approval,
changes, or cancellation of a committed spec revision. Review can open
`human-decision`; revisions return to the responsible worker and independent
review. `handoff-decision` waits for a revision, merge or closure information,
or cancellation. Completion inspects every required PR; closed is not merged.

## What this example shows

- All five default agents (`FOREMAN`, `TRIAGE`, `SPEC`, `IMPLEMENT`, and
  `REVIEW`) appear, along with a `CUSTOM` agent for work the default agents
  don't cover. The `triage` and `reviewer` agents override the default
  `model`. The reviewer uses a different model than the implementer to reduce
  shared blind spots.
- Three runners differ by size, image, and operating system, and each agent
  can select the one that suits its stage. See
  [Runner configuration](#runner-configuration).
- Requests come in from Slack, Linear, and GitHub, and a follow-up automation
  handles closed or merged pull requests. The directory structure below lists
  each automation's trigger.
- The `integrations` list declares `slack` and `linear`, and the factory
  covers multiple repositories.
- Skills under `skills/` are available to every agent. Skills under
  `agents/<name>/skills/` are available only to that agent.

## Directory structure

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
  github-pr-closed-or-merged/  inspect the full linked PR set
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

## Runner configuration

Each agent chooses its own compute. This factory uses three runners because
its stages have different needs:

- `linux-standard` (4 vCPU / 8 GB, `ubuntu:24.04`) is the `agentDefaults`
  runner, which the foreman, triage, spec, and review agents inherit. These
  stages read code and write prose.
- `linux-build` (8 vCPU / 16 GB, `golang:1.24-bookworm`) runs implementation,
  which compiles code and runs tests. The image provides the toolchain, so use
  `setupCommands` only for what the image lacks, and write them defensively.
  A setup command that exits non-zero fails the whole sandbox.
- `macos-build` (6 vCPU / 14 GB, `macos/aarch64`) runs the `mobile-build`
  agent. macOS sandboxes are virtual machines, not containers, so this runner
  declares no `dockerImage`. It takes an optional `mac.version` instead and
  accepts only a fixed set of shapes. macOS is `aarch64`-only.

Linux shapes must be powers of two. A runner named by an agent overrides the
runner in `agentDefaults`.

## How GitHub intake is routed

The mention and assignment automation mirrors the default automation that
Warp creates during setup. It watches only `acme/api-service` and
`acme/webapp`, so GitHub mentions and assignments in `acme/ios-app` don't
start work. GitHub intake for iOS work isn't set up.

Filter keys combine with AND. Each trigger combines a mention or assignment
filter with a label filter:

- `mentioned: [warp, warp-factory]` and `assignees: [warp, warp-factory]`
  restrict the trigger to the GitHub handles Warp Factories answers to.
  The current handle is `warp`. The earlier handle, `warp-factory`, still
  matches. Both are product constants, not placeholders.
  Without the `mentioned` key, `issue_mentioned` fires when anyone is
  @-mentioned in the repositories.
- `labels: ["factory:Acme"]` is the factory's routing label,
  `factory:<alias>`. Because filters combine with AND, the label must be on
  the issue or pull request before a mention or assignment can trigger the
  factory. A `@warp` mention on an unlabeled item is silently
  dropped, so apply the label when you open the item or before the first
  mention. After that, the foreman keeps the label on everything it touches,
  so later mentions and assignments keep matching.

The closed-or-merged follow-up automation watches `acme/api-service`,
`acme/webapp`, and `acme/ios-app`. The `mobile-build` agent's pull requests
land in `acme/ios-app` and need the same follow-up when they are closed or
merged. The same routing label limits the automation to factory pull requests
instead of every merge in the repository.

Widen these filters carefully. If you drop the `labels` key from the mention
triggers, any `@warp` mention starts work. If you also drop
`mentioned`, the trigger fires on every mention of anyone.

## Customize the example

1. Replace `acme/api-service` and `acme/webapp` with repositories that your
   installation can access. They appear in `factory.yaml` and in both GitHub
   automations. The repository name `api-service` also appears in the
   `linux-build` setup command.
2. Replace `acme/ios-app` with a repository that your installation can
   access. It appears in `factory.yaml` (repository and mobile stage),
   `agents/mobile-build/agent.md`, and the `github-pr-closed-or-merged`
   automation, but not in the `github-mention-assign` automation.
3. If you don't have macOS work, delete `agents/mobile-build/` and
   `runners/macos-build.yaml`, and remove the `ios-app` entry from
   `factory.yaml` and from the `github-pr-closed-or-merged` automation. Make
   all of these changes together. Also remove the `mobile-build` stage and
   every route, input, output, and instruction that names mobile work.
   Route non-mobile implementation directly to `review`; remove mobile-only
   branches from intake, triage, spec, review, and handoff.
4. Connect Slack to your Warp team, or remove its integration declaration and
   both Slack automations together.
5. Connect Linear to your Warp team, or remove its declaration and automation
   together for GitHub-only work. The `integrations` list declares which
   integrations the factory uses, but doesn't connect them.
6. Replace the two skill stubs, `skills/repository-conventions/SKILL.md` and
   `agents/implementer/skills/testing-standards/SKILL.md`, with your real
   conventions.
7. Optionally, narrow intake. Filters combine with AND, and an absent field
   matches everything. For example, to route only one Linear team, add a
   `filter` to the trigger:

   ```yaml
   triggers:
     - provider: linear
       event: agent_session_created
       filter:
         teams: [Platform]
   ```

   The `teams` and `projects` filters take plain lists of names.
   Warp resolves the names against Linear when you apply the definition, so
   add them only after you connect Linear. Otherwise, applying the definition
   fails on the unresolved name.

   The `agent_session_created` event also accepts `labels`, `keywords`, and
   `creator_ids`. It rejects a `states` filter. Use `states` with
   `issue_state_changed` instead.

## Use Jira instead of Linear

A factory can attach Linear or Jira, but not both. To use Jira instead of
Linear:

1. Change the integration in `factory.yaml` to `- type: jira`.
2. Replace `automations/linear-agent-sessions` with an automation that uses
   the `jira` provider and the `agent_session_created` event. Jira filters use
   `project_keys` instead of team names.
3. Update tracker references in the `triage` stage and its worker prompt.

## Configure additional triggers

For human-authored PRs that need only advisory review, use
[`04-code-review-only`](../04-code-review-only). Do not send them through this
implementation lifecycle. An automation fires once per delivery even if
several of its triggers match; that does not prove deduplication of distinct
deliveries.

For recurring work that doesn't start from a human request, such as a
dependency sweep, see the cron automation in
[`06-common-automations`](../06-common-automations).
