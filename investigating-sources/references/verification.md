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
      "peer_reviewed": "",
      "superseded_by": "",
      "tier": "",
      "notes": ""
    }
  ]
}
```

Field notes:

- `key`: short citation handle used inline in the draft as `[smith2021]`. Must
  be unique across the log. This is what `audit_report.py` matches against.
- `type`: one of `journal-article`, `preprint`, `book`, `report`,
  `conference-paper`, `dataset`, `webpage`, `news`, `other`.
- `doi`: bare DOI (`10.xxxx/...`), not a URL. Leave empty if none exists.
- `verified`: `pending`, `confirmed`, or `fail`. The checker updates this.
- `verify_method`: how existence was confirmed: `crossref`, `datacite`,
  `url-fetch`, `mcp:<server>`, `web-search`. Required once `verified` is
  `confirmed`.
- `peer_reviewed`: `peer-reviewed`, `preprint`, `not-peer-reviewed`, or
  `unknown`. Written by the checker from the registry record, never inferred
  from the publisher's name. Kept separate from `verified` so that "real but
  unreviewed" and "not real" never collapse into one field.
- `superseded_by`: the DOI of the peer-reviewed version, when the entry is a
  preprint that has since been published. Cite that DOI instead.
- `tier`: quality grade from `source_quality.md` (`tier_1` to `tier_4`).
- `notes`: flags such as conflict of interest, retraction, or currency caveat.

Only `key`, `type`, `title`, and `year` are strictly required. Everything with a
DOI should carry it, because that is the strongest automatic check.

## Verification decision per source

For each source, resolve `verified` to `confirmed` or `fail`:

1. **Has a DOI?** Run the checker (below). If Crossref resolves it and the
   metadata roughly matches, set `confirmed` / `crossref`. If Crossref returns
   404, the checker falls back to **DataCite** before failing anything: arXiv
   registers its DOIs there, so a Crossref-only check reports every arXiv
   citation as a fabrication. If neither registry has it, do not immediately
   fail it. A valid paper can have a DOI the APIs miss. Try step 2 first.
2. **Fetchable URL or in a connector?** `web_fetch` the page, or locate the item
   through an MCP database (PubMed, bioRxiv, Clinical Trials, etc.). If found and
   it matches, set `confirmed` with the matching method.
3. **Findable by search?** `web_search` for the exact title in quotes plus an
   author. If an independent, credible result confirms it, set `confirmed` /
   `web-search`.
4. **None of the above?** Set `fail`. It is removed from the deliverable along
   with any claim that depended only on it.

5. **Is it the version of record?** If the record is a preprint, look for the
   published version before citing it: Crossref's `is-preprint-of` relation, the
   bioRxiv and medRxiv API's `published` field, and OpenAlex `locations`. The
   checker does all three with `--upgrade-preprints`. When one is found, log and
   cite the published DOI and re-read the claim against it; numbers move during
   review. When none is found, the preprint may be cited as `tier_3`, typed
   `preprint`, and labelled as unreviewed in the prose.

Confirming existence is separate from grading quality, and both are separate
from peer-review status. A confirmed source can still be low-tier, unreviewed,
or flagged; see `source_quality.md`.

One trap worth naming. When a title search is used to find a replacement DOI,
near-identity is required, not containment. "Attention Is All You Need" is
contained in "Attention is all you need: utilizing attention in AI-enabled drug
discovery", which is a different paper by different authors in a different
field. Accepting that match would fabricate a citation while appearing to fix
one, so the checker also requires the first author to match.

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
      "peer_reviewed": "not-peer-reviewed",
      "superseded_by": "",
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
      "peer_reviewed": "unknown",
      "superseded_by": "",
      "tier": "",
      "notes": "Not in Crossref or DataCite; no URL; not found by title search. REMOVE."
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
      "peer_reviewed": "not-peer-reviewed",
      "superseded_by": "",
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
python scripts/check_citations.py sources.json --mailto you@institution.edu
python scripts/check_citations.py sources.json --upgrade-preprints
python scripts/check_citations.py sources.json --require-peer-reviewed
python scripts/check_citations.py sources.json --offline
python scripts/check_citations.py --self-test
```

Live, it queries Crossref for each DOI, falls back to DataCite when Crossref has
no record, corroborates retraction status against OpenAlex, compares title and
first author against the log, and updates `verified`, `verify_method`, and
`peer_reviewed`. Offline (no network or `--offline`), it validates DOI syntax,
required fields, and duplicate keys, flags known preprint prefixes as a hint,
and marks resolution as skipped rather than passed.

`--upgrade-preprints` looks for the peer-reviewed version of every preprint and
records it in `superseded_by`. `--require-peer-reviewed` turns any unreviewed
source into a `fail`; use it when the deliverable is restricted to the reviewed
literature. `--write` saves the updated statuses back to the log. `--json` emits
a machine-readable report, and `--self-test` checks the checker's own logic
against fixtures without touching the network. The exit code is non-zero if any
entry is `fail`, so it can gate delivery in a script.

## Handling FAIL states

A `fail` is not a warning to note and move past. Before delivering:

- Remove the source from the deliverable.
- Remove or re-source any claim that rested only on it. If another confirmed
  source supports the same claim, re-cite it there.
- Re-run the checker until nothing is in `fail`.

"Difficult to verify" collapses to `fail`. There is no third state.

A superseded preprint is the one `fail` that is fixed by swapping rather than
removing: replace the DOI with the value in `superseded_by`, update the venue
and year, set `type` to `journal-article`, and re-read the claim against the
published paper before keeping the sentence. Do not swap the DOI and leave the
sentence untouched; that is the whole reason the published version matters.
