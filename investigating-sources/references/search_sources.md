# Search Sources

Where to look, in what order, and how to make the peer-reviewed literature the
thing that comes back first. Read this in SEARCH, before running any query.

## Contents

- The search order
- Publisher and index surfaces
- Keyless APIs a script can actually call
- Query recipes
- Preprints: finding them, and not citing them
- What each surface will not tell you

## The search order

Search the reviewed record first and the open web last. Running it the other way
around is how a blog post ends up as the backbone of a report, with the peer
reviewed paper it was summarising never cited.

1. **Domain databases**, through whichever MCP connectors are available (PubMed,
   Europe PMC, ClinicalTrials.gov, and others the user has connected). These
   return structured metadata that can be logged directly.
2. **Federated indexes**: Scopus and Web of Science where the user has access;
   Europe PMC and OpenAlex where they do not, both of which are free.
3. **Publisher platforms** for the field in question: IEEE Xplore for
   engineering and computer science, the ACM Digital Library for computing,
   SpringerLink and nature.com for the Nature portfolio and Springer journals,
   ScienceDirect for Elsevier journals, Wiley Online Library.
4. **Preprint servers**, deliberately and last, to catch work too recent to have
   been reviewed. Everything found here gets checked for a published version
   before it is cited.
5. **Grey literature and web**: institutional and government reports, standards
   bodies, quality journalism. Real sources, lower tier, cited as what they are.

Do not stop at step 1 because it returned enough results. Coverage between these
surfaces is partial and non-overlapping, and "enough results" is a statement
about the searcher's patience rather than about the literature.

## Publisher and index surfaces

| Surface | Best for | How to reach it |
|---|---|---|
| IEEE Xplore | engineering, signal processing, computer vision, hardware; the peer-reviewed conference literature | web command search; `site:ieeexplore.ieee.org` in `web_search` |
| ACM Digital Library | computing; ACM conference proceedings are the reviewed venue of record | web advanced search; `site:dl.acm.org` |
| SpringerLink / nature.com | Nature portfolio, Springer journals, life and physical sciences | `site:nature.com`, `site:link.springer.com` |
| ScienceDirect | Elsevier journals, full text | `site:sciencedirect.com` |
| Wiley Online Library | Wiley journals, Cochrane Library | `site:onlinelibrary.wiley.com` |
| PubMed / Europe PMC | biomedical and clinical, free | MCP connector, or the Europe PMC REST API |
| Scopus / Web of Science | multidisciplinary, citation counts, exportable result sets | subscription required |
| OpenAlex | multidisciplinary, free, good metadata, weak relevance ranking | REST API, no key |

A `site:` restricted `web_search` is a real and effective way to reach a
publisher platform when no API key is available. It is not equivalent to running
the platform's own search: coverage is whatever the search engine indexed, and
results are not exportable. Say which one you did in the methods note.

## Keyless APIs a script can actually call

These need no key, no subscription, and no institutional network. They are what
`scripts/check_citations.py` uses.

| API | Endpoint | Gives you |
|---|---|---|
| Crossref | `https://api.crossref.org/works/<doi>` | metadata, record `type`, retraction notices via `updated-by`, `relation.is-preprint-of` |
| Crossref search | `https://api.crossref.org/works?query.bibliographic=<title>&filter=type:journal-article` | peer-reviewed matches by title |
| DataCite | `https://api.datacite.org/dois/<doi>` | arXiv and repository DOIs, which Crossref does not have |
| DOI registration agency | `https://doi.org/ra/<prefix>` | whether a prefix is Crossref or DataCite |
| OpenAlex | `https://api.openalex.org/works/doi:<doi>` | `type`, `is_retracted`, `primary_location.version`, all versions in `locations` |
| OpenAlex sources | `https://api.openalex.org/sources/issn:<issn>` | `is_core`, `is_in_doaj`, venue `type` |
| DOAJ | `https://doaj.org/api/search/journals/issn:<issn>` | `bibjson.editorial.review_process`, an explicit statement of the venue's peer-review model |
| Europe PMC | `https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=<q>&format=json` | biomedical search, `SRC:PPR` marks preprints |
| bioRxiv / medRxiv | `https://api.biorxiv.org/details/biorxiv/<doi>` | `published`, the journal DOI of the peer-reviewed version |
| Semantic Scholar | `https://api.semanticscholar.org/graph/v1/paper/DOI:<doi>` | `publicationVenue.type`, `externalIds` including the arXiv ID |

