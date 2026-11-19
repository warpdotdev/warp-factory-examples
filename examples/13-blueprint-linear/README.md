# Two stages in order

Turn incident notes into a handoff with a linear Blueprint:
`start → extract → handoff → end`.

All procedures live in [`factory.yaml`](factory.yaml). The only other
definition file, [`agents/foreman/agent.md`](agents/foreman/agent.md), declares
the foreman required by this complete factory root. Both stages run in that
foreman's conversation. There is no worker library, automation, skill, or
runner to configure. The factory attaches no repositories.

## Customize the example

- Confirm Blueprint availability and access for your team before attempting
  to run this draft example. Application and execution remain unverified.
- Copy this directory into a definition repository you control. Follow the
  [repository setup instructions](../../README.md#use-an-example), including
  validation and application, before testing.
- Keep `repositories: []` for this text-only task. No repository checkout,
  integration, secret, or project toolchain is needed by the stage procedures.

## Try the sequence

After applying the definition, start a new task with the foreman and send:

```text
Prepare an incident handoff from these notes. Do not access external data or publish it.
At 09:10 UTC, checkout requests began timing out. The team rolled back the
latest deployment at 09:25 UTC, and checkout recovered at 09:28 UTC.
The cause has not been confirmed.
```

Inspect the stage history: `extract` must finish before `handoff` starts.
The final message must include the supplied timeline, checkout timeouts as
the impact, and the unconfirmed cause under Open questions. It must not
identify the deployment as the proven cause or claim that content was posted
elsewhere.

Change `extract.to` to change what follows extraction. Moving stage blocks
within the YAML does not change their order. After applying a changed
definition, use a new task to test it. Existing tasks keep their Blueprint.

If the order is wrong, check `blueprint.start.to` and `extract.to`, then
confirm which applied revision the task used. Parser acceptance alone does
not prove the sequence ran.
