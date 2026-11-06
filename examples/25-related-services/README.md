# 25: Related services

Two repositories that share one contract, in one factory. `acme/api-service`
is a Go API whose `openapi.yaml` is the contract; `acme/webapp` is a Node web
app that consumes it. A maintainer labels an issue in either repository, the
foreman decides which repository changes first, the implementer opens one
pull request per changed repository and verifies each with its own
bootstrap, tests, and contract check, the reviewer checks that the pair
agrees, and a human merges the two PRs in a documented order. Nothing here
makes the two merges atomic, and nothing pretends to. Work confined to one
repository produces one PR, checked for compatibility with the unchanged
repository, with no companion PR or merge order.

## What it demonstrates

- Two differently named repositories in `repositories`, both checked out
  under `/workspace` on every run, with a per-repository bootstrap in one
  runner. The image carries both toolchains.
- A provider-first decision the foreman makes before any code changes: the
  repository that provides the contract changes first, and only additively,
  so the deployed consumer keeps working between the two merges.
- One PR per repository, linked both ways, titled `[1/2]` and `[2/2]`, with
  the merge order and the compatibility note in every PR description when
  both repositories change. One-repository work has no pair-only requirements.
- A contract check in each repository that the implementer must run,
  including the consumer's check against the provider's current `main`,
  followed by regeneration and positive checks using the vendored schema.
- A reviewer whose only job is contract consistency, for one PR or a pair.
- Intake from a `factory-ready` label on an issue in either repository.

## Tree

```
factory.yaml                two repositories, alias Services
agents/
  foreman/agent.md          FOREMAN, decides the order, posts it on the issue
  implementer/agent.md      IMPLEMENT, one PR per repository, contract checks
  reviewer/agent.md         REVIEW, contract consistency for one PR or a pair
automations/
  issue-labeled/automation.md   github/issue_labeled, either repo, factory-ready
runners/
  linux-services.yaml       4 vCPU / 8 GB, warpdotdev/dev-go:1.23 (Go 1.23 + Node 22)
```

## Expected repository shape

The prompts name commands that the two placeholder repositories are assumed
to have. This is the shape; map each command to what your repositories
really run (see "Make it yours").

`acme/api-service`, the provider:

- `openapi.yaml` at the repository root describes the HTTP API. It is the
  contract.
- `go mod download` bootstraps; `go build ./... && go test ./...` is the
  normal check.
- `make contract-check` verifies the handlers against `openapi.yaml`, for
  example with a spec-versus-implementation test.

`acme/webapp`, the consumer:

- `api/openapi.yaml` is a vendored copy of the provider contract the app was
  built against. A paired consumer PR updates it; consumer-only work keeps it.
- `npm ci` bootstraps; `npm run lint && npm test` is the normal check.
- `npm run contract-check` regenerates the typed API client from
  `api/openapi.yaml` and type-checks every call site. `API_SCHEMA=<path>`
  points it at another schema, which is how the implementer checks the
  consumer against the provider's current `main`. This probe overwrites the
  generated client, so the implementer regenerates from the vendored schema
  and reruns the positive checks before publishing, even if the probe fails.

Both checkouts live under `/workspace`, so the consumer's checks can read
the provider's branch directly from `/workspace/api-service`. The runner
prefetches both repositories' dependencies and swallows its own failures (a
failing setup command fails the whole sandbox); the implementer re-runs the
real bootstrap in each repository it touches.

## How intake is routed

One automation, one trigger: `github` / `issue_labeled`, filtered to
`repos: [acme/api-service, acme/webapp]` and `labels: [factory-ready]`.
Filter keys combine with AND, so the event reaches the foreman only when the
`factory-ready` label is added to an issue in one of those two repositories.
GitHub labels are per repository, so the label has to exist in both.

Everything else is dropped before any agent runs: a `factory-ready` label on
an issue in a third repository, any other label on these issues, and a
`factory-ready` label on a pull request (`issue_labeled` is issues only; PR
labels are `pull_request_labeled`). Labels applied by bots are skipped by the
default `skip_bots: all`. Removing and re-adding the label fires the trigger
again.

