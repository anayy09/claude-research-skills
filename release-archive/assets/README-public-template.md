# [Repository name]

[One paragraph: the claim the associated paper makes, and what this
repository regenerates from a fresh clone. No project history, no milestones.]

Paper: [Authors]. [Title]. [Venue, year]. https://doi.org/[paper DOI]
Archive: https://doi.org/10.5281/zenodo.[concept DOI]

## Regenerate the results

```bash
pip install -r requirements.txt
export DATA_ROOT=/path/to/data      # see Data below
python make.py all                  # Tables 2-5 and Figures 2-4 into results/ and figures/
```

Runtime on [hardware]: [n] minutes for the tables from the included result
files; [n] hours to re-run every experiment (`python make.py runs`).

## Data

| Dataset | Source | Access | Put it at |
|---|---|---|---|
| [name, version] | [URL or DOI] | [public / credentialed under agreement X] | `$DATA_ROOT/[dir]` |

[One sentence per restricted resource: what the code derives from it, and
that no row-level data is included here.]

## Layout

```
configs/      one YAML per run the paper reports
src/          [what the modules do, by function]
results/      result files the tables and figures are built from
figures/      generated figures
scripts/      make.py and the checks
```

## Cite

See `CITATION.cff`. [Paper citation in the venue's style.]

## License

[MIT for code; CC-BY-4.0 for figures and text in this repository. Data
sources carry their own terms.]
