# Wiki translation review checklist

For MIL-005 task 5 (issue #36): a native reader of Danish and of Bahasa
Malaysia checks the translated wiki pages before they are treated as final.
English is authoritative; the translations follow it (ADR-0001). The drafts
were written without a native review, so please read them as a reader, not as
a proofreader of the English.

This is a working document for reviewers, like [the term list](wiki-terms.md).
It is not a project artifact.

## What to review

Fifteen pages exist on the wiki. You review the five pages of your language.

| Page | Danish (`da`) | Bahasa Malaysia (`ms`) | What it is |
| --- | --- | --- | --- |
| Home | [Home.da](https://git.tirsystem.com/TirSystem/github-action/wiki/Home.da) | [Home.ms](https://git.tirsystem.com/TirSystem/github-action/wiki/Home.ms) | Overview, requirements, setup, run, tests |
| Onboarding | [Onboarding.da](https://git.tirsystem.com/TirSystem/github-action/wiki/Onboarding.da) | [Onboarding.ms](https://git.tirsystem.com/TirSystem/github-action/wiki/Onboarding.ms) | Steps to use the workflow, runners |
| Credentials | [Credentials.da](https://git.tirsystem.com/TirSystem/github-action/wiki/Credentials.da) | [Credentials.ms](https://git.tirsystem.com/TirSystem/github-action/wiki/Credentials.ms) | Secrets, token permissions, rotation |
| Troubleshooting | [Troubleshooting.da](https://git.tirsystem.com/TirSystem/github-action/wiki/Troubleshooting.da) | [Troubleshooting.ms](https://git.tirsystem.com/TirSystem/github-action/wiki/Troubleshooting.ms) | Error messages and fixes |
| Capabilities | [Capabilities.da](https://git.tirsystem.com/TirSystem/github-action/wiki/Capabilities.da) | [Capabilities.ms](https://git.tirsystem.com/TirSystem/github-action/wiki/Capabilities.ms) | What exists and what is planned, with a diagram |

Read each page next to its English page (`Home`, `Onboarding`, and so on). The
files are in `wiki/` in the repository (`Home.da.md`, `Home.ms.md`, ...).

## Checklist (per page)

Mark each item Pass, Fix or N/A. A "Fix" needs a row in the findings table
below.

| # | Check | Notes |
| --- | --- | --- |
| 1 | **Meaning:** every sentence says what the English says; nothing added, nothing dropped | Pay most attention to warnings (secrets, permissions, "not verified") |
| 2 | **Natural language:** reads as written by a native speaker, not as a word-for-word translation | Flag stiff or confusing phrasing, not only errors |
| 3 | **Terms:** the term list ([wiki-terms.md](wiki-terms.md)) is followed, and the same English term is always translated the same way | If a term in the list is a poor choice, say so with a better one |
| 4 | **Kept in English:** commands, file names, JSON keys, secret names, scope names, and the workflow's messages in backticks are unchanged | A translated message would no longer match what the workflow prints |
| 5 | **Register:** a clear, professional tone for DevOps and software engineers; consistent use of "you" form | Danish: du; Bahasa Malaysia: neutral, no slang |
| 6 | **Spelling, grammar, punctuation:** including compounds (Danish) and affixes (Bahasa Malaysia) | |
| 7 | **Headings and links:** headings are understandable; links go to the page in the same language | A link to an English page from a translated page is a defect |
| 8 | **Tables:** headers and cells are translated; the number of rows equals the English table | An automatic test already checks the row count |
| 9 | **Numbers, dates, units:** unchanged where they are technical (for example `03:17 UTC`, `HTTP 401`) | |
| 10 | **Not misleading:** nothing would make a reader take a wrong action (wrong secret, wrong scope, skipping a check) | A finding here is a blocker |

## Judgement calls to look at first

These are the choices where the draft is least certain.

| Topic | Danish draft | Bahasa Malaysia draft | Question |
| --- | --- | --- | --- |
| secret (a stored credential) | `secret` | `rahsia (secret)` | Is the English word clearer to your readers, or the local word? |
| mirror, push mirror | `spejl`, `push-spejl` | `cermin`, `push mirror` | Does the term read as the Gitea feature? |
| workflow | `workflow` | `aliran kerja (workflow)` | Keep the English word, or the local term only? |
| repository | `repository` | `repositori` | Which one do engineers actually use? |
| use case | `use case` | `kes guna (use case)` | Is `kes guna` understood, or is `use case` better? |
| preflight check | `forhåndskontrol (preflight)` | `semakan awal (preflight)` | Does the explanation help, or is it noise? |
| least privilege | `mindste rettigheder` | `keistimewaan paling minimum` | Is this the term security staff use? |
| rotate a token | `Udskiftning af et token` | `Menukar token` | Does it say "replace with a new one"? |

Bahasa Malaysia is the weaker draft; please read it more critically.

## Findings

One row per finding. Quote the current text and give your proposed text.

| # | Page | Section or line | Current text | Proposed text | Why | Severity |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | | | | | | Blocker / Fix / Suggestion |

Severity: **Blocker** changes the meaning or could mislead; **Fix** is a
mistake that should be corrected; **Suggestion** is a style preference.

## Outcome

| Language | Reviewer (name) | Date | Result |
| --- | --- | --- | --- |
| Danish | | | Go / Go with fixes / No-Go |
| Bahasa Malaysia | | | Go / Go with fixes / No-Go |

## After the review

1. Send the filled findings table and the outcome to S01.
2. Fixes are made in the `wiki/*.da.md` and `wiki/*.ms.md` files through a
   pull request; the first line of each translation (the source hash) stays
   as it is unless the English page changed.
3. The pull request lists the wiki pages it changes (rule 8 of `AGENTS.md`).
4. When both languages are Go, issue #36 is closed and MIL-005 can be closed.
