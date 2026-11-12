# 24: Monorepo product

Scope a factory to `apps/web` inside a monorepo. Changes are checked against
every affected workspace package. Shared-package edits are declared in a
draft pull request with review requested from their owners. A human controls
readiness and merging. This extends
[`01-single-repo-quickstart`](../01-single-repo-quickstart) with shared-impact
review.

## What this example shows

- Several products live in one attached repository. The factory is scoped
  to one of them by prompt and by label, not by repository.
- The runner initially installs the product's workspace
  and its dependencies, not the whole monorepo, with setup commands written
  so a failure is a warning the agent can read rather than a failed sandbox.
- Before checking a shared edit, the implementer
  installs the whole workspace to prepare other affected products and their
  dependencies, then runs tests and typechecks for changed packages and
  their dependents and lists every shared-package edit in the pull request.
- A pull request whose diff touches `packages/*` opens as a
  draft with review requested from the owning team, looked up in
  `CODEOWNERS` with a fallback named in a shared skill.
- A factory-wide skill (`skills/`) holds the repository-specific values
  so the three agent prompts stay short.

The label and prompts define the product scope. They do not enforce
filesystem isolation.

## Directory structure

```
factory.yaml
agents/
  foreman/agent.md        FOREMAN, scopes each issue to apps/web and routes it
  implementer/agent.md    IMPLEMENT, tests affected packages, declares shared edits
  reviewer/agent.md       REVIEW, checks the declaration against the diff
automations/
  web-issue-labeled/automation.md   github/issue_labeled, filtered to factory-ready:web
runners/
  linux-web.yaml          4 vCPU / 8 GB, node:22-bookworm, initial install scoped to apps/web
skills/
  monorepo-ownership/SKILL.md   scope, owners, commands, escalation rule; read by every agent
```

## How intake is routed

The automation has one trigger, `github` / `issue_labeled` on
`acme/monorepo`, filtered to the label `factory-ready:web`. The label does
two jobs. It is the maintainer's approval, as `factory-ready` is in
[`01-single-repo-quickstart`](../01-single-repo-quickstart), and it names
the product, so the foreman knows which directory the work belongs to
before it reads the issue. Filter keys combine with AND, but a `labels`
list matches any of its values, so one trigger cannot require two labels.
Putting the product in the label is how you get both.

- An issue labeled anything else, or in any other repository, does not
  match and nothing runs. The factory's own routing label, `factory:Web`,
  is not in the filter, so the labels the foreman applies never re-trigger
  it. The default `skip_bots` value of `all` drops bot-applied labels anyway.
- A matching issue whose work is not in `apps/web` still starts a run. The
  trigger checks the label, not the content. The foreman's scope check is
  what declines it. The foreman posts one comment on the issue naming the
  directory and its owners, without creating a branch or pull request.
- A second product in the same monorepo gets its own copy of this directory
  with a different `alias`, label, and product directory. Each factory
  then watches only its own label and leaves the other's issues alone.

## Repository prerequisites

