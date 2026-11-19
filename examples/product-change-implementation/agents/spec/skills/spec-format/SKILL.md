---
name: spec-format
description: Defines the specification template and detail level for this factory. Use when writing or revising a specification.
---

# Spec format

Only the spec agent can read this skill because it lives under
`agents/spec/skills/`. This file sets the factory's spec detail level. To
make specifications longer or shorter, edit the rules and template here.
The spec agent's prompt stays the same.

## Rules

- Write short sentences in active voice, with one instruction per sentence.
  Avoid vague qualifiers such as "as needed", "appropriately", and "etc.".
- Prefer lists over prose.
- Every acceptance criterion says how it is checked: a test file and case, a
  command, or a manual step.
- Name the exact files to change and the existing pattern to follow. A
  snippet illustrates a decision; it does not replace the work.
- Scale to the change. A small change needs Summary, Behavior,
  Implementation notes, Acceptance criteria, and Out of scope. Include
  Assumptions when choices need human approval. Add a Decisions section only
  when there was a choice between multiple defensible options.

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
