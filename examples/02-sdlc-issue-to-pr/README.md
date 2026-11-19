# 02: Issue to pull request

Route requests from Slack, Linear, and GitHub through triage, specification
when needed, implementation, and independent review. The foreman returns the
pull requests and check results in the original conversation. A person merges.

The Blueprint in `factory.yaml` defines the workflow. The files under `agents/`
configure the default roles and an additional agent for iOS work.
For the historical default-agent snapshot, see
[`00-warp-default-agents`](../00-warp-default-agents).

The stages are `intake`, `triage`, `spec`, `implement`, `mobile-build`,
`review`, `handoff`, and `completion`. Planning takes priority when explicitly
requested or when work is large or ambiguous. The `spec-review` gate waits for
approval of the committed spec, requested changes, or cancellation. A review
finding that needs your judgment opens `human-decision`. Corrections return to
the responsible worker and then to independent review. At `handoff-decision`,
you request a revision, report a merge or closure, or cancel. The `completion`
stage checks every required PR; closing a PR without merging it is not
successful completion.

## What this example shows

- All five default agents (`FOREMAN`, `TRIAGE`, `SPEC`, `IMPLEMENT`, and
  `REVIEW`) appear, along with a `CUSTOM` agent for work the default agents
  don't cover. The `triage` and `reviewer` agents override the default
  `model`. The reviewer uses a different model than the implementer.
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

## Exercise: plan and revise one PR

Use a disposable fork to document a validator command. The expected final
work diff is `README.md` plus one committed spec file. Your definition changes
belong in a separate repository, not in that work PR.

This draft exercise has not verified availability, team access, definition
application, the runner's tools, or the live approval and revision steps.
Confirm those prerequisites before treating it as runnable. The instructions
are not a record of a successful run. Apply a live definition only with
separate authorization.

### Prepare the two repositories

