# When a repository uses a workflow

Each workflow of this repository has one rule here that says when a repository
of the organisation, in its SQA and QC, should use it. The rule is the opt-in
test: a repository that meets the "Use when" condition calls the workflow, and a
review of that repository (SQA) checks that it does. A repository that does not
meet the condition does not call it.

A new workflow is not finished until its row is in the table below
(`AGENTS.md`, rule "Workflow adoption rules").

| Workflow | Use when | Do not use when | What it gives SQA and QC |
| --- | --- | --- | --- |
| Sync GitHub mirror metadata | Scoped: nothing to do. Every repository of the organisation gets it, so a repository has a GitHub push mirror only if it needs one. | The repository has no GitHub mirror. | The mirror shows the same description and topics as the source of truth. |
| Quality checks | The repository tracks Python (`*.py`) or shell (`*.sh`) files. | It has neither. | Evidence for the code checklists that formatting, typing and shell lint are clean before a merge. Mark the check required in the branch protection. |
| Quality checks C++ | The repository tracks C or C++ files. | It has none. | The same evidence for C and C++, at exact tool versions. |
| Quality checks C# | The repository tracks C# files and can restore packages from the network. | It has none, or cannot reach the package source. | The same evidence for C#, on an exact .NET SDK. |
| Code metrics | The repository has a test suite that writes a Cobertura report and its README or wiki shows size and coverage. | It has no tests, or no report is produced. | Coverage and size as badges, so a reviewer sees them without running anything. |
| English comments | The repository's code comments must be English (the project's language rule) and it takes pull requests. | The project's language rule allows other languages in comments. | Enforces the language rule on every pull request, with the author named. Mark it required to block the merge. |
| Publish wiki pages | Scoped: nothing to do. A repository with a wiki and its pages written as Markdown under `docs/wiki/` is published; one without that folder is skipped. | It has the folder but does not want it published (disable the wiki or use another folder), or the wiki is edited by hand. | The wiki equals the reviewed files; a page change goes through a pull request and its review. |
| Release | Opt-in is not by call: it is for repositories that publish versioned releases pinned by others, and it is run only in this repository. | Not applicable to other repositories. | A tagged, checked release other repositories can pin. |
| Publish accepted milestones | Internal to this repository (it reads this repository's milestones and reviews). A project that keeps `docs/milestones/` and `docs/sqa/reviews/` uses the framework's `templates/ci/` copy. | The repository has no `MIL-*` documents. | Only a milestone that is Accepted with a Go review becomes an issue (the plan-first gate). |
| Validate workflows | Internal: it gates this repository's own pull requests. | Not applicable to other repositories. | Proof that every workflow parses and passes the offline tests. |
