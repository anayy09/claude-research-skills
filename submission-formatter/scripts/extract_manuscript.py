#!/usr/bin/env python3
"""Extract a manuscript from any common format into a lossless-as-possible IR.

Produces three artifacts in the output directory:

    manuscript.json   structured intermediate representation (the IR)
    inventory.md      human-readable inventory for review
    media/            figures and images at original resolution

Supported inputs: .tex .docx .odt .rtf .html .htm .md .markdown .txt .pdf

The IR is a flat block list, deliberately close to the source order. Nothing is
summarized, reordered, or rewritten: block text is the extracted string. Every
lossy step is recorded in `source.warnings` so the caller can surface it.

Usage:
    python extract_manuscript.py paper.docx -o build
    python extract_manuscript.py paper.pdf -o build --format pdf
    python extract_manuscript.py main.tex -o build --quiet

External tools used when available: pandoc, pdftotext, pdfimages.
Python extras used when importable: python-docx, pdfplumber, pypdf.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

PANDOC_FORMATS = {
    ".docx": "docx",
    ".odt": "odt",
    ".rtf": "rtf",
    ".html": "html",
    ".htm": "html",
    ".tex": "latex",
    ".md": "markdown",
    ".markdown": "markdown",
    ".txt": None,
    ".pdf": None,
}

HEADING_WORDS = {
    "abstract", "keywords", "key words", "index terms", "introduction",
    "background", "related work", "literature review", "materials and methods",
    "methods", "methodology", "materials", "experiments", "experimental setup",
    "results", "results and discussion", "discussion", "conclusion",
    "conclusions", "conclusion and future work", "acknowledgements",
    "acknowledgments", "references", "bibliography", "appendix",
    "data availability", "author contributions", "conflict of interest",
    "declaration of competing interest", "funding", "ethics statement",
    "supplementary material",
}

CITE_PATTERNS = [
    re.compile(r"\\cite[a-zA-Z]*\s*(?:\[[^\]]*\])*\{([^}]*)\}"),
    re.compile(r"\[(\d+(?:\s*[-,–]\s*\d+)*)\]"),
    re.compile(r"\(([A-Z][A-Za-z\-']+(?:\s+et\s+al\.)?(?:\s*,\s*|\s+)\d{4}[a-z]?)\)"),
]

NUM_RE = re.compile(r"[-+]?\d[\d,]*(?:\.\d+)?(?:\s*[eE][-+]?\d+)?%?")


def warn(warnings: list, msg: str) -> None:
    if msg not in warnings:
        warnings.append(msg)


def have(tool: str) -> bool:
    return shutil.which(tool) is not None


def run(cmd: list, **kw) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


# --------------------------------------------------------------------------
# stage 1: input -> markdown-ish text
# --------------------------------------------------------------------------

def to_markdown(src: Path, fmt: str, media_dir: Path, warnings: list) -> str:
    """Convert the input to pandoc markdown, extracting media as a side effect."""
    if fmt == "pdf":
        return pdf_to_text(src, media_dir, warnings)

    if fmt in (None, "txt"):
        return src.read_text(encoding="utf-8", errors="replace")

    if not have("pandoc"):
        if fmt == "markdown":
            return src.read_text(encoding="utf-8", errors="replace")
        raise SystemExit(
            "pandoc is required to read %s files. Install pandoc, or supply the "
            "manuscript as .md/.txt/.pdf." % fmt
        )

    # --standalone matters: pandoc routes \title, \author, and the abstract
    # environment into document metadata, and without it they are dropped
    cmd = [
        "pandoc", "-f", fmt, "-t", "markdown-smart-simple_tables-multiline_tables",
        "--wrap=none", "--markdown-headings=atx", "--standalone",
        "--extract-media", str(media_dir), str(src),
    ]
    proc = run(cmd)
    if proc.returncode != 0:
        # retry without media extraction, which is the usual failure cause
        proc2 = run(cmd[:-3] + [str(src)])
        if proc2.returncode != 0:
            raise SystemExit("pandoc failed:\n" + (proc.stderr or proc2.stderr))
        warn(warnings, "media extraction failed; figures were not exported")
        return proc2.stdout
    if fmt == "latex":
        warn(warnings, "LaTeX input: the IR is an inventory and fidelity baseline "
                       "only. Reuse the original LaTeX body when building output.")
    return proc.stdout


def pdf_to_text(src: Path, media_dir: Path, warnings: list) -> str:
    """PDF text extraction. Lossy by nature; every known hazard is recorded."""
    warn(warnings, "PDF input is lossy: verify math, tables, footnotes, and "
                   "column reading order against the original")
    text = ""
    if have("pdftotext"):
        # default mode uses reading-order heuristics, which beats -layout on
        # two-column journal PDFs
        proc = run(["pdftotext", "-nopgbrk", str(src), "-"])
        if proc.returncode == 0:
            text = proc.stdout
    if not text.strip():
        try:
            import pdfplumber  # type: ignore
            with pdfplumber.open(str(src)) as pdf:
                text = "\n\n".join((p.extract_text() or "") for p in pdf.pages)
        except Exception:
            pass
    if not text.strip():
        try:
            from pypdf import PdfReader  # type: ignore
            reader = PdfReader(str(src))
            text = "\n\n".join((p.extract_text() or "") for p in reader.pages)
        except Exception:
            pass
    if not text.strip():
        raise SystemExit(
            "No extractable text in this PDF. It is probably a scan. OCR output "
            "cannot meet the fidelity contract without a full author proofread: "
            "ask for the DOCX or LaTeX source."
        )

    if have("pdfimages"):
        media_dir.mkdir(parents=True, exist_ok=True)
        rc = run(["pdfimages", "-png", "-p", str(src), str(media_dir / "img")])
        if rc.returncode != 0:
            warn(warnings, "pdfimages failed; figures were not exported")
        else:
            n = len(list(media_dir.glob("img-*.png")))
            warn(warnings, "%d raster objects extracted from the PDF; these are "
                           "page images, not necessarily figure files. Prefer the "
                           "author's original figure files." % n)
    return reflow_pdf_text(text)


def reflow_pdf_text(text: str) -> str:
    """Join wrapped lines into paragraphs and repair end-of-line hyphenation."""
    out_paras = []
    for block in re.split(r"\n\s*\n", text):
        lines = [ln.rstrip() for ln in block.splitlines() if ln.strip()]
        if not lines:
            continue
        buf = ""
        for ln in lines:
            ln = ln.strip()
            if not buf:
                buf = ln
            elif buf.endswith("-") and not buf.endswith("--"):
                buf = buf[:-1] + ln          # de-hyphenate across the break
            else:
                buf += " " + ln
        out_paras.append(buf)

    md = []
    for para in out_paras:
        if looks_like_heading(para):
            md.append("# " + para.strip())
        else:
            md.append(para)
    return "\n\n".join(md)


def looks_like_heading(line: str) -> bool:
    s = line.strip().rstrip(".")
    if not s or len(s) > 90 or s.endswith((",", ";", ":")):
        return False
    if s.lower().lstrip("0123456789. ") in HEADING_WORDS:
        return True
    if re.match(r"^(?:[IVXLC]+|\d+(?:\.\d+)*)[.)]?\s+[A-Z][\w\s\-,:()]+$", s):
        return len(s.split()) <= 12
    if s.isupper() and 1 < len(s.split()) <= 10:
        return True
    return False


# --------------------------------------------------------------------------
# stage 2a: pandoc metadata block
# --------------------------------------------------------------------------

META_KEYS = {"title", "subtitle", "author", "date", "abstract", "keywords",
             "institute", "thanks", "shorttitle"}


def split_front_matter(md: str):
    """Separate pandoc's YAML metadata block from the body.

    Only the keys a manuscript actually carries are read, and values are taken
    verbatim. Returns (metadata dict, body markdown).
    """
    lines = md.replace("\r\n", "\n").split("\n")
    if not lines or lines[0].strip() not in ("---", "..."):
        return {}, md

    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() in ("---", "..."):
            end = i
            break
    if end is None:
        return {}, md

    meta, key, buf, listing = {}, None, [], False

    def flush():
        if key is None:
            return
        if listing:
            meta[key] = [x for x in buf if x]
        else:
            val = "\n".join(buf).strip()
            if val:
                meta[key] = val

    for raw in lines[1:end]:
        line = raw.rstrip()
        m = re.match(r"^([A-Za-z][\w-]*):\s*(.*)$", line)
        if m and (not line.startswith((" ", "\t"))):
            flush()
            key, listing, buf = m.group(1).lower(), False, []
            inline = m.group(2).strip()
            if inline and inline not in ("|", ">", "|-", ">-"):
                buf = [inline.strip("'\"")]
        elif key is not None and line.strip().startswith("- "):
            listing = True
            buf.append(line.strip()[2:].strip().strip("'\""))
        elif key is not None and line.strip():
            buf.append(line.strip())
    flush()

    meta = {k: v for k, v in meta.items() if k in META_KEYS}
    return meta, "\n".join(lines[end + 1:])


# --------------------------------------------------------------------------
# stage 2b: markdown -> blocks
# --------------------------------------------------------------------------

ATTR_RE = re.compile(r"\{[#.][^}]*\}\s*$")
DIV_RE = re.compile(r"^:::+")
IMG_RE = re.compile(r"!\[(?P<cap>.*?)\]\((?P<src>[^)\s]+)(?:\s+\"[^\"]*\")?\)")
# Pandoc escapes a literal "[" as "\[", which collides with the display-math
# opener. A reference entry or citation ("\[1\] Smith, J.") holds only words and
# light punctuation, so anything with a control sequence or an operator in it is
# read as math and everything else as an escaped bracket.
ESC_BRACKET_RE = re.compile(r"^\\\[[\w\s.,;:&'\"()-]{1,80}\\\]")


def parse_markdown(md: str) -> list:
    lines = md.replace("\r\n", "\n").split("\n")
    blocks, i, n = [], 0, len(lines)
    counter = {"n": 0}

    def add(kind: str, **kw):
        counter["n"] += 1
        blocks.append(dict(id="b%04d" % counter["n"], type=kind, **kw))

    while i < n:
        raw = lines[i]
        line = raw.rstrip()
        stripped = line.strip()

        if not stripped or DIV_RE.match(stripped):
            i += 1
            continue

        # fenced code
        if stripped.startswith("```") or stripped.startswith("~~~"):
            fence = stripped[:3]
            j, body = i + 1, []
            while j < n and not lines[j].strip().startswith(fence):
                body.append(lines[j])
                j += 1
            add("code", text="\n".join(body), lang=stripped[3:].strip())
            i = j + 1
            continue

        # heading
        m = re.match(r"^(#{1,6})\s+(.*)$", stripped)
        if m:
            title = ATTR_RE.sub("", m.group(2)).strip()
            add("heading", level=len(m.group(1)), text=clean_inline(title))
            i += 1
            continue

        # display math
        is_marker = (re.match(r"^\\?\[\\?\[", stripped) is not None
                     or ESC_BRACKET_RE.match(stripped) is not None)
        if not is_marker and (stripped.startswith("$$") or stripped.startswith("\\[")):
            j, body = i, []
            closer = "$$" if stripped.startswith("$$") else "\\]"
            while j < n:
                body.append(lines[j])
                if lines[j].rstrip().endswith(closer) and (j > i or len(stripped) > 2):
                    break
                j += 1
            add("equation", latex="\n".join(body).strip())
            i = j + 1
            continue

        # tables: pipe or grid
        if stripped.startswith("|") or re.match(r"^\+[-=+]+\+$", stripped):
            j, body = i, []
            while j < n and (lines[j].strip().startswith("|")
                             or re.match(r"^\+[-=+]+\+$", lines[j].strip())):
                body.append(lines[j])
                j += 1
            grid = parse_table(body)
            cap = ""
            k = j
            while k < n and not lines[k].strip():
                k += 1
            if k < n and re.match(r"^\s*(:|Table\b)", lines[k]):
                cap = clean_inline(lines[k].strip().lstrip(":").strip())
                j = k + 1
            add("table", grid=grid, caption=cap, raw="\n".join(body))
            i = j
            continue

        # standalone figure
        img = IMG_RE.search(stripped)
        if img and stripped.startswith(("![", "[!", "!")):
            cap = clean_inline(img.group("cap"))
            if not cap:
                k = i + 1
                while k < n and not lines[k].strip():
                    k += 1
                if k < n and re.match(r"^\s*(Fig(ure)?\.?\s*\d|:)", lines[k], re.I):
                    cap = clean_inline(lines[k].strip().lstrip(":").strip())
                    i = k
            add("figure", caption=cap, file=img.group("src"))
            i += 1
            continue

        # list
        if re.match(r"^([-*+]|\d+[.)])\s+", stripped):
            items, j = [], i
            while j < n and (re.match(r"^([-*+]|\d+[.)])\s+", lines[j].strip())
                             or (lines[j].startswith(("  ", "\t")) and lines[j].strip())):
                s = lines[j].strip()
                if re.match(r"^([-*+]|\d+[.)])\s+", s):
                    items.append(clean_inline(re.sub(r"^([-*+]|\d+[.)])\s+", "", s)))
                elif items:
                    items[-1] += " " + clean_inline(s)
                j += 1
            add("list", ordered=bool(re.match(r"^\d+[.)]", stripped)), items=items)
            i = j
            continue

        # paragraph
        para, j = [], i
        while j < n and lines[j].strip() and not re.match(
                r"^(#{1,6}\s|\||\+[-=+]+\+|```|~~~|\$\$|:::)", lines[j].strip()):
            para.append(lines[j].strip())
            j += 1
        text = clean_inline(" ".join(para))
        if text:
            add("paragraph", text=text, citations=find_citations(text))
        i = j if j > i else i + 1

    return blocks


def parse_table(lines: list) -> list:
    rows = []
    for ln in lines:
        s = ln.strip()
        if not s.startswith("|"):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if all(re.fullmatch(r":?-{2,}:?", c or "-") for c in cells if c != ""):
            continue  # alignment rule
        rows.append([clean_inline(c) for c in cells])
    return rows


def clean_inline(text: str) -> str:
    """Remove pandoc markup scaffolding without touching author content."""
    text = re.sub(r"\[([^\]]*)\]\{[^}]*\}", r"\1", text)   # spans
    text = ATTR_RE.sub("", text)
    # pandoc escapes punctuation on the way out; undo it without touching "\\"
    text = re.sub(r"(?<!\\)\\([\[\]#$%&_{}~^*`<>!\"'.+()|@/:;,-])", r"\1", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def find_citations(text: str) -> list:
    found = []
    for pat in CITE_PATTERNS:
        for m in pat.finditer(text):
            for key in re.split(r"[;,]", m.group(1)):
                key = key.strip()
                if key and key not in found:
                    found.append(key)
    return found


# --------------------------------------------------------------------------
# stage 3: blocks -> manuscript IR
# --------------------------------------------------------------------------

def section_of(blocks: list, idx: int) -> str:
    for k in range(idx, -1, -1):
        if blocks[k]["type"] == "heading":
            return blocks[k]["text"]
    return ""


def build_ir(src: Path, fmt: str, blocks: list, warnings: list,
             meta: dict | None = None) -> dict:
    meta = meta or {}
    front = {"title": None, "authors": [], "affiliations": [],
             "abstract": None, "keywords": []}

    # document metadata wins over heuristics: it is what the source declared
    if meta.get("title"):
        front["title"] = clean_inline(str(meta["title"]))
    author = meta.get("author")
    if isinstance(author, list):
        front["authors"] = [clean_inline(a) for a in author]
    elif isinstance(author, str):
        front["authors"] = [clean_inline(author)]
    if meta.get("abstract"):
        front["abstract"] = clean_inline(str(meta["abstract"]))
    if meta.get("keywords"):
        kw = meta["keywords"]
        front["keywords"] = ([clean_inline(k) for k in kw] if isinstance(kw, list)
                             else [k.strip() for k in re.split(r"[;,]", kw) if k.strip()])
    back = {"references": [], "acknowledgements": None}

    headings = [(i, b) for i, b in enumerate(blocks) if b["type"] == "heading"]
    if front["title"] is None and headings:
        first = headings[0]
        if first[1]["level"] == 1 and first[0] <= 2 and \
                first[1]["text"].lower().strip() not in HEADING_WORDS:
            front["title"] = first[1]["text"]
    if front["title"] is None:
        for b in blocks[:3]:
            if b["type"] == "paragraph" and len(b["text"].split()) <= 30:
                front["title"] = b["text"]
                break

    def section_body(names, level_stop=True):
        out = []
        for i, b in enumerate(blocks):
            if b["type"] == "heading" and b["text"].lower().strip(" .:0123456789") in names:
                lvl = b["level"]
                for c in blocks[i + 1:]:
                    if c["type"] == "heading" and (not level_stop or c["level"] <= lvl):
                        break
                    out.append(c)
                break
        return out

    abs_blocks = section_body({"abstract"}) if not front["abstract"] else []
    if abs_blocks:
        front["abstract"] = "\n\n".join(
            b.get("text", "") for b in abs_blocks if b["type"] == "paragraph").strip() or None

    kw_blocks = [] if front["keywords"] else section_body(
        {"keywords", "key words", "index terms"})
    for b in kw_blocks:
        if b["type"] == "paragraph":
            front["keywords"] = [k.strip() for k in re.split(r"[;,]", b["text"]) if k.strip()]
            break
        if b["type"] == "list":
            front["keywords"] = list(b["items"])
            break
    if not front["keywords"]:
        for b in blocks[:40]:
            if b["type"] != "paragraph":
                continue
            # tolerate markdown emphasis around the label, e.g. "**Keywords:**"
            probe = b["text"].lstrip("*_ ")
            if re.match(r"^(keywords|key words|index terms)\b[*_ ]*\s*[:\-]", probe, re.I):
                tail = re.split(r"[:\-]", probe, 1)[1].lstrip("*_ ")
                front["keywords"] = [k.strip() for k in re.split(r"[;,]", tail) if k.strip()]
                break

    ref_blocks = section_body({"references", "bibliography", "references cited"}, level_stop=False)
    for b in ref_blocks:
        if b["type"] == "list":
            back["references"] += [{"raw": it} for it in b["items"]]
        elif b["type"] == "paragraph":
            back["references"].append({"raw": b["text"]})
    ack = section_body({"acknowledgements", "acknowledgments"})
    if ack:
        back["acknowledgements"] = "\n\n".join(
            b.get("text", "") for b in ack if b["type"] == "paragraph").strip() or None

    for i, b in enumerate(blocks):
        b["section"] = section_of(blocks, i)

    words = sum(len(b.get("text", "").split())
                for b in blocks if b["type"] in ("paragraph", "list", "heading"))
    words += sum(len(" ".join(b.get("items", [])).split())
                 for b in blocks if b["type"] == "list")

    cites = []
    for b in blocks:
        for c in b.get("citations", []):
            if c not in cites:
                cites.append(c)

    stats = {
        "words": words,
        "blocks": len(blocks),
        "headings": sum(1 for b in blocks if b["type"] == "heading"),
        "paragraphs": sum(1 for b in blocks if b["type"] == "paragraph"),
        "figures": sum(1 for b in blocks if b["type"] == "figure"),
        "tables": sum(1 for b in blocks if b["type"] == "table"),
        "equations": sum(1 for b in blocks if b["type"] == "equation"),
        "references": len(back["references"]),
        "distinct_citation_markers": len(cites),
    }

    if stats["figures"] == 0:
        warn(warnings, "no figures detected; confirm the source really has none")
    if stats["references"] == 0:
        warn(warnings, "no reference list detected; check the heading name used")

    return {
        "source": {
            "path": str(src),
            "format": fmt or "text",
            "lossy": fmt == "pdf",
            "warnings": warnings,
        },
        "front_matter": front,
        "blocks": blocks,
        "back_matter": back,
        "stats": stats,
    }


def write_inventory(ir: dict, path: Path) -> None:
    s = ir["stats"]
    lines = [
        "# Manuscript inventory", "",
        "| Field | Value |", "|---|---|",
        "| Source | `%s` |" % ir["source"]["path"],
        "| Format | %s%s |" % (ir["source"]["format"],
                               " (LOSSY)" if ir["source"]["lossy"] else ""),
        "| Title | %s |" % (ir["front_matter"]["title"] or "NOT DETECTED"),
        "| Abstract | %s |" % ("%d words" % len(ir["front_matter"]["abstract"].split())
                               if ir["front_matter"]["abstract"] else "NOT DETECTED"),
        "| Keywords | %s |" % (", ".join(ir["front_matter"]["keywords"]) or "NOT DETECTED"),
    ]
    for k, v in s.items():
        lines.append("| %s | %s |" % (k.replace("_", " ").capitalize(), v))
    lines += ["", "## Section outline", ""]
    for b in ir["blocks"]:
        if b["type"] == "heading":
            lines.append("%s- %s" % ("  " * (b["level"] - 1), b["text"]))
    if ir["source"]["warnings"]:
        lines += ["", "## Warnings", ""]
        lines += ["- " + w for w in ir["source"]["warnings"]]
    lines += ["", "## Figures", ""]
    for b in ir["blocks"]:
        if b["type"] == "figure":
            lines.append("- `%s` : %s" % (b.get("file", "?"), b.get("caption") or "NO CAPTION"))
    lines += ["", "## Tables", ""]
    for b in ir["blocks"]:
        if b["type"] == "table":
            g = b.get("grid") or []
            lines.append("- %d rows x %d cols : %s"
                         % (len(g), len(g[0]) if g else 0, b.get("caption") or "NO CAPTION"))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input")
    ap.add_argument("-o", "--outdir", default="build")
    ap.add_argument("--format", default="auto",
                    help="override input format detection (tex, docx, pdf, md, odt, rtf, html)")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    src = Path(args.input)
    if not src.exists():
        print("input not found: %s" % src, file=sys.stderr)
        return 2

    if args.format != "auto":
        fmt = {"tex": "latex", "md": "markdown"}.get(args.format, args.format)
    else:
        ext = src.suffix.lower()
        if ext not in PANDOC_FORMATS:
            print("unsupported extension %s; pass --format" % ext, file=sys.stderr)
            return 2
        fmt = "pdf" if ext == ".pdf" else PANDOC_FORMATS[ext]

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    media = outdir / "media"

    warnings: list = []
    md = to_markdown(src, fmt, media, warnings)
    (outdir / "extracted.md").write_text(md, encoding="utf-8")
    meta, body = split_front_matter(md)
    blocks = parse_markdown(body)
    ir = build_ir(src, fmt, blocks, warnings, meta)
    ir["source"]["metadata"] = meta

    assets = []
    if media.exists():
        assets = sorted(str(p.relative_to(outdir)) for p in media.rglob("*") if p.is_file())
    ir["assets"] = assets

    (outdir / "manuscript.json").write_text(
        json.dumps(ir, indent=2, ensure_ascii=False), encoding="utf-8")
    write_inventory(ir, outdir / "inventory.md")

    if not args.quiet:
        s = ir["stats"]
        print("wrote %s/manuscript.json, inventory.md, media/ (%d files)"
              % (outdir, len(assets)))
        print("words=%d sections=%d figures=%d tables=%d equations=%d references=%d"
              % (s["words"], s["headings"], s["figures"], s["tables"],
                 s["equations"], s["references"]))
        for w in warnings:
            print("WARNING: " + w)
    return 0


if __name__ == "__main__":
    sys.exit(main())
