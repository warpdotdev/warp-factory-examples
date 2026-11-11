# 08: Slack to pull request

Mention the factory in one Slack channel to request a code change. Progress,
questions, and the pull request link stay in the same thread. A human reviews
and merges. This example replaces the intake in
[`01-single-repo-quickstart`](../01-single-repo-quickstart) with Slack
mentions.

## What this example shows

- The `slack` / `app_mention` trigger is scoped to one channel with the
  `channels` alias. Mentions outside that channel do not match it.
- The `integrations` list declares Slack. You still need to install the app,
  invite it to the channel, and link accounts.
- The thread is the work item's home. The acknowledgement, any clarifying
  question, and the result all land in the thread that started the work,
  and plain replies there continue it.
- The foreman prompt confirms the deliverable before work starts and asks
  one question instead of guessing.
- Both agents share one runner and inherit `model` and `runner` from
  `agentDefaults`.

## Directory structure

```
factory.yaml                integrations: slack; one repository
agents/
  foreman/agent.md          FOREMAN, confirms in the thread, dispatches, reports the PR
  implementer/agent.md      IMPLEMENT, turns the request into a PR
automations/
  slack-intake/automation.md   slack/app_mention, filtered to your-intake-channel
runners/
  linux-small.yaml          2 vCPU / 4 GB, node:22-bookworm-slim
```

## How Slack intake is routed

The one automation subscribes to `slack` / `app_mention` and filters on
`channels: [your-intake-channel]`:

- `app_mention` fires when someone @-mentions the factory's Slack app in a
  channel the app has joined. Plain channel messages, direct messages, and
  reactions are different events and never match this trigger.
- `channels` is the authoring alias for `channel_ids`. It takes exact channel
  names, with or without a leading `#`, and Warp resolves each name through
  the team's Slack connection when the definition is applied. A name must
  resolve to exactly one channel the app can see, so invite the app before
  the definition syncs. The validator defers this lookup and passes with the
  placeholder in place. Applying the definition fails if a name is unresolved.
