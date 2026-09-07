# The manuscript boundary

What belongs in the manuscript, what belongs in the response to reviewers,
what belongs in internal notes, and how to move text that ended up in the
wrong one.

Contents

1. The reader test
2. Leak catalog: family A, review-process narration
3. Families B to F: non-manuscript text with no reviewer in it
4. What legitimately stays in the manuscript
5. Before/after pairs by section
6. Repair procedure for a leaked passage
7. Edge cases where the manuscript does narrate change

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

## 2. Leak catalog: family A, review-process narration

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

## 3. Families B to F: non-manuscript text with no reviewer in it

These are more common than family A in drafts written by careful authors,
and they are what makes a manuscript read as a series of defended positions
rather than a report of a study. The test is the same: is the sentence
about the study, or about the authors, the paper, or the reader?

### B. Editorial self-commentary

The sentence describes the authors' own honesty, restraint, or placement
decision.

- Announced restraint: "we would rather say so than bank the pass", "we
  report it and count it as nothing", "we declined it the first time it was
  available and again here", "we do not lean on it", "never instead of it".
- Announced honesty: "we report all of this because we registered it", "we
  state that plainly rather than let a reader find it", "we are explicit
  that", "we say so in the discussion rather than leaving a reader to
  notice", "we would rather say so than present a result as more damaging".
- Announced placement or emphasis: "worth stating rather than hiding", "worth
  naming rather than asserting", "belongs here rather than in a footnote",
  "which is the reason to report them rather than to treat them as a local
  curiosity", "we cite them as that".

Before: This is an easy test to pass and we would rather say so than bank
the pass.
After: The published interval is wide because six of fifteen targets have
fewer than fifty positives; the reproduction falls inside it.

Before: We report all of this because we registered it. An audit of how
other people's benchmarks are evaluated has no standing if it quietly
substitutes its own successful endpoints for its failed ones.
After: (delete) The registered-targets table in Results, with target and
measured value side by side, is the statement. Methods says once that
targets were registered and where.

Before: Haimovich and colleagues found the waveform arm adding real value
over the non-signal arms, which is a result in the opposite direction from
our hypothesis and belongs here rather than in a footnote.
After: Haimovich and colleagues found the waveform arm adding value over
age, sex, and biomarkers on a chest-pain cohort [35], the opposite direction
from our hypothesis.

### C. Protocol refrain

A methodological virtue restated at the point of each use. Pre-registration
is the usual one; "fixed in advance", "declared before the first run",
"before any number existed", "not chosen after seeing which was more
favourable", "every number resolves to a named cell of a generated table",
"nothing is plotted that is not tabulated". Each is true once. Stated ten
times it reads as insistence and it costs a sentence per result.

Before: The operating threshold is 0.10, fixed from the clinical framing and
recorded before any curve was computed, and quoted at 24-hour ICU admission
alone. ... We declared as much before computing any of it, precisely so that
it could not be offered afterwards as an explanation for an unflattering
number.
After: Methods, Registration (one paragraph, once): "Targets, the operating
threshold of 0.10, the matching specification, and the multiplicity families
were registered in [location] before any model was run." Results: "At the
registered threshold of 0.10, net benefit was ..." Nothing else.

Before: Every arm is trained at 5 seeds. Evaluation protocol, declared
before the first run. Four registered targets, and what they returned. No
number in this figure appears here first.
After: (figure caption describes panels; the registration statement is in
Methods)

### D. Reader management

The sentence tells the reader how to read a result rather than stating the
result's scope.

- "This paper must not be read as saying that it does."
- "The ordering is not a discrimination ordering and must not be read as
  one."
- "No part of our argument should be read as resting on a tight
  reproduction."
- "A reader's first suspicion of an audit is that the audited baseline was
  weakened."
- "We are not claiming the metadata arm is clinically more useful."
- "a reader cannot tell", "a reader given only a demographics baseline has no
  way to see it" (acceptable once, as the paper's motivating claim; not as a
  refrain).

Before: Acquisition context does not, however, explain the waveform arm, and
this paper must not be read as saying that it does. Those are two claims.
The first survives and the second does not.
After: Acquisition context recovers most of the waveform arm's discrimination
at short horizons without accounting for it: within matched strata the
waveform arm retains 78 to 93 percent of its advantage over demographics.

Before: This ordering is not a discrimination ordering and must not be read
as one. It follows from the calibration result above.
After: Because the waveform arm's probabilities run at roughly twice the
observed rate, it flags 96 percent of patients at a 0.10 threshold and its
net benefit sits close to treat-all.

### E. Internal workflow artifacts

Vocabulary and identifiers from the project's own management that mean
nothing to a reader: decision-log ids ("D-050", "closing D-018"), gate
names ("Gate G2"), plan vocabulary ("strengthener 10", "the second thing
cut if the schedule slips", "kill experiment", "the plan"), ledger and
pipeline terms used as if they were methods ("resolves to a named cell"),
repository paths ("docs/LIT-PROTOCOL.md"), machine arm labels in prose
("R3_acqctx_pre"), and shouted table notes ("THIS TABLE DOES NOT ORDER THE
ARMS BY DISCRIMINATION").

Before: It is strengthener 10 in the plan, the second thing cut if the
schedule slips. (table note)
After: (delete)

Before: And the kill-experiment contrast that preceded all of them,
acquisition context against demographics at the same longest horizon, is
-0.0216.
After: The prerequisite contrast, acquisition context against demographics
at one year, was -0.0216 [-0.0523, +0.0098].

Before: The search protocol is in docs/LIT-PROTOCOL.md, the record of what
ran in sources/search_record.md, and the screening decisions in
docs/LIT-SCREENING.md.
After: The search protocol, records, and screening decisions are in
Additional file 2.

### F. Pre-emptive objections

A paragraph or subsection framed as an objection and its rebuttal:
"Objections", "This is just known shortcut learning.", "Your waveform arm is
undertrained, so", "Acquisition context is legitimately available at
inference, so using it is fine." The substance is usually already in Methods
(the availability test, the tuning budget) or belongs in Limitations
(transfer to other sites). The frame is a response letter written before
the review.

Before: Your acquisition features leak the label. We separated the feature
blocks before fitting any model, every feature carries an availability
timestamp enforced by a test that fails on deliberately poisoned data, and
the confirmatory arm uses the pre-acquisition block only.
After: (delete the subsection) Methods, Acquisition context, already states
the block separation and the availability test. If the objection arrives in
review, the response letter points there.

Occasionally an objection is substantive enough to be part of the argument
(a competing account of the same result). Then it is written as
positioning, in Discussion, in the same voice as the rest: "An alternative
account attributes the non-specificity to shared pathophysiology [46]; our
matched arm is consistent with it because ..." No heading, no second-person
frame.

## 4. What legitimately stays in the manuscript

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

## 5. Before/after pairs by section

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

## 6. Repair procedure for a leaked passage

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

## 7. Edge cases where the manuscript does narrate change

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
