#!/usr/bin/env python3
"""Append-only screening log that produces a PRISMA 2020 flow diagram whose
numbers actually reconcile.

The flow diagram is where reviews most often fail arithmetic. Records go
missing between boxes, the excluded-at-full-text reasons do not sum to the
number excluded, and the error surfaces at peer review months later. Numbers
derived from a decision log cannot drift, because there is nowhere for a record
to go that is not recorded.

Usage
-----
    python screening_log.py init --title "AI triage in colorectal pathology"

    python screening_log.py identified --source "PubMed" --n 412
    python screening_log.py identified --source "Scopus" --n 388
    python screening_log.py identified --source "citation chasing" --n 17 --other
    python screening_log.py dedup --removed 291

    python screening_log.py screen --id S001 --decision exclude --reason "not colorectal"
    python screening_log.py screen --id S002 --decision include
    python screening_log.py fulltext --id S002 --decision exclude \\
        --reason "no external validation"
    python screening_log.py retrieval --id S003 --failed --reason "no full text available"

    python screening_log.py flow           # numbers + reconciliation check
    python screening_log.py flow --mermaid # diagram source
    python screening_log.py exclusions     # PRISMA item 16b table

Every command appends; nothing is edited. To reverse a decision, record the new
one: `screen --id S002 --decision include --supersedes` keeps the history and
uses the latest.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from collections import Counter, OrderedDict
from pathlib import Path
from typing import Any, Dict, List

DEFAULT_LOG = "screening_log.jsonl"


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def append(path: Path, event: Dict[str, Any]) -> None:
    event["ts"] = now()
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(event, sort_keys=True) + "\n")


def read(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        sys.exit(f"no log at {path}; run `init` first")
    out = []
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if line.strip():
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                print(f"warning: line {i} is not valid JSON, skipped", file=sys.stderr)
    return out


def fold(events: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Latest decision per record id wins, so a superseding decision is honoured
    without rewriting history."""
    state = {
        "title": "", "db_sources": OrderedDict(), "other_sources": OrderedDict(),
        "dedup_removed": 0, "ta": {}, "ft": {}, "retrieval_failed": {},
        "ta_reasons": [], "ft_reasons": [],
    }
    for e in events:
        k = e.get("event")
        if k == "init":
            state["title"] = e.get("title", "")
        elif k == "identified":
            bucket = "other_sources" if e.get("other") else "db_sources"
            state[bucket][e["source"]] = e["n"]
        elif k == "dedup":
            state["dedup_removed"] += int(e.get("removed", 0))
        elif k == "screen":
            state["ta"][e["id"]] = e
        elif k == "fulltext":
            state["ft"][e["id"]] = e
        elif k == "retrieval":
            state["retrieval_failed"][e["id"]] = e
    return state


def flow_numbers(state: Dict[str, Any]) -> Dict[str, Any]:
    id_db = sum(state["db_sources"].values())
    id_other = sum(state["other_sources"].values())
    dedup = state["dedup_removed"]
    after_dedup = id_db - dedup

    ta = state["ta"]
    ta_excluded = sum(1 for v in ta.values() if v["decision"] == "exclude")
    ta_included = sum(1 for v in ta.values() if v["decision"] == "include")

    not_retrieved = len(state["retrieval_failed"])
    ft = state["ft"]
    ft_excluded = sum(1 for v in ft.values() if v["decision"] == "exclude")
    included = sum(1 for v in ft.values() if v["decision"] == "include")

    return {
        "identified_databases": id_db,
        "identified_other": id_other,
        "duplicates_removed": dedup,
        "records_after_dedup": after_dedup,
        "records_screened": len(ta),
        "records_excluded_ta": ta_excluded,
        "reports_sought": ta_included + id_other,
        "reports_not_retrieved": not_retrieved,
        "reports_assessed": len(ft),
        "reports_excluded_ft": ft_excluded,
        "studies_included": included,
    }


def reconcile(n: Dict[str, Any]) -> List[str]:
    """Each check corresponds to an arrow in the PRISMA 2020 diagram. A failure
    means a record exists in one box and not the next, which is exactly what
    reviewers recompute."""
    issues = []
    if n["records_after_dedup"] != n["records_screened"]:
        issues.append(
            f"records after deduplication ({n['records_after_dedup']}) does not equal "
            f"records screened ({n['records_screened']}): "
            f"{abs(n['records_after_dedup'] - n['records_screened'])} record(s) "
            f"unaccounted for at title/abstract stage")
    if n["records_screened"] != n["records_excluded_ta"] + (
            n["reports_sought"] - n["identified_other"]):
        issues.append(
            "screened does not split cleanly into excluded plus sought; "
            "some records have no recorded title/abstract decision")
    expected_assessed = n["reports_sought"] - n["reports_not_retrieved"]
    if expected_assessed != n["reports_assessed"]:
        issues.append(
            f"reports sought minus not-retrieved ({expected_assessed}) does not "
            f"equal reports assessed ({n['reports_assessed']})")
    if n["reports_assessed"] != n["reports_excluded_ft"] + n["studies_included"]:
        issues.append(
            f"reports assessed ({n['reports_assessed']}) does not equal excluded "
            f"({n['reports_excluded_ft']}) plus included ({n['studies_included']})")
    return issues


