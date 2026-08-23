---
name: repository-conventions
description: Shared conventions for branches, commits, tests, and PRs in the acme repositories. Use before creating branches, commits, or pull requests.
---

# Repository conventions

Replace this stub with your team's real conventions. Every agent in the
factory can read this skill; keep it short and prescriptive.

- Branches: `factory/<work-item-id>-<slug>`.
- Commits: imperative subject line; reference the work item.
- Tests: changed behavior requires a test in the same PR. State the command
  you ran and its result in the PR description.
- PRs: link the work item, describe what changed and how it was verified.
  Draft until CI is green.
