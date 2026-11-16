---
name: github
description: "Work with GitHub branches, commits, and PRs using ordinary Git and the managed GitHub MCP, or the gh CLI for supported legacy runs. Covers direct Git pushes, server-side PR creation, feedback, reviews, and CI. Use for any branch, commit, or PR operation."
---

# github

How to use GitHub. This skill covers the mechanics of the surface, not what to implement or how to judge a change.

## Tools

- **Managed MCP:** When the Warp-managed GitHub MCP is available, use it for GitHub API operations. A run explicitly configured with restricted GitHub credentials must also use this path, even if tool discovery fails.
- In managed-MCP mode, do not use `gh`, raw GitHub API calls, or scripts that call `gh`. Missing `GH_TOKEN`, `GITHUB_TOKEN`, or CLI login is expected. Do not request personal tokens or extract Git credentials for API calls. Report missing tools and actual MCP errors instead of switching authentication paths.
- **Legacy CLI:** The `gh` commands and `scripts/resolve-threads` below apply only to runs outside managed-MCP/restricted mode with supported, configured CLI access. Use `gh` non-interactively with `--repo <owner>/<repo>` and `GH_PAGER=cat`. Do not pass `--no-pager` to `gh`; it is not a global `gh` option.
- Use `git --no-pager` for repository operations in either mode. Local commits do not require GitHub authentication; clone, fetch, and push use the existing Git credential configuration.
- Never merge a PR.
- Discover the actual tools and input schemas before claiming a capability. Documentation or source changes do not prove that this run has the new tools.

## Issue lifecycle

In managed-MCP mode, search for an existing issue before creating one. Use `search_issues` with `query` and required `owner`/`repo`. The query can include conjunctive GitHub filters, but not `repo:` qualifiers, `OR`, or parentheses. Search uses `page`/`perPage` and exposes at most 1000 results. `incomplete_results` means the search is not exhaustive. `list_issues` uses `after`/`perPage` and `pageInfo.hasNextPage`/`endCursor`; keep filters fixed and deduplicate by issue number.

1. Read a candidate with `issue_read` (`get` or paginated `get_comments`). Adopt a matching issue instead of creating a duplicate.
2. Use `list_label` with cursor pagination for repository labels. Use `ui_get` with `method: assignees` for assignable logins and avatars, not emails. The latter returns at most 1000 users; `has_more` means incomplete data with no continuation. Use an exact verified login, not a display name or inferred requester identity.
3. If no matching issue exists, use `issue_write` with `method: create`, title, body, and existing labels. Do not retry an uncertain write automatically; search and read first.
4. Use `issue_write` with `method: update` and `issue_number` for title/body changes. Omitted fields stay unchanged; clearing an issue body is not supported. `update_issue_labels` and `update_issue_assignees` replace complete lists; read the current values first, preserve unrelated values, then send the complete desired list. An empty list clears all values. Concurrent changes can be overwritten; reread after a write and report partial or uncertain results.
5. Use `add_issue_comment` for progress or evidence. Close with `issue_write`, `method: update`, `state: closed`, and `state_reason: completed` or `not_planned`. Reopen with `state: open` and no closing reason. `issue_write` rejects PRs; PR state uses `update_pull_request`.

GitHub Projects, custom tracker fields, and other tracker-specific metadata are not supported by these issue tools. Report those gaps without claiming that basic issue creation is unavailable. Report a successfully created issue with its returned URL; a prepared draft is not a created issue.

## Branches and commits

