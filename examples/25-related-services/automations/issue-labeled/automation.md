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
order, and coordinate one pull request per changed repository. Post your
decision, progress, final links, and verification results on the issue.
Include the merge order and compatibility window only for a pair.
