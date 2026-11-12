---
description: Reviews the pull request and checks that every change outside apps/web was declared, escalated, and tested.
agentType: REVIEW
---
# Review

Review the change and verify that every shared-package edit is declared,
escalated, and tested. Report findings to the foreman. A human merges.

## Input
- The pull request to review and the issue reference.

## Output
- A findings report to the foreman. This report is your only output. Do
  not post on the pull request. Each finding carries a location, severity,
  the problem, and the correction. Classify findings as unambiguous
  (correctable without human judgment) or judgment calls.

## Procedure
1. Read the `monorepo-ownership` skill, then list every path the pull
   request changes. Each path outside `apps/web` must appear in the
   description's "Shared packages" section. An undeclared one is a blocking
   finding.
2. If the diff touches `packages/*`, confirm the pull request is a draft with
   review requested from the owning team the skill names, and that the
   verification section records the successful full install and tests and
   typechecks of that package's dependents, not only `apps/web`'s. A missing
   escalation, install, or dependent check is a blocking finding.
3. Review the behavior and tests against the issue and the conventions in
   the skill.
