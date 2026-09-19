# Evidence rules

Every field in the report has exactly one legitimate origin. This file fixes
which, and how to phrase what is missing.

## Origin of each reported field

| Field | Legitimate source | If unavailable |
|---|---|---|
| Journal name, publisher | catalog plus current official journal identity | verify an outside-catalog title and document its fee route |
| OA model | current journal page; catalog is discovery evidence | mark model unverified |
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
  significant) may offer a more appropriate evaluation standard for a
  soundness-focused manuscript. This alone does not establish comparative
  acceptance rates.
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
never a bare "Q1". The catalog carries a quartile for about one record in
twenty: the IEEE, Elsevier and T&F workbooks supply one, and the ACM and
Springer workbooks, the DOAJ rows, and every researched fee-route CSV supply
none. Where it is silent, either report it as not stated in the provided list,
or verify from SCImago and cite that. Silence is the normal case, not a defect
in the record.

Distinguish coverage from quartile. Scopus coverage is a yes/no; SJR quartile is
a ranking within a subject category. The T&F list carries both, the IEEE list
carries a WoS index column, and the rest carry neither.

If a journal has a quartile in one subject category and a different one in
another, name the category. SCImago assigns a journal to several categories and
"best quartile" is the maximum across them, which is what the T&F list reports.

## APC and cost

State the selected route, author-payable APC, and any separate mandatory fees.
Cite the actual verification date, not "today" if this is a saved snapshot.
Apply the eligibility checks below for institution, date, article type, cap and
approval. Source retrieval, current policy verification, and author-level
approval are three different evidence states. Do not call a conditional route
guaranteed.

Use `other_fees=no` only when the source explicitly says so. Directory
declarations need live confirmation for finalists. A current publisher
statement overrides a stale directory entry; disclose the conflict.
Subscription publication is not
publisher OA, and APC-free publication is not necessarily free of page,
submission, overlength, colour, membership, or mandatory supplementary charges.

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
catalog alone with every unverifiable field marked. Do not skip it. The catalog
still supports scope shortlisting, the OA model, and the fee route with its
stated conditions, and desk-reject risk remains assessable from the manuscript
itself. Quartile and indexing are present for only a small minority of records,
so most entries will carry "not stated in the provided list" rather than a
metric, and no institutional or S2O route may be reported as confirmed from the
snapshot alone.

## Fee eligibility

Use the most recent specific publisher and institution evidence over an older
finder entry. A contract term, a title list, and an author's eligibility are
separate facts. The catalog's `apc_payable=0` describes the route **if its
conditions hold**, never an unconditional promise to the user.

### Institutions

MUJ and JKLU mapping comes from the user, dated 2026-09-19. Original workbooks
are retained unchanged. No current contracts were supplied for those mappings;
their rows say `user_confirmed_mapping`. Do not label them independently
verified, and do not apply MUJ funding to UF or JKLU authors.

UF's [current guide](https://guides.uflib.ufl.edu/openaccess/ufinvests) lists full
coverage at ASME, Cambridge, Canadian Science Publishing, IOP, IWA, JAFSCD,
Microbiology Society, OLH, Rockefeller, RSC, Portland Press, Company of Biologists,
and Royal Society. Title-level records come from the UF-linked
[SciFree finder](https://search.scifree.se/uflib), supplemented by current IOP and
ASME title lists. The guide warns the finder may lag; it is not a final invoice.

Check these material exceptions:

- **IOP:** UF is eligible for lists A, B, C and D with **40 accepted articles per
  year from 1 January**, according to the [current US agreement page](https://publishingsupport.iopscience.iop.org/questions/researchers-from-the-united-states/).
  Remaining quota is unknown. The [current title list](https://publishingsupport.iopscience.iop.org/questions/eligible-journals-transformative-agreements/)
  excludes review article types in *Reports on Progress in Physics*. Do not
  repeat the unlimited claim from the 2022 announcement as current policy.
- **Cambridge:** [SUS Florida terms](https://www.cambridge.org/core/services/open-access-policies/read-and-publish-agreements/oa-agreement-state-university-system-of-florida)
  require an affiliated corresponding author, covered journal, original-research
  eligible type (research, review, rapid communication, brief report, case
  report), and acceptance from 2026-01-01. Finder end dates are metadata and
  require confirmation; do not infer renewal beyond 2026.
- **Microbiology Society:** UF names **Publish & Read Essential**, whose
  [six-title scope](https://www.microbiologyresearch.org/publish-and-read) is
  Microbiology, Microbial Genomics, Access Microbiology, Journal of General
  Virology, Journal of Medical Microbiology, and International Journal of
  Systematic and Evolutionary Microbiology. JMM Case Reports is excluded.
- **Royal Society:** UF names Pack S; [publisher terms](https://royalsociety.org/journals/authors/read-and-publish/)
  identify it as all journals, with the corresponding author's institutional
  eligibility required.
- **Portland Press:** [2026 S2O decision](https://www.biochemistry.org/about-us/news-media/biochemical-society-journals-s2o-decision-2026/)
  opens Biochemical Society Transactions and Essays in Biochemistry. Biochemical
  Journal and Clinical Science did **not** open through S2O in 2026; UF R&P is a
  separate possible route. Emerging Topics in Life Sciences is excluded after
  the [publisher's closure announcement](https://www.biochemistry.org/about-us/news-media/biochemical-society-announces-the-closure-of-emerging-topics-in-life-sciences/).
- **UF discounts excluded from full-coverage CSV:** Elsevier 15%, BMC 15%, MDPI
  10%, ACS USD 250 reduction. ACS Read & Green concerns repository deposit,
  not a full waiver for publisher OA. Books, preprint hosting and internal
  discretionary funds are not journal APC guarantees. See the
  [UF guide](https://guides.uflib.ufl.edu/openaccess/ufinvests).

### Universal routes

**DOAJ:** use exact `APC=No`, never missing values, `APC=Yes` with a waiver, or
an unspecified amount. Keep `Has other fees` separately. Only `No/No` records
are candidate diamond/no-author-fee routes. Check the linked journal policy
because DOAJ declarations can lag or contain errors. Superseded records are
kept for audit but hidden in ordinary search. DOAJ is not exhaustive.

**S2O:** distinguish the general mechanism from the specific funded year. A
library's support does not itself impose a UF-only author restriction. Many
Annual Reviews titles invite contributions; do not suggest them as ordinary
original-research outlets. UF expressly warns of possible page/supplement fees
for its six ASM S2O titles. `s2o` is not an unconditional zero-total-cost flag.

**Subscription:** the non-OA route can have no APC even if an optional OA APC
is advertised. [Springer Nature's policy](https://support.springernature.com/en/support/solutions/articles/6000084580-costs-of-publishing-in-springer-nature-journal)
explicitly warns about page, colour and overlength charges.
[Elsevier's policy](https://www.elsevier.com/about/policies-and-standards/pricing)
allows the subscription route in hybrid journals without an OA APC. Check the
title's current model and all other fees. Never infer this option for a fully
OA title, including ACM's 2026 model.

**Conflicts:** a newer specific author-fee page overrides a directory
declaration. For example, [MELBA](https://www.melba-journal.org/) states no
publication charges but
a USD 10 Scholastica submission charge as checked on 2026-09-19. It is
APC-free, not zero-total-cost. Report conflicting evidence rather than selecting
the most favorable statement. Temporary full waivers must carry their dates;
discretionary hardship waivers are conditional possibilities, not universal free
publication.
