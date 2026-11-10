# 26: Product-change implementation

A single-repository factory for small, user-visible changes. The
`factory-ready` label requests a spec in a draft PR; a human reviews it and
adds `spec-approved` before implementation starts on that same PR.
The worked trace below shows the expected spec, implementation, review, and
handoff. Its paths and check results are illustrative, not a recorded run.

This is the worked example for the testing-and-tuning loop: run one small
change, compare its artifacts with the trace, then adjust one setting and
start a fresh trial from the same recorded baseline. For intake from Slack
or a tracker, or the triage stage, see
[`02-sdlc-issue-to-pr`](../02-sdlc-issue-to-pr); this example stays on one
task trace on purpose.

## What it demonstrates

- A spec gate a human controls: implementation cannot start until a person
  adds `spec-approved`. The foreman is told never to add that label, and
  the default bot policy would ignore the label if it did.
- Two labels in, comments out. Both automations are `github/issue_labeled`
  on the same repository, and the foreman re-enters the procedure at the
  right stage from the issue's own state instead of assuming an earlier run.
- A spec that is a file, not a conversation: the spec agent commits
  `docs/specs/<issue>-<slug>.md` in a draft PR, a human can edit it in place
  before approving, and the implementer builds on that same branch and PR.
- Review as a report: the review agent classifies findings as unambiguous or
  judgment calls, the foreman sends the first kind back to the implementer
  once and posts the second kind on the PR for a human.
- The three tuning knobs a team reaches for after a first run, each in one
  file: spec detail, implementer model, reviewer strictness.

## Tree

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

`skip_bots` is not set, so it takes its default, `all`: label changes made
by bots, including Warp's own GitHub App, never fire either automation. The
foreman applies the factory's routing label, `factory:<alias>`, to the
issue and the PR as it works; that label is not in either filter and would
be skipped as a bot event anyway. Only a label a person adds starts a run.

The automation bodies say "do not assume a previous run exists", and the
foreman reads the issue's labels, comments, and linked spec PR to find the
stage. New activity on an issue the factory already handles continues the
same work item, but the prompts do not depend on that: a `spec-approved`
run that starts fresh still finds the spec PR from the issue.

### The approval gate

As in the default agents, when a spec exists the foreman does not start
implementation until a human approves the spec, and it never approves a
spec on a human's behalf. The default agents accept a written confirmation
or an approval of the draft PR; this example narrows approval to one
signal so a first run has exactly one thing to check:

- **Approve:** add the `spec-approved` label to the issue. Nothing else
  counts, not a comment that says "approved", not an approving review on
  the spec PR, not the foreman's own confidence.
- **Change the spec first:** edit `docs/specs/<issue>-<slug>.md` on the spec
  PR's branch (the GitHub web editor is enough), commit, then add the
  label. The implementer reads the committed file at approval time, so your
  edits are the contract.
- **Answer a question:** if the foreman posts a question during
  implementation, put the answer in the spec file, then remove and re-add
  `spec-approved`. Re-adding the label fires the automation again, and the
  implementer continues on the same branch.
- **Start over:** close the spec PR and remove `spec-approved` from the issue
  if present. Fix the issue text, then remove and re-add `factory-ready`.
  Review the replacement spec before adding `spec-approved` again. The old
  approval does not carry over: adding an already-present label emits no
  new `issue_labeled` event. A human resets and approves; the factory never
  changes `spec-approved` itself.

There is no trigger for free-text replies in this example. To let a
maintainer steer the factory with `@warp` comments instead, add the
`issue_mentioned` automation from
[`02-sdlc-issue-to-pr`](../02-sdlc-issue-to-pr).

### Unmatched events

- A label other than the two, or either label on another repository:
  nothing runs.
- `factory-ready` on an issue that is out of scope (a question, a bug with
  no reproduction, work outside `acme/webapp`, or more than one PR's
  worth): the foreman comments why and stops. No branch, no spec, no label.
- `factory-ready` on an issue that already links an open spec PR: the
  foreman comments with the existing PR and stops.
- `factory-ready` with no open spec PR but `spec-approved` still present:
  the foreman asks a human to remove `spec-approved`, then remove and
  re-add `factory-ready`, and stops without creating a replacement spec.
- `spec-approved` on an issue with no open spec PR: the foreman comments
  that there is nothing to approve and stops.
