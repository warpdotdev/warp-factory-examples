---
triggers:
  - provider: github
    event: issue_labeled
    filter:
      repos: [acme/webapp]
      labels: [spec-approved]
---
A human added `spec-approved` to an issue. Do not assume a previous run
exists: find the spec PR linked from the issue and read the committed spec
on its branch, then implement, review, and hand the PR back on the issue. If
the issue links no open spec PR, say so in a comment and stop.
