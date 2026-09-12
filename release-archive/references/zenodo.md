# Zenodo deposits

## Concept DOI and version DOI

Every Zenodo record has two DOIs. The **version DOI** identifies one frozen
upload. The **concept DOI** identifies the record across versions and
resolves to the newest one. A manuscript cites the concept DOI in the
availability statement, so a corrected v1.1 is what a reader lands on; a
specific claim that depends on a frozen artifact (a checkpoint, a dataset
snapshot) cites the version DOI as well. `doi_writeback.py` takes both.

The concept DOI is assigned on the first publish and never changes. Do not
publish a throwaway record to "reserve" one; use the sandbox
(`sandbox.zenodo.org`, `--sandbox`) to rehearse, then publish once.

## Metadata

| Field | Value |
|---|---|
| upload_type | `software` for code releases, `dataset` for artifacts alone |
| title | the paper's short title plus "code and artifacts", or the repository name |
| creators | from `AUTHORS.yaml`: `Family, Given`, affiliation, ORCID; the order matches the paper |
| description | the README's first paragraph plus the entry command and the paper citation |
| version | the git tag (`v1.0.0`) |
| license | the repository's license id (`mit`, `apache-2.0`, `cc-by-4.0`) |
| related_identifiers | the paper's DOI with relation `isSupplementTo` once it exists; the GitHub tag URL with `isIdenticalTo` |
| keywords | four to eight, from the manuscript's keywords |
| access_right | `open`, or `embargoed` with a date when the venue requires it |

`zenodo_deposit.py metadata` prints and validates this without a network.
It refuses placeholder text, a missing version, and a creator name that is
not in `Family, Given` form.

## What to upload

- The tag archive (`git archive --format=zip -o release-v1.0.0.zip v1.0.0`),
  so the deposit and the tag are byte-identical.
- The result files the paper's tables and figures are built from, if they
  are too large for the repository.
- Artifacts a claim rests on that cannot be regenerated cheaply: predictions,
  a frozen split, a fitted calibration map.

Not: model checkpoints that regenerate nothing the saved predictions do not
already give, raw data under an agreement, the internal ledgers, anything
over the account's size limit without a reason in the description.

## Versions

A new tag is a new deposit version: `new-version` copies the metadata, takes
a new version string, and with `--replace` drops the old files before
uploading the new ones. The concept DOI stays; the paper's citation does not
change. The response letter, when the new version answers a reviewer, cites
the version DOI for the specific artifact and notes that the concept DOI now
resolves to it.

## The GitHub integration

Zenodo can archive every GitHub release automatically once the repository is
enabled on the Zenodo GitHub page. That produces the same concept and
version DOIs and needs no token in the environment. It is the better route
when the release is only the tag archive; the script is the better route when
artifacts outside the repository are part of the deposit, or when the
metadata needs the paper's DOI and the creators from `AUTHORS.yaml` rather
than the GitHub account names. Do not use both for one repository, or two
concept DOIs will exist.

## Tokens

Create the token on the Zenodo account page with `deposit:write` and
`deposit:actions`. Put it in the environment for the session or in a `.env`
that is gitignored. The script never accepts it as an argument. Revoke it
when the release is done; a token that sits in a `.env` on a laptop is a
token that will be committed by accident one day.

## After publishing

1. `doi_writeback.py` into the manuscript, `CITATION.cff` (`doi:` and
   `identifiers:`), and the response letter.
2. Add the DOI badge to the public README if wanted.
3. Rebuild and run `build-check`; its placeholder check is the last gate.
4. A `project-ledger` progress entry with both DOIs and the tag.
