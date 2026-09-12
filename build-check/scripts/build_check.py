#!/usr/bin/env python3
"""
build_check.py - Build a LaTeX submission package and report what a human
would see on the page, not just what the log says.

"Compiles clean" is not a deliverable. A build can exit 0 with a table running
past the margin, a figure sitting in the middle of the references, a page
count over the venue's cap, and a response letter PDF older than the markdown
it was built from. This script exists so that none of those can be reported
as done without being looked at.

For every target it:

  1. builds (latexmk, or engine passes) unless --no-build, and keeps the log
  2. triages the log: errors, undefined references and citations, multiply
     defined labels, overfull boxes above a threshold, floats that did not
     fit, missing files, "labels may have changed"
  3. counts pages against --max-pages and body words against --max-words
  4. measures every text line, image, and drawing against the text block
     edges the document itself establishes, and against the page edge, so
     a table or figure that runs out of bounds is reported by page with the
     overhang in points and the offending text
  5. maps every float (figure, table, algorithm) to the page it landed on,
     flags floats placed in the references, and flags floats placed outside
     the section that first cites them
  6. checks that every font is embedded (a journal technical check will
     bounce a PDF with unembedded fonts)
  7. compares derived artifacts against their sources by modification time,
     so a response letter or marked-up copy cannot be older than its source
  8. renders every page to a thumbnail and lists them in the report, so the
     next step is looking, not trusting

Output is BUILD_REPORT.md (plus --json), with one PASS / WARN / FAIL line per
check. --strict exits non-zero on any FAIL, so it works as a gate.

Usage:
    python build_check.py submission/cep/main.tex
    python build_check.py submission/*/main.tex --max-pages 16 --strict
    python build_check.py paper/main.pdf --no-build --max-words 4500
    python build_check.py main.tex --derived letter/response.pdf:letter/response.md
    python build_check.py --self-test

Dependencies: Python 3.9+, standard library. Uses whichever of these exist on
PATH: latexmk or pdflatex/xelatex/lualatex (build), pdftotext (text and
bounding boxes), pdftoppm (thumbnails), pdffonts (font embedding), pdfinfo
(page count). PyMuPDF, if importable, adds image and drawing bounds and is
used for thumbnails and page counts when the poppler tools are absent. Every
check that cannot run says so in the report; nothing is silently skipped.

Exit codes:
    0  no FAIL (WARNs may be present)
    1  at least one FAIL, or --strict and any FAIL
    2  usage error, or a target that could not be found or built
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import statistics
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple

PASS, WARN, FAIL, SKIP = "PASS", "WARN", "FAIL", "SKIP"

FLOAT_ENVS = ("figure", "figure*", "table", "table*", "algorithm", "algorithm*",
              "sidewaystable", "sidewaysfigure", "listing", "longtable")
REF_CMDS = r"\\(?:ref|Ref|cref|Cref|autoref|vref|pageref|ref\*|cref\*)\{([^}]+)\}"
HEADING_CMDS = r"\\(section|subsection|chapter)\*?\s*(?:\[[^\]]*\])?\s*\{"
REFS_TITLE = re.compile(r"^\s*(references|bibliography|literature cited|works cited)\s*$", re.I)


_TOOL_CACHE: Dict[str, Optional[str]] = {}


def tool(name: str) -> Optional[str]:
    """Locate a poppler/TeX tool. The first hit on PATH wins unless it is a
    build that lacks the option we need (the xpdf pdftotext shipped with Git
    for Windows predates -bbox-layout); then look next to pdftoppm/pdfinfo,
    which on Windows usually means the MiKTeX or TeX Live bin directory."""
    if name in _TOOL_CACHE:
        return _TOOL_CACHE[name]
    found = shutil.which(name)
    if name == "pdftotext" and found:
        try:
            p = subprocess.run([found, "-h"], capture_output=True, text=True, errors="replace", timeout=20)
            if "bbox" not in (p.stdout + p.stderr):
                found = None
        except Exception:
            found = None
    if not found:
        for sibling in ("pdftoppm", "pdfinfo", "pdflatex", "latexmk"):
            s = shutil.which(sibling)
            if s:
                cand = Path(s).parent / (name + (".exe" if os.name == "nt" else ""))
                if cand.exists():
                    found = str(cand)
                    break
    _TOOL_CACHE[name] = found
    return found


def have(name: str) -> bool:
    return tool(name) is not None


def run(cmd: List[str], cwd: Optional[Path] = None, timeout: int = 900) -> Tuple[int, str]:
    try:
        p = subprocess.run(cmd, cwd=str(cwd) if cwd else None, capture_output=True,
                           text=True, encoding="utf-8", errors="replace", timeout=timeout)
        return p.returncode, (p.stdout or "") + (p.stderr or "")
    except subprocess.TimeoutExpired:
        return 124, f"timed out after {timeout}s: {' '.join(cmd)}"
    except OSError as exc:
        return 127, f"could not run {cmd[0]}: {exc}"


try:  # optional
    import fitz  # type: ignore  # PyMuPDF
except Exception:  # pragma: no cover
    fitz = None


# ---------------------------------------------------------------------------
# result model
# ---------------------------------------------------------------------------

@dataclass
class Check:
    name: str
    status: str
    summary: str
    details: List[str] = field(default_factory=list)


@dataclass
class TargetReport:
    target: str
    pdf: str = ""
    log: str = ""
    pages: int = 0
    checks: List[Check] = field(default_factory=list)
    thumbnails: List[str] = field(default_factory=list)
    page_flags: Dict[int, List[str]] = field(default_factory=dict)

    def add(self, c: Check) -> None:
        self.checks.append(c)

    def flag(self, page: int, msg: str) -> None:
        self.page_flags.setdefault(page, []).append(msg)

    @property
    def verdict(self) -> str:
        statuses = {c.status for c in self.checks}
        if FAIL in statuses:
            return FAIL
        if WARN in statuses:
            return WARN
        return PASS


# ---------------------------------------------------------------------------
# 1. build
# ---------------------------------------------------------------------------

def detect_engine(tex: str) -> str:
    if re.search(r"\\usepackage(\[[^\]]*\])?\{fontspec\}|\\setmainfont|\\usepackage\{polyglossia\}", tex):
        return "xelatex"
    if re.search(r"\\usepackage\{luacode\}|\\directlua", tex):
        return "lualatex"
    return "pdflatex"


def build(main: Path, engine: str) -> Tuple[int, str, Path]:
    """Compile main.tex in its own directory. Returns (rc, output, logpath)."""
    tex = main.read_text(encoding="utf-8", errors="replace")
    if engine == "auto":
        engine = detect_engine(tex)
    cwd = main.parent
    logpath = cwd / (main.stem + ".log")
    if have("latexmk"):
        flag = {"pdflatex": "-pdf", "xelatex": "-xelatex", "lualatex": "-lualatex"}[engine]
        cmd = [tool("latexmk"), flag, "-bibtex", "-interaction=nonstopmode", "-file-line-error", main.name]
        rc, out = run(cmd, cwd)
        return rc, out, logpath
    if not have(engine):
        return 127, f"neither latexmk nor {engine} is on PATH", logpath
    out_all = []
    rc = 0
    has_bib = bool(re.search(r"\\bibliography\{|\\addbibresource\{", tex))
    for i in range(3):
        rc, out = run([tool(engine), "-interaction=nonstopmode", "-file-line-error", main.name], cwd)
        out_all.append(out)
        if i == 0 and has_bib:
            if have("bibtex"):
                out_all.append(run([tool("bibtex"), main.stem], cwd)[1])
            elif have("biber"):
                out_all.append(run([tool("biber"), main.stem], cwd)[1])
    return rc, "\n".join(out_all), logpath


# ---------------------------------------------------------------------------
# 2. log triage
# ---------------------------------------------------------------------------

OVERFULL_RE = re.compile(r"Overfull \\hbox \((\d+(?:\.\d+)?)pt too wide\) (?:in (paragraph|alignment) )?(?:at lines? (\d+)(?:--(\d+))?|detected at line (\d+))?")
OVERFULL_V_RE = re.compile(r"Overfull \\vbox \((\d+(?:\.\d+)?)pt too high\)")


def unwrap_log(log: str) -> str:
    """TeX wraps log lines at 79 characters. Join continuation lines so that
    messages split mid-word can be matched."""
    lines = log.splitlines()
    out: List[str] = []
    for ln in lines:
        if out and len(out[-1]) == 79 and not ln.startswith(("!", "Overfull", "Underfull", "LaTeX", "Package", "(", ")")):
            out[-1] += ln
        else:
            out.append(ln)
    return "\n".join(out)


def triage_log(log: str, overfull_pt: float) -> Dict[str, list]:
    log = unwrap_log(log)
    t: Dict[str, list] = {"errors": [], "undefined_refs": [], "undefined_cites": [],
                          "multiply_defined": [], "overfull": [], "overfull_v": [],
                          "float_problems": [], "missing_files": [], "rerun": [],
                          "font_warnings": []}
    for ln in log.splitlines():
        s = ln.strip()
        if s.startswith("! ") or re.match(r"^.+\.tex:\d+: ", s):
            t["errors"].append(s[:200])
        m = re.search(r"Reference `([^']+)' on page (\d+) undefined", s)
        if m:
            t["undefined_refs"].append(f"{m.group(1)} (page {m.group(2)})")
        m = re.search(r"Citation `([^']+)' on page (\d+) undefined", s)
        if m:
            t["undefined_cites"].append(f"{m.group(1)} (page {m.group(2)})")
        m = re.search(r"Label `([^']+)' multiply defined", s)
        if m:
            t["multiply_defined"].append(m.group(1))
        m = OVERFULL_RE.search(s)
        if m:
            pt = float(m.group(1))
            if pt >= overfull_pt:
                kind = m.group(2) or "box"
                where = m.group(3) or m.group(5) or "?"
                t["overfull"].append((pt, kind, where))
        m = OVERFULL_V_RE.search(s)
        if m and float(m.group(1)) >= overfull_pt:
            t["overfull_v"].append(float(m.group(1)))
        if "Float too large for page" in s or "float specifier changed" in s or "Float(s) lost" in s:
            t["float_problems"].append(s[:160])
        m = re.search(r"File `([^']+)' not found|LaTeX Error: File `([^']+)' not found|Package pdftex.def Error: File `([^']+)' not found", s)
        if m:
            t["missing_files"].append(next(g for g in m.groups() if g))
        if "Rerun to get" in s or "Label(s) may have changed" in s:
            t["rerun"].append(s[:120])
        if "Font shape" in s and "undefined" in s or "Missing character" in s:
            t["font_warnings"].append(s[:140])
    t["overfull"].sort(key=lambda x: -x[0])
    return t


# ---------------------------------------------------------------------------
# helpers on the PDF
# ---------------------------------------------------------------------------

def page_count(pdf: Path) -> int:
    if fitz is not None:
        try:
            with fitz.open(str(pdf)) as doc:
                return doc.page_count
        except Exception:
            pass
    if have("pdfinfo"):
        rc, out = run([tool("pdfinfo"), str(pdf)])
        m = re.search(r"Pages:\s+(\d+)", out)
        if m:
            return int(m.group(1))
    try:
        import pypdf  # type: ignore
        return len(pypdf.PdfReader(str(pdf)).pages)
    except Exception:
        return 0


def pdf_text_pages(pdf: Path) -> List[str]:
    """Plain text per page. pdftotext separates pages with form feeds."""
    if have("pdftotext"):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "t.txt"
            rc, _ = run([tool("pdftotext"), "-enc", "UTF-8", str(pdf), str(out)])
            if out.exists():
                return out.read_text(encoding="utf-8", errors="replace").split("\f")
    if fitz is not None:
        try:
            with fitz.open(str(pdf)) as doc:
                return [p.get_text() for p in doc]
        except Exception:
            pass
    return []


@dataclass
class Box:
    x0: float
    y0: float
    x1: float
    y1: float
    kind: str  # line | image | drawing
    text: str = ""
    words: List[tuple] = field(default_factory=list)  # (x0, y0, x1, y1, text) for lines


def page_boxes(pdf: Path) -> List[Tuple[float, float, List[Box]]]:
    """Per page: (width, height, boxes). Text lines from pdftotext -bbox-layout
    when available (its line grouping is better than PyMuPDF's for tables),
    images and drawings from PyMuPDF when available."""
    pages: List[Tuple[float, float, List[Box]]] = []
    if have("pdftotext"):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "b.html"
            run([tool("pdftotext"), "-bbox-layout", "-enc", "UTF-8", str(pdf), str(out)])
            if out.exists():
                html = out.read_text(encoding="utf-8", errors="replace")
                for pm in re.finditer(r'<page width="([\d.]+)" height="([\d.]+)">(.*?)</page>', html, re.S):
                    w, h, body = float(pm.group(1)), float(pm.group(2)), pm.group(3)
                    boxes: List[Box] = []
                    for lm in re.finditer(r'<line xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">(.*?)</line>', body, re.S):
                        words = [(float(a), float(b_), float(c), float(d), html_unescape(t)) for a, b_, c, d, t in
                                 re.findall(r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">(.*?)</word>', lm.group(5), re.S)]
                        boxes.extend(lines_from_words(words))
                    pages.append((w, h, boxes))
    if fitz is not None:
        try:
            with fitz.open(str(pdf)) as doc:
                if not pages:
                    for p in doc:
                        groups: Dict[Tuple[int, int], List[tuple]] = {}
                        for w in p.get_text("words"):
                            groups.setdefault((w[5], w[6]), []).append(w)
                        boxes = []
                        for key in sorted(groups):
                            boxes.extend(lines_from_words([(w[0], w[1], w[2], w[3], w[4]) for w in groups[key]]))
                        pages.append((p.rect.width, p.rect.height, boxes))
                for i, p in enumerate(doc):
                    if i >= len(pages):
                        break
                    boxes = pages[i][2]
                    try:
                        for info in p.get_image_info():
                            b = info.get("bbox")
                            if b:
                                boxes.append(Box(b[0], b[1], b[2], b[3], "image", "image"))
                    except Exception:
                        pass
                    try:
                        for d in p.get_drawings():
                            r = d.get("rect")
                            if r is not None and (r.width > 2 or r.height > 2):
                                boxes.append(Box(r.x0, r.y0, r.x1, r.y1, "drawing", "rule/drawing"))
                    except Exception:
                        pass
        except Exception:
            pass
    return pages


def box_from_words(ws: List[tuple]) -> Box:
    return Box(min(x[0] for x in ws), min(x[1] for x in ws), max(x[2] for x in ws),
               max(x[3] for x in ws), "line", " ".join(x[4] for x in ws), list(ws))


def lines_from_words(words: List[tuple]) -> List[Box]:
    """One line box per word group; splitting happens later, once the
    column geometry is known (see split_at_gutters)."""
    if not words:
        return []
    return [box_from_words(sorted(words, key=lambda w: w[0]))]


def split_at_gutters(b: Box, cols: List[Tuple[float, float]], tol: float = 6.0, big_gap: float = 30.0) -> List[Box]:
    """pdftotext joins a left-column line and a right-column line that share
    a baseline into one line. Split a line's words at any gap that straddles
    a gutter between two columns, or at any gap wider than big_gap, so each
    piece is measured against its own column."""
    if not b.words or len(b.words) < 2:
        return [b]
    gutters = [(cols[i][1], cols[i + 1][0]) for i in range(len(cols) - 1)]
    out: List[Box] = []
    cur = [b.words[0]]
    for w in b.words[1:]:
        prev_end, start = cur[-1][2], w[0]
        gap = start - prev_end
        crosses = any(prev_end <= R + tol and start >= L - tol for R, L in gutters) and gap > 2.0
        if crosses or gap > big_gap:
            out.append(box_from_words(cur))
            cur = [w]
        else:
            cur.append(w)
    out.append(box_from_words(cur))
    return out


def html_unescape(s: str) -> str:
    return (s.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
             .replace("&quot;", '"').replace("&#39;", "'"))


# ---------------------------------------------------------------------------
# 4. overflow against the text block
# ---------------------------------------------------------------------------

def justified_edges(values: List[float], side: str = "right", bin_pt: float = 4.0,
                    min_share: float = 0.03) -> List[float]:
    """Find the x positions where many lines start (side='left') or end
    (side='right'): the text block or column edges the document itself
    establishes."""
    if not values:
        return []
    bins: Dict[int, List[float]] = {}
    for v in values:
        bins.setdefault(int(v // bin_pt), []).append(v)
    threshold = max(5, int(len(values) * min_share))
    peaks = sorted(b for b, vs in bins.items() if len(vs) >= threshold)
    pick = max if side == "right" else min
    edges: List[float] = []
    for b in peaks:
        e = pick(bins[b])
        # Peaks closer than a paragraph indent (first lines start ~15 pt in;
        # an abstract or quotation block ends ~25 pt early) are one edge.
        if edges and abs(e - edges[-1]) <= 40.0:
            edges[-1] = pick(edges[-1], e)
        else:
            edges.append(e)
    return edges


def column_geometry(pages: List[Tuple[float, float, List[Box]]]) -> List[Tuple[float, float]]:
    """Columns as (left, right) from where justified lines start and end.
    A single-column paper yields one pair; a two-column class yields two."""
    lines = [b for _, _, boxes in pages for b in boxes if b.kind == "line" and len(b.text.split()) >= 4]
    lefts = justified_edges([b.x0 for b in lines], "left")
    rights = justified_edges([b.x1 for b in lines], "right")
    if not lefts or not rights:
        return []
    cols: List[Tuple[float, float]] = []
    for i, L in enumerate(lefts):
        nxt = lefts[i + 1] if i + 1 < len(lefts) else None
        cands = [r for r in rights if r > L and (nxt is None or r < nxt)]
        if not cands:
            continue
        cols.append((L, max(cands)))
    # an indented block (abstract, quotation) inside a column is not a column
    merged: List[Tuple[float, float]] = []
    for L, R in cols:
        if merged and L < merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], R))
        else:
            merged.append((L, R))
    return merged


def figure_regions(boxes: List[Box]) -> List[Tuple[float, float, float, float]]:
    """Cluster images and drawings that overlap vertically into regions: a
    vector figure is hundreds of small paths, a ruled table a few long ones.
    Returns bounding boxes of regions at least 40 pt tall or 80 pt wide."""
    shapes = [b for b in boxes if b.kind in ("image", "drawing") and (b.x1 - b.x0 > 2 or b.y1 - b.y0 > 2)]
    shapes.sort(key=lambda b: b.y0)
    regions: List[List[float]] = []
    for s in shapes:
        for r in regions:
            if s.y0 <= r[3] + 8 and s.y1 >= r[1] - 8:
                r[0], r[1], r[2], r[3] = min(r[0], s.x0), min(r[1], s.y0), max(r[2], s.x1), max(r[3], s.y1)
                break
        else:
            regions.append([s.x0, s.y0, s.x1, s.y1])
    return [(r[0], r[1], r[2], r[3]) for r in regions if (r[3] - r[1] >= 40 or r[2] - r[0] >= 80)]


def overflow_check(pages: List[Tuple[float, float, List[Box]]], tol_pt: float,
                   page_edge_pt: float = 9.0) -> Tuple[List[Tuple[int, float, str, str]], List[Tuple[float, float]]]:
    """Return (findings, columns). Each finding: (page, overhang_pt, kind, text).

    A box is measured against the right edge of the column it starts in. A
    box that reaches at least halfway into the next column is a full-width
    element (title, abstract, table*, figure*) and is measured against the
    outermost edge instead."""
    cols = column_geometry(pages)
    outer_right = max((R for _, R in cols), default=0.0)
    findings: List[Tuple[int, float, str, str]] = []
    for pno, (w, h, raw_boxes) in enumerate(pages, 1):
        boxes: List[Box] = []
        for rb in raw_boxes:
            boxes.extend(split_at_gutters(rb, cols) if rb.kind == "line" and cols else [rb])
        regions = figure_regions(boxes)
        for b in boxes:
            over_page = max(b.x1 - (w - page_edge_pt), 0.0)
            over_edge = 0.0
            if cols:
                ci = min(range(len(cols)), key=lambda i: abs(cols[i][0] - b.x0))
                allowed = cols[ci][1]
                if ci + 1 < len(cols):
                    nL, nR = cols[ci + 1]
                    # crossing a quarter of the way into the next column is a
                    # full-width element (title, caption, table*), not overflow
                    if b.x1 >= nL + 0.25 * (nR - nL):
                        allowed = outer_right
                if b.kind == "line":
                    # text inside a drawn figure or table is measured against
                    # that region; the region itself is measured against the
                    # column, so an overflowing table is still reported
                    for rx0, ry0, rx1, ry1 in regions:
                        if b.y0 >= ry0 - 2 and b.y1 <= ry1 + 2 and b.x0 >= rx0 - 6 and b.x1 <= rx1 + 6:
                            allowed = max(allowed, min(rx1, outer_right + tol_pt))
                            break
                over_edge = max(0.0, b.x1 - allowed)
            overhang = max(over_page, over_edge)
            if b.kind != "line" and over_edge and not over_page and over_edge < tol_pt * 2:
                # a rule or frame may bleed a little past the text edge
                continue
            if overhang > tol_pt:
                findings.append((pno, round(overhang, 1), b.kind, b.text[:90]))
            bottom_over = b.y1 - (h - page_edge_pt)
            if bottom_over > tol_pt and b.kind == "line":
                findings.append((pno, round(bottom_over, 1), "line (bottom)", b.text[:90]))
    findings.sort(key=lambda f: (f[0], -f[1]))
    return findings, cols


# ---------------------------------------------------------------------------
# 5. floats: where they landed vs where they are cited
# ---------------------------------------------------------------------------

def match_braces(s: str, start: int) -> Tuple[str, int]:
    """s[start] must be '{'. Return (inner, index after closing brace)."""
    depth = 0
    i = start
    while i < len(s):
        c = s[i]
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return s[start + 1:i], i + 1
        i += 1
    return s[start + 1:], len(s)


def norm_title(s: str) -> str:
    s = re.sub(r"\\numberline\s*\{[^}]*\}", " ", s)
    s = re.sub(r"\\[A-Za-z@]+\*?", " ", s)
    s = re.sub(r"[^a-z0-9]+", " ", s.lower())
    return s.strip()


def parse_aux(aux_text: str) -> Tuple[Dict[str, int], List[Tuple[str, str, int]]]:
    """labels -> page ; headings as (level, normalized title, page) in order."""
    labels: Dict[str, int] = {}
    for m in re.finditer(r"\\newlabel\{([^}]+)\}\{\{([^{}]*)\}\{(\d+)\}", aux_text):
        labels[m.group(1)] = int(m.group(3))
    headings: List[Tuple[str, str, int]] = []
    for m in re.finditer(r"\\contentsline \{(section|chapter|subsection)\}\{", aux_text):
        title, end = match_braces(aux_text, m.end() - 1)
        pm = re.match(r"\{(\d+)\}", aux_text[end:])
        if pm:
            headings.append((m.group(1), norm_title(title), int(pm.group(1))))
    return labels, headings


def gather_source(main: Path, seen: Optional[set] = None) -> str:
    """main.tex with \\input and \\include expanded, comments stripped."""
    seen = seen or set()
    if main in seen or not main.exists():
        return ""
    seen.add(main)
    text = main.read_text(encoding="utf-8", errors="replace")
    text = re.sub(r"(?<!\\)%.*", "", text)

    def repl(m: "re.Match[str]") -> str:
        name = m.group(2).strip()
        cand = main.parent / name
        if cand.suffix == "":
            cand = cand.with_suffix(".tex")
        return "\n" + gather_source(cand, seen) + "\n"

    return re.sub(r"\\(input|include)\{([^}]+)\}", repl, text)


def float_labels(source: str) -> Dict[str, str]:
    """label -> float environment name, for labels inside float environments."""
    out: Dict[str, str] = {}
    for env in FLOAT_ENVS:
        e = re.escape(env)
        for m in re.finditer(r"\\begin\{" + e + r"\}(.*?)\\end\{" + e + r"\}", source, re.S):
            for lm in re.finditer(r"\\label\{([^}]+)\}", m.group(1)):
                out[lm.group(1)] = env
    return out


def citing_sections(source: str) -> Dict[str, str]:
    """label -> normalized title of the section containing its first \\ref."""
    heads: List[Tuple[int, str]] = []
    for m in re.finditer(HEADING_CMDS, source):
        title, _ = match_braces(source, m.end() - 1)
        heads.append((m.start(), norm_title(title)))
    first_ref: Dict[str, int] = {}
    for m in re.finditer(REF_CMDS, source):
        for lab in m.group(1).split(","):
            lab = lab.strip()
            if lab and lab not in first_ref:
                first_ref[lab] = m.start()
    out: Dict[str, str] = {}
    for lab, pos in first_ref.items():
        current = ""
        for hpos, title in heads:
            if hpos <= pos:
                current = title
            else:
                break
        out[lab] = current
    return out


def section_page_ranges(headings: List[Tuple[str, str, int]], last_page: int) -> List[Tuple[str, int, int]]:
    """Top-level (section/chapter) ranges: (title, first page, last page)."""
    tops = [(t, p) for lvl, t, p in headings if lvl in ("section", "chapter")]
    out = []
    for i, (t, p) in enumerate(tops):
        end = tops[i + 1][1] if i + 1 < len(tops) else last_page
        out.append((t, p, max(end, p)))
    return out


def find_references_page(headings: List[Tuple[str, str, int]], texts: List[str]) -> Optional[int]:
    for lvl, t, p in headings:
        if REFS_TITLE.match(t.replace(" ", " ")):
            return p
    hit = None
    for i, t in enumerate(texts, 1):
        for ln in t.splitlines():
            if REFS_TITLE.match(ln) and i > len(texts) // 3:
                hit = i
    return hit


def float_check(main: Path, aux: Path, texts: List[str], n_pages: int) -> Tuple[List[str], List[str], Optional[int]]:
    """Return (fails, warns, references_page)."""
    if not aux.exists():
        return [], [f"no {aux.name}; float placement not checked"], None
    labels, headings = parse_aux(aux.read_text(encoding="utf-8", errors="replace"))
    source = gather_source(main)
    floats = float_labels(source)
    cites = citing_sections(source)
    ranges = section_page_ranges(headings, n_pages)
    refs_page = find_references_page(headings, texts)
    fails: List[str] = []
    warns: List[str] = []
    for lab, env in sorted(floats.items()):
        page = labels.get(lab)
        if page is None:
            warns.append(f"{env} {lab}: no page recorded in aux (never referenced or build incomplete)")
            continue
        if refs_page and page >= refs_page and not lab.lower().startswith(("app", "supp", "s")):
            fails.append(f"{env} {lab} is on page {page}, inside the references (start page {refs_page})")
            continue
        sec = cites.get(lab)
        if not sec:
            warns.append(f"{env} {lab} on page {page} is never cited with \\ref/\\cref")
            continue
        rng = next((r for r in ranges if r[0] == sec or (sec and r[0] and (sec.startswith(r[0]) or r[0].startswith(sec)))), None)
        if rng is None:
            continue
        _, a, b = rng
        if page < a - 1 or page > b:
            warns.append(f"{env} {lab} placed on page {page}, cited in '{sec.title()}' (pages {a} to {b})")
    twocol = bool(re.search(r"\\documentclass\[[^\]]*twocolumn|\\documentclass\[[^\]]*\]\{IEEEtran\}|\\twocolumn", source))
    if twocol and re.search(r"\\begin\{(figure|table)\*\}\s*\[[^\]]*H", source):
        warns.append("[H] on a starred (double-column) float is inert; use \\FloatBarrier, stfloats, or [!t]")
    return fails, warns, refs_page


# ---------------------------------------------------------------------------
# 6. fonts
# ---------------------------------------------------------------------------

def font_check(pdf: Path) -> Tuple[str, str, List[str]]:
    if have("pdffonts"):
        rc, out = run([tool("pdffonts"), str(pdf)])
        rows = [ln for ln in out.splitlines()[2:] if ln.strip()]
        not_emb = []
        type3 = []
        for ln in rows:
            cols = ln.split()
            if len(cols) < 5:
                continue
            name = cols[0]
            if re.search(r"\byes\b|\bno\b", ln):
                # columns: name type encoding emb sub uni object ID
                m = re.search(r"\s(yes|no)\s+(yes|no)\s+(yes|no)\s", ln)
                if m and m.group(1) == "no":
                    not_emb.append(name)
            if " Type 3 " in ln:
                type3.append(name)
        if not_emb:
            return FAIL, f"{len(not_emb)} font(s) not embedded", not_emb
        if type3:
            return WARN, f"{len(type3)} Type 3 (bitmap) font(s); journals usually reject these", type3
        return PASS, f"all {len(rows)} fonts embedded", []
    if fitz is not None:
        try:
            with fitz.open(str(pdf)) as doc:
                names = set()
                bad = set()
                for p in doc:
                    for f in p.get_fonts(full=True):
                        names.add(f[3])
                        # (xref, ext, type, basefont, name, encoding, referencer)
                        if f[1] == "n/a":
                            bad.add(f[3])
                if bad:
                    return FAIL, f"{len(bad)} font(s) not embedded", sorted(bad)
                return PASS, f"all {len(names)} fonts embedded", []
        except Exception:
            pass
    return SKIP, "no pdffonts or PyMuPDF available; font embedding not checked", []


# ---------------------------------------------------------------------------
# 7. derived artifacts
# ---------------------------------------------------------------------------

def derived_check(pairs: List[str]) -> Check:
    bad, ok, missing = [], [], []
    for pair in pairs:
        if ":" not in pair:
            missing.append(f"{pair}: expected OUT:SRC")
            continue
        out_s, src_s = pair.rsplit(":", 1) if not re.match(r"^[A-Za-z]:\\", pair) else pair.split(":", 2)[-2:]
        out, src = Path(out_s), Path(src_s)
        if not out.exists():
            bad.append(f"{out} does not exist (source {src})")
        elif not src.exists():
            missing.append(f"{src} does not exist")
        elif src.stat().st_mtime > out.stat().st_mtime + 1:
            age = (src.stat().st_mtime - out.stat().st_mtime) / 60
            bad.append(f"{out} is {age:.0f} min older than {src}; rebuild it")
        else:
            ok.append(f"{out} is newer than {src}")
    if bad:
        return Check("derived", FAIL, f"{len(bad)} derived artifact(s) stale or missing", bad + missing)
    if missing:
        return Check("derived", WARN, "some sources could not be checked", missing + ok)
    return Check("derived", PASS, f"{len(ok)} derived artifact(s) up to date", ok)


# ---------------------------------------------------------------------------
# 8. thumbnails
# ---------------------------------------------------------------------------

def thumbnails(pdf: Path, out_dir: Path, dpi: int) -> List[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    prefix = out_dir / pdf.stem
    if have("pdftoppm"):
        run([tool("pdftoppm"), "-r", str(dpi), "-png", str(pdf), str(prefix)])
        files = sorted(out_dir.glob(pdf.stem + "-*.png"), key=lambda p: int(re.search(r"-(\d+)\.png$", p.name).group(1)))
        if files:
            return files
    if fitz is not None:
        try:
            files = []
            with fitz.open(str(pdf)) as doc:
                for i, p in enumerate(doc, 1):
                    pix = p.get_pixmap(dpi=dpi)
                    f = out_dir / f"{pdf.stem}-{i}.png"
                    pix.save(str(f))
                    files.append(f)
            return files
        except Exception:
            pass
    return []


# ---------------------------------------------------------------------------
# orchestration
# ---------------------------------------------------------------------------

def check_target(target: Path, a: argparse.Namespace, report_dir: Path) -> TargetReport:
    rep = TargetReport(target=str(target))
    if target.is_dir():
        cand = target / "main.tex"
        target = cand if cand.exists() else next(iter(target.glob("*.tex")), target)
    if target.suffix.lower() == ".pdf":
        main, pdf, log = None, target, target.with_suffix(".log")
        rep.add(Check("build", SKIP, "PDF given directly; not rebuilt"))
    else:
        main = target
        pdf = target.with_suffix(".pdf")
        log = target.with_suffix(".log")
        if a.no_build:
            rep.add(Check("build", SKIP if pdf.exists() else FAIL,
                          "not rebuilt (--no-build); using existing PDF" if pdf.exists() else "no PDF and --no-build given"))
        else:
            t0 = time.time()
            rc, out, log = build(main, a.engine)
            pdf = main.with_suffix(".pdf")
            if rc == 127:
                rep.add(Check("build", FAIL, out))
            elif not pdf.exists():
                rep.add(Check("build", FAIL, f"build exited {rc} and produced no PDF", out.strip().splitlines()[-15:]))
            else:
                # latexmk exits non-zero on warnings it considers fatal (e.g. a
                # rerun limit); a PDF that exists with a clean log is still a build.
                rep.add(Check("build", PASS if rc == 0 else WARN,
                              f"exit {rc} in {time.time() - t0:.0f}s" + ("" if rc == 0 else "; see log triage")))
    rep.pdf, rep.log = str(pdf), str(log)
    if not pdf.exists():
        return rep

    # 2. log
    if log.exists():
        t = triage_log(log.read_text(encoding="utf-8", errors="replace"), a.overfull_pt)
        det = []
        status = PASS
        if t["errors"]:
            status = FAIL
            det += [f"error: {e}" for e in t["errors"][:20]]
        if t["undefined_refs"] or t["undefined_cites"]:
            status = FAIL
            det += [f"undefined reference: {r}" for r in t["undefined_refs"]]
            det += [f"undefined citation: {r}" for r in t["undefined_cites"]]
        if t["missing_files"]:
            status = FAIL
            det += [f"missing file: {f}" for f in t["missing_files"]]
        if t["multiply_defined"]:
            status = FAIL if status != FAIL else status
            det += [f"label multiply defined: {l}" for l in t["multiply_defined"]]
        if t["rerun"]:
            status = FAIL if status == FAIL else WARN
            det += ["labels changed on the last pass; run the build again before trusting cross-references"]
        if t["float_problems"]:
            status = FAIL if status == FAIL else WARN
            det += [f"float: {f}" for f in t["float_problems"][:10]]
        if t["overfull"]:
            status = FAIL if status == FAIL else WARN
            det += [f"overfull {kind} {pt:.1f}pt at line {where}" for pt, kind, where in t["overfull"][:25]]
            if len(t["overfull"]) > 25:
                det.append(f"... {len(t['overfull']) - 25} more overfull boxes above {a.overfull_pt}pt")
        if t["overfull_v"]:
            det += [f"overfull vbox {pt:.1f}pt" for pt in t["overfull_v"][:5]]
        if t["font_warnings"]:
            det += [f"font: {f}" for f in t["font_warnings"][:5]]
        n_over = len(t["overfull"])
        summary = (f"{len(t['errors'])} error(s), {len(t['undefined_refs']) + len(t['undefined_cites'])} undefined ref/cite, "
                   f"{n_over} overfull box(es) >= {a.overfull_pt}pt, {len(t['float_problems'])} float warning(s)")
        rep.add(Check("log", status, summary, det))
    else:
        rep.add(Check("log", SKIP, f"no log at {log.name}"))

    # 3. pages and words
    n = page_count(pdf)
    rep.pages = n
    if a.max_pages:
        if n > a.max_pages:
            rep.add(Check("pages", FAIL, f"{n} pages against a cap of {a.max_pages} ({n - a.max_pages} over)"))
        else:
            rep.add(Check("pages", PASS, f"{n} pages, cap {a.max_pages}"))
    else:
        rep.add(Check("pages", PASS if n else FAIL, f"{n} pages" if n else "could not count pages"))

    texts = pdf_text_pages(pdf)

    # 5. floats (needs texts for the references page)
    refs_page = None
    if main is not None:
        aux = main.with_suffix(".aux")
        fails, warns, refs_page = float_check(main, aux, texts, n)
        status = FAIL if fails else (WARN if warns else PASS)
        summary = f"{len(fails)} float(s) in the references, {len(warns)} placement warning(s)"
        rep.add(Check("floats", status, summary, fails + warns))
        for f in fails:
            m = re.search(r"on page (\d+)", f)
            if m:
                rep.flag(int(m.group(1)), "float in references")
    else:
        refs_page = find_references_page([], texts)
        rep.add(Check("floats", SKIP, "no .tex source given; float placement not checked"))

    if texts:
        body_pages = texts[:refs_page - 1] if refs_page else texts
        body = "\n".join(body_pages)
        if refs_page and refs_page - 1 < len(texts):
            page_txt = texts[refs_page - 1]
            head = None
            for ln in page_txt.splitlines():
                if REFS_TITLE.match(ln):
                    head = page_txt.find(ln)
                    break
            body += "\n" + (page_txt[:head] if head is not None else "")
        words = len(re.findall(r"[A-Za-z][A-Za-z'-]+", body))
        if a.max_words:
            status = FAIL if words > a.max_words else PASS
            rep.add(Check("words", status, f"{words} body words (before references) against guidance of {a.max_words}"))
        else:
            rep.add(Check("words", PASS, f"{words} body words before references" + (f" (references start page {refs_page})" if refs_page else "")))
    else:
        rep.add(Check("words", SKIP, "no text extraction available (pdftotext or PyMuPDF)"))

    # 4. overflow
    pages = page_boxes(pdf)
    if pages:
        findings, edges = overflow_check(pages, a.margin_pt)
        by_page: Dict[int, List[Tuple[float, str, str]]] = {}
        for pno, over, kind, text in findings:
            by_page.setdefault(pno, []).append((over, kind, text))
        det = []
        worst = 0.0
        for pno in sorted(by_page):
            items = by_page[pno]
            top = max(items, key=lambda x: x[0])
            worst = max(worst, top[0])
            det.append(f"page {pno}: {len(items)} item(s) past the text edge, worst {top[0]:.1f}pt ({top[1]}): \"{top[2]}\"")
            rep.flag(pno, f"{top[0]:.0f}pt past edge")
        edge_note = ("columns " + ", ".join(f"{L:.0f}-{R:.0f}pt" for L, R in edges)) if edges else "no text edge could be established"
        if by_page:
            status = FAIL if worst >= a.margin_pt * 3 else WARN
            rep.add(Check("overflow", status, f"{len(by_page)} page(s) with content past the text block; worst {worst:.1f}pt ({edge_note})", det))
        else:
            rep.add(Check("overflow", PASS, f"nothing past the text block on {len(pages)} pages ({edge_note})"))
    else:
        rep.add(Check("overflow", SKIP, "no bounding boxes available (needs pdftotext or PyMuPDF)"))

    # 6. fonts
    st, summ, det = font_check(pdf)
    rep.add(Check("fonts", st, summ, det))

    # 8. thumbnails
    if not a.no_thumbs:
        tdir = report_dir / "pages" / (pdf.parent.name + "-" + pdf.stem)
        files = thumbnails(pdf, tdir, a.dpi)
        rep.thumbnails = [os.path.relpath(f, report_dir).replace(os.sep, "/") for f in files]
        if not files:
            rep.add(Check("thumbnails", SKIP, "no renderer available (pdftoppm or PyMuPDF)"))
    return rep


def render_report(reports: List[TargetReport], derived: Optional[Check], a: argparse.Namespace) -> str:
    lines = ["# Build report", "",
             f"Generated {time.strftime('%Y-%m-%d %H:%M')} by build_check.py. "
             "PASS means the check found nothing; it does not mean the page is right. Look at the thumbnails.", ""]
    overall = PASS
    for r in reports:
        if r.verdict == FAIL:
            overall = FAIL
        elif r.verdict == WARN and overall != FAIL:
            overall = WARN
    if derived and derived.status == FAIL:
        overall = FAIL
    lines.append(f"## Overall: {overall}")
    lines.append("")
    lines.append("| Target | Verdict | Pages | Build | Log | Overflow | Floats | Fonts | Words |")
    lines.append("|---|---|---:|---|---|---|---|---|---|")
    for r in reports:
        st = {c.name: c.status for c in r.checks}
        lines.append(f"| `{r.target}` | **{r.verdict}** | {r.pages} | {st.get('build','-')} | {st.get('log','-')} | "
                     f"{st.get('overflow','-')} | {st.get('floats','-')} | {st.get('fonts','-')} | {st.get('words','-')} |")
    lines.append("")
    if derived:
        lines += [f"## Derived artifacts: {derived.status}", "", derived.summary, ""]
        lines += [f"- {d}" for d in derived.details] + [""]
    for r in reports:
        lines += [f"## {r.target}", "", f"PDF: `{r.pdf}`  ", f"Pages: {r.pages}", ""]
        for c in r.checks:
            lines.append(f"### {c.name}: {c.status}")
            lines.append("")
            lines.append(c.summary)
            if c.details:
                lines.append("")
                lines += [f"- {d}" for d in c.details]
            lines.append("")
        if r.thumbnails:
            lines.append("### Pages")
            lines.append("")
            lines.append("Flagged pages are marked. Open each image; a thumbnail is enough to see a table past the margin or a float in the wrong place.")
            lines.append("")
            cols = 4
            for i in range(0, len(r.thumbnails), cols):
                row = r.thumbnails[i:i + cols]
                cells = []
                for j, t in enumerate(row, start=i + 1):
                    flags = r.page_flags.get(j)
                    label = f"p{j}" + (f" **{'; '.join(flags)}**" if flags else "")
                    cells.append(f"![{label}]({t})<br>{label}")
                lines.append("| " + " | ".join(cells) + " |")
                if i == 0:
                    lines.append("|" + "---|" * len(row))
            lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# self-test
# ---------------------------------------------------------------------------

def self_test() -> int:
    ok = True

    def check(desc: str, cond: bool) -> None:
        nonlocal ok
        print(("  ok   " if cond else "  FAIL ") + desc)
        ok = ok and cond

    log = """! Undefined control sequence.
LaTeX Warning: Reference `tab:big' on page 4 undefined on input line 88.
LaTeX Warning: Citation `smith2020' on page 2 undefined on input line 12.
Overfull \\hbox (23.4pt too wide) in alignment at lines 120--131
Overfull \\hbox (1.2pt too wide) in paragraph at lines 40--41
LaTeX Warning: Float too large for page by 12.0pt on input line 300.
LaTeX Warning: Label(s) may have changed. Rerun to get cross-references right.
LaTeX Warning: Label `fig:a' multiply defined.
"""
    t = triage_log(log, 5.0)
    check("log: error caught", len(t["errors"]) == 1)
    check("log: undefined ref and cite", t["undefined_refs"] == ["tab:big (page 4)"] and t["undefined_cites"] == ["smith2020 (page 2)"])
    check("log: overfull threshold applied", len(t["overfull"]) == 1 and t["overfull"][0][1] == "alignment")
    check("log: float, rerun, multiply defined", t["float_problems"] and t["rerun"] and t["multiply_defined"] == ["fig:a"])

    # overflow: 40 justified lines ending at 500pt, one table row to 560pt
    boxes = [Box(72, 100 + i * 12, 500, 110 + i * 12, "line", "the quick brown fox jumps over") for i in range(40)]
    boxes.append(Box(72, 700, 561, 710, "line", "0.123 0.456 0.789 0.012 0.345 0.678 0.901"))
    boxes.append(Box(72, 720, 380, 730, "line", "short last line of a paragraph"))
    boxes.append(Box(150, 60, 420, 74, "line", "A Centered Title That Ends Before The Edge"))
    findings, cols = overflow_check([(595.0, 842.0, boxes)], 3.0)
    check("overflow: one column 72-500", len(cols) == 1 and abs(cols[0][1] - 500) <= 1)
    check("overflow: one wide table row flagged, short line and title not", len(findings) == 1 and findings[0][1] >= 58)

    # two-column: columns 60-300 and 320-540; a left-column line to 331; a centered title
    boxes2 = [Box(60, 100 + i * 12, 300, 110 + i * 12, "line", "left column text goes here now") for i in range(30)]
    boxes2 += [Box(320, 100 + i * 12, 540, 110 + i * 12, "line", "right column text goes here now") for i in range(30)]
    boxes2.append(Box(60, 600, 331, 610, "line", "a b c d e f g h wide"))
    boxes2.append(Box(110, 40, 490, 56, "line", "A Solver Fallback Not Uncertainty Awareness Title"))
    boxes2.append(Box(60, 70, 540, 82, "line", "abstract line spanning both columns of the page"))
    boxes2.append(Box(320, 700, 561, 710, "line", "right column table row past the edge 1 2 3"))
    # paragraph-indented first lines must not become a third column
    boxes2 += [Box(75, 500 + i * 12, 300, 510 + i * 12, "line", "indented first line of a paragraph here") for i in range(8)]
    # a joined line: left-column words then right-column words on one baseline
    joined = [(60, 800, 100, 810, "left"), (104, 800, 200, 810, "words"), (204, 800, 299, 810, "end"),
              (321, 800, 380, 810, "right"), (384, 800, 430, 810, "start")]
    boxes2.append(box_from_words(joined))
    # a full-width figure (drawing region 60-540) with an axis label ending at 345: inside the region, not overflow
    boxes2 += [Box(60 + i * 40, 200, 100 + i * 40, 320, "drawing", "rule/drawing") for i in range(12)]
    boxes2.append(Box(200, 300, 345, 310, "line", "fraction of cells screened in ranked"))
    findings2, cols2 = overflow_check([(595.0, 842.0, boxes2)], 3.0)
    check("overflow: two columns found despite indents", len(cols2) == 2 and abs(cols2[0][0] - 60) < 1 and abs(cols2[1][0] - 320) < 1)
    check("overflow: left overhang flagged, right overhang flagged, title/abstract/joined line not",
          len(findings2) == 2 and any(29 <= f[1] <= 32 for f in findings2) and any(19 <= f[1] <= 22 for f in findings2))

    aux = r"""\newlabel{tab:one}{{1}{3}{Caption}{table.1}{}}
\newlabel{fig:two}{{2}{9}{Caption}{figure.2}{}}
\@writefile{toc}{\contentsline {section}{\numberline {1}Introduction}{1}{section.1}\protected@file@percent }
\@writefile{toc}{\contentsline {section}{\numberline {2}Methods}{3}{section.2}\protected@file@percent }
\@writefile{toc}{\contentsline {section}{\numberline {3}Results}{5}{section.3}\protected@file@percent }
\@writefile{toc}{\contentsline {section}{References}{8}{section*.4}\protected@file@percent }
"""
    labels, heads = parse_aux(aux)
    check("aux: labels and pages", labels == {"tab:one": 3, "fig:two": 9})
    check("aux: headings with nested braces", [h[1] for h in heads] == ["introduction", "methods", "results", "references"])
    src = r"""\section{Introduction} text \section{Methods} see Table~\ref{tab:one}. \begin{table}\caption{x}\label{tab:one}\end{table}
\section{Results} see Figure~\cref{fig:two} \begin{figure}\label{fig:two}\end{figure}"""
    fl = float_labels(src)
    cs = citing_sections(src)
    check("source: float labels", fl == {"tab:one": "table", "fig:two": "figure"})
    check("source: citing sections", cs["tab:one"] == "methods" and cs["fig:two"] == "results")
    with tempfile.TemporaryDirectory() as td:
        main = Path(td) / "main.tex"
        main.write_text(src, encoding="utf-8")
        (Path(td) / "main.aux").write_text(aux, encoding="utf-8")
        fails, warns, refs_page = float_check(main, Path(td) / "main.aux", [""] * 10, 10)
        check("floats: figure in references is a FAIL", len(fails) == 1 and "fig:two" in fails[0] and refs_page == 8)
        check("floats: table in its own section passes", not any("tab:one" in w for w in warns))
        out = Path(td) / "out.pdf"
        srcf = Path(td) / "src.md"
        out.write_text("x")
        time.sleep(0.05)
        srcf.write_text("y")
        os.utime(srcf, (time.time() + 5, time.time() + 5))
        d = derived_check([f"{out}:{srcf}"])
        check("derived: stale output is a FAIL", d.status == FAIL)
    print("\nself-test " + ("passed" if ok else "FAILED"))
    return 0 if ok else 1


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("targets", nargs="*", help="main .tex files, directories containing main.tex, or PDFs")
    p.add_argument("--no-build", action="store_true", help="do not compile; check the existing PDF and log")
    p.add_argument("--engine", default="auto", choices=["auto", "pdflatex", "xelatex", "lualatex"])
    p.add_argument("--max-pages", type=int, default=0, help="page cap for the venue (FAIL if exceeded)")
    p.add_argument("--max-words", type=int, default=0, help="body word guidance (FAIL if exceeded)")
    p.add_argument("--overfull-pt", type=float, default=5.0, help="report overfull boxes at or above this many points (default 5)")
    p.add_argument("--margin-pt", type=float, default=3.0, help="tolerance past the text edge before content is reported (default 3)")
    p.add_argument("--derived", action="append", default=[], metavar="OUT:SRC",
                   help="derived artifact and its source; FAIL if the source is newer. Repeatable")
    p.add_argument("--report", help="path for BUILD_REPORT.md (default: <first target dir>/build-check/BUILD_REPORT.md)")
    p.add_argument("--json", dest="json_path", help="also write a JSON report here")
    p.add_argument("--dpi", type=int, default=45, help="thumbnail resolution (default 45)")
    p.add_argument("--no-thumbs", action="store_true", help="skip page thumbnails")
    p.add_argument("--strict", action="store_true", help="exit 1 on any FAIL")
    p.add_argument("--self-test", action="store_true", help="run the built-in checks on synthetic input")
    a = p.parse_args()

    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, OSError):
            pass

    if a.self_test:
        return self_test()
    if not a.targets and not a.derived:
        p.error("give at least one target, --derived pair, or --self-test")

    targets = [Path(t) for t in a.targets]
    for t in targets:
        if not t.exists():
            print(f"error: {t} does not exist", file=sys.stderr)
            return 2
    first_dir = (targets[0].parent if targets and targets[0].is_file() else (targets[0] if targets else Path.cwd()))
    report_path = Path(a.report) if a.report else first_dir / "build-check" / "BUILD_REPORT.md"
    report_dir = report_path.parent
    report_dir.mkdir(parents=True, exist_ok=True)

    reports = [check_target(t, a, report_dir) for t in targets]
    derived = derived_check(a.derived) if a.derived else None

    text = render_report(reports, derived, a)
    report_path.write_text(text, encoding="utf-8", newline="\n")
    if a.json_path:
        Path(a.json_path).write_text(json.dumps({
            "targets": [asdict(r) for r in reports],
            "derived": asdict(derived) if derived else None,
        }, indent=2), encoding="utf-8")

    any_fail = any(r.verdict == FAIL for r in reports) or (derived is not None and derived.status == FAIL)
    for r in reports:
        print(f"[{r.verdict:<4}] {r.target}  ({r.pages} pages)")
        for c in r.checks:
            if c.status in (FAIL, WARN):
                print(f"         {c.status:<4} {c.name}: {c.summary}")
    if derived:
        print(f"[{derived.status:<4}] derived artifacts: {derived.summary}")
    print(f"\nreport: {report_path}")
    if reports and any(r.thumbnails for r in reports):
        print("Open the report and look at the flagged pages before reporting the build as done.")
    return 1 if any_fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
