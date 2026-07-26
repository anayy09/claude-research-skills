# Example: a brief, start to finish

This shows the full workflow for `brief` mode on a single question, including
the verification step that catches a fabricated source. It is illustrative; the
sources and DOIs shown are examples.

## The request

> Is intermittent fasting actually more effective than daily calorie restriction
> for weight loss? Quick answer with sources.

Single focused question → `brief` mode. Steps: SCOPE → SEARCH → VERIFY →
COMPOSE → AUDIT.

## 1. SCOPE

- **Question:** For adults with overweight or obesity, does intermittent fasting
  produce greater weight loss than continuous daily calorie restriction?
- **In scope:** randomized comparisons of the two approaches, weight-loss
  outcomes.
- **Out of scope:** metabolic markers beyond weight, athletic performance,
  long-term maintenance beyond the trial windows.
- **Success criteria:** an answer grounded in head-to-head trials or a
  synthesis of them, with the strength of the evidence stated.

## 2. SEARCH

Searches run this session (logged):

| Query | Tool | Yield |
|-------|------|-------|
| "intermittent fasting vs calorie restriction" randomized | web_search | 6 relevant |
| intermittent fasting weight loss meta-analysis | web_search | 3 relevant |
| (deliberate disconfirming search) intermittent fasting "no difference" trial | web_search | 2 relevant |

The third search is the disconfirming one — looking for evidence that the two
approaches are equivalent, so the brief is not built only from studies favoring
fasting.

## 3. VERIFY

Candidate source log after checking (`sources.json`):

```json
{
  "topic": "Intermittent fasting vs daily calorie restriction for weight loss",
  "generated": "2026-07-25",
  "sources": [
    {
      "key": "review2020",
      "type": "journal-article",
      "authors": ["Example, A.", "Sample, B."],
      "year": 2020,
      "title": "Intermittent fasting versus continuous energy restriction: a systematic review",
      "venue": "Example Journal of Nutrition",
      "doi": "10.1234/ejn.2020.0456",
      "url": "https://doi.org/10.1234/ejn.2020.0456",
      "verified": "confirmed",
      "verify_method": "crossref",
      "tier": "tier_1",
      "notes": "Meta-analysis of 11 RCTs."
    },
    {
      "key": "trial2019",
      "type": "journal-article",
      "authors": ["Sample, C."],
      "year": 2019,
      "title": "A 12-month randomized trial of alternate-day fasting",
      "venue": "Journal of Clinical Examples",
      "doi": "10.1234/jce.2019.0789",
      "url": "https://doi.org/10.1234/jce.2019.0789",
      "verified": "confirmed",
      "verify_method": "crossref",
      "tier": "tier_1",
      "notes": "Head-to-head RCT, n=100."
    },
    {
      "key": "mashup2021",
      "type": "journal-article",
      "authors": ["Sample, C."],
      "year": 2021,
      "title": "Fasting decisively outperforms all other diets",
      "venue": "Journal of Clinical Examples",
      "doi": "10.1234/jce.2021.9999",
      "url": "",
      "verified": "fail",
      "verify_method": "",
      "tier": "",
      "notes": "DOI does not resolve; real author + real journal, invented title. Classic mashup. REMOVE."
    }
  ]
}
```

Running the checker:

```
$ python scripts/check_citations.py sources.json
[OK     ] review2020   DOI resolved; metadata matches
[OK     ] trial2019    DOI resolved; metadata matches
[FAIL   ] mashup2021   Crossref returned 404 (no such DOI)

Summary (3 sources): FAIL: 1, OK: 2

1 source(s) FAILED and must be removed along with any claims that depended on them.
```

`mashup2021` is the fabrication the skill exists to catch: a real author and a
real journal welded to a title that was never published, with an
overstated-sounding claim. It is removed. Any claim that rested only on it is
removed too. Here, no surviving claim depended on it, so the brief proceeds with
the two confirmed sources.

## 4. COMPOSE

Using `assets/brief_template.md`:

---

# Is intermittent fasting more effective than daily calorie restriction for weight loss?

**Mode:** Brief · **Date:** 2026-07-25

## Answer

For weight loss, intermittent fasting and continuous daily calorie restriction
produce broadly similar results; head-to-head trials generally find no
clinically meaningful difference in weight lost when total calorie intake is
matched [review2020; trial2019].

## Evidence

A systematic review of randomized trials comparing the two approaches found
comparable weight loss between them, with differences that were small and not
consistently in fasting's favor [review2020]. A twelve-month randomized trial
directly comparing alternate-day fasting with daily restriction reached the same
conclusion: similar weight change, with somewhat higher dropout in the fasting
arm [trial2019]. The practical implication is that adherence, not the specific
schedule, tends to drive results.

## Confidence and caveats

The evidence is moderately strong — multiple RCTs and a synthesis of them — but
trials are mostly short (weeks to a year) and adherence varies, so long-term
differences remain less certain. Evidence on outcomes other than weight is out
of scope here.

## Sources

- [review2020] Example, A., & Sample, B. (2020). Intermittent fasting versus
  continuous energy restriction: a systematic review. *Example Journal of
  Nutrition*. https://doi.org/10.1234/ejn.2020.0456
- [trial2019] Sample, C. (2019). A 12-month randomized trial of alternate-day
  fasting. *Journal of Clinical Examples*. https://doi.org/10.1234/jce.2019.0789

---
*AI-assisted research tools were used to produce this brief. Citations were
verified against the cited sources.*

---

## 5. AUDIT

```
$ python scripts/audit_report.py brief.md sources.json
OK    No phantom citations
OK    Every cited source is confirmed
WARN  Orphan sources (1): logged but never cited
        [mashup2021]  -> cite it or drop it from the log
OK    Limitations section present
OK    AI-assistance note present

RESULT: No hard failures, but warnings above should be resolved before delivery.
```

The one warning is the failed `mashup2021` sitting in the log uncited — expected,
since it was removed from the deliverable. Drop it from the log (or leave it with
its `fail` note as a record of what was caught) and the audit is clean. Deliver.
