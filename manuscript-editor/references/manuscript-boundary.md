# The manuscript boundary

What belongs in the manuscript, what belongs in the response to reviewers,
what belongs in internal notes, and how to move text that ended up in the
wrong one.

Contents

1. The reader test
2. Leak catalog
3. What legitimately stays in the manuscript
4. Before/after pairs by section
5. Repair procedure for a leaked passage
6. Edge cases where the manuscript does narrate change

## 1. The reader test

The manuscript is read by people who never saw the reviews: future readers,
citers, replicators, and the next set of reviewers if the paper is
transferred. Publisher guidance is consistent that the account of what
changed goes in the response letter and, where required, a marked copy
(Springer's revision guidance: describe the revisions in the response letter
and show them with tracked changes or highlighting). The clean manuscript
carries no trace of the process.

So for each sentence ask two questions:

1. Would a reader who never saw the review understand why this sentence is
   here?
2. Is it describing the science, or describing the paper, the authors, or
   the editing history?

Manuscript sentences answer yes to the first and "the science" to the
second. Everything else moves.

## 2. Leak catalog

Recognizable forms of revision commentary that end up in manuscripts. The
audit script catches most of the first three groups by pattern; the rest
need reading.

**Attribution to the review process**
- "As suggested by / requested by / pointed out by the reviewer"
- "Reviewer 2 raised the concern that"
- "In response to the reviewers' comments"
- "Following the editor's recommendation"
- "We thank the reviewer for"

**Narration of the editing history**
- "We have now added / revised / clarified / expanded"
- "In the revised version / in this revision / in the current manuscript"
- "The previous version of this paper"
- "This section has been rewritten for clarity"
- "Newly added analysis", "now included"
- Page and line references ("see page 12, lines 4 to 9"), which belong in
  the response letter

**Agreement and concession language**
- "We agree that this is an important consideration"
- "We acknowledge the reviewer's point"
- "This is a fair criticism"
- "As the reviewer correctly notes"

**Defensive justification** (harder to spot; no reviewer is named)
- "We emphasize that external validation is a major strength of this study"
- "It is important to stress that our approach is valid because"
- "To address potential concerns about X, we note that"
- "Despite this limitation, our results remain robust and significant"
- Any sentence whose function is to reassure rather than to inform

**Meta-commentary about the paper itself**
- "In this section we clarify", "this paragraph explains"
- "As mentioned above / as discussed earlier / as noted previously"
  (usually a symptom that the point is now in two places)
- "For clarity, we restate", "to summarize the above"

**Reviewer's question pasted as rhetorical frame**
- "One might ask whether X. We address this by" when the reviewer asked
  exactly that. Occasionally acceptable as a device; a tell when it appears
  at every point a reviewer raised.

**Change markers embedded in otherwise fine text**
- "now" and "also" carrying revision meaning: "we now report", "we also
  computed the ICI". Read "now" as "in this version" and cut it; read
  "also" as "in addition to what the reviewer already saw" and cut it.

