---
name: spec-format
description: The spec template for this factory and how much detail a spec carries. Use when writing or revising a spec.
---

# Spec format

Only the spec agent can read this skill; it lives under
`agents/spec/skills/`. This file sets the factory's spec detail level. To
make specs longer or shorter, edit the rules and the template here; the spec
agent's prompt stays the same.

## Rules

- Short sentences, active voice, one instruction per sentence. No vague
  qualifiers ("as needed", "appropriately", "etc.").
- Lists over prose.
- Every acceptance criterion says how it is checked: a test file and case, a
  command, or a manual step.
- Name the exact files to change and the existing pattern to follow. A
  snippet illustrates a decision; it does not replace the work.
- Scale to the change. A small change needs Summary, Behavior,
  Implementation notes, Acceptance criteria, Assumptions, and Out of scope.
  Add a Decisions section only when there was a real fork with more than one
  defensible option.

## Template

```markdown
# <Title> (#<issue-number>)

## Summary
What changes for the user, and why. One short paragraph.

## Behavior
Numbered, testable statements about what the user sees and does.

## Implementation notes
The files to change, the existing pattern to follow, and anything the
implementer must not do.

## Acceptance criteria
Numbered checks. Each one says how it is verified.

## Assumptions
Choices made without an answer from the requester, each marked as an
assumption. Omit the section when there are none.

## Out of scope
What this change deliberately does not do.
```
