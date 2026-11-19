# 26: Product-change implementation

Use an explicit Blueprint to take one small change from a committed spec to a
draft PR on the same branch. You edit and approve the spec in the original
issue before implementation. A separate reviewer checks each revised head.
A person decides readiness and merge.

The [disposable-fork exercise](#exercise-edit-a-committed-spec) needs no application
fixture. The React trace below is illustrative, not a recorded run. To compare
settings, use fresh issues and independently approved specs from the same
baseline. For triage, optional mobile work, and other intake sources, see
[`02-sdlc-issue-to-pr`](../02-sdlc-issue-to-pr).

## What this example shows

- `factory.yaml` owns `intake`, `spec`, `implement`, `review`, and `handoff`,
  their ordered prose routes, and the `spec-review` and `human-decision` gates.
  The files under `agents/` select each worker's role, model, and runner.
- `factory-ready` requests a spec. A filtered `@warp` issue mention answers
  the pending gate or requests a revision. The retired `spec-approved` label
  starts nothing and approves nothing.
- The spec is a human-editable file at `docs/specs/<issue>-<slug>.md` in a
  draft PR. Implementation reads the approved committed revision, including
  your edits, rather than relying on the spec worker's conversation.
- Unambiguous findings return to implementation on the same PR, then to
  independent review. A contract change returns to a revised spec and fresh
  approval. Nits alone do not cause another round.

## Directory structure

```text
factory.yaml                       inline Blueprint, acme/webapp, alias Webapp
agents/
  foreman/agent.md                 FOREMAN, communication and role boundaries
  spec/agent.md                    SPEC, writes the committed spec
    skills/spec-format/SKILL.md    short spec template
  implementer/agent.md             IMPLEMENT, model auto-genius, same draft PR
  reviewer/agent.md                REVIEW, reports current-head findings to foreman
automations/
  factory-ready/automation.md      github/issue_labeled, factory-ready
  issue-mentioned/automation.md    github/issue_mentioned, handle + routing label
runners/
  linux-node.yaml                  shared Linux runner
```

## How intake and approval are routed

Both automations filter to `acme/webapp` and reach the foreman. The label
trigger matches the added label `factory-ready`. The mention trigger requires
`mentioned: [warp, warp-factory]` and `labels: ["factory:Webapp"]`. Apply the
routing label before a mention; filter keys combine with AND. Preserve both
handles. Change the routing label when you change `alias`.

The foreman applies `factory:<alias>` to in-scope work before asking for a gate
answer. Mention the foreman in a new issue comment to answer it. Read the linked
PR and current spec revision first. Matching follow-ups continue the pending
stage using linked artifacts and conversation, not the current label alone.

### The approval gate

The native `spec-review` gate in `factory.yaml` holds the spec stage until you
answer in the original issue with a new `@warp` mention. Name the spec PR and
committed revision in the answer.

- **Approve:** explicitly approve the current committed file on the open PR.
- **Change the spec:** request a concrete change, or edit and commit the file
  on that same branch. The revised file needs a fresh ask and approval. If
  you edited directly, identify the edited revision you approve.
- **Answer a question:** reply to the pending question in the original issue.
  A question back or an unrelated reply is not approval.
- **Cancel:** explicitly cancel the work. No implementation follows.
- **Start over:** close the old spec PR, update the issue, then remove and
  re-add `factory-ready`. Review and approve the replacement spec separately.
  Closing the old PR invalidates its approval. An already-present label
  emits no new label-added event.

An old approval, legacy label, bot comment, or reviewer confidence cannot
approve a different revision. A `@warp` approval without a pending matching
spec does not start work.

### Unmatched events

A different label, an issue outside the configured repository, a mention
without the routing label, and all PR or assignment events match neither
specialized automation. Do not assume another automation handles them.
The default bot policy skips bot-generated events.

The intake stage rejects questions, unreproduced bugs, and work spanning
repositories before any branch. It permits the bounded documentation exercise
below. Reapplying `factory-ready` to an issue with an open spec PR links that
PR instead of creating a duplicate.

## Runner configuration

All four agents share `linux-node`, which uses `node:22-bookworm-slim`
with 4 vCPU and 8 GB of memory. The implementer and reviewer use the
repository's documented lint, typecheck, and test commands.

## Customize the example

1. Copy this example into your definition repository, following
   [Use an example](../../README.md#use-an-example).
2. Connect GitHub to your Warp team. See [Connect GitHub to your
   factory](https://docs.warp.dev/factories/integrations/github/).
3. Replace `acme/webapp` in `factory.yaml` (repository and intake prompt),
   both automation filters, and any repository-specific instructions.
4. Create `factory-ready` in that repository. Set `alias` in `factory.yaml`
   and replace `factory:Webapp` in the mention filter with `factory:YOUR_ALIAS`.
   Confirm the matching routing label exists before sending a mention.
5. Select a runner image with your toolchain, including Git, in
   `runners/linux-node.yaml`. For the Python exercise use `python:3.12-bookworm`.
6. Document the real lint, typecheck, and test commands in your work repository,
   or name them in the `implement` and `review` stage prompts. Do not install an
   application toolchain for a documentation-only exercise.
7. To change where specs live, update the `spec` stage and `agents/spec/agent.md`
   together. Keep the approved revision and same-PR contract explicit.

## Validate the example

Run these checks from the repository root.

```bash
python3 scripts/validate_factory_files.py examples/26-product-change-implementation
python3 scripts/check_conventions.py
```

The validator checks the definition's syntax and the trigger and filter
keys against Warp's parser. It cannot check that the labels exist, that the
GitHub installation reaches the repository, or that the agents follow the
approval and restart instructions. Check those prerequisites and behaviors
with real runs.

## Test the factory

Commit and push your customized definition. Create a factory in Warp with a
GitHub-backed definition pointing at your repository, branch, and directory
containing `factory.yaml`, as described in
[Use an example](../../README.md#use-an-example). Register it before
creating test issues.

Compare a throwaway issue with the worked trace below, then follow
[First-run checks](#first-run-checks). The trace is illustrative, not a
recorded run.

### Worked trace

The trace assumes `acme/webapp` is a TypeScript React app. `npm ci`
installs it, and `npm run lint`, `npm run typecheck`, and `npm test`
(Vitest and Testing Library) are its documented checks.
`src/components/ShareDialog.tsx` renders a share URL in a read-only input
and has tests in `src/components/ShareDialog.test.tsx`.
`src/components/ui/Button.tsx` is the shared button.
`src/components/InviteDialog.tsx` already places an action button next to an
input, which is the pattern to copy. If your repository differs, your
artifacts differ in detail. They should still follow the same stages.

#### The sample issue

A maintainer opens issue #128 and adds `factory-ready`:

```text
Title: Add a "Copy link" button to the share dialog

The share dialog (src/components/ShareDialog.tsx) shows the share URL in a
read-only text field, and people select the text and copy it by hand. Add a
"Copy link" button next to the field that copies the URL to the clipboard
and confirms that it did.

Acceptance:
- Clicking the button copies the exact URL shown in the field.
- The button confirms success briefly, then returns to its normal label.
- Keyboard users can reach and activate the button.
```

The issue is deliberately incomplete: it does not say how long "briefly"
is, what happens when the copy fails, or where the confirmation appears.
Those are the spec agent's job.

#### The draft spec pull request

The foreman's scope check passes (one repository, one pull request,
user-visible). The spec agent reads `ShareDialog.tsx`, its tests, and
`InviteDialog.tsx`, then opens draft pull request #131,
`Spec: Add a "Copy link" button to the share dialog (#128)`, on branch
`factory/128-copy-link-button`, with a single commit that adds one file,
`docs/specs/128-copy-link-button.md`. The foreman comments on the issue:

> Spec ready for review: acme/webapp#131. Review the spec. Edit the file on
> the PR branch if it needs changes. Reply in this issue with a new `@warp`
> mention and approve the current committed spec revision, request changes,
> or cancel. The spec path and committed revision accompany this ask.

Nothing else happens. The factory writes no code, creates no second branch,
and waits at `spec-review`.

#### The expected spec file

```markdown
# Add a "Copy link" button to the share dialog (#128)

## Summary
The share dialog shows the share URL in a read-only field, and people copy
it by hand. Add a "Copy link" button that writes the URL to the clipboard
and confirms it, so sharing takes one click.

## Behavior
1. The dialog shows a "Copy link" button immediately after the URL field.
2. Activating the button writes the field's current value to the clipboard.
3. On success the button's label changes to "Copied" for 2 seconds, then
   returns to "Copy link".
4. If the clipboard write fails, the label changes to "Copy failed" for 2
   seconds and the field's text is selected, so the user can copy by hand.
5. The button is a native button element: it is in the tab order and
   activates with Enter and Space. The label change is announced to
   assistive technology.

## Implementation notes
- Change `src/components/ShareDialog.tsx`. Add the button with the shared
  `Button` from `src/components/ui/Button.tsx` (`variant="secondary"`),
  placed the way `InviteDialog.tsx` places its action next to its input.
- Use `navigator.clipboard.writeText`. Do not add a clipboard library.
- Keep the label state in the component. Clear the reset timer on unmount.
- Render the label inside an element with `aria-live="polite"`.

## Acceptance criteria
1. `ShareDialog.test.tsx`: clicking "Copy link" calls
   `navigator.clipboard.writeText` with the exact value shown in the field.
2. `ShareDialog.test.tsx`: after a successful copy the button reads
   "Copied", and reads "Copy link" again after 2 seconds (fake timers).
3. `ShareDialog.test.tsx`: when `writeText` rejects, the button reads
   "Copy failed" and the field's text is selected.
4. `ShareDialog.test.tsx`: the button is reachable with Tab and activates
   with Enter and Space.
5. `npm run lint`, `npm run typecheck`, and `npm test` pass.

## Assumptions
- The confirmation lasts 2 seconds. The issue says "briefly".
- The copied value is the field's value as displayed, not a URL rebuilt
  from application state.
- The confirmation lives in the button, not a toast, because the dialog
  has no toast region today.

## Out of scope
- Changing how the share URL is generated.
- A "Copy link" action anywhere outside the share dialog.
```

A much longer spec may need a shorter template. See
[Tune the factory](#tune-the-factory). Check that unresolved choices appear
under Assumptions for human approval and that
each acceptance criterion names a test, command, or manual check. Omit
Assumptions when there are none.

#### The human's spec revision and approval

A maintainer reads the spec on pull request #131. Say they want a shorter
confirmation: they edit `docs/specs/128-copy-link-button.md` on the branch,
changing "2 seconds" to "1.5 seconds" in behaviors 3 and 4, criterion 2,
and the duration assumption, then commit. In issue #128 they post a new `@warp` mention approving
the edited spec on #131 and naming its committed revision. Implementation and review must now use the approved 1.5-second
duration, not the original draft's 2 seconds.

#### The implementation and review

The foreman finds pull request #131 from the issue and dispatches the
implementer, which works on `factory/128-copy-link-button`. The pull request
first arrives with the following changes.

- The title changes to `Add a "Copy link" button to the share dialog (#128)`,
  and the pull request remains draft.
- The commits contain the draft spec, the human's spec revision, then
  implementation.
- The files include `docs/specs/128-copy-link-button.md` (approved version
  retained), `src/components/ShareDialog.tsx` (about 40 lines added, 3
  changed), and `src/components/ShareDialog.test.tsx` (4 new test cases).
  Neither `package.json` nor the lockfile changes.
- The description contains the following summary, changes, and verification.

  ```markdown
  ## Summary
  Adds a "Copy link" button to the share dialog that copies the displayed
  URL and confirms in place. Closes #128. Spec:
  docs/specs/128-copy-link-button.md.

  ## Changes
  - `ShareDialog.tsx`: secondary `Button` after the URL input; label state
    `idle | copied | failed` with a 1.5 s reset; `aria-live="polite"` on the
    label; selects the input text on failure.
  - `ShareDialog.test.tsx`: copies the exact value; confirms and resets
    after 1.5 seconds with fake timers; shows "Copy failed" on rejection;
    Tab reaches the button, and Enter and Space activate it.

  ## Verification
  - `npm run lint`: clean. `npm run typecheck`: clean.
  - `npm test`: 27 passed (4 new).
  - Computer-use video of copying the displayed URL, confirmation, reset,
    keyboard activation, and failure fallback attached. Screenshots are
    supplemental static evidence.
  ```

The foreman then dispatches the reviewer on pull request #131. The reviewer
returns the following findings report in full.

1. **Blocking, unambiguous.** `src/components/ShareDialog.tsx:52`: the
   1.5-second reset is a `setTimeout` that nothing clears. Unmounting the
   dialog before it fires leaves a callback targeting an unmounted
   component. The spec's implementation notes require clearing it on
   unmount. Correction: keep the timer id in a ref and clear it in the
   effect cleanup.
2. **Should-fix, unambiguous.** `src/components/ShareDialog.test.tsx:48`:
   the rejection test asserts the "Copy failed" label but not that the
   field's text is selected, so criterion 3 is half-tested. Correction:
   after the rejected write, assert the input's `selectionStart` is 0 and
   `selectionEnd` is the value's length.
3. **Should-fix, judgment call.** `src/components/ShareDialog.tsx:41`:
   the implementation does not define behavior when `navigator.clipboard`
   is unavailable. The spec covers a rejected write, not an absent API.
   Options: treat an absent API like a failed write (show "Copy failed",
   select the text), or hide the button when the API is absent. A product
   decision.

Verdict: human decision needed.

The foreman opens `human-decision` for finding 3 and relays the options in the
original issue. A maintainer chooses to treat an absent API as a failed write.
That changes the contract, so the spec is revised on #131 and the new committed
revision receives fresh approval before implementation continues.

The implementer fixes the timer, strengthens the selection assertion, and
handles the approved absent-API behavior on the same branch and PR. It reruns
the checks and updates verification. The foreman dispatches independent review
of the new head. If that review finds another actionable defect, correction and
review repeat. Fixed test counts above are illustrative observations, not a
required count.

The foreman reports #131, the approved spec revision, delivered and reviewed
SHAs, actual checks, review findings, and remaining limits on the issue. The PR
stays draft. A person decides whether to mark it ready and merge; ending this
workflow means handoff, not merge.

#### The out-of-scope issue

A maintainer labels issue #129, "Why does the share URL sometimes have a
trailing slash?", with `factory-ready`. The foreman comments:

> This factory implements small, user-visible changes to acme/webapp that
> one PR can deliver. This issue is a question about current behavior, not a
> change to make. Describe the change you want, then add `factory-ready`
> again.

The foreman creates no branch, spec pull request, or label. The same comment
shape applies to a bug with no reproduction and to work that spans another
repository.

### First-run checks

Use a throwaway issue and record the actual results, not only run status.

1. `factory-ready` produces one spec-only draft PR and a `spec-review` ask
   naming its file and revision. Implementation waits while it is unanswered.
2. Request a spec change. Check for a revised file and fresh ask, without
   implementation. Edit the file yourself and approve that committed revision
   in the original issue with `@warp`.
3. Confirm implementation uses the approved file, branch, and PR and leaves it
   draft. Inspect the current-head independent review and reported checks.
4. Request a concrete same-contract revision with `@warp` on the issue. Check
   that the same PR gets new commits and another independent review of its head.
5. Test an unrelated reply, a legacy approval label, and an approval with no
   matching open spec. None authorizes implementation.
6. Close an old spec PR, then restart with `factory-ready`. The replacement
   waits for its own approval. No old approval transfers to it.
7. Observe a failed required check. Handoff must name the failure, not report
   the change as verified. The factory never approves or merges a PR.

## Tune the factory

Change one setting at a time. Record the requirements, starting commit,
configuration, output, and per-stage cost of the baseline trial. For each
comparison, use a separate test issue and a new branch and pull request
starting at that commit, with no implementation commits from earlier trials.
Review the new spec and approve it separately. Do not merge trial output.

Closing a pull request or reapplying a label continues or restarts existing
work. It does not create an independent comparison. Check the new branch's
baseline and diff. Repeat unchanged settings before attributing a difference
to tuning.

1. Adjust spec detail in `agents/spec/skills/spec-format/SKILL.md`. If specs
   are too thin, require unresolved behavior to be surfaced for approval
   and acceptance criteria with executable checks. If specs are too heavy
   for one-file changes, trim the template or loosen the "Scale to the change"
   rule so Implementation notes become optional.
2. Adjust the implementer model using the `model:` line in
   `agents/implementer/agent.md`, currently `auto-genius`. Compare `auto`,
   `auto-efficient`, or another supported Warp Agent model on simple changes.
   Change this agent's model, not `agentDefaults.model`, which affects every
   agent inheriting it. Compare candidates on the same task with
   [benchmarks](https://docs.warp.dev/factories/benchmarks/) before
   adopting one.
3. Adjust reviewer strictness in the "Strictness" section of
   `agents/reviewer/agent.md`. If there are too many revision rounds, narrow
   what blocks without removing correctness checks. If there are too few
   findings, add the failure modes your reviews keep catching by hand.
   You can compare a reviewer-specific `model:` in repeated fixed-baseline
   trials. A different model alone does not establish review quality.

Each stage is a separate run on the factory's
[Runs page](https://docs.warp.dev/factories/factory-dashboard/#inspect-runs).
Compare its duration and cost per agent after a change.

## Set up with an agent

Replace the uppercase placeholders, then send this to your foreman or a
coding agent connected through [MCP](https://docs.warp.dev/factories/factory-mcp/).

```text title="Set up the product-change factory"
Copy example 26 from the immutable examples revision linked in this README's
exercise, including factory.yaml, agents/, both automations, and runners/.
Use OWNER/REPO as the work repository and DEFINITION_PATH for the definition.
Replace acme/webapp in the repository entry, Blueprint intake, and automation
filters. Set alias to ALIAS and the mention label to factory:ALIAS.
Use RUNNER_IMAGE with Git and my toolchain. My checks are CHECK_COMMANDS.
Keep the native spec-review gate, editable committed spec, explicit approval
of its current revision in the original issue with @warp, same-PR implementation,
and independent review of revised heads. Keep PRs draft; never merge.
Validate the complete substituted tree. Open a definition PR, then list the
GitHub access, labels, availability, and application steps that still need me.
Do not apply a live configuration without separate authorization.
```
