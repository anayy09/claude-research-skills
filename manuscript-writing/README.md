# manuscript-writing

> Scholarly prose that reads like a working researcher wrote it, with the tell sweep built in.

[![Version](https://img.shields.io/badge/version-4.0.0-6E56CF)](../CHANGELOG.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../LICENSE)

Part of **[claude-research-skills](../)** · by [@anayy09](https://github.com/anayy09)

## What it does

Writes, rewrites, edits, and extends academic research prose that reads as if a
working researcher wrote it, not a language model. It handles full paper
sections (introduction, related work, method, results, discussion,
conclusion), thesis chapters, rebuttals and response letters, conference and
journal submissions, and technical reports. It is for scholarly writing
specifically, and deliberately not for casual summaries, blog posts, marketing
copy, slide text, or code.

The skill puts substance first: a real claim per paragraph, confidence that
matches the evidence, prior work cited by what it did, decisions explained
rather than listed. It then ends with a **tell sweep**, the manuscript subset
of `prose-naturalizer`'s patterns ordered by how much one sighting justifies
an edit: no dashes, no revision narration, no chatbot residue as hard rules;
not-X-but-Y, one-line closers, announcing, arguing with no one on one
sighting; triads, stock vocabulary, repeated openers, hedge stacks, bold
labels, inflated significance when several share a passage. A stdlib script
counts them per section so the sweep reads flagged places instead of the
whole draft again.

It also carries the identity rule: author names, affiliations, emails,
ORCIDs, funding, and ethics text come only from the user or a project file,
never from session context, with `[AUTHOR INPUT: ...]` where a value is
missing.

## When Claude uses it

- "Write the related work / introduction / discussion"
- "Tighten this paragraph" / "help me phrase this contribution"
- "Make this sound less like AI wrote it" / "remove the em dashes" / "there
  are AI-like sentences in the manuscript"
- Drafting a rebuttal or response-to-reviewers letter
- A final sweep before submission

> **Pairs with** [`manuscript-editor`](../manuscript-editor) for any revision
> round, resubmission, or whole-manuscript check: it decides what belongs in
> the paper versus the response letter and how much to change, then calls
> this skill for the sentences. [`investigating-sources`](../investigating-sources)
> keeps every citation honest. [`prose-naturalizer`](../prose-naturalizer) is
> for non-academic prose; a manuscript never needs both loaded.

## What's inside

```
manuscript-writing/
├── SKILL.md                 the drafting and editing playbook, ending in the tell sweep
└── scripts/
    └── prose_lint.py        per-section counts: dashes, stock words, contrasts, triads, openers,
                             labels, announcing, closers, hedge stacks, residue, revision narration
```

## Scripts

```bash
python manuscript-writing/scripts/prose_lint.py paper.md --report lint.md
python manuscript-writing/scripts/prose_lint.py sections/*.md
python manuscript-writing/scripts/prose_lint.py main.tex --strict        # exit 1 on a dash, residue, or narration
python manuscript-writing/scripts/prose_lint.py paper.md --allow-dashes  # the author's own style uses them
python manuscript-writing/scripts/prose_lint.py --self-test
```

Standard library only. Reads `.md`, `.tex`, and `.txt`; strips code, math,
tables, citations, comments, and LaTeX commands before counting, so a `--` in
a table or a `\cite{a--b}` key is not a dash.

## Changelog

- **4.0.0**: Renamed from `research-paper-writing` to `manuscript-writing`, matching `manuscript-editor` and `manuscript-figures` (breaking: the folder and name changed; `/research-paper-writing` no longer resolves). No pattern changed. Adds the loading-discipline section.
- **3.0.0**: Absorbs the manuscript subset of `prose-naturalizer` (behavior
  change: the skill now ends with a tell sweep and treats em and en dashes,
  revision narration, and chatbot residue as hard rules). Adds the identity
  and metadata rule, a note that a response letter is a list of answers and
  not an essay, and `scripts/prose_lint.py`. The description now names the
  prompts that used to bypass the skill ("remove the em dashes", "AI-like
  sentences") and says not to load `prose-naturalizer` for a manuscript.
- **2.1.0**: Draws the line against `manuscript-editor`. A scope section says
  this skill owns the prose and not placement, scope of change, or
  whole-manuscript coherence; the rebuttal section states that the account of
  what changed lives only in the response letter, never in the revised
  manuscript; and rewriting now starts by checking whether the manuscript
  already makes the point somewhere else.
- **2.0.1**: Hand off to `manuscript-figures` for the figure a results paragraph
  cites, and to `ml-eval-statistics` when a claimed gap still needs an interval.
- **2.0.0**: Current release.

---

Part of the **[claude-research-skills](../)** collection.
[Report an issue »](https://github.com/anayy09/claude-research-skills/issues/new/choose)
