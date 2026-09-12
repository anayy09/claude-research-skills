# SKILL-ROUTING.md

Which skill governs which file and which step in `{{PROJECT}}`. Load the
skill before the step, not during it. When a brief names several skills,
each is loaded at the step it governs, and the `PROGRESS.md` entry for that
step names it.

| Step or file | Skill | What it contributes |
|---|---|---|
| Direction, D-001 | `research-ideation` | ranked directions, the falsifiable claim, the kill experiment |
| `PLAN.md`, `DECISIONS.md`, `PROGRESS.md`, `GATES.md`, `RUNBOOK.md`, hand-offs | `project-ledger` | the record itself, its checks, the session bootstrap and hand-off |
| `configs/`, run directories, `RESULTS-LOG.md` run ids, results tables | `experiment-ledger` | config-as-file, hashed manifests, pre-declared comparisons, generated tables |
| Every interval, test, calibration, and noise floor | `ml-eval-statistics` | the unit of resampling, paired tests, multiplicity, MDE |
| Data staging, cohort and feature pipelines, leakage guards | `data-engineering` | schema contracts, validation, incremental loads |
| Cluster jobs, if any | `hpc-cluster` | job scripts, arrays, checkpointing against the wall clock |
| `LIT-REVIEW.md`, every citation, the related-work table, the reference diet | `investigating-sources` | verified sources, version of record, reference diet |
| A formal review with a screening log | `evidence-synthesis` | protocol, PRISMA-S, screening, appraisal, GRADE |
| Manuscript prose | `manuscript-writing` | argument per paragraph, honesty, the tell sweep |
| Revision rounds, response letters, whole-paper coherence, cuts to a page budget | `manuscript-editor` | what goes where, smallest complete change, the cut list |
| Figures | `manuscript-figures` | print-size figures, schematics, compliance check |
| Every built PDF | `build-check` | overflow, floats, page cap, fonts, stale derived files |
| Pre-submission review | `submission-reviewer` | scored review with ranked fixes |
| Venue | `journal-advisor` | shortlist with desk-reject risk |
| Package | `submission-formatter` | template, fidelity check, manifest |
