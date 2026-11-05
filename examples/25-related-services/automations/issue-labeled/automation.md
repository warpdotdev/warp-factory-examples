---
triggers:
  - provider: github
    event: issue_labeled
    filter:
      repos: [acme/api-service, acme/webapp]
      labels: [factory-ready]
---
A maintainer labeled an issue `factory-ready` in one of the two related
repositories. Read the issue, decide which repositories change and in which
order, and drive the change to one pull request per repository. Post your
decision, progress, and the final merge order as comments on the issue.
