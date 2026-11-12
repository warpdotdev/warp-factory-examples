# 12: GitHub assigned issue

Assign a labeled GitHub issue to the factory to request one bounded change.
The result is a pull request linked on the issue. A human reviews and merges.
This example replaces the readiness-label trigger in
[`01-single-repo-quickstart`](../01-single-repo-quickstart) with assignment.

## What this example shows

- The `github` / `issue_assigned` trigger filters intake to one
  repository, the factory's own GitHub identity, and the factory's routing
  label.
- The `assignees` filter lists both the current `warp` and earlier
  `warp-factory` logins.
- Filter keys combine with AND. An assignment that misses a filter
  starts no run through this automation and posts no explanation.
- The foreman prompt checks scope because an assignment carries no message.
  The issue text is the whole request.
- Assignment-based intake suits teams that dispatch work from an assignee
  queue. The label-based intake in `01` uses readiness as the signal instead.

## Directory structure

```
factory.yaml
agents/
  foreman/agent.md        FOREMAN, scope check, routes work, reports on the issue
  implementer/agent.md    IMPLEMENT, issue → PR on factory/issue-<n>-<slug>
automations/
  issue-assigned/automation.md   github/issue_assigned; repos + assignees + labels
runners/
  linux-small.yaml        2 vCPU / 4 GB, node:22-bookworm-slim
```

## How intake is routed

The one automation watches `acme/api-service` for `issue_assigned` events.
Its three filter keys combine with AND, so an event starts work only when
all three match:

- The `repos: [acme/api-service]` filter sets the repository scope.
  Assignments in any other repository never reach this factory, even one the
  same GitHub App installation covers. Warp routes GitHub events only for
  repositories that belong to the factory, so this list and `repositories` in
  `factory.yaml` must agree.
- The `assignees: [warp, warp-factory]` filter sets the identity scope. It
  matches the login that was just assigned, not the issue's whole assignee
  list. Keep the current `warp` and earlier `warp-factory` logins. Assigning
  another login does not match.
- The `labels: ["factory:Acme"]` filter requires the routing label,
  `factory:<alias>`. Warp creates this label with the factory, and the
  foreman keeps it on
  everything it touches. Because filters combine with AND, the label must
  already be on the issue when the assignment happens. Apply it first, then
  assign.

Events that do not match every filter are handled as follows.

