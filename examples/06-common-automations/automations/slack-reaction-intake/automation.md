---
triggers:
  - provider: slack
    event: reaction_added
    filter:
      channels: [your-intake-channel]
      emojis: [ticket]
---
Someone reacted with :ticket: to a Slack message. Read the thread, create a
GitHub issue that captures the request with a link back to the thread, and
reply in the thread with the issue link. Do not start the work. This
automation only creates the issue.
