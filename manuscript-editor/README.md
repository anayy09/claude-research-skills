# manuscript-editor

> Keeps manuscripts coherent through revision: right content in the right document, minimal changes, whole-paper consistency.

[![Version](https://img.shields.io/badge/version-1.0.0-6E56CF)](../CHANGELOG.md)
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
  `.docx`, `.txt`: outline with word counts, revision-commentary leaks,
  near-duplicate sentences, terminology variants, acronym problems,
  display-item order and orphans, hedge density, abstract/body number
  mismatches, open placeholders. Run before and after each round.

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
│   ├── manuscript-boundary.md     three containers, leak catalog, before/after by section, repair procedure
│   ├── coherence-audit.md         reading the audit, the manual pass, the four mirrors, decision rules
│   ├── journal-conventions.md     general principles vs. venue families, section rules, reporting guidelines
│   └── response-to-reviewers.md   structure, per-item template, disagreement, consistency check
├── assets/
│   ├── revision-ledger.md         internal ledger template
│   └── response-template.md       response letter template
└── scripts/
    └── audit_manuscript.py        stdlib-only mechanical audit (md/tex/docx/txt)
```

## Scripts

```bash
# before the round: outline, leaks, duplicates, terminology, placeholders
python manuscript-editor/scripts/audit_manuscript.py paper.md --report audit_before.md

# after the round: compare section word counts against audit_before
python manuscript-editor/scripts/audit_manuscript.py paper.md --report audit_after.md

# submission gate: exit 1 if any revision-commentary leak remains
python manuscript-editor/scripts/audit_manuscript.py paper.md --strict

# machine-readable, for a hook or CI step
python manuscript-editor/scripts/audit_manuscript.py paper.docx --json > audit.json
```

Standard library only, and pattern-based by design: it finds what a regular
expression can find and says so. Contradictions, claim-strength drift, and
semantic duplication are the manual pass in `references/coherence-audit.md`.

## Changelog

- **1.0.0**: Initial release.

---

Part of the **[claude-research-skills](../)** collection.
[Report an issue »](https://github.com/anayy09/claude-research-skills/issues/new/choose)
