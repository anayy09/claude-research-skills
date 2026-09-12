#!/usr/bin/env python3
"""
related_work_table.py - Render the comparative summary table that closes a
related-work section, from the verified source log, so every row is a real
source and every cell is either extracted or marked for the author.

Each source in the log may carry a `summary` object:

    "summary": {
      "objective": "what the study set out to do",
      "method": "the approach, model, or design",
      "data": "dataset, cohort, or evaluation setting",
      "findings": "the result that matters for this paper",
      "limitations": "what it did not do, or where it breaks"
    }

Rows are emitted only for sources whose `verified` is `confirmed` (others are
listed after the table with the reason). A missing cell is written as
`[AUTHOR INPUT: <field> for <key>]`, never filled from memory. Preprints are
marked in the status column; a preprint with `superseded_by` is reported as
"cite the version of record" and its row uses the superseding DOI.

Usage:
    python related_work_table.py sources.json                       # markdown
    python related_work_table.py sources.json --format tex          # LaTeX tabularx with \\cite{key}
    python related_work_table.py sources.json --only-cited draft.md # rows for keys cited in the draft
    python related_work_table.py sources.json --columns objective,data,findings
    python related_work_table.py sources.json --this-work "This paper|our method|our data|..." # last row
    python related_work_table.py --self-test

Standard library only.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional

DEFAULT_COLUMNS = ["objective", "method", "data", "findings", "limitations"]
LABELS = {"objective": "Objective", "method": "Method", "data": "Data / setting", "findings": "Key findings",
          "limitations": "Limitations", "year": "Year", "status": "Status"}


def cited_keys(paths: List[Path]) -> set:
    keys: set = set()
    for p in paths:
        text = p.read_text(encoding="utf-8", errors="replace")
        for m in re.finditer(r"\\(?:cite|citep|citet|parencite|textcite|autocite)\*?(?:\[[^\]]*\]){0,2}\{([^}]+)\}", text):
            keys |= {k.strip() for k in m.group(1).split(",")}
        for m in re.finditer(r"\[(@?[A-Za-z][A-Za-z0-9_:.+-]*(?:\s*[,;]\s*@?[A-Za-z][A-Za-z0-9_:.+-]*)*)\]", text):
            keys |= {k.strip().lstrip("@") for k in re.split(r"[,;]", m.group(1))}
    return keys


def cell(source: dict, field: str) -> str:
    v = ((source.get("summary") or {}).get(field) or "").strip()
    return v if v else f"[AUTHOR INPUT: {field} for {source.get('key')}]"


def status(source: dict) -> str:
    if source.get("superseded_by"):
        return f"preprint; cite version of record {source['superseded_by']}"
    pr = source.get("peer_reviewed") or ""
    if pr == "preprint":
        return "preprint (unreviewed)"
    if pr == "peer-reviewed":
        return "peer reviewed"
    return pr or "status unknown"


def first_author(source: dict) -> str:
    a = source.get("authors") or []
    if not a:
        return source.get("key", "")
    surname = a[0].split(",")[0].strip()
    return surname + (" et al." if len(a) > 2 else (" and " + a[1].split(",")[0].strip() if len(a) == 2 else ""))


def esc_tex(s: str) -> str:
    return re.sub(r"([&%$#_{}])", r"\\\1", s).replace("~", "\\textasciitilde{}")


def render(sources: List[dict], columns: List[str], fmt: str, this_work: Optional[List[str]], only: Optional[set]) -> str:
    rows = [s for s in sources if s.get("verified") == "confirmed" and (only is None or s.get("key") in only)]
    skipped = [s for s in sources if s.get("verified") != "confirmed" and (only is None or s.get("key") in only)]
    rows.sort(key=lambda s: (s.get("year") or 0, s.get("key") or ""))
    missing = 0
    heads = ["Study"] + [LABELS[c] for c in columns] + ["Status"]
    lines: List[str] = []
    if fmt == "md":
        lines.append("| " + " | ".join(heads) + " |")
        lines.append("|" + "---|" * len(heads))
        for s in rows:
            cells = [f"{first_author(s)} ({s.get('year', '')}) [{s['key']}]"]
            for c in columns:
                v = cell(s, c)
                missing += v.startswith("[AUTHOR INPUT")
                cells.append(v.replace("|", "\\|"))
            cells.append(status(s))
            lines.append("| " + " | ".join(cells) + " |")
        if this_work:
            lines.append("| " + " | ".join(["**This work**"] + this_work[:len(columns)] + [""] * (len(columns) - len(this_work)) + ["this paper"]) + " |")
    else:
        spec = "l" + "X" * len(columns) + "l"
        lines.append("\\begin{table*}[!t]\n\\caption{Summary of the closest related work.}\n\\label{tab:related-work}\n\\small")
        lines.append(f"\\begin{{tabularx}}{{\\textwidth}}{{{spec}}}\n\\toprule")
        lines.append(" & ".join(heads) + " \\\\\n\\midrule")
        for s in rows:
            cells = [f"{esc_tex(first_author(s))} \\cite{{{s['key']}}}"]
            for c in columns:
                v = cell(s, c)
                missing += v.startswith("[AUTHOR INPUT")
                cells.append(esc_tex(v))
            cells.append(esc_tex(status(s)))
            lines.append(" & ".join(cells) + " \\\\")
        if this_work:
            lines.append(" & ".join(["\\textbf{This work}"] + [esc_tex(x) for x in this_work[:len(columns)]] + [""] * (len(columns) - len(this_work)) + ["this paper"]) + " \\\\")
        lines.append("\\bottomrule\n\\end{tabularx}\n\\end{table*}")
    out = "\n".join(lines)
    notes = []
    if missing:
        notes.append(f"{missing} cell(s) are marked [AUTHOR INPUT]; fill them from the source, never from memory.")
    if skipped:
        notes.append("Not included (not confirmed in the source log): " + ", ".join(f"{s.get('key')} ({s.get('verified', 'pending')})" for s in skipped))
    upgr = [s for s in rows if s.get("superseded_by")]
    if upgr:
        notes.append("Cite the version of record for: " + ", ".join(f"{s['key']} -> {s['superseded_by']}" for s in upgr))
    if notes:
        out += "\n\n" + ("% " if fmt == "tex" else "") + ("\n% " if fmt == "tex" else "\n").join(notes)
    return out


def self_test() -> int:
    ok = True

    def check(desc: str, cond: bool) -> None:
        nonlocal ok
        print(("  ok   " if cond else "  FAIL ") + desc)
        ok = ok and cond

    log = {"sources": [
        {"key": "a2020", "authors": ["Alpha, A.", "Beta, B.", "Gamma, G."], "year": 2020, "verified": "confirmed", "peer_reviewed": "peer-reviewed",
         "summary": {"objective": "o", "method": "m", "data": "d", "findings": "f", "limitations": "l"}},
        {"key": "b2023", "authors": ["Beta, B."], "year": 2023, "verified": "confirmed", "peer_reviewed": "preprint", "superseded_by": "10.1/vor",
         "summary": {"objective": "o2"}},
        {"key": "c2019", "year": 2019, "verified": "pending"},
    ]}
    md = render(log["sources"], DEFAULT_COLUMNS, "md", ["ours", "x", "y", "z", "w"], None)
    check("confirmed rows only, unconfirmed listed", "a2020" in md and "b2023" in md and "| c2019" not in md and "c2019 (pending)" in md)
    check("missing cells marked", "[AUTHOR INPUT: method for b2023]" in md)
    check("et al. for three authors", "Alpha et al. (2020)" in md)
    check("version of record note", "b2023 -> 10.1/vor" in md)
    check("this-work row", "**This work**" in md)
    tex = render(log["sources"], ["objective", "findings"], "tex", None, {"a2020"})
    check("tex: only cited key, cite command, escaped", "\\cite{a2020}" in tex and "b2023" not in tex.split("\\bottomrule")[0] and "tabularx" in tex)
    print("\nself-test " + ("passed" if ok else "FAILED"))
    return 0 if ok else 1


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, OSError):
            pass
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("source_log", nargs="?")
    p.add_argument("--format", choices=["md", "tex"], default="md")
    p.add_argument("--columns", default=",".join(DEFAULT_COLUMNS))
    p.add_argument("--only-cited", nargs="*", help="manuscript files; include only keys cited in them")
    p.add_argument("--this-work", help="pipe-separated cells for a final 'This work' row")
    p.add_argument("--out", help="write here instead of stdout")
    p.add_argument("--self-test", action="store_true")
    a = p.parse_args()
    if a.self_test:
        return self_test()
    if not a.source_log:
        p.error("give the source log (or --self-test)")
    log = json.loads(Path(a.source_log).read_text(encoding="utf-8"))
    columns = [c.strip() for c in a.columns.split(",") if c.strip() in LABELS and c.strip() not in ("year", "status")]
    only = cited_keys([Path(f) for f in a.only_cited]) if a.only_cited else None
    this_work = [x.strip() for x in a.this_work.split("|")] if a.this_work else None
    out = render(log.get("sources", []), columns, a.format, this_work, only)
    if a.out:
        Path(a.out).write_text(out, encoding="utf-8", newline="\n")
        print(f"wrote {a.out}")
    else:
        print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
