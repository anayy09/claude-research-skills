#!/usr/bin/env python3
"""
project_ledger.py - The operating record of a research project: decisions,
progress, results, gates, and the session hand-off, kept append-only and
checked mechanically.

A project run by an agent across many sessions decays in a specific way:
decisions get silently reversed because nobody remembers why they were made,
a number in the paper stops matching the run that produced it, a gate is
declared passed without its check being run, and each new session starts
from a hand-written brief that is as good as the last person's memory. This
script keeps the record that prevents that, and generates the next session's
brief from the record instead of from memory.

Documents it manages (under docs/ by default):

    DECISIONS.md      D-NNN entries: decision, alternatives, rationale, consequences, status
    PROGRESS.md       NNNN entries: one per step, append-only, typed
    RESULTS-LOG.md    R-NNNN entries: one per reported metric, interval required
    GATES.md          - [ ] G1: <claim>  CHECK: <cmd>  EXPECT: <text>  EVIDENCE: <what ran>
    RUNBOOK.md        state and resume commands for long-running work
    PREREGISTRATION.md, PLAN.md, AGENT.md, SKILL-ROUTING.md   scaffolded, hand-edited

Commands:
    init       scaffold the documents from the bundled templates (never overwrites)
    next       print the next free id: next D | P | R
    append     add an entry with the fields validated: append decision|progress|result ...
    verify     append-only against git HEAD, id monotonicity, dangling references,
               results without intervals, open decisions
    state      one screen: counts, open decisions, blocked steps, last steps, gates
    gates      list gates; --run executes each CHECK and compares with EXPECT;
               --record writes the EVIDENCE line and ticks the box on success
    handoff    print the continuation brief for the next session, built from the
               record (git state, open decisions, last steps, next ids, read order)

Usage:
    python project_ledger.py init --name cpath-elicit
    python project_ledger.py next D
    python project_ledger.py append decision --title "Resampling unit is the patient" \\
        --decision "..." --alternatives "..." --rationale "..." --consequences "..."
    python project_ledger.py append progress --type RUN --role R4 --phase P2 \\
        --what "Ran D5 on val-1800" --result "1800/1800 parsed" --artifacts experiments/P2-D5 \\
        --refs "D-007, R-0042" --status done --next "adjudicate GATE A"
    python project_ledger.py append result --run-id P2-D5-val1800-20260901-a3f19c4e21b7 \\
        --metric AAUC --value 0.4123 --interval "[0.3987, 0.4251]" --method "paired-bootstrap(B=2000)"
    python project_ledger.py verify --git
    python project_ledger.py gates --run --record
    python project_ledger.py handoff > /dev/null   # print it; paste it into the new session
    python project_ledger.py --self-test

Standard library only. Exit codes: 0 ok, 1 a verify or gate failure, 2 usage.
"""
from __future__ import annotations

import argparse
import datetime as dt
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple

HERE = Path(__file__).resolve().parent
TEMPLATES = HERE.parent / "templates"

DOCS = ["PLAN.md", "DECISIONS.md", "PROGRESS.md", "RESULTS-LOG.md", "PREREGISTRATION.md",
        "GATES.md", "RUNBOOK.md", "AGENT.md", "SKILL-ROUTING.md", "AUTHORS.yaml"]

D_HEAD = re.compile(r"^## D-(\d{3,4})\.\s*(.*)$", re.M)
P_HEAD = re.compile(r"^### (\d{4}) \| ([^|]+) \| ([A-Z-]+) \| ([^|]+) \| ([^|\n]+)$", re.M)
R_HEAD = re.compile(r"^### R-(\d{4}) \| (.*)$", re.M)
G_LINE = re.compile(r"^- \[( |x)\] (G[0-9A-Za-z.]+): (.*)$", re.M)
PROGRESS_TYPES = {"PHASE-OPEN", "PHASE-CLOSE", "SETUP", "RUN", "ANALYSIS", "GATE", "DECISION",
                  "LIT", "WRITE", "BUILD", "CORRECTION", "BLOCKED", "HANDOFF"}


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def today() -> str:
    return dt.date.today().isoformat()


def read(p: Path) -> str:
    return p.read_text(encoding="utf-8") if p.exists() else ""


