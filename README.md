# Warp Factories examples

[Warp Factories](https://docs.warp.dev/factories/) provide open, flexible
infrastructure for building your own software factory. This repository
contains workflows defined as code that you can adapt for your projects,
from a single review automation to an issue-to-PR workflow.

Choose an example, customize its definition, and test it on work from your
repository. Use the results to identify what to change in your configuration. For guidance on evaluating results and comparing configurations, see [Measure and improve](https://docs.warp.dev/factories/measure-and-improve/).

Each directory under `examples/` contains all the files needed to define a
factory. To get started, copy the entire example directory into your
repository and follow the [setup instructions below](#use-an-example).

These examples use Warp Factories configuration schema version `v1alpha1`.

## The examples

- [`examples/00-warp-default-agents`](examples/00-warp-default-agents):
  Explore the five default agents Warp creates for every new factory,
  including their prompts, descriptions, and models. Copy this example to
  edit and version their configurations.
- [`examples/01-single-repo-quickstart`](examples/01-single-repo-quickstart):
  Start with this example to set up a factory for a single repository. A
  foreman routes labeled GitHub issues to an implementation agent, which
  opens a pull request with the changes.
- [`examples/02-sdlc-issue-to-pr`](examples/02-sdlc-issue-to-pr):
  Take requests from Slack, Linear, and GitHub through triage,
  specification, implementation, and review to produce pull requests for
  human review. This example extends the default agents with a custom agent
  and shows how to configure models, compute resources, skills, and automated
  scoring.
- [`examples/03-multi-harness`](examples/03-multi-harness):
  Coordinate work with the Warp Agent harness, implement changes with
  Claude Code, and review them with Codex. This example also shows how to
  authenticate third-party harnesses with managed secrets.
- [`examples/04-code-review-only`](examples/04-code-review-only):
  Review newly opened pull requests and post findings for a human to
  consider. A single agent serves as both the foreman and reviewer.
- [`examples/05-ui-verification`](examples/05-ui-verification):
  Check UI changes and reproduce reported bugs by having an agent run your
  app in a browser. Labels on pull requests and issues trigger the checks,
  and the agent posts links to screenshots and recordings.
- [`examples/06-common-automations`](examples/06-common-automations):
  Automate routine maintenance with one agent that triages CI failures,
  audits dependencies weekly, checks documentation when code is pushed, and
  responds to Slack reactions.
- [`examples/07-self-hosted-worker`](examples/07-self-hosted-worker):
  Run the quickstart factory on your own infrastructure. This example shows
  how to select a self-hosted worker with `workerHost` and configure a runner
  that matches the worker's platform.
- [`examples/08-slack-to-pr`](examples/08-slack-to-pr):
  Request code changes by mentioning the factory in a designated Slack
  channel. The foreman confirms the request and returns progress, questions,
  and the pull request link in the same thread.
- [`examples/10-linear-to-pr`](examples/10-linear-to-pr):
  Delegate Linear issues from one team to a factory. The agents report
  progress in the agent session and attach the pull request to the issue
  for human review.
- [`examples/11-jira-to-pr`](examples/11-jira-to-pr):
  Assign or mention Warp on a Jira Cloud work item to request a code change.
  The factory limits intake by project and returns the pull request link
  in the agent session and a work-item comment.
- [`examples/12-github-assigned-issue`](examples/12-github-assigned-issue):
  Start work by assigning a labeled GitHub issue to the factory. The foreman
  checks the request's scope and returns a linked pull request for human
  review. This example also explains when to use assignment instead of labels.
- [`examples/24-monorepo-product`](examples/24-monorepo-product):
  Scope a factory to one product in a monorepo and verify changes across
  affected packages. Changes to shared packages require a draft pull request
  and review from their owners.
- [`examples/25-related-services`](examples/25-related-services):
  Coordinate changes across an API and its consumer. The factory checks
  contract compatibility and opens one pull request per changed repository,
  with a provider-first merge order when both repositories change.
- [`examples/26-product-change-implementation`](examples/26-product-change-implementation):
  Take a small product change through specification, human approval,
  implementation, and review on the same pull request. An illustrative
  walkthrough shows the expected outputs and how to compare configuration
  changes in separate trials.

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

Check that an example is a valid factory definition:

```bash
python3 scripts/validate_factory_files.py examples/01-single-repo-quickstart
```

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
