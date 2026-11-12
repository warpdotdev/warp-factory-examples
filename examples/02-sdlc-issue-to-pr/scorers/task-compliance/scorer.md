---
description: Did the run deliver what the work item asked for, and only that?
agents:
  - implementer
labels:
  - value: compliant
    description: The pull request delivers exactly what the work item requests.
    score: 1
  - value: partial
    description: The pull request delivers some of the request or adds unrequested scope.
    score: 0.5
  - value: non_compliant
    description: The pull request does not deliver the request.
    score: 0
passingScore: 1
samplingRate: 25
model: claude-5-5-haiku-low
selfImprovement: true
---
Compare the pull request against the work item assigned to the run.
Return `compliant` when the change delivers exactly what the work item asks
for. Return `partial` when it delivers a subset or adds unrequested scope.
Otherwise, return `non_compliant`. Judge scope from the issue text, not from
the pull request's description of itself.
