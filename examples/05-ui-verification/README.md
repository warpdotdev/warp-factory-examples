# 05: UI verification

A single-agent factory that checks UI behavior visually. Label a pull
request `needs-ui-check` and the agent runs the app, exercises the change
in a browser, and posts evidence. Label an issue `needs-repro` and it
tries to reproduce the reported bug the same way.

## What it demonstrates

- Computer use is on by default for cloud agent runs, whatever the
  harness, with a bundled Chromium browser and the Playwright CLI in
  every sandbox; no factory-file field turns it on. Only the
  computer-use model pick is specific to the Warp Agent harness (what
  `model: auto` selects).
- A single-agent factory triggered by labels, with one automation per mode:
  verify a PR, reproduce an issue.
- Evidence as the deliverable: the screenshots and recordings the agent
  captures are saved on its run, and the agent links them from the comment
  it posts.

## Tree

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

## Make it yours

1. Replace `acme/webapp` in `factory.yaml` and both automations.
2. Swap the runner's `dockerImage` for whatever runs your app; the sandbox
   provides the browser regardless of image.
3. Rename the labels to whatever your team uses, and make sure the app's
   run commands are documented in the repository so the agent can find
   them.
