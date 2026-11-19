---
triggers:
  - provider: github
    event: issue_labeled
    filter:
      repos: [acme/webapp]
      labels: [factory-ready]
---
A maintainer labeled an issue `factory-ready`. Do not assume a previous run
exists. Read the issue and linked work first. Follow the Blueprint intake
stage. Link an existing open spec PR rather than creating a duplicate.
For new in-scope work, prepare the spec and wait at its native spec-review
gate. This label never approves implementation.
