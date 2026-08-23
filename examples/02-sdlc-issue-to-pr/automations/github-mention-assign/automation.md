---
triggers:
  - provider: github
    event: issue_mentioned
    filter:
      repos: [acme/api-service, acme/webapp]
      mentioned: [warp-factory]
      labels: ["factory:Acme"]
  - provider: github
    event: pull_request_mentioned
    filter:
      repos: [acme/api-service, acme/webapp]
      mentioned: [warp-factory]
      labels: ["factory:Acme"]
  - provider: github
    event: issue_assigned
    filter:
      repos: [acme/api-service, acme/webapp]
      assignees: [warp-factory]
      labels: ["factory:Acme"]
  - provider: github
    event: pull_request_assigned
    filter:
      repos: [acme/api-service, acme/webapp]
      assignees: [warp-factory]
      labels: ["factory:Acme"]
---
The factory was mentioned on or assigned to a GitHub issue or pull request
that carries this factory's routing label. Read the thread that triggered
this run, run the addressing check, and follow the standard lifecycle. For
pull request mentions, the usual request is to address review comments:
dispatch implementation on the existing branch rather than opening new work.
