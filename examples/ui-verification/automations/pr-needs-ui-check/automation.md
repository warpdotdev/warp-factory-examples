---
triggers:
  - provider: github
    event: pull_request_labeled
    filter:
      repos: [acme/webapp]
      labels: [needs-ui-check]
---
A pull request was labeled `needs-ui-check`. Check out the pull request
branch and run the app. Verify the behavior the pull request describes, then
post your findings and evidence as a pull request comment.
