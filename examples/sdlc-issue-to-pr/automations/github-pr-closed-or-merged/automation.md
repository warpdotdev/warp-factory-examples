---
triggers:
  - provider: github
    event: pull_request_merged
    filter:
      repos: [acme/api-service, acme/webapp, acme/ios-app]
      labels: ["factory:Acme"]
  - provider: github
    event: pull_request_closed
    filter:
      repos: [acme/api-service, acme/webapp, acme/ios-app]
      labels: ["factory:Acme"]
---
A pull request with this factory's routing label was closed or merged.
Follow the Blueprint's completion stage. Inspect linked work and every required
PR before reporting success or completing a tracked issue. A merged backend PR
does not complete work whose mobile PR is still open. Report closure without
merge on the originating issue; it is not successful completion.