def mermaid(n: Dict[str, Any]) -> str:
    return f"""```mermaid
flowchart TD
    A["Records identified from databases and registers (n = {n['identified_databases']})"]
    B["Records removed before screening:<br/>duplicates (n = {n['duplicates_removed']})"]
    C["Records screened (n = {n['records_screened']})"]
    D["Records excluded (n = {n['records_excluded_ta']})"]
    E["Reports sought for retrieval (n = {n['reports_sought']})"]
    F["Reports not retrieved (n = {n['reports_not_retrieved']})"]
    G["Reports assessed for eligibility (n = {n['reports_assessed']})"]
    H["Reports excluded, with reasons (n = {n['reports_excluded_ft']})"]
    I["Studies included in review (n = {n['studies_included']})"]
    J["Records identified from other methods (n = {n['identified_other']})"]

    A --> B --> C --> D
    C --> E --> F
    E --> G --> H
    G --> I
    J --> E
```"""


def cmd_flow(a: argparse.Namespace) -> int:
    state = fold(read(Path(a.log)))
    n = flow_numbers(state)

    if a.mermaid:
        print(mermaid(n))
        return 0
    if a.json:
        print(json.dumps(n, indent=2))
        return 0

    if state["title"]:
        print(f"{state['title']}\n")
    print("PRISMA 2020 flow")
    print("-" * 54)
    for src, v in state["db_sources"].items():
        print(f"  identified, {src:<28} {v:>7,}")
    for src, v in state["other_sources"].items():
        print(f"  identified (other), {src:<21} {v:>7,}")
    for k in ["identified_databases", "duplicates_removed", "records_after_dedup",
              "records_screened", "records_excluded_ta", "reports_sought",
              "reports_not_retrieved", "reports_assessed", "reports_excluded_ft",
              "studies_included"]:
        print(f"  {k:<32} {n[k]:>7,}")

    issues = reconcile(n)
    print()
    if issues:
        print(f"{len(issues)} reconciliation problem(s):")
        for i in issues:
            print(f"  - {i}")
        print("\nFix the log before drawing the diagram. A flow diagram that does "
              "not add up is the first thing a reviewer recomputes.")
        return 1
    print("reconciliation: all stages balance")
    return 0


def cmd_exclusions(a: argparse.Namespace) -> int:
    state = fold(read(Path(a.log)))
    ft = [v for v in state["ft"].values() if v["decision"] == "exclude"]
    counts = Counter(v.get("reason", "no reason recorded") for v in ft)

    print("## Reports excluded at full text, with reasons (PRISMA item 16b)\n")
    print("| Reason | n |")
    print("|---|---|")
    for reason, c in counts.most_common():
        print(f"| {reason} | {c} |")
    print(f"| **Total** | **{sum(counts.values())}** |")

    missing = counts.get("no reason recorded", 0)
    if missing:
        print(f"\n{missing} exclusion(s) have no recorded reason. PRISMA requires "
              f"a reason for every report excluded at full text, and 'did not meet "
              f"criteria' is not a reason.")
        return 1

    ta = [v for v in state["ta"].values() if v["decision"] == "exclude"]
    print(f"\nTitle/abstract exclusions: {len(ta)}. Reasons are not required at "
          f"this stage by PRISMA, but recording them makes the criteria auditable "
          f"and takes no extra time when logged as you screen.")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--log", default=DEFAULT_LOG)
    sub = p.add_subparsers(dest="cmd", required=True)

    q = sub.add_parser("init"); q.add_argument("--title", default="")
    q.set_defaults(func=lambda a: (append(Path(a.log), {"event": "init",
                                                        "title": a.title}),
                                   print(f"initialized {a.log}"), 0)[-1])

    q = sub.add_parser("identified", help="records found in one source")
    q.add_argument("--source", required=True)
    q.add_argument("--n", type=int, required=True)
    q.add_argument("--other", action="store_true",
                   help="found by methods other than database search")
    q.set_defaults(func=lambda a: (append(Path(a.log), {
        "event": "identified", "source": a.source, "n": a.n, "other": a.other}),
        print(f"recorded {a.n} from {a.source}"), 0)[-1])

    q = sub.add_parser("dedup")
    q.add_argument("--removed", type=int, required=True)
    q.add_argument("--method", default="", help="software and settings used")
    q.set_defaults(func=lambda a: (append(Path(a.log), {
        "event": "dedup", "removed": a.removed, "method": a.method}),
        print(f"recorded {a.removed} duplicates removed"), 0)[-1])

    for stage in ("screen", "fulltext"):
        q = sub.add_parser(stage, help=f"{stage} stage decision")
        q.add_argument("--id", required=True)
        q.add_argument("--decision", required=True, choices=["include", "exclude"])
        q.add_argument("--reason", default="")
        q.add_argument("--reviewer", default="")
        q.add_argument("--supersedes", action="store_true",
                       help="knowingly overrides an earlier decision for this id")
        q.set_defaults(func=lambda a, s=stage: (append(Path(a.log), {
            "event": s, "id": a.id, "decision": a.decision, "reason": a.reason,
            "reviewer": a.reviewer, "supersedes": a.supersedes}),
            print(f"{s}: {a.id} -> {a.decision}"), 0)[-1])

    q = sub.add_parser("retrieval", help="record a report that could not be obtained")
    q.add_argument("--id", required=True)
    q.add_argument("--failed", action="store_true")
    q.add_argument("--reason", default="")
    q.set_defaults(func=lambda a: (append(Path(a.log), {
        "event": "retrieval", "id": a.id, "failed": a.failed, "reason": a.reason}),
        print(f"retrieval: {a.id} not retrieved"), 0)[-1])

    q = sub.add_parser("flow", help="PRISMA numbers and reconciliation")
    q.add_argument("--mermaid", action="store_true")
    q.add_argument("--json", action="store_true")
    q.set_defaults(func=cmd_flow)

    q = sub.add_parser("exclusions", help="full-text exclusion reason table")
    q.set_defaults(func=cmd_exclusions)

    a = p.parse_args()
    return a.func(a)


if __name__ == "__main__":
    raise SystemExit(main())
