---
triggers:
  - provider: slack
    event: reaction_added
    filter:
      channels: [your-intake-channel]
      emojis: [ticket]
---
Someone reacted with :ticket: to a Slack message. Read the thread, file a
GitHub issue that captures the request with a link back to the thread, and
reply in the thread with the issue link. Do not start the work; this
automation only files it.
