#!/usr/bin/env python3
"""Emit a HiPerGator sbatch script with the safety boilerplate already in place.

The generated script always includes: strict bash mode, cache redirection away
from /home, a per-job output directory, and (for arrays) an idempotence guard so
resubmitting reruns only the missing work.

Examples
--------
Single GPU inference job:

    python gen_sbatch.py --name cpath-infer --account prismap --qos prismap-b \\
        --partition gpu --gpu a100:1 --cpus 8 --mem 64gb --time 04:00:00 \\
        --cmd "python -u infer.py --config configs/base.yaml" > jobs/infer.sbatch

Array over a manifest, 8 concurrent:

    python gen_sbatch.py --name tile-slides --account prismap --qos prismap \\
        --partition gpu --gpu a100:1 --cpus 16 --mem 128gb --time 08:00:00 \\
        --array 1-500 --throttle 8 --manifest /blue/prismap/$USER/manifests/slides.txt \\
        --cmd "python -u tile_and_infer.py --slide \\"\\$LINE\\" --out \\"\\$OUT.tmp\\"" \\
        > jobs/tile.sbatch

Nothing here talks to the scheduler. Review the output, then submit it.
"""

from __future__ import annotations

import argparse
import sys

HEADER = """#!/bin/bash
#SBATCH --job-name={name}
#SBATCH --account={account}
#SBATCH --qos={qos}
#SBATCH --partition={partition}
#SBATCH --nodes={nodes}
#SBATCH --ntasks={ntasks}
#SBATCH --cpus-per-task={cpus}
#SBATCH --mem={mem}
#SBATCH --time={time}
{gres}{array}{mail}#SBATCH --output={logdir}/%x_%j.out
#SBATCH --error={logdir}/%x_%j.err
"""

PREAMBLE = """
set -euo pipefail

module purge
module load conda
conda activate {env}

# Keep caches off the home quota. Filling /home mid-run produces failures that
# look like corrupted model downloads.
export HF_HOME={work}/.cache/huggingface
export TORCH_HOME={work}/.cache/torch
export XDG_CACHE_HOME={work}/.cache
export PIP_CACHE_DIR={work}/.cache/pip
export OMP_NUM_THREADS=${{SLURM_CPUS_PER_TASK:-1}}
export TOKENIZERS_PARALLELISM=false
umask 007   # keep group-shared output readable by the rest of the lab

echo "job=${{SLURM_JOB_ID}} node=$(hostname) started=$(date -Is)"
echo "python=$(which python)"
{gpu_probe}
"""

GPU_PROBE = 'nvidia-smi --query-gpu=name,memory.total --format=csv,noheader || true\n'

SIMPLE_BODY = """
RUN_DIR={work}/runs/${{SLURM_JOB_ID}}
mkdir -p "$RUN_DIR" {logdir}
echo "run_dir=$RUN_DIR"

srun {cmd}

echo "finished=$(date -Is)"
"""

ARRAY_BODY = """
RUN_DIR={work}/runs/${{SLURM_ARRAY_JOB_ID}}
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

    out = HEADER.format(
        name=a.name, account=a.account, qos=a.qos, partition=a.partition,
        nodes=a.nodes, ntasks=a.ntasks, cpus=a.cpus, mem=a.mem, time=a.time,
        gres=gres, array=array, mail=mail, logdir=a.logdir,
    )
    out += PREAMBLE.format(
        env=a.env, work=a.work,
        gpu_probe=GPU_PROBE if a.gpu else "",
    )
    if a.array:
        if not a.manifest:
            sys.exit("--array requires --manifest (one work unit per line)")
        out += ARRAY_BODY.format(
            work=a.work, logdir=a.logdir, manifest=a.manifest,
            cmd=a.cmd, ext=a.ext,
        )
    else:
        out += SIMPLE_BODY.format(work=a.work, logdir=a.logdir, cmd=a.cmd)
    return out


def main() -> None:
    p = argparse.ArgumentParser(
        description="Generate a HiPerGator sbatch script.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument("--name", required=True, help="job name")
    p.add_argument("--account", required=True, help="SLURM account (group)")
    p.add_argument("--qos", required=True, help="QoS; append -b for burst")
    p.add_argument("--partition", required=True, help="verify with: sinfo -s")
    p.add_argument("--cmd", required=True, help="command run under srun")
    p.add_argument("--gpu", default="", help='e.g. a100:1; verify type with sinfo -O gres')
    p.add_argument("--cpus", default="8")
    p.add_argument("--mem", default="64gb")
    p.add_argument("--time", default="04:00:00", help="D-HH:MM:SS or HH:MM:SS")
    p.add_argument("--nodes", default="1")
    p.add_argument("--ntasks", default="1")
    p.add_argument("--env", default="ENVNAME", help="conda env name or full path")
    p.add_argument("--work", default="/blue/GROUP/$USER", help="working root on /blue")
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
