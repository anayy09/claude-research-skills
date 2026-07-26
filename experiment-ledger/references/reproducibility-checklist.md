# Pre-submission reproducibility checklist

Run this before the final integration pass on a manuscript. Most items take
minutes; the ones that do not are the ones worth doing.

## Numbers

- [ ] `ledger.py verify --strict` passes with no findings.
- [ ] Every table in the paper is generated from the ledger, not hand-edited.
- [ ] Every numeral in the abstract, introduction, results prose, and conclusion
      matches a cell in a generated table. Grep the sources and check each one.
- [ ] Rounding is consistent and stated. If the table shows 2 decimals, the prose
      does not quote 3.
- [ ] Every reported difference has an interval or a spread, not a bare point
      estimate.
- [ ] The noise floor (rerun of an unchanged arm) is reported, and every claimed
      effect exceeds it.
- [ ] Counts add up: items, patients, slides, excluded cases. A reader summing
      the exclusion flowchart should reach the analysis N exactly.

## Comparisons

- [ ] Each primary comparison has a declaration file predating the runs.
- [ ] The reference arm is the one named in the declaration.
- [ ] The primary metric is the one named in the declaration.
- [ ] Arms added later are labeled exploratory in the text, not folded into the
      confirmatory result.
- [ ] Oracle and upper-bound arms are labeled as such wherever they appear.
- [ ] All arms of a comparison share the same split, preprocessing version, and
      model revision. If not, that is stated.

## Data

- [ ] The split is stored as a file and hashed, not regenerated at runtime.
- [ ] Grouping is respected: no patient appears in both train and test.
- [ ] The unit of analysis is stated explicitly and matches the resampling unit.
- [ ] Class balance of the test set is reported, since accuracy on an unbalanced
      set is uninterpretable without it.
- [ ] Data provenance and access conditions are described accurately, including
      which parts of the data cannot be released.

## Code and environment

- [ ] No result comes from a dirty working tree, or the ones that do are flagged.
- [ ] Environment is pinned (lock file or explicit version list), and the lock is
      in the repository.
- [ ] The entrypoint that produced each result is recorded and still exists in
      the repository at the recorded commit.
- [ ] A fresh clone plus the documented setup runs the smallest experiment end to
      end. Test this on a clean directory, not on the development machine's
      existing environment.

## Release artifact

Reviewers at clinical ML venues increasingly ask for these. Preparing them
before submission is cheaper than doing it under a revision deadline.

- [ ] Repository with code, configs, and split files.
- [ ] `README` that states what can and cannot be reproduced without restricted
      data access, and gives the command that reproduces the main table from
      released artifacts.
- [ ] Per-item predictions for the test set where data terms allow. This lets a
      reader recompute any metric, which is a stronger claim than reporting
      several metrics.
- [ ] Model weights or adapters if the license permits, with the license stated.
- [ ] The declaration files. Publishing them is a credibility signal that costs
      nothing when the work was done properly.

## Reproducibility statement

A short statement covering: what is released, what is withheld and why, the
hardware the results were produced on, the approximate compute cost, and the
level of determinism achieved. Example structure:

> Code, configuration files, and dataset splits are available at <url>.
> Per-patch predictions for the held-out set are included, allowing recomputation
> of all reported metrics. Slide images are governed by the source repository's
> terms and are not redistributed; the manuscript reports the accession
> identifiers required to obtain them. Experiments used N A100 GPUs for
> approximately H GPU-hours. Inference used continuous batching, which is not
> bitwise deterministic; run-to-run variation on an unchanged configuration was
> X points on the primary metric, reported alongside all comparisons.

That last sentence pre-empts the most common methodological objection to LLM
evaluation papers and costs one extra run to earn.

## Things reviewers ask for that are cheap to prepare in advance

- Class-wise results, not only aggregates.
- Calibration reported alongside discrimination.
- Performance stratified by an available confounder (scanner, site, stain batch).
- A failure analysis: which cases fail, and whether the failures are systematic.
- The comparison against a simple baseline that the paper's method should beat
  easily. Its absence is conspicuous, and its presence removes an easy objection.
