# Repository settings for repositories that use our workflows

Strict settings for a repository on `git.tirsystem.com` that runs the shared and the scoped
workflows of `TirSystem/git-workflows`. Written for a tool that creates and configures
repositories (RepoFoundry): every setting has its Gitea API field, its value and the reason.

The values were read from `Tirsvad-Udemy-100-days-of-code/006-a-robot-in-reeborg-s-world` and from
`TirSystem/git-workflows` on 2026-11-15, then tightened. Nothing here was applied by the person
who wrote it; check the open questions at the end first.

## Principles

1. Nothing reaches `main` except through a pull request whose checks are green.
2. Every commit on `main` is signed, and nobody (administrators included) can skip a rule.
3. The code that runs in every repository is protected at its source: the tag `v3` of
   `git-workflows` is fetched by all repositories, so whoever can move it controls them all.
4. Turn off what the repository does not use.

## 1. Repository settings

`PATCH /api/v1/repos/{owner}/{repo}`

| Field | Value | Why |
| --- | --- | --- |
| `default_branch` | `main` | The workflows and the release process assume it. |
| `private` | decided per repository | A public repository is also published to GitHub by the push mirror; see the open questions. |
| `has_issues` | `true` | `sync-milestones` creates the milestone issues. |
| `has_pull_requests` | `true` | Every change is a pull request. |
| `has_actions` | `true` | The workflows run there. |
| `has_releases` | `true` | The release workflow creates the release page. |
| `has_wiki` | `true` only when the repository has `docs/wiki/`, otherwise `false` | `publish-wiki-pages` writes the wiki; unused, it is surface without a use. |
| `has_projects` | `false` | Not used. |
| `has_packages` | `false` | Not used. |
| `allow_merge_commits` | `true` | The only merge style; the history and the release notes expect "Merge pull request". |
| `allow_squash_merge` | `false` | One style only. |
| `allow_rebase` | `false` | One style only. |
| `allow_rebase_explicit` | `false` | One style only. |
| `allow_fast_forward_only_merge` | `false` | One style only. |
| `allow_manual_merge` | `false` | A manually merged pull request skips the merge and its checks. |
| `autodetect_manual_merge` | `false` | Goes with the line above. |
| `default_merge_style` | `merge` | |
| `default_delete_branch_after_merge` | `true` | A merged branch does not stay behind. |
| `default_allow_maintainer_edit` | `false` | Nobody else pushes to a pull request branch by default. |
| `allow_rebase_update` | `false` | Updating a branch by rebase rewrites its signed commits. |
| `default_update_style` | `merge` | |
| `ignore_whitespace_conflicts` | `false` | |

## 2. Branch protection

`POST /api/v1/repos/{owner}/{repo}/branch_protections`

One rule, for `main`. No `release/**` rule: these repositories use trunk-based development, no
workflow uses a `release/*` branch, and the rule protected branches that do not exist. Add one
only when the project really maintains old versions, with the same values as `main`.

| Field | Value | Why |
| --- | --- | --- |
| `rule_name` | `main` | |
| `enable_push` | `false` | No direct push. |
| `enable_push_whitelist` | `false` | Nobody is exempt. |
| `enable_force_push` | `false` | History is never rewritten. |
| `enable_force_push_allowlist` | `false` | |
| `enable_status_check` | `true` | A pull request merges only on green checks. Missing in `006`. |
| `status_check_contexts` | `TirSystem/git-workflows: Validate / *`, `TirSystem/git-workflows: OpenGrep / *`, `TirSystem/git-workflows: Release / *` | Three explicit patterns make each check mandatory. A single `TirSystem/git-workflows: *` is, I believe, satisfied by any one passing check; verify that on this Gitea version before relying on it. |
| `required_approvals` | `0` for one-person repositories, `1` when a second person exists | Gitea does not let an author approve their own pull request; with one person a required approval blocks every merge. |
| `block_on_rejected_reviews` | `true` | |
| `block_on_official_review_requests` | `true` | |
| `block_on_outdated_branch` | `true` | The checks ran against the code that will be merged. |
| `dismiss_stale_approvals` | `true` | A new push needs a new approval. |
| `require_signed_commits` | `true` | |
| `block_admin_merge_override` | `true` | An administrator cannot bypass the rules. |
| `enable_bypass_allowlist` | `false` | |
| `enable_merge_whitelist` | `false`, or `true` with the owner and the release account | Optional: limits who presses merge. |
| `protected_file_patterns` | empty | With no push allowlist a pattern such as `.gitea/workflows/**` would block every merge. |

## 3. Tag protection

`POST /api/v1/repos/{owner}/{repo}/tag_protections`

| Field | Value | Why |
| --- | --- | --- |
| `name_pattern` | `v*` | Release tags and the moving major tag (`v3`). |
| `whitelist_usernames` | the account behind `TOKEN_FOR_GITEA_REPO` and the owner | The release workflow creates the tag and moves the major tag, so its account must be allowed. |

This matters most in `TirSystem/git-workflows`, because every repository fetches its scripts at
`v3`. Test the release workflow after turning it on.

## 4. Nothing by default

| Item | Value |
| --- | --- |
| Collaborators | none; access comes from organisation teams |
| Webhooks | none |
| Deploy keys | none |
| Repository Actions secrets | none; the tokens are organisation secrets |
| Push mirror to GitHub | only when the repository is public by design: `sync_on_commit` true, interval `8h`, with a token that can write that one repository |

## 5. Order of work for a new repository

1. Create the repository with the section 1 values and an initial commit on `main`.
2. Wait for the scoped workflows to run once, so their check names exist on the host.
3. Create the branch rule (section 2) and the tag rule (section 3).
4. Read them back and compare with this document (`GET` on the same endpoints).

## 6. Open questions before this is applied

1. Which account is behind `TOKEN_FOR_GITEA_REPO`? It goes into the tag allow list.
2. Does a merge made by Gitea get signed on every repository? It does in `git-workflows`; the
   instance signing key must exist for the rule to be satisfiable.
3. Are all public repositories meant to be public? The push mirror sends the whole history to GitHub.
4. Does a single `TirSystem/git-workflows: *` pattern require every matching check or just one?
5. Not read: the repository Actions page, the organisation settings and the signature trust
   model. Look at them before treating this list as complete.
