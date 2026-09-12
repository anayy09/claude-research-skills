---
name: release-archive
description: >-
  Turn an internal research repository into a public reproducibility release
  and archive it with a DOI: audit what must not ship (secrets, data under a
  use agreement, ledgers and hand-off notes, decision ids and milestone
  nomenclature, local paths, placeholders), curate the public repository
  (code that regenerates every number, configs, cited result files, README
  with an entry command, LICENSE, CITATION.cff), tag a release, deposit it
  on Zenodo with creators taken from AUTHORS.yaml, and write the concept DOI
  back into the availability statement, CITATION.cff, and the response
  letter. Use whenever the user says "Zenodo", "mint a DOI", "publish the
  code", "make the repo public", "the public repo is outdated", "add the
  artifacts as a new version", "code availability statement", "data
  availability", "reproducibility archive", "release v1.0", or "push to the
  public repo"; and before any manuscript that promises archived code is
  submitted. Never mints a DOI while the manuscript carries a placeholder.
summary: "Public reproducibility release: audit, curate, tag, Zenodo deposit with a DOI, write-back."
version: "1.0.0"
author: anayy09
license: MIT
metadata:
  status: active
  last_updated: "2026-09-12"
---

# Release Archive

A manuscript that says "code is available at" is making a promise a reviewer
will test. The public repository has to regenerate the paper's numbers from
a fresh clone, carry nothing that was internal (a decision log, a hand-off
brief, a token, a cohort under a data-use agreement), and be frozen at a DOI
that the paper cites. The internal repository, run by `project-ledger`, is
none of those things by design. This skill is the path from one to the other,
and the deposit script that has otherwise been rewritten in every project.

## Scope, and what belongs elsewhere

This skill owns the public release and its archive. It does not:

- Keep the internal record. `project-ledger`; its ids and vocabulary are
  exactly what this skill strips.
- Register runs or pin manifests. `experiment-ledger`; the release carries
  its manifests and result files, not its registry.
- Write the availability statement's science or the manuscript around it.
  `manuscript-writing` and `manuscript-editor`; this skill supplies the
  wording pattern and the DOI.
- Verify the built PDF after the write-back. `build-check`, whose
  placeholder check is the last gate before submission.

## What ships and what does not

| Ships | Stays internal |
|---|---|
| code needed to regenerate every number, figure, and table in the paper | ledgers: DECISIONS, PROGRESS, RESULTS-LOG, GATES, RUNBOOK, AGENT, hand-backs, starter prompts |
| configs and manifests for the runs the paper reports | exploratory runs the paper does not report |
| result files the figures are built from (CSV, JSON, parquet under the size limit) | raw data under a data-use agreement (MIMIC, PhysioNet, eICU, any PHI): pointer and access route only |
| figure and table scripts | scratch analyses, notebooks that were never re-run |
| README with one entry command, environment file, LICENSE, CITATION.cff | `.env`, tokens, cookies, local paths |
| a CHANGELOG or release notes for each version | milestone vocabulary in code, identifiers, commit subjects, branch names |

The test: a stranger with the README, the environment file, and access to
the data can produce Table 2 and Figure 3 without asking a question.

## Workflow

### 1. Audit the tree

```bash
python scripts/release_audit.py path/to/public-repo --strict
```

Secrets, restricted-data names, and a missing README or LICENSE are FAILs.
Internal ids, milestone nomenclature, local paths, placeholders, ledger
documents, large files, and missing CITATION.cff are WARNs, each with the
file. Fix every FAIL and either fix or justify every WARN before tagging.
`references/public-repo-curation.md` says what to do with each finding and
how to strip nomenclature without breaking the code.

### 2. Curate

Build the public tree from the internal one deliberately, never by copying
everything and deleting. Rename milestone-named modules and functions by
what they do. Replace decision ids in comments with the reason the decision
recorded. Point data loaders at a documented data root and say where the
data comes from and under what agreement. Write the README from
`assets/README-public-template.md`: what the paper claims, the one command
that regenerates it, what data to obtain and how, expected runtime, and how
to cite. Add `CITATION.cff` from `assets/CITATION.cff` with the creators from
`AUTHORS.yaml`.

