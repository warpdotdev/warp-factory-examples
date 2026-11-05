# 08: Slack to PR

Work intake from Slack. Someone @-mentions the factory in one designated
channel; the foreman replies in that thread with the deliverable it
understood, an implementation agent turns the request into a pull request,
and the foreman posts the PR link back in the same thread. It is the
[`01-single-repo-quickstart`](../01-single-repo-quickstart) topology with
Slack as the only intake path: the point is the intake contract, not the
lifecycle.

## What it demonstrates

- A `slack` / `app_mention` trigger scoped to one channel with the `channels`
  alias, and what Warp does with mentions that fall outside it.
- The `integrations` list declaring Slack, and the setup the files cannot do
  for you: installing the app, inviting it to the channel, linking accounts.
- The thread as the work item's home. The acknowledgement, any clarifying
  question, and the result all land in the thread that started the work,
  and plain replies there continue it.
- A foreman prompt that confirms the deliverable before work starts and asks
  one question instead of guessing.
- Two agents and one runner; both agents inherit `model` and `runner` from
  `agentDefaults`.

## Tree

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
  placeholder in place; the apply is what fails on an unresolved name.
- Filter keys combine with AND and an absent key is a wildcard. `app_mention`
  also accepts `users` (Slack usernames or email addresses) and `keywords`
  (case-insensitive substrings of the message), so `keywords: [please]` or
  `users: [alex@example.com]` would narrow intake further. See the
  [trigger reference](https://docs.warp.dev/factories/automation-triggers/)
  for the full key list.

What happens to Slack activity this definition does not match:

- **A mention in any other channel** matches no automation here, so nothing
  starts: no 👀 reaction, no reply, no work item. The 👀 the app adds to a
  message is the first sign that a mention matched.
- **A direct message** is a `message_dm` event, which this definition does
  not subscribe to, so it starts nothing. Add a `message_dm` automation, as
  [`02-sdlc-issue-to-pr`](../02-sdlc-issue-to-pr) does, if DMs should count.
- **A plain reply in a thread that already has a work item** can continue
  that work item without a new mention: Warp classifies whether the reply is
  meant for the factory, and the automation's filter is not consulted again.
  To require a mention for replies too, set
  `slack.autoRespondToThreadReplies: false` on the integration entry:

  ```yaml
  integrations:
    - type: slack
      slack:
        autoRespondToThreadReplies: false
  ```

Two cautions when you extend this. A channel message that mentions the app
also emits `app_mention`, so adding a `message_posted` trigger on the same
channel starts two runs per mention. And filters decide when work starts,
not what the app can read: its bot scopes cover history in every channel it
has joined, and the person mentioning the factory still has to have linked
their Slack account to a member of the factory's Warp team, or the app asks
them to connect one instead of starting work.

## Make it yours

1. Replace `acme/api-service` in `factory.yaml` with a repository your Warp
   team's GitHub installation can reach. The agents never name the
   repository; the factory has exactly one.
2. Connect Slack. Select Slack when you create the factory, or connect it
   later from the factory's **Settings**; finish the install with **Add to
   Slack** if your workspace needs administrator approval. The `integrations`
   entry in `factory.yaml` declares that the factory uses Slack; it does not
   connect it. Then invite the app to the intake channel. Private channels
   always need an invitation.
3. Replace `your-intake-channel` in `automations/slack-intake/automation.md`
   with that channel's name. Do step 2 first: the name is resolved against
   the Slack connection when the definition is applied, and an unresolved
   name fails the apply.
4. Link accounts. Everyone who will mention the factory must link their Slack
   account to their Warp account; the app prompts them the first time they
   mention it, and connecting the app does not link anyone. Work is
   attributed to the linked Warp user.
5. Adjust `alias` in `factory.yaml`; it is the handle the app answers to in
   Slack, written as `@Intake` below.
6. Swap the runner's `dockerImage` for your stack, and optionally change
   `agentDefaults.model` (any Warp Agent model ID).

To register the definition, create a factory in Warp with a GitHub-backed
definition pointing at your copy of this directory. The registered root is
the directory containing `factory.yaml`; pushes to the production branch sync
it after the `warp/factory-config` check passes. The
[Slack integration docs](https://docs.warp.dev/factories/integrations/slack/)
cover the install, channel invitations, and account linking in detail.

## Sample task and expected output

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
4. The foreman replies in the same thread with the PR link and how the change
   was verified. Nobody merges; a human reviews the PR.

Two more mentions worth sending on a first run:

- The same request in a channel that is not `#your-intake-channel`: nothing
  happens. No reaction, no reply, no work item.
- `@Intake make the API faster`: the foreman replies with one clarifying
  question, such as which endpoint is slow and what response time counts as
  fixed, and stops. No branch, no PR. Answer in the thread; the reply
  continues the same work item.

A request the factory cannot act on, such as a change to a repository that
is not attached or something that is not a code change, gets a one-sentence
reply saying so, and the foreman stops. A mention that is not a request at
all, such as a thank-you, gets no reply.

## Validate it

From the repository root:

```bash
python3 scripts/validate_factory_files.py examples/08-slack-to-pr
```

This runs Warp's parser over the tree, so a misspelled event name or an
unsupported filter key fails here. The channel name is reported as a
deferred resolution, not a failure. The `warp/factory-config` check on your
definition pull request dry-runs the change against your team, and the
apply resolves the name through your Slack connection; those are where an
unresolved name fails.

A first real run should prove four things: a mention in the intake channel
gets a 👀 and a one-sentence acknowledgement in the thread; the same thread
ends with a PR link; a mention in another channel starts nothing; and a
vague mention gets one question and no PR.

## Set it up with a prompt

Paste this into any agent that can edit your definition repository and reach
Warp's validation service:

- the factory's foreman, in a Slack thread or from the factory dashboard,
- the factory web composer, or
- Factory MCP, from a connected coding agent such as the Warp Agent.

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
agents, and the one runner. Validate the definition before you finish, and
list what I still have to do by hand: connect Slack to the factory, invite
the app to the channel, and have each requester link their Slack account.
```
