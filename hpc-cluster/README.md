# hipergator-hpc

> SLURM jobs and LLM serving on UF HiPerGator, adaptable to any SLURM cluster.

[![Version](https://img.shields.io/badge/version-1.0.0-6E56CF)](../CHANGELOG.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../LICENSE)

Part of **[claude-research-skills](../)** · by [@anayy09](https://github.com/anayy09)

## What it does

Writes, submits, debugs, and monitors SLURM jobs, and stands up LLMs (vLLM,
MedGemma, Gemma, nemotron, gpt-oss) on compute nodes as OpenAI-compatible
endpoints for batch evaluation. It is opinionated toward the University of
Florida's **HiPerGator** cluster — its accounts, QoS, and `/blue` and `/orange`
storage — but the SLURM recipes and troubleshooting transfer to any SLURM site.

## When Claude uses it

- Writing / submitting / debugging a `sbatch` job script
- `srun`, `squeue`, `sacct`, `seff`, job arrays
- GPU allocation, QoS or account errors, "my job is pending forever"
- A job that was killed or ran out of memory
- `/blue` or `/orange` storage and group permissions
- Serving an LLM on a compute node as an OpenAI-compatible endpoint
- "How many GPU hours will this take?"

## What's inside

```
hipergator-hpc/
├── SKILL.md
├── references/
│   ├── slurm-recipes.md              job-script patterns that work
│   ├── serving-llms.md               vLLM / model serving as OpenAI endpoints
│   ├── storage-and-permissions.md    /blue, /orange, group permissions
│   └── troubleshooting.md            pending jobs, OOM, QoS/account errors
└── scripts/
    ├── gen_sbatch.py                 generate a correct sbatch script
    └── gpu_hours.py                  estimate GPU-hour cost of a job
```

## Scripts

```bash
python hipergator-hpc/scripts/gen_sbatch.py --help    # scaffold an sbatch script
python hipergator-hpc/scripts/gpu_hours.py --help     # estimate GPU-hour cost
```

## Changelog

- **1.0.0** — Initial release.

---

Part of the **[claude-research-skills](../)** collection.
[Report an issue »](https://github.com/anayy09/claude-research-skills/issues/new/choose)
