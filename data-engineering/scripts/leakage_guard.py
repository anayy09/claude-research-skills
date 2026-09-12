#!/usr/bin/env python3
"""
leakage_guard.py - The two checks a research feature table has to pass before
any model is fitted, with a positive control so a guard that has never failed
is never trusted.

  availability   every feature value was available before the prediction
                 time: for each feature column F, a companion column
                 F__available_at (or a mapping file) holds the timestamp at
                 which the value became known; the guard fails on any row
                 where available_at > index_time
  disjoint       no group (patient, subject, site) appears in more than one
                 fold or split; a patch-level or stay-level split that shares
                 patients across folds leaks appearance into the held-out set

--poison rewrites one row's availability timestamp (or one group's fold) in
memory to a leaking value and confirms the guard fails on it. A guard whose
positive control passes is broken; the script reports that as a FAIL too.

Inputs: CSV, or parquet when pandas and pyarrow are importable.

Usage:
    python leakage_guard.py features.csv --index-time ed_arrival --group patient_id --fold fold
    python leakage_guard.py features.parquet --index-time index_time --availability availability.json
    python leakage_guard.py features.csv --index-time t0 --group subject --fold split --poison
    python leakage_guard.py --self-test

availability.json maps feature column -> availability column when the
F__available_at convention is not used:
    {"lactate_max": "lactate_available_at", "age": "constant"}
A feature mapped to "constant" is available at all times (demographics).

Standard library only for CSV; pandas + pyarrow for parquet.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import sys
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple

FAIL, PASS = "FAIL", "PASS"


def parse_ts(v: str) -> Optional[float]:
    v = (v or "").strip()
    if not v or v.lower() in ("nan", "none", "null", "nat"):
        return None
    try:
        return float(v)
    except ValueError:
        pass
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            return dt.datetime.strptime(v[:19], fmt).timestamp()
        except ValueError:
            continue
    try:
        return dt.datetime.fromisoformat(v.replace("Z", "+00:00")).timestamp()
    except ValueError:
        return None


def load(path: Path) -> List[Dict[str, str]]:
    if path.suffix.lower() == ".parquet":
        try:
            import pandas as pd  # type: ignore
            df = pd.read_parquet(path)
            return [{k: ("" if v is None else str(v)) for k, v in r.items()} for r in df.to_dict("records")]
        except ImportError:
            sys.exit("parquet input needs pandas and pyarrow")
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def availability_map(rows: List[Dict[str, str]], mapping_path: Optional[Path]) -> Dict[str, str]:
    if mapping_path:
        return json.loads(mapping_path.read_text(encoding="utf-8"))
    cols = rows[0].keys() if rows else []
    return {c[:-len("__available_at")]: c for c in cols if c.endswith("__available_at")}


def check_availability(rows: List[Dict[str, str]], index_col: str, amap: Dict[str, str]) -> Tuple[str, List[str], int]:
    problems: List[str] = []
    checked = 0
    if not amap:
        return FAIL, ["no availability columns found (F__available_at) and no --availability mapping; the guard cannot run"], 0
    for i, r in enumerate(rows):
        t0 = parse_ts(r.get(index_col, ""))
        if t0 is None:
            problems.append(f"row {i}: index time {index_col!r} missing or unparseable")
            continue
        for feat, acol in amap.items():
            if acol == "constant":
                continue
            if acol not in r:
                problems.append(f"row {i}: availability column {acol!r} for {feat!r} missing")
                continue
            checked += 1
            ta = parse_ts(r.get(acol, ""))
            val = r.get(feat, "")
            if ta is None:
                if val not in ("", "nan", "NaN", "None"):
                    problems.append(f"row {i}: {feat}={val!r} present with no availability time")
                continue
            if ta > t0:
                problems.append(f"row {i}: {feat} became available {ta - t0:.0f}s after the index time (leak)")
    return (FAIL if problems else PASS), problems[:40], checked


def check_disjoint(rows: List[Dict[str, str]], group_col: str, fold_col: str) -> Tuple[str, List[str], int]:
    seen: Dict[str, set] = {}
    for r in rows:
        g, f = r.get(group_col, ""), r.get(fold_col, "")
        seen.setdefault(g, set()).add(f)
    crossing = {g: fs for g, fs in seen.items() if len(fs) > 1}
    problems = [f"{group_col}={g} appears in folds {sorted(fs)}" for g, fs in list(crossing.items())[:40]]
    if crossing:
        problems.append(f"{len(crossing)} of {len(seen)} groups cross folds")
    return (FAIL if crossing else PASS), problems, len(seen)


def poison(rows: List[Dict[str, str]], index_col: str, amap: Dict[str, str], group_col: Optional[str], fold_col: Optional[str]) -> List[Dict[str, str]]:
    import copy
    bad = copy.deepcopy(rows)
    if amap and bad:
        feat, acol = next(((f, a) for f, a in amap.items() if a != "constant"), (None, None))
        if acol:
            t0 = parse_ts(bad[0].get(index_col, "")) or 0.0
            bad[0][acol] = dt.datetime.fromtimestamp(t0 + 3600).strftime("%Y-%m-%dT%H:%M:%S")
            bad[0][feat] = bad[0].get(feat) or "1"
    if group_col and fold_col and len(bad) > 1:
        folds = sorted({r.get(fold_col, "") for r in bad})
        if len(folds) > 1:
            g0 = bad[0].get(group_col, "")
            other = next((r for r in bad if r.get(fold_col) != bad[0].get(fold_col)), None)
            if other is not None:
                other[group_col] = g0
    return bad


def run(rows: List[Dict[str, str]], a: argparse.Namespace, amap: Dict[str, str]) -> Tuple[List[str], List[str]]:
    lines: List[str] = []
    fails: List[str] = []
    if a.index_time:
        st, probs, n = check_availability(rows, a.index_time, amap)
        lines.append(f"[{st}] availability: {n} feature values checked against {a.index_time}; {len(probs)} problem(s)")
        lines += [f"       {p}" for p in probs]
        if st == FAIL:
            fails.append("availability")
    if a.group and a.fold:
        st, probs, n = check_disjoint(rows, a.group, a.fold)
        lines.append(f"[{st}] disjoint: {n} groups across folds in {a.fold}; {len(probs)} problem(s)")
        lines += [f"       {p}" for p in probs]
        if st == FAIL:
            fails.append("disjoint")
    return lines, fails


def self_test() -> int:
    ok = True

    def check(desc: str, cond: bool) -> None:
        nonlocal ok
        print(("  ok   " if cond else "  FAIL ") + desc)
        ok = ok and cond

    rows = [
        {"patient_id": "p1", "fold": "0", "t0": "2026-01-01T10:00:00", "lactate": "2.1", "lactate__available_at": "2026-01-01T09:30:00", "age": "60"},
        {"patient_id": "p2", "fold": "1", "t0": "2026-01-01T11:00:00", "lactate": "", "lactate__available_at": "", "age": "70"},
        {"patient_id": "p3", "fold": "1", "t0": "2026-01-01T12:00:00", "lactate": "3.0", "lactate__available_at": "2026-01-01T11:00:00", "age": "50"},
    ]
    amap = availability_map(rows, None)
    check("availability columns discovered", amap == {"lactate": "lactate__available_at"})
    st, probs, n = check_availability(rows, "t0", amap)
    check("honest table passes availability", st == PASS and n == 3)
    st2, probs2, _ = check_disjoint(rows, "patient_id", "fold")
    check("disjoint split passes", st2 == PASS)
    bad = poison(rows, "t0", amap, "patient_id", "fold")
    st3, probs3, _ = check_availability(bad, "t0", amap)
    st4, probs4, _ = check_disjoint(bad, "patient_id", "fold")
    check("positive control: poisoned timestamp fails", st3 == FAIL and "leak" in probs3[0])
    check("positive control: shared patient across folds fails", st4 == FAIL)
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "f.csv"
        with open(p, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]))
            w.writeheader(); w.writerows(rows)
        check("csv load", len(load(p)) == 3)
    print("\nself-test " + ("passed" if ok else "FAILED"))
    return 0 if ok else 1


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, OSError):
            pass
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("table", nargs="?", help="CSV or parquet with one row per prediction unit")
    p.add_argument("--index-time", help="column holding the prediction time per row")
    p.add_argument("--availability", help="JSON mapping feature column -> availability column (or 'constant')")
    p.add_argument("--group", help="group column that must not cross folds (patient, subject, site)")
    p.add_argument("--fold", help="fold or split column")
    p.add_argument("--poison", action="store_true", help="also run the positive control and fail if the guard does not catch it")
    p.add_argument("--self-test", action="store_true")
    a = p.parse_args()
    if a.self_test:
        return self_test()
    if not a.table:
        p.error("give the table (or --self-test)")
    if not a.index_time and not (a.group and a.fold):
        p.error("give --index-time and/or --group with --fold")
    rows = load(Path(a.table))
    if not rows:
        print("error: empty table", file=sys.stderr)
        return 2
    amap = availability_map(rows, Path(a.availability) if a.availability else None) if a.index_time else {}
    lines, fails = run(rows, a, amap)
    print("\n".join(lines))
    if a.poison:
        bad = poison(rows, a.index_time or "", amap, a.group, a.fold)
        _, pf = run(bad, a, amap)
        expected = set(c for c in (["availability"] if a.index_time and amap else []) + (["disjoint"] if a.group and a.fold else []))
        caught = set(pf)
        if expected and expected <= caught:
            print(f"[PASS] positive control: the guard fails on poisoned data ({', '.join(sorted(expected))})")
        else:
            print(f"[FAIL] positive control: the guard did NOT fail on poisoned data (expected {sorted(expected)}, caught {sorted(caught)}); do not trust the guard")
            fails.append("positive-control")
    print(f"\n{len(fails)} failing check(s)" if fails else "\nall checks passed")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
