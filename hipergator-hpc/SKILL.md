---
name: hipergator-hpc
description: >-
  Write, submit, debug, and monitor SLURM jobs on UF HiPerGator, and serve LLMs
  (vLLM, MedGemma, Gemma, nemotron, gpt-oss) on compute nodes as
  OpenAI-compatible endpoints. Use whenever the user mentions HiPerGator, sbatch,
  SLURM, srun, squeue, sacct, seff, a job script, GPU allocation, a QoS or
  account error, /blue or /orange storage, group permissions on a shared
  research directory, OnDemand, apptainer/singularity containers, job arrays,
  a job that was killed or ran out of memory, or launching an inference server
  for batch model evaluation. Also use for "run this on the cluster", "how many
  GPU hours will this take", "my job is pending forever", or any request whose
  deliverable is a job script or a cluster diagnosis. Trigger even when the user
  only pastes an error from a scheduler or a job log.
summary: "SLURM jobs and LLM serving on UF HiPerGator, adaptable to any SLURM cluster."
version: "1.0.0"
author: anayy09
license: MIT
metadata:
  status: active
  last_updated: "2026-07-25"
---

# HiPerGator HPC

Cluster work fails in a small number of predictable ways: wrong account or QoS,
data on the wrong filesystem, a job that dies at hour 71 of a 72 hour wall clock
with no checkpoint, and permissions on a shared group directory. Everything here
exists to make those failures either impossible or cheap.

The governing rule: **never submit a long job you have not first run for two
minutes.** Submit the same script with a tiny input and a 10 minute wall clock,
confirm it produces one correct output file, then scale. A five minute smoke test
routinely saves a day of queue time.

## Step 1: discover the environment, do not assume it

Partition names, QoS names, and group allocations change. Read them from the
cluster rather than from memory or from an old job script:

```bash
sinfo -s                                  # partitions, availability, node counts
sinfo -O partition,gres:40,nodes,statelong # what GPU types exist where
sacctmgr show assoc user=$USER format=account,qos,partition%40
squeue -u $USER --start                   # why pending, estimated start
slurmInfo                                 # UF RC wrapper: group allocation usage
showQos <group>                           # limits attached to a QoS
home_quota; blue_quota; orange_quota      # UF RC quota wrappers
```

If a wrapper command does not exist on the current node, fall back to the plain
SLURM command. Report what you actually observed rather than what you expected.

The `--account` and `--qos` come from the group allocation, not from the user.
An investment QoS (`<group>`) is guaranteed capacity; a burst QoS (`<group>-b`)
is higher capacity, lower priority, and preemptible. Use burst for
restartable work like inference sweeps, never for a job without checkpointing.

## Step 2: place the data before writing the script

| Path | Use for | Do not use for |
|---|---|---|
| `/home/$USER` | dotfiles, small scripts. Tight quota. | data, conda envs, checkpoints |
| `/blue/<group>/<user>` | active working data, checkpoints, job I/O | long-term archives |
| `/orange/<group>` | bulk and shared datasets, results archive | high-IOPS job scratch |
| `$TMPDIR` (node-local) | unpacking many small files, e.g. patch tiles | anything you need after the job |

The single biggest throughput mistake on a patch-level pipeline is reading
100k small files directly off `/blue` or `/orange`. Pack tiles into a small
number of archives or WebDataset shards, copy the shard to node-local `$TMPDIR`
at job start, and read from there. See `references/storage-and-permissions.md`.

## Step 3: the canonical job script

```bash
#!/bin/bash
#SBATCH --job-name=NAME
#SBATCH --account=GROUP
#SBATCH --qos=GROUP                 # or GROUP-b for burst
#SBATCH --partition=PARTITION       # from sinfo, not from memory
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64gb
#SBATCH --gres=gpu:a100:1           # verify the type string with sinfo
#SBATCH --time=04:00:00
#SBATCH --output=logs/%x_%j.out
#SBATCH --error=logs/%x_%j.err
#SBATCH --mail-type=FAIL,TIME_LIMIT_80
#SBATCH --mail-user=USER@ufl.edu

set -euo pipefail                   # a silent partial failure is worse than a crash

module purge
module load conda
conda activate ENVNAME

export OMP_NUM_THREADS=${SLURM_CPUS_PER_TASK}
export HF_HOME=/blue/GROUP/$USER/.cache/huggingface   # never let this default to /home
export TOKENIZERS_PARALLELISM=false

echo "job=$SLURM_JOB_ID node=$(hostname) gpu=${CUDA_VISIBLE_DEVICES:-none}"
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader

srun python -u run.py --config configs/CONFIG.yaml --out /blue/GROUP/$USER/runs/$SLURM_JOB_ID
```

Details that matter and are usually omitted:

- `set -euo pipefail` turns a failed `cp` into a failed job instead of a job that
  writes an empty results file and exits 0.
