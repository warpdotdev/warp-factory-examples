---
triggers:
  - provider: slack
    event: message_dm
---
Someone sent the factory a direct message in Slack. Treat it as a work
request or a question about work in flight. Follow the standard lifecycle and
reply in the DM with progress and the final result.
