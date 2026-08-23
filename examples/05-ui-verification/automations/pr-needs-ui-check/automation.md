---
triggers:
  - provider: github
    event: pull_request_labeled
    filter:
      repos: [acme/webapp]
      labels: [needs-ui-check]
---
A pull request was labeled `needs-ui-check`. Check out the PR branch, run
the app, verify the behavior the PR describes, and post your findings and
evidence as a PR comment.
