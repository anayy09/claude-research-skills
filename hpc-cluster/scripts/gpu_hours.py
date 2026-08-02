#!/usr/bin/env python3
"""Estimate wall clock and GPU hours for a sweep, and suggest an array shape.

Measure --throughput from a real smoke test rather than guessing it. Run the job
on a few hundred items, divide by elapsed seconds, and use that number here.

Example
-------
    python gpu_hours.py --items 412000 --throughput 6.2 --arms 5 \\
        --overhead 0.25 --gpus-per-task 1 --max-concurrent 8

Prints a per-arm and total estimate, a recommended --time request with headroom,
and an array shape that keeps each task inside a target wall clock.

The GPU-hour figure is a physical quantity, not a bill. Sites charge in
core-hours, GPU-hours, or node-hours, and some charge for a whole node however
much of it you requested. Convert to the site's own accounting unit before
reporting a cost against an allocation.
"""

from __future__ import annotations

import argparse
import math


def hms(seconds: float) -> str:
    seconds = int(math.ceil(seconds))
    d, rem = divmod(seconds, 86400)
    h, rem = divmod(rem, 3600)
    m, s = divmod(rem, 60)
    if d:
        return f"{d}-{h:02d}:{m:02d}:{s:02d}"
    return f"{h:02d}:{m:02d}:{s:02d}"


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--items", type=float, required=True,
                   help="work units per arm (samples, records, shards, steps)")
    p.add_argument("--throughput", type=float, required=True,
                   help="items per second per task, measured not guessed")
    p.add_argument("--arms", type=int, default=1,
                   help="number of conditions in the sweep")
    p.add_argument("--overhead", type=float, default=0.20,
                   help="fraction added for startup, staging, model load (0.20 = 20%%)")
    p.add_argument("--gpus-per-task", type=int, default=1)
    p.add_argument("--max-concurrent", type=int, default=1,
                   help="array throttle: tasks running at once")
    p.add_argument("--target-task-hours", type=float, default=4.0,
                   help="wall clock to aim for per array task")
    p.add_argument("--headroom", type=float, default=1.5,
                   help="multiplier on the estimate for the --time request")
    a = p.parse_args()

    if a.throughput <= 0:
        raise SystemExit("--throughput must be positive")

    serial_s = a.items / a.throughput * (1.0 + a.overhead)
    total_serial_s = serial_s * a.arms
    gpu_hours = total_serial_s / 3600.0 * a.gpus_per_task

    # Array shaping: split one arm into tasks that each land near the target.
    target_s = a.target_task_hours * 3600.0
    n_tasks = max(1, int(math.ceil(serial_s / target_s)))
    per_task_s = serial_s / n_tasks
    wall_s = per_task_s * math.ceil(n_tasks * a.arms / max(1, a.max_concurrent))

    print(f"items per arm          : {a.items:,.0f}")
    print(f"measured throughput    : {a.throughput:,.2f} items/s/task")
    print(f"overhead assumed       : {a.overhead:.0%}")
    print()
    print(f"serial time, one arm   : {hms(serial_s)}")
    print(f"serial time, all arms  : {hms(total_serial_s)}  ({a.arms} arms)")
    print(f"GPU hours (billed)     : {gpu_hours:,.1f}")
    print()
    # 1-based to match the manifest convention used by gen_sbatch.py, where the
    # task index selects a line with `sed -n "${SLURM_ARRAY_TASK_ID}p"`.
    print(f"suggested array        : --array=1-{n_tasks}%{a.max_concurrent}  "
          f"({n_tasks} tasks per arm, {n_tasks * a.arms} total)")
    print(f"per-task compute       : {hms(per_task_s)}")
    print(f"per-task --time request: {hms(per_task_s * a.headroom)}  "
          f"({a.headroom:g}x headroom)")
    print(f"expected wall clock    : {hms(wall_s)} at {a.max_concurrent} concurrent")
    print()
    print("Reminder: a --time far above the true runtime delays scheduling, and")
    print("one far below it kills the job. Re-measure throughput after any change")
    print("to batch size, model, or input resolution.")


if __name__ == "__main__":
    main()
