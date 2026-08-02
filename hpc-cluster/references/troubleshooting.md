# Troubleshooting: symptom to cause to fix

Work from the observed symptom. Do not guess at a cause without reading the
`.err` file, `scontrol show job`, and `sacct` output first.

---

## Submission is rejected

**`Invalid account or account/partition combination specified`**
The `--account` or `--qos` does not exist for this user, or the QoS is not valid
on that partition. Confirm with `sacctmgr show assoc user=$USER format=account,qos,partition%40`.
A common cause is copying a job script from a colleague in a different group.

**`Requested node configuration is not available`**
The combination of `--gres`, `--mem`, and `--cpus-per-task` exceeds any single
node in the partition, or the GPU type string is wrong. Check the actual node
shapes: `sinfo -O partition,gres:40,cpus,memory,statelong`. A wrong GPU type
string (`gpu:a100` where the partition only has another type) produces this too.

**`Job violates accounting/QOS policy`**
Requested time exceeds the QoS limit, or requested GPUs exceed the per-user or
per-group cap. `showQos <qos>` or `sacctmgr show qos <qos> format=name,maxwall,maxtresperuser%40`.

---

## Job stays pending

Read the reason field: `squeue -u $USER -o "%.12i %.9P %.8T %.10M %R"`.

| Reason | Meaning | What to do |
|---|---|---|
| `Priority` / `Resources` | normal queueing | shrink the request; smaller and shorter jobs schedule sooner |
| `QOSMaxGRESPerUser` | at your GPU cap | wait, or reduce array throttle (`%N`) |
| `AssocGrpGPUMinutesLimit` | group allocation exhausted | use burst QoS or wait for the accounting window to roll |
| `ReqNodeNotAvail` | node reserved or in maintenance | check for a scheduled outage; resubmit after |
| `Dependency` | waiting on another job | verify the parent did not fail; `afterok` never satisfies after a failure |
| `JobHeldUser`/`JobHeldAdmin` | held | `scontrol release <jobid>` if user-held |

`squeue -u $USER --start` gives the scheduler's estimated start time. If it is
days out, the request is too large.

---

## Job dies immediately

**Empty output, nonzero exit, nothing in the log**
Usually the conda environment. Batch jobs do not source interactive shell init.
Put `module load conda && conda activate <env>` in the script explicitly, and
echo `which python` at the top to confirm it resolved.

**`CondaError: Run 'conda init'`**
Use `conda activate` after `module load conda`, or source the profile script
explicitly: `source $(conda info --base)/etc/profile.d/conda.sh`.

**`Permission denied` on the script**
`chmod +x` is not required for `sbatch`, but is for a script invoked directly.
More often the failure is on a data path: run `namei -l <path>` to find which
component of the path lacks group execute.

---

## Job dies during the run

**`slurmstepd: error: ... Killed ... out of memory` / `oom-kill event`**
Host RAM, not GPU memory. Raise `--mem`, or reduce dataloader workers, or stop
loading the whole dataset into RAM. Check what it actually used on a smaller
run: `seff <jobid>`.

**`torch.cuda.OutOfMemoryError`**
GPU memory. Lower batch size, enable gradient checkpointing, lower
`--gpu-memory-utilization` or `--max-model-len` for vLLM, or request a GPU with
more memory. Note that a job can hit this only at a specific input (the longest
sequence in the dataset), so it can appear at hour 20 of a run that started fine.

**`DUE TO TIME LIMIT`**
Wall clock exceeded. This is not a bug; it is a planning failure. Add
checkpointing (see `slurm-recipes.md` section 2) and use
`--mail-type=TIME_LIMIT_80` so you know it is coming.

**`State: PREEMPTED` on a burst QoS**
The investment QoS reclaimed the node. Expected behavior. Add `--requeue` and
make the job idempotent, or move to the non-burst QoS.

**`Disk quota exceeded` on a filesystem with free space**
Inode (file count) quota, not byte quota. See `storage-and-permissions.md`
section 5. Almost always an unsharded directory of small patch files.

**`Input/output error` or `Stale file handle`**
Transient parallel filesystem problem, or a file deleted while open. Retry once;
if it recurs on the same path, the file or directory is genuinely damaged.

**NCCL timeout or hang in distributed training**
Check that every rank got a GPU (`echo $CUDA_VISIBLE_DEVICES` per rank), that
`--ntasks` matches the launcher's expectation, and that `MASTER_PORT` is not
colliding. For single node, prefer `torchrun --standalone`, which removes most
of this surface.

---

## Results are wrong rather than absent

**Two runs wrote to the same output directory**
Symptom: metrics that do not match any config. Always include `$SLURM_JOB_ID`
or a run hash in the output path.

**The job exited 0 but produced nothing useful**
Missing `set -euo pipefail`. A failed `cp` or a failed `python` inside a pipe
does not fail the script by default.

**Array tasks silently did nothing**
`sed -n "${SLURM_ARRAY_TASK_ID}p"` past the end of the manifest returns an empty
string. Guard for it and log the skip, otherwise the job succeeds with no work
done and the aggregate step reports on a partial dataset.

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
seff <jobid>                               # efficiency summary after completion
sacct -u $USER -S $(date -d '3 days ago' +%F) --format=JobID,JobName%20,State,Elapsed,ExitCode
nvidia-smi                                 # inside an interactive session on the node
```

Report exactly what these returned when asking for help, including the job id.
A description of the failure without the job id and the `.err` tail cannot be
diagnosed by anyone, including the person who wrote the script.
