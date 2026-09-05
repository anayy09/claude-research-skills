---
name: manuscript-editor
description: >-
  Manuscript-level editorial discipline for research papers at the standard
  of reputable Q1 journals: what belongs in the manuscript versus the response
  to reviewers versus internal notes, how to make the smallest complete
  change, and how to keep a paper coherent across many revision rounds
  instead of letting it decay into patches. Use whenever the user is revising
  a paper after peer review, addressing reviewer or editor comments,
  integrating a batch of edits, drafting a response-to-reviewers letter,
  preparing a resubmission or camera-ready, asking whether something belongs
  in the paper, saying the manuscript reads like patches, repeats itself, or
  has grown too long, or wanting a whole-manuscript consistency, redundancy,
  or structure check. Also use when drafting a full manuscript so structure
  and section content match the target venue and article type. Pairs with
  research-paper-writing, which owns sentence and paragraph quality.
summary: "Keeps manuscripts coherent through revision: right content in the right document, minimal changes, whole-paper consistency."
version: "1.0.0"
author: anayy09
license: MIT
metadata:
  status: active
  last_updated: "2026-09-05"
---

# Manuscript Editor

A manuscript that has been through three rounds of review is often worse
written than the first submission, even though every individual change was
justified. Each reviewer comment became a paragraph. Each paragraph explained
why it existed. Points got restated where the reviewer happened to look
instead of where they belong. Terminology drifted. The result reads as a
record of the review process rather than as a research article.

This skill is the discipline that prevents that. It treats the manuscript as
one artifact with one author voice, and it treats everything about the
editing process as belonging somewhere else. It does not replace
`research-paper-writing`; that skill makes each paragraph argue well. This
one decides what goes where, how much to change, and whether the whole still
holds together afterwards.

## Scope, and what belongs elsewhere

This skill owns placement, scope of change, coherence, and the boundary
between manuscript and revision commentary. It does not:

- Rewrite prose for argument, tone, or AI-sounding register. That is
  `research-paper-writing`; read it alongside this skill for any change that
  produces new sentences.
- Score or review the science. `submission-reviewer`.
- Typeset into a venue template or verify format compliance.
  `submission-formatter`, which also owns the marked-copy build once the
  content is final.
- Pick the venue. `journal-advisor`.
- Compute statistics or produce figures a reviewer asked for.
  `ml-eval-statistics`, `manuscript-figures`. When a reviewer request needs
  new numbers, get them there first, then come back here to place them.
- Run a literature search to fill a related-work gap. `evidence-synthesis`
  or `investigating-sources`; this skill only decides where the result goes.

## The three containers

Every sentence produced during revision lands in exactly one of these.

| Container | Reader | Content | Voice |
|---|---|---|---|
| **Manuscript** | Anyone who never saw the review | The science as it now stands: rationale, method, results, interpretation, limitations | Author writing a paper for the first time |
| **Response to reviewers** | Editor and reviewers | What changed, where, why, and any disagreement | Author replying to a colleague |
| **Revision ledger** (internal) | Future you, co-authors | Decisions, standing choices, deferred items, open placeholders | Notes |

The test for any sentence: would it make sense, and be worth printing, to a
reader who has never seen the reviews? If not, it is not manuscript text. A
change can be prompted by a reviewer; the resulting text presents the science
as if the author had always intended to say it that way. "We now report the
integrated calibration index" belongs in the response; "Calibration was
assessed with the integrated calibration index" belongs in Methods. The full
leak catalog with before/after pairs is in `references/manuscript-boundary.md`.

Three things that legitimately stay in the manuscript even when a reviewer
caused them: scientific rationale for a design choice, methodological
justification a reader in the field would expect, and limitations. These are
part of the science. Defensive framing around them is not.

## Modes

Identify which one applies before starting; each has a different entry point.

- **Revision round.** Reviewer or editor comments plus an existing
  manuscript. Follow the full workflow below.
- **Editorial pass.** An existing draft, no external comments, and a request
  to tighten, check consistency, or remove patchiness. Skip triage; run
  steps 1, 6, and 7.
- **Initial drafting.** Writing a manuscript or a section from results and
  notes. Read `references/journal-conventions.md` for the venue, build the
  section plan, then write with `research-paper-writing`. Start the ledger on
  day one so terminology and standing decisions are recorded before the
  first review.
- **Response letter only.** The manuscript is already revised and the user
  wants the response document. Use `references/response-to-reviewers.md` and
  the ledger; do not touch the manuscript except to fix mismatches between
  what the letter claims and what the paper says.

## Workflow for a revision round

### 1. Parse and inventory before touching anything

Read the whole manuscript once. Then run the audit so the mechanical picture
is on the table before editing starts:

```bash
python scripts/audit_manuscript.py paper.md --report audit_before.md
```

