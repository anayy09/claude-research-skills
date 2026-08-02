# Scheduler portability: SLURM, PBS/Torque, LSF, SGE

The rest of this skill is written for SLURM because it runs most academic and
national-lab clusters. The reasoning transfers unchanged to other schedulers;
only the syntax differs. This file is the translation layer.

Two cautions before using any table here:

- **Dialects differ.** PBS Pro and OpenPBS accept directives that Torque does
  not, and vice versa. Grid Engine survives as Son of Grid Engine, Altair Grid
  Engine, and several forks with divergent flags. Treat a row as the common case
  and verify against the site's own documentation.
- **Resource request syntax is where portability breaks first.** Memory, CPU, and
  GPU requests are the least standardized part of every scheduler. Copy a working
  example from the site's user guide for those three, and use this table for
  everything else.

---

## Commands

| Task | SLURM | PBS / Torque | LSF | SGE |
|---|---|---|---|---|
| Submit a batch job | `sbatch job.sh` | `qsub job.sh` | `bsub < job.sh` | `qsub job.sh` |
| Run / launch a task | `srun cmd` | `pbsdsh cmd`, `mpiexec` | `blaunch cmd` | `mpirun` |
| Interactive session | `srun --pty bash -i`, `salloc` | `qsub -I` | `bsub -Is bash` | `qrsh` |
| List my jobs | `squeue -u $USER` | `qstat -u $USER` | `bjobs` | `qstat -u $USER` |
| Job detail | `scontrol show job <id>` | `qstat -f <id>` | `bjobs -l <id>` | `qstat -j <id>` |
| Cancel a job | `scancel <id>` | `qdel <id>` | `bkill <id>` | `qdel <id>` |
| Hold / release | `scontrol hold`/`release <id>` | `qhold`/`qrls <id>` | `bstop`/`bresume <id>` | `qhold`/`qrls <id>` |
| Completed job accounting | `sacct -j <id>` | `tracejob <id>`, `qstat -x <id>` | `bacct -l <id>` | `qacct -j <id>` |
| Partitions / queues | `sinfo -s` | `qstat -Q`, `pbsnodes -a` | `bqueues`, `bhosts` | `qconf -sql`, `qhost` |
| Requeue a running job | `scontrol requeue <id>` | `qrerun <id>` | `brequeue <id>` | `qmod -r <id>` |

---

## Directives

| Meaning | SLURM | PBS / Torque | LSF | SGE |
|---|---|---|---|---|
| Directive prefix | `#SBATCH` | `#PBS` | `#BSUB` | `#$` |
| Job name | `--job-name=X` | `-N X` | `-J X` | `-N X` |
| Queue / partition | `--partition=X` | `-q X` | `-q X` | `-q X` |
| Account / project | `--account=X` | `-A X` | `-P X` | `-A X` |
| Wall clock | `--time=HH:MM:SS` | `-l walltime=HH:MM:SS` | `-W HH:MM` | `-l h_rt=HH:MM:SS` |
| Nodes and tasks | `--nodes=N --ntasks-per-node=M` | `-l select=N:ncpus=M` (PBS Pro) or `-l nodes=N:ppn=M` (Torque) | `-n total -R "span[ptile=M]"` | `-pe <pe_name> N` |
| Cores per task | `--cpus-per-task=C` | `ncpus=C` in the select statement | `-n C` | slots via the parallel environment |
| Memory | `--mem=64gb` (per node) or `--mem-per-cpu=` | `-l mem=64gb` or `select=1:mem=64gb` | `-M 64000 -R "rusage[mem=64000]"` | `-l h_vmem=64G` (**per slot**) |
| GPUs | `--gres=gpu:2` | `-l select=1:ngpus=2` or `-l gpus=2` | `-gpu "num=2"` | `-l gpu=2` (site-defined) |
| Stdout / stderr | `--output=`, `--error=` | `-o`, `-e` | `-o`, `-e` | `-o`, `-e` |
| Merge stdout and stderr | (default when only `--output`) | `-j oe` | (default) | `-j y` |
| Email | `--mail-type=FAIL --mail-user=` | `-m a -M addr` | `-N -u addr` | `-m a -M addr` |
| Job array | `--array=1-100%10` | `-J 1-100` (PBS Pro), `-t 1-100` (Torque) | `-J "name[1-100]%10"` | `-t 1-100 -tc 10` |
| Dependency | `--dependency=afterok:<id>` | `-W depend=afterok:<id>` | `-w "done(<id>)"` | `-hold_jid <id>` |
| Requeue on preemption | `--requeue` | `-r y` | (queue policy) | `-r y` |
| Start in submit directory | (default) | `cd $PBS_O_WORKDIR` **required** | (default) | `-cwd` |

