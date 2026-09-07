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
version: "1.1.0"
author: anayy09
license: MIT
metadata:
  status: active
  last_updated: "2026-09-06"
---

# Manuscript Editor

A manuscript that has been through three rounds of review is often worse
written than the first submission, even though every individual change was
justified. Each reviewer comment became a paragraph. Each paragraph explained
why it existed. Points got restated where the reviewer happened to look
instead of where they belong. Terminology drifted. The result reads as a
record of the review process rather than as a research article.

The same decay happens without any reviewer. A careful author who has
pre-registered a study and is anxious to be seen as honest produces a
different patchwork: every design choice is defended at the point of use,
every number is followed by a sentence announcing that it was declared in
advance, the same headline is restated in six places, the Introduction
grows a literature review that cites everything the search returned, and the
Discussion acquires an "Objections" section. Nothing in it is reviewer-facing
and all of it is non-manuscript text.

This skill is the discipline that prevents both. It treats the manuscript as
one artifact with one author voice, and it treats everything about the
editing process, the authors' own conduct, and the reader's presumed
suspicions as belonging somewhere else. The check is a paragraph-by-paragraph
editorial read (`references/editorial-read.md`); the audit script is an
instrument that points the read at likely trouble, not a substitute for it.
This skill does not replace `research-paper-writing`; that skill makes each
paragraph argue well. This one decides what goes where, how much to say, how
often, and whether the whole still holds together afterwards.

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

## Six families of non-manuscript text

Reviewer-facing language is the most obvious family and the least common in
a well-run draft. The other five do most of the damage and none of them
mentions a reviewer. Full catalog with before/after pairs in
`references/manuscript-boundary.md`; the audit script has a detector for each.

| Family | What it sounds like | Where it goes |
|---|---|---|
| A. Review-process narration | "As suggested by Reviewer 2, we have now added" | Response letter |
| B. Editorial self-commentary | "We would rather say so than bank the pass." "We report all of this because we registered it." "Worth stating rather than hiding." "Belongs here rather than in a footnote." | Nowhere; do the thing, do not announce it |
| C. Protocol refrain | "declared before the first run", "fixed in advance", "not chosen after seeing", "every number resolves to a named cell", restated at each use | Once, in Methods; once in the abstract if the venue expects it |
| D. Reader management | "This must not be read as", "a reader's first suspicion is", "no part of our argument rests on", "we are not claiming" | State the claim's scope once; the reader is not instructed |
| E. Internal workflow artifacts | Decision ids (D-050), gate names, "strengthener 10", "kill experiment", "the plan", repo paths, ledger vocabulary, shouted table notes | Repository, supplement, ledger |
| F. Pre-emptive objections | A subsection or paragraph framed as "This is just X." followed by rebuttal | Substance into Methods rationale or Limitations; frame deleted |

The common test: the sentence is about the authors, the paper, or the
reader, not about the study. A manuscript sentence is about the study.

Honesty in a manuscript is shown, not narrated. A failed pre-registered
target is reported by putting the target and the measured value in one
table and interpreting it in one paragraph. Saying five times that it was
reported because it was registered persuades no one and costs a page.

## Modes

Identify which one applies before starting; each has a different entry point.

- **Revision round.** Reviewer or editor comments plus an existing
  manuscript. Follow the full workflow below.
- **Editorial pass.** An existing draft, no external comments, and a request
  to tighten, check consistency, or remove patchiness. Run the editorial
  read and the audit, deliver the editorial report with its prioritized cut
  list (`assets/editorial-report.md`), and make the cuts only after the
  author has seen the list. Then steps 6 and 7.
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

Read the whole manuscript once as a reader, then once as an editor following
`references/editorial-read.md`: for each paragraph, what is its one job, is it
the first place that job is done, and does its opening connect to what the
previous paragraph established. Keep the three running indexes that read
produces (claims, justifications, summaries) in the ledger. Then run the
audit so the mechanical picture is on the table too:

```bash
python scripts/audit_manuscript.py paper.md --report audit_before.md
```

It reports the outline with word counts, all six families above, recurring
distinctive phrases (one argument in several homes), summary paragraphs,
near-duplicate sentences, terminology variants, acronym problems,
display-item references, captions that argue, citation density, limitations
length, abstract/body number mismatches, and open placeholders. Accepts
`.md`, `.tex`, `.docx`, `.txt`. Read `references/coherence-audit.md` for how
to interpret it and what it cannot see. The script finds candidates; the read
decides.

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

Then repeat the editorial read (`references/editorial-read.md`) on every
section that changed, and the whole-manuscript pass in
`references/coherence-audit.md`. The parts the script cannot do and that
matter most:

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
- **One home per justification.** Why a choice was made, why a feature
  cannot leak, why recalibration was out of scope: each is explained once,
  where the choice is introduced (usually Methods). Every later mention is
  the bare fact or a cross-reference, never a re-explanation. The editorial
  read builds a justification index for exactly this; the audit's
  recurring-phrase section finds the ones that have spread.
- **State the protocol once.** Pre-registration, what was fixed in advance,
  how numbers are checked: one paragraph in Methods, one clause in the
  abstract if the venue expects it. After that, the Results simply report
  and the tables mark registered items with a column. A sentence that adds
  "as declared in advance" to a result is protocol refrain.
- **Summary budget.** The paper summarizes itself at most three times
  outside the abstract: the contributions at the end of the Introduction,
  the first paragraph of the Discussion, and the Conclusion. Each is shorter
  than the last full account, adds interpretation rather than repeating
  numbers, and shares no sentence with the others. A Results subsection
  titled "Summary of outcomes" is a table, not prose. A Discussion
  subsection titled "What failed" is one paragraph, not a second Results.
