#!/usr/bin/env python3
"""
make_checklist.py - Turn reviewer, editor, and internal-review text into the
consolidated revision checklist: one row per atomic comment, with a stable id,
the comment reproduced, and the columns the revision has to fill before any
edit is made.

Sources it reads:

  reviewer files     plain text or markdown, one file per reviewer or editor;
                     split into comments at numbered lines ("1.", "1)",
                     "(1)", "Comment 3", "R2.4") or, failing that, at blank
                     lines
  --from-review      a submission-reviewer report; its "Fix list" table rows
                     (id, severity, location, problem, fix, evidence, effort)
                     become items with the reviewer's id preserved
  --from-checklist   an existing checklist to carry ids and statuses forward
                     into a new round

Output is a Markdown table (and --json) with the columns:

  ID | Source and comment number | Requested change | Affected section, figure,
  table, experiment, or supplement | Proposed action (change type) | Required
  evidence, citation, analysis, or experiment | Dependencies or open questions
  | Projected time | Status

Cells the script cannot know are left as "(fill)". The checklist is the
artifact the user approves before the revision starts; nothing in it is a
change to the manuscript.

Usage:
    python make_checklist.py reviews/Reviewer1.txt reviews/Reviewer2.txt reviews/Editor.txt --out docs/REVIEWER_CHECKLIST.md
    python make_checklist.py reviews/*.txt --from-review reviews/external-review-02.md --out docs/REVISION-P12.md
    python make_checklist.py --self-test

Standard library only.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional

NUMBERED = re.compile(r"^\s*(?:\(?(\d{1,3})[.)]\s+|Comment\s+(\d{1,3})[:.]?\s+|([RE]\d?\.\d{1,3})[:.]?\s+|([A-Z]-?\d{1,3})[.):]\s+)", re.I)
CHANGE_TYPES = ["response only", "edit in place", "insert", "new paragraph or subsection", "supplementary",
                "new analysis or experiment", "declined", "needs author input"]
COLUMNS = ["ID", "Source and comment no.", "Requested change", "Affected section / figure / table / experiment / supplement",
           "Proposed action (change type)", "Required evidence, citation, analysis, or experiment",
           "Dependencies / open questions", "Projected time", "Status"]


def source_prefix(path: Path, index: int) -> str:
    n = path.stem.lower()
    if "editor" in n or n.startswith("e"):
        return "E"
    m = re.search(r"(\d+)", n)
    if m:
        return f"R{int(m.group(1))}"
    return f"R{index}"


def split_comments(text: str) -> List[str]:
    lines = text.splitlines()
    items: List[str] = []
    cur: List[str] = []
    numbered_hits = sum(1 for ln in lines if NUMBERED.match(ln))
    if numbered_hits >= 2:
        for ln in lines:
            if NUMBERED.match(ln):
                if cur and "".join(cur).strip():
                    items.append("\n".join(cur).strip())
                cur = [NUMBERED.sub("", ln, count=1)]
            elif cur:
                cur.append(ln)
            elif ln.strip():
                # preamble before the first numbered item: keep only if substantive
                if len(ln.strip()) > 120:
                    items.append(ln.strip())
        if cur and "".join(cur).strip():
            items.append("\n".join(cur).strip())
    else:
        for para in re.split(r"\n\s*\n", text):
            p = para.strip()
            if len(p) >= 40 and not re.match(r"^(dear|sincerely|regards|thank you for)", p, re.I):
                items.append(p)
    return items


def parse_review_report(text: str) -> List[dict]:
    """Rows of a submission-reviewer 'Fix list' table."""
    rows: List[dict] = []
    m = re.search(r"##\s*Fix list.*?\n(.*?)(?=\n##\s|\Z)", text, re.S | re.I)
    if not m:
        return rows
    for ln in m.group(1).splitlines():
        if not ln.strip().startswith("|") or re.match(r"^\s*\|\s*-{2,}", ln):
            continue
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        if len(cells) < 4 or cells[0].lower() in ("id", "#"):
            continue
        rows.append({"id": cells[0], "severity": cells[1] if len(cells) > 1 else "",
                     "location": cells[2] if len(cells) > 2 else "", "problem": cells[3] if len(cells) > 3 else "",
                     "fix": cells[4] if len(cells) > 4 else "", "evidence": cells[5] if len(cells) > 5 else "",
                     "effort": cells[6] if len(cells) > 6 else ""})
    return rows


def parse_existing(text: str) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    for ln in text.splitlines():
        if not ln.strip().startswith("|"):
            continue
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        if len(cells) >= 9 and re.match(r"^[RE]\d*\.\d+$|^F\d+$", cells[0]):
            out[cells[0]] = {"status": cells[8], "action": cells[4], "time": cells[7]}
    return out


def build_items(files: List[Path], review: Optional[Path], existing: Optional[Path]) -> List[dict]:
    items: List[dict] = []
    prev = parse_existing(existing.read_text(encoding="utf-8", errors="replace")) if existing else {}
    for i, f in enumerate(files, 1):
        prefix = source_prefix(f, i)
        for j, c in enumerate(split_comments(f.read_text(encoding="utf-8", errors="replace")), 1):
            iid = f"{prefix}.{j}"
            items.append({"id": iid, "source": f"{f.name}, comment {j}", "request": c,
                          "affected": "(fill)", "action": prev.get(iid, {}).get("action", "(fill)"),
                          "evidence": "(fill)", "dependencies": "(fill)",
                          "time": prev.get(iid, {}).get("time", "(fill)"),
                          "status": prev.get(iid, {}).get("status", "open")})
    if review:
        for r in parse_review_report(review.read_text(encoding="utf-8", errors="replace")):
            iid = r["id"] if re.match(r"^F\d+$", r["id"]) else f"F{len([x for x in items if x['id'].startswith('F')]) + 1}"
            items.append({"id": iid, "source": f"{review.name}, {r['severity'] or 'fix'} {r['id']}",
                          "request": r["problem"] + (f" Fix: {r['fix']}" if r["fix"] else ""),
                          "affected": r["location"] or "(fill)",
                          "action": prev.get(iid, {}).get("action", "(fill)"),
                          "evidence": r["evidence"] or "(fill)", "dependencies": "(fill)",
                          "time": r["effort"] or prev.get(iid, {}).get("time", "(fill)"),
                          "status": prev.get(iid, {}).get("status", "open")})
    return items


def render(items: List[dict], title: str) -> str:
    lines = [f"# {title}", "",
             "One row per atomic comment. Approve this before any edit is made. Change types: " + "; ".join(CHANGE_TYPES) + ".",
             "Projected time is from comparable items in earlier rounds, not a guess; write the basis in the cell.", "",
             "| " + " | ".join(COLUMNS) + " |", "|" + "---|" * len(COLUMNS)]
    for it in items:
        req = re.sub(r"\s+", " ", it["request"]).replace("|", "\\|")
        if len(req) > 400:
            req = req[:397] + "..."
        lines.append(f"| {it['id']} | {it['source']} | {req} | {it['affected']} | {it['action']} | {it['evidence']} | {it['dependencies']} | {it['time']} | {it['status']} |")
    lines += ["", f"{len(items)} items. Open: {sum(1 for i in items if i['status'] == 'open')}.", "",
              "## Decisions this checklist needs from the author", "", "- (fill: each item whose action is 'needs author input' or 'declined', with the question and the options)", ""]
    return "\n".join(lines)


def self_test() -> int:
    ok = True

    def check(desc: str, cond: bool) -> None:
        nonlocal ok
        print(("  ok   " if cond else "  FAIL ") + desc)
        ok = ok and cond

    r1 = "Dear editor,\n\n1. The methods are unclear about imputation.\n2) The baseline is weak. Please compare\nagainst method X.\n(3) Figure 2 is unreadable.\n"
    items = split_comments(r1)
    check("numbered comments split (3)", len(items) == 3 and items[1].startswith("The baseline is weak") and "method X" in items[1])
    r2 = "Thank you for the submission.\n\nThe cohort description in section 3 omits the exclusion criteria, which matters for the leakage argument.\n\nThe limitations section is too long and repeats the methods.\n"
    check("paragraph fallback (2)", len(split_comments(r2)) == 2)
    rep = "## Snapshot\nx\n## Fix list\n\n| id | severity | location | problem | fix | evidence | effort |\n|---|---|---|---|---|---|---|\n| F1 | blocking | Table 2 | one untuned baseline | tune it | sweep results | a week |\n| F2 | minor | Sec 4 | typo | fix | | 5 min |\n\n## Outlook\n"
    rows = parse_review_report(rep)
    check("fix list parsed (2 rows)", len(rows) == 2 and rows[0]["severity"] == "blocking")
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        f1 = Path(td) / "Reviewer1.txt"; f1.write_text(r1, encoding="utf-8")
        fe = Path(td) / "Editor.txt"; fe.write_text(r2, encoding="utf-8")
        fr = Path(td) / "review.md"; fr.write_text(rep, encoding="utf-8")
        its = build_items([f1, fe], fr, None)
        ids = [i["id"] for i in its]
        check("ids: R1.1..R1.3, E.1, E.2, F1, F2", ids == ["R1.1", "R1.2", "R1.3", "E.1", "E.2", "F1", "F2"])
        md = render(its, "Checklist")
        old = Path(td) / "old.md"; old.write_text(md.replace("| R1.2 | Reviewer1.txt, comment 2 |", "| R1.2 | Reviewer1.txt, comment 2 |").replace("| (fill) | (fill) | (fill) | (fill) | open |", "| edit in place | (fill) | (fill) | 2 h | done |", 1), encoding="utf-8")
        its2 = build_items([f1, fe], fr, old)
        check("existing statuses carried forward", its2[0]["status"] == "done" and its2[0]["action"] == "edit in place")
        check("render has the nine columns", md.count("|---") == len(COLUMNS))
    print("\nself-test " + ("passed" if ok else "FAILED"))
    return 0 if ok else 1


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, OSError):
            pass
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("reviews", nargs="*", help="reviewer and editor files")
    p.add_argument("--from-review", help="a submission-reviewer report with a Fix list table")
    p.add_argument("--from-checklist", help="an earlier checklist whose ids, actions, and statuses carry forward")
    p.add_argument("--title", default="Revision checklist")
    p.add_argument("--out", help="write the Markdown here")
    p.add_argument("--json", dest="json_path")
    p.add_argument("--self-test", action="store_true")
    a = p.parse_args()
    if a.self_test:
        return self_test()
    if not a.reviews and not a.from_review:
        p.error("give reviewer files and/or --from-review")
    files = [Path(f) for f in a.reviews]
    for f in files:
        if not f.exists():
            print(f"error: {f} not found", file=sys.stderr)
            return 2
    items = build_items(files, Path(a.from_review) if a.from_review else None, Path(a.from_checklist) if a.from_checklist else None)
    md = render(items, a.title)
    if a.out:
        Path(a.out).write_text(md, encoding="utf-8", newline="\n")
        print(f"wrote {a.out} ({len(items)} items)")
    else:
        print(md)
    if a.json_path:
        Path(a.json_path).write_text(json.dumps(items, indent=2, ensure_ascii=False), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
