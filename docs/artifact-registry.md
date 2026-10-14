# Artifact Registry

This project's artifact state. Types, short names and `CrossReference
Candidates` come from the framework catalog
(`framework/registry/artifact-catalog.md`); this file only records where
each document lives in *this* project and the next version to use.

| Short Name | Artifact Type | Primary File | Next Available Version |
| --- | --- | --- | --- |
| BC | Business Case | docs/business-case.md | 002 |
| SA | Stakeholder Analysis | docs/stakeholder-analysis.md | 002 |
| PP | Project Plan | docs/project-plan.md | 002 |
| MIL | Milestone / Gateway | docs/milestones/*.md | 010 |
| RC | SQA Review Record | docs/sqa/reviews/rc-*.md | 067 |
| TM | Traceability Matrix | docs/sqa/traceability-matrix.md | 002 |
| ADR | Architecture Decision Record | docs/adr/adr-NNNN-*.md | 0010 |
| UCD | Use Case Diagram | docs/use-case-diagram.md | 002 |
| US | User Story | docs/user-stories.md | 002 |
| UC | Use Case | docs/uc-NNN/uc.md | 008 |

## Languages

| Setting | Value |
| --- | --- |
| PO language | en (English, IT) |
| High-level register | IT Executive English |
| Technical register | IT Professional English |

The PO language is English, so no PO-language translations are kept.

The Gitea wiki (MIL-005) is the one exception: its pages are kept in English
(authoritative), Danish (`da`) and Bahasa Malaysia (`ms`). A translation is named
`<Page>.<lang>` (`Home.da`) and names the English source it follows; see
`docs/adr/adr-0001-wiki-structure-and-languages.md`.

| Artifact types | Register | Also kept as a PO-language file |
| --- | --- | --- |
| BC, KPI, PP, MIL | IT Executive English | No (PO language is English) |
| SA, BMC, BPMN, UCD, US, UC, SSD, DM, RA, GOV, DICT | IT Professional English | No (PO language is English) |
| OC, SD, DCD, ERD, ADR, TM, RC, QC, source code | IT Professional English | No |

## Notes

- "Next Available Version" is the zero-padded (3-digit) version to use the
  *next* time a new document of that type is created. Increment it only when
  a brand-new document is created, not when an existing document's
  `## Version History` gets a row.
- `ADR` uses 4 digits (`0001`); `RC` is sequential across all artifact types.