- An assignment to the factory on an issue without the label is silently
  dropped. No run starts, nothing is posted on the issue, and nothing appears
  in the dashboard. An unlabeled `@warp` mention can still be routed to a
  single accessible factory ([mention
  routing](https://docs.warp.dev/factories/integrations/github/#mention-the-factory)).
  An assignment has no such fallback. Add the label, then unassign and assign
  again. The original event is not replayed.
- Assigning a different user does not trigger work, even on a labeled issue.
  The same applies when the factory is already assigned and a teammate is
  added later, because the event carries the teammate's login.
- Assigning a pull request does not trigger work. That is a separate event,
  `pull_request_assigned`, with the same filter keys.
  [`02-sdlc-issue-to-pr`](../02-sdlc-issue-to-pr) declares it alongside
  `issue_assigned` and the two mention events in one automation.
- An assignment made by a bot or app, such as an auto-assign action, is
  dropped because GitHub triggers skip bot senders by default
  (`skip_bots: all`). Set `skip_bots: self` or `none` in the filter to admit
  them. See [bot
  events](https://docs.warp.dev/factories/integrations/github/#events-from-bots-dont-start-work).

Decide deliberately whether to widen these filters. Dropping `labels` makes
every assignment of the factory in the repository start work. Dropping
`assignees` would start work whenever anyone is assigned anything in the
repository. The optional `authors` key narrows the other way, to issues opened
by specific logins. See [events and
filters](https://docs.warp.dev/factories/automation-triggers/#github) for
every key this event accepts.

## Choose assignment-based or label-based intake

Label-based intake
([`01-single-repo-quickstart`](../01-single-repo-quickstart), `issue_labeled`
with `factory-ready`) makes readiness the signal. The label can be applied
during triage or bulk processing, leaving the assignee field for the human
responsible for the outcome.

Assignment-based intake starts when a maintainer assigns the factory.
The routing label must already be present. Prefer it when your team
dispatches work from an assignee queue.

Inspect existing automations before adding either route. Reuse or narrow
setup-seeded handlers and preserve their unrelated triggers. Different
labels alone do not prevent an issue from matching both paths. If you keep
both, use these `labels` matchers alongside their existing filters:

Label-based `issue_labeled` route:

```yaml
labels:
  in: [factory-ready]
  not_in: ["factory:Acme"]
```

Assignment-based `issue_assigned` route:

```yaml
labels:
  in: ["factory:Acme"]
  not_in: [factory-ready]
```

Append to existing exclusions rather than replacing them. An issue carrying
both labels matches neither path. The committed assignment-only automation
does not require this dual-route adaptation.

## Runner configuration

Both agents use `linux-small`, with 2 vCPUs, 4 GB of memory, and the
`node:22-bookworm-slim` image. The image provides Node and npm.

## Customize the example

Copy the entire example directory into your repository before making these
changes. See [Use an example](../../README.md#use-an-example) for the shared
setup procedure.

1. Replace `acme/api-service` in `factory.yaml` and
   `automations/issue-assigned/automation.md` with a repository your Warp
   team's GitHub App installation can reach. Change both or the trigger
   never fires.
2. Set `alias` in `factory.yaml` to the foreman name you want.
3. Change the label in `automations/issue-assigned/automation.md` to match
   the alias. It is always `factory:<alias>`. Warp creates the label when
   the factory is created. If you rename the alias later, delete the old
   label by hand.
4. Leave `assignees: [warp, warp-factory]` as it is.
5. Confirm that the identity is assignable. Open any issue in the repository
   and check that `warp` is offered in the assignee picker. GitHub only offers
   accounts eligible for assignment. App installation and account
   assignability are separate requirements. If `warp` is missing, ask an
   administrator to check [GitHub's assignment
   requirements](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/assigning-issues-and-pull-requests-to-other-github-users),
   or use label-based intake. Do not grant write access solely to enable
   assignment.
6. Have each person who will assign issues connect their GitHub account to
   Warp and confirm their membership in the factory's Warp team. The run is
   attributed to that account.
7. Replace `dockerImage` in `runners/linux-small.yaml` with an image for your
   stack.
8. Optionally, change `agentDefaults.model` to another Warp Agent model ID.

## Validate the example

From the repository root:

```bash
python3 scripts/validate_factory_files.py examples/12-github-assigned-issue
```

A pass means the definition files parse and every trigger, filter key, and
field is one the server accepts. It does not prove that `acme/api-service`
exists, that the GitHub App covers it, or that `warp` can be assigned there.
Those are checked when the definition is applied and on the first real
event. Schema validation alone does not prove prompt behavior.

## Register the factory

Follow [Use an example](../../README.md#use-an-example) to copy this directory
into your definition repository, customize it, commit and push the files,
and create a factory with a GitHub-backed definition pointing at your copy.
The registered root is the directory containing `factory.yaml`, not
necessarily the repository root. Pushes to the production branch sync the
definition after the `warp/factory-config` check passes.

## Test the factory

### Assign a sample issue

Prepare issue #42 in `acme/api-service`, already labeled `factory:Acme`,
with this body.

> **Return 400 for unknown `currency` codes on `POST /invoices`**
>
> `POST /invoices` accepts any string in `currency` and stores it. Validate
> it against the ISO 4217 list in `src/money/currencies.ts` and reject
> anything else with `400` and the body `{"error": "unsupported_currency"}`.
> Lowercase codes are accepted and normalized to uppercase. Add tests for a
> valid code, an unknown code, and a lowercase code.

A maintainer assigns the issue to `warp`. You should see the following
results in order.

1. A work item appears in the factory's dashboard with the issue as its
   source.
2. The factory posts a comment on #42 restating the deliverable, along the
   lines of "Deliverable: `POST /invoices` rejects `currency` values not in
   `src/money/currencies.ts` with 400 and `{"error": "unsupported_currency"}`,
   and uppercases lowercase codes. Verification: tests for valid, unknown,
   and lowercase codes must pass."
3. The factory creates a branch `factory/issue-42-unsupported-currency` and a
   pull request against the default branch, carrying the `factory:Acme`
   label, with `Closes #42` and the test output in its description.
4. The factory posts a final comment on #42 with the pull request link and
   a one-line summary of the change.
5. A human reviews and merges. The factory never merges.

When the issue is out of scope, for example "Investigate why invoice totals
drift at month boundaries", the foreman posts one comment naming the failing
check ("this asks for an investigation rather than a bounded change; once
the cause is known, file the fix as its own issue") and stops. It creates no
branch or pull request. The assignment stays in place. Edit the issue, then
unassign and reassign `warp` to send a fresh event.

### Check the first-run results

The first real run should prove three things:

1. A small labeled issue assigned to `warp` produces a
   work item, a restatement comment, a pull request that links the issue,
   and a closing comment with the link.
2. Assigning `warp` to an unlabeled issue starts nothing,
   and assigning a teammate to a labeled issue starts nothing. Check the
   dashboard's runs page, not only the issue, so a silent drop is
   distinguishable from a run that failed.
3. Assigning `warp` to a labeled issue that asks a
   question produces one comment and no branch.

If both routes are configured, also prepare an issue with both labels
before assigning the factory. Neither route should handle that assignment.
Reapply the readiness label while the routing label remains. The label
route must not handle it either. Check for other matching automations.

Pick a first issue that a reviewer can verify in minutes, with acceptance
criteria written down.

## Set up with an agent

<!-- terminology-allow-begin -->
Paste this into your factory's foreman, the factory web composer, or a coding
agent connected to [Factory
MCP](https://docs.warp.dev/factories/factory-mcp/):
<!-- terminology-allow-end -->

```text title="Set up assignment-based GitHub intake"
Read the example at
https://github.com/warpdotdev/warp-factory-examples/tree/main/examples/12-github-assigned-issue
and set up the same factory for my repository OWNER/REPO.

Keep the tree's shape: one foreman, one implementation agent, one
github/issue_assigned automation, one Linux runner. Replace:
- acme/api-service with OWNER/REPO, in factory.yaml and in
  automations/issue-assigned/automation.md
- the alias Acme with ALIAS, and the label factory:Acme with factory:ALIAS
- the runner's dockerImage with an image that has my toolchain

Keep assignees: [warp, warp-factory] exactly as it is.
Reuse or narrow existing assignment handlers instead of adding duplicates;
preserve unrelated triggers. If readiness-label intake is also enabled,
exclude its readiness label from the assignment route and the routing
label from the readiness route. Preserve existing exclusions.

Validate the result with scripts/validate_factory_files.py from the
warp-factory-examples repository before applying it. Then give me the
exact steps to test it: one labeled issue assigned to warp that should
start work, one unlabeled issue that should not, and, when both routes are
enabled, an issue carrying both labels that neither route should handle.
List manual access steps separately; do not grant extra permissions or
apply the definition without my approval.
```
