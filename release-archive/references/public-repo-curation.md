# Curating the public repository

The internal repository is a laboratory notebook with code in it. The public
repository is a reproduction kit. They share code and result files and
nothing else, and the second is built from the first on purpose, file by
file, not by deleting until it looks clean.

## What each audit finding means

| Finding | Why it matters | What to do |
|---|---|---|
| secret file, token-shaped string | a live credential in a public tree is used within minutes | remove, rotate the credential, and add the pattern to `.gitignore`; check git history, since a removed file is still in it (`git filter-repo` or a fresh history) |
| restricted-data name | a file named `mimic_cohort.csv` is presumptively row-level data under an agreement | never ship rows; ship the cohort *definition* (ids of the query, the script that builds it) and the access route |
| internal document | ledgers and hand-offs narrate the process, cite ids nobody outside can resolve, and sometimes contain names | leave in the internal repo; the public README carries a short "how this was built" if wanted |
| internal ids | `D-041`, `R-0042`, `P5G3` mean nothing to a reader and mark the tree as a copy of something else | replace with the reason the decision recorded, in a sentence, or delete the comment |
| milestone nomenclature | `phase3_runner.py`, `stage2/`, "kill experiment" describe when, not what | rename by function (`train_baselines.py`, `sweeps/`), and rename callers; commit subjects on the public repo describe changes, not milestones |
| local absolute path | breaks on every other machine and names the author's drive | a data root from an environment variable or a config key, with the default documented |
| placeholders | `[AUTHOR INPUT ...]`, `TODO`, `zenodo.XXXXXXX` in a public tree are an unfinished release | resolve before tagging; `doi_writeback.py --check` for the DOI ones |
| large file | git is the wrong store for a 400 MB parquet; clones become slow and the file is not versioned usefully | upload to the Zenodo deposit as an artifact and have the README fetch it |
| no entry command in README | a reader cannot tell how to regenerate a number | one command near the top: `python make.py all`, `make figures`, `snakemake` |
| no CITATION.cff | GitHub and Zenodo read it; without it the citation is guessed | `assets/CITATION.cff`, creators from `AUTHORS.yaml`, DOI after the first deposit |
| no environment file | the code will not run the same way twice | `requirements.txt` with pinned versions, or `environment.yml`, or a Dockerfile |

## Renaming without breaking

Milestone words are removed by renaming to function, never by deleting the
code. Procedure: list every occurrence (`grep -rn "phase\|stage" --include=*.py`),
decide the functional name for each module and identifier, rename with the
editor's refactor or `git mv` plus a search-and-replace limited to
identifiers, run the entry command, and diff the regenerated numbers against
the results log. A rename that changes a number is a bug in the rename.

Comments that cite a decision id are rewritten to say the decision:
`# D-041: parser reads LABEL line only` becomes
`# The parser reads only the LABEL line; matching anywhere in the response
# mis-classified 5.7 percent of answers.`

## The README

Order, from `assets/README-public-template.md`:

1. One paragraph: what the paper claims and what this repository regenerates.
2. The entry command, and what it produces (which tables and figures, where).
3. Data: what to obtain, from where, under what agreement, and where to put
   it. Never instructions that would breach the agreement.
4. Environment: the one-line install, the Python or R version, the GPU if
   any, the expected runtime.
5. Layout: the directories a reader will open.
6. How to cite: the paper and the archive DOI, from CITATION.cff.
7. License.

No project history, no milestones, no status table, no "phase" words.

## Licenses

MIT or Apache-2.0 for code; CC-BY-4.0 for documents and figures; CC0 for
data the authors own. A repository with code and data may carry two, stated
in the README. Data under someone else's agreement carries no license
because it is not there.

## The reproduction test

Before tagging: clone into an empty directory, create the environment from
the environment file, obtain or point at the data as the README says, run
the entry command, and compare every number the paper reports with the
regenerated output. `project-ledger`'s results log is the reference. Record
the test as a progress entry with the commit and the count of numbers
checked. A release whose reproduction test was not run is not a release.