It reports the outline with word counts, revision-commentary leaks already
present, near-duplicate sentences, terminology variants, acronym problems,
display-item references, hedge density, abstract/body number mismatches, and
open placeholders. Accepts `.md`, `.tex`, `.docx`, `.txt`. Read
`references/coherence-audit.md` for how to interpret it and what it cannot see.

Load the revision ledger if one exists; otherwise create it from
`assets/revision-ledger.md`. Record the venue, article type, word budget,
voice, and canonical terminology now. In later rounds the ledger is what stops
a decision from round 1 being silently reversed in round 3 because nobody
remembered why it was made.

### 2. Triage the comments into atomic items

Split every reviewer and editor comment into single-issue items with ids
(R1.1, R1.2, R2.1, E.1). A comment that says "the methods are unclear and the
baseline is weak" is two items. For each item decide the change type before
writing anything:

| Change type | When | Manuscript effect |
|---|---|---|
| Response only | Misreading, or the point is already in the paper | None; quote the existing passage in the response |
| Edit in place | The point exists but is unclear, incomplete, or wrong | Revise the existing sentence or paragraph |
| Insert | The point is absent and fits an existing paragraph | One to three sentences, in the paragraph that owns the topic |
| New paragraph or subsection | The point is absent and is a distinct unit of the argument | Placed where the structure calls for it, not where the reviewer looked |
| Supplementary | Detail a reader needs for reproduction but not for the argument | Supplement, with a one-line pointer in the main text |
| Declined | The request would weaken the paper or is out of scope | Response with reasons; ledger records the decision |
| Needs author input | Requires data, results, or a decision only the author has | Placeholder in the manuscript, item flagged in ledger and response |

Most items are "response only" or "edit in place". A revision round in which
every item became an insertion is the failure mode this skill exists to stop.

### 3. Locate before writing

For each item that touches the manuscript, search the whole text for every
passage that already addresses the topic (the audit's duplicate and
terminology sections help; so does a plain search on the key terms). Decide
the single home for the point. If two passages both half-say it, merge them
into the home and remove the other. Then read the paragraph before and after
the home so the change is written into the flow rather than dropped in.

### 4. Make the smallest complete change

Write the new text as if it had always been there. Concretely:

- No revision markers: no "now", "newly", "in the revised version", no
  reviewer attribution, no "we agree", no page or line references.
- Register and tense match the section (Methods past tense, Results past
  tense, Discussion present tense for interpretation, or whatever the
  manuscript already uses).
- If the change adds a claim, it comes with its evidence or a placeholder.
  Never invent a number, a reference, a result, or a justification to satisfy
  a comment. Placeholder convention: `[AUTHOR INPUT: what is needed and why]`.
  The audit script counts these, so none can be forgotten at submission.
- Expansion is allowed when the science needs it: a missing ablation, a
  method step a reader could not reproduce without, a limitation that was
  absent. It is not allowed as reassurance. A reviewer asking "why did you
  choose X" usually needs one sentence of rationale in Methods, not a
  paragraph defending X.
- Keep claim strength proportional to evidence. Do not strengthen a claim
  because a reviewer was enthusiastic or hedge it into vagueness because one
  was hostile. If the evidence changed, the claim changes to match.

Apply `research-paper-writing` to the sentences themselves.

### 5. Record every decision in the ledger

One row per item: id, comment in a few words, change type, location in the
manuscript, one line on what changed, and the reason if declined or deferred.
Add standing decisions (canonical term choices, a section that was
deliberately cut, a comparison deliberately not added) to the standing
decisions list so the next round inherits them.

### 6. Coherence pass on the whole manuscript

After the batch, not after each item. Re-run the audit:

```bash
python scripts/audit_manuscript.py paper.md --report audit_after.md
```

Then do the manual pass in `references/coherence-audit.md`. The parts the
script cannot do and that matter most:

- Contradictions: a number or claim changed in one place and not another.
  Abstract, Introduction contributions, Results, Discussion, and Conclusion
  must agree on every headline number and every claim's strength.
- Semantic duplication: the same point made in different words in two
  sections. Keep one, and keep it where it does the most work.
- Transitions: a paragraph inserted in round 2 may leave the paragraph after
  it opening with "However" against nothing, or referring to "this" with a
  moved antecedent.
- Structure: does the section still have one job? A Methods paragraph that
  now discusses results because a reviewer asked "what happens if" needs
  splitting.
- Length: compare `audit_before` and `audit_after` word counts per section.
  Growth should be traceable to specific items that needed it.

Fix what the pass finds. This is where most of the quality of a revised
manuscript comes from, and it is the step that gets skipped under deadline.

### 7. Assemble the package

Deliver, in this order:

1. The clean revised manuscript.
2. The response to reviewers, built from the ledger, following
   `references/response-to-reviewers.md`. Every "we changed X, see Section Y"
   in the letter must be true of the clean manuscript; check each one.
3. The updated ledger.
4. A short change summary for the user: items by change type, sections whose
   length changed and why, open placeholders, declined items.

