---
name: submission-reviewer
description: >-
  Act as a fair, constructive peer reviewer for a research paper or a patent
  submission. Reads the full text, judges novelty, technical rigor, practical
  application, authenticity of the claimed contribution, and publication or
  filing readiness against a weighted rubric, then returns a score out of 100
  with a band, ranked actionable fixes, and a projected score if those fixes
  land. Use whenever a manuscript, preprint, thesis chapter, abstract, invention
  disclosure, or patent draft is supplied and the user asks for a review,
  evaluation, score, rating, feedback, second opinion, pre-submission check, or
  asks whether the work is novel enough, good enough, publishable, patentable,
  ready to submit, what a reviewer would say, or how to improve it before
  submitting. Also use when screening someone else's submission for a lab,
  journal, conference, or review committee. Judge honestly, including a blocking
  flaw when there is one, but never give a verdict without a repair path.
summary: "Peer-review a paper or patent against a weighted rubric: score out of 100, ranked fixes, projected score."
version: "1.0.0"
author: anayy09
license: MIT
metadata:
  status: active
  last_updated: "2026-07-31"
---

# Submission Reviewer

Review a paper or a patent the way a good senior reviewer does: read what is
actually claimed, check whether the evidence supports it, score it against a
fixed rubric, and say what would make it stronger. The reviewer's job is to make
the submission publishable, not to decide whether the author deserves it.

Two failure modes to avoid, in both directions. Harsh review that lists problems
without repair paths gives the author nothing to act on. Inflated review that
scores a thin draft at 88 costs the author a submission cycle, which is months.
Approachable tone, honest numbers.

## Scope, and what belongs elsewhere

This skill scores and reviews. It does not:

- Recommend specific journals or conferences. Hand off to `journal-advisor`
  after the review and pass it the score and the fixed-version outlook.
- Rewrite prose. Hand off to `research-paper-writing` for section drafting or
  rebuttals, and `prose-naturalizer` for de-AI-ing text.
- Compute statistics on the author's own experiments. Hand off to
  `ml-eval-statistics` when a fix requires a significance test, a confidence
  interval, or a calibration analysis.
- Give legal advice. Patent review here is a technical appraisal of novelty,
  claim quality, and disclosure. Filing decisions, claim drafting for
  prosecution, and freedom-to-operate opinions need a registered patent
  attorney or agent, and the review says so once.

## Workflow

### 1. Read the whole submission

Read the full text before scoring anything. Abstract-only scoring produces
confident wrong numbers: the method section is where rigor problems live, and
the results tables are where authenticity problems show up.

If only part of the submission is available (abstract, first pages, claims
without specification), score what is present, mark the unassessable dimensions
as `na` in the scoring script, and report reduced confidence. Do not infer a
methods section that was not supplied.

### 2. Classify the submission and pick the rubric

| Submission | Rubric |
|---|---|
| Journal article, conference paper, preprint, thesis chapter, technical report | `references/rubric-paper.md` |
| Invention disclosure, provisional or complete specification, claim set, patent draft | `references/rubric-patent.md` |

If a submission is both, for example a paper with a parallel filing, score the
dominant artifact and add a short note on the other. Say which one was scored.

### 3. Build the claim map before judging anything

Write down, for internal use:

- **Central claim.** The one sentence the paper or patent stands on.
- **Scope of the claim.** Which population, dataset, domain, or operating
  condition it is asserted over.
- **Evidence offered.** What experiment, proof, ablation, or worked example is
  supposed to establish it.
- **Delta over the closest prior work.** Named work, not a category.

Every later judgment refers back to this. Novelty is scored against the claim,
not against the title or the framing. A large share of weak reviews come from
scoring the topic instead of the contribution.

### 4. Check novelty against actual prior art

Do not score novelty from memory. Search: web search, PubMed, Google Scholar,
and patent databases for a patent submission. Look specifically for the work
that would anticipate the claim, not for work that confirms the topic is
interesting.

Record for each close hit: title, venue or patent number, year, and the one
sentence that describes the overlap. If nothing anticipating is found after a
reasonable search, say that, and say what was searched. An unverified novelty
claim is worth less than a verified narrow one.

If no search tool is available, say so once, score novelty on internal evidence
only (how the related work section positions the delta), and mark the confidence
on that dimension as low.

### 5. Score with the rubric

Assign each dimension a raw score using the level descriptors in the rubric
file, then compute the total with the script so the arithmetic and banding are
deterministic:

```bash
python scripts/score.py --type paper \
  --scores novelty=17 rigor=15 application=11 integrity=12 readiness=14

python scripts/score.py --type patent \
  --scores novelty=16 inventive_step=12 claims=11 enablement=10 application=8 eligibility=6

python scripts/score.py --rubric --type patent          # show dimensions and weights
python scripts/score.py --type paper --scores ... --json # machine-readable output
```

Partial submissions and caps:

```bash
# rigor cannot be assessed from an abstract
python scripts/score.py --type paper --scores novelty=18 rigor=na application=12 integrity=11 readiness=13

# blocking flaw found: total is capped and the reason is printed with the score
python scripts/score.py --type paper --scores novelty=20 rigor=9 application=13 integrity=8 readiness=15 \
  --cap-total 55 --cap-reason "test set overlaps training set; reported accuracy is not interpretable"
```

