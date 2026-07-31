# Authenticity checks

These checks establish whether the contribution described is the contribution
that was made. Run them before scoring the `integrity` dimension, and before
writing the review, because a finding here changes the snapshot.

The governing rule: **report the observation, not the inference.** A discrepancy
between two numbers is an observation. "The data appear fabricated" is an
inference, and almost always the wrong call from a reviewer's position. Most
discrepancies are transcription errors made at 2am. Write what is visible, ask
what the author should clarify, and let the severity ladder at the end decide
how loudly to say it.

---

## 1. Internal consistency

Cheap, and it catches more than any other check.

- Do the numbers in the abstract match the results tables? Headline numbers get
  updated in one place and not the other more often than any other error.
- Do sample sizes agree across the cohort description, the flow diagram, the
  tables, and the statistics? Track the exclusions: if 500 enrolled and 380
  analyzed, the 120 should be accounted for.
- Do percentages and counts reconcile? Recompute a few. If n=47, no percentage
  ending in .0 for a non-multiple is possible.
- Do the figures show what the captions claim, at the axis ranges given?
- Do reported means, standard deviations, and test statistics sit in a possible
  relationship to each other and to the sample size?
- Do the totals in tables add up to the stated totals?

For a paper with many tables, extract the numbers and check them with a short
script rather than by eye. Arithmetic checks belong in code.

## 2. Citation verification

- Spot-check at least eight references, weighted toward those supporting the
  central claim and toward the most recent ones. Verify existence via search,
  PubMed, Crossref, or the publisher page: authors, year, venue, and DOI
  resolution.
- Check that the cited work says what the sentence citing it claims. A citation
  that exists but does not support the statement is a real problem and more
  common than an invented one.
- Watch for the invented-citation pattern: plausible author names in a real
  venue, a title that reads as a perfect fit for the sentence, and a DOI that
  does not resolve or resolves to something unrelated.
- Check self-citation density and whether the closest prior work is cited at
  all. Missing the nearest competitor is usually an oversight, and pointing it
  out is one of the most useful things a reviewer does.

Record the verification status for each spot-checked reference. Report only the
ones that failed, with what specifically failed.

## 3. Statistical plausibility

- Do the reported effect sizes fit the sample size? Very large effects from very
  small samples deserve a question about variance and selection.
- Are p-values consistent with the reported test statistics and degrees of
  freedom? Recompute where the values are given.
- Accuracy at or near 100 percent on a non-trivial task is a leakage signal
  first and an achievement second. Ask how the split was constructed before
  congratulating.
- Are results suspiciously uniform across conditions that should differ, or
  suspiciously smooth across a sweep?
- Does the number of comparisons match the multiplicity handling? Twenty
  ablation arms and one uncorrected significant result is a finding about
  multiplicity, not about the method.

When a fix requires an actual statistical procedure, name it and hand off to
`ml-eval-statistics` rather than describing the procedure inline.

## 4. Data provenance and ethics

- Is the data source named, with version, access date, and license?
- For human-subject or patient data: is there an IRB or ethics committee
  approval number, a consent statement, and a de-identification description?
  Missing approval on clinical data is a cap-level finding.
- Does the license permit the use described, including redistribution of derived
  data if that is claimed?
- For scraped or synthetic data, is the generation or collection procedure
  described specifically enough to be reproduced?
- Is the train, validation, and test partitioning described at the unit that
  prevents leakage, and can that be verified from what is written?

## 5. Contribution and disclosure completeness

- Author contributions, funding, and conflicts of interest declared.
- Overlap with the authors' own prior work disclosed, especially where a
  conference version is being extended. The expected standard is usually a
  stated percentage of new material.
- Prior submission history disclosed if the venue requires it.
- Use of generative AI disclosed if the venue requires it.
- Code and data availability stated, with a working link or an explicit reason
  for restriction. A dead repository link is worth flagging.
- For patents: inventorship complete and consistent with who contributed to the
  claimed conception, plus any employer, funder, or institutional obligation.

## 6. Text-level signals

Do not treat these as proof of anything. They are prompts to check the
substance, and they are frequently wrong about honest authors.

- Sections of uniform, generic prose that could describe any paper in the field,
  especially in related work and discussion.
- Citations clustered in a way that suggests they were assembled to fill a
  paragraph rather than to support specific statements.
- A methods section that describes an approach in general terms without the
  specific choices that would have been forced during implementation. Real
  implementation leaves fingerprints: odd hyperparameters, a workaround for a
  library quirk, an explanation of why the obvious thing failed.
- Inconsistent voice or terminology between sections, or a notation that changes
  midway.

If these signals appear, ask for the implementation detail that would resolve
them. That is a useful reviewer question regardless of the cause, and it is
never phrased as an accusation.

---

## Severity ladder and phrasing

| Severity | What it is | Where it goes | Phrasing pattern |
|---|---|---|---|
| Cosmetic | Typo-class inconsistency with no effect on the claim | Minor comments | "Table 2 gives 0.847 while the abstract gives 0.85; align them." |
| Clarification | Something is missing or ambiguous, probably an omission | Priority or secondary fixes | "The cohort section reports 380 patients and Table 3 reports 412. Please state which set each analysis used." |
| Material | Affects interpretation of the result | Priority fixes, and named in the snapshot | "Split is described at the patch level while the cohort has multiple patches per patient, so the test set likely contains patients seen in training. The reported accuracy cannot be read as generalization until the split is redone at patient level." |
| Blocking | The claim cannot be evaluated, or the record would be harmed | Snapshot, first item, plus a cap | "References 14, 19, and 27 do not resolve and could not be located in Crossref, PubMed, or a general search. These support the central comparison, so they need to be corrected or replaced before the paper can be assessed." |

Even at blocking severity the sentence describes what was checked and what was
found. That is what makes it actionable and what makes it fair if the author has
an innocent explanation, which is the usual case.

**Never write**: "fabricated", "fake", "dishonest", "plagiarized" as a
conclusion the reviewer has drawn, unless there is direct evidence such as a
matched source text or a duplicated figure region, and even then state the
evidence and let it speak. If the finding is that serious, say that it needs
resolution with the author or the editor before the review can proceed, and
score the `integrity` dimension accordingly.