- Branch off the repository's base branch. Confirm the base branch from the repository's conventions; do not assume `main`. Capture it once into a variable (e.g. `BASE_BRANCH=develop`) when you check out, and reuse that value for the PR's MCP `base` argument or CLI `--base`.
- Name factory branches `factory/<short-slug>`.
- The git identity and GitHub credentials for this run are already configured. Use them as-is; never set or override them, whether through `git config user.*`, `git -c user.*`, `--author`, or the `GIT_AUTHOR_*`/`GIT_COMMITTER_*` environment variables.
- In managed-MCP mode, call `get_commit_attribution(owner, repo)` before each new commit. Preserve the configured bot author/committer and append a nonempty returned `coauthor_trailer` exactly once. A null trailer means no human credit. Check the resulting commit metadata before pushing. If lookup fails, stop rather than guessing an identity. Do not rewrite earlier commits to change credit.
- Commit co-author credit is metadata, not authentication. The lookup does not create commits, push them, or return a GitHub token.
- The server prefers the human co-author's Factory account email and falls back to GitHub noreply when it is missing or blank. Use the returned trailer even if that email is not associated with the person's GitHub account; do not substitute a public GitHub email or infer another address.
- A factory's or agent's display name belongs in labels, comments, and footers - never in a commit's author or committer field.

## Creating a PR

### Managed MCP: push first, then request a PR

Git and MCP use separate network paths. The runner sends Git pushes directly to GitHub with its restricted App installation token. It does not push code to Warp server, and Warp server does not proxy the Git commands. The runner sends the PR tool request to Warp server, which calls GitHub's PR API using server-selected credentials. For permitted human-authored PRs, the human's token stays on the server; bot-authored PRs use installation credentials.

1. Prepare the intended branch and any new local commits using the guidance above. If the branch is already published with the intended commits, no new commit or push is needed.
2. Otherwise, push the branch to the intended GitHub repository with ordinary `git push` and the existing Git configuration. If the push fails, report the failure and stop PR creation. Do not upload files to Warp server or try to create a PR for unpublished commits.
3. Call `create_pull_request` through the managed MCP with `owner`, `repo`, `head`, `base`, `title`, `body`, and `draft: true`. Use the captured base branch. Read the prepared description file and pass its contents as `body`, not its local path. The tool opens a PR between branches already on GitHub; it does not publish local code. Cross-repository heads are not supported.
4. Call `report_pr` as soon as creation succeeds, before any labeling operation.
5. Use `pull_request_read` with `method: "get"` and `pullNumber` to verify the head branch, base branch, and changed-file count. If the PR is wrong, close it with `update_pull_request` and correct the branch selection before creating its replacement.

Size the description to the change, using the implementation agent's proportionality rule. Update the title or body with `update_pull_request` and `pullNumber`. When the work is ready, call it with `draft: false`, then reread the PR to confirm the draft state. GitHub validates whether the change is allowed. This operation does not approve or merge the PR. The `state` field only means open or closed.

### Legacy CLI

```bash
GH_PAGER=cat gh pr create --draft --repo <owner>/<repo> --head <branch> --base "$BASE_BRANCH" \
  --title "<title>" --body-file /tmp/pr_body.md
```

- Call `report_pr` immediately after `gh pr create` returns, before labeling the PR.
- Write the body to a file first. Do not inline multi-line bodies in the command.
- Size the body to the change, not the template - a body is as permanent as a comment. The implementation agent's PR description section sets the proportionality rule; this skill only carries the mechanics.
- Verify the creation: `GH_PAGER=cat gh pr view <pr> --repo <owner>/<repo> --json headRefName,baseRefName,changedFiles`. A wrong head branch, a `baseRefName` that does not match `$BASE_BRANCH`, or 0 changed files means the PR is wrong. Close it and create it again correctly.
- Promote when ready: `GH_PAGER=cat gh pr ready <pr> --repo <owner>/<repo>`.
- Update title or body: `GH_PAGER=cat gh pr edit <pr> --repo <owner>/<repo> --title "<title>" --body-file <file>`.

## Native PR stacks

Push each branch and create/report each PR first. Set the bottom PR's base to the trunk and each later PR's base to the previous layer's head branch. Native stack operations do not push commits or create PRs.