Marked-up copies (tracked changes or highlighted text) are a venue
requirement, not an editorial one; hand off to `submission-formatter` for
that once content is final.

## Redundancy and length rules

These apply in every mode, including initial drafting.

- **One home per point.** A fact, justification, or limitation appears once
  in the main text, in the section whose job it is. The abstract restates
  headline results by design; that is the only sanctioned duplication.
- **Add only what is absent.** Before writing a sentence, check that the
  manuscript does not already say it. If it does and the reviewer missed it,
  the fix is a clearer sentence or a better location, not a second sentence.
- **Justify design, not existence.** Explain why a method choice was made in
  the terms a reader needs to reproduce or evaluate it. Do not explain why
  the paper is valid, why a section is present, or why the authors are
  confident.
- **Caveat budget.** One limitation gets one clear statement in the
  Discussion, with its mechanism if known. Hedges scattered through Results
  to pre-empt criticism are cut. If a caveat is real, it belongs in the
  limitations paragraph; if it is not, it goes.
- **No summaries of what was just said.** End-of-section recaps,
  "in summary" sentences inside a section, and Conclusion paragraphs that
  restate the Discussion are removed. The Conclusion states what was shown
  and what it means, in a form shorter than the Discussion.
- **Background lives in the Introduction.** Discussion paragraphs that
  re-explain why the problem matters are cut. Discussion positions the
  result against prior work, which is different.
- **Growth must be earned.** A round that adds more than about 10 percent to
  a section needs a reason in the ledger.

## Short examples

Each pair shows text that leaked into a manuscript and the form it should
take. More, organized by section, in `references/manuscript-boundary.md`.

**Reviewer attribution in Methods.**
Before: As suggested by Reviewer 2, we have now added a sensitivity analysis
excluding stays with missing lactate.
After: A sensitivity analysis excluded stays with missing lactate
measurements.
Response letter gets: "We added a sensitivity analysis excluding stays with
missing lactate (Methods, Sensitivity analyses; Results, Table S3)."

**Defensive justification in Discussion.**
Before: To address concerns about generalizability, we emphasize that
external validation on an independent cohort is a major strength of this
study and supports the robustness of our findings.
After: Performance on the external cohort was 0.05 lower than internally,
which is within the range reported for other vital-sign models transferred
between sites [refs].
The reviewer's concern is answered by the number and the comparison, not by
the word "strength".

**Narrated change in Results.**
Before: In the revised analysis we also report the integrated calibration
index, which confirms that the model is well calibrated overall.
After: Integrated calibration index was 0.021 (internal) and 0.048 (external).
Interpretation of "well calibrated" goes to Discussion, once.

**Restated background in Discussion.**
Before: Sepsis is a leading cause of in-hospital mortality, and early
identification is important because delayed treatment increases mortality.
Our model achieved an external AUROC of 0.81.
After: (delete the first sentence; it is in the Introduction) An external
AUROC of 0.81 places the model with the better-performing published
approaches, but the calibration drift in older patients means the operating
threshold would need to be reset per site.

**Hedge stacking after a critical review.**
Before: Note that this may potentially be due to differences in case mix,
although it could possibly also reflect labeling differences, and it might
perhaps be related to sampling frequency.
After: The most likely cause is case-mix difference: the external cohort had
a higher proportion of surgical admissions (Table 1). Labeling and sampling
frequency differed as well and cannot be excluded.

**Missing evidence.**
Before: Our method also generalizes to pediatric populations.
After: `[AUTHOR INPUT: Reviewer 1 asked about pediatric generalization. No
pediatric cohort was evaluated. Either supply results or we state this as a
limitation.]`
Then, once the author decides: either a result with numbers or one sentence
in limitations. Never an unsupported claim.

## Journal and article-type conventions

Q1 venues share a core of structural expectations and differ in specifics.
`references/journal-conventions.md` separates the two: general principles
that hold across Nature, Science, Cell, Lancet, IEEE, ACM, Elsevier, and
Springer titles, and then the venue-family conventions (Nature summary
paragraph and Methods placement, Cell STAR Methods and highlights, medical
journals' structured abstracts and reporting guidelines, IEEE index terms and
contribution lists, ML conference limitations sections). It also gives the
section-by-section content rules and how to derive conventions for an
unfamiliar venue from its recent published articles. Consult it in initial
drafting mode and whenever a revision changes structure.

## Before returning

Confirm, without narrating the check to the user:

- Zero revision-commentary leaks in the audit, and none of the softer kinds
  the audit cannot see (a paragraph that only exists to reassure).
- Every headline number and claim agrees across abstract, contributions,
  results, discussion, conclusion.
- Every claimed change in the response letter exists in the manuscript at
  the stated location.
- Every placeholder is listed in the ledger and the change summary.
- Section lengths changed only where an item required it.
- The ledger has a row for every item and the standing decisions are
  current.

Then hand over the package. Do not describe the workflow in the reply; the
change summary is the account of what was done.
