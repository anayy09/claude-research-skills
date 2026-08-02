---
name: hpc-cluster
description: >-
  Write, submit, debug, and monitor batch jobs on a shared HPC cluster, and
  serve models on compute nodes as OpenAI-compatible endpoints. SLURM is the
  default; PBS/Torque, LSF, and SGE are covered by a translation reference. Use
  whenever the user mentions a cluster, a scheduler, sbatch, srun, squeue, sacct,
  seff, qsub, qstat, bsub, a job script, a partition or queue, GPU allocation, an
  account or QoS error, a project or scratch filesystem, group permissions on a
  shared research directory, job arrays, checkpointing against a wall clock, a
  job that was killed or ran out of memory, containers on a cluster
  (apptainer/singularity), or launching an inference server for batch model
  evaluation. Also use for "run this on the cluster", "how many GPU hours will
  this take", "my job is pending forever", or any request whose deliverable is a
  job script or a cluster diagnosis. Trigger even when the user only pastes an
  error from a scheduler or a job log.
summary: "Write, debug, and monitor cluster batch jobs, and serve models on compute nodes."
version: "2.0.0"
author: anayy09
license: MIT
metadata:
  status: active
  last_updated: "2026-08-02"
---

# HPC Cluster

Cluster work fails in a small number of predictable ways: the wrong account or
queue, data on the wrong filesystem, a job that dies at hour 71 of a 72 hour wall
clock with no checkpoint, and permissions on a shared group directory. Everything
here exists to make those failures either impossible or cheap.

The governing rule: **never submit a long job you have not first run for two
minutes.** Submit the same script with a tiny input and a 10 minute wall clock,
confirm it produces one correct output file, then scale. A five minute smoke test
routinely saves a day of queue time.

Examples use SLURM, which runs most academic and national-lab clusters. On
PBS/Torque, LSF, or SGE the concepts are identical and the commands are not.
`references/scheduler-portability.md` maps every directive, command, and
environment variable used in this skill.

## Every site is different. Read it, do not assume it.

Partition names, queue names, accounting units, filesystem mount points, and
allocation policies are set per site and change over time. There is no portable
default worth guessing at. Establish the following before writing a single
`#SBATCH` line, and say which of them came from the cluster and which the user
supplied:

```bash
sinfo -s                                      # partitions, availability, node counts
sinfo -O partition,gres:40,cpus,memory,statelong   # node shapes and GPU types
sacctmgr show assoc user=$USER format=account,qos,partition%40,maxwall
scontrol show partition <name>                # time limits, allowed accounts
squeue -u $USER --start                       # why pending, estimated start
sacct -u $USER -S $(date -d '7 days ago' +%F) --format=JobID,JobName%20,State,Elapsed
```

Two things come from the site's documentation rather than from these commands,
because they are policy and not scheduler state:

- **The accounting unit.** Some sites bill core-hours, some GPU-hours, some
  node-hours, and some charge for a whole node no matter what you requested. This
  decides whether asking for one GPU on a shared node is thrifty or wasteful.
- **The purge policy.** Scratch filesystems are frequently purged on a fixed file
  age (30, 60, 90 days). Results left there disappear without warning.