- `python -u` so stdout appears in the log while the job runs, not after it dies.
- `HF_HOME`, `TORCH_HOME`, and pip caches must point at `/blue`. Filling the home
  quota mid-run causes failures that look like model download corruption.
- `--mail-type=TIME_LIMIT_80` warns you before a wall clock kill, which is the
  moment a checkpoint is still useful.
- Write outputs to a per-job directory. Two runs writing to the same path is the
  most common source of results that cannot be reproduced.

Use `scripts/gen_sbatch.py` to emit this with the placeholders filled:

```bash
python scripts/gen_sbatch.py --name cpath-infer --account prismap --qos prismap-b \
  --partition gpu --gpu a100:1 --cpus 8 --mem 64gb --time 04:00:00 \
  --cmd "python -u run.py --config configs/base.yaml" > jobs/infer.sbatch
```

## Step 4: parallelize with arrays, not with more loops

Patch-level inference over shards, prompt ablations, and seed sweeps are all
embarrassingly parallel. One array job is easier to monitor, easier to resume,
and gets scheduled faster than one large multi-GPU job:

```bash
#SBATCH --array=0-63%8      # 64 tasks, at most 8 running at once
...
SHARD=$(printf "%04d" $SLURM_ARRAY_TASK_ID)
OUT=/blue/GROUP/$USER/runs/$SLURM_ARRAY_JOB_ID/shard_${SHARD}.parquet
if [[ -f "$OUT" ]]; then echo "shard $SHARD done, skipping"; exit 0; fi
srun python -u infer.py --shard "$SHARD" --out "$OUT.tmp" && mv "$OUT.tmp" "$OUT"
```

The `if [[ -f ... ]]` guard plus write-to-`.tmp`-then-`mv` makes the array
idempotent. Resubmitting after a preemption reruns only the missing shards, and
a killed task never leaves a truncated file that looks complete. The `%8` throttle
keeps one sweep from consuming the group's entire allocation.

## Step 5: serve a model instead of reloading it

Loading a 27B model per batch is the dominant cost in a prompt ablation. Start
one vLLM server on the allocated node, run every ablation arm against it, then
tear it down. Full recipe including port selection, health check polling, SSH
tunneling from a login node, and the client config in
`references/serving-llms.md`.

Key points: bind to `0.0.0.0` on a random high port, write the resolved
`http://$(hostname):$PORT/v1` to a file the client reads, poll `/health` before
sending work, and set `--max-model-len` explicitly so a long prompt fails at
startup rather than mid-sweep.

## Step 6: monitor and do the post-mortem

```bash
squeue -u $USER -o "%.12i %.20j %.8T %.10M %.6D %R"
scontrol show job <jobid>          # while running: reason, node, requested resources
seff <jobid>                       # after: CPU efficiency, peak memory vs requested
sacct -j <jobid> --format=JobID,State,ExitCode,Elapsed,MaxRSS,ReqMem,ReqTRES%40
```

Run `seff` on every job type once. Requesting 128gb for a job with 9gb peak RSS
lengthens queue time for no benefit, and CPU efficiency under about 20 percent on
a dataloader-bound job usually means `--cpus-per-task` is too low, not too high.

`references/troubleshooting.md` maps observed symptoms to causes: `OOMKilled` vs
CUDA OOM, `Invalid account or account/partition combination`, jobs pending on
`QOSMaxGRESPerUser` or `AssocGrpGPUMinutesLimit`, `Permission denied` on a group
directory, and disappearing preempted burst jobs.

## Estimating cost before requesting time

```bash
python scripts/gpu_hours.py --items 412000 --throughput 6.2 --arms 5 --overhead 0.25
```

Measure `throughput` (items per second) from the smoke test rather than guessing.
Ask for wall clock roughly 1.5x the estimate: too short kills the job, but too
long delays scheduling and can exceed the QoS time limit.

## Shared group directories

Data written by one lab member and unreadable by the next is a recurring cost.
Set the group sticky bit and a default ACL once, on the directory, rather than
chmod-ing files after every run:

```bash
chgrp -R <group> /orange/<group>/<project>
chmod g+s /orange/<group>/<project>                 # new files inherit the group
setfacl -R  -m g:<group>:rwX /orange/<group>/<project>
setfacl -R -d -m g:<group>:rwX /orange/<group>/<project>   # applies to future files
umask 007                                            # put in the job script
```

`rwX` with a capital X grants execute on directories only, which is what you
want. Full explanation and the read-only variant for released datasets are in
`references/storage-and-permissions.md`.

## Reference files

- `references/slurm-recipes.md` — job script variants: interactive, multi-GPU
  single node, checkpoint-and-resume, dependency chains, array with manifest.
- `references/storage-and-permissions.md` — filesystem selection, small-file
  handling, `$TMPDIR` staging, ACLs, quota diagnosis.
- `references/serving-llms.md` — vLLM on a compute node, OpenAI-compatible
  clients, tunneling, batching and concurrency settings for sweeps.
- `references/troubleshooting.md` — symptom to cause to fix table.
