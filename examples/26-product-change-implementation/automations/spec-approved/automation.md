---
triggers:
  - provider: github
    event: issue_labeled
    filter:
      repos: [acme/webapp]
      labels: [spec-approved]
---
A human added `spec-approved` to an issue. Do not assume a previous run
exists. Find the linked specification pull request and read the committed
specification on its branch. Coordinate implementation and review, then post
the pull request link on the issue. If the issue links no open specification
pull request, say so in a comment and stop.
