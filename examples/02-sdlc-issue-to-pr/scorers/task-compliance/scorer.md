---
description: Did the run deliver what the work item asked for, and only that?
agents:
  - implementer
labels:
  - value: compliant
    description: The PR delivers the work item's request, scoped to it.
    score: 1
  - value: partial
    description: The PR delivers some of the request or adds unrequested scope.
    score: 0.5
  - value: non_compliant
    description: The PR does not deliver the request.
    score: 0
passingScore: 1
samplingRate: 25
model: claude-4-5-haiku
selfImprovement: true
---
Compare the pull request against the work item the run was dispatched with.
Return `compliant` when the change delivers exactly what the work item asks
for; `partial` when it delivers a subset or adds unrequested scope; otherwise
`non_compliant`. Judge scope from the issue text, not from the PR's own
description of itself.
