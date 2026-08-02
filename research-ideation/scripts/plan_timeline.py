#!/usr/bin/env python3
"""Schedule a research direction against a deadline.

Lays the standard phases for a contribution type across the available time,
marks the decision gates, holds a buffer, and reports slack. When slack is
negative it names the compressible phases rather than shrinking everything.

Usage:
    python scripts/plan_timeline.py --deadline 2026-11-15 --effort-months 3
    python scripts/plan_timeline.py --deadline 2026-11-15 --effort-months 3 \\
        --profile method --buffer 0.2 --start 2026-08-05
    python scripts/plan_timeline.py --profiles
    python scripts/plan_timeline.py --deadline 2026-11-15 --effort-months 3 --json

Standard library only. No network, no filesystem writes.
"""

import argparse
import datetime as dt
import json
import sys

WEEKS_PER_MONTH = 4.345

# profile -> list of (phase, share of effort, gate or "", compressible)
PROFILES = {
    "empirical": [
        ("Pilot and kill experiment", 0.10,
         "Effect visible at pilot scale, per the pre-written decision rule", False),
        ("Main experiments", 0.28, "", False),
        ("Baselines and ablations", 0.20,
         "Minimum evidence set complete", False),
        ("Statistics, calibration, figures", 0.12, "", False),
        ("Drafting", 0.18, "", True),
        ("Internal review and revision", 0.12, "Submission-ready", True),
    ],
    "method": [
        ("Pilot and kill experiment", 0.10,
         "Proposed component beats the tuned baseline on the pilot split", False),
        ("Implementation and tuning", 0.22, "", False),
        ("Baselines at matched budget", 0.16,
         "Baseline tuning budget matches the method's", False),
        ("Ablations and cost accounting", 0.16, "", False),
        ("Statistics and figures", 0.10, "", False),
        ("Drafting", 0.16, "", True),
        ("Internal review and revision", 0.10, "Submission-ready", True),
    ],
    "analysis": [
        ("Scope the analysis on existing runs", 0.12,
         "Existing runs are reportable: configs recorded, no since-fixed bugs", False),
        ("Re-analysis at the decision unit", 0.24, "", False),
        ("Confirmatory runs", 0.20,
         "Effect holds on the confirmatory setting", False),
        ("Statistics and figures", 0.14, "", False),
        ("Drafting", 0.20, "", True),
        ("Internal review and revision", 0.10, "Submission-ready", True),
    ],
    "dataset": [
        ("Provenance, licensing, ethics", 0.12,
         "Release is legally clear", False),
        ("Curation and annotation", 0.34, "", False),
        ("Agreement study and split protocol", 0.16,
         "Agreement acceptable, splits leak-free", False),
        ("Baselines including a trivial one", 0.14, "", False),
        ("Datasheet and documentation", 0.10, "", True),
        ("Drafting and internal review", 0.14, "Submission-ready", True),
    ],
    "negative": [
        ("Reproduce the original positive result", 0.22,
         "Original claim reproduces, so the null is not an implementation bug", False),
        ("Search the design space", 0.26, "", False),
        ("Equivalence or non-inferiority analysis", 0.16,
         "Null is adequately powered", False),
        ("Mechanism for the failure", 0.14, "", False),
        ("Drafting", 0.14, "", True),
        ("Internal review and revision", 0.08, "Submission-ready", True),
    ],
    "survey": [
        ("Protocol and search strategy", 0.16,
         "Search is reproducible and reported", False),
        ("Screening and extraction", 0.28, "", False),
        ("Appraisal and synthesis", 0.20, "", False),
        ("Original element: comparison or meta-analysis", 0.16,
         "Original contribution exists beyond the summary", False),
        ("Drafting", 0.12, "", True),
        ("Internal review and revision", 0.08, "Submission-ready", True),
    ],
}


def parse_date(value, label):
    try:
        return dt.date.fromisoformat(value)
    except ValueError:
        sys.exit("error: %s must be ISO format YYYY-MM-DD, got '%s'" % (label, value))


def build_schedule(start, phases, total_weeks):
    rows = []
    cursor = start
    for name, share, gate, compressible in phases:
        weeks = total_weeks * share
        end = cursor + dt.timedelta(days=round(weeks * 7))
        rows.append({
            "phase": name,
            "weeks": round(weeks, 1),
            "start": cursor.isoformat(),
            "end": end.isoformat(),
            "gate": gate,
            "compressible": compressible,
        })
        cursor = end
    return rows, cursor


