# Cutting to a budget

A page cap or a word guidance turns editing into arithmetic. The procedure:
measure, rank the cuts by yield and cost, apply them in batches, re-measure,
and stop when the cap is met, not when the text feels shorter.

## Measure

```bash
python <build-check>/scripts/build_check.py submission/ieee/main.tex --max-pages 16
python scripts/audit_manuscript.py paper/main.md --report audit_before.md
```

Record: pages against the cap, body words, words per section, the
references page, and whether the overage is word-bound (uniform density,
spill at the end), float-bound (half-empty pages), or table-bound. Fix
float placement first (`build-check`'s `references/float-placement.md`);
it can recover a page with no prose change.

## Rank the cuts

Ordered by yield per unit of damage to the paper. Take from the top.

| Class | Typical yield | Where the audit points |
|---|---|---|
| appendix and supplementary-grade tables moved to a supplement, one-line pointers left | pages | outline word counts; tables cited once |
| references cited once in related work, and preprints with a version of record (`investigating-sources` reference-diet) | half a page per 15 to 20 references | citation density; once-only references |
| summary paragraphs beyond the three the paper is allowed | 100 to 300 words each | summary paragraphs |
| protocol refrain, editorial self-commentary, reader management (families B, C, D) | 5 to 10 percent of a pre-registered paper | the six-family detectors |
| justifications explained more than once | 50 to 150 words per duplicate | recurring distinctive phrases; justification index |
| limitations that re-explain methods | a third of a long Limitations section | limitations length |
| captions that repeat the body | 30 to 80 words each | captions that argue |
| related-work paragraphs that survey rather than position | up to half of a long related-work section | Introduction plus related work share of body |
| background in the Discussion | a paragraph or two | Discussion paragraphs opening on the problem |
| body tables that summarize prose in the same section, or the prose they summarize (keep one) | 100 to 300 words | body tables |

Not on the list: results, controls, ablations, a limitation's mechanism,
the sentence that scopes a claim. A cut that removes evidence is a
different decision and belongs to the owner.

## Apply in batches, re-measure after each

Words do not map to pages linearly. A 600-word cut can recover nothing if a
float moves into the freed space, or two pages if a break clears. So: apply
one class, rebuild, run `build_check.py`, record the new count, continue.
Quote the last report in the hand-back, not the first.

## What a reviewer reads as a paper pushed over its limit

Shrunk figures, a smaller bibliography font, tightened margins or leading,
`\vspace` around floats, `\small` on the body. Typesetters undo them and the
checker's overflow and font checks do not see them. Do not use them.

## Hand-back

Pages before and after per target, words per section before and after,
each cut class applied with its yield, what was moved to the supplement,
and the count of references removed. If the cap is still not met after the
whole list, say so and list the evidence-bearing candidates for the owner
to rule on, with what each costs the argument.
