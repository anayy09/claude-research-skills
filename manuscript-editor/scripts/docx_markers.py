#!/usr/bin/env python3
"""
docx_markers.py - Work a Word manuscript the way the revision workflow needs:
list, add, and clear the red author-action markers, and extract the text for
the audit, without touching styles.

A .docx revision cannot be marked up with real tracked changes from Python
(python-docx has no API for revisions; Word's Compare produces the marked
copy from the clean revised file and the submitted file). What can be done
mechanically, and what this script does:

  list      every [AUTHOR ACTION: ...], [AUTHOR INPUT: ...], TODO, TBD with
            its paragraph index and surrounding text
  add       insert a red, highlighted [AUTHOR ACTION: ...] run after the
            paragraph containing --after "text", so the author sees it
  clear     remove a marker by its exact text once the author has acted
  extract   plain text (paragraphs and table cells) for audit_manuscript.py
            and prose_lint.py, which read .docx directly but not tables

Usage:
    python docx_markers.py list working/round-2/Manuscript_round2.docx
    python docx_markers.py add working/round-2/Manuscript_round2.docx --after "Table 4 summarises" \\
        --text "AUTHOR ACTION: supply the RMSE column for the baseline sweep"
    python docx_markers.py clear working/round-2/Manuscript_round2.docx --text "AUTHOR ACTION: supply the RMSE column for the baseline sweep"
    python docx_markers.py extract working/round-2/Manuscript_round2.docx --out working/round-2/manuscript.txt
    python docx_markers.py --self-test

Requires python-docx (pip install python-docx) for everything but --help.
"""
from __future__ import annotations

import argparse
import re
import sys
import tempfile
from pathlib import Path
from typing import List

MARKER_RE = re.compile(r"\[AUTHOR (?:ACTION|INPUT)[^\]]*\]|\bTODO\b|\bTBD\b", re.I)


def load_docx():
    try:
        import docx  # type: ignore
        from docx.shared import RGBColor  # type: ignore
        from docx.enum.text import WD_COLOR_INDEX  # type: ignore
        return docx, RGBColor, WD_COLOR_INDEX
    except ImportError:
        print("error: python-docx is not installed (pip install python-docx)", file=sys.stderr)
        sys.exit(2)


def iter_paragraphs(doc):
    for i, p in enumerate(doc.paragraphs):
        yield ("body", i, p)
    for ti, t in enumerate(doc.tables):
        for ri, row in enumerate(t.rows):
            for ci, cell in enumerate(row.cells):
                for pi, p in enumerate(cell.paragraphs):
                    yield (f"table {ti + 1} r{ri + 1}c{ci + 1}", pi, p)


def cmd_list(path: Path) -> int:
    docx, _, _ = load_docx()
    doc = docx.Document(str(path))
    n = 0
    for where, i, p in iter_paragraphs(doc):
        for m in MARKER_RE.finditer(p.text):
            n += 1
            ctx = " ".join(p.text[max(0, m.start() - 50):m.end() + 50].split())
            print(f"{where} #{i}: {m.group(0)}\n    ...{ctx}...")
    print(f"\n{n} marker(s)")
    return 1 if n else 0


def cmd_add(path: Path, after: str, text: str) -> int:
    docx, RGBColor, WD_COLOR_INDEX = load_docx()
    doc = docx.Document(str(path))
    target = None
    for where, i, p in iter_paragraphs(doc):
        if after.lower() in p.text.lower():
            target = p
            break
    if target is None:
        print(f"error: no paragraph contains \"{after}\"", file=sys.stderr)
        return 1
    marker = text if text.startswith("[") else f"[{text}]"
    run = target.add_run(" " + marker)
    run.font.color.rgb = RGBColor(0xC0, 0x00, 0x00)
    run.font.bold = True
    run.font.highlight_color = WD_COLOR_INDEX.YELLOW
    doc.save(str(path))
    print(f"added {marker} after \"{after[:40]}\"")
    return 0


