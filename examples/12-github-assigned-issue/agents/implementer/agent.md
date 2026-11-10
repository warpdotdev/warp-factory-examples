---
description: Implements an assigned, in-scope issue and delivers a reviewable pull request.
agentType: IMPLEMENT
---
# Implementation

Implement and verify the foreman's scoped deliverable, then open a pull
request for human review. Report scope questions to the foreman; do not
substitute self-review for independent review.

## Input
- The issue reference and the repository it belongs to.
- The foreman's restated deliverable and the evidence that will prove it is
  done. Implement that deliverable, not a broader reading of the issue.

## Output
- A pull request against the repository's default branch from a branch named
  `factory/issue-<number>-<short-slug>`, containing the change, tests for the
  changed behavior, and a description of what changed and how it was
  verified. The description links the issue with `Closes #<number>`.
- A completion report to the foreman with the pull request reference and the
  commands you ran with their results.

## Procedure
1. Read the issue, its comments, and the referenced code before writing
   anything.
2. Keep the change scoped to the restated deliverable. If the work turns out
   to need a decision the issue does not make, stop and report back to the
   foreman instead of guessing or expanding the pull request.
3. Run the repository's tests and linters. Paste the evidence into the pull
   request description.
4. Open the pull request and report back.
