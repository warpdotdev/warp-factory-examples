# 26: Product-change implementation

This single-repository factory implements small, user-visible changes. The
`factory-ready` label requests a spec in a draft pull request. A human reviews
it and adds `spec-approved` before implementation starts on that same
pull request.
The worked trace below shows the expected spec, implementation, review, and
handoff. Its paths and check results are illustrative, not a recorded run.

Use this example to test and tune a factory. Run one small change, compare
its artifacts with the trace, then adjust one setting and start a fresh
trial from the same recorded baseline. For intake from Slack
or a tracker, or the triage stage, see
[`02-sdlc-issue-to-pr`](../02-sdlc-issue-to-pr). This example stays on one
task trace on purpose.

## What this example shows

- A human controls the spec gate. Implementation cannot start until a person
  adds `spec-approved`. The foreman is told never to add that label, and
  the default bot policy would ignore the label if it did.
- Two labels start work, and comments report progress. Both automations are
  `github/issue_labeled` on the same repository, and the foreman re-enters the
  procedure at the right stage from the issue's own state instead of assuming
  an earlier run.
- The spec is a file, not a conversation. The spec agent commits
  `docs/specs/<issue>-<slug>.md` in a draft pull request. A human can edit it
  in place before approving, and the implementer builds on that same branch
  and pull request.
- The review agent reports findings classified as unambiguous or
  judgment calls. The foreman sends the first kind back to the implementer
  once and posts the second kind on the pull request for a human.
- A team can tune spec detail, implementer model, and reviewer strictness
  after a first run. Each setting is in one file.

## Directory structure

```
factory.yaml                       acme/webapp, alias Webapp, model auto
agents/
  foreman/agent.md                 FOREMAN, two entry points, holds the approval gate
  spec/agent.md                    SPEC, writes docs/specs/<issue>-<slug>.md in a draft PR
    skills/spec-format/SKILL.md    the spec template; the spec-detail knob
  implementer/agent.md             IMPLEMENT (model: auto-genius), builds on the spec PR's branch
  reviewer/agent.md                REVIEW, findings report to the foreman, never posts on the PR
automations/
  factory-ready/automation.md      github/issue_labeled, factory-ready: write the spec
  spec-approved/automation.md      github/issue_labeled, spec-approved: implement, review, hand off
runners/
  linux-node.yaml                  4 vCPU / 8 GB, node:22-bookworm-slim, shared by all four agents
```

## How intake and approval are routed

Both automations watch `acme/webapp` for `github/issue_labeled`, and both
route to the foreman (an automation with no `agent:` field goes to the
foreman). They differ only in the `labels` filter: `factory-ready` starts
the spec stage, `spec-approved` starts implementation. Filters combine with
AND, and on `issue_labeled` the `labels` filter matches the label that was
just added, compared exactly (case-sensitive), so applying either label
fires exactly one automation, once.

`skip_bots` is not set, so it takes its default, `all`. Label changes made by
bots, including Warp's own GitHub App, never fire either automation. The
foreman applies the factory's routing label, `factory:<alias>`, to the issue
and the pull request as it works. That label is not in either filter and would
be skipped as a bot event anyway. Only a label a person adds starts a run.

The automation bodies say "do not assume a previous run exists", and the
foreman reads the issue's labels, comments, and linked spec pull request to
find the stage. New activity on an issue the factory already handles continues
the same work item, but the prompts do not depend on that. A `spec-approved`
run that starts fresh still finds the spec pull request from the issue.

### The approval gate

As in the default agents, when a spec exists the foreman does not start
implementation until a human approves the spec, and it never approves a
spec on a human's behalf. The default agents accept a written confirmation
or an approval of the draft pull request. This example narrows approval to
one signal so a first run has exactly one thing to check.

- **Approve:** add the `spec-approved` label to the issue. Nothing else
  counts, not a comment that says "approved", not an approving review on
  the spec pull request, not the foreman's own confidence.