def cmd_clear(path: Path, text: str) -> int:
    docx, _, _ = load_docx()
    doc = docx.Document(str(path))
    marker = text if text.startswith("[") else f"[{text}]"
    n = 0
    for where, i, p in iter_paragraphs(doc):
        for r in p.runs:
            if marker in r.text:
                r.text = r.text.replace(" " + marker, "").replace(marker, "")
                n += 1
    doc.save(str(path))
    print(f"cleared {n} run(s) carrying {marker}")
    return 0 if n else 1


def cmd_extract(path: Path, out: Path) -> int:
    docx, _, _ = load_docx()
    doc = docx.Document(str(path))
    lines: List[str] = []
    for p in doc.paragraphs:
        style = (p.style.name or "").lower() if p.style is not None else ""
        if style.startswith("heading"):
            level = re.search(r"(\d)", style)
            lines.append("#" * (int(level.group(1)) if level else 1) + " " + p.text.strip())
        else:
            lines.append(p.text)
        lines.append("")
    for ti, t in enumerate(doc.tables, 1):
        lines.append(f"[Table {ti}]")
        for row in t.rows:
            lines.append("| " + " | ".join(c.text.strip().replace("\n", " ") for c in row.cells) + " |")
        lines.append("")
    out.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    print(f"wrote {out} ({len(doc.paragraphs)} paragraphs, {len(doc.tables)} tables)")
    return 0


def self_test() -> int:
    try:
        import docx  # type: ignore
    except ImportError:
        print("  skip python-docx not installed; nothing to test")
        return 0
    ok = True

    def check(desc: str, cond: bool) -> None:
        nonlocal ok
        print(("  ok   " if cond else "  FAIL ") + desc)
        ok = ok and cond

    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "t.docx"
        d = docx.Document()
        d.add_heading("Methods", level=1)
        d.add_paragraph("Table 4 summarises the sweep. TODO check.")
        t = d.add_table(rows=1, cols=2)
        t.rows[0].cells[0].text = "a"
        t.rows[0].cells[1].text = "TBD"
        d.save(str(p))
        check("list finds body and table markers", cmd_list(p) == 1)
        check("add marker", cmd_add(p, "Table 4 summarises", "AUTHOR ACTION: supply the RMSE column") == 0)
        d2 = docx.Document(str(p))
        check("marker present and red", any("[AUTHOR ACTION: supply the RMSE column]" in r.text and r.font.bold for para in d2.paragraphs for r in para.runs))
        check("clear marker", cmd_clear(p, "AUTHOR ACTION: supply the RMSE column") == 0)
        out = Path(td) / "t.txt"
        cmd_extract(p, out)
        txt = out.read_text(encoding="utf-8")
        check("extract has heading and table", txt.startswith("# Methods") and "| a | TBD |" in txt)
    print("\nself-test " + ("passed" if ok else "FAILED"))
    return 0 if ok else 1


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, OSError):
            pass
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("command", nargs="?", choices=["list", "add", "clear", "extract"])
    p.add_argument("docx", nargs="?")
    p.add_argument("--after", help="add: text of the paragraph to mark")
    p.add_argument("--text", help="add/clear: marker text")
    p.add_argument("--out", help="extract: output text file")
    p.add_argument("--self-test", action="store_true")
    a = p.parse_args()
    if a.self_test:
        return self_test()
    if not a.command or not a.docx:
        p.error("give a command and a .docx (or --self-test)")
    path = Path(a.docx)
    if not path.exists():
        print(f"error: {path} not found", file=sys.stderr)
        return 2
    if a.command == "list":
        return cmd_list(path)
    if a.command == "add":
        if not a.after or not a.text:
            p.error("add needs --after and --text")
        return cmd_add(path, a.after, a.text)
    if a.command == "clear":
        if not a.text:
            p.error("clear needs --text")
        return cmd_clear(path, a.text)
    return cmd_extract(path, Path(a.out) if a.out else path.with_suffix(".txt"))


if __name__ == "__main__":
    raise SystemExit(main())