def git(args: List[str], cwd: Path) -> Tuple[int, str]:
    if not shutil.which("git"):
        return 127, "git not on PATH"
    try:
        p = subprocess.run(["git"] + args, cwd=str(cwd), capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=60)
        return p.returncode, (p.stdout or "") + (p.stderr or "")
    except Exception as exc:  # pragma: no cover
        return 1, str(exc)


# ---------------------------------------------------------------------------
# parsing
# ---------------------------------------------------------------------------

def split_entries(text: str, head: re.Pattern) -> List[Tuple[re.Match, str]]:
    """Return [(heading match, entry text incl. heading)] in file order."""
    heads = list(head.finditer(text))
    out = []
    for i, m in enumerate(heads):
        end = heads[i + 1].start() if i + 1 < len(heads) else len(text)
        out.append((m, text[m.start():end].rstrip() + "\n"))
    return out


def field_value(entry: str, name: str) -> str:
    m = re.search(r"^- \*{0,2}" + re.escape(name) + r":?\*{0,2}:?\s*(.*)$", entry, re.M | re.I)
    return m.group(1).strip() if m else ""


def decisions(docs: Path) -> List[dict]:
    out = []
    for m, body in split_entries(read(docs / "DECISIONS.md"), D_HEAD):
        out.append({"id": int(m.group(1)), "title": m.group(2).strip(),
                    "status": field_value(body, "Status").lower(), "date": field_value(body, "Date"),
                    "text": body})
    return out


def progress(docs: Path) -> List[dict]:
    out = []
    for m, body in split_entries(read(docs / "PROGRESS.md"), P_HEAD):
        out.append({"seq": int(m.group(1)), "ts": m.group(2).strip(), "type": m.group(3).strip(),
                    "role": m.group(4).strip(), "phase": m.group(5).strip(),
                    "status": field_value(body, "Status").lower(), "what": field_value(body, "What"),
                    "next": field_value(body, "Next"), "refs": field_value(body, "Refs"), "text": body})
    return out


def results(docs: Path) -> List[dict]:
    out = []
    for m, body in split_entries(read(docs / "RESULTS-LOG.md"), R_HEAD):
        out.append({"id": int(m.group(1)), "run_id": m.group(2).strip(),
                    "metric": field_value(body, "Metric"), "value": field_value(body, "Value"),
                    "interval": field_value(body, "Interval"), "method": field_value(body, "Interval method"),
                    "supersedes": field_value(body, "Supersedes"), "text": body})
    return out


def gates(docs: Path) -> List[dict]:
    text = read(docs / "GATES.md")
    out = []
    for m in G_LINE.finditer(text):
        start = m.end()
        nxt = G_LINE.search(text, start)
        block = text[start:nxt.start() if nxt else len(text)]
        g = {"id": m.group(2), "done": m.group(1) == "x", "claim": m.group(3).strip(),
             "check": "", "expect": "", "evidence": "", "line_start": m.start(), "block_end": (nxt.start() if nxt else len(text))}
        for key in ("CHECK", "EXPECT", "EVIDENCE"):
            km = re.search(r"^\s+" + key + r":\s*(.*)$", block, re.M)
            if km:
                g[key.lower()] = km.group(1).strip()
        out.append(g)
    return out


# ---------------------------------------------------------------------------
# init / next / append
# ---------------------------------------------------------------------------

def cmd_init(a: argparse.Namespace) -> int:
    docs = Path(a.dir)
    docs.mkdir(parents=True, exist_ok=True)
    if not TEMPLATES.exists():
        print(f"error: templates directory not found at {TEMPLATES}", file=sys.stderr)
        return 2
    created, kept = [], []
    for name in DOCS:
        src = TEMPLATES / name
        dst = docs / name
        if dst.exists():
            kept.append(name)
            continue
        text = read(src).replace("{{PROJECT}}", a.name).replace("{{DATE}}", today())
        dst.write_text(text, encoding="utf-8", newline="\n")
        created.append(name)
    print("created: " + (", ".join(created) or "nothing"))
    if kept:
        print("kept (already existed): " + ", ".join(kept))
    print("\nNext: fill PLAN.md and PREREGISTRATION.md by hand, open D-001 for the direction, "
          "and run `verify` before the first commit.")
    return 0


def next_id(docs: Path, kind: str) -> int:
    kind = kind.upper()
    if kind == "D":
        ids = [d["id"] for d in decisions(docs)]
    elif kind == "P":
        ids = [p["seq"] for p in progress(docs)]
    elif kind == "R":
        ids = [r["id"] for r in results(docs)]
    else:
        raise ValueError("kind must be D, P, or R")
    return (max(ids) + 1) if ids else 1


