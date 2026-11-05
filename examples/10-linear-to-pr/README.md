# 10: Linear to PR

A delegated Linear issue is the only way work enters this factory. Someone
delegates an issue to the Warp app, or mentions it in a comment, and Linear
opens an agent session; the session reaches this factory because the issue
belongs to the team the automation filters on. The foreman acknowledges in
the session, the implementation agent opens a pull request, and the foreman
attaches the PR to the issue and posts the link back in the session. A human
reviews and merges.

## What it demonstrates

- `linear` / `agent_session_created` as a single-source intake, with the
  `teams` filter deciding which sessions reach this factory.
- Name-based Linear filters (`teams`, `projects`) that the server resolves
  against your connected Linear workspace when the definition is applied,
  not when it is validated.
- The `linear` entry under `integrations` in `factory.yaml`, and what
  connecting Linear does and does not grant.
- The acknowledge → implement → link-back loop inside one agent session,
  including what the foreman does when an issue has no acceptance criteria
  or is out of scope.
- The [`01-single-repo-quickstart`](../01-single-repo-quickstart) topology
  with the intake swapped from a GitHub label to a Linear delegation.

## Tree

```
factory.yaml              integrations: linear; one repository
agents/
  foreman/agent.md        FOREMAN, acknowledges, dispatches, links the PR back
  implementer/agent.md    IMPLEMENT, one issue → one PR
automations/
  linear-delegation/automation.md   linear/agent_session_created, one team
runners/
  linux-standard.yaml     4 vCPU / 8 GB, node:22-bookworm-slim
```

## How Linear intake is routed

Connecting Linear to your Warp team authorizes the Warp app for your Linear
workspace (once per workspace) and asks which Linear teams should trigger
the factory. After that, delegating an issue to the Warp app, or mentioning
the app in an issue comment, makes Linear open an agent session. In this
tree, the automation below is the route a session takes into the factory:

```yaml
triggers:
  - provider: linear
    event: agent_session_created
    filter:
      teams: [your-linear-team]
```

- `teams` is a plain list of Linear team names. The server resolves each
  name against Linear when the definition is applied, and the apply fails if
  a name does not resolve to exactly one team the app can see. `projects`
  works the same way for project names. The local validator reports both as
  deferred and does not check them, so connect Linear and use your real
  team name before the first apply.
