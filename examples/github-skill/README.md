# Version a GitHub skill

Keep a shared GitHub skill in your factory definition and review its updates
in pull requests. One foreman uses the skill for explicit requests in one
repository. No automations start work in the background.

This version is a historical baseline. It copies the default GitHub skill
from before managed GitHub MCP support was added. It is not the current
default and does not support MCP-only runs. Use it to inspect the starting
point for a skill migration, not to bypass current runtime restrictions.

## Directory structure

```text
factory.yaml
agents/
  foreman/agent.md
runners/
  linux-small.yaml
skills/
  github/
    SKILL.md
    scripts/resolve-threads
```

The `skills/` directory makes the skill available to every agent in the
factory. The helper posts replies and resolves review threads through
`gh`; do not run it in an MCP-only runtime.

## Use this example

Follow the repository's [setup instructions](../../README.md#use-an-example).
After setup, send the foreman an explicit request, such as:

> Read pull request #42 in the configured repository. Summarize the requested
> changes, all three feedback surfaces, and the current CI state. Do not
> change the pull request.

Replace the number with a pull request in your repository. The agent should
return its findings and any missing evidence. This baseline requires a
supported legacy runtime with configured GitHub CLI access. If the runtime
requires managed MCP, update the skill before testing GitHub operations.

## Customize the example

1. Replace `acme/api-service` in `factory.yaml` with a repository that your
   Warp team's GitHub installation can access.
2. Connect the required GitHub integration and confirm that the run has
   access to the repository.
3. Set `alias` to the handle you want to use for the foreman.
4. Replace the runner's `dockerImage` with an image for your stack. This
   baseline needs Git, `gh`, `jq`, Python 3, and the repository's build and
   test tools. The committed Node image is a starting point, not a complete
   toolchain for the skill.
5. Confirm that the runtime permits legacy CLI access and supplies its
   credentials. Do not add tokens to these files or replace restricted
   runtime credentials. Keep this version for comparison only if legacy
   access is unavailable.
6. Optionally, change `agentDefaults.model` to another Warp Agent model ID.

## Compare an update

Keep this baseline in Git history, then update `skills/github/` in a
separate pull request. Leave the factory, agent, and runner unchanged so
reviewers can focus on the skill migration.

For a managed GitHub MCP update, check that API operations use the managed
tools, ordinary Git still publishes branches, and restricted runs cannot
fall back to the CLI. Updating these files does not enable a server feature
flag or make MCP tools available.

## Snapshot provenance

`skills/github/SKILL.md` and `skills/github/scripts/resolve-threads` are
unchanged copies from `logic/factorysource/defaults/skills/github/` in
`warpdotdev/warp-server` at commit
`249c621bc8f0e001bcffd8413d63f5b26f539249`. File modes are also preserved.
The skill's Git blob is `ea7f0d6e436bc596fe11f8d423b7c801f5ec4013`.

Maintainers with access to that source repository can check the copies.
From this repository's root, set `WARP_SERVER` to a local checkout that
contains the pinned commit, then run:

```bash
SOURCE_REF=249c621bc8f0e001bcffd8413d63f5b26f539249
SOURCE_DIR=logic/factorysource/defaults/skills/github
for file in SKILL.md scripts/resolve-threads; do
  git -C "$WARP_SERVER" show "$SOURCE_REF:$SOURCE_DIR/$file" \
    | cmp - "examples/github-skill/skills/github/$file" || break
done
```

No output means both files match. This checks content, not runtime behavior.
The copied skill is exempt from the repository's terminology check so that
the source stays exact; the README and agent prompt are not exempt.
