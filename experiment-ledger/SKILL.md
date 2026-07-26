---
name: experiment-ledger
description: >-
  Set up and maintain a reproducible experiment tracking discipline for ML
  research: config-as-file, content-hashed run manifests, an append-only run
  registry, and comparison arms declared before the run rather than selected
  after it. Use whenever the user is designing or running an ablation, sweep, or
  baseline comparison; asks "which config produced this number", "why do these
  two runs disagree", "how do I organize these experiments", or "what should the
  baseline be"; is about to write results into a paper table; or is debugging an
  inconsistency between reported and reproduced results. Also use when setting up
  a new research repo that will run experiments, when a results table needs to be
  regenerated from data, and whenever a comparison risks being assembled from
  whichever runs happen to exist. Prefer this over ad hoc directories and
  spreadsheet tracking.
summary: "Reproducible ML experiment tracking: config-as-file, hashed manifests, honest baselines."
version: "1.0.0"
author: anayy09
license: MIT
metadata:
  status: active
  last_updated: "2026-07-25"
---

# Experiment Ledger

Most irreproducible results are not fabricated. They come from a chain of small
losses: a config edited between runs, a baseline picked after seeing the
outcome, a number retyped into a table, a preprocessing change that predates the
result but postdates the baseline. Each step is defensible alone. Together they
produce a paper whose central comparison cannot be rebuilt.

This skill enforces three properties:

1. **Every number traces to a run.** A metric in a table exists in a registry
   entry with a manifest that pins the code, data, config, and environment.
2. **Comparisons are declared before they are run.** The set of arms, the
   primary metric, and the claim are written down while the outcome is still
   unknown.
3. **Tables are generated, never typed.** A rerun propagates automatically, and
   a number in the abstract cannot disagree with the table.

## The one rule that matters most

**Write down the comparison before you run it.**

A baseline chosen after inspecting results is not a baseline, it is a selection
effect. This is the single most common structural flaw in ML papers, it survives
peer review often enough to be worth exploiting, and it is invisible in the final
manuscript because the prose reads identically either way.

The concrete failure to watch for: an experiment produces several conditions,
then a "consistency" or "agreement" comparison is constructed against whichever
condition makes the contrast cleanest. The measured effect then partly reflects
the choice of contrast rather than the intervention. If a comparison arm was
added after seeing results, that is legitimate exploration, but it must be
labeled exploratory and reported separately from the pre-declared confirmatory
comparison. See `references/preregistration.md`.

Practical test: if the comparison had come out the other way, would the same arm
still have been the baseline? If not, the comparison is post hoc.

## Directory contract

```
project/
  configs/
    base.yaml                  # everything a run needs, no hidden defaults
    arms/prompt_v3.yaml        # overlays, merged onto base
  comparisons/
    prompt_ablation.yaml       # declared arms, primary metric, hypothesis
  runs/
    <run_id>/
      manifest.json            # what produced this run
      config.resolved.yaml     # base + overlays, fully merged
      metrics.json             # scalar results
      predictions.parquet      # per-item outputs, for later re-analysis
      logs/
  ledger/
    runs.jsonl                 # append-only registry, one line per run
  results/
    table_main.tex             # generated, never hand-edited
```

`run_id` is a content hash of the resolved config plus the code commit, so two
runs with identical inputs collide by construction and an accidental config
change produces a visibly different id. That is the point: an id that changes
when nothing changed is annoying, but an id that stays the same when something
changed is a reproducibility failure.

## What the manifest pins

`references/manifest-spec.md` gives the full schema. The fields that are
normally omitted and later needed:

- **Code**: git commit, and whether the working tree was dirty. A dirty tree
  means the run is not reproducible; record it honestly rather than suppressing
  it.
- **Data**: split file hash and row count, not just a dataset name. "NCT-CRC-HE-100K"
  does not identify which patches were held out.
- **Model**: full identifier including revision or commit, plus the serving stack
  version. For a hosted endpoint, the server job id as well, since a restart
  between arms silently changes the comparison.
- **Prompt**: hash of the exact template string. A description of the prompt is
  not a prompt.
- **Randomness**: seed, and whether the run is actually deterministic. Most LLM
  inference under continuous batching is not; say so rather than implying it.
- **Environment**: Python version, key package versions, GPU model, CUDA version.

## Workflow

```bash
# 1. Declare the comparison while the outcome is unknown.
python scripts/ledger.py preregister --name prompt_ablation \
  --arms base,cot,fewshot,structured \
  --primary-metric balanced_accuracy \
  --hypothesis "structured prompting raises balanced accuracy over base by >2 points" \
  --analysis "paired bootstrap over patients, 10k resamples, alpha 0.05"

# 2. Create a run from a config. Prints the run_id and creates runs/<id>/.
RUN=$(python scripts/ledger.py new --config configs/base.yaml --overlay configs/arms/cot.yaml \
        --tag arm=cot --tag comparison=prompt_ablation --quiet)

# 3. Your job writes metrics.json and predictions.parquet into runs/$RUN/.
#    Then register the result.
python scripts/ledger.py record --run "$RUN" --metrics runs/$RUN/metrics.json

# 4. Inspect and generate.
python scripts/ledger.py list --comparison prompt_ablation
python scripts/ledger.py table --comparison prompt_ablation --format latex > results/table_main.tex
python scripts/ledger.py verify
```

`verify` is the step that earns the system. It reports runs whose resolved config
no longer hashes to their id, runs recorded against a comparison but absent from
its declared arms, arms declared but never run, and runs recorded from a dirty
working tree. Run it before every table regeneration and before submission.

## Deciding what counts as a new run

A new run is required when any manifest field changes. In particular, changing
preprocessing invalidates every arm, not just the one being edited. The common
error is re-running one arm after a preprocessing fix and comparing it against
baselines computed before the fix. `verify` catches this by comparing data hashes
across the arms of a comparison and flagging mismatches.

Reruns for variance estimation are different: same config, different seed, and
they should share a `--tag group=<name>` so the table can report mean and spread
rather than a single point. Reporting a single seed as though it were the effect
is how a 0.4 point difference becomes a claim.

## When results go into the paper

The generated table is the source of truth. If a number appears in the abstract,
introduction, or discussion, it must be traceable to a cell in a generated table.
Before submission:

```bash
python scripts/ledger.py verify --strict
python scripts/ledger.py table --comparison <name> --format latex > results/table_main.tex
grep -rn "[0-9]\+\.[0-9]" paper/sections/*.tex | # then check each against the table
```

`references/reproducibility-checklist.md` covers what to put in the paper's
reproducibility statement, what a public artifact release needs, and which items
reviewers at clinical ML venues ask for most often.

## Retrofitting an existing project

Do not try to reconstruct manifests for old runs from memory. Instead:

1. Freeze the current state and initialize the ledger going forward.
2. For each result already in a draft, either re-run it under the ledger or mark
   it explicitly as unverified in the draft.
3. Prioritize re-running the primary comparison. Secondary and exploratory
   results can carry a lower standard as long as the paper labels them as such.

Reconstructing a manifest after the fact produces a document that looks like
provenance and is not. An honest gap is better.

## Reference files

- `references/manifest-spec.md` — full manifest schema, hashing rules, what to
  do when a field is genuinely unknown.
- `references/preregistration.md` — declaring arms, primary versus secondary
  metrics, handling exploratory findings, what to do when the pre-declared
  comparison fails.
- `references/reproducibility-checklist.md` — pre-submission checks, artifact
  release, and the reproducibility statement.
- `assets/config_template.yaml` — starting config with the fields the manifest
  expects.
