# 11: Jira to pull request

Assign or mention Warp on a Jira Cloud work item to request a code change.
Progress appears in the agent session, and the result is linked on the work
item. A human reviews and merges. This example replaces the intake in
[`01-single-repo-quickstart`](../01-single-repo-quickstart) with Jira
delegation.

## What this example shows

- The `jira` / `agent_session_created` trigger accepts assignments and
  mentions. This example uses no label or status trigger.
- The `integrations` list uses `type: jira` in `factory.yaml`. A factory
  attaches Linear or Jira, not both.
- The `project_keys` filter controls scope. A Jira session is offered to every
  automation in the workspace rather than addressed to one factory, so the
  project filter is what keeps this factory to its own project.
- The prompts link the result back. The agent posts nothing on the work item
  unless asked, so the prompts ask for a comment with the pull request link,
  and the implementation agent puts the work item key in the branch name and
  the pull request title.
- A reply in the agent session continues the same run, which is how the
  foreman's clarifying questions get answered.

## Directory structure

```
factory.yaml                integrations: jira; one repository
agents/
  foreman/agent.md          FOREMAN, accepts sessions, reports back to Jira
  implementer/agent.md      IMPLEMENT, turns a work item into a PR
automations/
  jira-agent-sessions/automation.md   jira/agent_session_created, project_keys: [YOURKEY]
runners/
  linux-small.yaml          2 vCPU / 4 GB, node:22-bookworm-slim
```

## How Jira intake is routed