- A label added by a bot or by another automation: skipped by the default
  bot policy.

## Make it yours

1. Replace `acme/webapp` in `factory.yaml`,
   `automations/factory-ready/automation.md`,
   `automations/spec-approved/automation.md`, and the scope check in
   `agents/foreman/agent.md` with a repository your Warp team's GitHub
   installation can reach. Connect GitHub to your Warp team first; see
   [Connect GitHub to your factory](https://docs.warp.dev/factories/integrations/github/).
2. Create the two labels, `factory-ready` and `spec-approved`, in that
   repository. Warp creates `factory:<alias>` for you when the factory is
   registered, but not these two. Rename them in both automations and in
   `agents/foreman/agent.md` if your team uses other names.
3. Set `alias` in `factory.yaml`. It becomes the routing label,
   `factory:<alias>`, and the foreman's handle.
4. Swap the runner's `dockerImage` in `runners/linux-node.yaml` for an image
   that has your toolchain, and make sure the repository documents its lint,
   typecheck, and test commands (a README or `package.json` scripts are
   enough); the implementer and reviewer run "the repository's documented
   checks". If they are not documented, name them in step 4 of
   `agents/implementer/agent.md` and step 2 of `agents/reviewer/agent.md`.
5. Change where specs live if `docs/specs/` is wrong for your repository:
   the path and the branch pattern are in `agents/spec/agent.md`.
6. Register it: create a factory in Warp with a GitHub-backed definition
   pointing at your copy of this directory. The registered root is the
   directory containing `factory.yaml`.

## Sample task and expected output

The trace assumes `acme/webapp` is a TypeScript React app: `npm ci`
installs it, and `npm run lint`, `npm run typecheck`, and `npm test`
(Vitest and Testing Library) are its documented checks.
`src/components/ShareDialog.tsx` renders a share URL in a read-only input
and has tests in `src/components/ShareDialog.test.tsx`;
`src/components/ui/Button.tsx` is the shared button; and
`src/components/InviteDialog.tsx` already places an action button next to an
input, which is the pattern to copy. If your repository differs, your
artifacts differ in detail; they should still match in shape.

### 1. The issue

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

### 2. What `factory-ready` produces

The foreman's scope check passes (one repository, one PR, user-visible). The
spec agent reads `ShareDialog.tsx`, its tests, and `InviteDialog.tsx`, then
opens draft PR #131, `Spec: Add a "Copy link" button to the share dialog
(#128)`, on branch `factory/128-copy-link-button`, with a single commit that
adds one file, `docs/specs/128-copy-link-button.md`. The foreman comments on
the issue:

> Spec ready for review: acme/webapp#131. Review the spec. Edit the file on
> the PR branch if it needs changes. When it is right, add the
> `spec-approved` label to this issue.

Nothing else happens. No code, no second branch, no `spec-approved` label.

### 3. The expected spec

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

A much longer spec may need a shorter template (see "Tune it"). Check that
unresolved choices appear under Assumptions for human approval and that
each acceptance criterion names a test, command, or manual check. Omit
Assumptions when there are none.

### 4. The approval

A maintainer reads the spec on PR #131. Say they want a shorter
confirmation: they edit `docs/specs/128-copy-link-button.md` on the branch,
changing "2 seconds" to "1.5 seconds" in behaviors 3 and 4, criterion 2,
and the duration assumption, then commit. They add `spec-approved` to issue
#128. Implementation and review must now use the approved 1.5-second
duration, not the original draft's 2 seconds.

### 5. What `spec-approved` produces

The foreman finds PR #131 from the issue and dispatches the implementer,
which works on `factory/128-copy-link-button`. The PR as first delivered:

- Title changed to `Add a "Copy link" button to the share dialog (#128)`;
  marked ready for review.
- Commits: the draft spec, the human's spec revision, then implementation.
- Files: `docs/specs/128-copy-link-button.md` (approved version retained),
  `src/components/ShareDialog.tsx` (about 40 lines added, 3 changed),
  `src/components/ShareDialog.test.tsx` (4 new test cases). No change to
  `package.json` or the lockfile.
- Description:

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

The foreman then dispatches the reviewer on PR #131. The findings report
the reviewer returns, in full:

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
updates the Verification section (27 passed; an assertion was added, not a
test case). The foreman posts finding 3 on PR #131 as a comment-only review,
neither approving nor requesting changes; confirms `factory:Webapp` is on
the issue and the PR; and comments on the issue:

> PR ready for review: acme/webapp#131. Verified with `npm run lint`,
> `npm run typecheck`, and `npm test` (27 passed, 4 new). Review found two
> issues, both fixed on the branch: an uncleared reset timer, and a
> rejection test that did not check the text selection. One question is
> open on the PR for you: what the button should do when the clipboard API
> is absent. A human merges.

The run stops there. The PR is not merged, the issue is not closed, and
`spec-approved` was added exactly once, by a person.

### 6. Out of scope

A maintainer labels issue #129, "Why does the share URL sometimes have a
trailing slash?", with `factory-ready`. The foreman comments:

> This factory implements small, user-visible changes to acme/webapp that
> one PR can deliver. This issue is a question about current behavior, not a
> change to make. Describe the change you want, then add `factory-ready`
> again.

No branch, no spec PR, no label. The same comment shape applies to a bug
with no reproduction and to work that spans another repository.

### Tune it

Change one setting at a time. Record the requirements, starting commit,
configuration, output, and per-stage cost of the baseline trial. For each
comparison, use a separate test issue and a new branch and PR starting at
that commit, with no implementation commits from earlier trials. Review
the new spec and approve it separately. Do not merge trial output.

Closing a PR or reapplying a label continues or restarts existing work; it
does not create an independent comparison. Check the new branch's baseline
and diff. Repeat unchanged settings before attributing a difference to tuning.

1. **Spec detail level:** `agents/spec/skills/spec-format/SKILL.md`. Specs
   too thin: require unresolved behavior to be surfaced for approval and
   acceptance criteria with executable checks. Specs too heavy for
   one-file changes: trim the template, or loosen the "Scale to the change"
   rule so Implementation notes become optional.
2. **Implementer model:** the `model:` line in
   `agents/implementer/agent.md`, currently `auto-genius`. Compare `auto`,
   `auto-efficient`, or another supported Warp Agent model on simple changes.
   Change this agent's model, not `agentDefaults.model`, which affects every
   agent inheriting it. Compare candidates on the same task with
   [benchmarks](https://docs.warp.dev/factories/benchmarks/) before
   adopting one.
3. **Reviewer strictness:** the "Strictness" section of
   `agents/reviewer/agent.md`. Too many revision rounds: narrow what
   blocks without removing correctness checks. Too few findings: add the
   failure modes your reviews keep catching by hand. You can compare a
   reviewer-specific `model:` in repeated fixed-baseline trials; a
   different model alone does not establish review quality.

Each stage is a separate run on the factory's
[Runs page](https://docs.warp.dev/factories/factory-dashboard/#inspect-runs);
its duration and cost per agent are what you compare after a change.

## Validate it

```bash
python3 scripts/validate_factory_files.py examples/26-product-change-implementation
python3 scripts/check_conventions.py
```

The validator checks the tree's syntax and the trigger and filter keys
against Warp's parser. It cannot check that the labels exist or that the
GitHub installation reaches the repository; the first real run does that.
Run it on a throwaway issue like the one above and confirm, in order:

1. Adding `factory-ready` produced exactly one draft PR, on a
   `factory/<issue>-<slug>` branch, whose only change is
   `docs/specs/<issue>-<slug>.md`, plus one issue comment with the approval
   instruction. Nothing else changed in the repository.
2. Nothing further happened until you added `spec-approved`; the Runs page
   shows no run in between.
3. Adding `spec-approved` produced commits on the same branch, the PR
   retitled and marked ready for review with the description shape above,
   tests in the diff, at most one comment-only review on the PR, and one
   issue comment with the PR link and the verification evidence.
4. The factory never merged, never approved the PR, and never added
   `spec-approved`: the issue's timeline shows a person as the only actor
   on that label.
5. Test a restart after approval: close the old spec PR, remove
   `spec-approved`, update the issue, then remove and re-add `factory-ready`.
   The replacement spec arrives in a draft PR and waits without
   implementation. Review it, then add `spec-approved` again; only that
   fresh human approval starts implementation on the replacement PR's
   branch. Confirm the issue timeline shows a person removing and re-adding
   the approval label.

## Set it up with a prompt

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
