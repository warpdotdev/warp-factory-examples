---
triggers:
  - provider: slack
    event: app_mention
    filter:
      channels: [your-intake-channel]
---
Someone @-mentioned the factory in the intake channel. Treat the message and
its thread as a work request for this factory's repository. Reply in the same
thread with one sentence that restates the deliverable, coordinate
implementation, and post the pull request link in that thread. If the request
is too vague to restate, ask one clarifying question in the thread and stop.
