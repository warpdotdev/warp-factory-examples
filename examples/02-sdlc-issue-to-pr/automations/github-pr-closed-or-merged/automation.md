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
Inspect its description for links to work items. If it was merged, move each
linked Linear issue to its completed state and complete the factory task that
produced the pull request. If it was closed without merging, report that on
the linked issue instead. Do not mark anything done.
