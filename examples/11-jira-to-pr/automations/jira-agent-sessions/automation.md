---
triggers:
  - provider: jira
    event: agent_session_created
    filter:
      project_keys: [YOURKEY]
---
Someone assigned or mentioned Warp on a Jira work item in a project this
factory serves, which started this agent session. The session's work item is
the work item: read it and the instruction that started the session, restate
the deliverable, and drive it to a pull request. Post progress and the final
pull request link in the session, and comment the pull request link on the
work item so it stays visible in Jira after the session ends.