- Use `pull_request_stack_read` with `method: list`, optionally `pull_request`, and `page`/`per_page`; use `method: get` with `stack_number` for details. Members are ordered bottom to top.
- Use `pull_request_stack_write` with `method: create` and ordered `pull_requests`. Use `method: add`, `stack_number`, and new members above the current top to extend it. GitHub validates branch links.
- `method: unstack` removes unmerged/unlocked members; merged or queued members can remain. It does not delete PRs or branches. Inspect the result instead of assuming the entire stack was dissolved. Do not retry uncertain writes automatically.
- `merge_queue_read` discovers the queue on the stack trunk, not an intermediate branch. A missing queue entry is not proof of merge.

The no-merge rule above still applies. Tool availability does not grant authorization. For a workflow that separately authorizes queue admission, `merge_pull_request_async` with `merge_action: merge_queue` and a verified `expected_head_sha` requires the queue without direct fallback. For a native stack, the operation includes **all open downstack PRs**; authorization must cover that scope. Do not select `default` or `direct_merge` for a queue-only workflow.

Async responses distinguish `pending`, `enqueued`, `merged`, and `failed`. Poll a returned `details.uuid` with `get_pull_request_merge_result`. `pending` is not acceptance of completion; `enqueued` is final for admission, not eventual merge or deployment. A 409 returns an existing request and its options, not acceptance of newly supplied options. Results expire 24 hours after their last update. Both async submission and polling require Contents write permission. Report a missing permission without changing grants or falling back to another operation. After an uncertain result, read current state rather than resubmitting.

## Reporting the PR as a run output

Call the `report_pr` tool with the PR's HTTPS URL (e.g. `https://github.com/<owner>/<repo>/pull/<number>`) and its head branch as soon as the PR exists in your run — whether you just created it or you adopted an existing one (e.g. picking up review of a PR opened earlier). This is what makes the PR show up as a run output in the UI; without it, nothing is recorded even though the PR itself exists. Adopting a PR is easy to treat as "nothing to report" since you did not open it — report it anyway.

## Labeling a PR or issue

### Managed MCP

Use the exact canonical `factory:<alias>` label supplied in the run context or task brief. Prefer the server-derived name, color, and description; do not derive a different label from a display name. If the canonical name is unavailable, report that limitation rather than inventing a label.

1. For a PR, successfully call `report_pr` before applying the label. A label event before reporting can start a duplicate Factory task.
2. Read PR labels with `pull_request_read` and `method: "get"`. If the canonical label is missing, call `update_issue_labels` with `owner`, `repo`, `issue_number` (the PR number for a PR), and the complete current label list plus the canonical name. This replaces the list; do not send only the new label.
3. If the repository label is missing, use `label_write` with `method: create`, `owner`, `repo`, and the canonical `name`, `color`, and `description`. An existing label can cause an error; inspect `list_label` before retrying and do not change existing metadata. If creation metadata is unavailable, report it rather than guessing.
4. After recovery, read the PR again and apply the label if still missing. Confirm the label appears in the returned label set before claiming success. A failed or partial operation is not proof that no labels were applied.

Report actual MCP failures and continue delivery with the limitation stated. Do not use `gh` or direct API fallbacks.

To remove an obsolete label, read the current list and use `update_issue_labels` with the complete desired list minus that label. For review-time labels, preserve unrelated labels and include exactly the chosen review-time label. Concurrent changes can be overwritten; read the PR again to verify the final set.

### Legacy CLI

In legacy CLI mode, every PR and issue you open or adopt carries this factory's own label, `factory:<alias>`. Apply it as soon as you have the artifact in hand. For a PR, call `report_pr` first: the label fires this factory's labeled-PR automation, and a PR that is not yet reported starts a duplicate task instead of continuing yours.

Resolve the alias first. It is the top-level `alias` in the factory's own `factory.yaml`, checked out beside the skills listed in `WARP_SKILL_DIRS`. Resolve it once per run and reuse it:

```bash
skills_root="${WARP_SKILL_DIRS##*,}"
factory_root="${skills_root%/skills}"
factory_alias=$(sed -n 's/^alias:[[:space:]]*//p' "$factory_root/factory.yaml" | head -1 \
  | sed -e 's/[[:space:]]*$//' -e 's/^"\(.*\)"$/\1/' -e "s/^'\(.*\)'$/\1/")
```

An empty `$factory_alias` means the label is unresolved - warn and leave the artifact unlabeled. Never apply a bare `factory:`.

Canonicalize the parsed value the way the platform derives its own label (`deriveFactoryLabel` in `logic/factory_labels.go`), or a raw value can create a second, mismatched label instead of reusing the one the platform already manages:

```bash
factory_alias=$(printf '%s' "$factory_alias" | tr -s '[:space:][:cntrl:]' ' ' | sed -e 's/^ *//' -e 's/ *$//')
if [ "$(printf '%s' "$factory_alias" | wc -m)" -gt 42 ]; then
  factory_alias="$(printf '%s' "$factory_alias" | cut -c1-41)…"
fi
```

With the alias in hand, run the line that matches the artifact:

```bash
GH_PAGER=cat gh pr edit <pr> --repo <owner>/<repo> --add-label "factory:$factory_alias"
GH_PAGER=cat gh issue edit <issue> --repo <owner>/<repo> --add-label "factory:$factory_alias"
```

If no label exists, create it first then try re-applying:

```bash
GH_PAGER=cat gh label create "factory:$factory_alias" --repo <owner>/<repo>
```

Applying it blocks nothing: on failure, warn and carry on with an unlabeled artifact rather than aborting. Re-applying is free, so apply rather than checking first.

## Reading a PR

In managed-MCP mode, use `pull_request_read` with `pullNumber` and `method: "get"`, `"get_diff"`, or `"get_files"`. Read the branch and repository from the PR details, then use ordinary Git to fetch and check out code. Follow `page`/`perPage` for paginated REST reads. Use `list_pull_requests` with `fields` for compact records, or read each PR separately. A truncated response is not a complete result. Use `list_tags` and `get_tag` for ordinary tags; arbitrary tag-object traversal and commit-associated PR lookup are not available.

Legacy CLI:

```bash
GH_PAGER=cat gh pr view <pr> --repo <owner>/<repo> --json title,body,headRefOid,baseRefName,files,isDraft
GH_PAGER=cat gh pr diff <pr> --repo <owner>/<repo>
GH_PAGER=cat gh pr checkout <pr> --repo <owner>/<repo>
```

## Reading all feedback surfaces

A PR has three comment surfaces. In managed-MCP mode, read conversation comments and top-level reviews with `pull_request_read`, using `method: "get_comments"` and `"get_reviews"`. Read inline discussions with `method: "get_review_comments"` and `after`/`perPage`. Follow the thread connection's `pageInfo.hasNextPage` and `endCursor`. Each thread contains at most 100 comments; a larger comment `totalCount` means the discussion is incomplete, with no per-thread continuation. Do not claim to have read the full discussion in that case. An empty result from one surface does not mean there is no feedback.

Do not infer the requesting human's login from the shared bot, a display name, email, or commit co-author trailer. Use only an explicitly verified human login for rules that distinguish the requester's own comments. If that identity is unavailable, keep uncertain feedback actionable.

In legacy CLI mode, `GH_PAGER=cat gh pr view --comments` shows only one surface. Read all three, each with `--paginate`:

```bash
GH_PAGER=cat gh api repos/<o>/<r>/issues/<n>/comments --paginate   # conversation comments
GH_PAGER=cat gh api repos/<o>/<r>/pulls/<n>/reviews --paginate     # top-level reviews
GH_PAGER=cat gh api repos/<o>/<r>/pulls/<n>/comments --paginate    # inline comments
```

For thread resolution state (`isResolved`, `isOutdated`) in legacy CLI mode, query GraphQL `reviewThreads` with a cursor loop.

## Posting comments

A GitHub comment is permanent and stacks in the PR timeline - be concise. Aim for 4 lines and 300 characters.

