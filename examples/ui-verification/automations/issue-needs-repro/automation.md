---
triggers:
  - provider: github
    event: issue_labeled
    filter:
      repos: [acme/webapp]
      labels: [needs-repro]
---
An issue was labeled `needs-repro`. Follow the reported steps against the
default branch, confirm whether the bug occurs, and post your findings and
evidence as an issue comment.
