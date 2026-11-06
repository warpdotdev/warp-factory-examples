---
triggers:
  - provider: github
    event: issue_labeled
    filter:
      repos: [acme/webapp]
      labels: [factory-ready]
---
A maintainer labeled an issue `factory-ready`. Do not assume a previous run
exists; read the issue's current state first. Run the scope check, have the
spec agent write the spec in a draft PR, comment on the issue with the PR
link and the approval instruction, and stop at the approval gate. Do not
start implementation.
