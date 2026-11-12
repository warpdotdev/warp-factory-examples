---
triggers:
  - provider: slack
    event: app_mention
---
Someone @-mentioned the factory in Slack. Treat the message as a work request.
Check that it is for this factory, then follow the standard lifecycle.
Reply in the same thread with what you are doing, and again when there is a
pull request or an answer.