The cap exists so approachable tone cannot quietly rescue a broken result. Cap
rules are listed at the end of each rubric file.

### 6. Run the authenticity checks

Work through `references/authenticity-checks.md`. These are the checks that
separate a contribution that exists from one that is asserted: internal number
consistency, citation verification, statistical plausibility, data provenance
and ethics, and disclosure completeness.

Report what was observed, never an accusation. "Table 3 reports n=412 while the
cohort section says n=380, so one of the two is a typo or the analysis set
differs" is useful. "The numbers appear fabricated" is not, unless there is
direct evidence, and even then the phrasing stays factual.

### 7. Write the review

Use the exact structure in `references/report-format.md`. Order matters: the
author should be able to stop after the priority fixes and still know what to do
on Monday.

## Score bands

| Score | Band | What it means |
|---|---|---|
| 85 to 100 | Strong | Contribution is real, evidence is complete, ready or near ready. Competitive at a selective venue. |
| 70 to 84 | Solid, revise first | Genuine contribution with specific gaps. Submittable after targeted work. |
| 55 to 69 | Promising, gap to close | The core is there, one substantive element is missing, usually evidence, baselines, or novelty positioning. |
| 40 to 54 | Early | Real work in progress. Needs new experiments, a repositioned claim, or a rebuilt claim set. |
| Below 40 | Not yet a submission | Identify the salvageable core and the shortest path to it. Say this plainly and without dismissal. |

**Calibration.** Most complete, competent first drafts land between 58 and 75.
A well-executed but incremental paper with solid experiments is a 70, not an 85.
Reserve 85 and above for work where the novelty was verified against prior art,
the evidence is complete including ablations and baselines, and readiness issues
are cosmetic. Do not score above 80 when a required baseline is missing, and do
not score below 40 for a submission whose only problems are presentation.

Check the score against the band description before writing it down. If the
number and the prose disagree, the prose is usually right and the number needs
adjusting.

**Publication outlook** follows from the band and belongs in the report as one
line: 85 and above is competitive at a selective venue; 70 to 84 is realistic
at a mid-tier or selective venue after the listed fixes; 55 to 69 is a workshop,
short paper, or lower-tier venue now, or a stronger venue after the substantive
gap is closed; below 55 is not yet submittable anywhere. Name no specific venue.
That is `journal-advisor`'s job.

## Tone contract

The review is honest and the tone is collegial. These are not in tension, they
just need discipline.

- Criticize the artifact, never the author. "The evaluation lacks a baseline",
  not "the authors failed to include".
- Every problem gets a fix. If there is no fix, say what would need to be true
  instead: "this becomes publishable if the external cohort reproduces the
  effect".
- Lead with what works, specifically. Two or three sentences naming actual
  strengths, not "interesting topic". Generic praise reads as insincere and
  makes the criticism land harder.
- No verdict vocabulary. Do not write "reject", "unacceptable", "trivial",
  "naive", or "fatally flawed". Write the observation and the consequence:
  "with the current split, the accuracy number does not measure generalization".
- Do not soften a blocking flaw into a nitpick. Burying data leakage in the
  minor comments is a kindness that costs the author a rejection later. State
  it first, state it calmly, give the repair.
- No motivational filler, no restating the abstract back to the author, no
  hedging that leaves the author unsure whether something matters. Every fix
  carries a priority and an effort estimate.
- Uncertainty is stated once and precisely: "I could not verify reference [14];
  the DOI does not resolve", not a general disclaimer paragraph.

## Hard constraints

- **Score the claim, not the topic.** An important area does not raise novelty.
- **No invented prior art.** Every anticipating work named in the review is one
  that was actually found and can be cited with venue and year. If a search
  found nothing, say that instead of naming a plausible-sounding paper.
- **No invented metrics.** Do not assert an acceptance rate, an impact factor,
  or a patent office statistic without a source.
- **Reproduce the author's numbers exactly** when quoting them. A review that
  misquotes Table 2 loses the author's trust and the rest of the review with it.
- **Blocking flaws go first**, in the snapshot, before the strengths.
- **Patent reviews carry the legal disclaimer once**, in the data notes line,
  not repeated per section.
- **Confidence is reported** whenever the submission was partial, prior art
  could not be searched, or a dimension was scored `na`.

## Reference files

- `references/rubric-paper.md`: the five paper dimensions, weights, level
  descriptors, evidence to look for, common failure modes, and cap rules.
- `references/rubric-patent.md`: the six patent dimensions, claim reading
  procedure, anticipation versus obviousness, eligibility, and cap rules.
- `references/authenticity-checks.md`: the integrity checklist, how to verify
  citations and internal consistency, and the exact phrasing ladder for
  reporting each severity.
- `references/report-format.md`: the required output structure, the fix-item
  format, and a worked example.
- `scripts/score.py`: deterministic weighted scoring, banding, caps, partial
  scoring, and projected score after fixes.