In managed-MCP mode, use `add_issue_comment` for a PR conversation comment and `add_reply_to_pull_request_comment` with `pullNumber`, `commentId`, and `body` for an inline reply. Use the top-level comment's numeric ID, not a reply ID. Apply the footer and attribution rules below in either mode.

### Footer

End every comment - including replies from `scripts/resolve-threads` - with:

```
[View in factory](<run url>)
```

Keep only this root-run link in run-backed replies; do not add a session link, automation or Factory identity text, or a separate Factory link. No link back to the PR - redundant on the surface the reader is already on. Resolve the link once per run and reuse it. If it cannot be resolved, omit it rather than skipping the comment. Does not apply to the PR description or the managed attribution comment; see "Attribution comment" below.

- To @-mention a person in a comment, reply, or PR description, use the GitHub login provided to you. Never type a handle inferred from a display name, an email, or a chat handle.
- Resolve `FOOTER` once and reuse it verbatim for comments, reviews, and `scripts/resolve-threads --footer "$FOOTER"`. In managed-MCP mode, append it to each comment or review body before passing the body to the tool; MCP does not append the footer for you.
- The link targets the root/foreman run. Resolve a separate `footer_run_id` from the executing run's metadata; never overwrite `OZ_RUN_ID`, which identifies the executing worker. Use the run itself only when metadata establishes that it has no parent. If ancestry cannot be resolved, omit the link rather than falling back to a worker.
- `$OZ_CLI` is the path or command the runtime exports; never hardcode the binary name. If the CLI, run ID, or origin is unavailable, omit the link:
  ```bash
  footer_run_id=""
  if [ -n "${OZ_CLI:-}" ] && [ -n "${OZ_RUN_ID:-}" ]; then
    footer_run_id=$("$OZ_CLI" run get "$OZ_RUN_ID" --output-format json \
      --jq '.root_run_id // (if has("parent_run_id") and .parent_run_id == null then .run_id else empty end) // empty' 2>/dev/null) || footer_run_id=""
  fi
  run_url=""
  if [ -n "${WARP_FACTORY_ORIGIN:-}" ] && [ -n "$footer_run_id" ]; then
    run_url="${WARP_FACTORY_ORIGIN%/}/runs/${footer_run_id}"
  fi
  FOOTER=""
  if [ -n "$run_url" ]; then
    FOOTER="[View in factory]($run_url)"
  fi
  ```
- "View in factory" opens the root run. If the link cannot be resolved, `FOOTER` is empty and the reply is still posted.

### Attribution comment

Post the managed attribution comment (`<!-- warp:pr-artifacts-comment start -->` / `<!-- warp:pr-artifacts-comment end -->`) right after creating the PR; when adopting one that already existed before this run, post it before your first other write to it instead. Check first: a comment already carrying both markers means it is posted - do nothing, and never resolve a duplicate yourself. It is exempt from the Footer above - post its body verbatim, with no footer. Use the run/conversation/thread links your brief supplied, not your own sub-run's, so the reader lands on the factory task - but swap only those `href` values and copy every other byte of the handed-down block, its image markup and both marker pairs included. Never rebuild it from memory. Not posting it blocks nothing - note it in your report and move on.

## Posting a review

In managed-MCP mode, read the current head SHA and changed-file patches with `pull_request_read`. Use `pull_request_review_write` with `method: create`, `pullNumber`, and the verified `commitID`. Include `event` for an immediate body-only review. For inline findings, omit `event` to create a pending review, add each finding with `add_comment_to_pending_review` using verified `path`, `subjectType`, and diff coordinates, then use `method: submit_pending` with `event` and the review body. Each call is a separate write. If the head changes or a call fails, report partial completion and inspect the PR and pending review before proceeding; do not blindly repost comments. Use `delete_pending` only when explicitly discarding the pending review.

In legacy CLI mode, post the body and all inline comments in one API call:

