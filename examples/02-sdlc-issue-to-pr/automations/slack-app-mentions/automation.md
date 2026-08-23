---
triggers:
  - provider: slack
    event: app_mention
---
Someone @-mentioned the factory in Slack. Treat the message as a work request:
run the addressing check, then follow the standard lifecycle. Reply in the
same thread with what you are doing, and again when there is a PR or an
answer.