This example does not ship a fixture repository. It assumes a pnpm workspace
laid out as shown below. [Customize the example](#customize-the-example)
covers other tools.

```
acme/monorepo
  package.json            "packageManager": "pnpm@10.x"
  pnpm-workspace.yaml     packages: [apps/*, packages/*]
  .github/CODEOWNERS      /packages/  @acme/platform
  apps/
    web/                  this factory's product; package.json with test and typecheck scripts
    admin/                another product, same shape, not this factory's
  packages/
    api-client/           shared; both apps depend on it
    ui/                   shared
```

Every package needs `test` and `typecheck` scripts so
`pnpm --filter "...[origin/main]" test` runs the right suites. The shared
packages must be workspace dependencies of the products so pnpm can compute
dependents.

`CODEOWNERS` must name a team for `packages/` so the implementer can find
who to ask. The skill's fallback team covers a path with no `CODEOWNERS` line.

## Runner configuration

All three agents share the `linux-web` runner. Its setup commands install
only the product and its dependencies initially.

- `sudo corepack enable` turns on the pnpm version the repository pins in
  `packageManager`. Corepack writes to `/usr/local/bin`, and because this
  image starts as root, the sandbox runs as a non-root `agent` user with
  passwordless `sudo`.
- `pnpm install --frozen-lockfile --filter "{apps/web}..."` installs the
  product and the workspace packages it depends on, and nothing else. This
  keeps initial setup efficient for product-only changes.

If the diff touches `packages/*`, the implementer must then run
`pnpm install --frozen-lockfile` successfully before tests or typechecks.
This installs other affected products, such as `apps/admin`, and their
dependencies. The scoped setup does not prepare them. Do not suppress a
failure of this expanded install or skip a dependent's checks. Installing
and checking another product does not permit editing it.

Both runner setup commands end in `|| echo "Warning: ..." >&2`. A setup
command that exits non-zero fails the whole sandbox before any agent can
read the error, so a flaky registry would become a failed run with nothing
to inspect. See the same rule in
[`02-sdlc-issue-to-pr`](../02-sdlc-issue-to-pr). A logged warning lets the
implementer see it and rerun the install from the skill.
Every setup command starts from `/workspace`, which is why the install
changes into `/workspace/monorepo` first.

The image is the full `node:22-bookworm` rather than `-slim` because it
ships `git`, which pnpm's `[origin/main]` filter shells out to. Do not count
on the sandbox to add tools the image lacks.

## Customize the example

1. Copy this example into your definition repository, following
   [Use an example](../../README.md#use-an-example).
2. Confirm that your Warp team's GitHub App installation covers the
   repository.
3. Replace `acme/monorepo` in `factory.yaml`,
   `automations/web-issue-labeled/automation.md`, `runners/linux-web.yaml`
   (the `/workspace/monorepo` checkout path), and
   `skills/monorepo-ownership/SKILL.md`.
4. Replace the product directory `apps/web` and the shared-package glob
   `packages/*` wherever they appear: `skills/monorepo-ownership/SKILL.md`,
   the three `agents/*/agent.md` prompts, `runners/linux-web.yaml`, and the
   automation body.
5. Create the label `factory-ready:web` in the repository, or rename it in
   `automations/web-issue-labeled/automation.md` (filter and body). The
   label has to exist before a maintainer can apply it, and the filter
   matches the name exactly.
6. Name the owners. `skills/monorepo-ownership/SKILL.md` reads `CODEOWNERS`
   first and falls back to the team `acme/platform`. Replace that slug with
   a real `org/team`. The team needs at least read access to the
   repository, or GitHub rejects the review request.
7. Replace the pnpm commands in `skills/monorepo-ownership/SKILL.md` and
   `runners/linux-web.yaml` if your workspace tool differs (npm or yarn
   workspaces, Nx, Turborepo, Bazel). Keep the initial install scoped to
   the product and its dependencies. Keep an expanded install of
   affected dependents and their dependency closure before shared-change
   checks, and test and typecheck commands that select changed packages
   plus their dependents. If your default branch is not `main`, change
   `[origin/main]` in the skill.
8. Replace the runner's `dockerImage` if the product does not build on Node
   22.
9. Adjust `alias`. It becomes the factory's @-mention handle and its
   `factory:<alias>` label.

## Validate the example

Run these checks from the repository root.

```bash
python3 scripts/validate_factory_files.py examples/24-monorepo-product
python3 scripts/check_conventions.py
```

The validator checks the definition against Warp's schema. It does not
check that the install succeeds, that `acme/platform` exists, or that the
agents follow the prompts. Registration and real runs are needed to check
those prerequisites and behaviors.

## Test the factory

Commit and push your customized definition. Create a factory in Warp with a
GitHub-backed definition pointing at your repository, branch, and directory
containing `factory.yaml`, as described in
[Use an example](../../README.md#use-an-example). Register it before
creating test issues.

Use the sample below to compare the factory's output with the expected
behavior. Then run the checks under [First-run checks](#first-run-checks).

### Sample task and expected output

Open an issue in `acme/monorepo` titled "Show the account's display name
in the web header" with this body:

> Acceptance: the header in `apps/web` shows `displayName` from the profile
> response. The API already returns the field, but `packages/api-client`
> does not expose it on `Profile` yet.

Label it `factory-ready:web`. You should see the following results.

1. A work item appears in the factory dashboard, and the foreman comments
   on the issue that it has started on `apps/web` and that the change will
   probably touch a shared package.
2. The implementer creates a branch `web/123-header-display-name` (the issue
   number and a slug) with changes to the header component and its test under
   `apps/web/`, and a one-line type addition in
   `packages/api-client/src/profile.ts`.
3. Because the diff touches `packages/*`, the pull request opens as a
   draft, carries `factory:Web`, and has review requested from
   `@acme/platform`. Its description has a "Shared packages" section naming
   the file and why, and a verification section recording a successful
   `pnpm install --frozen-lockfile` before
   `pnpm --filter "...[origin/main]" test` and
   `pnpm --filter "...[origin/main]" typecheck`, covering `api-client`,
   `web`, and the other dependent, `admin`.
4. The reviewer's findings go to the foreman. Unambiguous ones come back as
   commits on the same branch.
5. The foreman comments on the issue with the pull request link and says it
   is a draft waiting on `@acme/platform`. A human on that team marks it
   ready for review, and a human merges.

If the issue needs no shared change, step 3 differs. The pull request opens
ready for review, "Shared packages" says `none`, the scoped install is
enough, and only `apps/web` tests and typechecks appear. If the issue
describes work in `apps/admin`, or a change whose point is a shared package,
the foreman posts one comment naming the directory and its owners and
stops without creating a branch or pull request.

### First-run checks

Check these cases in order.

1. A small issue that stays inside `apps/web` ends in a ready-for-review
   pull request. Its description shows the scoped install and only
   `apps/web` tests and typechecks.
2. An issue that needs a `packages/*` edit ends in a draft with the
   "Shared packages" section, a team review request, and a successful
   expanded install followed by the dependents' tests and typechecks.
3. An issue labeled anything other than `factory-ready:web` starts nothing.

## Set up with an agent

Paste this into your factory's foreman, the factory web composer, or a
coding agent connected to your factory through
[MCP](https://docs.warp.dev/factories/factory-mcp/). Fill in the uppercase
placeholders first.

```text title="Set up a product-scoped monorepo factory"
Read https://github.com/warpdotdev/warp-factory-examples/tree/main/examples/24-monorepo-product
and set up the same factory for my monorepo, OWNER/REPO. Keep its shape:
one repository; a foreman that scopes every task to one product directory;
an implementer that installs affected dependents and their dependencies
before running tests and typechecks for a shared edit and lists any
shared-package edit in the pull request; a reviewer that checks that list
and verification against the diff; a runner whose initial setup installs
only the product's workspace and its dependencies; and the escalation rule
that a pull request touching shared packages opens as a draft with review
requested from the owning team.

Replace the placeholders: acme/monorepo with OWNER/REPO; apps/web with
PRODUCT_DIR; packages/* with SHARED_PACKAGES_GLOB; acme/platform with the
GitHub team that owns the shared packages (check CODEOWNERS first);
factory-ready:web with the label I will apply; and the pnpm commands with
the commands this repository uses for the scoped initial install, the
expanded install before shared-change checks, and tests and typechecks of
changed packages plus their dependents. Validate the definition before you
open a pull request, and tell me which labels, teams, and access I still
have to create or grant.
```
