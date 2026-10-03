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
