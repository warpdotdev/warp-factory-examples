---
triggers:
  - provider: github
    event: pull_request_opened
    filter:
      repos: [acme/api-service]
      base_branches: [main]
      labels:
        not_in: [wip]
---
A pull request was opened against the default branch. If it is a draft,
stop silently. Otherwise review it and post your findings and verdict on
the PR.
