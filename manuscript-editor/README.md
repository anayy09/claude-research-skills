# manuscript-editor

> Keeps manuscripts coherent through revision: right content in the right document, minimal changes, whole-paper consistency.

[![Version](https://img.shields.io/badge/version-1.1.0-6E56CF)](../CHANGELOG.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../LICENSE)

Part of **[claude-research-skills](../)** · by [@anayy09](https://github.com/anayy09)

## What it does

A paper that has been through several review rounds is often worse written
than the first submission, even though every individual change was
justified: reviewer explanations leak into the text ("as suggested by
Reviewer 2, we have now added"), points get restated where the reviewer
looked instead of where they belong, every comment becomes a paragraph, and
the result reads as a record of peer review rather than as a research
article.

This skill is the editorial discipline that prevents that. It gives the
agent:

- **A paragraph-level editorial read** as the actual check: three questions
  per paragraph (its one job, is this the first home, does it connect to the
  last paragraph), three running indexes (claims, justifications,
  summaries), an outline test per section, a citation job test, and an
  editorial report with a prioritized cut list delivered before any cut is
  made.
- **Six families of non-manuscript text**, five of which never mention a
  reviewer: review-process narration, editorial self-commentary ("we would
  rather say so than bank the pass"), protocol refrain ("declared before the
  first run" at every result), reader management ("must not be read as"),
  internal workflow artifacts (decision ids, plan vocabulary, repo paths),
  and pre-emptive objection sections.
- **Three containers with a hard boundary.** Manuscript (the science as it
  now stands, for readers who never saw the review), response to reviewers
  (what changed, where, why), and a revision ledger (decisions, terminology,
  deferred items). A leak catalog with before/after pairs by section shows
  what moves where.
- **A revision-round workflow.** Parse and audit, triage comments into
  atomic items with a change type (response only, edit in place, insert,
  new paragraph, supplementary, declined, needs author input), locate the
  single home for each point before writing, make the smallest complete
  change, record it, then run a whole-manuscript coherence pass and assemble
  the package.
- **Redundancy and length rules.** One home per point, add only what is
  absent, justify design not existence, one limitation stated once, no
  end-of-section recaps, growth must be traceable to an item.
- **Integrity rules.** No invented evidence, references, or justifications;
  `[AUTHOR INPUT: ...]` placeholders where the author must decide; claims at
  the strength the evidence supports, identical everywhere they appear.
- **Venue conventions, general vs. local.** Principles that hold across Q1
  venues, then the Nature, Nature Portfolio, Nature Communications, Science,
  Cell Press, medical journal, Elsevier, IEEE, ACM, ML conference, and
  Springer/PLOS families, article-type modifiers, and reporting guidelines
  by study type.
- **A stdlib-only audit script** (`audit_manuscript.py`) for `.md`, `.tex`,
  `.docx`, `.txt`: outline with word counts, all six families above,
  recurring distinctive phrases (one argument in several homes), summary
  paragraphs, near-duplicate sentences, terminology variants, acronym
  problems, display-item order and orphans, captions that argue, citation
  density and once-only references, limitations length, hedge density,
  abstract/body number mismatches, open placeholders. It points the read
  at trouble; it does not replace it.

## When Claude uses it

- "Revise the paper according to the reviewer comments"
- "Address Reviewer 2's point about X"
- "Draft the response to reviewers"
- "This is the third revision and it reads like a patchwork"
- "Does this belong in the paper or just the response letter?"
- "Check the manuscript for repetition and inconsistencies"
- "Structure a Nature Communications article from these results"
- Any resubmission, camera-ready, or multi-round revision

Hands off elsewhere: [`research-paper-writing`](../research-paper-writing)
for the sentences themselves (argument, tone, honesty at paragraph level),
[`submission-reviewer`](../submission-reviewer) to score the science,
[`submission-formatter`](../submission-formatter) for templates and marked
copies, [`journal-advisor`](../journal-advisor) to choose the venue,
[`ml-eval-statistics`](../ml-eval-statistics) and
[`manuscript-figures`](../manuscript-figures) when a reviewer request needs
new numbers or artwork.

## What's inside

```
manuscript-editor/
├── SKILL.md
├── references/
│   ├── editorial-read.md          paragraph-level read: three questions, three indexes, section tests, cut decisions
│   ├── manuscript-boundary.md     three containers, families A to F with before/after pairs, repair procedure
│   ├── coherence-audit.md         reading the audit, the whole-manuscript pass, the four mirrors, decision rules
│   ├── journal-conventions.md     general principles vs. venue families, section rules, reporting guidelines
│   └── response-to-reviewers.md   structure, per-item template, disagreement, consistency check
├── assets/
│   ├── revision-ledger.md         internal ledger template
│   ├── response-template.md       response letter template
│   └── editorial-report.md        editorial report template (indexes, cut list, projected lengths)
└── scripts/
    └── audit_manuscript.py        stdlib-only mechanical audit (md/tex/docx/txt)
```

## Scripts

```bash
# before the round: outline, the six families, recurring phrases, citations
python manuscript-editor/scripts/audit_manuscript.py paper.md --report audit_before.md

# after the round: compare section word counts against audit_before
python manuscript-editor/scripts/audit_manuscript.py paper.md --report audit_after.md

# submission gate: exit 1 if any revision-commentary leak remains
python manuscript-editor/scripts/audit_manuscript.py paper.md --strict

# machine-readable, for a hook or CI step
python manuscript-editor/scripts/audit_manuscript.py paper.docx --json > audit.json
```

Standard library only, and pattern-based by design: it finds what a regular
expression can find and says so. It reports candidates; the editorial read in
`references/editorial-read.md` decides. Contradictions, claim-strength drift,
and citation relevance are not detectable here.

## Changelog

- **1.1.0**: The check is now a paragraph-level editorial read, with the script
  as its instrument rather than its substitute. Adds five families of
  non-manuscript text that never mention a reviewer (editorial self-commentary,
  protocol refrain, reader management, internal workflow artifacts, pre-emptive
  objections), ten new detectors including recurring distinctive phrases and
  summary paragraphs, rules for citation jobs, continuity, captions, and the
  summary budget, plus `references/editorial-read.md` and an editorial-report
  template. Section detection no longer splits a bibliography into sections or
  reads a PDF axis label as a heading.
- **1.0.0**: Initial release.

---

Part of the **[claude-research-skills](../)** collection.
[Report an issue »](https://github.com/anayy09/claude-research-skills/issues/new/choose)
