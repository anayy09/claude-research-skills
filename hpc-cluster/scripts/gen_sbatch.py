#!/usr/bin/env python3
"""Emit a SLURM sbatch script with the safety boilerplate already in place.

The generated script always includes: strict bash mode, cache redirection away
from $HOME, a per-job output directory, and (for arrays) an idempotence guard so
resubmitting reruns only the missing work.

Nothing here talks to a scheduler and nothing is site-specific. Verify the
account, partition, QoS, and GPU type against the cluster (`sinfo -s`,
`sacctmgr show assoc user=$USER`) before submitting.

Examples
--------
Single GPU inference job:

    python gen_sbatch.py --name infer --account myproj --partition gpu \\
        --gpu 1 --cpus 8 --mem 64gb --time 04:00:00 \\
        --activate 'conda activate myenv' \\
        --cmd "python -u infer.py --config configs/base.yaml" > jobs/infer.sbatch

Array over a manifest, 8 concurrent:

    python gen_sbatch.py --name process --account myproj --partition gpu \\
        --qos normal --gpu a100:1 --cpus 16 --mem 128gb --time 08:00:00 \\
        --array 1-500 --throttle 8 --manifest '$WORK/manifests/items.txt' \\
        --cmd "python -u process.py --input \\"\\$LINE\\" --out \\"\\$OUT.tmp\\"" \\
        > jobs/process.sbatch

For PBS/Torque, LSF, or SGE, generate the SLURM version and translate the header
with references/scheduler-portability.md.
"""

from __future__ import annotations

import argparse
import sys

HEADER = """#!/bin/bash
#SBATCH --job-name={name}
#SBATCH --account={account}
#SBATCH --partition={partition}
{qos}#SBATCH --nodes={nodes}
#SBATCH --ntasks={ntasks}
#SBATCH --cpus-per-task={cpus}
#SBATCH --mem={mem}
#SBATCH --time={time}
{gres}{array}{mail}#SBATCH --output={logdir}/%x_%j.out
#SBATCH --error={logdir}/%x_%j.err
"""

PREAMBLE = """
set -euo pipefail

# Working root. Point this at the site's fast filesystem; changing this one line
# is what makes the script portable to another cluster.
WORK={work}

{modules}{activate}
# Keep caches off the home quota. Filling $HOME mid-run produces failures that
# look like corrupted model downloads.
export HF_HOME="$WORK/.cache/huggingface"
export TORCH_HOME="$WORK/.cache/torch"
export XDG_CACHE_HOME="$WORK/.cache"
export PIP_CACHE_DIR="$WORK/.cache/pip"
export PYTHONNOUSERSITE=1
export OMP_NUM_THREADS=${{SLURM_CPUS_PER_TASK:-1}}
export TOKENIZERS_PARALLELISM=false
umask 007   # keep group-shared output readable by the rest of the group

echo "job=${{SLURM_JOB_ID}} node=$(hostname) started=$(date -Is)"
echo "python=$(which python)"
{gpu_probe}
"""

GPU_PROBE = 'nvidia-smi --query-gpu=name,memory.total --format=csv,noheader || true\n'

SIMPLE_BODY = """
RUN_DIR="$WORK/runs/${{SLURM_JOB_ID}}"
mkdir -p "$RUN_DIR" {logdir}
echo "run_dir=$RUN_DIR"

srun {cmd}

echo "finished=$(date -Is)"
"""

ARRAY_BODY = """
RUN_DIR="$WORK/runs/${{SLURM_ARRAY_JOB_ID}}"
mkdir -p "$RUN_DIR" {logdir}

MANIFEST={manifest}
LINE=$(sed -n "${{SLURM_ARRAY_TASK_ID}}p" "$MANIFEST")
if [[ -z "$LINE" ]]; then
  echo "no work for task ${{SLURM_ARRAY_TASK_ID}} (manifest shorter than array range)"
  exit 0
fi

ITEM=$(basename "$LINE" | sed 's/\\.[^.]*$//')
OUT="$RUN_DIR/${{ITEM}}{ext}"
if [[ -f "$OUT" ]]; then
  echo "already complete: $ITEM"
  exit 0
fi

# Write to .tmp then rename so a killed task never leaves a truncated file that
# the completeness check would treat as done.
srun {cmd}
mv "$OUT.tmp" "$OUT"

echo "finished=$(date -Is) item=$ITEM"
"""