def cmd_next(a: argparse.Namespace) -> int:
    n = next_id(Path(a.dir), a.kind)
    fmt = {"D": "D-{:03d}", "P": "{:04d}", "R": "R-{:04d}"}[a.kind.upper()]
    print(fmt.format(n))
    return 0


def append_text(path: Path, entry: str) -> None:
    text = read(path)
    if text and not text.endswith("\n"):
        text += "\n"
    if text and not text.endswith("\n\n"):
        text += "\n"
    path.write_text(text + entry.rstrip() + "\n", encoding="utf-8", newline="\n")


def cmd_append(a: argparse.Namespace) -> int:
    docs = Path(a.dir)
    if a.what_kind == "decision":
        n = next_id(docs, "D")
        missing = [f for f in ("title", "decision", "alternatives", "rationale", "consequences") if not getattr(a, f)]
        if missing:
            print("error: a decision needs " + ", ".join(f"--{m}" for m in missing), file=sys.stderr)
            return 2
        entry = (f"## D-{n:03d}. {a.title}\n\n"
                 f"- **Date:** {today()}\n"
                 f"- **Status:** {a.status}\n"
                 f"- **Decision:** {a.decision}\n"
                 f"- **Alternatives considered:** {a.alternatives}\n"
                 f"- **Rationale:** {a.rationale}\n"
                 f"- **Consequences:** {a.consequences}\n"
                 f"- **Revisit if:** {a.revisit or 'not expected'}\n\n---\n")
        append_text(docs / "DECISIONS.md", entry)
        print(f"appended D-{n:03d} ({a.status})")
        return 0
    if a.what_kind == "progress":
        n = next_id(docs, "P")
        if a.type not in PROGRESS_TYPES:
            print(f"error: --type must be one of {', '.join(sorted(PROGRESS_TYPES))}", file=sys.stderr)
            return 2
        if not a.what:
            print("error: --what is required", file=sys.stderr)
            return 2
        if a.type == "CORRECTION" and not a.refs:
            print("error: a CORRECTION must name the entry it corrects in --refs", file=sys.stderr)
            return 2
        if a.type == "BLOCKED" and a.status != "blocked":
            a.status = "blocked"
        entry = (f"### {n:04d} | {now_iso()} | {a.type} | {a.role} | {a.phase}\n"
                 f"- What: {a.what}\n"
                 f"- Result: {a.result or 'n/a'}\n"
                 f"- Artifacts: {a.artifacts or 'none'}\n"
                 f"- Refs: {a.refs or 'none'}\n"
                 f"- Status: {a.status}\n"
                 f"- Next: {a.next or 'n/a'}\n")
        append_text(docs / "PROGRESS.md", entry)
        print(f"appended {n:04d} {a.type} ({a.status})")
        return 0
    if a.what_kind == "result":
        n = next_id(docs, "R")
        missing = [f for f in ("run_id", "metric", "value", "interval", "method") if not getattr(a, f)]
        if missing:
            print("error: a result needs " + ", ".join(f"--{m.replace('_', '-')}" for m in missing)
                  + " (no point estimate without an interval and the method that produced it)", file=sys.stderr)
            return 2
        entry = (f"### R-{n:04d} | {a.run_id}\n"
                 f"- Date: {today()}\n"
                 f"- Phase: {a.phase}\n"
                 f"- Metric: {a.metric}\n"
                 f"- n: {a.n or 'n/a'}\n"
                 f"- Value: {a.value}\n"
                 f"- Interval: {a.interval}\n"
                 f"- Interval method: {a.method}\n"
                 f"- Comparison: {a.comparison or 'none'}\n"
                 f"- Notes: {a.notes or 'none'}\n"
                 f"- Supersedes: {a.supersedes or 'none'}\n")
        append_text(docs / "RESULTS-LOG.md", entry)
        print(f"appended R-{n:04d} {a.metric} = {a.value} {a.interval}")
        return 0
    return 2


# ---------------------------------------------------------------------------
# verify
# ---------------------------------------------------------------------------

def strip_status(text: str) -> str:
    return re.sub(r"^- \*{0,2}Status:?\*{0,2}:?.*$", "", text, flags=re.M | re.I)


