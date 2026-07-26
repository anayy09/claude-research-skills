# Critical appraisal: choosing and applying the right instrument

Five different things get called "quality assessment" and they answer different
questions. Confusing them is the most common appraisal error after using the
wrong tool entirely.

| Question | Instrument |
|---|---|
| Did the authors report what they did? | reporting guideline (PRISMA, CONSORT, TRIPOD+AI, STARD) |
| Is an included primary study at risk of bias? | RoB 2, ROBINS-I, QUADAS-2, PROBAST+AI |
| Was an existing review conducted well? | AMSTAR 2 |
| Is an existing review at risk of bias? | ROBIS |
| How certain is the body of evidence for an outcome? | GRADE |

Reporting quality is not study quality. A well-conducted study reported badly
and a badly conducted study reported well look similar on a reporting checklist
and completely different on a risk-of-bias tool. Say which you assessed.

## Primary study tools

### RoB 2 (randomized trials)
Five domains: randomization process, deviations from intended interventions,
missing outcome data, measurement of the outcome, selection of the reported
result. Judged per outcome and per result, not once per study, which is the
detail most often skipped. Signaling questions drive the domain judgment;
answering the domain directly without them defeats the design.

Overall judgment: low risk, some concerns, high risk. There is no numeric score,
and constructing one destroys the information.

### ROBINS-I (non-randomized studies of interventions)
Seven domains, built around comparison with a hypothetical target trial:
confounding, selection of participants, classification of interventions,
deviations, missing data, measurement of outcomes, selection of the reported
result. Requires specifying the confounders that matter *before* appraisal.
Judgments run to critical risk, and a study at critical risk should not be
included in the synthesis.

### QUADAS-2 (diagnostic test accuracy)
Four domains: patient selection, index test, reference standard, and flow and
timing. Each rated for risk of bias, the first three also for applicability.
Domain-specific signaling questions must be tailored to the review; using the
generic ones unmodified is a known misuse. QUADAS-C extends it to comparative
accuracy.

The two failures that dominate: a reference standard that is not independent of
the index test, and a case-control design where healthy controls make the test
look better than it will be in practice.

### PROBAST+AI (prediction models, including machine learning)
The 2019 PROBAST predates most current modelling practice. PROBAST+AI (Moons et
al., BMJ 2025;388:e082505) restructures the tool into two parts, one for model
development and one for model evaluation, and adds explicit attention to
fairness, to the data used for training, and to how a model performs in real
deployment rather than in a controlled comparison. It aligns with the TRIPOD+AI
reporting guideline (Collins et al., BMJ 2024;385:q902).

For a review that includes ML prediction models, the recurring high-risk
findings are: development without external validation, discrimination reported
without calibration, sample size inadequate for the number of candidate
predictors, and data leakage between training and test partitions. Look for
these specifically; they are usually present and usually not discussed by the
study authors.

Extraction for these reviews should follow CHARMS, which specifies the items to
pull from a prediction model study.

### ROBINS-E (exposures)
For observational studies of exposure rather than intervention. Where an older
review would have used the Newcastle-Ottawa Scale, ROBINS-E is the more current
choice. NOS remains widely used and widely criticized: its star system has poor
inter-rater reliability and converts domain judgments into a score, which is the
thing modern tools deliberately avoid. If you use NOS, say why and report the
domains rather than only the total.

### JBI checklists
Design-specific checklists covering prevalence studies, case series, qualitative
research, economic evaluations, and more. Useful coverage for designs the
Cochrane tools do not address.

## Review-level tools

### AMSTAR 2
Sixteen items assessing how well a systematic review was conducted, with seven
designated critical. The output is a confidence rating (high, moderate, low,
critically low), not a score; summing items is explicitly discouraged because it
lets a fatal flaw in a critical domain be offset by trivia.

Critical items include protocol registration before the review started, adequacy
of the search, justification for excluded studies, appropriate risk-of-bias
assessment of the included studies, appropriate meta-analytic methods, and
consideration of risk of bias when interpreting results. One uncorrected
critical flaw makes the review critically low confidence, which means its
conclusions should not be relied on without independent verification.

### ROBIS
Assesses risk of bias in the review process itself across four domains (study
eligibility criteria, identification and selection, data collection and
appraisal, synthesis and findings) plus an overall judgment. Overlaps AMSTAR 2
but asks about bias rather than conduct quality. Empirical comparisons find
moderate agreement between the two, so they are not interchangeable, and using
both is normal in a high-stakes umbrella review.

## Applying tools without corrupting them

- **Two independent assessors**, with a documented disagreement process. Where
  only one is available, say so; it is a limitation, not a detail.
- **Judge per outcome** where the tool requires it (RoB 2 explicitly does).
- **Never convert to a total score** unless the tool was designed for scoring.
  Domain-based tools deliberately resist summation because domains are not
  exchangeable.
- **Use the judgment in the synthesis.** An appraisal that appears as a
  traffic-light figure and never affects a conclusion has not been used. Options:
  restrict the primary analysis to low-risk studies, run a sensitivity analysis
  excluding high-risk studies, or rate down for risk of bias in GRADE.
- **Report the tool version and any tailoring.** QUADAS-2 signaling questions
  should be tailored; the tailoring must be reported.

## AI-assisted appraisal

If a model was used to draft risk-of-bias judgments, that is a judgment-making
use and must be disclosed and human-verified. The current expectation from the
2025 joint position statement of Cochrane, the Campbell Collaboration, JBI and
CEE is human oversight plus transparent reporting of any AI use that makes or
suggests judgments. Drafting a judgment that a human then confirms is acceptable
and disclosable; substituting for the human is not. See
`ai-use-reporting.md`.
