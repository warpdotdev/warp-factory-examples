# 12: GitHub assigned issue

Assign a labeled GitHub issue to the factory to request one bounded change.
The result is a pull request linked on the issue; a human reviews and merges.
This example replaces the readiness-label trigger in
[`01-single-repo-quickstart`](../01-single-repo-quickstart) with assignment.

## What it demonstrates

- `github` / `issue_assigned` as an intake trigger, filtered to one
  repository, the factory's own GitHub identity, and the factory's routing
  label.
- Why `assignees` lists two handles, `warp` and `warp-factory`.
- AND semantics across filter keys: an assignment that misses a filter
  starts no run through this automation and posts no explanation.
- A foreman prompt built around a scope check, because an assignment carries
  no message: the issue text is the whole request.
- When to prefer assignment-based intake over the label-based intake in
  `01`.

## Tree

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

- `repos: [acme/api-service]`: the repository scope. Assignments in any
  other repository never reach this factory, even one the same GitHub App
  installation covers. Warp routes GitHub events only for repositories that
  belong to the factory, so this list and `repositories` in `factory.yaml`
  must agree.
- `assignees: [warp, warp-factory]`: the identity scope. `assignees` matches
  the login that was just assigned, not the issue's whole assignee list.
  Keep the current `warp` and earlier `warp-factory` logins. Assigning
  another login does not match.
- `labels: ["factory:Acme"]`: the routing label, `factory:<alias>`. Warp
  creates this label with the factory, and the foreman keeps it on
  everything it touches. Because filters combine with AND, the label must
  already be on the issue when the assignment happens. Apply it first, then
  assign.

What happens to an event that does not match every filter:

