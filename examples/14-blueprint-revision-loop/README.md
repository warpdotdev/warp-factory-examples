# Conditional entry and a revision loop

Check an existing release note or draft a new one, then return corrections
to `draft` until the note meets the request.

[`factory.yaml`](factory.yaml) contains the entry conditions, procedures, and
return transition. [`agents/foreman/agent.md`](agents/foreman/agent.md) is the
small foreman declaration required by this complete factory root. One worker
runs both stages in one conversation, so `check` is not independent review.
There are no automations, skills, runners, or attached repositories.

## Customize the example

- Confirm Blueprint availability and access for your team before attempting
  to run this draft example. Application and execution remain unverified.
- Copy this directory into a definition repository you control. Follow the
  [repository setup instructions](../../README.md#use-an-example), including
  validation and application, before testing.
- Keep `repositories: []`. Supply the release facts in the request. The
  procedures need no integration, secret, repository checkout, or toolchain.

## Try the paths

After applying the definition, send each request as a separate new task to
the foreman:

| Request | Expected path and result |
| --- | --- |
| `Draft a release note. Fact: CSV exports now retain the selected date filter. Do not access external data or publish.` | `draft → check → end`; a note of at most 40 words using that fact |
| `Draft a release note from this existing draft: "CSV exports retain the selected date filter and run twice as fast." The only verified fact is that CSV exports retain the selected date filter. Do not access external data or publish.` | Both entry conditions fit; the first selects `check`. It identifies the unsupported speed claim, then `draft → check → end` removes it |
| `Please handle this.` | Neither entry condition fits; the foreman asks what release note is needed instead of silently finishing |

The worker evaluates conditions in order; they are prose, not code
expressions. Inspect the stage history and final text, not only the task's
completion status. The correction must update the note in the same
conversation, not create a PR or publish a release.

If a needed fact is unavailable, neither outgoing condition from `check`
fits. Answer the foreman's question in the same task. If a correction loops,
check whether the facts support it and whether `check` reports the remaining
finding. Parser acceptance does not prove any of these paths executed.
