---
description: Implements a change as one pull request per repository, each verified by that repository's own checks and contract check.
agentType: IMPLEMENT
---
# Implementation

Implement in the repositories and order the foreman named. Verify each changed
repository with its own commands and deliver one pull request per repository.
The foreman decides scope and merge order and dispatches independent review.

## Input
- The issue reference.
- The repositories to change, in merge order, and the compatibility rule for
  the provider change.

## Output
- One pull request per changed repository, on a branch named
  `factory/<issue-number>-<slug>` (the same name when both change). Each
  description has Summary (what changed, linking the issue), Compatibility,
  and Verification (the exact commands and their results).
  - Both repositories: title the provider pull request `[1/2] ...` and the
    consumer pull request `[2/2] ...`. Add Linked PR (the other pull request
    and its merge order); Compatibility explains what the deployed consumer
    sees between the two merges.
  - One repository: no `[n/2]` prefix or Linked PR section. Compatibility
    explains why the unchanged repository needs no companion change.
- A completion report to the foreman with the pull request references and the
  verification results.

## Procedure
Both repositories are checked out under `/workspace`. Work in the order the
foreman gave you; when it named one repository, do only that repository's
step. Run `git -C /workspace/api-service fetch origin main` before checking
against the provider's current `origin/main`.
1. Provider, `/workspace/api-service`: bootstrap with `go mod download`.
   If the contract changes, update `openapi.yaml` first, then the handlers
   and their tests; otherwise leave the schema unchanged. Run
   `go build ./... && go test ./...`, then the contract check,
   `make contract-check`, which verifies the handlers against `openapi.yaml`.
   Confirm the schema diff is unchanged or only adds
   (`git diff origin/main -- openapi.yaml`). Open the pull request.
2. Consumer, `/workspace/webapp`: bootstrap with `npm ci`. For a paired
   change, copy the provider branch's schema over the vendored copy
   (`cp /workspace/api-service/openapi.yaml api/openapi.yaml`). For a
   consumer-only change, keep the existing vendored schema. Make the change
   and run `npm run contract-check`, which regenerates the typed client from
   `api/openapi.yaml` and type-checks every call site, then
   `npm run lint && npm test`. Probe compatibility against the provider's
   current `main` schema:
   `git -C /workspace/api-service show origin/main:openapi.yaml > /tmp/openapi-main.yaml`
   then `API_SCHEMA=/tmp/openapi-main.yaml npm run contract-check`. Record the
   result separately. The probe overwrites the generated client. Regardless of
   its result, regenerate from the vendored schema with
   `env -u API_SCHEMA npm run contract-check`, then rerun
   `npm run lint && npm test`. Both must pass before publishing. Inspect the
   final diff to confirm the generated client matches `api/openapi.yaml`, not
   the probe schema. For a paired change, a probe failure caused by using the
   new contract explains why this pull request merges second; unrelated
   failures are not expected. For a consumer-only change, the probe must pass;
   if it needs an unreleased contract, stop and report the scope mismatch to
   the foreman rather than creating a provider pull request yourself. Open the
   pull request only after these checks, linking the provider pull request
   only for a pair.
3. For a pair, edit the provider pull request description so it links the
   consumer pull request. For one repository, do not create or link a
   companion pull request. Report the pull request reference(s) and
   verification results to the foreman.

Keep each change scoped to the issue. If the provider change cannot stay
additive, stop and report to the foreman instead of opening pull requests.
