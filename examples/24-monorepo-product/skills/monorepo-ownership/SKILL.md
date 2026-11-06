---
name: monorepo-ownership
description: Product scope, shared-package boundary, owner lookup, workspace commands, and the escalation rule for acme/monorepo. Read before scoping, implementing, or reviewing any change.
---

# Monorepo ownership

Every agent in this factory reads this skill; the prompts refer to it instead
of repeating these values. Replace them with your monorepo's.

## Scope

- Product directory: `apps/web`. This factory changes files here.
- Shared packages: `packages/*`. Other products depend on them, so a change
  here affects code this factory does not own.
- Everything else (`apps/*` other than `web`, `infra/`, root configuration)
  is out of scope. The foreman declines it on the issue.

## Owners

- `CODEOWNERS` (at the repository root or under `.github/`) is the source of
  truth. The line that matches a changed path under `packages/` names the
  owning team. GitHub does not request code owners on a draft, so request
  them explicitly.
- Fallback when no `CODEOWNERS` line matches: the team `acme/platform` owns
  `packages/*`.

## Commands

Run from `/workspace/monorepo`, the checkout of `acme/monorepo`.

- Initial install for the product workspace and its dependencies:
  `pnpm install --frozen-lockfile --filter "{apps/web}..."`
- If the diff touches `packages/*`, run `pnpm install --frozen-lockfile`
  successfully before the tests or typechecks below. The initial install
  does not prepare other products such as `apps/admin`; the full install
  supplies affected dependents and their dependency closure. Do not skip
  this step or treat a failed install as a warning. Product-only changes
  keep the scoped install.
- Tests for every affected package (changed packages and their dependents):
  `pnpm --filter "...[origin/main]" test`
- Typecheck the same set: `pnpm --filter "...[origin/main]" typecheck`

## Conventions

- Branches: `web/<issue-number>-<slug>`.
- Pull request description, in this order:
  - Summary: what changed and why, with the issue link.
  - Shared packages: every changed path under `packages/*` and why the edit
    was necessary, or `none`.
  - Verification: the install and check commands you ran and their results,
    naming each package the checks covered.

## Escalation rule

A pull request whose diff touches `packages/*`:

1. opens as a draft, not ready for review;
2. has review requested from the owning team above;
3. lists every shared path in its "Shared packages" section;
4. records the successful full install and passing tests and typechecks for
   the shared package and all of its dependents, not only `apps/web`.

A human on the owning team marks it ready for review. The factory never does.
