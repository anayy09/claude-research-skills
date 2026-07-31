# Report format

Use this structure. It is ordered so the author can stop after the priority
fixes and still know exactly what to do next.

---

## Required structure

```
## Snapshot
Three to four lines: what was submitted, the central claim in one sentence, the
score with its band, and the single thing that most limits the score. If a cap
or a blocking finding applies, it goes here, first, before anything else.

## Score

| Dimension | Score | Reason |
(one line per dimension, from the script output; the reason is one clause, not a
paragraph)

**Total: NN/100 (band).** Confidence: high | medium | low, with the reason if
not high.

## What works
Two to four specific strengths. Name the actual thing: the ablation design, the
size of the cohort, the clarity of Figure 2. No generic praise.

## Priority fixes
Three to five items, ranked by effect on the score. Each in the fix-item format
below.

## Secondary fixes
A compact list. One line each: what, where, and what to do.

## Authenticity and evidence check
What was verified and what was found. Include the negative result: "references
spot-checked, 8 of 8 resolved" is worth stating. Any severity item above
cosmetic appears here with its phrasing from the severity ladder.

## Projected score after fixes
The score if the priority fixes land, per dimension delta, with the script
output. State what each point of uplift depends on, so the projection is a plan
and not a promise.

## Outlook and next step
One line on publication or filing outlook by band. One line handing off: venue
selection to journal-advisor, statistical work to ml-eval-statistics, drafting
to research-paper-writing, filing questions to a patent attorney.

## Data notes
One or two lines: what could not be assessed, whether prior art was searched and
where, and for patents the legal disclaimer.
```

## Fix-item format

Every priority fix carries four parts. Missing any one of them makes the item
harder to act on than it needs to be.

```
**N. <Short imperative title>**
*What a reviewer will see.* One or two sentences, factual, referring to the
specific section, table, or claim.
*Fix.* The concrete action. Name the experiment, the baseline, the analysis, or
the restructuring. Specific enough to start today.
*Effort.* Rough: hours, a day, a week, or a new experiment cycle.
*Worth.* Which dimension it moves and by roughly how much.
```

---

## Worked example of a snapshot and one fix item

> ## Snapshot
>
> Full-length manuscript on patch-level triage for colorectal histopathology,
> claiming that a vision-language model can defer 40 percent of patches while
> holding sensitivity above 0.92. The method is sound and the ablations are
> unusually complete. **Score: 64/100 (promising, gap to close), capped at 65
> because the claim rests on a comparison against a single baseline that was
> not tuned.** The uncapped rubric total is 71.
>
> ## Priority fixes
>
> **1. Add a tuned baseline at comparable effort**
> *What a reviewer will see.* Table 2 compares the proposed policy against one
> off-the-shelf classifier at default settings, while the proposed method was
> tuned over a stated sweep. The first reviewer question will be whether the
> gain survives equal tuning, and on the current evidence the answer is unknown.
> *Fix.* Run the same sweep budget on the baseline and report both curves. If a
> stronger baseline exists in the recent literature, add it; the two closest are
> named in the prior-art notes below.
> *Effort.* One experiment cycle, roughly a week including the sweep.
> *Worth.* Rigor from 15 to about 20, and it lifts the cap. Largest single
> uplift available.

Note what the example does: the score is stated with the cap and the reason in
the same sentence, the strength is named before the criticism, the fix names the
actual experiment, and the uplift is quantified so the author can decide whether
the week is worth it.

---

## Style rules

- Second person, or no person at all. "The evaluation needs a tuned baseline"
  and "add a tuned baseline" both work. "The authors failed to" does not.
- Reproduce the author's numbers exactly when quoting them, with the table or
  section they come from.
- One clause of hedging is enough where evidence is thin. No disclaimer
  paragraphs.
- Tables for scores and secondary fixes, prose for priority fixes. Priority
  fixes need the reasoning visible.
- Keep the whole review readable in about five minutes. If it runs longer than
  roughly two pages, the secondary fixes list is doing too much.
- Do not restate the submission back to the author. They wrote it.
- No venue names, no acceptance-probability percentages, no impact-factor
  claims. The band already carries the outlook.

## When the submission is very early

Below 40, the review changes shape but not tone. Keep the score, keep the score
table so the author sees where the weight is, then replace the priority fixes
with a short reconstruction plan: what the salvageable core is, what the
smallest publishable claim built on it would be, and the two or three steps to
get there. Say plainly that the current draft is not yet a submission, in one
sentence, without softening it into ambiguity and without a verdict word.