def main():
    ap = argparse.ArgumentParser(description="Backward-plan a paper against a deadline.")
    ap.add_argument("--deadline", help="ISO date, YYYY-MM-DD")
    ap.add_argument("--effort-months", type=float,
                    help="real working months of effort, including writing")
    ap.add_argument("--start", help="ISO date, defaults to today")
    ap.add_argument("--profile", default="empirical",
                    help="contribution type: %s" % ", ".join(sorted(PROFILES)))
    ap.add_argument("--buffer", type=float, default=0.15,
                    help="share of effort held as buffer, default 0.15")
    ap.add_argument("--profiles", action="store_true",
                    help="print the phase profiles and exit")
    ap.add_argument("--json", action="store_true", dest="as_json")
    args = ap.parse_args()

    if args.profiles:
        for name, phases in sorted(PROFILES.items()):
            print("%s" % name)
            for phase, share, gate, compressible in phases:
                tag = " [compressible]" if compressible else ""
                print("  %4.0f%%  %s%s" % (share * 100, phase, tag))
                if gate:
                    print("        gate: %s" % gate)
            print()
        return

    if not args.deadline or args.effort_months is None:
        ap.error("provide --deadline and --effort-months, or --profiles")

    if args.profile not in PROFILES:
        sys.exit("error: unknown profile '%s'. Valid: %s"
                 % (args.profile, ", ".join(sorted(PROFILES))))
    if args.effort_months <= 0:
        sys.exit("error: --effort-months must be positive")
    if args.buffer < 0:
        sys.exit("error: --buffer must be non-negative")

    start = parse_date(args.start, "--start") if args.start else dt.date.today()
    deadline = parse_date(args.deadline, "--deadline")
    if deadline <= start:
        sys.exit("error: deadline %s is not after the start date %s"
                 % (deadline.isoformat(), start.isoformat()))

    phases = PROFILES[args.profile]
    work_weeks = args.effort_months * WEEKS_PER_MONTH
    buffer_weeks = work_weeks * args.buffer
    needed_weeks = work_weeks + buffer_weeks
    available_weeks = (deadline - start).days / 7.0
    slack_weeks = available_weeks - needed_weeks

    rows, work_end = build_schedule(start, phases, work_weeks)
    buffer_end = work_end + dt.timedelta(days=round(buffer_weeks * 7))

    if args.as_json:
        print(json.dumps({
            "profile": args.profile,
            "start": start.isoformat(),
            "deadline": deadline.isoformat(),
            "effort_months": args.effort_months,
            "work_weeks": round(work_weeks, 1),
            "buffer_weeks": round(buffer_weeks, 1),
            "available_weeks": round(available_weeks, 1),
            "slack_weeks": round(slack_weeks, 1),
            "projected_ready": buffer_end.isoformat(),
            "phases": rows,
        }, indent=2))
        return

    print("Schedule: %s profile, %.1f months of effort" % (args.profile, args.effort_months))
    print("Start %s, deadline %s, %.1f weeks available"
          % (start.isoformat(), deadline.isoformat(), available_weeks))
    print()

    fmt = "%-44s %6s  %-10s %-10s"
    print(fmt % ("phase", "weeks", "start", "end"))
    print("-" * 76)
    for row in rows:
        print(fmt % (row["phase"], "%.1f" % row["weeks"], row["start"], row["end"]))
        if row["gate"]:
            print("    gate: %s" % row["gate"])
    print(fmt % ("Buffer", "%.1f" % buffer_weeks, work_end.isoformat(),
                 buffer_end.isoformat()))
    print("-" * 76)
    print("Projected submission-ready: %s" % buffer_end.isoformat())
    print()

    if slack_weeks >= 0:
        print("Slack: %.1f weeks. The plan fits." % slack_weeks)
        if slack_weeks < 2:
            print("Under two weeks of slack means one failed experiment cycle "
                  "misses the deadline. Treat the kill-experiment gate as real.")
    else:
        deficit = -slack_weeks
        print("Slack: -%.1f weeks. The plan does not fit." % deficit)
        print("Do not compress every phase. Options, in order of least damage:")
        print("  1. Cut a non-blocking requirement from the gap ledger and "
              "re-estimate effort.")
        print("  2. Narrow the claim so a smaller evidence set supports it.")
        compressible = [r["phase"] for r in rows if r["compressible"]]
        recoverable = sum(r["weeks"] for r in rows if r["compressible"]) * 0.4
        print("  3. Compress only: %s. That recovers roughly %.1f weeks and "
              "costs draft quality." % (", ".join(compressible), recoverable))
        print("  4. Move to a later deadline. Losing %.1f weeks of experiments "
              "to hit a date is usually the worse trade." % deficit)


if __name__ == "__main__":
    main()
