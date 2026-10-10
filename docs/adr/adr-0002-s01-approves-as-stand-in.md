# ADR-0002: S01 approves as stand-in for other reviewers

## Metadata
| Key | Value |
| --- | --- |
| ID | ADR-0002 |
| CrossReference | [SA-001], [RC-001] |

## Version History
| Date | Status | Author | Reviewer | Change | Commit |
| --- | --- | --- | --- | --- | --- |
| 2026-10-10 | Accepted | Jens Tirsvad Nielsen | S01 | Initial version | pending |

Allowed Status values: `Proposed`, `Accepted`, `Rejected`, `Deprecated`, `Superseded by ADR-NNNN`.

---

## Context

The project plan names reviewers by stakeholder ID: S01 (Product Owner) is
the approving reviewer, S05 (DevOps owner and security authority) owns the
milestones, and S03 operates runners and secrets. The Stakeholder Analysis
([SA-001]) says credential, token and permission design cannot be accepted
without S05, and the Business Case lists S05's review of every security-relevant
change as the mitigation for a risk. In practice S01 has been approving
documents and has stood in for S05 and S03 (the first time is recorded in
[RC-001]), because there is currently one person doing all three roles. The
framework also requires that a reviewer is not the author of an artifact.

Options:

1. **Require each named person to review.** The record is independent, but
   work waits for a person who is not available in the project's current
   setup, and the S05 actions in RC-001 and RC-011 stayed open.
2. **S01 approves for everyone and the records say so.** Work continues, and
   each record names who really approved.
3. **Drop the other reviewers from the documents.** Simple, but it hides who
   is accountable and removes the way back to independent review.

## Decision

An artifact approved by S01 counts as approved for the stakeholders named
as its reviewers or action owners (S05, S03), and the record says that S01
stood in. This applies to every artifact of this project, including the review
records themselves, until a named stakeholder asks to review in their own
right; that person's review then replaces the stand-in for later changes.

## Consequences

**Positive:**

- Work is not blocked by a reviewer who is not present, and the records stay honest about who approved.
- The way back to independent review is kept: the stakeholder IDs stay in the documents.

**Negative:**

- No independent check: the author, the approving reviewer and the stand-in are the same person, so a security-relevant change (credentials, tokens, permissions, workflow code) has had no second reader.
- It conflicts with the text of [SA-001] (S05 must accept credential, token and permission design) and with the Business Case mitigation "S05 reviews every change"; both still say so and need an amendment, or S05 needs to be told.
- The framework rule that the reviewer must not be the author is not met; this is a project deviation to be taken upstream, not a framework change.

## Affected Artifacts

- [SA-001] — the statement that credential, token and permission design cannot be accepted without S05 no longer holds.
- [RC-001] — its action item for an independent S05 review is closed by this decision; the other records that refer to it follow.

---

[SA-001]: ../stakeholder-analysis.md
[RC-001]: ../sqa/reviews/rc-001-business-case.md
