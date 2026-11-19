# A human decision gate

Ask a person which audience needs an incident update before writing it:
`prepare → audience-choice gate → write → end`.

The gate and both stage procedures live in [`factory.yaml`](factory.yaml).
[`agents/foreman/agent.md`](agents/foreman/agent.md) declares the foreman
required by this complete factory root. The foreman runs both stages in its
conversation. No worker library, automation, skill, runner, or repository
checkout is needed.

## Customize the example

- Confirm Blueprint availability and access for your team before attempting
  to run this draft example. Application and execution remain unverified.
- Copy this directory into a definition repository you control. Follow the
  [repository setup instructions](../../README.md#use-an-example), including
  validation and application, before testing.
- Keep `repositories: []` and use fictional incident facts for the exercise.
  The procedures need no integration, secret, or project toolchain.

## Try the gate

After applying the definition, start a new task with the foreman and send:

```text
Prepare an incident update. Facts: checkout timed out from 09:10 to 09:28 UTC.
Restarting the cart-cache service restored checkout. The cause is unknown.
Do not access external data, choose an audience for me, or publish the update.
```

The `prepare` stage must present the facts and open `audience-choice`.
It must not write the update yet.

1. Reply `What are my options?` in the same conversation. The foreman must
   answer without closing the gate or starting `write`.
2. Reply `Use customers.` The gate now has an answer, and `write` must return
   a customer update with the outage times and recovery, without the internal
   `cart-cache` name or an invented cause.
3. In a new task, repeat the request and choose `Use the internal incident
   channel.` The update must retain `cart-cache`.
4. In another new task, repeat the request and reply `Cancel the update.`
   The workflow must end without running `write`.

Inspect the gate and stage history as well as the text. A gate asks for a
decision; it does not publish the update or grant publishing permissions.
If the task writes before an answer, check that the applied definition
contains the gate and that the task started after application. Parser
acceptance does not prove the pause or resumption.
