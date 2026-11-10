# 11: Jira to PR

Assign or mention Warp on a Jira Cloud work item to request a pull request.
Progress appears in the agent session, and the result is linked on the work
item. A human reviews and merges. This example replaces the intake in
[`01-single-repo-quickstart`](../01-single-repo-quickstart) with Jira delegation.

## What it demonstrates

- `jira` / `agent_session_created` for assignments and mentions. This
  example uses no label or status trigger.
- `integrations` with `type: jira` in `factory.yaml`. A factory attaches
  Linear or Jira, not both.
- `project_keys` as the scope control. A Jira session is offered to every
  automation in the workspace rather than addressed to one factory, so the
  project filter is what keeps this factory to its own project.
- Linking the result back. The agent posts nothing on the work item unless
  asked, so the prompts ask for a comment with the pull request link, and
  the implementation agent puts the work item key in the branch name and
  the PR title.
- Session continuation: a reply in the agent session continues the same
  run, which is how the foreman's clarifying questions get answered.

## Tree

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
it. Adding the `warp-agent` label is a different path: it starts a
standalone cloud agent run, not a factory run.

The automation declares no `agent:` field, so sessions go to the foreman.
Its filter is one key:

- `project_keys: [YOURKEY]`: only sessions on work items in that project
  start a run through this automation. Sessions in other projects do not
  match; other automations or factories may still handle them.

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

Jira shows the session's status as the run progresses: submitted, working,
waiting for input, completed, failed, or cancelled. The result appears in
the session; the comment on the work item is there because the foreman's
prompt asks for it. Writes to Jira are made by the Warp app on behalf of the
person who started the session, after checking that person's Jira
permissions, which is why that person's Atlassian account has to be linked
to Warp (see "Make it yours").

## Make it yours

1. Replace `acme/api-service` in `factory.yaml` with a repository your Warp
   team's GitHub installation can reach. It appears in no other file.
2. Replace `YOURKEY` in `automations/jira-agent-sessions/automation.md`
   with your Jira project key, the prefix of the project's issue keys (the
   `ENG` in `ENG-123`).
3. Install Warp for Jira and connect the site. This is Jira Cloud only;
   Jira Server and Data Center are not supported. A Jira site admin installs
   the Warp app and, from the app's **Configure** page in Jira, connects it
   to your Warp workspace. If you are not a site admin, the setup flow lets
   you send the request to one; the approval link lasts seven days. Once
   connected, the site is available to every factory in the workspace. The
   [Jira integration page](https://docs.warp.dev/factories/integrations/jira/)
   has the exact steps.
4. Attach Jira to this factory. The `integrations` entry in `factory.yaml`
   attaches Jira when the definition is applied; it does not install the
   app or connect the site, and the apply checks that the workspace
   connection from step 3 exists. This GitHub-backed definition is edited in
   files, not through dashboard project selection. Set the project scope in
   `automations/jira-agent-sessions/automation.md` with `project_keys`.
   Reuse or narrow an existing Jira session automation instead of adding
   another handler for the same sessions.
5. Link accounts. Each teammate who will assign or mention Warp links their
   Atlassian account to Warp from their Jira personal settings (**Personal
   settings** > **Warp**). An unlinked account gets a prompt to connect
   instead of a run.
6. Optionally narrow intake with `labels` as shown above. If you want the
   foreman to move the work item, for example to "In Review" once the PR is
   open, say so in the automation body; Jira permissions and the project's
   valid transitions apply to everything the agent does.
7. Swap the runner's `dockerImage` for your stack, and optionally change
   `agentDefaults.model` (any Warp Agent model ID). `alias` is the
   factory's handle on chat platforms and Linear; in Jira you always
   address Warp, so here it only names the factory.

## Sample task and expected output

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
- A branch named after the key, such as `yourkey-123-unknown-customer-404`,
  pushed to `acme/api-service`, and a pull request titled
  `YOURKEY-123: Return 404 for unknown customer IDs` whose description links
  the work item and includes the test and lint output.
- A comment on `YOURKEY-123` with the pull request link and one line on
  what changed and how it was verified, and the same result in the session,
  which Jira now shows as completed.
- Nothing merged, and the work item's status and assignee unchanged.

When the task is out of scope, the foreman opens no PR. If the description
has no acceptance criteria, or the change belongs in a repository this
factory is not attached to, it asks one question in the session and the
session shows as waiting for input; reply in the session to continue the
same run. If the instruction only asks a question, the foreman answers it in
the session and stops.

## Validate it

```bash
python3 scripts/validate_factory_files.py examples/11-jira-to-pr
python3 scripts/check_conventions.py
```

The validator checks the tree against the server's parser. It defers
integration availability to apply time, so a pass does not prove that the
Jira connection, the project, or the account links exist.

Register the factory in Warp with a GitHub-backed definition pointing at
your copy of this directory; pushes sync the definition after the
`warp/factory-config` check passes. Then prove the intake path with one
small work item: a session in the configured project starts a run under the
automation, a PR with the key in its title appears in the attached
repository, and the comment lands on the work item. Also assign Warp on a
work item in a project outside the filter and confirm this automation starts
nothing. Reply to a clarification in the session and confirm it continues
the same run. Check that no other automation or factory matches the trial.

## Set it up with a prompt

Paste this prompt into any of:

- your factory's foreman, in the factory dashboard
- the factory web composer
- Factory MCP, from a coding agent [connected to it](https://docs.warp.dev/factories/factory-mcp/)

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
