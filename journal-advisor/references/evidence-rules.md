# Evidence rules

Every field in the report has exactly one legitimate origin. This file fixes
which, and how to phrase what is missing.

## Origin of each reported field

| Field | Legitimate source | If unavailable |
|---|---|---|
| Journal name, publisher | `assets/journals.csv` | not possible; the title would not be recommendable |
| OA model | catalog | check the journal page |
| Quartile, indexing | catalog where present, else SCImago or the journal page, with the metric and year named | "not stated in the provided list; not verified this session" |
| Topical fit | your reading of the manuscript against the journal's stated aims and scope | do not recommend the journal |
| Acceptance rate | a figure the publisher states on the journal page or in its journal metrics panel | "no acceptance rate published"; then use proxies, labeled |
| Review speed | publisher-stated median or mean days to first decision, review, or publication | "review times not publicly stated" |
| Article type | the journal's own list of accepted types | "article types not enumerated on the journal page" |
| APC | the journal's APC page, with currency and date | "APC not stated"; note if an institutional agreement may apply |
| Page or word limits | author guidelines | "no explicit limit stated" |
| Template | author guidelines | "no template specified" |
| Desk-reject risk | your assessment via `desk-reject-rubric.md` | always assessable; it is a judgment, and must state its reasons |

## Acceptance rate

Publishers vary in what they disclose. Roughly:

- Taylor & Francis publishes an acceptance rate on many journal pages.
- Springer Nature publishes submission-to-first-decision and
  submission-to-acceptance times on many journal pages, and acceptance rates on
  some.
- IEEE publishes acceptance-related statistics for some journals in the
  publication details or author information section.
- Elsevier surfaces some figures through journal insights, inconsistently.
- ACM rarely publishes per-journal acceptance rates.

Check the page rather than assuming from this list, which describes tendencies
and will drift.

When no rate is published, these proxies may be used **if each is labeled as a
proxy and not as a rate**:

- **Scope breadth.** A journal with an explicitly broad remit and a stated
  soundness-based criterion (technically correct rather than novel or
  significant) accepts a larger share of submissions than a selective venue with
  a narrow remit.
- **Selectivity signals in the scope text.** Phrases requiring substantial
  novelty, significant advance, or broad interest indicate higher rejection.
- **Quartile as a weak inverse proxy.** Q1 venues are typically more selective.
  Weak because quartile measures citation, not selectivity, and the two diverge
  for large open-access venues.
- **Fit strength itself.** A manuscript squarely inside the stated scope has a
  materially better chance than a marginal fit, and this often outweighs the
  base rate.

Prohibited: stating a numeric acceptance rate that the publisher does not
publish, converting a proxy into a percentage, or presenting a figure from
training data as current. Rates change and stale numbers are indistinguishable
from invented ones in the user's hands.

## Review speed

Report only what the publisher states, quoting the metric exactly as labeled:

> Springer states a median of 21 days to first decision and 89 days from
> submission to acceptance (journal page, checked <date>).

Distinguish the metrics; they are not interchangeable:

- submission to first decision
- submission to first review completed
- submission to acceptance
- acceptance to online publication

A journal advertising a fast first decision may still be slow to publication,
and for a user with a deadline the second number is often the binding one.

When nothing is stated: "review times not publicly stated." Do not substitute
anecdote, do not infer from OA status, and do not infer speed from a journal
being large. If the user needs speed and no candidate publishes times, say that
the priority cannot be evaluated from public data for these venues, and let them
weigh it.

Contextual signals that may be reported as context, clearly separated from
stated times: a journal that publishes continuously rather than in issues
removes queueing delay after acceptance; a journal explicitly running a fast
track or a rapid communication type states so in its author guidelines.

## Indexing and quartile

Name the metric and year every time: "Q1 (CiteScore 2024)" or "Q1 (JIF 2024)",
never a bare "Q1". Where the catalog is silent (all ACM and Springer titles),
either report it as not stated in the provided list, or verify from SCImago and
cite that.

Distinguish coverage from quartile. Scopus coverage is a yes/no; SJR quartile is
a ranking within a subject category. The T&F list carries both, the others do
not.

If a journal has a quartile in one subject category and a different one in
another, name the category. SCImago assigns a journal to several categories and
"best quartile" is the maximum across them, which is what the T&F list reports.

## APC and cost

State the amount, the currency, and that it was checked today. Note when an
institutional agreement may apply, since three of the five bundled lists are
agreement or eligibility lists and the user's access to them is the reason those
titles are in scope at all. Do not assert that a specific waiver applies to this
user without evidence; phrase it as something to confirm with their library.

## Phrasing absent data

Use these forms. They are short and unambiguous.

- "No acceptance rate published by the journal."
- "Review times not publicly stated."
- "Quartile not stated in the provided list."
- "Article types not enumerated on the journal page."
- "APC not stated; confirm with the publisher."
- "Not verified in this session (no web access)."

Avoid softening these into implications of speed or selectivity. "Review times
are not published, though the journal appears to move quickly" is an invented
claim wearing a hedge.

## When web verification is unavailable

Say so once at the top of the report, then produce the recommendation from the
catalog alone with every unverifiable field marked. Do not skip the
recommendation; the catalog still supports scope shortlisting, quartile,
indexing, and OA model for most titles, and desk-reject risk remains assessable
from the manuscript itself.
