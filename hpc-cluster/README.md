# hpc-cluster

> Write, debug, and monitor cluster batch jobs, and serve models on compute nodes.

[![Version](https://img.shields.io/badge/version-2.0.0-6E56CF)](../CHANGELOG.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../LICENSE)

Part of **[claude-research-skills](../)** · by [@anayy09](https://github.com/anayy09)

## What it does

Turns a vague "run this on the cluster" into a job script that will not waste a
day of queue time, and turns a scheduler error into a diagnosis. It covers the
whole loop: discovering what the site actually offers, placing data on the right
filesystem, writing the script, sharding the work into an array, standing up an
inference server on the allocated node, and reading the post-mortem afterwards.

Cluster work fails in a small number of predictable ways — wrong account or
queue, data on the wrong filesystem, a job that dies at hour 71 of a 72 hour wall
clock with no checkpoint, permissions on a shared group directory. Every recipe
here exists to make one of those failures either impossible or cheap.

Two rules run through all of it:

- **Never submit a long job you have not first run for two minutes.** A five
  minute smoke test on a tiny input routinely saves a day of queue time.
- **Read the site, do not assume it.** Partitions, QoS names, filesystem mounts,
  accounting units, and purge policies are set per site and change. The skill
  queries the cluster and says which facts came from it and which the user
  supplied, rather than emitting a script full of plausible guesses.

## Site-agnostic by construction

Nothing here is tied to one cluster. Filesystems are addressed by role
(`$HOME`, `$SCRATCH`, `$PROJECT`, `$TMPDIR`) so a script moves between sites by
changing one line. Priority tiers are described by behavior — guaranteed versus
preemptible — rather than by any one site's naming. Local wrapper commands are
treated as something to discover, not to assume.

SLURM is the worked-out default because it runs most academic and national-lab
clusters. `references/scheduler-portability.md` maps every directive, command,
and environment variable to **PBS/Torque, LSF, and SGE**, including the traps
that bite on a port: SGE's per-slot `h_vmem`, PBS not starting in the submit
directory, and node lists arriving as a variable on some schedulers and a file
on others.

## When Claude uses it

- Writing, submitting, or debugging a job script
- `sbatch`, `srun`, `squeue`, `sacct`, `seff` — or `qsub`, `qstat`, `bsub`
- GPU allocation, account or QoS errors, "my job is pending forever"
- A job that was killed, ran out of memory, or hit the wall clock
- Scratch, project, and archive filesystems; group permissions and ACLs
- Job arrays, dependency chains, checkpoint-and-resume, preemptible jobs
- Apptainer/Singularity containers on a cluster
- Serving a model on a compute node as an OpenAI-compatible endpoint
- "How many GPU hours will this take?"

It triggers on a pasted scheduler error or job log with no other context, which
is how these questions usually arrive.

## What's inside

```
hpc-cluster/
├── SKILL.md
├── references/
│   ├── slurm-recipes.md            interactive, checkpoint/resume, multi-GPU, arrays,
│   │                               dependencies, preemptible jobs, requeue, containers
│   ├── storage-and-scratch.md      filesystem roles, the small-file problem, staging,
│   │                               ACLs, quota and inode diagnosis, purge, restricted data
│   ├── serving-llms.md             inference server on a node, readiness, tunneling,
│   │                               concurrency, determinism for ablations
│   ├── troubleshooting.md          symptom → cause → fix, from rejection to wrong results
│   └── scheduler-portability.md    SLURM ↔ PBS/Torque ↔ LSF ↔ SGE
└── scripts/
    ├── gen_sbatch.py               generate a job script with the safety boilerplate
    └── gpu_hours.py                estimate GPU-hours and shape the array
```

## Scripts

Standard library only. Neither script talks to a scheduler — they print, you
review, you submit.

```bash
# single GPU job
python hpc-cluster/scripts/gen_sbatch.py --name infer --account myproj \
  --partition gpu --gpu 1 --cpus 8 --mem 64gb --time 04:00:00 \
  --module conda --activate 'conda activate myenv' \
  --cmd "python -u infer.py --config configs/base.yaml" > jobs/infer.sbatch

# array over a manifest, 8 concurrent, idempotent on resubmit
python hpc-cluster/scripts/gen_sbatch.py --name process --account myproj \
  --partition gpu --qos normal --gpu a100:1 --array 1-500 --throttle 8 \
  --manifest '$WORK/manifests/items.txt' \
  --cmd 'python -u process.py --input "$LINE" --out "$OUT.tmp"' > jobs/process.sbatch

# cost estimate and array shape, from a measured throughput
python hpc-cluster/scripts/gpu_hours.py --items 412000 --throughput 6.2 \
  --arms 5 --overhead 0.25 --max-concurrent 8
```

Every generated script carries `set -euo pipefail`, caches redirected off
`$HOME`, a per-job output directory, and — for arrays — a skip-if-complete guard
with write-to-`.tmp`-then-`mv`, so a resubmission after preemption reruns only
the missing work and a killed task never leaves a truncated file that looks
finished.

## Fits with

[`experiment-ledger`](../experiment-ledger) for recording which config produced
which run, [`ml-eval-statistics`](../ml-eval-statistics) for what to do with the
numbers once the jobs finish, and [`research-ideation`](../research-ideation)
when the question is which experiments are worth the allocation in the first
place.

## Changelog

- **2.0.0** — Generalized to any HPC cluster. Breaking: the skill was renamed
  from `hipergator-hpc` to `hpc-cluster`, so remove the old folder from your
  skills directory. Site-specific paths, accounts, QoS names, and wrapper
  commands are replaced by filesystem roles and discovery steps;
  `storage-and-permissions.md` is now `storage-and-scratch.md`; added
  `scheduler-portability.md` for PBS/Torque, LSF, and SGE, plus new material on
  containers, purge policies, accounting units, and offline weight staging.
  `gen_sbatch.py` gains `--module` and `--activate` and no longer assumes conda
  or a fixed filesystem layout.
- **1.0.0** — Initial release.

---

Part of the **[claude-research-skills](../)** collection.
[Report an issue »](https://github.com/anayy09/claude-research-skills/issues/new/choose)
