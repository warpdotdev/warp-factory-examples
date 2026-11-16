# 09: Version a GitHub skill

Keep a shared GitHub skill in your factory definition and review its updates
in pull requests. One foreman uses the skill for explicit requests in one
repository. No automations start work in the background.

This version updates the historical CLI-only skill to the MCP-ready default.
The [baseline commit](https://github.com/warpdotdev/warp-factory-examples/commit/1d33242339265ab6e3765e3dbdb488b215e6c697)
and [baseline pull request](https://github.com/warpdotdev/warp-factory-examples/pull/12)
preserve the exact pre-MCP skill. Compare the two versions to see the update
without changes to the factory, agent, or runner.

Managed GitHub MCP is feature-gated. This example does not enable it or
promise a release date. The run's runtime instructions and available tools
determine which mode the agent can use.

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
factory. The helper remains for supported legacy CLI runs only. In managed
MCP mode, use the reply and thread-resolution tools instead.

## Use this example

Follow the repository's [setup instructions](../../README.md#use-an-example).
After setup, send the foreman an explicit request, such as:

> Read pull request #42 in the configured repository. Summarize the requested
> changes, all three feedback surfaces, and the current CI state. Do not
> change the pull request.

Replace the number with a pull request in your repository. The agent should
return its findings and any missing evidence, using the mode permitted by
the runtime.

## What changes with managed MCP

- GitHub API operations use the managed MCP tools. The agent discovers their
  actual schemas rather than assuming that every upstream GitHub tool is
  available.
- Restricted runs do not fall back to `gh`, raw HTTP, or a script that calls
  `gh`. Missing CLI authentication is expected. A missing MCP tool or a
  permission error is a limitation to report, not a request for a token.
- Ordinary Git still creates commits and pushes branches with the existing
  configuration. Before a managed-mode commit, the agent obtains the
  required attribution metadata without changing the configured identity.
- PR creation happens after the branch is pushed. The MCP tool opens the
  PR; it does not publish local commits. The agent verifies and reports the
  PR before applying its factory label.
- Issues, labels, reviews, feedback, CI, and reviewer operations use their
  matching tools. The skill explains pagination, incomplete results,
  replacement-list updates, and how to handle uncertain writes.
- Supported legacy runs retain their CLI instructions. The optional stack
  mechanics do not require a stacked-PR workflow or authorize merging.

The update uses the shared default, not a particular factory's automatic
approval or reviewer policy. The helper's footer documentation also follows
the default's root-run link format; its GitHub operations remain CLI-only.

## Customize the example

1. Replace `acme/api-service` in `factory.yaml` with a repository that your
   Warp team's GitHub installation can access.
2. Connect the required GitHub integration and confirm that the run has
   access to the repository.
3. Set `alias` to the handle you want to use for the foreman.
4. Replace the runner's `dockerImage` with an image containing Git and your
   repository's build and test tools. Legacy CLI workflows also need `gh`,
   `jq`, and Python 3. The committed Node image is a starting point, not a
   complete toolchain for the skill.
5. Confirm the run's permitted GitHub mode. For managed MCP, verify that the
   runtime supplies the server and required tools. Do not add a guessed MCP
   server ID or tokens to `factory.yaml`. For legacy mode, use only the
   runtime's supported CLI credentials.
6. Optionally, change `agentDefaults.model` to another Warp Agent model ID.

## Compare an update

Compare `skills/github/` against the baseline commit. Keep later policy
changes separate from the tool migration.

When testing the updated skill, check these three cases:

1. Managed MCP is available: GitHub API operations use it; branch publishing
   still uses Git.
2. The runtime requires MCP but discovery fails: the agent reports the
   missing tools and does not try CLI authentication or a fallback.
3. The runtime permits legacy CLI access and supplies credentials: the
   legacy instructions remain usable.

Use a repository you can test in. Start with read-only requests before
testing writes. Parser validation does not test any of these behaviors.

## Snapshot provenance

`skills/github/SKILL.md` and `skills/github/scripts/resolve-threads` are
unchanged copies from `logic/factorysource/defaults/skills/github/` in
`warpdotdev/warp-server` at commit
`bbd2b4f0f0e6751dbf97cf3222bb1f5dae942475`. File modes are also preserved.
The skill's Git blob is `f4bb836fd452b39aebf6e6560ef3c2615eb2423a`.

The baseline copied the same paths from
`249c621bc8f0e001bcffd8413d63f5b26f539249`, with skill blob
`ea7f0d6e436bc596fe11f8d423b7c801f5ec4013`.

Maintainers with access to that source repository can check the copies.
From this repository's root, set `WARP_SERVER` to a local checkout that
contains the pinned commit, then run:

```bash
SOURCE_REF=bbd2b4f0f0e6751dbf97cf3222bb1f5dae942475
SOURCE_DIR=logic/factorysource/defaults/skills/github
for file in SKILL.md scripts/resolve-threads; do
  git -C "$WARP_SERVER" show "$SOURCE_REF:$SOURCE_DIR/$file" \
    | cmp - "examples/09-github-skill/skills/github/$file" || break
done
```

No output means both files match. This checks content, not runtime behavior.
The copied skill is exempt from the repository's terminology check so that
the source stays exact; the README and agent prompt are not exempt.