- **Add only what is absent.** Before writing a sentence, check that the
  manuscript does not already say it. If it does and the reviewer missed it,
  the fix is a clearer sentence or a better location, not a second sentence.
- **Justify design, not existence.** Explain why a method choice was made in
  the terms a reader needs to reproduce or evaluate it. Do not explain why
  the paper is valid, why a section is present, why a number is reported, or
  why the authors are confident or restrained.
- **Caveat budget.** One limitation gets one clear statement in the
  Discussion, with its mechanism and its consequence for the claim, in one
  to three sentences. Hedges scattered through Results to pre-empt criticism
  are cut. A Limitations section that re-explains Methods is cut back to the
  limitation itself plus a cross-reference.
- **No summaries of what was just said.** End-of-section recaps,
  "in summary" sentences inside a section, and Conclusion paragraphs that
  restate the Discussion are removed.
- **Background lives in the Introduction.** Discussion paragraphs that
  re-explain why the problem matters are cut. Discussion positions the
  result against prior work, which is different.
- **Growth must be earned.** A round that adds more than about 10 percent to
  a section needs a reason in the ledger.

## Citations and related work

A citation has to do a job for this paper's argument. The four jobs: it
establishes the gap, it supplies a method or definition used here, it
supplies a comparator or precedent the results are read against, or it is a
direct counter-example the paper must answer. A work that merely shows the
authors have read widely does none of these and is cut. Concretely:

- Evidence about research practice in another field (recommender systems,
  numerical PDEs) gets at most one sentence and one or two citations, in the
  Introduction, if the point cannot be made with in-field evidence.
- Studies that ask a neighbouring question the paper does not answer are
  mentioned only if a reader would otherwise confuse the two; one sentence
  each, no subsection.
- The method of a literature search belongs in Methods (one paragraph) or
  the supplement, not in the Introduction. A table of every screened study
  is a supplementary table. The Introduction cites what the search found,
  not how it was run.
- Introduction and related-work text together should not exceed roughly a
  quarter of the body. When it does, the paper is reviewing a literature
  instead of reporting a study, and the venue's article type will say which
  one it is.
- A reference cited once, in the related-work section only, is the first
  candidate for removal. The audit reports these.

## Continuity

A manuscript reads as stitched when each paragraph is a self-contained
essay with an aphoristic opening ("The noise floor is a table, not a
number.") and no dependence on what came before. It reads as continuous
when each paragraph's first sentence takes something the previous paragraph
established and does the next thing with it. This is not achieved with
connectives ("Furthermore", "However") and not with aphorisms; it is
achieved by ordering the paragraphs so that each needs the last.

Test: read only the first sentence of every paragraph in a section. They
should form an outline of an argument a reader could follow without the
paragraphs. If they read as a list of independent assertions, reorder or
merge until they do. One aphoristic opener per section is a stylistic
choice; one per paragraph is a tic.

## Captions, table notes, and figure text

Captions and notes describe what is shown: what the marks are, the unit,
the sample, the interval definition, where the values come from. They do
not argue, warn, shout, or instruct ("THIS TABLE DOES NOT ORDER THE ARMS
BY DISCRIMINATION", "two things visible here are arguments the text makes",
"strengthener 10 in the plan"). If a table can be misread, the sentence
that prevents the misreading goes in the text where the table is cited,
once. Decision-log ids and pipeline provenance go in the supplement or the
repository, not in the caption.

## Short examples

One pair per family plus the two integrity cases. More, organized by
section and family, in `references/manuscript-boundary.md`.

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

**Announced restraint (family B).**
Before: This is an easy test to pass and we would rather say so than bank
the pass. Landing inside the published interval shows the reproduction is
not badly wrong; it does not show that it is precisely right.
After: The published interval is wide because six of the fifteen targets
have fewer than fifty positives in the test fold; the reproduction falls
inside it, which bounds but does not pin the reference arm.
The restraint is now in the content of the sentence, not narrated.

**Protocol refrain (family C).**
Before: The operating threshold is 0.10, fixed from the clinical framing
and recorded before any curve was computed. We declared as much before
computing any of it, precisely so that it could not be offered afterwards as
an explanation for an unflattering number.
After: The operating threshold was 0.10 (Methods, Registration). Then the
result.
One Methods paragraph says what was registered and where the registration
lives. Every later mention is a cross-reference.

**Reader management (family D).**
Before: Acquisition context does not, however, explain the waveform arm,
and this paper must not be read as saying that it does. Those are two
claims. The first survives and the second does not.
After: Acquisition context recovers most of the waveform arm's discrimination
at short horizons but does not account for it: within matched strata the
waveform arm retains 78 to 93 percent of its advantage over demographics.
The scope is in the numbers; the reader is not told how to read.

**Internal artifacts (family E).**
Before: Net benefit is strengthener 10 in the plan, the second thing cut if
the schedule slips. Every value here is a cell of Table 11 (D-065, closing
D-018).
After: (delete; the note describes the table's contents and the threshold)

**Pre-emptive objection (family F).**
Before: *Your acquisition features leak the label.* We separated the feature
blocks before fitting any model, every feature carries an availability
timestamp enforced by a test that fails on deliberately poisoned data, ...
After: (delete the subsection) The availability test is already in Methods,
Acquisition context. If a reviewer raises the leak, the response letter
points there.

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

- Zero hits in audit families A to F that were not consciously kept, and
  none of the softer kinds the audit cannot see (a paragraph that only
  exists to reassure).
- Each justification in the justification index has one home. Each
  recurring phrase the audit reports has been resolved to one home or
  accepted as terminology.
- At most three summaries outside the abstract, each shorter than the last.
- Every citation passes the job test; the Introduction plus related work is
  within the venue's proportion.
- First sentences of each section's paragraphs read as an outline.
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
