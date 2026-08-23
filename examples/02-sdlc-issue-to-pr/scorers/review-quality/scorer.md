---
description: Did the review report actionable findings with locations and corrections?
agents:
  - reviewer
labels:
  - value: actionable
    description: Every finding has a location, an impact, and a correction.
    score: 1
  - value: vague
    description: Findings exist but lack locations or corrections.
    score: 0.5
  - value: empty_or_noise
    description: No findings on a diff with defects, or noise findings only.
    score: 0
passingScore: 1
samplingRate: 25
model: claude-4-5-haiku
---
Evaluate the review agent's findings report. Return `actionable` when each
finding names a file and line, states the impact, and proposes a correction.
Return `vague` when findings are real but under-specified. Return
`empty_or_noise` when the report misses evident defects or consists of
restated style preferences.