`h_vmem` in SGE is enforced **per slot**, not per job. A 4-slot job with
`-l h_vmem=64G` reserves 256 GB. This is the single most common porting mistake
onto Grid Engine.

---

## Environment variables

| Meaning | SLURM | PBS / Torque | LSF | SGE |
|---|---|---|---|---|
| Job ID | `SLURM_JOB_ID` | `PBS_JOBID` | `LSB_JOBID` | `JOB_ID` |
| Job name | `SLURM_JOB_NAME` | `PBS_JOBNAME` | `LSB_JOBNAME` | `JOB_NAME` |
| Array task index | `SLURM_ARRAY_TASK_ID` | `PBS_ARRAY_INDEX` (Pro) / `PBS_ARRAYID` (Torque) | `LSB_JOBINDEX` | `SGE_TASK_ID` |
| Parent array job ID | `SLURM_ARRAY_JOB_ID` | `PBS_ARRAY_ID` | `LSB_JOBID` | `JOB_ID` |
| Submit directory | `SLURM_SUBMIT_DIR` | `PBS_O_WORKDIR` | `LS_SUBCWD` | `SGE_O_WORKDIR` |
| Node list | `SLURM_JOB_NODELIST` | `PBS_NODEFILE` (a file) | `LSB_HOSTS` | `PE_HOSTFILE` (a file) |
| Cores allocated | `SLURM_CPUS_PER_TASK` | `NCPUS` | `LSB_DJOB_NUMPROC` | `NSLOTS` |
| Node-local scratch | `SLURM_TMPDIR`, `TMPDIR` | `TMPDIR` | `TMPDIR` | `TMPDIR` |

Note the difference in shape: SLURM and LSF give you a node *list* in a variable,
while PBS and SGE give you a *path to a file* containing the list. Code that
does `for host in $SLURM_JOB_NODELIST` has to become
`for host in $(cat "$PBS_NODEFILE")`.

---

## Porting a job script

The array recipe from `slurm-recipes.md`, translated. The body is identical; only
the header and the index variable change.

**PBS Pro**

```bash
#!/bin/bash
#PBS -N process
#PBS -q gpu
#PBS -A myproject
#PBS -l select=1:ncpus=8:mem=64gb:ngpus=1
#PBS -l walltime=04:00:00
#PBS -J 1-500
#PBS -o logs/
#PBS -j oe

set -euo pipefail
cd "$PBS_O_WORKDIR"            # PBS does not do this for you

TASK_ID=$PBS_ARRAY_INDEX
LINE=$(sed -n "${TASK_ID}p" "$WORK/manifests/items.txt")
[[ -z "$LINE" ]] && { echo "no work for task $TASK_ID"; exit 0; }
...
```

**LSF**

```bash
#!/bin/bash
#BSUB -J "process[1-500]%20"
#BSUB -q gpu
#BSUB -P myproject
#BSUB -n 8
#BSUB -R "rusage[mem=64000]"
#BSUB -gpu "num=1"
#BSUB -W 04:00
#BSUB -o logs/%J_%I.out

set -euo pipefail
TASK_ID=$LSB_JOBINDEX
...
```

**SGE**

```bash
#!/bin/bash
#$ -N process
#$ -q gpu.q
#$ -cwd
#$ -pe smp 8
#$ -l h_rt=04:00:00,h_vmem=8G      # per slot: 8 slots x 8G = 64G
#$ -t 1-500
#$ -tc 20
#$ -o logs/
#$ -j y

set -euo pipefail
TASK_ID=$SGE_TASK_ID
...
```

A portable pattern for scripts that must run on more than one cluster: resolve
the index once at the top and use a neutral name everywhere below it.

```bash
TASK_ID=${SLURM_ARRAY_TASK_ID:-${PBS_ARRAY_INDEX:-${LSB_JOBINDEX:-${SGE_TASK_ID:-1}}}}
JOB_ID=${SLURM_JOB_ID:-${PBS_JOBID:-${LSB_JOBID:-${JOB_ID:-manual}}}}
```

---

## What does not translate

- **`seff`** is SLURM-specific. For efficiency after the fact, use `bacct -l`
  (LSF), `qacct -j` (SGE), or `tracejob` (Torque). Where nothing equivalent
  exists, log peak RSS from inside the job.
- **`--signal=B:USR1@600`** for pre-kill checkpointing has no exact analogue.
  LSF has `bsub -wa 'signal' -wt '10'`, SGE sends `SIGUSR1` before `SIGKILL` on
  `h_rt` if configured, and PBS behavior is site-dependent. Verify by testing a
  short job rather than assuming the signal arrives.
- **Heterogeneous job steps** (`srun --het-group`) and SLURM's `--gres` syntax
  have no general equivalent. Ask the site.
- **Fairshare and preemption policy** are configured per site on every scheduler.
  Nothing about priority behavior is portable, including the meaning of "high
  priority".
