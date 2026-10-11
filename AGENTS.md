# AGENTS.md

This project uses the SQA and QC framework mounted at `framework/`.

For any document under `docs/` (create, edit or review) use the `artifact`
skill. For planning a project or a phase into tasks, and syncing phases and
tasks to Gitea/GitHub as Milestones and Issues, use the `project-planning`
skill. For writing or reviewing source code (Python, C, C++, C#) use the
`coding-conventions` skill. Skills are read from `.agents/skills/` (this harness and Codex CLI)
and `.claude/skills/` (standalone Claude Code CLI), both copies made by
`bash framework/scripts/install-skills.sh` — re-run it after updating the
framework.

**Never commit, push or open a PR unless asked.** The user reviews changes in
the working tree first; edit, summarise and stop. The commit/PR rules below
apply once a commit has been asked for.

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
- The `framework/` pin here is independent of the one in `sqa-and-qc`; the two
  may differ, and neither is moved to follow the other without a reason in
  the pull request.

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
for a go-ahead. Only the user can waive the plan, in chat, for that request.
Before planning, find the Product Owner's language (the prompt, or the
`Languages` section of `docs/artifact-registry.md`); if neither states it, ask.

To enforce the gate at commit time, run
`bash framework/scripts/install-git-hooks.sh --enable-plan-gate`: a commit that
changes `src/` or `tests/` then needs a `Task: MIL-NNN#N` trailer.

Rules that apply to every document:

1. Get the short name from `framework/registry/artifact-catalog.md` and the
   next version from `docs/artifact-registry.md`. Create files with
   `bash framework/scripts/new-artifact.sh <SHORT>`.
2. Owners, reviewers and RACI use stakeholder IDs from the project's
   Stakeholder Analysis, never invented role names.
3. Every QC criterion is tagged with an ISO/IEC 25010:2023 characteristic.
4. Every reviewed instance gets an `RC-*` record in `docs/sqa/reviews/`.
5. Do not edit `framework/` from this project; propose changes upstream.
6. Every PR description closes the issues its work completes, one
   `Closes #N` per line (`Refs #N` for partial work); see the
   `project-planning` skill.
7. Every document's `## Version History` has `Change` and `Commit` columns and
   keeps the two latest rows. After committing, run
   `framework/scripts/resolve-pending-commits.sh` and commit the result before
   opening the PR (no amend). Never ask for or perform the merge: a reviewer
   merges.
8. Keep the wiki current. A PR that changes a workflow under `.gitea/`, a file
   in `guides/` or `README.md` also updates the matching pages in `wiki/`:
   run `python tools/build_wiki.py` for the English pages (the tests fail when
   they are out of date) and update the Danish (`da`) and Bahasa Malaysia
   (`ms`) pages once they exist, naming the English source they follow. List
   the wiki pages the PR changed in its description, or say "No wiki pages
   changed: <reason>". Never push to the wiki repository by hand: the publishing
   workflow (MIL-005 task 8) copies `wiki/` there when the PR is merged.
