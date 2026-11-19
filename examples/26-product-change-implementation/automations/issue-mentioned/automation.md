---
triggers:
  - provider: github
    event: issue_mentioned
    filter:
      repos: [acme/webapp]
      mentioned: [warp, warp-factory]
      labels: ["factory:Webapp"]
---
Continue the matching issue's existing task and pending Blueprint stage.
Read its linked PR, committed spec revision, and conversation before treating
the mention as an answer. A comment without a pending matching spec does not
approve anything or start implementation. Relay a concrete same-contract
revision on the existing PR through implementation and independent review.