**Hedge stacking** after a critical review
- Three or more hedges in one sentence ("may potentially ... although it
  could possibly ... might perhaps")
- A caveat appended to every result sentence rather than stated once

**Redundancy created by patching**
- The same result reported in Results and restated in Discussion with the
  same numbers and no added interpretation
- Background from the Introduction repeated at the top of the Discussion
- Contribution list in the Introduction and again in the Conclusion, word
  for word
- A limitation stated in Methods, in Results, and in Discussion

## 3. What legitimately stays in the manuscript

Reviewer-caused is not the same as reviewer-facing. These belong in the
paper regardless of who prompted them:

- **Scientific rationale**: why this question, what prior work left open.
- **Design justification**: why this cohort, this loss, this comparator,
  this threshold. Written as the reason a reader needs, in one or two
  sentences, in Methods or at the point of the decision.
- **Methodological detail** sufficient for reproduction.
- **Scope conditions**: where the result holds and where it was not tested.
- **Limitations**: stated plainly, once, with mechanism where known.
- **Additional analyses** a reviewer requested, presented as part of the
  study: a sensitivity analysis is a Methods paragraph and a Results
  paragraph, not "as requested, we also ran".
- **Comparisons to prior work** a reviewer asked for, presented as
  positioning, not as rebuttal.

The distinction is in the framing. "We used a 6-hour minimum stay because
shorter stays have too few vital-sign measurements to compute the features"
is design justification. "We used a 6-hour minimum stay; we emphasize that
this choice is standard and does not bias our results" is defense. Keep the
first form.

## 4. Before/after pairs by section

Each "after" is what the manuscript should say. Where the change also
produces response-letter text, it is shown.

### Abstract

Before: In this revised study, we additionally show that the model
generalizes to an external cohort.
After: On an external cohort of 9,874 stays, AUROC was 0.81 (95% CI 0.79 to
0.83).

Before: Our findings, which have been strengthened by additional
experiments, demonstrate robust performance.
After: (delete the frame; state the finding with its number)

### Introduction

Before: Although some may argue that vital-sign models are well studied, we
note that most prior models were validated only internally, which limits
their applicability.
After: Most vital-sign models have been validated only on the site that
trained them [refs]; the two exceptions reported drops of 0.04 and 0.09
AUROC on transfer [refs].
The "some may argue" frame is the reviewer's objection in disguise. The
after version makes the same case with evidence.

Before: The contributions of this paper, which have been clarified following
review, are as follows.
After: This paper makes three contributions.

### Related work

Before: As the reviewer noted, we had omitted the work of Chen et al., which
we now discuss here.
After: Chen et al. [12] transferred a similar model across three hospitals
and attributed the loss to case-mix shift; they did not examine calibration.
Response letter gets: "We added Chen et al. to Related Work (Section 2.2)
and compare against their transfer results in Discussion."

### Methods

Before: To address the concern that forward-fill imputation may bias the
results, we have now added a comparison with mean imputation.
After: Missing vitals were forward-filled; a comparison with mean imputation
is reported in the Supplement (Table S2).

Before: For clarity, the hyperparameter search procedure has been described
in more detail below.
After: (delete; the detail simply follows)

Before: We used 5-fold cross-validation, which we believe is sufficient
given the dataset size.
After: We used 5-fold cross-validation.
If the reviewer asked whether 5 folds is enough, the answer is in the
response letter with the variance across folds, or in Results as a number.

### Results

Before: In the revised analysis we also examined calibration in age
subgroups, which the reviewer rightly suggested. Calibration was worst in
patients over 75.
After: Calibration degraded with age; in patients over 75 the integrated
calibration index was 0.11 versus 0.03 in patients under 50 (Fig. 3).

Before: Importantly, and contrary to what might be expected, the sensitivity
analysis did not change our conclusions.
After: Excluding stays with missing lactate left AUROC unchanged (0.81 vs
0.80; Table S3).

Before: These results are consistent with those reported in the original
submission.
After: (delete)

### Discussion

Before: We acknowledge that using only one external site is a limitation,
as noted by the reviewer, but we emphasize that this is common practice in
the field.
After: A single external site limits what can be said about
generalization; the calibration drift we observed may be specific to the
case mix of that site, and multi-site validation is the obvious next step.
The "common practice" defense goes in the response letter if it goes
anywhere.

Before: As discussed in Section 3.2, the model uses only routine vitals.
This design choice, which we have justified above, means that
After: Because the model uses only routine vitals,

Before: We have expanded this section to discuss clinical implications in
more depth.
After: (delete; the discussion of implications follows)

### Conclusion

Before: In conclusion, and in response to the helpful comments of the
reviewers, we have shown that
After: This study showed that

Before: (a Conclusion that repeats the Discussion's three paragraphs in
condensed form, added because a reviewer said the paper "ends abruptly")
After: Three or four sentences: what was shown, the one condition under
which it holds, what it changes for practice or research.

### Figure captions

Before: Figure 3 (new). Calibration by age group, added in response to
Reviewer 1.
After: Figure 3. Calibration by age group.

## 5. Repair procedure for a leaked passage

1. Identify the fact inside the frame. Most leaked sentences contain one
   real statement wrapped in commentary.
2. Cut the frame entirely. Do not soften it ("we note that" is still a
   frame).
3. Decide where the fact belongs. Often it is not where the leak occurred,
   because the leak was placed where the reviewer looked.
4. Check whether the manuscript already states the fact. If so, merge; keep
   the better version in the better location; delete the other.
5. Write the fact in the register of its new home, as if first drafted.
6. Record in the ledger: item id, what the fact is, where it now lives.
7. Write the response-letter entry from the ledger, with the location.

## 6. Edge cases where the manuscript does narrate change

A few document types describe change by design. Do not strip these:

- **Corrections, errata, corrigenda.** The entire document narrates what
  changed and why.
- **Registered Reports, Stage 2.** Deviations from the approved Stage 1
  protocol must be declared in the manuscript, usually in a dedicated
  subsection. That is protocol deviation, not reviewer response.
- **Clinical trial reports.** Deviations from the registered protocol,
  changes to outcomes after trial start, and interim analyses are reported
  in Methods per CONSORT. Same logic: the science changed, and the reader
  needs to know.
- **Preprint version notes.** A "changes from v1" note on a preprint server
  is a versioning artifact outside the manuscript body; keep it outside.
- **Replication and reanalysis papers.** "Unlike the original analysis, we
  ..." is scientific positioning against a published paper, not narration of
  the present paper's revision.
- **Second-round "note added in proof".** Rare and journal-specific; follow
  the venue's instructions.

In every one of these, the narrated change is about the study or the
scientific record, never about the peer review of the manuscript itself.