Re-run the audit. Then run the entry command from a fresh clone in a clean
environment and compare the regenerated numbers against the manuscript's
results log. A number that does not reproduce is a finding for
`project-ledger`, not something to paper over here.

### 3. Tag

```bash
git tag -a v1.0.0 -m "Release for <paper short title>, submitted <venue> <date>"
git push origin v1.0.0
```

The tag is what the deposit archives. Nothing is deposited from a working
tree.

### 4. Deposit

```bash
python scripts/zenodo_deposit.py metadata --title "..." --version v1.0.0 --description-file README.md \
    --related-doi 10.xxxx/paper --authors AUTHORS.yaml
python scripts/zenodo_deposit.py create  --title "..." --version v1.0.0 --description-file README.md \
    --upload release-v1.0.0.zip --sandbox          # rehearse on the sandbox first
python scripts/zenodo_deposit.py create  ... --publish
python scripts/zenodo_deposit.py new-version --concept-doi 10.5281/zenodo.NNNNNNN --version v1.1.0 \
    --upload release-v1.1.0.zip --replace --publish
```

The token comes from `ZENODO_TOKEN` in the environment or `.env`, never from
the command line, never printed. Creators come from `AUTHORS.yaml` and are
never typed. `metadata` validates without a network and refuses placeholder
text. `references/zenodo.md` covers concept versus version DOIs, what to
upload (the tag archive plus the artifacts the paper's numbers rest on, not
the model checkpoints that regenerate nothing), embargoes, and the GitHub
integration alternative.

### 5. Write back

```bash
python scripts/doi_writeback.py --doi 10.5281/zenodo.NNNNNNN --version-doi 10.5281/zenodo.NNNNNNM \
    paper/main.tex CITATION.cff letter/response.md
python scripts/doi_writeback.py --check paper/main.tex CITATION.cff
```

The manuscript cites the concept DOI, which resolves to the newest version.
The availability statement follows `references/availability-statements.md`
for the venue family; data under an agreement is described by its access
route, and "available on reasonable request" carries the reason. Then
rebuild and run `build-check`; its placeholder check fails on anything the
write-back missed.

## Rules

- **No DOI while a placeholder remains.** `doi_writeback.py --check` and
  `build_check.py` both refuse. A minted DOI cannot be unminted.
- **Creators and affiliations come from `AUTHORS.yaml`** or the owner. A
  deposit with a guessed affiliation is a public record with a wrong name on
  it.
- **Credentials from the environment only.** A token on a command line lands
  in shell history and in the transcript.
- **Restricted data never ships.** MIMIC, PhysioNet, eICU, and any PHI: the
  README names the resource, the access route, and the credentialing, and
  the loader reads from a data root the user sets.
- **Internal vocabulary never ships.** Decision ids, gate names, phase
  labels, run-registry paths, hand-off notes. The audit lists them; the
  curation removes them by rewriting, not by search-and-replace into
  nonsense.
- **The release reproduces.** The entry command was run from a fresh clone
  before the tag, and the numbers matched the results log.
- **Each new version is a new deposit version**, not an edit of the old one,
  with a version string matching the git tag, and the paper's concept DOI
  unchanged.

## Reference files

| File | Read it when |
|---|---|
| `references/public-repo-curation.md` | building the public tree; what each audit finding means; renaming without breaking; the README shape; licenses |
| `references/zenodo.md` | depositing; concept versus version DOI; metadata fields; what to upload; sandbox; the GitHub integration |
| `references/availability-statements.md` | writing the code and data availability statements for Nature, Elsevier, IEEE, BMC, PLOS families; restricted data; "on request" |
| `assets/README-public-template.md` | the public README |
| `assets/CITATION.cff` | the citation file |

## Loading discipline

Load this skill once per session, before the step it governs, and do not
invoke it again when it is already in context; a second load re-injects the
same text and nothing else. When a repository carries `docs/SKILL-ROUTING.md`
(`project-ledger`), it names the skill for each step and file; follow it, and
record the skill in that step's progress entry. When a brief names several
skills, each is loaded at the step it governs, not all at the start.
