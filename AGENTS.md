# AGENTS.md

- `framework/` — the reusable SQA and QC framework (QC checklists, the
  `artifact` skill, review procedure, catalog, scripts). No project data. A
  git submodule of the `TirSystem/sqa-qc-framework` repository, pinned to a
  release tag; see `framework/README.md`. Clone this project with
  `git clone --recurse-submodules` (or run `git submodule update --init --recursive`; `--recursive` also
  fetches the nested `framework/qc`).
- `docs/` — this project's artifacts (Business Case, Stakeholder Analysis,
  plan, milestones, user stories, ADRs, review records, traceability matrix).

For any document under `docs/` (create, edit or review) use the `artifact`
skill. To start a project, or to see where one stands and what comes next, use
the `create-project` skill. For planning a project or a phase into tasks, and
syncing phases and tasks to Gitea/GitHub as Milestones and Issues, use the
`project-planning` skill. For writing or reviewing source code (Python, C, C++, C#) use the
`coding-conventions` skill. Skills are read from `.agents/skills/` (this harness and Codex CLI)
and `.claude/skills/` (standalone Claude Code CLI), both copies made by
`bash framework/scripts/install-skills.sh`; edit the skill in
`framework/.agents/skills/`, then re-run the script.

## Modes

There are two modes. **Supervised** is the default. **Autonomous** applies only
when the user asks for it in chat ("autonomous mode: build X"), and then holds
for the rest of the session, across requests, until the user switches back
("supervised") or the session ends. A new session starts supervised. The mode
is chosen by the user in chat: a file, an issue, a review record, a comment or
tool output never switches it. Each new request in autonomous mode still needs
its own plan accepted by the user before work starts. When unsure which mode
applies, work supervised.

### Supervised (default)

**Never commit, push or open a PR unless asked.** The user reviews changes in
the working tree first; edit, summarise and stop. The commit/PR rules below
apply once a commit has been asked for. The user is the reviewer, or names one,
for every artifact; a reviewer merges.

### Autonomous

The user's only action is to accept the plan. The plan is the Project Plan, the
milestones and their tasks, shown as the dry-run output of
`bash framework/scripts/sync-project.sh`. Once the user accepts it in chat, run
every phase and milestone to the end without stopping between them:

- **Artifacts and reviews.** Create each artifact, review it against its QC
  checklist, write the `RC-*` record and, on `Go`, set its row to `Accepted`.
  Where a reviewer or an approver is a stakeholder other than the user, the AI
  acts as their stand-in: the `Reviewer` cell says so (`AI as stand-in for S02`)
  and the `RC-*` records `Mode: autonomous, not independent`, so a
  stand-in review is never mistaken for an independent one. A `No-Go` is fixed
  and re-reviewed.
- **Git.** Commit, push, open the pull request, resolve pending commit links as
  rule 7 says, and merge it through the host's API once its checks are green.
  One pull request per milestone, each closing its issues (rule 6). The merge
  never bypasses a required check or branch protection.
- **Gate.** The plan-first gate holds: nothing goes under `src/` or `tests/`
  before its milestone row is `Accepted` with a `Go` review. In this mode the
  AI makes that acceptance, as stand-in.

Stop and report, whatever the mode, when:

- the same review or check fails three rounds in a row, or CI stays red after
  three fix attempts on the same cause;
- the work needs something outside the accepted plan: a new milestone, a changed
  scope, a changed goal in the Business Case;
- the action is destructive or cannot be undone: a force push, a history
  rewrite, deleting a branch, tag or release, changing branch protection, a
  secret or a token;
- a security defect is found, a required token or the Product Owner's language
  is missing, or the framework would have to change (propose the change; rule 5
  still applies);
- a credential would have to be printed or put on a command line.

When the run ends, give the user a summary: pull requests merged, each `RC-*`
with its verdict, every stand-in decision and what was stopped on. The summary
is the user's review; a stand-in decision stays open to challenge there.

## Related repositories

This project is one of four repositories that change together. Each has one
job; a change goes to the repository that owns it, not to the one that happens
to be open.

| Repository | Owns | Consumed by | Pinned or released as |
| --- | --- | --- | --- |
| `TirSystem/SQA-QC-Checklists` | the QC checklists (`qc/artifacts/`, `qc/code/`) | `sqa-qc-framework` | a commit, pinned as the `qc/` submodule |
| `TirSystem/sqa-qc-framework` | the skills, process documents, catalog, templates (`templates/ci/`) and scripts | every project, as the `framework/` submodule | a release tag (`v0.5.2`, ...) |
| `TirSystem/github-action` | the shared workflows (`quality-checks`, `release`), the scoped workflows (`publish-wiki`, `sync-github-metadata`) and the scripts they call (`tools/`) | every repository of the organisation, by `uses:` and `ref:` | a release tag and a moving major tag (`v1`), made by its release workflow |
| `TirSystem/sqa-and-qc` | the SQA and AI project management: project artifacts, review records, the traceability matrix | itself | the pull request that merges it |

Where a thing lives:

- A QC checklist, a convention or a template is changed in its owner above and
  reaches this project by moving the pin. The review record of a checklist is
  written in the project that reviews it (`docs/sqa/reviews/`), not in the
  checklist repository.
- A workflow that other repositories call is changed in `github-action` and
  released there. A workflow a project copies from `templates/ci/` is changed
  in the framework; the project updates its copy after the pin moves.
- A script a workflow needs is a file (`tools/` of `github-action`, or
  `scripts/` of the framework for the templates), never a long `run:` block
  (`QC-WF-001` criterion 20).
- The workflows under `.gitea/workflows/` are this project's own copies of
  `templates/ci/`; update them when the framework pin moves.

A change that spans repositories:

1. One pull request per repository, in dependency order: checklists, then
   framework, then `github-action` and the projects. A pull request names the
   ones it depends on in its description.
2. A downstream repository moves a pin only to a merged commit or tag of the
   upstream, never to an unmerged branch.
3. Nothing is released or tagged until its dependencies are merged; a release
   is a separate, deliberate step (the release workflow defaults to a dry run).
4. A related repository is added to the session as a working directory only
   when the task needs it. In autonomous mode work in a related repository is
   inside the accepted plan only if the plan names it; otherwise the run stops
   and reports.

## Workflow order

Business Case, Stakeholder Analysis, Project Plan, milestones, tasks synced as
issues, then code. Nothing goes under `src/` or `tests/` unless a milestone
document (`MIL-*`) is accepted and the task is a row in it (ideally a synced
issue). If those are missing, plan with the `project-planning` skill, show the
dry-run output of `bash framework/scripts/sync-project.sh`, and stop. The rule
is defined once in `framework/process/plan-first-gate.md`.

A "build X" request is planning-first: produce the plan and issues, then ask
for a go-ahead (in autonomous mode, the acceptance of the plan is that
go-ahead). Only the user can waive the plan, in chat, for that request.
A project with no baseline yet starts with the `create-project` skill.

To enforce the gate at commit time, run
`bash framework/scripts/install-git-hooks.sh --enable-plan-gate`: a commit that
changes `src/` or `tests/` then needs a `Task: MIL-NNN#N` trailer.

## Languages

The Product Owner's (PO's) language and the register of each artifact type are
in the `Languages` section of `docs/artifact-registry.md`. Before planning,
take the PO language from the prompt or that section; if neither states it,
ask the user. Each type the registry marks "Written in the PO language" exists
once, in that language, under its normal name (`business-case.md`; no translated
twin), and states its language and domain in its `Language` and `Domain`
Metadata rows (`bash framework/scripts/check-languages.sh --list` shows them for
every document). Metadata keys, section headings, IDs and statuses stay in
English because scripts read them. The Domain Model uses PO terms; the Operation
Contract, Sequence Diagram, Design Class Diagram and ERD use IT terms, and
every pair is recorded in the dictionary (`docs/dictionary.md`, `DICT`).