```bash
cat > /tmp/review_body.md << 'EOF'
...
EOF
jq -n '[{"path":"src/f.py","line":42,"side":"RIGHT","body":"..."}]' > /tmp/review_comments.json
HEAD_SHA=$(GH_PAGER=cat gh pr view <pr> --repo <o>/<r> --json headRefOid -q .headRefOid)
jq -n --rawfile body /tmp/review_body.md \
  --slurpfile comments /tmp/review_comments.json \
  --arg event "REQUEST_CHANGES" --arg sha "$HEAD_SHA" \
  '{"commit_id":$sha,"body":$body,"event":$event,"comments":$comments[0]}' | \
  GH_PAGER=cat gh api repos/<o>/<r>/pulls/<pr>/reviews --method POST --input -
```

- `event` is `REQUEST_CHANGES`, `COMMENT`, or `APPROVE`.
- An inline comment must point at a file and line in the PR's diff. GitHub silently drops comments on unchanged lines. Verify each `path` and `line` against the diff first, and move the rest into the body.
- A suggestion block replaces exactly the commented line range. Keep the indentation exact, and do not include lines from outside the range.

## CI and mergeability

### Historical CI and PR evidence

Use `actions_list` with `method: list_workflow_runs` for repository-wide discovery, or supply a workflow ID as `resource_id`. Use `workflow_runs_filter` for `branch`, `event`, `actor`, and `status` (including conclusions such as `failure`). Follow `page`/`perPage` and inspect `total_count`; filtered queries expose at most 1000 results. Compare returned `head_sha` and creation times locally. Server-side SHA/date filters are not available.

Use `actions_get` with `method: get_workflow_run` and the run ID as `resource_id` for current run details. Exact historical run-attempt metadata is not available. Use `actions_list` with `method: list_workflow_jobs`, the run ID as `resource_id`, and `workflow_jobs_filter: {filter: all}` to find prior jobs. A later successful attempt does not erase an earlier failure. Keep the run ID, job ID, `head_sha`, and `run_attempt` together. Call `get_job_logs` for the selected run/job, then compare the returned identity with that evidence. Report missing evidence rather than substituting the latest attempt.

Use `pull_request_history` with `method: events` for dismissed-review IDs and prior review states. Use `method: queue_history` for queue-added/removed, base-ref-changed, and merged events. Queue history uses `events.next_cursor`, `after`, and a fixed `per_page`, not numeric `page`; other history methods use `next_page`. Preserve missing/null facts. A branch name or nearby timestamp is not proof of queue membership or CI causality.

When authorized, use `actions_run_trigger` with `method: rerun_workflow_run` for the whole run or `rerun_failed_jobs` for failed jobs and their dependents. `cancel_workflow_run` also takes `run_id`; `run_workflow` takes `workflow_id`, `ref`, and optional string `inputs`. Read and verify the target first. These official triggers have no head/attempt guards; acceptance is not completion. Do not retry an uncertain mutation without reading current state.

### Current CI

`pull_request_read` with `get_status` returns only the first page of detailed statuses and ignores `page`/`perPage`. If `total_count` exceeds the returned `statuses` count, report incomplete status details; there is no continuation.

In managed-MCP mode, use `pull_request_read` with `method: "get_status"` for commit statuses, `"get_check_runs"` for checks, and `"get"` for mergeability. Use `actions_list`/`actions_get` for workflows, runs, and jobs. Read failed check annotations with `get_check_run_annotations`. Read a completed job with `get_job_logs`, supplying its `run_id` and `job_id`. This returns one tail with `max_bytes` (default 65536, maximum 131072). `truncated` means the prefix is omitted; there is no continuation. A tail can start mid-line or mid-character, and invalid UTF-8 is replaced for display. If the host ignores suffix Range, only a complete small log is accepted; otherwise report `log_range_unsupported`. Follow available metadata and annotation pages. Do not ask for pasted logs before trying these tools. Archive downloads remain unsupported.

Legacy CLI:

