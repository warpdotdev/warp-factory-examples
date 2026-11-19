---
triggers:
  - provider: github
    event: issue_mentioned
    filter:
      repos: [acme/api-service, acme/webapp]
      mentioned: [warp, warp-factory]
      labels: ["factory:Acme"]
  - provider: github
    event: pull_request_mentioned
    filter:
      repos: [acme/api-service, acme/webapp]
      mentioned: [warp, warp-factory]
      labels: ["factory:Acme"]
  - provider: github
    event: issue_assigned
    filter:
      repos: [acme/api-service, acme/webapp]
      assignees: [warp, warp-factory]
      labels: ["factory:Acme"]
  - provider: github
    event: pull_request_assigned
    filter:
      repos: [acme/api-service, acme/webapp]
      assignees: [warp, warp-factory]
      labels: ["factory:Acme"]
---
The factory was mentioned on or assigned to a GitHub issue or pull request
that carries this factory's routing label. Read the thread that triggered
this run, check that the request is for this factory, and continue its pending
Blueprint stage. A spec answer belongs to the matching spec gate. For review
corrections, reuse the existing branch and PR and independently review the new
head. Do not bypass an unanswered gate or create duplicate work.
