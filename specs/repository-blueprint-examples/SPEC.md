# Repository-wide Blueprint examples and linked docs

## Summary

Audit every example. Move the five multi-stage workflows to explicit Blueprints. Add two no-fixture exercises that connect setup, approval, implementation, independent review, and same-PR revision. Reconcile directly related docs in a separate draft PR. Preserve the small examples, historical snapshots, access boundaries, and unresolved verification holds.

- Work item: [docs #1045](https://github.com/warpdotdev/docs/issues/1045).
- Requester: `hongyi-chen`.
- Status: approved by the requester at commit `960160b2d9d4c7d22fcf8e36d4363452e6a49cd4`.
- Delivery: exactly two draft PRs, one in this repository and one in `warpdotdev/docs`.
- Implementation reuses this specification's branch and PR. Do not create a third spec-only PR.
- This specification expands the old `sdlc-issue-to-pr`-only scope. It does not reopen or replace the merged docs work.

## Requester decisions

The requester answered the four scope proposals:

> Yes one PR for these and one PR for docs updates

The [written answer](https://warpdev.slack.com/archives/C09BVK0PL3Y/p1795110000462349) and the [foreman's decision record](https://github.com/warpdotdev/docs/issues/1045#issuecomment-7017068331) resolve the scope as follows:

1. Convert the `sdlc-issue-to-pr`, `multi-harness`, `monorepo-product`, `related-services`, and `product-change-implementation` examples. Do not migrate every minimal or intake-focused example.
2. Replace `product-change-implementation`'s label-only spec approval with a native gate answered in the original issue conversation. Add the narrowly filtered mention intake required for answers. Independently review revisions.
3. Add practical exercises to the existing `sdlc-issue-to-pr` and `product-change-implementation` READMEs. Do not add an application fixture or another example directory.
4. Include directly related docs corrections in a separate draft PR. Do not redo merged guides.

These decisions approved the interview scope, not the then-unwritten specification. The requester subsequently answered “yes approved” to the approval request for committed specification `960160b2d9d4c7d22fcf8e36d4363452e6a49cd4`. See the [written approval](https://warpdev.slack.com/archives/C09BVK0PL3Y/p1795110569201039) and [approval record](https://github.com/warpdotdev/docs/issues/1045#issuecomment-7017292689). Approval covers this specification only. It does not authorize live configuration application, publication, or merge.

## Evidence and audit baseline

| Repository | Researched revision | Use |
| --- | --- | --- |
| `warpdotdev/warp-factory-examples` | `76f0f06f59a3c3d5fc29eb7699fe281073fa58c1` | Clean prepared checkout; all 16 examples, root guidance, helpers, and CI inventoried |
| `warpdotdev/docs` | `94c72e274eec6d6b9f36b19f8fd2370e6b6deb8b` | Current merged Blueprint concepts, reference, guides, positioning, terminology, and writing policy |
| `warpdotdev/warp-server` | `f39168209795a161ad3c17f6e5b3c38061896a8d` | Parser, schema, runtime, and generated worker instructions |
| `warpdotdev/docs-factory-config` | `3c80494cd71c2614c17d8f116286b2e437470d41` | Merged checkout provisioning and factory skills |

Merged docs PRs #1046, #1055, and #1056 and provisioning PR #37 are prior work, not new deliverables. The earlier specification in `docs/specs/blueprints-docs-and-examples/SPEC.md` supplies preserved decisions and runtime holds. Its approval covered `sdlc-issue-to-pr`, not this expansion.

Baseline checks in this checkout:

- `python3 scripts/check_conventions.py`: passed.
- `python3 scripts/test_check_conventions.py -v`: 10 tests passed.
- `python3 scripts/test_verify_default_agents.py -v`: 4 tests passed.
- `GH_PAGER=cat python3 scripts/verify_default_agents.py --ref d7295cefa21526eabb9ae7b007cf78706a8b3ec1`: the historical default-agent snapshot matches its pinned source.
- The committed validator returned exit 2 with HTTP 401 for all 16 examples. None of those invocations validated a definition.
- The current bundled validator, with `--server-root https://app.warp.dev`, returned exit 0 for all 16 untouched examples using the public `v1alpha1` parser. It retried without the rejected ambient credential. State-dependent apply checks did not run.
- The bundled validator's SHA-256 was `c69b352f860b3cad34ba047851c5dd92e6299fa68980f4601e64a18079a25966`. The committed copy's was `3e9faa9f43dc5c2eb2b9f10bb3716cc53e251d8c59d685989548a1a85cd1f29b`.

Baseline parser success proves neither the proposed migrated definitions nor application or runtime behavior. Repository API permission metadata reported all false; that alone does not establish whether authenticated branch delivery works.

## Product behavior

1. A reader can distinguish a Blueprint's routing from a worker's execution configuration. Agent definitions remain the workers that execute stages.
2. Each converted example has one inspectable workflow in `factory.yaml`. Worker prompts do not contain a competing stage sequence.
3. Each stage names its worker, procedure, required inputs, and reported outputs. The foreman binds those inputs and chooses the first matching outgoing prose condition.
4. A worker asks through the foreman when required information is missing. It does not silently choose an undefined route or leave a stage while a required human answer is pending.
5. A specification gate distinguishes approval of the current spec, requested changes, and cancellation. A question or unrelated reply does not approve a spec. A new spec revision needs a new answer.
6. Implementation and revisions reuse the existing branch and PR for each repository. A branch or PR never spans repositories.
7. Independent review stays separate from implementation. Review is advisory. `related-services` retains its deliberately limited contract-review pass; the other converted workflows re-review actionable revisions.
8. People control merge. A delivered PR, a resolved gate, a completed worker run, and a successful parser check are not merge evidence.
9. Existing work retains its selected Blueprint. A separately started task uses the newly applied definition. Reapplying a label or closing a PR is not an independent comparison trial.
10. Every exercise names prerequisites, substitutions, actions, expected artifacts, failure recovery, and verification limits. Illustrative output is never described as a recorded run.

## Technical design

### Common definition contract

- Retain `schemaVersion: v1alpha1`. Do not perform a version-only migration to `v1alpha2`.
- Retain `agents/<name>/agent.md`, `agentDefaults`, `agentType`, existing worker names, models, harnesses, credentials, runners, skills, and scorer settings unless a change is listed below.
- Use an inline root `blueprint` with `worker: foreman`. Use flat leaf stages with inline `prompt` text. Do not introduce hosted catalog references, nested scopes, or external prompt files.
- Use `gates`, not the legacy `loopIn` spelling.
- Use a scalar `to` for one unconditional route. For multiple routes, give every item a `stage` and a prose `when`. Put specific conditions before broader conditions.
- Do not invent executable expressions or typed server-validated stage outputs.
- Every stage has an outgoing route. The graph has a path from `start` to `end`. Do not add a rule that all stages must be reachable from `start`; disconnected entry stages are supported.
- Keep role boundaries and shared instructions in worker files and skills. Move stage-specific procedures, routing, and gate policy into the Blueprint. Remove or rewrite conflicting descriptions and numbered workflow procedures together.
- Automations retain their existing event and filter constraints except for the explicit example-26 change. Do not add blanket stage targeting or execution overrides.
- If an automation uses `stage`, it names an existing stage and declares neither `agent`/`worker` nor per-run execution overrides. A separate review-only path must not send an externally supplied PR through implementation.
- Report missing tools, access, failed checks, and unresolved questions as such. Do not approve or merge a PR.

Maintainer source references at the recorded server revision:

- `logic/factoryfile/registry.go:10`: `v1alpha1` is canonical; `v1alpha2` accepts the same fields and layouts.
- `logic/factoryfile/blueprint.go:176` (`decodeBlueprint`), `:284` (`decodeBlueprintStage`), `:376` (`decodeBlueprintGates`), and `:441` (`decodeBlueprintEdges`): authored grammar.
- `logic/factoryfile/blueprint.go:493` (`validateBlueprintReachability`), `:527` (`validateBlueprintProfiles`), and `:605` (`validateAutomationStage`): graph and worker references.
- `logic/factoryfile/schema/documents.go:321`: Blueprint schema and qualified availability; `:347`: stage reachability and explicit entry.
- `logic/ai/ambient_agents/templates/factory_blueprint_scope_prompt.tmpl`, sections “Operating procedure” and “Declaring transitions”: ordered conditions, stage continuation, human-answer relay, and gates.
- `logic/ai/ambient_agents/templates/factory_blueprint_stage_agent_prompt.tmpl`: delegated workers execute only their dispatched stage and return its outputs.
- `logic/factoryruntime/runtime.go`, `logic/factoryruntime/blueprint.go`, and `logic/ai/ambient_agents/factory_runtime.go`: selected task definition and continuation. Recheck these at implementation time.

Source reads and a schema's acceptance do not prove production availability. Keep private rollout details out of reader-facing files and PR text.

### Repository-wide disposition

| Surface | Required action |
| --- | --- |
| Root `README.md` | Identify the five Blueprint examples; explain workflow versus worker configuration; link the two exercises and canonical docs; explain validator exit 2 and network access |
| `CONTRIBUTING.md` | Explain when a Blueprint belongs in an example; retain one concept per example and complete-root rules; document new checks and validator recopy policy |
| `warp-default-agents` | Preserve the pinned snapshot, prompts, source ref, and verification helper; do not relabel it as the current Blueprint default |
| `single-repo-quickstart` | Keep the two-worker minimal workflow; add only a concise pointer to explicit Blueprint routing |
| `sdlc-issue-to-pr` | Convert the complete lifecycle and optional mobile extension; add the first practical exercise |
| `multi-harness` | Convert implementation and review routing; preserve third-party harness authentication and runner choices |
| `code-review-only` | Preserve its single-worker advisory-review purpose; no forced implementation or spec stages |
| `ui-verification` | Preserve verification-only intake and evidence limits; no new application fixture or lifecycle |
| `common-automations` | Preserve independent maintenance jobs; do not combine them into a single SDLC lifecycle |
| `self-hosted-worker` | Preserve hosting and worker-selection purpose; no blanket routing migration |
| `slack-to-pr` | Preserve Slack intake and reply behavior; link the complete Blueprint workflow |
| `github-skill` | Preserve the exact historical vendored skill and helper, including provenance; no silent refresh |
| `linear-to-pr` | Preserve Linear intake, alias resolution, and progress reporting; link the complete Blueprint workflow |
| `jira-to-pr` | Preserve Jira intake and filters; link the complete Blueprint workflow |
| `github-assigned-issue` | Preserve assignment-versus-label teaching and filters; link the complete Blueprint workflow |
| `monorepo-product` | Convert scope, implementation, review, revision, and owner handoff |
| `related-services` | Convert scope, ordered implementation, contract review, correction, and human handoff |
| `product-change-implementation` | Convert spec-first lifecycle and native approval; add the second practical exercise |
| `scripts/` and `.github/workflows/validate.yml` | Refresh the validator by recopying; add focused regression coverage; retain all-example parser validation and fail-closed CI |
| `.gitignore` and `LICENSE` | No change |

There is no standalone templates tree. The template owned by this work is `examples/product-change-implementation/agents/spec/skills/spec-format/SKILL.md`.

### `sdlc-issue-to-pr`: complete lifecycle

Change `factory.yaml`, its README, conflicting worker procedures, and affected automation prose together.

| Stage / worker | Inputs and outputs | Ordered routes |
| --- | --- | --- |
| `intake` / `foreman` | Check intended recipient; identify source, tracked work, affected repositories, existing PRs, and mobile work | Irrelevant request → `end`; lifecycle notification → `completion`; unknown cause, missing tracked issue, or duplicate uncertainty → `triage`; otherwise use the planning/build rules below |
| `triage` / `triage` | Return evidence, reproduction, tracked issue, scope, complexity, and unresolved decisions | Large or ambiguous work, or an explicit plan request → `spec`; otherwise non-mobile changes → `implement`; mobile-only changes → `mobile-build` |
| `spec` / `spec` | Commit the spec in a draft PR; return its path, revision, assumptions, and human answer | Requested changes → `spec`; cancellation → `end`; approved non-mobile work → `implement`; approved mobile-only work → `mobile-build` |
| `implement` / `implementer` | Receive the approved contract when present and existing non-mobile PRs; return updated PRs, head SHAs, checks, and outstanding mobile work | Outstanding mobile changes → `mobile-build`; otherwise → `review` |
| `mobile-build` / `mobile-build` | Receive iOS scope, contract, and existing iOS PR; return the iOS PR, head SHA, build/check results | → `review` after the required mobile result exists |
| `review` / `reviewer` | Review every resulting PR; classify findings by repository and by unambiguous correction versus human decision | A changed product contract → `spec`; non-mobile or mixed actionable findings → `implement`; mobile-only actionable findings → `mobile-build`; no actionable findings → `handoff` |
| `handoff` / `foreman` | Return all PRs, checks, review evidence, and unresolved limits in the originating conversation | Contract changes → `spec`; non-mobile or mixed revision → `implement`; mobile-only revision → `mobile-build`; merge/closure report → `completion`; explicit cancellation → `end` |
| `completion` / `foreman` | Inspect all linked PRs; distinguish verified merge, closure without merge, and an incomplete linked set | All required PRs verified merged → `end`; explicit cancellation → `end`; otherwise → `handoff` |

The planning/build rules used after `intake` match those after `triage`: explicit planning requirements and large or ambiguous work take priority over build routes. Do not require triage again when the request already provides its outputs.

- Add a `spec-review` gate to `spec`. Ask for approval of the linked committed revision, requested changes, or cancellation. Return the answer and referenced revision in the stage outputs.
- Add a conditional `human-decision` gate to `review` when a judgment call affects the contract or correction. Its answer chooses a contract revision, an unambiguous correction, or an explicitly accepted nonblocking finding.
- Add a `handoff-decision` gate to `handoff`. Delivery alone leaves the stage waiting. Ask for a revision, merge/closure information, or explicit cancellation. Closure without merge is not successful completion.
- Reuse existing worker conversations on revision. Mixed review findings go through non-mobile implementation first and through mobile build only when mobile work remains.
- The non-mobile implementer does not edit iOS code. The mobile worker owns its repository's PR. Review and completion wait for every required PR, not only the first successful backend PR.
- Preserve all mention/assignment handles, routing labels, repository filters, and merged/closed filters. Keep iOS outside GitHub initial intake unless the reader deliberately changes that existing boundary.
- Update the optional-mobile removal checklist to remove its repository, worker, runner, stage, routes, and prose references together.
- Replace the README's direct-to-reviewer automation suggestion with a linked review-only example or an explicitly isolated review-only path. Do not accidentally turn a human PR review request into implementation.
- Retain optional integrations. For the GitHub-only exercise, remove unused integration declarations and their automations together.

### `multi-harness`, `monorepo-product`, and `related-services`: preserve their distinct policies

- **multi-harness:** use `intake`/foreman → `implement`/implementer → `review`/reviewer → `handoff`/foreman → `end`. Unambiguous review findings return to `implement` and then to `review`. Human questions pause the affected stage. Preserve Claude Code and Codex configuration, managed-secret prerequisites, and both runner definitions.
- **monorepo-product:** use `scope`/foreman → `implement`/implementer → `review`/reviewer → `handoff`/foreman → `end`. Rejected scope ends after the existing explanatory comment and before any branch. Unambiguous findings return to implementation and independent review. Keep additive shared edits, full dependent installation before shared checks, changed-package/dependent tests, explicit owner review requests, and shared-edit draft status. The factory never marks a shared-edit draft ready on an owner's behalf.
- **related-services:** use `scope`/foreman → `implement`/implementer → `review`/reviewer. Review with unambiguous findings → `correct`/implementer → `handoff`/foreman → `end`; otherwise review → handoff. `scope` rejects breaking or unattached-repository work before creating branches. `correct` reuses the implementer's conversation and each existing PR.
- `related-services` retains one advisory contract-review pass. Handoff names the reviewed SHA and each revised head, describes corrections, and states when the revised head was not independently re-reviewed. Do not claim a clean latest-head review.
- `related-services` retains one PR per changed repository, one-repository cases without invented companion PRs, additive provider-first changes, linked-pair merge order, consumer probing against the provider's current default branch, and restoration/regeneration from the vendored schema after that probe.
- Do not broaden `related-services`' review into a general style/test review or live-service integration test. Preserve its existing boundary.
- For `multi-harness`, `monorepo-product`, and `related-services`, `end` means the configured handoff finished, not that PRs merged. Keep the PR state and human decision explicit.

### `product-change-implementation`: native approval and reviewed revisions

Use `intake`/foreman → `spec`/spec → `implement`/implementer → `review`/reviewer → `handoff`/foreman → `end`.

- `intake` preserves one-repository, one-PR scope. It rejects questions, unreproduced bugs, and multi-repository work before creating a branch. Permit the bounded documentation smoke test below as a one-PR setup exercise.
- Retain the `factory-ready` label trigger and its repository filter. Apply the factory routing label to in-scope work before asking for a gate answer.
- Remove `automations/spec-approved/automation.md`. A legacy `spec-approved` label is no longer an approval signal and starts no implementation.
- Add `automations/issue-mentioned/automation.md` for `github/issue_mentioned`, with the configured repository, `mentioned: [warp, warp-factory]`, and `labels: ["factory:Webapp"]` before substitution. Do not add PR, assignment, or unfiltered mention triggers.
- Mention intake continues the task and stage identified by its linked artifacts and conversation. An approval-shaped comment without a pending matching spec does not create work or approve a different spec.
- `factory-ready` on an issue with an open spec PR links that PR instead of creating a duplicate. Closing an old PR invalidates its approval. A replacement spec always needs fresh approval.
- Keep the spec file at `docs/specs/<issue-number>-<slug>.md` on `factory/<issue-number>-<slug>`. Keep it human-editable. Record the spec path and committed revision in the gate request and answer.
- Put `spec-review` on the `spec` stage. A human answers in the original issue with a new `@warp` mention. Requested changes return to `spec` and open a new ask for the revised file; explicit cancellation ends without implementation.
- Require explicit approval of the current committed spec. A stale label, old approval, bot comment, unrelated answer, or reviewer's confidence is not approval. When a human edits the file directly, read it again and confirm which revision the answer approves.
- Preserve the spec worker's short template and careful recorded assumptions. The worker can relay a blocking question through the foreman; it never approves an assumption itself.
- `implement` reads the approved committed file, including human edits, and uses the existing PR. It keeps the PR draft and reports the head SHA, changes, and actual checks.
- `review` independently checks the current head against that spec. Unambiguous findings return to `implement`, then to `review`. Judgment calls open a `human-decision` gate; contract changes return to `spec` for revision and fresh approval.
- `handoff` accepts only a reviewed head or an explicitly disclosed blocked result. It reports the spec, PR, checks, findings, and remaining questions. A person decides whether to mark the draft ready and merge it.
- Update the illustrative React trace, first-run checks, directory tree, customization checklist, restart instructions, and agent-setup prompt to match this behavior. Keep fabricated PR numbers, paths, test counts, and UI output labeled illustrative.
- Replace static before/after screenshots as sufficient proof of an interactive UI change with required computer-use video, while allowing screenshots as supplemental static evidence. This does not create a new UI fixture.

### Practical exercises

Both exercises use separate disposable work and factory-definition repositories owned by the reader. Reuse the setup guidance instead of copying account or billing tables.

Common preparation:

1. Enable Issues in a disposable fork of this repository.
2. Create `blueprint-demo` at `76f0f06f59a3c3d5fc29eb7699fe281073fa58c1`, push it, and select it as that fork's default branch.
3. Obtain the selected updated example and validation helper from one immutable delivered examples revision. During draft review, link that exact implementation commit; do not point to unchanged `main` as though it contains the migration.
4. Copy the example to a separate definition repository. Enumerate every repository, alias, routing-label, automation, runner, command, and skill substitution.
5. For these Python-only exercises, use `python:3.12-bookworm` for participating Linux runner images and remove application-specific setup commands. Confirm `git` and `python3` are present before validation or runtime claims.
6. Validate the complete substituted definition. Commit it and, only with separate authorization, apply it to a disposable factory through the supported GitHub-backed path. Confirm the applied revision, checkout branch, PR base, and enabled automations.
7. Use a new issue and independently approved spec for each exercise or comparison trial. Never merge trial output automatically.

#### `sdlc-issue-to-pr`: explicitly request planning and revise the same PR

- Keep the earlier `Document single-example validation` exercise.
- Ask for the single-example validator command and an explanation that exit 2 means no validation occurred.
- Say “Keep implementation changes in README.md; the committed specification is the only other allowed file.” This resolves the merged tutorial's contradictory README-only diff check.
- Require a short plan before implementation, actual convention-check results, honest validator reporting, a draft PR, and no merge.
- Apply `factory:blueprint-demo` before mentioning `@warp`.
- Request one plan change before approval. Confirm implementation remains blocked and the revised plan needs approval.
- Approve the current linked spec. Inspect the draft PR and independent review.
- Request a same-PR revision to explain network access. Confirm the PR number and branch do not change and the new head receives independent review.
- Expected final diff: `README.md` plus the single committed spec file. No worker/configuration changes belong in the work PR.

#### `product-change-implementation`: edit a committed spec before approval

- Use a separate issue titled `Document helper unit tests`.
- Request documentation in `CONTRIBUTING.md` for `python3 scripts/test_check_conventions.py -v` and `python3 scripts/test_verify_default_agents.py -v`. Those commands are absent from that pinned file.
- Restrict implementation to `CONTRIBUTING.md`; the committed spec is the only other allowed file. Require running both commands, a draft PR, and no merge.
- Apply `factory-ready`. Expect one spec-only draft PR and a native approval ask.
- Edit the committed spec on that same branch to require an explicit distinction between helper unit tests and server validation. Approve the edited revision in the original issue with `@warp`, the spec PR link, and the revision identifier.
- Confirm implementation follows the edited file and does not create another branch or PR.
- After independent review, request a revision on that PR to distinguish helper unit tests from the separate pinned-default snapshot check. Confirm another independent review covers the revised head.
- Expected final diff: `CONTRIBUTING.md` and the single spec file. Fixed test counts are observations, not promises to readers.

For both exercises, give recovery actions for failed validation, unavailable integration/access, nonmatching intake, a stale or missing approval, a closed spec PR, failed checks, and work waiting on a human. Do not invent UI controls or a runnable acquisition step while its prerequisite is held.

### Validation tooling and CI

- Recopy `scripts/validate_factory_files.py` from the current bundled `factory-files` skill. Do not hand-edit the vendored copy.
- Record the bundle revision or checksum used. Preserve its no-local-fallback contract and all three exit codes.
- Retain the `agents/` resource layout and inline prompts because the researched collector does not collect `workers/` or external prompt files. Do not use this task to claim those paths work through that public helper.
- Add `scripts/test_validate_factory_files.py` using standard-library `unittest` and mocks. Cover one unauthenticated retry on 401/403 with a forwarded token; no retry on other errors; a failed retry remaining unvalidated; exit codes 0/1/2; and collection of the actual inline-Blueprint/agent/automation/runner/scorer tree. Use synthetic credentials in tests, never live ones.
- Extend `scripts/check_conventions.py` with repository-specific coverage/layout checks, not another Blueprint parser: the five selected examples must have a top-level Blueprint and retain their `agents/` roots; focused examples are not required to have a Blueprint.
- Add regression cases to `scripts/test_check_conventions.py` for a missing required Blueprint, acceptance of a focused example without one, and a migrated example that loses its agent layout.
- Do not duplicate the server's graph, schema, or prose evaluation in a local YAML parser.
- Add the new validator tests to CI. Keep validation of all 16 examples and the existing helper tests.
- Retain the current-version drift check with `PINNED_SCHEMA_VERSION: v1alpha1`. A future registry change is a separately reported dependency, not permission to bypass CI or change versions without investigation.
- Any exit 2 remains a failed/unverified validation check, even after a retry. Do not suppress parser diagnostics, widen filters, or delete workers to obtain a pass.

### Narrow docs companion

Use a new docs draft PR. Link this specification and the exact delivered examples commit. Do not reopen merged PRs or put the expanded spec on an old merged branch.

| Existing page under `docs/src/content/docs/` | Allowed delta |
| --- | --- |
| `guides/agent-workflows/running-an-issue-to-pr-blueprint.mdx` | Replace the blocked acquisition claim with the delivered revision; reconcile all substitutions, Python runner setup, mobile/integration removal, gate names, and allowed spec-plus-README diff; retain runtime and availability holds without evidence |
| `factories/guides/monorepo-factory.mdx` | Replace the generic `single-repo-quickstart` acquisition pointers with migrated `monorepo-product` in the introduction and setup prompt; reconcile actual stage names and configuration locations only |
| `factories/guides/microservices-factory.mdx` | Replace generic `single-repo-quickstart` pointers with migrated `related-services`; retain additive contracts, one-repo cases, provider-first order, probe restoration, and the advisory review limit |
| `factories/guides/testing-and-tuning-your-factory.mdx` | Link `product-change-implementation`'s no-fixture committed-spec exercise; align approval and latest-head re-review wording; retain fresh-task/fixed-baseline comparison rules |

- Preserve each page's audience, content type, headings, and ownership. These are corrections/extensions, not new concept pages or a new tutorial.
- Keep the merged Blueprint concept, routes, stages, gates, setup, and reference pages intact.
- Do not rewrite the web-application guide, copy entire example graphs into docs, or add navigation/screenshots for this scope.
- Follow `docs/AGENTS.md`, `.agents/rules/warp-positioning.md`, terminology, compliance policy, `docs-quality`, and the current content/PR contract.
- The reader controls repositories, workers, transitions, gates, and merge. Explain actions and observable results in plain language.
- Account for every retained or new `VERIFY` marker in the docs PR. Use `engineering-review-required`; use the policy's source-owner reviewer resolution rather than guessing a reviewer.
- A changed claim can lose its adjacent hold only when its specific evidence exists. Parser success alone cannot remove availability, apply, or runtime holds.

## Decisions and alternatives

| Decision | Selected option and reason | Alternative and trade-off |
| --- | --- | --- |
| Conversion scope | Five multi-stage workflows; preserve focused examples. This follows the accepted interview boundary. | Migrating all examples makes syntax uniform but obscures their single teaching purpose. |
| Worker format | Keep existing agent definitions and `v1alpha1`; add explicit routing. | A new resource root or version adds compatibility work without adding Blueprint capability. |
| Prompt placement | Inline stage prompts. Readers inspect a complete graph and the current validator collects the required configuration. | External prompts shorten YAML but need collector compatibility work outside this scope. |
| `product-change-implementation` approval | Native gate plus filtered issue mentions; retire the approval label. It demonstrates the approved human-decision model. | Keeping two label triggers preserves the old teaching point but not the requested native-gate exercise. |
| Review policy | Re-review `product-change-implementation` revisions; preserve `related-services`' single advisory contract pass with honest SHA disclosure. | Quietly claiming every revised head was reviewed changes `related-services`' policy and overstates evidence. |
| Practical input | Two bounded documentation changes in a disposable fork. | A UI fixture permits application-level interaction but adds an unapproved app/toolchain maintenance scope. |
| Docs work | Four narrow companion-page deltas, separate from examples. | Rewriting merged concepts duplicates completed work and risks losing holds. |
| Delivery | This examples spec PR becomes the examples implementation PR; one docs companion. | A separate spec-only PR would create a third PR against the requester's two-PR instruction. |
| Readiness | Deliver drafts with named verification holds. | Treating merged source or parser acceptance as shipped behavior makes unsupported availability claims. |

## Assumptions

- Assumption: GitHub-backed definitions and GitHub issue intake remain the primary practical path. Optional existing Slack, Linear, mobile, and harness examples retain their documented prerequisites.
- Assumption: a no-fixture documentation smoke test is within `product-change-implementation`'s small one-PR scope; the main product-change trace remains illustrative.
- Assumption: for `product-change-implementation`, a human marks the delivered draft ready. This is the conservative interpretation of keeping it draft through handoff.
- Assumption: no new YAML-parsing dependency is needed for repository coverage/layout checks. The server remains the format authority.
- Assumption: authorized runtime tests will use disposable reader-controlled repositories and factories. The scope answer alone does not grant that authorization.

## Out of scope

- Product/runtime implementation, new Blueprint features, a general format migration, and fixes to public worker-path or prompt-file collection.
- Blanket conversion of minimal, intake-only, hosting, or verification-only examples.
- A new app fixture, new example directory, new trigger family, or expanded integration access.
- Refreshing historical default agents or the historical GitHub skill.
- Adding or expanding self-improvement behavior; leave existing scorer settings untouched.
- Rewriting merged concept/reference docs or unrelated guides.
- Live configuration application, publication, automatic PR promotion in this delivery, or merge.
- The two previously deferred product screenshot embeds. Their deferral does not waive runtime or visual verification.

## Validation criteria

Report every check as passed, failed, or not run with an exact reason. Record source and tested commits, service URL, schema version, task/run links, PR heads, and evidence in the two draft PRs. Specification-stage baseline checks are not implementation acceptance results.

### Static and parser checks

Run from this repository after implementation:

```bash
python3 scripts/check_conventions.py
python3 scripts/test_check_conventions.py -v
python3 scripts/test_verify_default_agents.py -v
python3 scripts/test_validate_factory_files.py -v
status=0
for example in examples/*/; do
  python3 scripts/validate_factory_files.py "$example" --server-root https://app.warp.dev || status=1
done
test "$status" -eq 0
git --no-pager diff --check
```

- Require exit 0 for every one of the 16 parser invocations; the loop's final status alone is insufficient. Record an individual result for every example.
- Validate complete reader-substituted `sdlc-issue-to-pr` and `product-change-implementation` definitions separately with `python3 scripts/validate_factory_files.py DEFINITION_ROOT --server-root https://app.warp.dev`.
- Run the full `.github/workflows/validate.yml` checks after helper or CI changes.
- Compare the copied validator's SHA-256 against its bundled source. Require byte-for-byte equality.
- Compare the diff against the disposition table. Require no execution changes outside the five selected examples except the specified shared checks/helper refresh.
- Confirm `warp-default-agents` and `github-skill`'s pinned configuration/vendor content remains unchanged with `git --no-pager diff BASE_COMMIT -- examples/warp-default-agents examples/github-skill scripts/verify_default_agents.py`, where `BASE_COMMIT` is the recorded implementation base.
- Inspect each graph and worker prompt together against the stage tables. Produce a route checklist covering every conditional branch, every gate answer, optional mobile removal, and every stage worker binding. Server validation establishes reference correctness; the runtime cases below establish behavior.

### Docs checks

Run from the docs repository:

```bash
python3 .agents/skills/style_lint/style_lint.py --changed
python3 .agents/skills/check_for_broken_links/check_links.py --internal-only
npm run typecheck
npm run test:heading-vars
npm run build
npm run test:heading-tocs
npm run test:homepage-json-ld
```

- Run `python3 .agents/skills/doc_quality_policy/check_compression_contract.py FILE --content-type TYPE` for each changed content page using its existing content type.
- Run `python3 .agents/skills/doc_quality_policy/check_pr_contract.py --body BODY_FILE CHANGED_CONTENT_FILES` with the actual PR body and changed paths.
- Reconcile the four-page diff with the examples head. Require no dangling acquisition placeholders, missing substitutions, unsupported runnable claims, or lost `VERIFY` accounting.
- Apply `factory:docs-factory` to both PRs and `warpy-factory` to the docs PR. Retain draft status and the required managed attribution/artifact blocks.

### Preserved seven runtime cases

Run only after separate authorization to use a disposable factory and apply a definition. Otherwise record the missing prerequisite and retain the corresponding hold.

| Case | Check and expected result |
| --- | --- |
| Labeled GitHub issue plus configured mention | Execute the `sdlc-issue-to-pr` request; one intended intake path reaches the workflow and asks for its explicitly required plan approval |
| PR follow-up matching mention/assignment conditions | Record the event delivery and resulting work; overlapping triggers within one automation do not duplicate the same delivery; do not assume distinct deliveries are deduplicated |
| Missing routing label or repository outside the filter | Send a fresh nonmatching input; the specialized GitHub automation does not start work; do not claim a fallback without evidence |
| Requested plan changes | Request a concrete change before approving; no implementation starts; the revised spec asks for a fresh answer |
| Human revision after the first draft PR | Request the documented revision; the same task, branch, and PR continue through implementation and independent review |
| Definition edit while the run exists | Record old and new applied revisions; the existing task retains its selected Blueprint; a separately started task selects the new one |
| PR closed without merge | Close a disposable PR without merging; the foreman reports closure and does not mark the work merged or successfully complete |

### Added acceptance cases

- **product-change-implementation approval:** execute the complete no-fixture exercise; show the spec-only draft, unanswered native gate, human edit, approval of that revision, same-PR implementation, independent review, revision, and review of the new head.
- **product-change-implementation nonapproval:** test an unrelated reply, a legacy approval label, an approval without a matching open spec, and a replacement spec after closure. None authorizes implementation without fresh approval of the current spec.
- **multi-harness:** record implementation and review worker/harness identities and preservation of credential prerequisites. A missing credential is a blocker, not a reason to substitute a different harness.
- **monorepo-product:** test product-only, additive shared-package, and out-of-product inputs. Confirm dependent installation/checks, owner review request, and shared-edit draft status; no branch for declined scope.
- **related-services:** test provider-only, consumer-only, paired additive, and breaking requests. Confirm correct PR count, reciprocal links only for a pair, human merge order, default-branch probe, restored final client, and reviewed-versus-revised SHA disclosure.
- **All five:** inject or observe a failed required check. Handoff reports failure and missing evidence rather than calling the change verified.

### Visual proof and publication holds

- Use computer use after the relevant build succeeds. Record video of authorized setup/definition inspection, request submission, pending gate, human approval, draft PR, independent review, and same-PR revision. Link the tested commit and observed UI labels.
- Capture the `sdlc-issue-to-pr` and `product-change-implementation` workflows separately when both cannot be shown clearly in one recording. Use static screenshots only as supplemental proof of a genuinely static state.
- For the docs MDX changes, inspect the built changed pages for readable commands, links, callouts, and unbroken layout. This does not replace the live workflow proof.
- Do not clear a hold using an illustrative trace, source read, parser pass, another task's captures, or a draft PR's existence.
- Preserve explicit holds for public availability/access; complete-definition validation and successful application; public-parser/worker-path compatibility; all seven runtime cases; acquisition/substitution reconciliation; real setup-to-same-PR-revision proof; publication; and human merge.
- Draft implementation may be handed off with unavailable checks named. It must not be presented as published, production-ready, successfully applied, or runtime-verified while those checks remain held.