Assigning or mentioning Warp on a work item, with an instruction, starts a
Jira agent session. The Warp agent has to be available on the site (Jira
lists it among Atlassian's Rovo agents) before anyone can assign or mention
it. Adding the `warp-agent` label starts a standalone cloud agent run, not
a factory run.

The automation declares no `agent:` field, so sessions go to the foreman.
Its filter uses one key.

- The `project_keys: [YOURKEY]` filter allows only sessions on work items in
  that project to start a run through this automation. Sessions in other
  projects do not match. Other automations or factories may still handle them.

Within the project, every session matches. To require an opt-in instead,
add a `labels` filter. It checks the work item's current labels when the
session starts, so the label has to be on the work item before the
assignment or mention, and Jira label names are case-sensitive:

```yaml
filter:
  project_keys: [YOURKEY]
  labels: [factory-ready]
```

Filters decide what this automation picks up, not who else sees the event.
A second factory in the same workspace with an overlapping project filter
starts its own run on the same work item, so keep project sets disjoint
across factories.

Jira shows the session's status as the run progresses. The statuses are
submitted, working, waiting for input, completed, failed, or cancelled.
The result appears in the session. The comment on the work item is there
because the foreman's prompt asks for it. Writes to Jira are made by the
Warp app on behalf of the person who started the session, after checking
that person's Jira permissions. That person's Atlassian account must be linked
to Warp (see [Customize the example](#customize-the-example)).

## Runner configuration

Both agents use `linux-small`, with 2 vCPUs, 4 GB of memory, and the
`node:22-bookworm-slim` image. The image provides Node and npm.

## Customize the example

Copy the entire example directory into your repository before making these
changes. See [Use an example](../../README.md#use-an-example) for the shared
setup procedure.

1. Replace `acme/api-service` in `factory.yaml` with a repository your Warp
   team's GitHub installation can reach. It appears in no other file.
2. Replace `YOURKEY` in `automations/jira-agent-sessions/automation.md`
   with your Jira project key, the prefix of the project's issue keys (the
   `ENG` in `ENG-123`).
3. Install Warp for Jira. This is Jira Cloud only.
   Jira Server and Data Center are not supported. A Jira site admin installs
   the Warp app. If you are not a site admin, the setup flow lets
   you send the request to one. The approval link lasts seven days. Once
   approved, continue with the connection step below. The
   [Jira integration page](https://docs.warp.dev/factories/integrations/jira/)
   has the exact steps.
4. Connect the Jira site to your Warp workspace from the app's **Configure**
   page in Jira. A Jira site admin completes this step. Once connected, the
   site is available to every factory in the workspace.
5. Attach Jira to this factory. The `integrations` entry in `factory.yaml`
   attaches Jira when the definition is applied. It does not install the
   app or connect the site. Applying the definition checks that the
   workspace connection exists. This GitHub-backed definition is edited in
   files, not through dashboard project selection. Set the project scope in
   `automations/jira-agent-sessions/automation.md` with `project_keys`.
6. Inspect existing Jira session automations. Reuse or narrow an existing
   automation instead of adding another handler for the same sessions.
7. Link accounts. Each teammate who will assign or mention Warp links their
   Atlassian account to Warp from their Jira personal settings (**Personal
   settings** > **Warp**). An unlinked account gets a prompt to connect
   instead of a run.
8. Optionally narrow intake with `labels` as shown above.
9. Replace `dockerImage` in `runners/linux-small.yaml` with an image for your
   stack.
10. Optionally, change `agentDefaults.model` to another Warp Agent model ID.

If you want the foreman to move the work item, for example to "In Review"
once the pull request is open, say so in the automation body. Jira
permissions and the project's valid transitions apply to everything the
agent does.

The `alias` is the factory's handle on chat platforms and Linear. In Jira
you always address Warp, so here it only names the factory.

## Validate the example

From the repository root:

```bash
python3 scripts/validate_factory_files.py examples/11-jira-to-pr
python3 scripts/check_conventions.py
```

The validator checks the definition files against the server's parser. It
defers integration availability until the definition is applied. A pass does
not prove that the Jira connection, the project, or the account links exist.
Schema validation alone does not prove prompt behavior.

## Register the factory

Follow [Use an example](../../README.md#use-an-example) to copy this directory
into your definition repository, customize it, commit and push the files,
and create a factory with a GitHub-backed definition pointing at your copy.
Pushes sync the definition after the `warp/factory-config` check passes.

## Test the factory

### Assign a sample work item

Create a work item in the project, say `YOURKEY-123`, with the summary
"Return 404 for unknown customer IDs" and a description that states the
acceptance criteria: `GET /customers/{id}` returns 404 with
`{"error": "customer_not_found"}` instead of 500 when the ID does not exist,
covered by a regression test. Assign it to Warp with the instruction:

```text
Implement this against the acceptance criteria and open a pull request.
```

What you should see:

- Jira shows the session moving from submitted to working. In the factory
  dashboard, the run appears under the `jira-agent-sessions` automation.
- The factory pushes a branch named after the key, such as
  `yourkey-123-unknown-customer-404`, to `acme/api-service` and opens a pull
  request titled
  `YOURKEY-123: Return 404 for unknown customer IDs` whose description links
  the work item and includes the test and lint output.
- The foreman posts a comment on `YOURKEY-123` with the pull request link
  and one line on what changed and how it was verified. The same result
  appears in the session, which Jira now shows as completed.
- Nothing is merged, and the work item's status and assignee are unchanged.

When the task is out of scope, the foreman opens no pull request. If the
description has no acceptance criteria, or the change belongs in a repository
this factory is not attached to, it asks one question in the session and the
session shows as waiting for input. Reply in the session to continue the same
run. If the instruction only asks a question, the foreman answers it in the
session and stops.

### Check the first-run results

1. Confirm that a session in the configured project starts a run under this
   automation. A pull request with the key in its title should appear in the
   attached repository, and the comment should appear on the work item.
2. Assign Warp on a work item in a project outside the filter and confirm
   that this automation starts nothing.
3. Reply to a clarification in the session and confirm that it continues
   the same run.
4. Check that no other automation or factory matches the trial.

## Set up with an agent

Use one of these options to give an agent the setup prompt below.

<!-- terminology-allow-begin -->
- Ask your factory's foreman in the factory dashboard.
- Use the factory web composer.
- Use Factory MCP from a coding agent
  [connected to it](https://docs.warp.dev/factories/factory-mcp/).
<!-- terminology-allow-end -->

```text title="Set up Jira delegation for my repository"
Read https://github.com/warpdotdev/warp-factory-examples/tree/main/examples/11-jira-to-pr
and set up the same factory for me. Ask which repository it should work on,
which Jira Cloud project key it should serve, and where the definition
files should live.

Replace acme/api-service in factory.yaml with my repository, YOURKEY in
automations/jira-agent-sessions/automation.md with my project key, and the
runner image with one that has my toolchain. Declare Jira in factory.yaml;
configure project_keys in the automation, not dashboard project selection.
Reuse or narrow an existing Jira session handler and preserve unrelated
triggers. Validate the tree, then open a pull request with the definition.

List the manual steps: install Warp for Jira on my Jira Cloud site, connect
it to my workspace, and link each requester's Atlassian account to Warp.
Give me matching-project, unmatched-project, and session-reply trials, and
check for overlapping handlers. Do not register the factory or change
anything in Jira without asking me first.
```
