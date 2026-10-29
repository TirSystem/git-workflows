# ADR-0014: Wiki sidebar and the names of translated pages

## Metadata
| Key | Value |
| --- | --- |
| ID | ADR-0014 |
| CrossReference | [MIL-014], [ADR-0001], [BC-001], [RC-095] |

## Version History
| Date | Status | Author | Reviewer | Change | Commit |
| --- | --- | --- | --- | --- | --- |
| 2026-10-29 | Accepted | Jens Tirsvad Nielsen | S01 | Initial version; Accepted on a Go review (RC-095); accepted by the author in chat on 2026-10-29 as stand-in for S01, not independent | [9a3bfb0] |

Allowed Status values: `Proposed`, `Accepted`, `Rejected`, `Deprecated`, `Superseded by ADR-NNNN`.

---

## Context

[ADR-0001] named a translation `<Page>.<code>` (`Home.da`) because Gitea reads a
hyphen as a space, so the title of `Home-da` shows as "Home da". The sidebar it
produced lists every page once per language (three lists of eleven pages). The
framework wiki and the checklists wiki have since fixed one shape for every wiki
of the organisation (`process/wiki.md`, checklist `QC-WIKI-001`): one list of
the English pages, a `Related` section when there is one, a `Languages` section
last, and translated pages named `<Page>-<code>`. This wiki is the only one that
differs, and a reader who knows one wiki has to learn a second layout.

Options:

1. **Keep `Home.da` and the three lists.** No change to the published wiki; this
   wiki stays the exception, which `QC-WIKI-001` allows only as a recorded
   deviation with a plan to remove it.
2. **Keep `Home.da` and change only the sidebar.** The layout agrees, the page
   names do not.
3. **Name translations `<Page>-<code>` and use the shared sidebar.** One shape
   everywhere; the pages are renamed and the old pages are left on the wiki.

## Decision

Translated pages are named `<Page>-<code>` (`Home-da`, `Home-ms`) and the sidebar
has one English page list, a `Related` section and a `Languages` section last, as
`QC-WIKI-001` requires; this supersedes the page naming of [ADR-0001].

The rules that follow from it:

- `tools/build_wiki.py` generates the sidebar and the language line (the current
  language in bold, the others as links, separated by `·`); the generator is
  changed, never the page.
- The files are `docs/wiki/<Page>-<code>.md` and each starts with the hash comment
  of [ADR-0001], which is unchanged.
- `Related` links the framework wiki; `Languages` has one `Home` link per language.
- The publisher keeps pages that are not in the folder, so the old `Home.da` and
  `Home.ms` pages stay on the wiki until a person deletes them there.

## Consequences

Positive:

- The three wikis of the organisation have the same sidebar and the same page names.
- The sidebar is a third of its former length and a new page is added once.

Negative:

- The old translated pages (22) and the links to them stay until someone deletes
  them by hand; permanent deletion is not done by the workflow.
- The title of a translated page shows "Home da" on Gitea; the sidebar and the
  language line carry the readable names.

## Affected Artifacts

- [ADR-0001]: its naming decision is superseded.
- [MIL-014]: task 10 does the change.

---

[ADR-0001]: ./adr-0001-wiki-structure-and-languages.md
[MIL-014]: ../milestones/mil-014-wiki-publishing-scoped-again.md
[BC-001]: ../business-case.md
[RC-095]: ../sqa/reviews/rc-095-adr-0014-mil-014.md
[9a3bfb0]: https://git.tirsystem.com/TirSystem/git-workflows/commit/9a3bfb02a1540806399a60bfab898a76a146d4c0
