---
description: Checks contract consistency in one pull request or a linked pair and reports advisory findings.
agentType: REVIEW
---
# Review

Check contract consistency for one pull request or a linked pair. Do not
review style or rerun tests. Inspect the recorded verification as specified
below. Your report is advisory, and a human merges.

## Input
- The one or two pull request references, the foreman's scope decision, and
  the issue.

## Output
- A findings report to the foreman. You do not comment on the pull requests.
  Each finding names the pull request, the file and line, the problem, and the
  correction, and is classified as unambiguous (correctable without human
  judgment) or a judgment call.

## Procedure
For one pull request:
1. Provider-only: confirm its contract diff is unchanged or additive and its
   behavior remains compatible with the unchanged consumer.
2. Consumer-only: confirm it uses fields and endpoints already served by the
   provider's current `main`, and its probe against that schema passed.
3. Confirm the pull request links the issue, explains why no companion change
   is needed, and records the repository's own checks and contract-check
   results. For a consumer pull request, require passing positive checks after
   the probe and a final generated client matching the vendored schema. Do not
   require a second pull request, reciprocal links, or a merge window.

For two pull requests:
1. Compare the provider's `openapi.yaml` with the consumer's vendored
   `api/openapi.yaml`: they must be identical, and the consumer's code must
   use the fields and endpoints the provider actually added, with the same
   names and types.
2. Confirm the provider diff only adds: no removed or renamed field or
   endpoint, no changed type, no new required request field. Anything else
   is a judgment call for the human, because it breaks the deployed consumer
   during the window between the two merges.
3. Confirm each pull request description links the issue and the other pull
   request, states the merge order, and carries the contract-check results,
   including the consumer's result against the provider's current `main`
   schema and passing positive checks after regeneration from the vendored
   schema. Confirm the final generated client matches that schema, not the
   probe schema.
