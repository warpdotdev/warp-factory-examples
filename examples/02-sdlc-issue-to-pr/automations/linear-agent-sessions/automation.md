---
triggers:
  - provider: linear
    event: agent_session_created
---
A Linear agent session was delegated to this factory. The session's issue is
the work item: read it, run the addressing check, and follow the standard
lifecycle. Post progress and the final PR link back to the Linear session so
the requester can follow along in Linear.
