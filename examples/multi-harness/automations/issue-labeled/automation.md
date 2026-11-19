---
triggers:
  - provider: github
    event: issue_labeled
    filter:
      repos: [acme/api-service]
      labels: [factory-ready]
---
A maintainer labeled an issue `factory-ready`. Have the Claude Code agent
implement the change and the Codex agent review it. Deliver a reviewed pull
request and post progress as comments on the issue.
