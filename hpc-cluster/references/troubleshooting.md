# Troubleshooting: symptom to cause to fix

Work from the observed symptom. Do not guess at a cause without reading the
`.err` file, `scontrol show job`, and `sacct` output first.

Messages below are SLURM's wording. Other schedulers phrase the same conditions
differently; `scheduler-portability.md` has the command equivalents for
inspecting them.

---

## Submission is rejected

**`Invalid account or account/partition combination specified`**
The `--account` or `--qos` does not exist for this user, or the QoS is not valid
on that partition. Confirm with
`sacctmgr show assoc user=$USER format=account,qos,partition%40`. A common cause
is copying a job script from a colleague in a different group, or from a tutorial
written for another cluster.

**`Requested node configuration is not available`**
The combination of `--gres`, `--mem`, and `--cpus-per-task` exceeds any single
node in the partition, or the GPU type string is wrong. Check the actual node
shapes: `sinfo -O partition,gres:40,cpus,memory,statelong`. Asking for
`gpu:a100:1` on a partition that has a different accelerator produces this too;
drop the type qualifier unless you need a specific one.

**`Job violates accounting/QOS policy`**
Requested time exceeds the QoS or partition limit, or requested GPUs exceed the
per-user or per-group cap. Check with
`sacctmgr show qos <qos> format=name,maxwall,maxtresperuser%40` and
`scontrol show partition <name>`.

**`Batch job submission failed: Invalid job array specification`**
The array range exceeds `MaxArraySize`. Check with
`scontrol show config | grep MaxArraySize` and split the submission.

---

## Job stays pending

Read the reason field: `squeue -u $USER -o "%.12i %.9P %.8T %.10M %R"`.

| Reason | Meaning | What to do |
|---|---|---|
| `Priority` / `Resources` | normal queueing | shrink the request; smaller and shorter jobs schedule sooner |
| `QOSMaxGRESPerUser`, `QOSMaxJobsPerUser` | at a per-user cap | wait, or lower the array throttle (`%N`) |
| `AssocGrpGPUMinutesLimit`, `AssocGrpCPUMinutesLimit` | group allocation exhausted | use the opportunistic tier, or wait for the accounting window to roll |
| `ReqNodeNotAvail` | node reserved or in maintenance | check for a scheduled outage; resubmit after |
| `Dependency` | waiting on another job | verify the parent did not fail; `afterok` never satisfies after a failure |
| `JobHeldUser` / `JobHeldAdmin` | held | `scontrol release <jobid>` if user-held; contact support if admin-held |
| `PartitionTimeLimit` | requested time exceeds the partition maximum | shorten `--time` and add checkpointing |

`squeue -u $USER --start` gives the scheduler's estimated start time. If it is
days out, the request is too large, usually in wall clock or GPU count.

---

## Job dies immediately

**Empty output, nonzero exit, nothing in the log**
Usually the environment. Batch jobs do not source interactive shell init. Load
the environment explicitly in the script, and echo `which python` at the top to
confirm it resolved to what you expected.

**`CondaError: Run 'conda init' before 'conda activate'`**
Source the profile script explicitly rather than relying on shell init:
`source "$(conda info --base)/etc/profile.d/conda.sh"` before `conda activate`.

**`Permission denied` on the script**
`chmod +x` is not required for `sbatch`, but is for a script invoked directly.
More often the failure is on a data path: run `namei -l <path>` to find which
component of the path lacks group execute.

**`ModuleNotFoundError` for a package that is installed**
A stray `~/.local/lib/python3.x/site-packages` shadowing the environment. Set
`export PYTHONNOUSERSITE=1` in the job script.

---

## Job dies during the run

**`slurmstepd: error: ... Killed ... out of memory` / `oom-kill event`**
Host RAM, not GPU memory. Raise `--mem`, reduce dataloader workers, or stop
loading the whole dataset into RAM. Check what it actually used on a smaller run
with `seff <jobid>` or `sacct -j <jobid> --format=MaxRSS,ReqMem`.

**`torch.cuda.OutOfMemoryError`**
GPU memory. Lower batch size, enable gradient checkpointing, lower
`--gpu-memory-utilization` or the maximum context length for an inference server,
or request a GPU with more memory. A job can hit this only at one specific input
(the longest sequence in the dataset), so it can appear at hour 20 of a run that
started fine.

**`DUE TO TIME LIMIT`**
Wall clock exceeded. Not a bug; a planning failure. Add checkpointing (see
`slurm-recipes.md` section 2) and use `--mail-type=TIME_LIMIT_80` so you know it
is coming.

**`State: PREEMPTED` on the opportunistic tier**
A guaranteed-tier job reclaimed the node. Expected behavior. Add `--requeue` and
make the job idempotent, or move to the non-preemptible tier.

**`Disk quota exceeded` on a filesystem with free space**
Inode (file count) quota, not byte quota. See `storage-and-scratch.md` section 5.
Almost always an unsharded directory of small output files.

**`Input/output error` or `Stale file handle`**
Transient parallel filesystem problem, or a file deleted while open. Retry once;
if it recurs on the same path, the file or directory is genuinely damaged.

**A job that ran last month now cannot find its input**
Scratch purge. Check the site's retention window before concluding the data was
deleted by something you did.

**NCCL timeout or hang in distributed training**
Check that every rank got a GPU (`echo $CUDA_VISIBLE_DEVICES` per rank), that
`--ntasks` matches the launcher's expectation, and that `MASTER_PORT` is not
colliding. For single node, prefer `torchrun --standalone`, which removes most of
this surface. On multi-node, `NCCL_DEBUG=INFO` names the interface it chose; if
it picked the management network instead of the high-speed fabric, pin it with
`NCCL_SOCKET_IFNAME`.

---

## Results are wrong rather than absent

**Two runs wrote to the same output directory**
Symptom: metrics that do not match any config. Always include `$SLURM_JOB_ID` or
a run hash in the output path.

**The job exited 0 but produced nothing useful**
Missing `set -euo pipefail`. A failed `cp`, or a failed `python` inside a pipe,
does not fail the script by default.

**Array tasks silently did nothing**
`sed -n "${SLURM_ARRAY_TASK_ID}p"` past the end of the manifest returns an empty
string. Guard for it and log the skip, otherwise the job succeeds with no work
done and the aggregation step reports on a partial dataset.

**Model outputs differ between two supposedly identical runs**
Check whether the inference server restarted between them, whether the model
revision string changed, and whether temperature was actually zero. Then measure
the run-to-run variation directly before attributing any difference to the
condition under test.

---

## Diagnostic commands worth running first

```bash
scontrol show job <jobid>                  # while running
sacct -j <jobid> --format=JobID,JobName%20,State%20,ExitCode,Elapsed,MaxRSS,ReqTRES%40
seff <jobid>                               # efficiency summary, where installed
sacct -u $USER -S $(date -d '3 days ago' +%F) --format=JobID,JobName%20,State,Elapsed,ExitCode
nvidia-smi                                 # inside an interactive session on the node
```

Report exactly what these returned when asking for help, including the job id. A
description of the failure without the job id and the `.err` tail cannot be
diagnosed by anyone, including the person who wrote the script.
