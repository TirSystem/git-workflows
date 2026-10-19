# ADR-0012: How a comment is judged not to be English

## Metadata
| Key | Value |
| --- | --- |
| ID | ADR-0012 |
| CrossReference | [MIL-013], [ADR-0005], [ADR-0010] |

## Version History
| Date | Status | Author | Reviewer | Change | Commit |
| --- | --- | --- | --- | --- | --- |
| 2026-10-19 | Proposed | Jens Tirsvad Nielsen | S01 | Initial version | pending |

Allowed Status values: `Proposed`, `Accepted`, `Rejected`, `Deprecated`, `Superseded by ADR-NNNN`.

---

## Context

[MIL-013] adds a check that fails a pull request when a comment in its source code is not written in English. A comment is short (most have three to twelve words), is full of identifiers, paths and option names, and Danish and Malay words are often close to English ones. The method has to be offline (no source text leaves the instance, criterion 6 of the milestone), small enough to install on every run, deterministic (the same comment gives the same answer on every run), and measured on a corpus, not chosen by taste (criterion 1: recall at least 90 % for Danish and Malay, at most one false positive per 200 English comments).

**Corpus** (`tests/fixtures/comments/`): 300 English comments taken from this repository (`english.tsv`: comments and first docstring lines of `tools/`, `tests/`, `actions/` and the workflows, including fragments, paths and option names), and 138 comments in other languages written for the purpose (`foreign.tsv`): 45 Danish, 45 Bahasa Malaysia, and 12 each of German, Swedish, Norwegian and French. The foreign comments are written by the AI, not collected from real code (the TirSystem repositories have none) and not checked by a native reader. They are typical code comments of three to fifteen words, some with identifiers.

**Methods compared** (`tests/fixtures/comments/compare_detectors.py`; Python 3.13):

1. A rule-based one: letters outside English (`æ ø å ä ö ü ß é ...`) and word lists for English, Danish, Malay and others.
2. `langdetect` 1.0.9, a port of Google's detector (random start unless the seed is fixed).
3. `langid` 1.1.6, restricted to the candidate languages (`en da no sv de fr ms id nl`).
4. `lingua-language-detector` 2.2.0, restricted to the same candidates.

**Results** on the corpus, as the number of comments flagged as not English:

| Method | Danish | Malay | Other (48) | English flagged (of 300) | Install size | Time per 438 comments |
| --- | --- | --- | --- | --- | --- | --- |
| Rule-based (word lists written after the corpus, so optimistic) | 42/45 | 26/45 | 39/48 | 0 | none | 0.01 s |
| `langdetect`, probability at least 0.8 | 41/45 | 42/45 | 47/48 | 14 | 1 MB | 1.45 s |
| `langid`, no threshold | 45/45 | 45/45 | 48/48 | 2 | 2 MB and `numpy` | 0.02 s |
| `lingua`, confidence at least 0.5 | 29/45 | 41/45 | 47/48 | 0 | 170 MB wheel | 0.14 s |

Lowering the `lingua` threshold trades one error for the other: at 0.4 it flags 36/45 Danish and 2 English, at 0.2 it flags all Danish and Malay and 14 English. Raising the `langid` threshold on its normalised probability does the same (`0.5`: one English comment flagged; `0.6`: none).

The two English comments `langid` flagged without a threshold are lines that are mostly a script name and an option (`connect-tailscale.sh mask print ::add-mask:: for every secret input`). A pre-filter that removes tokens that are not words (paths, options, `::` tokens, tokens with digits or underscores, camelCase) and refuses to judge fewer than three words lowers the language signal of such lines, but it made the result worse at a threshold of 0.5 (three English comments flagged), so the threshold and the pre-filter go together:

| `langid` with the pre-filter | Danish | Malay | Other (48) | English flagged | English not judged (under 3 words) |
| --- | --- | --- | --- | --- | --- |
| probability at least 0.5, 3 words | 45/45 | 45/45 | 48/48 | 3 | 35 of 300 |
| probability at least 0.6, 3 words | 44/45 | 41/45 | 48/48 | 0 | 35 of 300 |

## Decision

A comment is judged **not English** when `langid` 1.1.6, restricted to `en da no sv de fr ms id nl`, with normalised probabilities, ranks a language other than English first with a probability of at least **0.6**, after this pre-filter, and only when the filter leaves **at least three words**:

- remove URLs and tokens that contain `/`, `\`, `::`, `_` or a digit, and camelCase tokens; split the rest on `-`;
- keep a token only if it is letters, with at most one inner apostrophe (letters include `æ ø å ä ö ü` and the other letters of Latin scripts);
- a comment with fewer than three words left is **not judged** (it passes), and so is a comment that holds only identifiers, URLs or numbers.

On the corpus this gives 0 false positives in 300 English comments, Danish 44/45 (97.8 %), Malay 41/45 (91.1 %), and 48/48 for the other languages, meeting criterion 1 of [MIL-013]. The threshold, the minimum of three words and the candidate languages are inputs of the workflow with these values as defaults; the rates are a test that fails when the code changes them (task 7).

The versions are pinned (`langid==1.1.6`, `numpy` at a pinned version) and installed in the job's virtual environment like the other tools ([ADR-0005]). Nothing is downloaded at run time and nothing is sent to a service.

## Consequences

**Positive:**

- Offline, deterministic, about 2 MB plus `numpy`, 0.06 s per 1 000 comments; no model download.
- The cases that matter most for TirSystem (Danish and Malay) are caught at or above the milestone's bar, and the rule is explainable to an author: "these words look Danish".

**Negative:**

- **The rates are an estimate, not a guarantee.** The foreign comments were written by the AI and are not checked by a native reader, the threshold and the filter were chosen on the same corpus they are measured on, and the English comments come from one repository. Real Danish and Malay comments will differ; the corpus must grow with every miss or false positive found in use (the allowed-words file and the exception marker of the workflow are the answer to a false positive in the meantime).
- Malay recall of 91.1 % leaves little margin over the bar of 90 %; short Malay comments and comments with many English technical terms are the cases it misses.
- A short comment (under three words after the filter) is never judged, so a Danish "TODO: ret" passes. This is the price of a low false positive rate.
- `langid` is not actively developed (its last release is 1.1.6). It is pinned, and `lingua` is the recorded alternative (better on long text, much larger, and weaker on short Danish at a comparable false positive rate).
- The method judges the language of words, not the quality of English: a comment in poor English passes.

## Affected Artifacts

- [MIL-013] — the decision behind tasks 3, 4 and 7, and criterion 1.
- [ADR-0005] — the tools are pinned and installed in the job's environment, like the quality-check tools.
- [ADR-0010] — the comment scanner of the code counter is reused to extract the comments.

---

[MIL-013]: ../milestones/mil-013-english-comments-check.md
[ADR-0005]: ./adr-0005-quality-check-contract.md
[ADR-0010]: ./adr-0010-code-metrics-badges-contract.md
