---
name: repository-conventions
description: Shared conventions for branches, commits, tests, and pull requests in the acme repositories. Use before creating branches, commits, or pull requests.
---

# Repository conventions

Replace this placeholder with your team's conventions. Every agent in the
factory can read this skill. Keep it short and specific.

- Name branches `factory/<work-item-id>-<slug>`.
- Use imperative commit subject lines and reference the work item.
- Add a test for changed behavior in the same pull request. State the command
  you ran and its result in the pull request description.
- Link the work item in the pull request and describe what changed and how
  it was verified. Keep the pull request in draft until CI passes.