- **Change the spec first:** edit `docs/specs/<issue>-<slug>.md` on the spec
  pull request's branch (the GitHub web editor is enough), commit, then add
  the label. The implementer reads the committed file at approval time, so
  your edits are the contract.
- **Answer a question:** if the foreman posts a question during
  implementation, put the answer in the spec file, then remove and re-add
  `spec-approved`. Re-adding the label fires the automation again, and the
  implementer continues on the same branch.
- **Start over:** close the spec pull request and remove `spec-approved` from
  the issue if present. Fix the issue text, then remove and re-add
  `factory-ready`. Review the replacement spec before adding `spec-approved`
  again. The old approval does not carry over. Adding an already-present label
  emits no new `issue_labeled` event. A human resets and approves. The factory
  never changes `spec-approved` itself.

There is no trigger for free-text replies in this example. To let a
maintainer steer the factory with `@warp` comments instead, add the
`issue_mentioned` automation from
[`02-sdlc-issue-to-pr`](../02-sdlc-issue-to-pr).

### Unmatched events

- A label other than the two, or either label on another repository,
  starts nothing.
- When `factory-ready` is added to an out-of-scope issue, the foreman
  comments why and stops without creating a branch, spec, or label.
  Out-of-scope issues include questions, bugs with no reproduction, work
  outside `acme/webapp`, and work that needs more than one pull request.
- When `factory-ready` is added to an issue that already links an open spec
  pull request, the foreman comments with the existing pull request and stops.
- When `factory-ready` is added with no open spec pull request but
  `spec-approved` still present, the foreman asks a human to remove
  `spec-approved`, then remove and re-add `factory-ready`. It stops without
  creating a replacement spec.
- When `spec-approved` is added to an issue with no open spec pull request,
  the foreman comments that there is nothing to approve and stops.
- The default bot policy skips labels added by bots or other automations.

## Runner configuration

All four agents share `linux-node`, which uses `node:22-bookworm-slim`
with 4 vCPU and 8 GB of memory. The implementer and reviewer use the
repository's documented lint, typecheck, and test commands.

## Customize the example