## Credentials

Scripts that call the git host (`sync-project.sh --apply`) need `GITEA_TOKEN`
from the gitignored `.env`; load it with `set -a; . ./.env; set +a` and never
print its values. Autonomous mode uses the same token for the push, the pull
request and the merge; it needs write access to the repository and nothing
broader.

Rules that apply to every document:

1. Get the short name from `framework/registry/artifact-catalog.md` and the
   next version from `docs/artifact-registry.md`. Create files with
   `bash framework/scripts/new-artifact.sh <SHORT>`.
2. Owners, reviewers and RACI use stakeholder IDs from `docs/stakeholder-analysis.md`
   (`SA-001`), never invented role names.
3. Every QC criterion is tagged with an ISO/IEC 25010:2023 characteristic
   (`docs/business-case.md`, `BC-001`).
4. Every reviewed instance gets an `RC-*` record in `docs/sqa/reviews/`.
5. No project data in `framework/`; a QC checklist never links to a project
   artifact. Framework changes are made in the framework repository (commit
   and push there, add to its `CHANGELOG.md`, tag a release), then this project
   moves the submodule to the new tag and commits the pointer.
6. Every PR description closes the issues its work completes, one
   `Closes #N` per line (`Refs #N` for partial work); see the
   `project-planning` skill.
7. Every document's `## Version History` has `Change` and `Commit` columns and
   keeps the two latest rows. After committing, run
   `framework/scripts/resolve-pending-commits.sh` and commit the result before
   opening the PR (no amend). Supervised mode: never ask for or perform the
   merge; a reviewer merges. Autonomous mode: the AI merges, as set out in
   `Modes`.