```bash
GH_PAGER=cat gh pr checks <pr> --repo <owner>/<repo>
GH_PAGER=cat gh pr view <pr> --repo <owner>/<repo> --json mergeable,mergeStateStatus
```

- Interpret the fields for the selected API: MCP PR details expose REST's `mergeable_state`, not the boolean-or-null `mergeable` field; `gh pr view` uses the GraphQL fields below. Missing or `unknown` merge state is not proof of a conflict or readiness to merge.
- For the legacy CLI, `mergeable: MERGEABLE` with `mergeStateStatus` of `CLEAN`, `BLOCKED`, or `HAS_HOOKS` is a healthy state. `BLOCKED` frequently means only that a review or branch protection is outstanding.
- `CONFLICTING`, `DIRTY`, or `BEHIND`: fetch the base branch and merge it into the PR branch. Do not rebase a branch that others share. Resolve only mechanically safe conflicts, push, and check again.
- `UNKNOWN` or null: GitHub is still computing. Retry a few times with short delays. Do not convert an unknown result into a claim of success.
- These commands are point-in-time reads. Do not block on CI: never sleep-and-recheck until the checks finish before reporting or handing off a PR. Report the current state and move on; a CI failure that lands later arrives as its own follow-up.

## Resolving review threads

In managed-MCP mode, read the full thread discussion first. Reply with `add_reply_to_pull_request_comment`, using the numeric ID after `#discussion_r` in the first/root comment's `html_url` as `commentId`, with `pullNumber`, the fixing commit link, and footer. If that URL is missing or has a different form, report the missing ID; do not guess. The write checks that the comment belongs to the specified PR. Only after the reply succeeds, use `pull_request_review_write` with `method: resolve_thread`, the verified thread `id` as `threadId`, and `pullNumber`. Resolve only feedback you addressed and are authorized to resolve. If a write outcome is unclear, reread the thread before retrying; do not duplicate a successful reply. Do not run `scripts/resolve-threads`, which uses `gh`, even if another procedure references it.

In legacy CLI mode, after a revision addresses a review finding:
1. Reply in that thread with the commit that addresses it (link the commit SHA).
2. Resolve the thread through the GraphQL `resolveReviewThread` mutation, with the thread ID from the `reviewThreads` query.

Use the bundled script for both steps in one call, with `--footer` from Posting comments above:

```bash
scripts/resolve-threads --repo <owner>/<repo> --pr <number> \
  --thread-ids <PRRT_id1,PRRT_id2> --revision <N> --commit-sha <sha> \
  --footer "$FOOTER"
```

The script replies with a link to the commit, then resolves each listed thread. Do not resolve a thread without a reply that shows where it was addressed. Leave a thread that you did not address open, with a reply that says why.

Do not also post a summary comment - the per-thread replies are already the complete record.

## Reviewers

In managed-MCP mode, use `pull_request_history` with `method: "requested_reviewers"` to read current users and teams and `"events"` to read request/removal events with their actors and requesters. Follow all pages. Where the workflow protects human-requested reviews, compare the current requests with those events before adding reviewers; uncertain actor identity is not proof of an agent request. Add with `request_pull_request_reviewers`, `pullNumber`, and `reviewers` containing user logins or `org/team` names. Remove with `remove_pull_request_reviewers`, `pull_number`, and `reviewers` logins or `team_reviewers` slugs without the organization prefix. Each call changes only those names. To replace a reviewer, make separate remove/add calls and report any partial failure.

Legacy CLI:

```bash
GH_PAGER=cat gh pr edit <pr> --repo <owner>/<repo> --add-reviewer <user>
GH_PAGER=cat gh pr edit <pr> --repo <owner>/<repo> --remove-reviewer <old> --add-reviewer <new>
```

The reviewer's GitHub login is provided to you. Never assume or guess a handle or login - ask the requester when you were not given one.

## Media in PR bodies

Embed screenshots or video links in the PR body markdown. Never commit media files to the branch.