1. Copy this example into your definition repository, following
   [Use an example](../../README.md#use-an-example).
2. Connect GitHub to your Warp team. See [Connect GitHub to your
   factory](https://docs.warp.dev/factories/integrations/github/).
3. Replace `acme/webapp` in `factory.yaml`,
   `automations/factory-ready/automation.md`,
   `automations/spec-approved/automation.md`, and the scope check in
   `agents/foreman/agent.md` with a repository your Warp team's GitHub
   installation can reach.
4. Create the two labels, `factory-ready` and `spec-approved`, in that
   repository. Warp creates `factory:<alias>` for you when the factory is
   registered, but not these two. Rename them in both automations and in
   `agents/foreman/agent.md` if your team uses other names.
5. Set `alias` in `factory.yaml`. It becomes the routing label,
   `factory:<alias>`, and the foreman's handle.
6. Replace the runner's `dockerImage` in `runners/linux-node.yaml` with an
   image that has your toolchain.
7. Make sure the repository documents its lint,
   typecheck, and test commands (a README or `package.json` scripts are
   enough). The implementer and reviewer run "the repository's documented
   checks". If they are not documented, name them in step 4 of
   `agents/implementer/agent.md` and step 2 of `agents/reviewer/agent.md`.
8. Change where specs live if `docs/specs/` is wrong for your repository.
   The path and the branch pattern are in `agents/spec/agent.md`.

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
> the PR branch if it needs changes. When it is right, add the
> `spec-approved` label to this issue.

Nothing else happens. The factory writes no code, creates no second branch,
and does not add `spec-approved`.

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
and the duration assumption, then commit. They add `spec-approved` to issue
#128. Implementation and review must now use the approved 1.5-second
duration, not the original draft's 2 seconds.

#### The implementation and review

The foreman finds pull request #131 from the issue and dispatches the
implementer, which works on `factory/128-copy-link-button`. The pull request
first arrives with the following changes.

- The title changes to `Add a "Copy link" button to the share dialog (#128)`,
  and the pull request is marked ready for review.
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
  - Two screenshots of the dialog, before and after the click, attached.
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

The foreman sends findings 1 and 2 to the implementer as one follow-up.
The implementer pushes a second commit that clears the timer in the effect
cleanup and extends the rejection test, re-runs the three checks, and
updates the Verification section. The count stays at 27 passed because an
assertion was added, not a test case.

The foreman posts finding 3 on pull request #131 as a comment-only review,
neither approving nor requesting changes. It confirms `factory:Webapp` is
on the issue and the pull request, then comments on the issue.

> PR ready for review: acme/webapp#131. Verified with `npm run lint`,
> `npm run typecheck`, and `npm test` (27 passed, 4 new). Review found two
> issues, both fixed on the branch: an uncleared reset timer, and a
> rejection test that did not check the text selection. One question is
> open on the PR for you: what the button should do when the clipboard API
> is absent. A human merges.

The run stops there. The pull request is not merged, the issue is not closed,
and `spec-approved` was added exactly once, by a person.

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

Use a throwaway issue like the one in the worked trace and confirm these
results in order.

1. Adding `factory-ready` produced exactly one draft pull request, on a
   `factory/<issue>-<slug>` branch, whose only change is
   `docs/specs/<issue>-<slug>.md`, plus one issue comment with the approval
   instruction. Nothing else changed in the repository.
2. Nothing further happened until you added `spec-approved`. The Runs page
   shows no run in between.
3. Adding `spec-approved` produced commits on the same branch, the pull
   request retitled and marked ready for review with the description shape
   above, tests in the diff, at most one comment-only review on the pull
   request, and one issue comment with the pull request link and the
   verification evidence.
4. The factory never merged, never approved the pull request, and never added
   `spec-approved`. The issue's timeline shows a person as the only actor
   on that label.
5. Test a restart after approval. Close the old spec pull request, remove
   `spec-approved`, update the issue, then remove and re-add `factory-ready`.
   The replacement spec arrives in a draft pull request and waits without
   implementation. Review it, then add `spec-approved` again. Only that fresh
   human approval starts implementation on the replacement pull request's
   branch. Confirm the issue timeline shows a person removing and re-adding
   the approval label.

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

Paste this into your factory's foreman, the factory web composer, or a
coding agent connected to your factory over MCP, after replacing the
angle-bracket placeholders.

```text title="Set up the product-change factory for my repository"
Read https://github.com/warpdotdev/warp-factory-examples/tree/main/examples/26-product-change-implementation
and set up the same factory for my repository <owner>/<repo>.

1. Copy the example's tree into <path in my definition repository>, keeping
   the layout: factory.yaml; agents/foreman, agents/spec (with
   agents/spec/skills/spec-format), agents/implementer, agents/reviewer;
   automations/factory-ready and automations/spec-approved;
   runners/linux-node.yaml.
2. Replace every acme/webapp with <owner>/<repo>: factory.yaml, both
   automations, and the scope check in agents/foreman/agent.md. Set alias
   to <alias>.
3. Set the runner's dockerImage to <image with my toolchain>, keeping the
   instance shape a power of two.
4. My documented checks are <lint command>, <typecheck command>, and
   <test command>. Name them in step 4 of agents/implementer/agent.md and
   step 2 of agents/reviewer/agent.md.
5. Create the labels factory-ready and spec-approved in <owner>/<repo>.
6. Validate the tree and open a pull request to my definition repository.
   Do not change the human gates: a person removes spec-approved before
   restarting and adds it again only after reviewing the replacement spec.
   The factory never changes spec-approved itself and never merges.
Then help me run the first test: pick one small, user-visible change from
my backlog, write the issue the way the example's sample issue is written,
and tell me what to expect at each stage so I can compare it with the
example's trace.
```