- Filter keys combine with AND and an absent key is a wildcard. `app_mention`
  also accepts `users` (Slack usernames or email addresses) and `keywords`
  (case-insensitive substrings of the message), so `keywords: [please]` or
  `users: [alex@example.com]` would narrow intake further. See the
  [trigger reference](https://docs.warp.dev/factories/automation-triggers/)
  for the full key list.

Slack activity that does not match this definition is handled as follows.

- **A mention in any other channel** does not match this automation, so
  this route adds no 👀 reaction, reply, or work item. Other automations may
  still handle it.
- **A direct message** is a `message_dm` event, which this definition does
  not subscribe to, so this route starts nothing. Add a `message_dm`
  automation like [`02-sdlc-issue-to-pr`](../02-sdlc-issue-to-pr) if DMs
  should count.
- **A plain reply in a thread that already has a work item** can continue
  that work item without a new mention. Warp classifies whether the reply is
  meant for the factory, and the automation's filter is not consulted again.
  To require a mention for replies too, set
  `slack.autoRespondToThreadReplies: false` on the integration entry:

  ```yaml
  integrations:
    - type: slack
      slack:
        autoRespondToThreadReplies: false
  ```

Avoid overlapping triggers when you extend this example. A channel message
that mentions the app also emits `app_mention`, so adding a `message_posted`
trigger on the same channel starts two runs per mention.

Filters decide when work starts, not what the app can read. Its bot scopes
cover history in every channel it has joined. The requester must link their
Slack account to their Warp account and belong to the factory's Warp team.
If their accounts are not linked, the app prompts them to connect those
accounts instead of starting work.

## Runner configuration

Both agents use `linux-small`, with 2 vCPUs, 4 GB of memory, and the
`node:22-bookworm-slim` image. The image provides Node and npm.

## Customize the example

Copy the entire example directory into your repository before making these
changes. See [Use an example](../../README.md#use-an-example) for the shared
setup procedure.

1. Replace `acme/api-service` in `factory.yaml` with a repository your Warp
   team's GitHub installation can reach. The agents never name the
   repository. The factory has exactly one.
2. Connect Slack. Select Slack when you create the factory, or connect it
   later from the factory's **Settings**. Finish the install with **Add to
   Slack** if your workspace needs administrator approval. The `integrations`
   entry in `factory.yaml` declares that the factory uses Slack. It does not
   connect it.
3. Invite the app to the intake channel. Private channels always need an
   invitation.
4. Inspect existing automations. Reuse or narrow an `app_mention` handler,
   and avoid a `message_posted` handler that also matches the same mentions.
   Preserve unrelated triggers.
5. Replace `your-intake-channel` in `automations/slack-intake/automation.md`
   with that channel's name after connecting Slack and inviting the app.
   Warp resolves the name against the Slack connection when the definition
   is applied. An unresolved name prevents the definition from being applied.
6. Link accounts. Everyone who will mention the factory must link their Slack
   account to their Warp account. The app prompts them the first time they
   mention it, and connecting the app does not link anyone. Work is
   attributed to the linked Warp user.
7. Adjust `alias` in `factory.yaml`. It is the handle the app answers to in
   Slack, written as `@Intake` below.
8. Replace `dockerImage` in `runners/linux-small.yaml` with an image for your
   stack.
9. Optionally, change `agentDefaults.model` to another Warp Agent model ID.

The [Slack integration
docs](https://docs.warp.dev/factories/integrations/slack/) cover the install,
channel invitations, and account linking in detail.

## Validate the example

From the repository root:

```bash
python3 scripts/validate_factory_files.py examples/08-slack-to-pr
```

The validator runs Warp's parser over the definition files. A misspelled
event name or an unsupported filter key fails this check. The channel name
is reported as a deferred resolution, not a failure. The
`warp/factory-config` check on your definition pull request dry-runs the
change against your team. Applying the definition resolves the name through
your Slack connection. These checks catch an unresolved name, but schema
validation alone does not prove prompt behavior.

## Register the factory

Follow [Use an example](../../README.md#use-an-example) to copy this directory
into your definition repository, customize it, commit and push the files,
and create a factory with a GitHub-backed definition pointing at your copy.
The registered root is the directory containing `factory.yaml`. Pushes to
the production branch sync it after the `warp/factory-config` check passes.

## Test the factory

### Send a sample task

The sample assumes `acme/api-service` is a Node service with an HTTP router
and a test script the runner image can run (`npm test`). Any repository
works as long as the runner image carries its toolchain.

In `#your-intake-channel`:

> @Intake add a `GET /healthz` route that returns `{"status":"ok"}` with a
> 200, and a test that covers it.

What you should see, in order:

1. The app reacts to the message with 👀, and a work item appears in the
   factory dashboard.
2. The foreman replies in the thread with one sentence restating the
   deliverable, along the lines of "Adding a `GET /healthz` route that
   returns `{"status":"ok"}` with a 200, plus a test; the PR will land in
   this thread."
3. A branch named like `factory/healthz-route` appears on `acme/api-service`
   with a pull request against the default branch. The description links the
   Slack thread and includes the test command and its result.
4. The foreman replies in the same thread with the pull request link and how
   the change was verified. The factory does not merge. A human reviews the
   pull request.

Two more mentions worth sending on a first run:

- The same request in a channel that is not `#your-intake-channel` does not
  match this automation. This automation adds no reaction, reply, or work
  item. Other automations may still handle the request.
- `@Intake make the API faster`: the foreman replies with one clarifying
  question, such as which endpoint is slow and what response time counts as
  fixed, and stops without a branch or pull request. Answer in the thread.
  The reply continues the same work item.

A request the factory cannot act on, such as a change to a repository that
is not attached or something that is not a code change, gets a one-sentence
reply saying so, and the foreman stops. A mention that is not a request at
all, such as a thank-you, gets no reply.

### Check the first-run results

Confirm that a mention in the intake channel gets a 👀 reaction and a
one-sentence acknowledgement in the thread, followed by a pull request link.
A mention in another channel must start nothing through this automation.
A vague mention should get one question and no pull request.

## Set up with an agent

Paste this into any agent that can edit your definition repository and reach
Warp's validation service:

<!-- terminology-allow-begin -->
- Ask the factory's foreman in a Slack thread or from the factory dashboard.
- Use the factory web composer.
- Use Factory MCP from a connected coding agent such as the Warp Agent.
<!-- terminology-allow-end -->

Fill in the four values first.

```text title="Set up Slack intake for my repository"
Read the example at
https://github.com/warpdotdev/warp-factory-examples/tree/main/examples/08-slack-to-pr
and set up the same factory for my repository. Copy its tree into my
definition repository and replace these placeholders:

- acme/api-service in factory.yaml -> <owner/repository>
- your-intake-channel in automations/slack-intake/automation.md -> <#channel>
- alias: Intake in factory.yaml -> <handle the app should answer to>
- node:22-bookworm-slim in runners/linux-small.yaml -> <image with my toolchain>

Keep the single-channel app_mention trigger, the foreman and implementer
agents, and the one runner. Reuse or narrow existing handlers so a mention
matches only one route, preserving unrelated triggers. Validate the
definition and open a pull request without applying it.
List what I still have to do by hand: connect Slack to the factory, invite
the app to the channel, and have each requester link their Slack account.
```