The foreman does the second level of routing itself, from the issue text:
one repository, both repositories in provider-then-consumer order, or out of
scope. Issues it cannot place get one clarifying comment and no branch.

## The merge order

The factory never merges. For a two-repository change, a human merges in
this order:

1. Merge the provider PR, `[1/2]`, in `acme/api-service`. Its contract
   change only adds, so the deployed web app keeps working against the new
   API.
2. Wait for it to land, and to deploy if merging deploys.
3. Merge the consumer PR, `[2/2]`, in `acme/webapp`.

Between steps 1 and 3 the API serves the new field or endpoint and the
deployed web app ignores it. Merging the consumer first breaks it: the web
app would call a contract the deployed API does not serve yet, which is
exactly what the consumer's contract check against the provider's `main`
records in its PR. To back out, revert in reverse order: consumer first,
then provider.

For one-repository work, a human merges the single PR after its checks pass.
There is no `[n/2]` title, reciprocal link, or two-merge window. The PR explains
why the unchanged repository needs no change. A provider-only PR preserves
compatibility with the consumer; a consumer-only PR must pass its contract
check against the provider's current `main`, not depend on an unreleased API.

Breaking contract changes (removing, renaming, or retyping a field or
endpoint) are out of scope by design. The foreman comments on the issue with
what they need instead, a versioned endpoint or a coordinated deploy, and
stops.

## Make it yours

1. Replace `acme/api-service` (provider) and `acme/webapp` (consumer) with
   repositories your Warp team's GitHub installation can reach. They appear
   in `factory.yaml`, `automations/issue-labeled/automation.md`,
   `runners/linux-services.yaml`, `agents/foreman/agent.md`,
   `agents/implementer/agent.md`, and `agents/reviewer/agent.md`. Keep the
   roles straight: the provider owns the contract.
2. Replace the commands and paths with your repositories' real ones: the
   prefetch commands in `runners/linux-services.yaml`; the bootstrap, test,
   and contract-check commands and the schema paths in
   `agents/implementer/agent.md`; and the schema paths in
   `agents/reviewer/agent.md`. The commands assume the default branch is
   `main`. If your repositories have no contract check yet, add one before
   the first run; without it the implementer has nothing to prove the pair
   with.
3. Swap the runner's `dockerImage` if your stacks differ.
   `warpdotdev/dev-go:1.23` carries Go 1.23, Node 22, and Python 3;
   `warpdotdev/dev-full:latest` carries every language in Warp's prebuilt
   images; any public image with both toolchains works. See
   [runners](https://docs.warp.dev/factories/runners/).
4. Create the `factory-ready` label in both repositories, or change `labels`
   in `automations/issue-labeled/automation.md` to a label you already use.
5. Adjust `alias`; it becomes the factory's @-mention handle. Optionally
   change `agentDefaults.model` to any Warp Agent model ID.

## Sample task and expected output

A maintainer opens `acme/webapp#118`, "Show fulfillment status on the orders
page":

> The orders table should show each order's fulfillment status.
> `GET /orders` doesn't return it yet. Add an optional `status` field
> (`pending`, `shipped`, or `delivered`) to each order in `GET /orders`, and
> render it as a column in the orders table.

and labels it `factory-ready`. What you should see:

1. A foreman comment on #118: this changes the contract, `api-service`
   provides `status` and `webapp` consumes it, so the API changes first with
   an optional field and the web app follows.
2. A pull request in `acme/api-service`, `[1/2] Add optional status to GET
   /orders`, on branch `factory/118-order-status`. `openapi.yaml` gains the
   optional `status` enum on the order schema, with the handler change and
   a test. Its Verification section shows `go build ./... && go test ./...`
   and `make contract-check` passing and the schema diff as additive. It
   links #118 and the consumer PR.
3. A pull request in `acme/webapp`, `[2/2] Show order status in the orders
   table`, on a branch of the same name. `api/openapi.yaml` is updated, the
   client is regenerated, and the table gains the column and a test. Its
   Verification section shows `npm run lint && npm test` and
   `npm run contract-check` passing, and the same check against the
   provider's current `main` schema failing (`status` does not exist on the
   order type), recorded separately as the reason this PR merges second.
   After that probe, it shows `env -u API_SCHEMA npm run contract-check` and
   `npm run lint && npm test` passing again. The final generated client
   includes `status` from the updated vendored schema. It links #118 and the
   provider PR.
