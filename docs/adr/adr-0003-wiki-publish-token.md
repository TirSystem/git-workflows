# ADR-0003: Wiki publish token and dot-named page titles

## Metadata
| Key | Value |
| --- | --- |
| ID | ADR-0003 |
| CrossReference | [MIL-005], [ADR-0001], [RC-011] |

## Version History
| Date | Status | Author | Reviewer | Change | Commit |
| --- | --- | --- | --- | --- | --- |
| 2026-10-10 | Accepted | Jens Tirsvad Nielsen | S01 | Initial version | [bc3bd07] |

Allowed Status values: `Proposed`, `Accepted`, `Rejected`, `Deprecated`, `Superseded by ADR-NNNN`.

---

## Context

The Publish wiki workflow (MIL-005 task 8) writes the Gitea wiki and so
needs a token that can write to the repository. The existing `TOKEN_FOR_GITEA`
only reads (`read:repository`) and is used by the metadata sync, so raising its
scope would also give the sync write access. Gitea has no wiki-only scope.
After the first publish two open points from [ADR-0001] and [RC-011] were
answered: pages with a dot in the title are accepted, and the stored secret
must hold the bare token string (a value of the form `NAME=token` is rejected
with HTTP 401).

Options:

1. **Reuse `TOKEN_FOR_GITEA` and raise its scope.** One secret, but the
   metadata sync gets write access it does not need.
2. **A separate `TOKEN_FOR_GITEA_WIKI` for a dedicated user.** One more
   secret to store and rotate, and the sync token stays read-only.
3. **Push to the wiki repository by hand.** No secret, but unreviewed content
   and no record of who published.

## Decision

The wiki is published with a separate secret, `TOKEN_FOR_GITEA_WIKI`, holding
a bare Gitea token with scope `write:repository` for a dedicated user that has
write access to this repository only; the workflow falls back to
`TOKEN_FOR_GITEA` only when it is absent. Dot-named titles (`Home.da`,
`Home.ms`) are kept as ADR-0001 decided.

## Consequences

**Positive:**

- The metadata sync token stays read-only, so a leak of it cannot change the wiki or the code.
- The first publish (run 65) created all 15 pages and a read-back matched `wiki/` byte for byte.
- A rejected token is diagnosed from the log (length and shape, never the value).

**Negative:**

- One more secret to store and rotate, at organisation level for now; scoping it to this repository is a follow-up for the person who administers the secrets.
- The fallback to `TOKEN_FOR_GITEA` can hide a missing wiki secret until a write is refused (HTTP 403).
- The credentials guide and MIL-005 task 2 still say that S05 decides which token to use; the decision is recorded here.

## Affected Artifacts

- [MIL-005] — task 2 and task 8 (issues #33 and #42) are settled by this decision.
- [ADR-0001] — its negative consequence about dot-named titles is resolved: they work.
- [RC-011] — its action items for the secret scope (S05) and for storing the secret (S03) are done.

---

[MIL-005]: ../milestones/mil-005-wiki-and-translations.md
[ADR-0001]: ./adr-0001-wiki-structure-and-languages.md
[RC-011]: ../sqa/reviews/rc-011-mil-005-wiki-publishing.md
[bc3bd07]: https://git.tirsystem.com/TirSystem/github-action/commit/bc3bd07b29a0a3dcf45045b9baac64c36144c6d1
