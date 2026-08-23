---
triggers:
  - provider: github
    event: issue_labeled
    filter:
      repos: [acme/api-service]
      labels: [factory-ready]
---
A maintainer labeled an issue `factory-ready`. Drive it to a reviewed pull
request: implement on the Claude agent, review on the Codex agent, and post
progress as comments on the issue.