def verify(docs: Path, use_git: bool) -> Tuple[List[str], List[str]]:
    fails: List[str] = []
    warns: List[str] = []
    D, P, R = decisions(docs), progress(docs), results(docs)

    # ids monotone and, for P and R, gap-free
    for name, items, key in (("DECISIONS", D, "id"), ("PROGRESS", P, "seq"), ("RESULTS-LOG", R, "id")):
        ids = [i[key] for i in items]
        if ids != sorted(ids):
            fails.append(f"{name}: ids are not in increasing order")
        dup = {i for i in ids if ids.count(i) > 1}
        if dup:
            fails.append(f"{name}: duplicate ids {sorted(dup)}")
        if name != "DECISIONS" and ids and ids != list(range(ids[0], ids[0] + len(ids))):
            fails.append(f"{name}: gaps in the sequence (an abandoned entry is completed with Status: abandoned, never removed)")

    # references resolve
    d_ids = {f"D-{d['id']:03d}" for d in D} | {f"D-{d['id']:04d}" for d in D}
    r_ids = {f"R-{r['id']:04d}" for r in R}
    p_ids = {f"{p['seq']:04d}" for p in P}
    for p in P:
        for ref in re.findall(r"\bD-\d{3,4}\b", p["refs"]):
            if ref not in d_ids:
                fails.append(f"PROGRESS {p['seq']:04d} refers to {ref}, which does not exist")
        for ref in re.findall(r"\bR-\d{4}\b", p["refs"]):
            if ref not in r_ids:
                fails.append(f"PROGRESS {p['seq']:04d} refers to {ref}, which does not exist")
        if p["type"] == "CORRECTION" and not re.search(r"\b\d{4}\b|\bD-\d+|\bR-\d+", p["refs"]):
            fails.append(f"PROGRESS {p['seq']:04d} is a CORRECTION with no entry named in Refs")
    for r in R:
        sup = r["supersedes"]
        if sup and sup.lower() != "none":
            for ref in re.findall(r"\bR-\d{4}\b", sup):
                if ref not in r_ids:
                    fails.append(f"RESULTS-LOG R-{r['id']:04d} supersedes {ref}, which does not exist")
        if r["value"] and (not r["interval"] or r["interval"].lower() in ("", "none", "tbd", "-")):
            fails.append(f"RESULTS-LOG R-{r['id']:04d} ({r['metric']}) has a value with no interval")
        if r["value"] and not r["method"]:
            fails.append(f"RESULTS-LOG R-{r['id']:04d} ({r['metric']}) has no interval method")
    for d in D:
        m = re.search(r"superseded by (D-\d{3,4})", d["status"], re.I)
        if m and m.group(1).upper() not in d_ids:
            fails.append(f"DECISIONS D-{d['id']:03d} superseded by {m.group(1)}, which does not exist")
        if not d["status"]:
            fails.append(f"DECISIONS D-{d['id']:03d} has no Status line")

    # append-only against git
    if use_git:
        root_rc, root = git(["rev-parse", "--show-toplevel"], docs)
        if root_rc != 0:
            warns.append("not a git repository; append-only check skipped")
        else:
            root = Path(root.strip())
            for name, head, strict in (("DECISIONS.md", D_HEAD, False), ("PROGRESS.md", P_HEAD, True), ("RESULTS-LOG.md", R_HEAD, True)):
                rel = (docs / name).resolve().relative_to(root.resolve()).as_posix()
                rc, committed = git(["show", f"HEAD:{rel}"], root)
                if rc != 0:
                    warns.append(f"{name}: not in HEAD yet; append-only check skipped")
                    continue
                cur = read(docs / name)
                old_entries = {m.group(1): body for m, body in split_entries(committed, head)}
                new_entries = {m.group(1): body for m, body in split_entries(cur, head)}
                for eid, body in old_entries.items():
                    if eid not in new_entries:
                        fails.append(f"{name}: committed entry {eid} was removed")
                        continue
                    a_, b_ = (body, new_entries[eid]) if strict else (strip_status(body), strip_status(new_entries[eid]))
                    if a_.strip() != b_.strip():
                        what = "edited in place (append a correction instead)" if strict else "edited beyond its Status line"
                        fails.append(f"{name}: committed entry {eid} was {what}")

    open_d = [d for d in D if d["status"].startswith("open")]
    blocked = [p for p in P if p["status"] == "blocked"]
    if open_d:
        warns.append(f"{len(open_d)} open decision(s): " + ", ".join(f"D-{d['id']:03d}" for d in open_d))
    if blocked:
        warns.append(f"{len(blocked)} blocked step(s): " + ", ".join(f"{p['seq']:04d}" for p in blocked))
    return fails, warns


