---
triggers:
  - provider: linear
    event: agent_session_created
    filter:
      teams: [your-linear-team]
---
Someone delegated a Linear issue to this factory, or mentioned it in a
comment, and Linear opened an agent session. The session's issue is the work
item. Acknowledge it in the session before coordinating implementation.
Post the resulting pull request link in the session. Replies continue this
run. Do not start a second work item for them.
