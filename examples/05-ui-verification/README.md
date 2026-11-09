# 05: UI verification

This example is a single-agent factory that checks UI behavior in a browser.
When you label a pull request `needs-ui-check`, the agent runs the app,
exercises the change, and posts evidence. When you label an issue
`needs-repro`, the agent tries to reproduce the reported bug the same way.

## What this example shows

- Computer use is a capability of the Warp Agent harness, which
  `model: auto` selects in this example. Cloud runs on that harness include
  a Chromium browser and the Playwright CLI in every sandbox. No
  factory-file field is required to enable computer use.
- Third-party harnesses don't integrate with Warp's computer-use tools.
  The `computerUseModel` setting has no effect under them. A foreman on
  another harness can still delegate to a verifier on the Warp Agent harness.
- Labels trigger the factory, with one automation for each mode: verifying a
  pull request and reproducing an issue.
- The deliverable is evidence. The agent saves the screenshots and recordings
  it captures on its run, and it links them from the comment it posts.

## Directory structure

```
factory.yaml
agents/
  verifier/agent.md       FOREMAN, runs the app and verifies visually
automations/
  pr-needs-ui-check/automation.md   github/pull_request_labeled, needs-ui-check
  issue-needs-repro/automation.md   github/issue_labeled, needs-repro
runners/
  linux-app.yaml          4 vCPU / 8 GB, node:22-bookworm-slim
```

## Customize the example

1. Replace `acme/webapp` in `factory.yaml` and both automations.
2. Replace the runner's `dockerImage` with an image that can run your app. The
   sandbox provides the browser regardless of the image.
3. Replace the `needs-ui-check` label in `pr-needs-ui-check` and the
   `needs-repro` label in `issue-needs-repro` with the labels your team uses.
4. Document the app's run commands in the repository so the agent can find
   them.
