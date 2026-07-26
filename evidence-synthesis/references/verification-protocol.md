# Verification protocol

Two independent failure modes, two different checks. Conflating them is why
reference lists pass informal review and fail at proof stage.

| Failure | What it looks like | Caught by |
|---|---|---|
| Fabricated | plausible authors, plausible title, plausible journal, no such paper | metadata lookup against Crossref, OpenAlex, or PubMed |
| Mashup | real authors, real journal, title assembled from two real papers | title similarity comparison, not existence check |
| Wrong DOI | the citation is real, the DOI resolves to a different work | comparing the resolved record against the claimed one |
| Retracted | the paper exists and has been withdrawn | retraction status check |
| Corrected | the paper exists and has a correction or expression of concern | update notices on the record |

A DOI that resolves proves the first only. Everything else needs the comparison.

## Why the retraction check is separate

Crossref acquired the Retraction Watch database and exposes it through the REST
API: a retracted work carries `updated-by` entries pointing at the notice, and
the notice carries `update-to` pointing back, with a `source` field
distinguishing publisher-supplied from Retraction Watch records. OpenAlex
exposes the same fact more simply as `is_retracted`.

The two sources update on different schedules and disagree at the margin.
`scripts/verify_citations.py` queries both and reports disagreement rather than
picking a winner, because a conflict is a signal to look manually, not noise to
be smoothed.

Language models are unreliable at this specific task. Asking a model whether a
paper has been retracted produces a confident answer with no relationship to the
retraction record, because retraction status is a fact about the world after
training and often after publication of the citing work. It has to be looked up.

## Running it

```bash
# reference list, any common format
python scripts/verify_citations.py --refs references.md --mailto you@uni.edu

# BibTeX
python scripts/verify_citations.py --refs refs.bib --mailto you@uni.edu

# spot check a few DOIs
python scripts/verify_citations.py --doi 10.1136/bmj.n71 --mailto you@uni.edu

# see what the parser extracted, without network
python scripts/verify_citations.py --refs references.md --offline

# confirm the verdict logic is behaving
python scripts/verify_citations.py --self-test
```

Provide a real address in `--mailto`. Crossref's polite pool is more reliable
than the anonymous one, and identifying yourself is the condition on which a
free public service stays usable.

## Reading the verdicts

| Verdict | Meaning | Action |
|---|---|---|
| `VERIFIED` | record found, metadata consistent, no retraction | none |
| `CHECK` | found but something is off: partial title match, year drift, author not on the record, or a correction notice exists | look at it; usually a citation error, occasionally a mashup |
| `FAIL` | not found, resolves to a different work, or retracted | remove or fix before the document goes anywhere |
| `UNCHECKED` | the service could not be reached | rerun with network access; this is not a finding |

Exit status: 0 clean, 1 if anything failed, 2 if anything was unchecked. Suitable
for a pre-submission gate or a git hook.

The `UNCHECKED` distinction matters. An earlier design marked unreachable
lookups as failures, which would tell a user on a restricted network that their
entire genuine bibliography was fabricated. A firewall is not evidence.

## What the script does not prove

- **That the citation supports the claim.** Existence and correct metadata say
  nothing about whether the paper says what you cite it for. Citation-content
  errors are common and only a human reading the paper catches them.
- **That the paper is any good.** Verification is not appraisal.
- **That an unretracted paper is reliable.** Retraction is a lagging indicator;
  many flawed papers are never retracted.
- **That coverage is complete.** Crossref covers works with DOIs. Books, older
  literature, some conference proceedings, theses, and grey literature may be
  absent, and a `FAIL` on those should be checked by hand rather than treated as
  a fabrication verdict.

## Manual verification when the automated check cannot help

For anything without a DOI: find the item in the publisher's own catalogue or in
a library catalogue, confirm the title, authors, year, and page range, and record
where you confirmed it. For a conference paper, the proceedings entry. For a
thesis, the institutional repository.

If you cannot confirm it exists, it does not go in the document. There is no
category of citation that is too useful to verify.

## Where to run this in the workflow

- After drafting any section that cites, not only at the end.
- Before sending a draft to a co-author, so that the co-author is not the
  verification mechanism.
- Before submission, as the final gate, together with the search update.
- On the reference list of a review you are about to rely on heavily; retracted
  primary studies inside an existing review are a known and unfixed problem, and
  finding one changes how much weight that review can carry.
