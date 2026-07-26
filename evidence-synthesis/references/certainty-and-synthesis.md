# Synthesis and certainty

## Deciding whether to pool

Meta-analysis answers: what is the common effect, if there is one. If the
studies do not estimate a common effect, the pooled number is precise and
meaningless.

Pool when:

- The populations, interventions, comparators, and outcomes are similar enough
  that a shared effect is plausible. This is a clinical and methodological
  judgment made before looking at the results, and it belongs in the protocol.
- The outcome is measured on a scale that can be combined, or converted with a
  defensible transformation.
- There are enough studies. Two studies can be pooled arithmetically; the
  between-study variance cannot be estimated from two studies, so the interval
  is not trustworthy.

Do not pool when the studies differ in ways that matter to the effect, when the
outcome definitions are incompatible, or when the included studies are at high
risk of bias in ways that would propagate directly into the pooled estimate.

"We could not pool because of heterogeneity" is a weak reason if the
heterogeneity was foreseeable from the eligibility criteria. The stronger move
is to define subgroups in the protocol that are internally poolable.

## When not pooling: SWiM

Synthesis Without Meta-analysis (SWiM) provides reporting structure for
narrative synthesis, which otherwise degenerates into study-by-study
description. It asks you to specify: how studies were grouped, the standardized
metric used for comparison, the synthesis method (for example vote counting
based on direction of effect, or summarizing effect estimates), how results were
presented, and how certainty was assessed.

Vote counting deserves a specific caution: counting how many studies were
"positive" ignores effect size and precision entirely, and a formal
direction-of-effect vote count with a sign test is the defensible version. Say
which you did.

## Model choice

**Fixed effect** assumes one true effect and that differences are sampling
error. Rarely defensible outside very homogeneous sets.

**Random effects** assumes a distribution of true effects and estimates its
variance. The default in most reviews. Note the interpretation shift: the pooled
estimate is the mean of a distribution, not "the" effect, and small studies get
relatively more weight than under a fixed-effect model, which matters when small
studies are also the biased ones.

Estimator choice affects the interval when the number of studies is small.
Restricted maximum likelihood with the Hartung-Knapp adjustment is a common
current recommendation for random effects; DerSimonian-Laird intervals are too
narrow with few studies. Report which estimator and adjustment were used.

## Heterogeneity, read correctly

**I-squared is not the amount of heterogeneity.** It is the proportion of total
variability attributable to between-study variance rather than sampling error.
It rises as studies get more precise even when the actual spread of effects is
unchanged, so a large I-squared in a set of very large trials can accompany
clinically trivial differences, and a small I-squared in small trials can hide
important ones.

Report instead:

- **tau-squared** (or tau), the between-study variance on the effect scale. This
  is the magnitude.
- **A prediction interval**, which gives the range in which the effect of a new
  study would be expected to fall. This is what a clinician actually wants and
  it is usually much wider than the confidence interval, which is precisely why
  it should be reported.
- **The forest plot**, read rather than glanced at.

Threshold rules ("I-squared above 50 percent means do not pool") are not
supported by the statistic's definition. Investigate heterogeneity with
prespecified subgroups and meta-regression, and treat post hoc subgroup findings
as hypothesis-generating.

## Small-study effects and publication bias

Funnel plot asymmetry has several causes, of which publication bias is only one:
true heterogeneity related to study size, poorer methodology in small studies,
and chance all produce it. Do not label asymmetry "publication bias" without
argument.

Tests (Egger, Peters) need roughly ten or more studies to have any power. Below
that, note the limitation rather than running the test and reporting a
meaningless p-value. Registry searching for unpublished trials is more
informative than any funnel plot.

## Certainty: GRADE

Rate certainty per outcome, in four levels: high, moderate, low, very low.
Certainty is a statement about how much confidence to place in the estimate for
that outcome, not a label for the review.

Start from the design (trials start high, observational start low), then:

**Rate down for:**
- Risk of bias in the contributing studies
- Inconsistency (unexplained heterogeneity across studies)
- Indirectness (population, intervention, comparator, or outcome differs from
  the question)
- Imprecision (the interval spans decisions that differ)
- Publication bias (suspected)

**Rate up for (observational evidence only):**
- Large magnitude of effect
- Dose-response gradient
- Plausible residual confounding that would work against the observed effect

Two points that get lost. First, a downgrade must name the reason and the
outcome; "moderate certainty" alone is not a GRADE assessment. Second,
indirectness is the domain most often ignored and most often relevant in applied
AI reviews: a model validated retrospectively on curated data is indirect
evidence for prospective clinical use, and that indirectness should be rated,
not mentioned in passing in the discussion.

For qualitative evidence, use GRADE-CERQual, which has its own components
(methodological limitations, coherence, adequacy, relevance).

## Summary of findings table

One row per outcome with: number of participants and studies, the effect with
its interval, the certainty rating, and a plain-language comment. This table is
what most readers actually read, and constructing it early exposes outcomes that
have no usable evidence before months are spent on them.

## Reporting the synthesis honestly

- State the pre-specified analysis and any deviation from it, with the reason.
- Distinguish pre-specified from post hoc subgroups every time.
- Report the number of studies contributing to each analysis; a pooled estimate
  from three of nineteen included studies should say so next to the number.
- If the synthesis is narrative, say so plainly and report against SWiM rather
  than presenting an unstructured discussion as a synthesis.