1. Complete [factory setup](https://docs.warp.dev/factories/quickstart/) for
   team access, GitHub, and usage. Grant the GitHub App access to both the
   work fork and definition repository, including issue, label, comment,
   branch, and PR operations.
2. Fork this repository into an account you control. On GitHub, enable
   **Issues** under the fork's **Settings** > **General**.
3. In a fresh local directory, create the fixed work baseline. Replace
   `YOUR_GITHUB_USER` with the fork's owner.

   ```bash
   git clone https://github.com/YOUR_GITHUB_USER/warp-factory-examples.git blueprint-work
   git -C blueprint-work switch -c blueprint-demo 76f0f06f59a3c3d5fc29eb7699fe281073fa58c1
   git -C blueprint-work push -u origin blueprint-demo
   ```

4. On GitHub, set the fork's default branch to `blueprint-demo`. Check that
   its README does not explain single-example validation or exit code 2.
5. Copy the definition and validation helper from the same
   [pinned revision](https://github.com/warpdotdev/warp-factory-examples/tree/81205a3c5a43e20cc6bd95b64bd8d3f7f098cdbb).
   You need Git and Python 3 locally. The `main` branch does not yet contain
   this Blueprint.

   ```bash
   git clone https://github.com/warpdotdev/warp-factory-examples.git blueprint-source
   git -C blueprint-source checkout --detach 81205a3c5a43e20cc6bd95b64bd8d3f7f098cdbb
   git clone DEFINITION_REPO_URL blueprint-definition
   cp -R blueprint-source/examples/02-sdlc-issue-to-pr/. blueprint-definition/
   ```

   `DEFINITION_REPO_URL` is your separate, empty definition repository.
   Keep its `.git` directory.

### Substitute the complete definition

In `blueprint-definition`, make these changes together:

1. In `factory.yaml`, replace the repository list with one entry for
   `YOUR_GITHUB_USER/warp-factory-examples` and set `alias: blueprint-demo`.
   Remove the `integrations` list and describe the GitHub-only README workflow
   in the factory description.
2. In both GitHub automation files, replace every `repos` list with your
   fork and every `factory:Acme` with `factory:blueprint-demo`. Preserve all
   mention, assignment, label, merged, and closed constraints.
3. Remove the optional mobile extension: `agents/mobile-build/`,
   `runners/macos-build.yaml`, and the `mobile-build` stage. Remove mobile-only
   routes from intake, triage, spec, review, and handoff. Make `implement.to`
   the scalar `review`. Remove mobile references from the remaining stage
   inputs, outputs, prompts, and the implementer worker. Keep every
   non-mobile approval, revision, review, and completion condition. Remove
   the mobile example from the closed-or-merged automation's instructions.
4. Remove `automations/slack-app-mentions/`, `automations/slack-dms/`, and
   `automations/linear-agent-sessions/`. Keep `triage`, using its GitHub-only
   issue path if needed. In `agents/foreman/agent.md`, replace the Slack and
   Linear communication instructions with replies in the original GitHub issue.
5. In both `runners/linux-standard.yaml` and `runners/linux-build.yaml`, set
   `platform.linux.dockerImage: python:3.12-bookworm`. Remove the Go
   `setupCommands` block from `linux-build.yaml` and update its description.
   Keep the Linux shape, architecture, worker bindings, models, and scorers.
   Confirm `git --version` and `python3 --version` in the selected runtime
   before running the exercise.
6. In `skills/repository-conventions/SKILL.md`, name the fork and
   `blueprint-demo` PR base. Require a draft through handoff and no merge.
   In `agents/implementer/skills/testing-standards/SKILL.md`, require
   `python3 scripts/check_conventions.py` for this copy-only task and honest
   reporting of the single-example validator result. Do not require an
   application build or add a redundant test for a prose edit.
7. Read `factory.yaml` beside every remaining worker and automation. Keep
   `spec-review`, `human-decision`, and `handoff-decision`. Their required
   answers and the same-PR revision path must remain intact.

### Validate, then apply only with authorization

From the directory containing the three checkouts, run:

```bash
python3 blueprint-source/scripts/validate_factory_files.py blueprint-definition --server-root https://app.warp.dev
```

Exit 0 means the parser checked the definition without diagnostics; it does
not prove that application or execution will succeed. On exit 1, fix the
diagnostics. On exit 2, restore access to the validator and retry. Continue
only after exit 0, then commit and push the customized definition.

With separate authorization, use the
[GitHub-backed setup path](https://docs.warp.dev/factories/factory-as-code/#where-the-definition-lives)
for a disposable factory. Confirm its applied definition revision and enabled
automations. In the actual work checkout confirm `blueprint-demo` is the
default branch and eventual PR base. Check the applied revision, not only the
commit you pushed.

### Request planning, approval, and a revision

1. In the work fork, open `Document single-example validation`. Apply
   `factory:blueprint-demo` before posting a new comment with `@warp` and:

   ```text
   In the root README, document:
   python3 scripts/validate_factory_files.py examples/02-sdlc-issue-to-pr.
   Explain that exit code 2 means validation did not run and is not a pass.
   Keep implementation changes in README.md; the committed specification is
   the only other allowed file. Propose a short plan and wait for my approval.
   Run python3 scripts/check_conventions.py and report the validator result
   honestly. Open a draft pull request. Do not merge.
   ```

2. Check for a spec-only draft and an unanswered `spec-review` request. Request
   one change before approval, for example: `@warp Add the exact validator
   command to the spec's acceptance criteria.` Confirm no implementation
   starts and the revised committed spec gets a new approval request.
3. Read the revised file. In the same issue, post a new `@warp` comment
   approving its linked PR and committed revision. Require the draft and
   no-merge limits again.
4. Inspect the draft's branch, PR number, head, actual checks, and independent
   review. Its only files are `README.md` and the one spec file.
5. In the same issue, post: `@warp Revise the same PR to explain that
   validation requires network access. Keep implementation in README.md and
   rerun the convention check. Do not merge.`
6. Confirm the branch and PR number stayed the same, the new head explains
   network access, and independent review covers that new head. Record both
   heads, checks, and run links. The foreman waits at `handoff-decision`; leave
   the PR unmerged and explicitly cancel the disposable trial when finished.

### Recover a blocked exercise

- **Validation fails or cannot run:** fix diagnostics or restore Python,
  network, and service access, then rerun the complete tree. Exit 2 is not a pass.
- **GitHub or another integration is unavailable:** grant access first, or
  remove the unused integration declaration and its automations together.
- **No work starts:** check the applied repository, routing label, and handle
  filters. Apply the label, then send a new mention. Nonmatching events do
  not use this specialized intake.
- **Approval is stale or missing:** read the open spec's current revision and
  answer its pending approval request in the original issue. A question is not
  approval.
- **The spec PR is closed:** restart on a replacement spec and approve it
  separately. Never transfer an old approval.
- **A required check fails:** keep the failure and correction request visible.
  Rerun the check and independently review the corrected head.
- **Work waits for a person:** answer the named pending gate in the original
  issue. A revision continues the same work, not a comparison trial.

For comparisons, use a separate issue, new PR, and newly approved spec from
the recorded baseline. Existing work retains its selected Blueprint after a
definition edit. Verify that separately; do not infer it from static parsing.