- Filter keys combine with AND, and an absent key is a wildcard. Dropping
  `teams` would route every agent session the app receives, from any team,
  into this factory. To narrow further, add `projects: [Payments]`,
  `labels: [factory-ready]` (the issue's current labels), or
  `keywords: [implement]` (matched against the text that opened the
  session).
- `states` is not accepted on `agent_session_created`; it is an alias for
  `state_ids`, which exists only on the issue events and `comment_created`.
  To gate intake on a workflow state instead of on delegation, use
  `issue_state_changed` with `teams: [your-linear-team]` and
  `states: [Ready for Engineering]`. Both aliases resolve at apply time like
  `teams`.
- A session from a team not in `teams` does not match, and nothing in this
  factory runs. The session still exists in Linear, where the Linear
  integration's default handling applies to it instead of this tree.
- Agent sessions need the session creator's Linear user linked to a Warp
  account. Without that link, Linear shows an authentication prompt instead
  of starting work.
- Replies in the session continue the same run; they do not create a second
  work item. The factory's own Linear activity never triggers automations,
  so the foreman's acknowledgement cannot start a loop.
- This tree has no `comment_created` automation on purpose. A comment that
  mentions the app already opens an agent session, and a second route
  matching the same comment would start a second run.

For the full list of events and keys, see
[events and filters for factory automations](https://docs.warp.dev/factories/automation-triggers/#linear).

## Make it yours

1. Replace `acme/api-service` in `factory.yaml` with a repository your Warp
   team's GitHub installation can reach. Branches and pull requests use that
   installation's credentials; connecting Linear grants no repository
   access.
2. Connect Linear to your Warp team, either in the factory's setup wizard or
   from its settings, following the
   [Linear integration guide](https://docs.warp.dev/factories/integrations/linear/).
   The `- type: linear` entry under `integrations` in `factory.yaml` only
   declares that this factory uses the connection. After the first apply,
   open the factory's Automations page and confirm that exactly one
   automation listens for Linear agent sessions: if connecting Linear also
   seeded a default agent-session automation, a delegation would start two
   runs.
3. Replace `your-linear-team` in
   `automations/linear-delegation/automation.md` with the exact name of a
   Linear team the Warp app has access to. The apply fails on an unresolved
   name, so do this after step 2.
4. Have each person who will delegate issues link their Linear user to
   their Warp account. The first delegation from an unlinked user shows the
   authentication prompt in Linear; completing it and delegating again is
   enough.
5. Swap the runner's `dockerImage` in `runners/linux-standard.yaml` for
   your stack. The image, not a setup command, is where the toolchain comes
   from. Optionally change `agentDefaults.model` (any Warp Agent model ID).
6. Adjust `alias`; it is the factory's display handle, and the dashboard
   labels it "Foreman name".
7. The foreman leaves the issue's workflow state alone. To move the issue
   when the PR opens, add the transition to step 5 of
   `agents/foreman/agent.md` (for example "set the issue to In Review").
   That change is prompt policy, not an enforced rule.

## Sample task and expected output

In a Linear team named `Platform` (with `teams: [Platform]` applied), create
this issue and delegate it to the Warp app:

```text
ENG-142  Reject unsupported currency codes on POST /invoices

POST /invoices accepts any string in `currency`. Reject anything that is
not USD, EUR, or GBP.

Acceptance criteria:
- A request with an unsupported `currency` returns 400 with
  {"error": "unsupported_currency"}.
- Requests with USD, EUR, or GBP behave as before.
- Tests cover one accepted code and one rejected code.
```

What you should see:

1. Before anything happens in the repository, one acknowledgement in the
   issue's agent session that restates the deliverable: "Picking this up:
   POST /invoices will return 400 `unsupported_currency` for anything other
   than USD, EUR, or GBP, with tests for both paths."
2. On `acme/api-service`, a branch named like
   `eng-142-reject-unsupported-currency` and a pull request titled
   "Reject unsupported currency codes on POST /invoices (ENG-142)" that
   contains the change, the two tests, and a description listing the test
   and lint commands that were run and their results.
3. The pull request attached to ENG-142, and a final session message with
   the PR link and a one-line verification summary.
4. ENG-142 still in the workflow state it was in when you delegated it, and
   no merge. On the factory's Runs page, one foreman run with one child
   implementation run.

Two variations show the foreman's stop conditions:

- Out of scope: delegate "ENG-143 Add a currency picker to the billing page
  in `acme/webapp`". The foreman replies in the session that `acme/webapp`
  is not a repository of this factory, suggests where the issue belongs, and
  stops. No branch, no PR.
- No acceptance criteria: delegate "ENG-144 Invoices are broken for some
  currencies" with no description. The foreman asks in the session which
  currencies are affected and what should happen for unsupported ones, then
  stops. Replying in the session continues the same run; it does not open a
  second one.

## Validate it

```bash
python3 scripts/validate_factory_files.py examples/10-linear-to-pr
```

A passing run prints `factory files are valid.`, the disclosure that
state-dependent apply checks were not run, and one deferred line:

```text
deferred: automations/linear-delegation/automation.md triggers[0].filter.teams (linear_name_alias) is resolved when the plan is applied
```

That deferral is the point: the validator proves the file shape and the
event and filter names, and leaves the team name, the Linear connection,
and repository reach to the apply.

A first real run should prove three things the validator cannot:

1. Routing: delegating an issue from your team creates a run on the
   factory's Runs page and an acknowledgement in the session.
2. The deliverable: a PR on your repository, attached to the issue, with
   verification evidence in its description.
3. The negative case: delegating an issue from a team not in `teams` starts
   nothing in this factory.

## Set it up with a prompt

Paste this into your factory's foreman, the factory web composer, or
[a coding agent connected to your factory over MCP](https://docs.warp.dev/factories/factory-mcp/),
after filling in the two angle-bracket values:

```text title="Set up Linear delegation to PR for my repository"
Read https://github.com/warpdotdev/warp-factory-examples/tree/main/examples/10-linear-to-pr
and set up the same factory for my repository <owner/repo>, whose issues
live in the Linear team <team name>. Keep the tree shape: one foreman, one
implementation agent, one `linear` / `agent_session_created` automation
filtered to my team, and one Linux runner. Replace `acme/api-service` with
my repository, `your-linear-team` with my team name, and the runner's
dockerImage with an image that has my stack's toolchain. Before applying,
confirm Linear is connected to my Warp team and that only one automation
routes Linear agent sessions to this factory. Validate the definition, then
tell me how to delegate a first test issue and exactly what I should see in
the issue's agent session and on the pull request.
```
