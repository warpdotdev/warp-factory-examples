---
triggers:
  - provider: github
    event: issue_labeled
    filter:
      repos: [acme/api-service]
      labels: [factory-ready]
---
A maintainer labeled an issue `factory-ready`. Read the issue, restate the
deliverable, and drive it to a pull request. Post progress as comments on the
issue.
