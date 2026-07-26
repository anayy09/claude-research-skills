# Source Verification

How to confirm a source is real before citing it, and the source-log schema the
verification scripts expect.

## Contents

- Why verification matters
- The source log (schema)
- Verification decision per source
- Worked example
- Running the checker
- Handling FAIL states

## Why verification matters

Language models produce citations that *look* correct: real-sounding authors,
plausible titles, well-formed DOIs, journals that exist. A meaningful fraction
of these were never published. The most dangerous kind is the **mashup**: a real
author, a real journal, and an invented title welded together. It passes every
surface check and only fails when you try to actually find it.

The defense is simple and absolute: **cite only what you have independently
confirmed exists in this session.** Not what you remember, not what sounds
right, not what "a paper probably said." If a search or a database connector did
not return it, it does not get cited.

## The source log

Maintain one JSON file listing every candidate source. It is the single source
of truth that both scripts read. Structure:

```json
{
  "topic": "Short description of the research question",
  "generated": "2026-07-25",
  "sources": [
    {
      "key": "smith2021",
      "type": "journal-article",
      "authors": ["Smith, J.", "Doe, A."],
      "year": 2021,
      "title": "Effect of X on Y: a randomized trial",
      "venue": "Journal of Examples",
      "doi": "10.1234/example.2021.001",
      "url": "https://doi.org/10.1234/example.2021.001",
      "verified": "pending",
      "verify_method": "",
      "tier": "",
      "notes": ""
    }
  ]
}
```

Field notes:

- `key` — short citation handle used inline in the draft as `[smith2021]`. Must
  be unique across the log. This is what `audit_report.py` matches against.
- `type` — one of `journal-article`, `preprint`, `book`, `report`,
  `conference-paper`, `dataset`, `webpage`, `news`, `other`.
- `doi` — bare DOI (`10.xxxx/...`), not a URL. Leave empty if none exists.
- `verified` — `pending`, `confirmed`, or `fail`. The checker updates this.
- `verify_method` — how existence was confirmed: `crossref`, `url-fetch`,
  `mcp:<server>`, `web-search`. Required once `verified` is `confirmed`.
- `tier` — quality grade from `source_quality.md` (`tier_1` … `tier_4`).
- `notes` — flags: conflict of interest, retraction, currency caveat, etc.

Only `key`, `type`, `title`, and `year` are strictly required. Everything with a
DOI should carry it, because that is the strongest automatic check.

## Verification decision per source

For each source, resolve `verified` to `confirmed` or `fail`:

1. **Has a DOI?** Run the checker (below). If Crossref resolves it and the
   metadata roughly matches, set `confirmed` / `crossref`. If it does not
   resolve, do not immediately fail it — a valid paper can have a DOI the API
   misses. Try step 2 before failing.
2. **Fetchable URL or in a connector?** `web_fetch` the page, or locate the item
   through an MCP database (PubMed, bioRxiv, Clinical Trials, etc.). If found and
   it matches, set `confirmed` with the matching method.
3. **Findable by search?** `web_search` for the exact title in quotes plus an
   author. If an independent, credible result confirms it, set `confirmed` /
   `web-search`.
4. **None of the above?** Set `fail`. It is removed from the deliverable along
   with any claim that depended only on it.

Confirming existence is separate from grading quality. A confirmed source can
still be low-tier or flagged; see `source_quality.md`.

## Worked example

Candidate log with three entries in mixed states after checking:

```json
{
  "topic": "Micro-credentials in professional development",
  "generated": "2026-07-25",
  "sources": [
    {
      "key": "kato2020",
      "type": "report",
      "authors": ["Kato, S.", "Galan-Muros, V.", "Weko, T."],
      "year": 2020,
      "title": "The emergence of alternative credentials",
      "venue": "OECD Education Working Papers",
      "doi": "10.1787/b741f39e-en",
      "url": "https://doi.org/10.1787/b741f39e-en",
      "verified": "confirmed",
      "verify_method": "crossref",
      "tier": "tier_3",
      "notes": "Institutional report; high credibility, not peer-reviewed."
    },
    {
      "key": "invented2022",
      "type": "journal-article",
      "authors": ["Real, A.", "Author, B."],
      "year": 2022,
      "title": "A title that was never actually published",
      "venue": "Journal of Real Things",
      "doi": "10.9999/not.a.real.doi",
      "url": "",
      "verified": "fail",
      "verify_method": "",
      "tier": "",
      "notes": "DOI does not resolve; no URL; not found by title search. REMOVE."
    },
    {
      "key": "wsj2026",
      "type": "news",
      "authors": ["Reporter, C."],
      "year": 2026,
      "title": "Employers weigh micro-credentials in hiring",
      "venue": "Wall Street Journal",
      "doi": "",
      "url": "https://www.wsj.com/example-article",
      "verified": "confirmed",
      "verify_method": "url-fetch",
      "tier": "tier_4",
      "notes": "Journalism, not research; use for context only."
    }
  ]
}
```

`invented2022` is exactly the case the skill exists to catch. It does not appear
in the final deliverable.

## Running the checker

```bash
python scripts/check_citations.py sources.json
```

Live, it queries Crossref for each DOI, compares title and first author against
the log, and updates `verified` / `verify_method`. Offline (no network or
`--offline`), it validates DOI syntax, required fields, and duplicate keys, and
marks DOI resolution as skipped rather than passed. `--json` emits a
machine-readable report; the exit code is non-zero if any entry is `fail`, so it
can gate delivery in a script.

## Handling FAIL states

A `fail` is not a warning to note and move past. Before delivering:

- Remove the source from the deliverable.
- Remove or re-source any claim that rested only on it. If another confirmed
  source supports the same claim, re-cite it there.
- Re-run the checker until nothing is in `fail`.

"Difficult to verify" collapses to `fail`. There is no third state.
