---
triggers:
  - provider: jira
    event: agent_session_created
    filter:
      project_keys: [YOURKEY]
---
Someone assigned or mentioned Warp on a Jira work item in a project this
factory serves, starting this agent session. Read the work item and the
triggering instruction, restate the deliverable, and coordinate implementation
through to a pull request. Post progress and the final link in the session.
Also post a work-item comment with the link so it remains visible after the
session ends.
