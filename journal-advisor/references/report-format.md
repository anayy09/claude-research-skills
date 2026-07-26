# Report format

Use this structure exactly. It is ordered so the user can stop reading after the
first section if they only want the answer.

---

## Required structure

```
## Manuscript profile
Three to five lines: contribution, field, article type, novelty class, and any
constraint the user stated. No restatement of the abstract.

## Overall best recommendation
**<Journal> (<Publisher>)**
One paragraph: why this one wins on the priority order, and the single tradeoff
it carries. Then the full field block (below).

## Ranked by publisher
### IEEE
1. <Journal> — field block
2. ...
### Springer Nature
### Elsevier
### ACM
### Taylor & Francis

Three to five per publisher. If a publisher's list has fewer than three
defensible matches, say so and give the ones that exist rather than padding.

## Tradeoffs and what would change the ranking
Three to six lines. Name the decision the user actually faces.

## Data notes
One or two lines: which fields were unavailable, and whether web verification
was performed.
```

## The field block

Every journal, in the overall recommendation and in every ranked list, carries
these eight items. Keep each to one line where possible.

- **Publisher and OA model** — from the catalog.
- **Topical fit** — one or two sentences naming what in the journal's stated
  scope matches what in the manuscript. Specific, not "strong alignment with the
  journal's aims".
- **Review speed** — the publisher-stated figure with its metric named, or
  "not publicly stated".
- **Indexing and quartile** — with the metric and year, or "not stated in the
  provided list".
- **Article type** — the journal's own category this manuscript would be
  submitted under.
- **Submission constraints** — APC, length limit, template, and any gate.
- **Acceptance likelihood** — stated rate if published; otherwise the labeled
  proxies and the fit-strength judgment.
- **Desk-reject risk** — low, medium, or high, with the driving factors.

A compact table works when the journals are similar; prose blocks work better
when they differ on different axes. Either is acceptable; do not mix them within
one section.

---

## Worked example of a single entry

> **2. Computers in Biology and Medicine (Elsevier)** — hybrid open access
>
> **Fit.** The journal's remit covers computational methods applied to clinical
> and biological problems, including diagnostic image analysis; the manuscript's
> patch-level triage pipeline for colorectal histopathology sits inside that
> remit rather than at its edge. Its evaluation-methodology emphasis suits a
> journal that publishes applied validation work rather than architecture
> novelty alone.
>
> **Review speed.** Not publicly stated on the journal page as of <date>;
> Elsevier does not publish a median first-decision time for this title.
>
> **Indexing and quartile.** Q1 (CiteScore 2024) per the provided Elsevier list.
> Scopus coverage not stated in that list; confirm on the journal page if the
> user needs it recorded.
>
> **Article type.** Full-length original research article.
>
> **Constraints.** Hybrid: no APC unless open access is elected; confirm the
> current gold OA fee and whether the institutional agreement covers it. No
> hard page limit stated; Elsevier article template.
>
> **Acceptance likelihood.** No acceptance rate published. Proxies: broad
> applied scope, high submission volume, and a stated preference for clinical
> relevance over methodological novelty. Fit strength is the main favorable
> factor here.
>
> **Desk-reject risk: medium.** Scope fit is strong, but the journal favors work
> with demonstrated clinical relevance, and the manuscript's validation is
> single-cohort. Adding an external cohort, or foregrounding the triage workload
> reduction rather than the model, would move this to low.

Note what the example does: names the metric and year for the quartile, marks
review speed as unstated instead of guessing, labels the acceptance-likelihood
reasoning as proxies, and gives the desk-reject rating a reason and a remedy.

---

## Style rules

- Journal names in bold on first mention in each block.
- Never a bare "Q1"; always the metric and year.
- Never a review time without its source and metric.
- No superlatives about journals ("prestigious", "top-tier"). Give the quartile
  and let it speak.
- No recommendation of a journal outside the bundled lists. If the best fit is
  outside them, say so in one sentence in the tradeoffs section and move on.
- Do not pad a publisher's section to reach three entries. Fewer honest matches
  is more useful than three with one invented rationale.
- Keep the whole report readable in a few minutes. If the manuscript profile
  section runs longer than five lines, it is doing the user's reading for them
  rather than advising.

## When the answer is "none of these"

If no permitted title is a defensible match, say so first, explain the gap in one
sentence (the topic falls outside the disciplines these lists cover; the
agreement lists are scoped to particular imprints), and then give the closest
permitted options with honest low ratings. Do not manufacture fit.