4. A reviewer report to the foreman, which never appears on GitHub. A
   finding such as "the table maps `pending` and `shipped` but the provider
   enum also has `delivered`" is unambiguous and goes back to the
   implementer, which fixes it on the same branch.
5. A final foreman comment on #118 with both PR links, the merge order, and
   the note that the deployed web app ignores `status` until its PR merges.
6. A human merges `[1/2]`, waits for it to land, and merges `[2/2]`.

For a consumer-only task, such as "Sort the orders table by order ID" using
an existing API field, the foreman dispatches only `webapp`. The implementer
leaves the vendored schema unchanged and opens one PR without `[n/2]` or a
Linked PR section. Its Verification section records the normal checks, a
passing probe against provider `main`, and passing positive checks after
regenerating from the vendored schema. The reviewer checks compatibility
with the unchanged API and the foreman posts the one PR link and results.
There is no provider PR or merge window. A provider-only internal fix follows
the same one-PR path with Go checks and `make contract-check`, plus evidence
that its unchanged or additive contract remains compatible with the consumer.

For an out-of-scope task, such as `acme/api-service#204`, "Rename
`customer_id` to `customerId` in all responses", labeled `factory-ready`, the
foreman comments that this is a breaking contract change that needs a
versioned endpoint or a coordinated deploy, which this factory does not do,
and stops. No branch and no PR are created.

## Validate it

```bash
python3 scripts/validate_factory_files.py examples/25-related-services
python3 scripts/check_conventions.py
```

The validator proves the tree parses. It does not prove the runner image,
the commands, or the repositories exist; the first real run does. Pick a
small additive change like the sample task and check four things: both
repositories are present under `/workspace` and the implementer's commands
ran in each; two PRs exist and each links the other and the issue; the
consumer PR records its probe against the provider's `main` followed by
passing checks with the regenerated vendored-schema client; and
the foreman's final comment states the merge order. Merge in that order.
Also try a one-repository task: exactly one PR should link the issue, record
the relevant checks and compatibility with the unchanged repository, and
appear in the foreman's final comment without a companion PR or merge window.

## Set it up with a prompt

<!-- terminology-allow-begin -->
Paste this into your factory's foreman, the factory web composer, or a
coding agent connected through Factory MCP:
<!-- terminology-allow-end -->

```text title="Set up a related-services factory"
Read https://github.com/warpdotdev/warp-factory-examples/tree/main/examples/25-related-services
and set up the same factory for my repositories. My provider repository is
OWNER/PROVIDER; it owns the API contract. My consumer repository is
OWNER/CONSUMER. Replace acme/api-service and acme/webapp everywhere they
appear (factory.yaml, the automation, the runner, and all three agent
prompts), replace the bootstrap, test, and contract-check commands and the
schema paths with the ones each repository really uses, and pick a runner
image that carries both toolchains. Keep the rules: when both repositories
change, the provider changes first and only additively, the two pull requests
link both ways, and a human follows the posted merge order. One-repository
work produces only one PR, verified against the unchanged repository, without
a companion PR or merge window. Always regenerate the consumer client from
its vendored schema and rerun positive checks after the provider-main probe.
Before you finish, list anything you could not do yourself: connecting GitHub,
creating the factory-ready label in both repositories, and registering the
definition.
```

The quickstart topology this builds on is
[`01-single-repo-quickstart`](../01-single-repo-quickstart). For the same two
repositories inside a full lifecycle with Slack and Linear intake, see
[`02-sdlc-issue-to-pr`](../02-sdlc-issue-to-pr).
