# 25: Related services

Two repositories that share one contract, in one factory. `acme/api-service`
is a Go API whose `openapi.yaml` is the contract; `acme/webapp` is a Node web
app that consumes it. A maintainer labels an issue in either repository, the
foreman decides which repository changes first, the implementer opens one
pull request per repository and verifies each with that repository's own
bootstrap, tests, and contract check, the reviewer checks that the pair
agrees, and a human merges the two PRs in a documented order. Nothing here
makes the two merges atomic, and nothing pretends to.

## What it demonstrates

- Two differently named repositories in `repositories`, both checked out
  under `/workspace` on every run, with a per-repository bootstrap in one
  runner. The image carries both toolchains.
- A provider-first decision the foreman makes before any code changes: the
  repository that provides the contract changes first, and only additively,
  so the deployed consumer keeps working between the two merges.
- One PR per repository, linked both ways, titled `[1/2]` and `[2/2]`, with
  the merge order and the compatibility note in every PR description.
- A contract check in each repository that the implementer must run,
  including the consumer's check against the provider's current `main`.
- A reviewer whose only job is the cross-repository consistency check.
- Intake from a `factory-ready` label on an issue in either repository.

## Tree

```
factory.yaml                two repositories, alias Services
agents/
  foreman/agent.md          FOREMAN, decides the order, posts it on the issue
  implementer/agent.md      IMPLEMENT, one PR per repository, contract checks
  reviewer/agent.md         REVIEW, cross-repository consistency check only
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
  built against. A consumer PR updates it.
- `npm ci` bootstraps; `npm run lint && npm test` is the normal check.
- `npm run contract-check` regenerates the typed API client from
  `api/openapi.yaml` and type-checks every call site. `API_SCHEMA=<path>`
  points it at another schema, which is how the implementer checks the
  consumer against the provider's current `main`.

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

The factory never merges. A human merges, in this order:

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
   order type), recorded as the reason this PR merges second. It links #118
   and the provider PR.
4. A reviewer report to the foreman, which never appears on GitHub. A
   finding such as "the table maps `pending` and `shipped` but the provider
   enum also has `delivered`" is unambiguous and goes back to the
   implementer, which fixes it on the same branch.
5. A final foreman comment on #118 with both PR links, the merge order, and
   the note that the deployed web app ignores `status` until its PR merges.
6. A human merges `[1/2]`, waits for it to land, and merges `[2/2]`.

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
consumer PR records its contract check against the provider's `main`; and
the foreman's final comment states the merge order. Merge in that order.

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
image that carries both toolchains. Keep the rules: the provider changes
first and only additively, one pull request per repository linked both ways,
and a human merges in the order the foreman posts on the issue. Before you
finish, list anything you could not do yourself: connecting GitHub, creating
the factory-ready label in both repositories, and registering the definition.
```

The quickstart topology this builds on is
[`01-single-repo-quickstart`](../01-single-repo-quickstart). For the same two
repositories inside a full lifecycle with Slack and Linear intake, see
[`02-sdlc-issue-to-pr`](../02-sdlc-issue-to-pr).
