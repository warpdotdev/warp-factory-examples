---
triggers:
  - provider: github
    event: issue_assigned
    filter:
      repos: [acme/api-service]
      assignees: [warp, warp-factory]
      labels: ["factory:Acme"]
---
A maintainer assigned an issue carrying this factory's routing label to the
factory. The assignment is the whole request. Run the scope check, restate
the deliverable on the issue, and drive it to a pull request. Post progress
as comments on the issue. If the issue is not actionable, say what is missing
in one comment and stop.