def cmd_verify(a: argparse.Namespace) -> int:
    fails, warns = verify(Path(a.dir), a.git)
    for f in fails:
        print(f"FAIL {f}")
    for w in warns:
        print(f"note {w}")
    print(f"\n{len(fails)} failure(s), {len(warns)} note(s)")
    return 1 if fails else 0


# ---------------------------------------------------------------------------
# state / gates / handoff
# ---------------------------------------------------------------------------

def git_state(docs: Path) -> str:
    rc, top = git(["rev-parse", "--show-toplevel"], docs)
    if rc != 0:
        return "not a git repository"
    root = Path(top.strip())
    _, sha = git(["rev-parse", "--short", "HEAD"], root)
    _, branch = git(["rev-parse", "--abbrev-ref", "HEAD"], root)
    _, status = git(["status", "--porcelain"], root)
    _, ahead = git(["rev-list", "--count", "@{u}..HEAD"], root)
    dirty = len([l for l in status.splitlines() if l.strip()])
    ahead_s = ahead.strip() if ahead.strip().isdigit() else "?"
    return (f"branch {branch.strip()} at {sha.strip()}, "
            f"{'clean' if dirty == 0 else f'{dirty} uncommitted path(s)'}, "
            f"{ahead_s} commit(s) not pushed")


def state_text(docs: Path) -> str:
    D, P, R, G = decisions(docs), progress(docs), results(docs), gates(docs)
    lines = [f"# State of {docs.resolve().parent.name} ({today()})", ""]
    lines.append(f"Repository: {git_state(docs)}")
    lines.append(f"Ledger: {len(D)} decisions ({sum(1 for d in D if d['status'].startswith('open'))} open), "
                 f"{len(P)} progress entries, {len(R)} results, {sum(1 for g in G if g['done'])}/{len(G)} gates met")
    lines.append(f"Next ids: D-{next_id(docs, 'D'):03d}, PROGRESS {next_id(docs, 'P'):04d}, R-{next_id(docs, 'R'):04d}")
    lines.append("")
    open_d = [d for d in D if d["status"].startswith("open")]
    if open_d:
        lines.append("## Open decisions (yours to rule on)")
        for d in open_d:
            lines.append(f"- D-{d['id']:03d} {d['title']} ({d['status']})")
        lines.append("")
    blocked = [p for p in P if p["status"] == "blocked"]
    if blocked:
        lines.append("## Blocked steps")
        for p in blocked:
            lines.append(f"- {p['seq']:04d} {p['what']}")
        lines.append("")
    if P:
        lines.append("## Last steps")
        for p in P[-3:]:
            lines.append(f"- {p['seq']:04d} {p['type']} {p['phase']}: {p['what']} [{p['status']}]")
        lines.append(f"- Next, as recorded: {P[-1]['next']}")
        lines.append("")
    unmet = [g for g in G if not g["done"]]
    if unmet:
        lines.append("## Gates not yet met")
        for g in unmet[:10]:
            lines.append(f"- {g['id']}: {g['claim']}")
        lines.append("")
    rb = read(docs / "RUNBOOK.md")
    m = re.search(r"^## State.*?$(.*?)(?=^## |\Z)", rb, re.M | re.S)
    if m and m.group(1).strip():
        lines.append("## Runbook state")
        lines.append(m.group(1).strip()[:1200])
        lines.append("")
    return "\n".join(lines)


def cmd_state(a: argparse.Namespace) -> int:
    print(state_text(Path(a.dir)))
    return 0


