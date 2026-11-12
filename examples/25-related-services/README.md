# 25: Related services

Coordinate a Go API and its Node consumer in one factory. Each changed
repository gets its own pull request and checks. Paired changes merge
provider first, then consumer. The merges are not atomic. One-repository
work produces one pull request with evidence of compatibility with the
unchanged repository. A human controls every merge.

## What this example shows

- Both repositories listed in `repositories` are checked out under
  `/workspace` on every run. One runner bootstraps each repository, and its
  image carries both toolchains.
- The foreman decides the provider-first order before any code changes. The
  repository that provides the contract changes first, and only additively, so
  the deployed consumer keeps working between the two merges.
- When both repositories change, each gets one pull request, titled
  `[1/2]` or `[2/2]`. Both descriptions link to the other pull request and
  include the merge order and compatibility note. One-repository work has
  no pair-only requirements.
- The implementer runs a contract check in each repository, including the
  consumer's check against the provider's current `main`. It then
  regenerates the client and runs positive checks using the vendored schema.
- The reviewer checks only contract consistency, for one pull request or a
  pair.
- A `factory-ready` label on an issue in either repository starts work.

## Directory structure

```
factory.yaml                two repositories, alias Services
agents/
  foreman/agent.md          FOREMAN, decides the order, posts it on the issue
  implementer/agent.md      IMPLEMENT, one PR per repository, contract checks
  reviewer/agent.md         REVIEW, contract consistency for one PR or a pair
automations/
  issue-labeled/automation.md   github/issue_labeled, either repo, factory-ready
runners/
  linux-services.yaml       4 vCPU / 8 GB, warpdotdev/dev-go:1.23 (Go + Node)
```

## Repository prerequisites

