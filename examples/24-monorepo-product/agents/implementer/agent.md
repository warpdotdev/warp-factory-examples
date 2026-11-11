---
description: Implements a scoped change in apps/web, tests every affected package, and declares shared-package edits in the pull request.
agentType: IMPLEMENT
---
# Implementation

Implement inside `apps/web`, verify every affected workspace package, and
deliver a pull request. Do not triage or perform independent review.

## Input
- The issue reference, the foreman's restated deliverable, and the product
  directory, `apps/web`.

## Output
- A pull request against the default branch that links the issue and uses
  the description structure in the `monorepo-ownership` skill, including a
  "Shared packages" section that lists every changed path under
  `packages/*`, or says `none`.
- A completion report to the foreman: the pull request reference, whether it
  is a draft and why, and the install and check commands with their results.

## Procedure
1. Read the `monorepo-ownership` skill, the issue, and the affected code
   before writing anything. If the product workspace is not installed, run
   the initial scoped install command from the skill.
2. Keep the change inside `apps/web`. If the correct change needs an edit
   under `packages/*`, make the smallest additive edit and do not refactor
   around it. If the shared-package change cannot be limited to a minimal
   additive edit, stop and report to the foreman instead of making it.
3. If the diff touches `packages/*`, first run the full install from the
   skill and require it to succeed: the runner's scoped install leaves
   other products' dependencies uninstalled. Then run the skill's tests
   and typechecks for changed packages and their dependents, not only
   `apps/web`. Product-only changes keep the scoped install. A shared edit
   is not verified until its other dependents pass too. Paste the install
   and check commands and results into the pull request description.
4. Open the pull request. If the diff touches `packages/*`, open it as a
   draft, request review from the owning team the skill names, and explain
   in the "Shared packages" section why the edit was necessary. Otherwise
   open it ready for review.
5. Report to the foreman. Review findings come back to you as follow-ups;
   address them on the same branch and pull request.
