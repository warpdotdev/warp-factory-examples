# Warp Factories examples

[Warp Factories](https://docs.warp.dev/factories/) provides open, flexible
infrastructure for building your own software factory. This repository
contains workflows defined as code that you can adapt for your projects,
from a single review automation to an issue-to-PR workflow.

Choose an example, customize its definition, and test it on work from your
repository. Use the results to identify what to change in your configuration. For guidance on evaluating results and comparing configurations, see [Measure and improve](https://docs.warp.dev/factories/measure-and-improve/).

Each directory under `examples/` contains a complete factory definition.
Copy the entire example directory into your repository and follow the
[setup instructions below](#use-an-example).

These examples use Warp Factories configuration schema version `v1alpha1`.

The multi-stage workflow examples define explicit
[Blueprints](https://docs.warp.dev/factories/blueprints/) in `factory.yaml`.
Each Blueprint defines stages, the order in which work moves between them,
and gates that wait for a person's answer. A worker is the agent assigned to
execute a stage. The files under `agents/` configure its role, model or
harness, runner, and skills. The other examples focus on individual tasks;
the default-agent and GitHub-skill examples preserve historical snapshots.

For smaller Blueprint patterns, start with
[two stages in order](examples/blueprint-linear),
[conditional entry and revision](examples/blueprint-revision-loop), or
[a human decision gate](examples/blueprint-human-gate).
Their procedures stay in `factory.yaml`, with one small foreman file and no
automation, skill, runner, or project setup.

Try [planning and revising one PR](examples/sdlc-issue-to-pr#exercise-plan-and-revise-one-pr)
or [editing a committed spec before approval](examples/product-change-implementation#exercise-edit-a-committed-spec)
in a disposable fork. These draft exercises still need verification of public
availability, team access, successful definition application, and the live
approval and revision steps. Do not treat them as runnable until those checks
are complete. Parser validation does not verify application or execution.

## The examples

- [`examples/warp-default-agents`](examples/warp-default-agents):
  Explore the five default agents Warp creates for every new factory,
  including their prompts, descriptions, and models. Copy this example to
  edit and version their configurations.
- [`examples/single-repo-quickstart`](examples/single-repo-quickstart):
  Start with this example to set up a factory for a single repository. A
  foreman routes labeled GitHub issues to an implementation agent, which
  opens a pull request with the changes.
- [`examples/sdlc-issue-to-pr`](examples/sdlc-issue-to-pr):
  Take requests from Slack, Linear, and GitHub through triage,
  specification, implementation, and review to produce pull requests for
  human review. This example extends the default agents with a custom agent
  and shows how to configure models, compute resources, skills, and automated
  scoring.
- [`examples/multi-harness`](examples/multi-harness):
  Coordinate work with the Warp Agent harness, implement changes with
  Claude Code, and review them with Codex. This example also shows how to
  authenticate third-party harnesses with managed secrets.
- [`examples/code-review-only`](examples/code-review-only):
  Review newly opened pull requests and post findings for a human to
  consider. A single agent serves as both the foreman and reviewer.
- [`examples/ui-verification`](examples/ui-verification):
  Check UI changes and reproduce reported bugs by having an agent run your
  app in a browser. Labels on pull requests and issues trigger the checks,
  and the agent posts links to screenshots and recordings.
- [`examples/common-automations`](examples/common-automations):
  Automate routine maintenance with one agent that triages CI failures,
  audits dependencies weekly, checks documentation when code is pushed, and
  responds to Slack reactions.
- [`examples/self-hosted-worker`](examples/self-hosted-worker):
  Run the quickstart factory on your own infrastructure. This example shows
  how to select a self-hosted worker with `workerHost` and configure a runner
  that matches the worker's platform.
- [`examples/slack-to-pr`](examples/slack-to-pr):
  Request code changes by mentioning the factory in a designated Slack
  channel. The foreman confirms the request and returns progress, questions,
  and the pull request link in the same thread.
- [`examples/github-skill`](examples/github-skill):
  Version a shared GitHub skill and review its updates separately from the
  factory configuration. The starting point is an exact historical default
  skill from before managed GitHub MCP support.
- [`examples/linear-to-pr`](examples/linear-to-pr):
  Delegate Linear issues from one team to a factory. The agents report
  progress in the agent session and attach the pull request to the issue
  for human review.
- [`examples/jira-to-pr`](examples/jira-to-pr):
  Assign or mention Warp on a Jira Cloud work item to request a code change.
  The factory limits intake by project and returns the pull request link
  in the agent session and a work-item comment.
- [`examples/github-assigned-issue`](examples/github-assigned-issue):
  Start work by assigning a labeled GitHub issue to the factory. The foreman
  checks the request's scope and returns a linked pull request for human
  review. This example also explains when to use assignment instead of labels.
- [`examples/blueprint-linear`](examples/blueprint-linear):
  Extract incident facts, then format a handoff in two ordered stages.
- [`examples/blueprint-revision-loop`](examples/blueprint-revision-loop):
  Check or draft a release note, then return corrections to the draft stage.
- [`examples/blueprint-human-gate`](examples/blueprint-human-gate):
  Wait for a person to choose an incident update's audience before writing it.
- [`examples/monorepo-product`](examples/monorepo-product):
  Scope a factory to one product in a monorepo and verify changes across
  affected packages. Changes to shared packages require a draft pull request
  and review from their owners.
- [`examples/related-services`](examples/related-services):
  Coordinate changes across an API and its consumer. The factory checks
  contract compatibility and opens one pull request per changed repository,
  with a provider-first merge order when both repositories change.
- [`examples/product-change-implementation`](examples/product-change-implementation):
  Specify, approve, implement, and review a small product change on one pull
  request. Edit a committed spec before approval in a disposable-fork exercise,
  or follow an illustrative React example.

## Use an example

1. Copy the entire example directory into your own GitHub repository. You
   can place it at the repository root or in a subdirectory.
2. Complete the "Customize the example" checklist in the example's README. It
   explains which placeholders to replace and any additional setup required.
3. Commit and push the example files to GitHub.
4. Create a factory in Warp using a
   [GitHub-backed definition](https://docs.warp.dev/factories/factory-as-code/#where-the-definition-lives).
   Specify your repository, branch, and the directory containing `factory.yaml`.

After setup, Warp syncs changes pushed to the configured branch once the
`warp/factory-config` check passes.

## Validate an example

Check an example with Warp's parser:

```bash
python3 scripts/validate_factory_files.py examples/single-repo-quickstart
```

The helper requires Python 3 and network access to Warp's validation service.
Exit 0 means the parser checked the tree without diagnostics; state-dependent
apply checks did not run. Exit 1 reports diagnostics to fix before retrying.
Exit 2 means validation did not run; restore Python, network, or service access
and retry. Neither exit 1 nor exit 2 is a pass.

Existing work keeps its selected Blueprint. After applying a definition
change, start a separate task to test the new workflow. Reapplying an intake
label or closing a PR does not create an independent comparison trial.

## Layout rules

- A resource's name is its path: `agents/<name>/agent.md`,
  `automations/<name>/automation.md`, `runners/<name>.yaml`,
  `scorers/<name>/scorer.md`. Renaming a resource means moving the file.
- Exactly one agent per factory declares `agentType: FOREMAN` (alias `MAIN`).
- `model` (shorthand for the Warp Agent harness) and `harness` are mutually
  exclusive everywhere; `agentDefaults` must declare exactly one of them.
- Declaring `secrets` or `mcpServers` on an agent or automation replaces the
  inherited list; it does not merge.
- Skills under `skills/` are available to every agent in the factory. Skills
  under `agents/<name>/skills/` are available only to that agent.

## License

[MIT](LICENSE)
