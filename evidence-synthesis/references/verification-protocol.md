# Verification protocol

Two independent failure modes, two different checks. Conflating them is why
reference lists pass informal review and fail at proof stage.

| Failure | What it looks like | Caught by |
|---|---|---|
| Fabricated | plausible authors, plausible title, plausible journal, no such paper | metadata lookup against Crossref, DataCite, OpenAlex, or PubMed |
| Mashup | real authors, real journal, title assembled from two real papers | title similarity comparison, not existence check |
| Wrong DOI | the citation is real, the DOI resolves to a different work | comparing the resolved record against the claimed one |
| Retracted | the paper exists and has been withdrawn | retraction status check |
| Corrected | the paper exists and has a correction or expression of concern | update notices on the record |
| Superseded | the citation points at a preprint that has since been peer reviewed and published | record type plus the preprint-to-published relation |
| Unreviewed | the citation is a preprint, working paper, or dataset presented as a peer-reviewed finding | record type from Crossref, DataCite, or OpenAlex |

A DOI that resolves proves the first only. Everything else needs the comparison.

## Why peer-review status is checked from the record, never from the publisher

A rule like "prefer IEEE, Nature, and Elsevier" cannot be implemented by
matching a publisher name or a DOI prefix. SSRN publishes working papers under
Elsevier's registration, and TechRxiv publishes preprints under IEEE's. A filter
on publisher would admit both and would exclude a peer-reviewed society journal
with an unfamiliar prefix.

The script reads `type` and `subtype` from the Crossref record,
`resourceTypeGeneral` from DataCite, and `type` plus
`primary_location.source.type` from OpenAlex. Full signal table and the list of
preprint prefixes are in `references/peer-reviewed-sources.md`.

## Why arXiv needs a second registry

arXiv registers its DOIs with **DataCite**, not Crossref. A verifier that
queries Crossref alone reports every arXiv DOI in a reference list as
nonexistent, which is a fabrication verdict on a real object and the worst error
a citation checker can make. `verify_citations.py` falls back to DataCite on a
Crossref 404 before it will fail anything, and it reconstructs the registered
DOI from a bare `arXiv:2401.01234` string so those references get checked rather
than skipped.

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

# fail anything that is not a peer-reviewed publication
python scripts/verify_citations.py --refs references.md --mailto you@uni.edu \
    --require-peer-reviewed

# find the published version of every preprint in the list
python scripts/verify_citations.py --refs references.md --mailto you@uni.edu \
    --upgrade-preprints

# spot check a few DOIs
python scripts/verify_citations.py --doi 10.1136/bmj.n71 --mailto you@uni.edu

# see what the parser extracted, without network
python scripts/verify_citations.py --refs references.md --offline

# confirm the verdict logic is behaving
python scripts/verify_citations.py --self-test
```

`--upgrade-preprints` checks the Crossref `is-preprint-of` relation, the
bioRxiv and medRxiv APIs, and OpenAlex locations, and prints the DOI to cite
instead. `--require-peer-reviewed` turns "real but unreviewed" from a CHECK into
a FAIL; use it when the protocol restricts the review to the peer-reviewed
record, and leave it off when the protocol admits preprints, in which case the
default CHECK is the reminder to label them.

Provide a real address in `--mailto`. Crossref's polite pool is more reliable
than the anonymous one, and identifying yourself is the condition on which a
free public service stays usable.

## Reading the verdicts

| Verdict | Meaning | Action |
|---|---|---|
| `VERIFIED` | record found, metadata consistent, peer reviewed, no retraction | none |
| `CHECK` | found but something is off: partial title match, year drift, author not on the record, a correction notice, or an unreviewed record type with no published version | look at it; usually a citation error, occasionally a mashup |
| `FAIL` | not found, resolves to a different work, retracted, or a preprint whose peer-reviewed version exists | remove or fix before the document goes anywhere |
| `UNCHECKED` | the service could not be reached | rerun with network access; this is not a finding |

Each reference also carries a peer-review status (`peer-reviewed`, `preprint`,
`not-peer-reviewed`, `unknown`) reported separately from the verdict, so that
"real but not reviewed" and "not real" never collapse into the same finding. A
preprint with a published version is a `FAIL` regardless of the flag, because
the citation points at numbers that changed during review.

Exit status: 0 clean, 1 if anything failed, 2 if anything was unchecked. Suitable
for a pre-submission gate or a git hook.

The `UNCHECKED` distinction matters. An earlier design marked unreachable
lookups as failures, which would tell a user on a restricted network that their
entire genuine bibliography was fabricated. A firewall is not evidence.

## What the script does not prove

- **That the citation supports the claim.** Existence and correct metadata say
  nothing about whether the paper says what you cite it for. Citation-content
  errors are common and only a human reading the paper catches them.
- **That the paper is any good.** Verification is not appraisal. Peer-reviewed
  status is a fact about the venue's process, not a quality verdict: peer review
  admits weak studies routinely, and a rigorous preprint can be better than a
  reviewed paper in a marginal journal. The status determines which version you
  cite and how you label it. Risk of bias is what determines how much weight it
  carries, and that is Step 5, not this script.
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