def cmd_gates(a: argparse.Namespace) -> int:
    docs = Path(a.dir)
    G = gates(docs)
    if not G:
        print("no gates found in GATES.md (expected lines like '- [ ] G1: claim' with CHECK/EXPECT/EVIDENCE)")
        return 0
    root_rc, top = git(["rev-parse", "--show-toplevel"], docs)
    cwd = Path(top.strip()) if root_rc == 0 else docs.parent
    failed = 0
    text = read(docs / "GATES.md")
    edits: List[Tuple[dict, str]] = []
    for g in G:
        if not a.run:
            print(f"[{'x' if g['done'] else ' '}] {g['id']}: {g['claim']}")
            continue
        if not g["check"]:
            print(f"[skip] {g['id']}: no CHECK line")
            continue
        try:
            p = subprocess.run(g["check"], shell=True, cwd=str(cwd), capture_output=True, text=True,
                               encoding="utf-8", errors="replace", timeout=a.timeout)
            out = (p.stdout or "") + (p.stderr or "")
            rc = p.returncode
        except subprocess.TimeoutExpired:
            out, rc = "timed out", 124
        tail = out.strip().splitlines()[-1] if out.strip() else ""
        ok = rc == 0 and (not g["expect"] or g["expect"] in out)
        print(f"[{'pass' if ok else 'FAIL'}] {g['id']}: {g['claim']}\n       ran: {g['check']}\n       exit {rc}, last line: {tail[:120]}")
        if not ok:
            failed += 1
        if ok and a.record:
            ev = f"EVIDENCE: shell={'powershell' if os.name == 'nt' else 'sh'} cwd={cwd} exit={rc}; run {today()}; stdout ended '{tail[:100]}'"
            edits.append((g, ev))
    if edits:
        for g, ev in sorted(edits, key=lambda e: -e[0]["line_start"]):
            block = text[g["line_start"]:g["block_end"]]
            block2 = re.sub(r"^- \[ \] ", "- [x] ", block, count=1)
            if re.search(r"^\s+EVIDENCE:", block2, re.M):
                block2 = re.sub(r"^(\s+)EVIDENCE:.*$", r"\g<1>" + ev.replace("\\", "\\\\"), block2, count=1, flags=re.M)
            else:
                block2 = block2.rstrip("\n") + "\n  " + ev + "\n"
            text = text[:g["line_start"]] + block2 + text[g["block_end"]:]
        (docs / "GATES.md").write_text(text, encoding="utf-8", newline="\n")
        print(f"\nrecorded evidence for {len(edits)} gate(s)")
    if a.run:
        print(f"\n{len(G) - failed - sum(1 for g in G if not g['check'])} passed, {failed} failed")
    return 1 if failed else 0


def handoff_text(docs: Path) -> str:
    D, P, R, G = decisions(docs), progress(docs), results(docs), gates(docs)
    proj = docs.resolve().parent.name
    open_d = [d for d in D if d["status"].startswith("open")]
    last = P[-3:]
    recent_d = D[-5:]
    lines = [f"# Continuation: {proj}", "",
             f"Working directory: `{docs.resolve().parent}`", "",
             "## First actions", "",
             "1. Read `docs/PLAN.md`, then `docs/DECISIONS.md` entries "
             + (", ".join(f"D-{d['id']:03d}" for d in recent_d) if recent_d else "(none yet)")
             + " in full, then the last three `docs/PROGRESS.md` entries, then `docs/RUNBOOK.md`.",
             "2. Run `python <skill>/scripts/project_ledger.py state` and `verify --git` before touching anything.",
             "3. Load the skills named in `docs/SKILL-ROUTING.md` before the step each governs.", "",
             "## Exact state", "",
             f"- Repository: {git_state(docs)}",
             f"- Ledger: {len(D)} decisions ({len(open_d)} open), {len(P)} progress entries, {len(R)} results, "
             f"{sum(1 for g in G if g['done'])}/{len(G)} gates met",
             f"- Next identifiers: D-{next_id(docs, 'D'):03d}, PROGRESS {next_id(docs, 'P'):04d}, R-{next_id(docs, 'R'):04d}", ""]
    if last:
        lines.append("## What the last session did")
        lines.append("")
        for p in last:
            lines.append(f"- {p['seq']:04d} {p['type']} {p['phase']}: {p['what']} Result: {field_value(p['text'], 'Result')} [{p['status']}]")
        lines.append("")
        lines.append("## Next step, as the last entry recorded it")
        lines.append("")
        lines.append(P[-1]["next"] or "(not recorded; decide from PLAN.md and open a PROGRESS entry first)")
        lines.append("")
    if open_d:
        lines.append("## Open decisions: escalate, do not resolve")
        lines.append("")
        for d in open_d:
            lines.append(f"- D-{d['id']:03d} {d['title']}")
        lines.append("")
    unmet = [g for g in G if not g["done"]]
    if unmet:
        lines.append("## Gates not yet met")
        lines.append("")
        for g in unmet[:12]:
            lines.append(f"- {g['id']}: {g['claim']}")
        lines.append("")
    lines += ["## Rules carried forward, unchanged", "",
              "1. `PROGRESS.md` and `RESULTS-LOG.md` are append-only. Corrections are new entries naming the entry they correct.",
              "2. No value without an interval and the method that produced it.",
              "3. `PREREGISTRATION.md` is frozen. Anything designed after the data existed is exploratory and says so.",
              "4. A gate is met when its CHECK has been run and its EVIDENCE line written; a claim is not evidence.",
              "5. Escalate rather than reinterpret: when a rule does not cleanly apply, open a decision with status `open` and stop that thread.",
              "6. Every session ends with a PROGRESS entry of type HANDOFF and, if anything was committed, the commit hash in it.",
              "7. Author names, affiliations, emails, and funding come only from the owner or a project file, never from session context.",
              "", "This brief was generated from the record; the record wins where they disagree. Do not commit this file."]
    return "\n".join(lines)