def build(a: argparse.Namespace) -> str:
    qos = f"#SBATCH --qos={a.qos}\n" if a.qos else ""
    gres = f"#SBATCH --gres=gpu:{a.gpu}\n" if a.gpu else ""
    if a.array:
        throttle = f"%{a.throttle}" if a.throttle else ""
        array = f"#SBATCH --array={a.array}{throttle}\n"
    else:
        array = ""
    mail = ""
    if a.mail:
        mail = (
            "#SBATCH --mail-type=FAIL,TIME_LIMIT_80\n"
            f"#SBATCH --mail-user={a.mail}\n"
        )
    if a.requeue:
        mail += "#SBATCH --requeue\n"

    modules = "".join(f"module load {m}\n" for m in a.module)
    if modules:
        modules = "module purge\n" + modules
    activate = f"{a.activate}\n" if a.activate else ""

    out = HEADER.format(
        name=a.name, account=a.account, partition=a.partition, qos=qos,
        nodes=a.nodes, ntasks=a.ntasks, cpus=a.cpus, mem=a.mem, time=a.time,
        gres=gres, array=array, mail=mail, logdir=a.logdir,
    )
    out += PREAMBLE.format(
        work=a.work, modules=modules, activate=activate,
        gpu_probe=GPU_PROBE if a.gpu else "",
    )
    if a.array:
        if not a.manifest:
            sys.exit("--array requires --manifest (one work unit per line)")
        out += ARRAY_BODY.format(
            logdir=a.logdir, manifest=a.manifest, cmd=a.cmd, ext=a.ext,
        )
    else:
        out += SIMPLE_BODY.format(logdir=a.logdir, cmd=a.cmd)
    return out


def main() -> None:
    p = argparse.ArgumentParser(
        description="Generate a SLURM sbatch script with safe defaults.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument("--name", required=True, help="job name")
    p.add_argument("--account", required=True, help="allocation account")
    p.add_argument("--partition", required=True, help="verify with: sinfo -s")
    p.add_argument("--cmd", required=True, help="command run under srun")
    p.add_argument("--qos", default="", help="QoS, if the site uses one")
    p.add_argument("--gpu", default="",
                   help='GPU request: "1", or "a100:1" if the site needs a type')
    p.add_argument("--cpus", default="8")
    p.add_argument("--mem", default="64gb")
    p.add_argument("--time", default="04:00:00", help="D-HH:MM:SS or HH:MM:SS")
    p.add_argument("--nodes", default="1")
    p.add_argument("--ntasks", default="1")
    p.add_argument("--module", action="append", default=[],
                   help="module to load; repeatable (implies module purge)")
    p.add_argument("--activate", default="",
                   help="environment activation line, e.g. 'conda activate myenv' "
                        "or 'source $WORK/venv/bin/activate'")
    p.add_argument("--work", default="${SCRATCH:-/scratch/$USER}/myproject",
                   help="working root on a fast filesystem")
    p.add_argument("--logdir", default="logs")
    p.add_argument("--array", default="", help="e.g. 1-500")
    p.add_argument("--throttle", default="", help="max concurrent array tasks")
    p.add_argument("--manifest", default="", help="file with one work unit per line")
    p.add_argument("--ext", default=".parquet", help="output extension for array items")
    p.add_argument("--mail", default="", help="email for FAIL and TIME_LIMIT_80")
    p.add_argument("--requeue", action="store_true", help="allow automatic requeue")
    a = p.parse_args()
    sys.stdout.write(build(a))


if __name__ == "__main__":
    main()