- The factory is assigned to an issue without the label: silently dropped.
  No run starts, nothing is posted on the issue, and nothing appears in the
  dashboard. An unlabeled `@warp` mention can still be routed to a single
  accessible factory
  ([mention routing](https://docs.warp.dev/factories/integrations/github/#mention-the-factory));
  an assignment has no such fallback. Add the label, then unassign and
  assign again. The original event is not replayed.
- A different user is assigned: no trigger, even on a labeled issue. The
  same applies when the factory is already assigned and a teammate is added
  later, because the event carries the teammate's login.
- A pull request is assigned: no trigger. That is a separate event,
  `pull_request_assigned`, with the same filter keys.
  [`02-sdlc-issue-to-pr`](../02-sdlc-issue-to-pr) declares it alongside
  `issue_assigned` and the two mention events in one automation.
- The assignment is made by a bot or app, such as an auto-assign action:
  dropped, because GitHub triggers skip bot senders by default
  (`skip_bots: all`). Set `skip_bots: self` or `none` in the filter to admit
  them; see
  [bot events](https://docs.warp.dev/factories/integrations/github/#events-from-bots-dont-start-work).

Widen these filters on purpose. Dropping `labels` makes every assignment of
the factory in the repository start work, which is sometimes exactly what
you want and is the main decision to make deliberately. Dropping `assignees`
would start work whenever anyone is assigned anything in the repository. The
optional `authors` key narrows the other way, to issues opened by specific
logins. See
[events and filters](https://docs.warp.dev/factories/automation-triggers/#github)
for every key this event accepts.

## Assignment or label?

Label-based intake ([`01-single-repo-quickstart`](../01-single-repo-quickstart),
`issue_labeled` with `factory-ready`) makes readiness the signal. The label
can be applied during triage or bulk processing, leaving the assignee field
for the human responsible for the outcome.

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

## Make it yours

1. Replace `acme/api-service` in `factory.yaml` and
   `automations/issue-assigned/automation.md` with a repository your Warp
   team's GitHub App installation can reach. Change both or the trigger
   never fires.
2. Set `alias` in `factory.yaml` to the foreman name you want, and change
   the label in `automations/issue-assigned/automation.md` to match: it is
   always `factory:<alias>`. Warp creates the label when the factory is
   created. If you rename the alias later, delete the old label by hand.
3. Leave `assignees: [warp, warp-factory]` as it is. Then confirm the
   identity is assignable: open any issue in the repository and check that
   `warp` is offered in the assignee picker. GitHub only offers accounts
   eligible for assignment. App installation and account assignability are
   separate requirements. If `warp` is missing, ask an administrator to
   check [GitHub's assignment requirements](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/assigning-issues-and-pull-requests-to-other-github-users),
   or use label-based intake. Do not grant write access solely to enable
   assignment.
4. Whoever assigns the issue needs a GitHub account connected to Warp and
   membership in the factory's Warp team. The run is attributed to that
   account.
5. Swap the runner's `dockerImage` in `runners/linux-small.yaml` for your
   stack, and optionally change `agentDefaults.model` (any Warp Agent model
   ID).

## Sample task and expected output

Input: issue #42 in `acme/api-service`, already labeled `factory:Acme`,
with this body:

> **Return 400 for unknown `currency` codes on `POST /invoices`**
>
> `POST /invoices` accepts any string in `currency` and stores it. Validate
> it against the ISO 4217 list in `src/money/currencies.ts` and reject
> anything else with `400` and the body `{"error": "unsupported_currency"}`.
> Lowercase codes are accepted and normalized to uppercase. Add tests for a
> valid code, an unknown code, and a lowercase code.

A maintainer assigns the issue to `warp`. In order, you should see:

1. A work item in the factory's dashboard with the issue as its source.
2. A comment on #42 from the factory restating the deliverable, along the
   lines of: "Deliverable: `POST /invoices` rejects `currency` values not in
   `src/money/currencies.ts` with 400 and `{"error": "unsupported_currency"}`,
   and uppercases lowercase codes. Verification: tests for valid, unknown,
   and lowercase codes must pass."
3. A branch `factory/issue-42-unsupported-currency` and a pull request
   against the default branch, carrying the `factory:Acme` label, with
   `Closes #42` and the test output in its description.
4. A final comment on #42 with the pull request link and a one-line summary
   of the change.
5. A human reviews and merges. The factory never merges.

When the issue is out of scope, for example "Investigate why invoice totals
drift at month boundaries", the foreman posts one comment naming the failing
check ("this asks for an investigation rather than a bounded change; once
the cause is known, file the fix as its own issue") and stops. No branch, no
pull request. The assignment stays in place; edit the issue, then unassign
and reassign `warp` to send a fresh event.

## Validate it

From the repository root:

```bash
python3 scripts/validate_factory_files.py examples/12-github-assigned-issue
```

A pass means the tree parses and every trigger, filter key, and field is one
the server accepts. It does not prove that `acme/api-service` exists, that
the GitHub App covers it, or that `warp` can be assigned there. Those are
checked when the definition is applied and on the first real event.

Then register it: create a factory in Warp, choose a GitHub-backed
definition, and point it at your copy of this directory. The registered root
is the directory containing `factory.yaml`, not necessarily the repository
root. Pushes to the production branch sync the definition after the
`warp/factory-config` check passes.

The first real run should prove three things:

1. The positive path: a small labeled issue assigned to `warp` produces a
   work item, a restatement comment, a pull request that links the issue,
   and a closing comment with the link.
2. The negative paths: assigning `warp` to an unlabeled issue starts nothing,
   and assigning a teammate to a labeled issue starts nothing. Check the
   dashboard's runs page, not only the issue, so a silent drop is
   distinguishable from a run that failed.
3. The out-of-scope path: assigning `warp` to a labeled issue that asks a
   question produces one comment and no branch.

If both routes are configured, also prepare an issue with both labels
before assigning the factory: neither route should handle that assignment.
Reapply the readiness label while the routing label remains; the label
route must not handle it either. Check for other matching automations.

Pick the first issue deliberately: something a reviewer can verify in
minutes, with acceptance criteria written down.

## Set it up with a prompt

<!-- terminology-allow-begin -->
Paste this into your factory's foreman, the factory web composer, or a
coding agent connected to [Factory MCP](https://docs.warp.dev/factories/factory-mcp/):
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
