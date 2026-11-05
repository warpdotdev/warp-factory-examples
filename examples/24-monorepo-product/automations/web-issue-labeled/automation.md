---
triggers:
  - provider: github
    event: issue_labeled
    filter:
      repos: [acme/monorepo]
      labels: ["factory-ready:web"]
---
A maintainer labeled an issue `factory-ready:web`: approved work for the
`apps/web` product. Read the issue, scope it to that product as the
`monorepo-ownership` skill describes, and drive it to a pull request. Post
progress as comments on the issue.
