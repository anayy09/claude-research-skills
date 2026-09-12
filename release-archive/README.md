# release-archive

> Public reproducibility release: audit, curate, tag, Zenodo deposit with a DOI, write-back.

[![Version](https://img.shields.io/badge/version-1.0.0-6E56CF)](../CHANGELOG.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../LICENSE)

Part of **[claude-research-skills](../)** · by [@anayy09](https://github.com/anayy09)

## What it does

Takes a research project from its internal repository, with ledgers,
hand-off notes, decision ids, and a data root under an agreement, to a public
repository that regenerates the paper's numbers from a fresh clone, frozen at
a Zenodo DOI the paper cites. It gives the agent:

- **An audit** (`release_audit.py`) that fails on secrets, restricted-data
  names, and a missing README or LICENSE, and warns on internal ids, milestone
  nomenclature, local paths, placeholders, ledger documents, large files, and
  a missing CITATION.cff, each with the file.
- **A curation procedure**: what ships and what stays, how to rename
  milestone-named code by what it does, the README shape with one entry
  command, the fresh-clone reproduction test against the results log.
- **A deposit script** (`zenodo_deposit.py`) for create, new-version,
  inspect, and metadata validation, with the token from the environment or
  `.env` only, creators from `AUTHORS.yaml`, sandbox rehearsal, and both DOIs
  printed after publish.
- **A write-back script** (`doi_writeback.py`) that puts the concept DOI into
  every waiting site (manuscript, CITATION.cff, response letter) and reports
  what is still a placeholder.
- **Availability-statement wording** per venue family, including restricted
  data and the reason an "on request" statement needs.

## When Claude uses it

- "Publish the code and add the Zenodo link"
- "Add the artifacts to Zenodo as a new version"
- "The public repo is outdated; the internal one has milestone naming"
- "Write the code and data availability statements"
- "Make a public repo and replace the placeholder DOI"
- Before submitting any manuscript that promises archived code

Hands off elsewhere: [`project-ledger`](../project-ledger) keeps the
internal record this skill strips, [`experiment-ledger`](../experiment-ledger)
owns the manifests the release carries, [`manuscript-editor`](../manuscript-editor)
places the availability statement, [`build-check`](../build-check) catches
any placeholder the write-back missed.

## What's inside

```
release-archive/
├── SKILL.md
├── references/
│   ├── public-repo-curation.md     what ships, what each audit finding means, renaming, README, licenses
│   ├── zenodo.md                   concept vs version DOI, metadata, what to upload, sandbox, GitHub integration
│   └── availability-statements.md  wording by venue family; restricted data; "on request"
├── assets/
│   ├── README-public-template.md   the public README shape
│   └── CITATION.cff                citation file template
└── scripts/
    ├── release_audit.py            audit a tree before it ships
    ├── zenodo_deposit.py           create, new-version, inspect, metadata (token from env only)
    └── doi_writeback.py            write the DOI into every placeholder site; --check for leftovers
```

## Scripts

```bash
python release-archive/scripts/release_audit.py public-repo --strict
python release-archive/scripts/zenodo_deposit.py metadata --title "..." --version v1.0.0 --description-file README.md
python release-archive/scripts/zenodo_deposit.py create --title "..." --version v1.0.0 --upload release.zip --sandbox
python release-archive/scripts/zenodo_deposit.py new-version --concept-doi 10.5281/zenodo.NNNNNNN --version v1.1.0 --upload release.zip --replace --publish
python release-archive/scripts/doi_writeback.py --doi 10.5281/zenodo.NNNNNNN paper/main.tex CITATION.cff
python release-archive/scripts/doi_writeback.py --check paper/main.tex
python release-archive/scripts/release_audit.py --self-test
python release-archive/scripts/zenodo_deposit.py --self-test
python release-archive/scripts/doi_writeback.py --self-test
```

Standard library only; `requests` is used for the Zenodo API when installed
and urllib otherwise. `ZENODO_TOKEN` is read from the environment or a
`.env` file and is never accepted as an argument or printed.

## Changelog

- **1.0.0**: Initial release.

---

Part of the **[claude-research-skills](../)** collection.
[Report an issue »](https://github.com/anayy09/claude-research-skills/issues/new/choose)