The prompts name commands that the two placeholder repositories are assumed
to have. Map each command to what your repositories really run when you
[customize the example](#customize-the-example).

The provider repository, `acme/api-service`, needs the following files and
commands.

- `openapi.yaml` at the repository root describes the HTTP API. It is the
  contract.
- `go mod download` installs dependencies. `go build ./... && go test ./...`
  is the normal check.
- `make contract-check` verifies the handlers against `openapi.yaml`, for
  example with a spec-versus-implementation test.

The consumer repository, `acme/webapp`, needs the following files and
commands.

- `api/openapi.yaml` is a vendored copy of the provider contract the app was
  built against. A paired consumer pull request updates it. Consumer-only
  work keeps it.
- `npm ci` installs dependencies. `npm run lint && npm test` is the normal
  check.
- `npm run contract-check` regenerates the typed API client from
  `api/openapi.yaml` and type-checks every call site. `API_SCHEMA=<path>`
  points it at another schema, which is how the implementer checks the
  consumer against the provider's current `main`. This probe overwrites the
  generated client, so the implementer regenerates from the vendored schema
  and reruns the positive checks before publishing, even if the probe fails.

## Runner configuration

Both checkouts live under `/workspace`, so the consumer's checks can read
the provider's branch directly from `/workspace/api-service`. The runner
prefetches both repositories' dependencies. Each setup command logs a warning
on failure instead of returning a nonzero exit code, which would fail the
whole sandbox.
The implementer reruns dependency setup in each repository it changes.

## How intake is routed

The automation has one trigger, `github` / `issue_labeled`, filtered to
`repos: [acme/api-service, acme/webapp]` and `labels: [factory-ready]`.
Filter keys combine with AND, so the event reaches the foreman only when the
`factory-ready` label is added to an issue in one of those two repositories.
GitHub labels are per repository, so the label has to exist in both.

Everything else is dropped before any agent runs: a `factory-ready` label on
an issue in a third repository, any other label on these issues, and a
`factory-ready` label on a pull request (`issue_labeled` is issues only,
while pull request labels are `pull_request_labeled`). The default
`skip_bots: all` skips labels applied by bots. Removing and re-adding the
label fires the trigger again.

The foreman does the second level of routing itself, from the issue text:
one repository, both repositories in provider-then-consumer order, or out of
scope. Issues it cannot place get one clarifying comment and no branch.

## Merge paired changes in provider-first order

The factory never merges. For a two-repository change, a human merges in
this order:

1. Merge the provider pull request, `[1/2]`, in `acme/api-service`. Its
   contract change only adds, so the deployed web app keeps working against
   the new API.
2. Wait for it to land, and to deploy if merging deploys.
3. Merge the consumer pull request, `[2/2]`, in `acme/webapp`.

Between steps 1 and 3 the API serves the new field or endpoint and the
deployed web app ignores it. Merging the consumer first breaks it because the
web app would call a contract the deployed API does not serve yet, which is
exactly what the consumer's contract check against the provider's `main`
records in its pull request. To back out, revert the consumer first, then the
provider.

For one-repository work, a human merges the single pull request after its
checks pass. There is no `[n/2]` title, reciprocal link, or two-merge window.
The pull request explains why the unchanged repository needs no change.

A provider-only pull request preserves compatibility with the consumer.
A consumer-only pull request must pass its contract check against the
provider's current `main`, not depend on an unreleased API.

Breaking contract changes (removing, renaming, or retyping a field or
endpoint) are out of scope by design. The foreman comments on the issue with
what they need instead, a versioned endpoint or a coordinated deploy, and
stops.

## Customize the example

1. Copy this example into your definition repository, following
   [Use an example](../../README.md#use-an-example).
2. Replace `acme/api-service` (provider) and `acme/webapp` (consumer) with
   repositories your Warp team's GitHub installation can reach. They appear
   in `factory.yaml`, `automations/issue-labeled/automation.md`,
   `runners/linux-services.yaml`, `agents/foreman/agent.md`,
   `agents/implementer/agent.md`, and `agents/reviewer/agent.md`. Keep the
   roles distinct. The provider owns the contract.
3. Replace the prefetch commands in `runners/linux-services.yaml`.
4. Replace the bootstrap, test, and contract-check commands and the schema
   paths in `agents/implementer/agent.md`, and the schema paths in
   `agents/reviewer/agent.md`. The commands assume the default branch is
   `main`. If your repositories have no contract check yet, add one before
   the first run. Without it, the implementer cannot verify compatibility.
5. Choose a runner `dockerImage` with both toolchains and verify their
   versions against your repositories' requirements. The example uses
   `warpdotdev/dev-go:1.23`. Replace it if it does not meet those
   requirements. See [runners](https://docs.warp.dev/factories/runners/).
6. Create the `factory-ready` label in both repositories, or change `labels`
   in `automations/issue-labeled/automation.md` to a label you already use.
7. Adjust `alias`. It becomes the factory's @-mention handle.
8. Optionally change `agentDefaults.model` to any Warp Agent model ID.

## Validate the example

Run these checks from the repository root.

```bash
python3 scripts/validate_factory_files.py examples/25-related-services
python3 scripts/check_conventions.py
```

The validator checks that the definition parses. It does not prove the
runner image, commands, or repositories exist, or that the agents follow
the contract-check and merge-order instructions. Check those prerequisites
and behaviors with real runs.

## Test the factory

Commit and push your customized definition. Create a factory in Warp with a
GitHub-backed definition pointing at your repository, branch, and directory
containing `factory.yaml`, as described in
[Use an example](../../README.md#use-an-example). Register it before
creating test issues.

Use the sample below to compare the factory's output with the expected
behavior. Then run the checks under [First-run checks](#first-run-checks).

### Sample task and expected output

A maintainer opens `acme/webapp#118`, "Show fulfillment status on the orders
page", with this body.

> The orders table should show each order's fulfillment status.
> `GET /orders` doesn't return it yet. Add an optional `status` field
> (`pending`, `shipped`, or `delivered`) to each order in `GET /orders`, and
> render it as a column in the orders table.

The maintainer labels it `factory-ready`. You should see the following
results.

1. The foreman comments on #118 that this changes the contract.
   `api-service` provides `status` and `webapp` consumes it, so the API
   changes first with an optional field and the web app follows.
2. The implementer opens a pull request in `acme/api-service`,
   `[1/2] Add optional status to GET /orders`, on branch
   `factory/118-order-status`. `openapi.yaml` gains the optional `status` enum
   on the order schema, with the handler change and a test. Its Verification
   section shows `go build ./... && go test ./...` and `make contract-check`
   passing and the schema diff as additive. It links #118 and the consumer
   pull request.
3. The implementer opens a pull request in `acme/webapp`,
   `[2/2] Show order status in the orders table`, on a branch of the same
   name. `api/openapi.yaml` is updated, the client is regenerated, and the
   table gains the column and a test. Its Verification section shows
   `npm run lint && npm test` and `npm run contract-check` passing, and the
   same check against the provider's current `main` schema failing (`status`
   does not exist on the order type), recorded separately as the reason this
   pull request merges second. After that probe, it shows
   `env -u API_SCHEMA npm run contract-check` and `npm run lint && npm test`
   passing again. The final generated client includes `status` from the
   updated vendored schema. It links #118 and the provider pull request.
4. The reviewer sends a report to the foreman. It never appears on GitHub. A
   finding such as "the table maps `pending` and `shipped` but the provider
   enum also has `delivered`" is unambiguous and goes back to the
   implementer, which fixes it on the same branch.
5. The foreman posts a final comment on #118 with both pull request links, the
   merge order, and the note that the deployed web app ignores `status` until
   its pull request merges.
6. A human merges `[1/2]`, waits for it to land, and merges `[2/2]`.

For a consumer-only task, such as "Sort the orders table by order ID" using an
existing API field, the foreman dispatches only `webapp`. The implementer
leaves the vendored schema unchanged and opens one pull request without
`[n/2]` or a "Linked PR" section. Its Verification section records the normal
checks, a passing probe against provider `main`, and passing positive checks
after regenerating from the vendored schema. The reviewer checks compatibility
with the unchanged API and the foreman posts the one pull request link and
results. There is no provider pull request or merge window. A provider-only
internal fix follows the same single-pull-request process with Go checks and
`make contract-check`, plus evidence that its unchanged or additive contract
remains compatible with the consumer.

For an out-of-scope task, such as `acme/api-service#204`, "Rename
`customer_id` to `customerId` in all responses", labeled `factory-ready`, the
foreman comments that this is a breaking contract change that needs a
versioned endpoint or a coordinated deploy, which this factory does not do,
and stops. No branch and no pull request are created.

### First-run checks

Pick a small additive change like the sample task and check these results.

1. Both repositories are present under `/workspace`, and the implementer's
   commands ran in each.
2. Two pull requests exist, and each links the other and the issue.
3. The consumer pull request records its probe against the provider's `main`,
   followed by passing checks with the regenerated vendored-schema client.
4. The foreman's final comment states the merge order. A human merges in that
   order, waiting for the provider to land and to deploy if merging deploys.

Also try a one-repository task. Exactly one pull request should link the
issue, record the relevant checks and compatibility with the unchanged
repository, and appear in the foreman's final comment without a companion
pull request or merge window.

## Set up with an agent

<!-- terminology-allow-begin -->
Paste this into your factory's foreman, the factory web composer, or a
coding agent connected through Factory MCP.
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

This example builds on
[`01-single-repo-quickstart`](../01-single-repo-quickstart). For the same two
repositories inside a full lifecycle with Slack and Linear intake, see
[`02-sdlc-issue-to-pr`](../02-sdlc-issue-to-pr).