def cmd_handoff(a: argparse.Namespace) -> int:
    text = handoff_text(Path(a.dir))
    if a.out:
        Path(a.out).write_text(text, encoding="utf-8", newline="\n")
        print(f"wrote {a.out} (keep it out of the repository)")
    else:
        print(text)
    return 0


# ---------------------------------------------------------------------------
# self-test
# ---------------------------------------------------------------------------

def self_test() -> int:
    ok = True

    def check(desc: str, cond: bool) -> None:
        nonlocal ok
        print(("  ok   " if cond else "  FAIL ") + desc)
        ok = ok and cond

    with tempfile.TemporaryDirectory() as td:
        docs = Path(td) / "docs"
        docs.mkdir()
        (docs / "DECISIONS.md").write_text("# DECISIONS\n\n## D-001. First\n\n- **Date:** 2026-01-01\n- **Status:** closed\n- **Decision:** x\n\n---\n", encoding="utf-8")
        (docs / "PROGRESS.md").write_text("# PROGRESS\n\n### 0001 | 2026-01-01T00:00:00Z | SETUP | human | P0\n- What: init\n- Result: n/a\n- Artifacts: none\n- Refs: D-001\n- Status: done\n- Next: run\n", encoding="utf-8")
        (docs / "RESULTS-LOG.md").write_text("# RESULTS\n", encoding="utf-8")
        (docs / "GATES.md").write_text("# Gates\n\n- [ ] G1: python prints ok\n  CHECK: python -c \"print('GATE OK')\"\n  EXPECT: GATE OK\n\n- [ ] G2: fails\n  CHECK: python -c \"import sys; sys.exit(3)\"\n  EXPECT: never\n", encoding="utf-8")
        check("next ids", next_id(docs, "D") == 2 and next_id(docs, "P") == 2 and next_id(docs, "R") == 1)
        ns = argparse.Namespace(dir=str(docs), what_kind="result", run_id="RUN-1", metric="AUROC", value="0.81",
                                interval="", method="", phase="P1", n="", comparison="", notes="", supersedes="")
        check("result without interval refused", cmd_append(ns) == 2)
        ns.interval, ns.method = "[0.78, 0.84]", "bootstrap(B=2000)"
        check("result with interval appended", cmd_append(ns) == 0 and results(docs)[0]["id"] == 1)
        ns2 = argparse.Namespace(dir=str(docs), what_kind="progress", type="CORRECTION", role="R6", phase="P1",
                                 what="fix", result="", artifacts="", refs="", status="done", next="")
        check("correction without refs refused", cmd_append(ns2) == 2)
        ns2.refs = "0001"
        check("correction appended", cmd_append(ns2) == 0 and progress(docs)[-1]["seq"] == 2)
        (docs / "PROGRESS.md").write_text(read(docs / "PROGRESS.md") + "\n### 0004 | 2026-01-02T00:00:00Z | RUN | R4 | P1\n- What: gap\n- Result: n/a\n- Artifacts: none\n- Refs: D-009\n- Status: done\n- Next: x\n", encoding="utf-8")
        fails, warns = verify(docs, use_git=False)
        check("verify finds the gap and the dangling reference", any("gaps" in f for f in fails) and any("D-009" in f for f in fails))
        G = gates(docs)
        check("gates parsed with CHECK/EXPECT", len(G) == 2 and G[0]["expect"] == "GATE OK")
        ns3 = argparse.Namespace(dir=str(docs), run=True, record=True, timeout=60)
        rc = cmd_gates(ns3)
        G2 = gates(docs)
        check("gate run: G1 recorded, G2 failed", rc == 1 and G2[0]["done"] and "EVIDENCE" in read(docs / "GATES.md") and not G2[1]["done"])
        h = handoff_text(docs)
        check("handoff names next ids and rules", "D-002" in h and "append-only" in h and "Do not commit" in h)
        # append-only against git
        if shutil.which("git"):
            root = Path(td)
            git(["init", "-q"], root)
            git(["config", "user.email", "t@t"], root)
            git(["config", "user.name", "t"], root)
            git(["add", "."], root)
            git(["commit", "-q", "-m", "init"], root)
            txt = read(docs / "PROGRESS.md").replace("- What: init", "- What: init EDITED")
            (docs / "PROGRESS.md").write_text(txt, encoding="utf-8")
            fails, _ = verify(docs, use_git=True)
            check("append-only: in-place edit of a committed PROGRESS entry is a FAIL", any("edited in place" in f for f in fails))
            dtxt = read(docs / "DECISIONS.md").replace("- **Status:** closed", "- **Status:** superseded by D-002")
            (docs / "DECISIONS.md").write_text(dtxt + "\n## D-002. Second\n\n- **Date:** 2026-01-02\n- **Status:** open\n- **Decision:** y\n\n---\n", encoding="utf-8")
            fails, _ = verify(docs, use_git=True)
            check("append-only: a DECISIONS status change is allowed", not any("DECISIONS" in f for f in fails))
        else:
            print("  skip git checks (git not on PATH)")
    print("\nself-test " + ("passed" if ok else "FAILED"))
    return 0 if ok else 1


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, OSError):
            pass
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--dir", default="docs", help="ledger directory (default: docs)")
    p.add_argument("--self-test", action="store_true")
    sub = p.add_subparsers(dest="cmd")

    s = sub.add_parser("init", help="scaffold the documents from templates")
    s.add_argument("--name", default=Path.cwd().name)
    s.set_defaults(func=cmd_init)

    s = sub.add_parser("next", help="print the next free id")
    s.add_argument("kind", choices=["D", "P", "R", "d", "p", "r"])
    s.set_defaults(func=cmd_next)

    s = sub.add_parser("append", help="append a validated entry")
    s.add_argument("what_kind", choices=["decision", "progress", "result"])
    s.add_argument("--title"); s.add_argument("--decision"); s.add_argument("--alternatives")
    s.add_argument("--rationale"); s.add_argument("--consequences"); s.add_argument("--revisit")
    s.add_argument("--status", default="open")
    s.add_argument("--type", default="SETUP"); s.add_argument("--role", default="agent"); s.add_argument("--phase", default="meta")
    s.add_argument("--what"); s.add_argument("--result"); s.add_argument("--artifacts"); s.add_argument("--refs"); s.add_argument("--next")
    s.add_argument("--run-id", dest="run_id"); s.add_argument("--metric"); s.add_argument("--value"); s.add_argument("--interval")
    s.add_argument("--method"); s.add_argument("--n"); s.add_argument("--comparison"); s.add_argument("--notes"); s.add_argument("--supersedes")
    s.set_defaults(func=cmd_append)

    s = sub.add_parser("verify", help="check the ledger's integrity")
    s.add_argument("--git", action="store_true", help="also check append-only against git HEAD")
    s.set_defaults(func=cmd_verify)

    s = sub.add_parser("state", help="one-screen state summary")
    s.set_defaults(func=cmd_state)

    s = sub.add_parser("gates", help="list or run the gate ledger")
    s.add_argument("--run", action="store_true"); s.add_argument("--record", action="store_true")
    s.add_argument("--timeout", type=int, default=1800)
    s.set_defaults(func=cmd_gates)

    s = sub.add_parser("handoff", help="print the continuation brief for the next session")
    s.add_argument("--out", help="write to this path instead of stdout (outside the repository)")
    s.set_defaults(func=cmd_handoff)

    a = p.parse_args()
    if a.self_test:
        return self_test()
    if not a.cmd:
        p.print_help()
        return 2
    if a.cmd == "append":
        # progress defaults
        if not hasattr(a, "status") or a.status == "open" and a.what_kind == "progress":
            a.status = "done"
    return a.func(a)


if __name__ == "__main__":
    raise SystemExit(main())
