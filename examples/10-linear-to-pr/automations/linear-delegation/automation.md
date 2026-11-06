---
triggers:
  - provider: linear
    event: agent_session_created
    filter:
      teams: [your-linear-team]
---
Someone delegated a Linear issue to this factory, or mentioned it in a
comment, and Linear opened an agent session. The session's issue is the work
item. Acknowledge in the session first, then drive the issue to a pull
request and post the PR link back in the session. Replies in the session
continue this run; do not start a second work item for them.
