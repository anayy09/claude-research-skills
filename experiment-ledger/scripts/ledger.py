#!/usr/bin/env python3
"""Experiment ledger: content-hashed runs, an append-only registry, and
comparisons declared before they are run.

Subcommands
-----------
  preregister   declare a comparison (arms, primary metric, hypothesis)
  new           resolve a config, compute a run_id, create runs/<id>/
  record        attach metrics to a run and append to the registry
  list          show runs, optionally filtered by comparison or tag
  table         generate a results table (markdown, latex, or csv)
  verify        check registry integrity and flag post hoc comparisons

The registry (ledger/runs.jsonl) is append-only. State is derived by folding the
event stream, so a mistake is corrected by appending a correction rather than by
editing history. That property is what makes the file worth trusting.

Requires: Python 3.9+. PyYAML only if configs are YAML rather than JSON.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import io
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

try:
    import yaml  # type: ignore
except ImportError:  # pragma: no cover
    yaml = None


# --------------------------------------------------------------------------
# small helpers
# --------------------------------------------------------------------------

def utcnow() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def canonical(obj: Any) -> str:
    """Stable serialization. Key order and whitespace must not affect the hash,
    otherwise reformatting a config silently creates a 'new' experiment."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)


def sha256_str(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_structured(path: Path) -> Dict[str, Any]:
    text = path.read_text()
    if path.suffix in {".yaml", ".yml"}:
        if yaml is None:
            sys.exit("PyYAML is required to read YAML configs: pip install pyyaml")
        return yaml.safe_load(text) or {}
    return json.loads(text)


def dump_structured(obj: Any, path: Path) -> None:
    if path.suffix in {".yaml", ".yml"} and yaml is not None:
        path.write_text(yaml.safe_dump(obj, sort_keys=True, default_flow_style=False))
    else:
        path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n")


def deep_merge(base: Dict[str, Any], overlay: Dict[str, Any]) -> Dict[str, Any]:
    """Overlay wins. Nested dicts merge; lists and scalars are replaced outright,
    because element-wise list merging is ambiguous and hides mistakes."""
    out = dict(base)
    for k, v in overlay.items():
        if k in out and isinstance(out[k], dict) and isinstance(v, dict):
            out[k] = deep_merge(out[k], v)
        else:
            out[k] = v
    return out


def git_info(root: Path) -> Dict[str, Any]:
    def run(*args: str) -> Optional[str]:
        try:
            return subprocess.run(
                ["git", *args], cwd=root, capture_output=True, text=True, check=True
            ).stdout.strip()
        except Exception:
            return None

    commit = run("rev-parse", "--short=8", "HEAD")
    # -uno: ignore untracked files. Generated run directories and logs are
    # untracked by design; what breaks reproducibility is a modified tracked
    # file, since that is what the recorded commit no longer describes.
    status = run("status", "--porcelain", "-uno")
    return {
        "git_commit": commit,
        "git_dirty": bool(status) if status is not None else None,
        "git_remote": run("config", "--get", "remote.origin.url"),
    }


def parse_tags(pairs: Iterable[str]) -> Dict[str, str]:
    tags: Dict[str, str] = {}
    for p in pairs:
        if "=" not in p:
            sys.exit(f"tag must be key=value, got: {p}")
        k, v = p.split("=", 1)
        tags[k.strip()] = v.strip()
    return tags


# --------------------------------------------------------------------------
# registry
# --------------------------------------------------------------------------

class Ledger:
    def __init__(self, root: Path):
        self.root = root
        self.ledger_dir = root / "ledger"
        self.runs_dir = root / "runs"
        self.comparisons_dir = root / "comparisons"
        self.jsonl = self.ledger_dir / "runs.jsonl"

    def ensure(self) -> None:
        for d in (self.ledger_dir, self.runs_dir, self.comparisons_dir):
            d.mkdir(parents=True, exist_ok=True)

    def append(self, event: Dict[str, Any]) -> None:
        self.ensure()
        event.setdefault("ts", utcnow())
        with open(self.jsonl, "a") as f:
            f.write(canonical(event) + "\n")

    def events(self) -> List[Dict[str, Any]]:
        if not self.jsonl.exists():
            return []
        out = []
        for i, line in enumerate(self.jsonl.read_text().splitlines(), 1):
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                print(f"warning: registry line {i} is not valid JSON, skipped",
                      file=sys.stderr)
        return out

    def state(self) -> Dict[str, Dict[str, Any]]:
        """Fold the event log into current per-run state."""
        runs: Dict[str, Dict[str, Any]] = {}
        for e in self.events():
            rid = e.get("run_id")
            if not rid:
                continue
            r = runs.setdefault(rid, {"run_id": rid, "metrics": {}, "tags": {}})
            kind = e.get("event")
            if kind == "created":
                r.update({k: v for k, v in e.items()
                          if k not in {"event", "ts", "metrics"}})
                r["created_ts"] = e.get("ts")
            elif kind == "recorded":
                r["metrics"].update(e.get("metrics") or {})
                r["recorded_ts"] = e.get("ts")
            elif kind == "invalidated":
                r["invalidated"] = True
                r["invalidated_reason"] = e.get("reason")
            if e.get("tags"):
                r["tags"].update(e["tags"])
        return runs


# --------------------------------------------------------------------------
# subcommands
# --------------------------------------------------------------------------

def cmd_preregister(a: argparse.Namespace) -> int:
    led = Ledger(Path(a.root))
    led.ensure()
    path = led.comparisons_dir / f"{a.name}.yaml"
    if path.exists() and not a.force:
        sys.exit(f"{path} already exists. Amend it by appending to `amendments:`, "
                 f"not by overwriting. Use --force only to fix a same-day typo.")

    arms = [s.strip() for s in a.arms.split(",") if s.strip()]
    if a.reference and a.reference not in arms:
        sys.exit(f"reference arm '{a.reference}' is not in --arms")
    reference = a.reference or arms[0]

    doc = {
        "name": a.name,
        "declared_utc": utcnow(),
        "declared_at_commit": git_info(Path(a.root)).get("git_commit"),
        "question": a.question or "",
        "arms": [
            {"id": arm, "role": "reference" if arm == reference else "treatment"}
            for arm in arms
        ],
        "primary_metric": a.primary_metric,
        "primary_unit": a.unit,
        "secondary_metrics": [s.strip() for s in (a.secondary or "").split(",") if s.strip()],
        "hypothesis": a.hypothesis or "",
        "analysis_plan": a.analysis or "",
        "stopping_rule": a.stopping or "all declared arms run to completion; "
                                       "no interim inspection of the primary metric",
        "amendments": [],
    }
    dump_structured(doc, path)
    led.append({"event": "preregistered", "comparison": a.name,
                "arms": arms, "reference": reference,
                "primary_metric": a.primary_metric})
    print(f"declared {path}")
    print(f"  reference arm : {reference}")
    print(f"  primary metric: {a.primary_metric} (unit: {a.unit})")
    print("Edit the file to fill in question, hypothesis, and analysis plan "
          "before running anything.")
    return 0


def cmd_new(a: argparse.Namespace) -> int:
    root = Path(a.root)
    led = Ledger(root)
    led.ensure()

    base = load_structured(Path(a.config))
    resolved = base
    for ov in a.overlay or []:
        resolved = deep_merge(resolved, load_structured(Path(ov)))

    git = git_info(root)
    config_sha = sha256_str(canonical(resolved))
    run_id = sha256_str(config_sha + (git.get("git_commit") or "nogit"))[:16]

    run_dir = led.runs_dir / run_id
    new_tags = parse_tags(a.tag or [])
    if run_dir.exists():
        # An identical config plus commit is the same experiment, so a collision
        # is normally benign. It is not benign when the two invocations claim to
        # be different arms: that means an overlay had no effect (a typo in a key
        # nests a new branch instead of overriding one) and the "ablation" is
        # comparing a config against itself.
        prev_arm = None
        mpath = run_dir / "manifest.json"
        if mpath.exists():
            try:
                prev_arm = (json.loads(mpath.read_text()).get("tags") or {}).get("arm")
            except Exception:
                pass
        if prev_arm and new_tags.get("arm") and prev_arm != new_tags["arm"]:
            print(f"ERROR: arm '{new_tags['arm']}' resolves to the same config as "
                  f"arm '{prev_arm}' (run_id {run_id}).", file=sys.stderr)
            print("The overlay changed nothing. Check for a misspelled key: a typo "
                  "adds a new branch instead of overriding the intended one.",
                  file=sys.stderr)
            return 2
        if not a.force:
            if not a.quiet:
                print(f"run {run_id} already exists at {run_dir}", file=sys.stderr)
                print("Nothing re-run. Use --force to recreate, or change the config "
                      "or seed if a genuinely different run was intended.", file=sys.stderr)
            print(run_id)
            return 0

    (run_dir / "logs").mkdir(parents=True, exist_ok=True)
    cfg_out = run_dir / ("config.resolved.yaml" if yaml else "config.resolved.json")
    dump_structured(resolved, cfg_out)

    tags = new_tags
    manifest = {
        "run_id": run_id,
        "created_utc": utcnow(),
        "tags": tags,
        "code": {**git, "entrypoint": a.entrypoint},
        "config": {
            "path": str(a.config),
            "overlays": list(a.overlay or []),
            "resolved_sha256": config_sha,
            "resolved_path": str(cfg_out.relative_to(root)) if root in cfg_out.parents else str(cfg_out),
        },
        "data": {},
        "model": {},
        "prompt": {},
        "env": {
            "python": sys.version.split()[0],
            "slurm_job_id": os.environ.get("SLURM_JOB_ID"),
            "slurm_array_job_id": os.environ.get("SLURM_ARRAY_JOB_ID"),
        },
        "determinism": {"seed": resolved.get("seed"), "claimed_deterministic": False},
    }
    if a.split:
        sp = Path(a.split)
        manifest["data"] = {"split_file": str(sp), "split_sha256": sha256_file(sp)}
    if a.prompt:
        pp = Path(a.prompt)
        manifest["prompt"] = {"template_path": str(pp),
                              "template_sha256": sha256_file(pp)}
    (run_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")

    led.append({"event": "created", "run_id": run_id, "tags": tags,
                "config_sha256": config_sha, **git,
                "config_path": str(a.config), "overlays": list(a.overlay or [])})

    if not a.quiet:
        print(f"run_id   : {run_id}")
        print(f"run_dir  : {run_dir}")
        print(f"config   : {cfg_out}")
        if git.get("git_dirty"):
            print("WARNING  : working tree is dirty. This run is not reproducible "
                  "from the recorded commit.", file=sys.stderr)
        print("Fill data/model/prompt fields in manifest.json from the job, then "
              "`record` the metrics.")
    else:
        print(run_id)
    return 0


def cmd_record(a: argparse.Namespace) -> int:
    led = Ledger(Path(a.root))
    run_dir = led.runs_dir / a.run
    if not run_dir.exists():
        sys.exit(f"unknown run {a.run}; create it with `new` first")

    if a.metrics:
        metrics = load_structured(Path(a.metrics))
    else:
        metrics = {}
        for kv in a.metric or []:
            k, v = kv.split("=", 1)
            metrics[k.strip()] = float(v)
    if not metrics:
        sys.exit("nothing to record: pass --metrics <file> or --metric k=v")

    bad = [k for k, v in metrics.items() if not isinstance(v, (int, float))]
    if bad:
        sys.exit(f"non-numeric metric values are not recordable: {bad}")

    (run_dir / "metrics.json").write_text(json.dumps(metrics, indent=2, sort_keys=True) + "\n")
    led.append({"event": "recorded", "run_id": a.run, "metrics": metrics,
                "tags": parse_tags(a.tag or [])})
    print(f"recorded {len(metrics)} metrics for {a.run}")
    return 0


def _select(runs: Dict[str, Dict[str, Any]], comparison: Optional[str],
            tags: Dict[str, str]) -> List[Dict[str, Any]]:
    out = []
    for r in runs.values():
        if r.get("invalidated"):
            continue
        t = r.get("tags", {})
        if comparison and t.get("comparison") != comparison:
            continue
        if any(t.get(k) != v for k, v in tags.items()):
            continue
        out.append(r)
    out.sort(key=lambda r: (r.get("tags", {}).get("arm", ""), r.get("created_ts", "")))
    return out


def cmd_list(a: argparse.Namespace) -> int:
    led = Ledger(Path(a.root))
    rows = _select(led.state(), a.comparison, parse_tags(a.tag or []))
    if not rows:
        print("no matching runs")
        return 0
    for r in rows:
        t = r.get("tags", {})
        m = r.get("metrics", {})
        flag = " DIRTY" if r.get("git_dirty") else ""
        summary = ", ".join(f"{k}={v:.4g}" for k, v in sorted(m.items())[:4]) or "no metrics"
        print(f"{r['run_id']}  arm={t.get('arm','-'):<14} {summary}{flag}")
    return 0


def _fmt(v: Any, nd: int) -> str:
    return f"{v:.{nd}f}" if isinstance(v, (int, float)) else "-"


def cmd_table(a: argparse.Namespace) -> int:
    led = Ledger(Path(a.root))
    rows = _select(led.state(), a.comparison, parse_tags(a.tag or []))
    rows = [r for r in rows if r.get("metrics")]
    if not rows:
        sys.exit("no runs with recorded metrics matched")

    if a.metrics:
        cols = [c.strip() for c in a.metrics.split(",")]
    else:
        cols = sorted({k for r in rows for k in r["metrics"]})
    lower = {c.strip() for c in (a.lower_is_better or "").split(",") if c.strip()}

    # Group repeated runs of the same arm so a seed sweep reports spread rather
    # than a single point estimate.
    grouped: Dict[str, List[Dict[str, Any]]] = {}
    for r in rows:
        grouped.setdefault(r.get("tags", {}).get("arm", r["run_id"][:8]), []).append(r)

    body: List[List[str]] = []
    numeric: Dict[str, Dict[str, float]] = {}
    for arm, rs in grouped.items():
        cells = [arm]
        numeric[arm] = {}
        for c in cols:
            vals = [r["metrics"][c] for r in rs if c in r["metrics"]]
            if not vals:
                cells.append("-")
                continue
            mean = sum(vals) / len(vals)
            numeric[arm][c] = mean
            if len(vals) > 1:
                sd = (sum((v - mean) ** 2 for v in vals) / (len(vals) - 1)) ** 0.5
                cells.append(f"{_fmt(mean, a.decimals)} ({_fmt(sd, a.decimals)}, n={len(vals)})")
            else:
                cells.append(_fmt(mean, a.decimals))
        body.append(cells)

    best = {}
    for c in cols:
        vals = {arm: numeric[arm][c] for arm in numeric if c in numeric[arm]}
        if vals:
            best[c] = (min if c in lower else max)(vals, key=vals.get)

    header = ["arm"] + cols
    if a.format == "csv":
        w = csv.writer(sys.stdout)
        w.writerow(header)
        w.writerows(body)
    elif a.format == "latex":
        print("% generated by ledger.py table; do not edit by hand")
        print("\\begin{tabular}{l" + "r" * len(cols) + "}")
        print("\\toprule")
        print(" & ".join(h.replace("_", "\\_") for h in header) + " \\\\")
        print("\\midrule")
        for cells in body:
            arm = cells[0]
            out = [arm.replace("_", "\\_")]
            for c, cell in zip(cols, cells[1:]):
                out.append(f"\\textbf{{{cell}}}" if best.get(c) == arm and cell != "-" else cell)
            print(" & ".join(out) + " \\\\")
        print("\\bottomrule")
        print("\\end{tabular}")
    else:
        widths = [max(len(header[i]), *(len(r[i]) for r in body)) for i in range(len(header))]
        print("| " + " | ".join(h.ljust(w) for h, w in zip(header, widths)) + " |")
        print("|" + "|".join("-" * (w + 2) for w in widths) + "|")
        for cells in body:
            print("| " + " | ".join(c.ljust(w) for c, w in zip(cells, widths)) + " |")

    if a.comparison:
        print(f"\n% source: comparison={a.comparison}, "
              f"{len(rows)} runs, generated {utcnow()}", file=sys.stderr)
    return 0


def cmd_verify(a: argparse.Namespace) -> int:
    root = Path(a.root)
    led = Ledger(root)
    runs = led.state()
    findings: List[str] = []

    for rid, r in runs.items():
        if r.get("invalidated"):
            continue
        run_dir = led.runs_dir / rid
        if not run_dir.exists():
            findings.append(f"{rid}: registry entry has no run directory")
            continue

        # Config drift: does the stored resolved config still hash to the id?
        cfg = next((p for p in (run_dir / "config.resolved.yaml",
                                run_dir / "config.resolved.json") if p.exists()), None)
        if cfg is None:
            findings.append(f"{rid}: no resolved config stored")
        else:
            try:
                sha = sha256_str(canonical(load_structured(cfg)))
                if r.get("config_sha256") and sha != r["config_sha256"]:
                    findings.append(
                        f"{rid}: resolved config was modified after the run "
                        f"(hash {sha[:12]} != registry {r['config_sha256'][:12]})")
            except Exception as exc:
                findings.append(f"{rid}: could not re-hash config ({exc})")

        if r.get("git_dirty"):
            findings.append(f"{rid}: produced from a dirty working tree, "
                            f"not reproducible from commit {r.get('git_commit')}")
        if not r.get("metrics"):
            findings.append(f"{rid}: created but never recorded")

    # Comparison integrity.
    for decl_path in sorted(led.comparisons_dir.glob("*.y*ml")):
        try:
            decl = load_structured(decl_path)
        except Exception as exc:
            findings.append(f"{decl_path.name}: unreadable ({exc})")
            continue
        name = decl.get("name") or decl_path.stem
        declared = {arm["id"] if isinstance(arm, dict) else arm for arm in decl.get("arms", [])}
        recorded = {r.get("tags", {}).get("arm") for r in runs.values()
                    if r.get("tags", {}).get("comparison") == name and r.get("metrics")}
        recorded.discard(None)

        undeclared = recorded - declared
        if undeclared:
            findings.append(
                f"{name}: arms recorded but not declared: {sorted(undeclared)}. "
                f"These are exploratory unless the declaration was amended; "
                f"do not report them as part of the confirmatory comparison.")
        missing = declared - recorded
        if missing:
            findings.append(f"{name}: declared arms with no recorded result: {sorted(missing)}")

        declared_ts = decl.get("declared_utc")
        if declared_ts:
            late = [r["run_id"] for r in runs.values()
                    if r.get("tags", {}).get("comparison") == name
                    and r.get("created_ts") and r["created_ts"] < declared_ts]
            if late:
                findings.append(
                    f"{name}: runs predate the declaration ({sorted(late)}). "
                    f"The comparison was declared after these results existed.")

        # All arms of a comparison must share preprocessing and split.
        splits = {}
        for r in runs.values():
            if r.get("tags", {}).get("comparison") != name:
                continue
            mpath = led.runs_dir / r["run_id"] / "manifest.json"
            if mpath.exists():
                try:
                    m = json.loads(mpath.read_text())
                    s = (m.get("data") or {}).get("split_sha256")
                    if s:
                        splits.setdefault(s, []).append(r["run_id"])
                except Exception:
                    pass
        if len(splits) > 1:
            findings.append(
                f"{name}: arms used different data splits {list(splits.values())}. "
                f"These results are not comparable.")

    if findings:
        print(f"{len(findings)} finding(s):\n")
        for f in findings:
            print(f"  - {f}")
        print("\nFix or explicitly justify each before generating a paper table.")
        return 1 if a.strict else 0
    print("verify: no findings")
    return 0


# --------------------------------------------------------------------------

def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--root", default=".", help="project root containing runs/ and ledger/")
    sub = p.add_subparsers(dest="cmd", required=True)

    q = sub.add_parser("preregister", help="declare a comparison before running it")
    q.add_argument("--name", required=True)
    q.add_argument("--arms", required=True, help="comma separated arm ids")
    q.add_argument("--reference", default="", help="reference arm; defaults to the first")
    q.add_argument("--primary-metric", required=True)
    q.add_argument("--unit", default="item", help="unit of analysis, e.g. patient")
    q.add_argument("--secondary", default="")
    q.add_argument("--question", default="")
    q.add_argument("--hypothesis", default="")
    q.add_argument("--analysis", default="")
    q.add_argument("--stopping", default="")
    q.add_argument("--force", action="store_true")
    q.set_defaults(func=cmd_preregister)

    n = sub.add_parser("new", help="resolve a config and create a run")
    n.add_argument("--config", required=True)
    n.add_argument("--overlay", action="append", default=[])
    n.add_argument("--tag", action="append", default=[], help="key=value, repeatable")
    n.add_argument("--split", default="", help="split file to hash into the manifest")
    n.add_argument("--prompt", default="", help="prompt template to hash")
    n.add_argument("--entrypoint", default="")
    n.add_argument("--force", action="store_true")
    n.add_argument("--quiet", action="store_true", help="print only the run_id")
    n.set_defaults(func=cmd_new)

    r = sub.add_parser("record", help="attach metrics to a run")
    r.add_argument("--run", required=True)
    r.add_argument("--metrics", default="", help="json or yaml file of scalar metrics")
    r.add_argument("--metric", action="append", default=[], help="key=value, repeatable")
    r.add_argument("--tag", action="append", default=[])
    r.set_defaults(func=cmd_record)

    l = sub.add_parser("list", help="list runs")
    l.add_argument("--comparison", default="")
    l.add_argument("--tag", action="append", default=[])
    l.set_defaults(func=cmd_list)

    t = sub.add_parser("table", help="generate a results table")
    t.add_argument("--comparison", default="")
    t.add_argument("--tag", action="append", default=[])
    t.add_argument("--metrics", default="", help="comma separated column order")
    t.add_argument("--lower-is-better", default="ece,brier,nll,risk",
                   help="metrics where smaller is better, for bolding")
    t.add_argument("--format", choices=["markdown", "latex", "csv"], default="markdown")
    t.add_argument("--decimals", type=int, default=3)
    t.set_defaults(func=cmd_table)

    v = sub.add_parser("verify", help="check registry and comparison integrity")
    v.add_argument("--strict", action="store_true", help="exit nonzero on findings")
    v.set_defaults(func=cmd_verify)

    a = p.parse_args()
    return a.func(a)


if __name__ == "__main__":
    raise SystemExit(main())