Many sites also ship local wrapper commands for quota and allocation reporting.
They are site-specific, not standard, so discover them (`module avail`, the
site's user guide, the login banner) rather than assuming a name, and fall back
to the plain SLURM command when one does not exist. Report what you actually
observed rather than what you expected.

### Accounts, queues, and priority tiers

`--account` and `--qos` come from a group allocation, not from the user. Most
sites offer at least two service levels, under varying names:

| Tier | Common names | Property |
|---|---|---|
| Guaranteed | investment, primary, `normal`, `<group>` | Reserved capacity, not preemptible |
| Opportunistic | burst, preemptable, scavenger, spot, low-priority, `<group>-b` | More capacity, lower priority, **can be killed mid-run** |

Use the opportunistic tier for restartable work: inference sweeps, array jobs
with an idempotence guard, anything that checkpoints. Never for a job that would
have to start over.

## Step 1: place the data before writing the script

Sites name their filesystems differently; they play the same four roles. Map the
site's paths onto this table once, then use variables in the job script so the
script survives a move to another cluster.

| Role | Typical variable | Use for | Do not use for |
|---|---|---|---|
| Home | `$HOME` | dotfiles, source, small scripts. Tight quota. | data, environments, checkpoints |
| Fast parallel scratch | `$SCRATCH`, `$WORK` | active job I/O, checkpoints, intermediate artifacts | anything you cannot regenerate, if it is purged |
| Bulk / project | `$PROJECT`, `$ARCHIVE` | source datasets, released results, sharing across the group | high-IOPS random reads during training |
| Node-local scratch | `$TMPDIR`, `$SLURM_TMPDIR` | unpacking many small files, temporary shards, embedded databases | anything you need after the job exits |

If the site does not define these variables, define them yourself at the top of
the job script so a move to another cluster is a one-line change:

```bash
WORK=${SCRATCH:-/scratch/$USER}/myproject
DATA=${PROJECT:-/projects/$GROUP}/datasets
```

The single biggest throughput mistake in a pipeline over many small files is
reading them one at a time off a parallel filesystem. Pack them into a small
number of archives or shards, stage a shard to node-local scratch at job start,
and read from there. See `references/storage-and-scratch.md`.

## Step 2: the canonical job script

```bash
#!/bin/bash
#SBATCH --job-name=NAME
#SBATCH --account=ACCOUNT
#SBATCH --partition=PARTITION       # from sinfo, not from memory
#SBATCH --qos=QOS                   # omit if the site does not use QoS
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64gb
#SBATCH --gres=gpu:1                # add a type only if the site requires one
#SBATCH --time=04:00:00
#SBATCH --output=logs/%x_%j.out
#SBATCH --error=logs/%x_%j.err
#SBATCH --mail-type=FAIL,TIME_LIMIT_80
#SBATCH --mail-user=USER@EXAMPLE.EDU

set -euo pipefail                   # a silent partial failure is worse than a crash

WORK=${SCRATCH:-/scratch/$USER}/myproject

module purge
module load ENVMODULE               # site-specific: conda, python, cuda...
source "$WORK/venv/bin/activate"    # or: conda activate ENVNAME

export OMP_NUM_THREADS=${SLURM_CPUS_PER_TASK:-1}
export HF_HOME="$WORK/.cache/huggingface"   # never let caches default to $HOME
export TOKENIZERS_PARALLELISM=false

echo "job=$SLURM_JOB_ID node=$(hostname) gpu=${CUDA_VISIBLE_DEVICES:-none}"
echo "python=$(which python)"
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader || true

srun python -u run.py --config configs/CONFIG.yaml --out "$WORK/runs/$SLURM_JOB_ID"
```

Details that matter and are usually omitted:

- `set -euo pipefail` turns a failed `cp` into a failed job instead of a job that
  writes an empty results file and exits 0.
- `python -u` so stdout appears in the log while the job runs, not after it dies.
- `HF_HOME`, `TORCH_HOME`, and pip caches must point off `$HOME`. Filling the home
  quota mid-run causes failures that look like model download corruption.
- `--mail-type=TIME_LIMIT_80` warns you before a wall clock kill, which is the
  moment a checkpoint is still useful.
- Write outputs to a per-job directory. Two runs writing to the same path is the
  most common source of results that cannot be reproduced.
- Name a GPU type (`--gres=gpu:a100:1`) only when the site's partitions mix types
  and you need a specific one. A type string the partition does not have is
  rejected at submit time.

Use `scripts/gen_sbatch.py` to emit this with the placeholders filled:

```bash
python scripts/gen_sbatch.py --name infer --account myproj --partition gpu \
  --qos normal --gpu 1 --cpus 8 --mem 64gb --time 04:00:00 \
  --work '$SCRATCH/myproject' --activate 'conda activate myenv' \
  --cmd "python -u run.py --config configs/base.yaml" > jobs/infer.sbatch
```

## Step 3: parallelize with arrays, not with more loops

Sharded inference, prompt ablations, and seed sweeps are all embarrassingly
parallel. One array job is easier to monitor, easier to resume, and gets
scheduled faster than one large multi-node job:

```bash
#SBATCH --array=0-63%8      # 64 tasks, at most 8 running at once
...
SHARD=$(printf "%04d" "$SLURM_ARRAY_TASK_ID")
OUT="$WORK/runs/$SLURM_ARRAY_JOB_ID/shard_${SHARD}.parquet"
if [[ -f "$OUT" ]]; then echo "shard $SHARD done, skipping"; exit 0; fi
srun python -u infer.py --shard "$SHARD" --out "$OUT.tmp" && mv "$OUT.tmp" "$OUT"
```

The `if [[ -f ... ]]` guard plus write-to-`.tmp`-then-`mv` makes the array
idempotent. Resubmitting after a preemption reruns only the missing shards, and a
killed task never leaves a truncated file that looks complete. The `%8` throttle
keeps one sweep from consuming the group's entire allocation, and on sites with a
per-user running-job cap it is what keeps the submission legal.

## Step 4: serve a model instead of reloading it

Loading a large model once per batch is the dominant cost in a prompt ablation.
Start one inference server on the allocated node, run every ablation arm against
it, then tear it down. The full recipe (port selection, health check polling,
SSH tunneling from a login node, and the client config) is in
`references/serving-llms.md`.

Key points: bind to `0.0.0.0` on a port chosen at runtime, write the resolved
`http://$(hostname):$PORT/v1` to a file the client reads, poll `/health` before
sending work, and set the maximum context length explicitly so an over-long
prompt fails at startup rather than mid-sweep.

## Step 5: monitor and do the post-mortem

```bash
squeue -u $USER -o "%.12i %.20j %.8T %.10M %.6D %R"
scontrol show job <jobid>          # while running: reason, node, requested resources
seff <jobid>                       # after: CPU efficiency, peak memory vs requested
sacct -j <jobid> --format=JobID,State,ExitCode,Elapsed,MaxRSS,ReqMem,ReqTRES%40
```

Run `seff` on every job type once. It is a common SLURM add-on rather than a
guaranteed one; where it is missing, `sacct` with `MaxRSS` and `Elapsed` gives
the same information. Requesting 128gb for a job with 9gb peak RSS lengthens
queue time for no benefit, and CPU efficiency under about 20 percent on a
dataloader-bound job usually means `--cpus-per-task` is too low, not too high.

`references/troubleshooting.md` maps observed symptoms to causes: host OOM kill
versus CUDA OOM, invalid account and partition combinations, jobs pending on a
GPU or allocation limit, permission denied on a group directory, and preempted
jobs that vanish.

## Estimating cost before requesting time

```bash
python scripts/gpu_hours.py --items 412000 --throughput 6.2 --arms 5 --overhead 0.25
```

Measure `throughput` (items per second) from the smoke test rather than guessing.
Ask for wall clock roughly 1.5x the estimate: too short kills the job, too long
delays scheduling and can exceed the queue's time limit. Convert the result into
the site's own accounting unit before reporting a cost. A job billed per node
behaves very differently from one billed per GPU.

## Shared group directories

Data written by one group member and unreadable by the next is a recurring cost.
Set the group sticky bit and a default ACL once, on the directory, rather than
chmod-ing files after every run:

```bash
PROJ=/path/to/shared/project
chgrp -R GROUP "$PROJ"
chmod g+s "$PROJ"                              # new entries inherit the group
setfacl -R  -m g:GROUP:rwX "$PROJ"
setfacl -R -d -m g:GROUP:rwX "$PROJ"           # applies to files created later
umask 007                                      # put this in the job script
```

`rwX` with a capital X grants execute on directories only, which is what you
want. Some parallel filesystems are deployed without POSIX ACL support and will
reject `setfacl`; there, rely on setgid plus `umask 007` and verify by creating a
test file. Full explanation and the read-only variant for released datasets are
in `references/storage-and-scratch.md`.

## Reference files

- `references/slurm-recipes.md`: job script variants: interactive, multi-GPU
  single node, checkpoint and resume, dependency chains, array driven by a
  manifest, preemptible jobs, conditional requeue.
- `references/storage-and-scratch.md`: filesystem selection, the small-file
  problem, node-local staging, ACLs, quota and inode diagnosis, restricted data.
- `references/serving-llms.md`: an inference server on a compute node,
  OpenAI-compatible clients, tunneling, concurrency, determinism for ablations.
- `references/troubleshooting.md`: symptom to cause to fix table.
- `references/scheduler-portability.md`: SLURM to PBS/Torque, LSF, and SGE:
  directives, commands, environment variables, arrays, and dependencies.
