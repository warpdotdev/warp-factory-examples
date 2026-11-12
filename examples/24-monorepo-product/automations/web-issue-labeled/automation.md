---
triggers:
  - provider: github
    event: issue_labeled
    filter:
      repos: [acme/monorepo]
      labels: ["factory-ready:web"]
---
A maintainer labeled an issue `factory-ready:web` to approve work for
`apps/web`. Read the issue and check its scope using the `monorepo-ownership`
skill. Coordinate implementation through to a pull request and post progress
as comments on the issue.
