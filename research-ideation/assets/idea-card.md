# Idea card template

One card per direction. The lead direction gets the full card; runners-up
compress to claim, delta, what exists, what is missing, kill experiment, and why
it is not the lead.

---

### D<n>. <Title: the claim in plain words, not a topic>

**Claim.** One falsifiable sentence: what is asserted, over what population or
regime, measured how, at what unit.

**Why it is not obvious.** One or two sentences naming the assumption it
violates or the gap it fills. Not a restatement of the claim.

**Operators.** Ids from `references/idea-operators.md`.

**Closest work.**

| Citation | Overlap | Difference | Threat |
|---|---|---|---|
| Authors, venue, year | one sentence | one sentence | anticipates / constrains / supports / context |

If nothing was found, state the queries and sources searched instead.

**Delta type.** From the taxonomy in `references/novelty-check.md`.

**Assets used.** Ids from the inventory.

**Assets still needed.** Ids or descriptions, each with how it would be obtained
and what it costs. A direction needing an asset the user does not have says so
here and takes the feasibility hit.

**Headline table.**

Rows, columns, and the cell the claim lives in. State the value that would have
to appear there as a target, never as a result.

**Evidence plan.** Blocking items from the gap ledger in execution order, with
effort per item. Name the statistics required and hand them to
`ml-eval-statistics`.

| # | Item | Effort | Blocking |
|---|---|---|---|

**Kill experiment.**

```
Experiment:    <the smallest run that could show the effect is not there>
Cost:          <hours or days>
Decision rule: continue if <specific, measurable>; otherwise <named alternative
               direction, or stop>
```

**Top three reviewer objections.**

1. <objection> Answer: <answer, or the experiment that produces it>
2. ...
3. ...

**Risks.**

| Risk | Early signal | Mitigation |
|---|---|---|

Include the scooping risk when the area is active, with what would be seen first.

**Score.** Composite with band, from `scripts/rank_ideas.py`, and the one
dimension that limits it.

**Timeline.** Phases and slack from `scripts/plan_timeline.py`.