Send a `mailto` to Crossref and OpenAlex. The polite pool is more reliable, and
identifying yourself is the condition on which a free public service stays free.

## Query recipes

**Scope a title search to peer-reviewed journal articles.**

```
https://api.crossref.org/works?query.bibliographic=<title>
  &filter=type:journal-article&rows=5&mailto=<you@institution.edu>
```

**Scope to one publisher's peer-reviewed output.** Add a Crossref member ID.
These were confirmed against the live API: IEEE 263, Elsevier 78, Springer
Nature 297, ACM 320, Wiley 311.

```
&filter=type:journal-article,member:263
```

Always pair `member` with `type:journal-article`. Member 78 also returns SSRN
working papers and member 263 also returns TechRxiv preprints, so the member
filter alone does the opposite of what it looks like it does.

**Exclude preprints from a biomedical search.**

```
https://www.ebi.ac.uk/europepmc/webservices/rest/search
  ?query=<terms> NOT SRC:PPR&format=json
```

**Reach a publisher platform through web search.**

```
web_search: "<exact phrase>" site:ieeexplore.ieee.org
web_search: <topic> site:nature.com OR site:link.springer.com
web_search: <topic> site:sciencedirect.com
```

## Preprints: finding them, and not citing them

Preprints are worth finding. In fast-moving fields the peer-reviewed record lags
by a year or more, and ignoring preprints means writing about the state of the
field as it was. The rule is not "do not read preprints." It is **cite the
version of record**.

Before any preprint goes in the source log:

1. Check Crossref `relation["is-preprint-of"]` on the preprint's DOI.
2. For a bioRxiv or medRxiv DOI (`10.1101/...`), check the bioRxiv API's
   `published` field.
3. Check OpenAlex `locations` for a `source.type == "journal"` entry with
   `version == "publishedVersion"`.
4. Search the exact title on Crossref with `filter=type:journal-article`, and
   confirm the authors match before accepting the hit.

`scripts/check_citations.py` does all four with `--upgrade-preprints`.

If a published version exists, log and cite that one, and re-read the claim
against it. Numbers move during review: an effect size, a sample size, or a
conclusion can differ between the preprint and the paper, and citing the preprint
attributes to the authors something they revised.

If no published version exists, a preprint may still be cited when it is the
best available evidence, provided it is:

- typed `preprint` in the source log, not `journal-article`;
- graded `tier_3`, never `tier_1` or `tier_2`, regardless of the authors;
- labelled in the prose, so the reader knows what they are being shown, for
  example "in a preprint that has not been peer reviewed, Chen et al. report ...";
- named in the limitations section as unreviewed evidence the conclusion rests on.

Never treat an arXiv identifier as an absence of a paper. Many arXiv preprints
were published at conferences whose proceedings carry no Crossref DOI, so a
failed lookup means "not found in this registry", not "never published". Check
the venue before concluding a work is unreviewed.

## What each surface will not tell you

- **Google Scholar** is not reproducible. Results are personalized, counts are
  unstable across runs, and it silently mixes preprint and published versions of
  the same work. Use it to find a known item or to chase citations, never as the
  documented search of record.
- **Crossref** is a registration agency, not a bibliographic database. Its
  subject indexing is thin and its relevance ranking is not a controlled
  vocabulary search. Absence from Crossref is not absence from the literature:
  books, older work, theses, and many conference proceedings are not there.
- **A resolving DOI** proves a record exists, not that the paper says what you
  cite it for, not that the venue is reputable, and not that the paper has not
  been retracted. Those are separate checks.
- **Publisher name** proves nothing about peer review. See the prefix table in
  `source_quality.md`.
