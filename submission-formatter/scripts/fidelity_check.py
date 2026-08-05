#!/usr/bin/env python3
"""Verify that a reformatted manuscript still says exactly what the source said.

Compares the source (IR json, or any readable document) against the built output
along four axes:

    sentences   which sentences were dropped, added, or altered
    numbers     every numeric token, as a multiset, including units and percents
    citations   citation markers and \\cite keys
    structure   figure, table, and equation counts

Exit status is 0 when the output is within thresholds, 1 when drift needs
attention, 2 on usage errors. Drift is not automatically a defect: template
headings and restyled citation markers legitimately appear as differences. The
point is that every difference is surfaced and consciously resolved.

Usage:
    python fidelity_check.py --source build/manuscript.json --output build/main.tex
    python fidelity_check.py --source paper.docx --output main.pdf --json report.json
    python fidelity_check.py --source a.json --output b.tex --ignore-added ignore.txt

`--ignore-added` takes a file of regular expressions, one per line; added output
sentences matching any of them (template boilerplate, class notices) are excluded
from the added list.
"""

from __future__ import annotations

import argparse
import difflib
import json
import re
import shutil
import subprocess
import sys
import unicodedata
from collections import Counter
from pathlib import Path

NUM_RE = re.compile(r"[-+]?\d[\d,]*(?:\.\d+)?(?:\s*[×xeE]\s*10\^?-?\d+)?\s*%?")
CITE_KEY_RE = re.compile(r"\\cite[a-zA-Z]*\s*(?:\[[^\]]*\])*\{([^}]*)\}")
CITE_NUM_RE = re.compile(r"\[(\d+(?:\s*[-,–]\s*\d+)*)\]")
SENT_SPLIT_RE = re.compile(r"(?<=[.!?])\s+(?=[A-Z(\[$\\])")

DEFAULT_IGNORE = [
    r"^\s*$",
    r"^\d+$",
    r"^(figure|table|fig\.|tab\.)\s*\d+\.?$",
    r"^(preprint|submitted to|manuscript|draft)\b",
]


def have(tool: str) -> bool:
    return shutil.which(tool) is not None


def strip_yaml_keys(text: str) -> str:
    """Drop pandoc's YAML metadata scaffolding while keeping its values, so the
    word count is not inflated by keys the document does not contain."""
    keys = r"(title|subtitle|author|date|abstract|keywords|institute|thanks|bibliography)"
    text = re.sub(r"(?m)^---\s*$", "", text)
    text = re.sub(r"(?m)^%s:\s*\|?\s*$" % keys, "", text)
    text = re.sub(r"(?m)^%s:\s*" % keys, "", text)
    return text


def unescape(text: str) -> str:
    r"""Undo LaTeX and markdown punctuation escaping so that an escaped percent
    sign compares equal to a bare one. A doubled backslash is left alone: it is
    a line break, not an escape."""
    return re.sub(r"(?<!\\)\\([%&$#_{}\[\]*`~^<>])", r"\1", text)


READER_NOTES: list = []


def read_text(path: Path) -> str:
    """Get plain text out of whatever this file is."""
    ext = path.suffix.lower()

    if ext == ".json":
        ir = json.loads(path.read_text(encoding="utf-8"))
        return unescape(ir_to_text(ir))

    if ext == ".pdf":
        if have("pdftotext"):
            p = subprocess.run(["pdftotext", "-nopgbrk", str(path), "-"],
                               capture_output=True, text=True,
                           encoding="utf-8", errors="replace")
            if p.returncode == 0 and p.stdout.strip():
                return dehyphenate(p.stdout)
        try:
            from pypdf import PdfReader  # type: ignore
            return dehyphenate("\n".join((pg.extract_text() or "")
                                         for pg in PdfReader(str(path)).pages))
        except Exception as exc:
            raise SystemExit("cannot read %s: %s" % (path, exc))

    if ext in (".txt", ".md", ".markdown"):
        return unescape(path.read_text(encoding="utf-8", errors="replace"))

    fmt = {".tex": "latex", ".docx": "docx", ".odt": "odt",
           ".rtf": "rtf", ".html": "html", ".htm": "html"}.get(ext)
    if fmt and have("pandoc"):
        # --standalone matters: without it pandoc drops title, author, and the
        # abstract environment into metadata and they vanish from the output,
        # which would look like catastrophic content loss
        # markdown rather than plain, and --standalone: pandoc routes title,
        # author, and the abstract environment into metadata, and the plain
        # writer drops them, which would look like catastrophic content loss
        p = subprocess.run(["pandoc", "-f", fmt, "-t", "markdown", "--wrap=none",
                            "--standalone", str(path)],
                           capture_output=True, text=True,
                           encoding="utf-8", errors="replace")
        if p.returncode == 0:
            return unescape(strip_yaml_keys(p.stdout))
        p = subprocess.run(["pandoc", "-f", fmt, "-t", "plain", "--wrap=none", str(path)],
                           capture_output=True, text=True,
                           encoding="utf-8", errors="replace")
        if p.returncode == 0:
            return unescape(p.stdout)
    if ext == ".tex":
        # A regex stripper is not a LaTeX parser: it loses environments the
        # class defines and anything the reader would have routed into
        # metadata. Drift measured against it is a floor, so say so rather than
        # letting a reader failure surface as missing content.
        READER_NOTES.append(
            "%s was read with the fallback LaTeX stripper because pandoc could "
            "not parse it. Abstract text, custom environments, and macro-heavy "
            "passages may be absent from this side of the comparison, so treat "
            "reported drift as an upper bound and verify against the file."
            % path.name)
        return unescape(strip_latex(path.read_text(encoding="utf-8", errors="replace")))
    raise SystemExit("no reader available for %s (install pandoc)" % path)


def ir_to_text(ir: dict) -> str:
    """Flatten the IR to text. Front matter is derived from blocks, so it is
    only emitted when it is not already carried by a block."""
    parts = []
    fm = ir.get("front_matter", {})
    seen = {normalize(b.get("text", "")) for b in ir.get("blocks", []) if b.get("text")}
    for b in ir.get("blocks", []):
        for item in b.get("items", []) or []:
            seen.add(normalize(item))
    for key in ("title", "abstract"):
        val = fm.get(key)
        if val and not any(normalize(s) in seen for s in val.split("\n\n")):
            parts.append(val)
    if fm.get("keywords"):
        kw = ", ".join(fm["keywords"])
        if normalize(kw) not in seen:
            parts.append(kw)
    for b in ir.get("blocks", []):
        t = b.get("type")
        if t in ("heading", "paragraph"):
            parts.append(b.get("text", ""))
        elif t == "list":
            parts.extend(b.get("items", []))
        elif t == "table":
            for row in b.get("grid") or []:
                parts.append(" ".join(row))
            if b.get("caption"):
                parts.append(b["caption"])
        elif t == "figure":
            if b.get("caption"):
                parts.append(b["caption"])
        elif t == "equation":
            parts.append(b.get("latex", ""))
    for ref in ir.get("back_matter", {}).get("references", []):
        raw = ref.get("raw", "")
        if raw and normalize(raw) not in seen:
            parts.append(raw)
    return "\n\n".join(p for p in parts if p)


def strip_latex(tex: str) -> str:
    tex = re.sub(r"(?m)^\s*%.*$", "", tex)
    tex = re.sub(r"\\begin\{(figure|table)\*?\}.*?\\end\{\1\*?\}", " ", tex, flags=re.S)
    tex = re.sub(r"\\[a-zA-Z@]+\*?(\[[^\]]*\])*(\{[^{}]*\})?", " ", tex)
    tex = re.sub(r"[{}$&~^_\\]", " ", tex)
    return tex


def dehyphenate(text: str) -> str:
    return re.sub(r"(\w)-\n(\w)", r"\1\2", text)


def normalize(s: str) -> str:
    s = unicodedata.normalize("NFKC", s)
    s = (s.replace("\u2018", "'").replace("\u2019", "'")
           .replace("\u201c", '"').replace("\u201d", '"')
           .replace("\u2013", "-").replace("\u2014", "-")
           .replace("\u00a0", " ").replace("\ufb01", "fi").replace("\ufb02", "fl"))
    s = re.sub(r"\\[a-zA-Z@]+\*?", " ", s)
    s = re.sub(r"[^\w\s.%()/+-]", " ", s)
    s = re.sub(r"\s+", " ", s)
    return s.strip().lower()


def sentences(text: str) -> list:
    text = dehyphenate(text)
    out = []
    for para in re.split(r"\n\s*\n", text):
        para = re.sub(r"\s*\n\s*", " ", para).strip()
        if not para:
            continue
        for s in SENT_SPLIT_RE.split(para):
            n = normalize(s)
            if len(n) >= 12:                  # ignore fragments and labels
                out.append(n)
    return out


STRUCTURAL_WORDS = {
    "table", "tables", "figure", "figures", "fig", "figs", "tab", "section",
    "sections", "appendix", "keywords", "keyword", "references", "bibliography",
    "abstract", "index", "terms", "et", "al", "pp", "vol", "no",
}


def tokens(text: str) -> Counter:
    """Content words, grouping-invariant. Numbers are audited separately, and
    structural vocabulary is excluded because templates legitimately add it."""
    out = []
    for tok in normalize(text).split():
        tok = tok.strip(".,;:()/-%")
        if len(tok) < 2 or tok in STRUCTURAL_WORDS:
            continue
        if re.fullmatch(r"[\d.%/+-]+", tok):
            continue
        out.append(tok)
    return Counter(out)


def numbers(text: str) -> Counter:
    vals = []
    for m in NUM_RE.finditer(text):
        tok = re.sub(r"[,\s]", "", m.group(0))
        if len(tok.strip("%+-")) <= 4 and re.fullmatch(r"[-+]?\d{1,4}", tok):
            # bare small integers are dominated by citation markers, section
            # numbers, and figure numbers; counted separately below
            continue
        vals.append(tok)
    return Counter(vals)


def citations(text: str) -> Counter:
    keys = []
    for m in CITE_KEY_RE.finditer(text):
        keys += [k.strip() for k in m.group(1).split(",") if k.strip()]
    if keys:
        return Counter(keys)
    for m in CITE_NUM_RE.finditer(text):
        keys += [k.strip() for k in re.split(r"[,;]", m.group(1)) if k.strip()]
    return Counter(keys)


def structure(text: str) -> dict:
    return {
        "figure_captions": len(re.findall(r"(?mi)^\s*(?:fig(?:ure)?\.?|\\caption)\s*\d*", text)),
        "table_captions": len(re.findall(r"(?mi)^\s*tab(?:le)?\.?\s*\d", text)),
        "equations": len(re.findall(r"\\begin\{(?:equation|align|gather|eqnarray)", text))
                     + len(re.findall(r"\$\$", text)) // 2,
    }


def load_ignore(path: str | None) -> list:
    pats = list(DEFAULT_IGNORE)
    if path:
        pats += [ln.strip() for ln in Path(path).read_text().splitlines()
                 if ln.strip() and not ln.startswith("#")]
    return [re.compile(p, re.I) for p in pats]


def diff_sentences(src: list, out: list, ignore: list):
    sm = difflib.SequenceMatcher(a=src, b=out, autojunk=False)
    missing, added, altered = [], [], []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "delete":
            missing += src[i1:i2]
        elif tag == "insert":
            added += out[j1:j2]
        elif tag == "replace":
            for a in src[i1:i2]:
                best, score = None, 0.0
                for b in out[j1:j2]:
                    r = difflib.SequenceMatcher(a=a, b=b).ratio()
                    if r > score:
                        best, score = b, r
                if score >= 0.90:
                    altered.append({"source": a, "output": best, "similarity": round(score, 3)})
                else:
                    missing.append(a)
            matched = {x["output"] for x in altered}
            added += [b for b in out[j1:j2] if b not in matched]
    added = [a for a in added if not any(p.search(a) for p in ignore)]
    return missing, added, altered


def split_missing(missing: list, token_missing: Counter):
    """A sentence whose words all survive somewhere in the output was regrouped
    (a table reflowed, a paragraph merged), not lost. Only sentences carrying
    genuinely absent words are content loss."""
    lost, regrouped = [], []
    for sent in missing:
        if any(t in token_missing for t in tokens(sent)):
            lost.append(sent)
        else:
            regrouped.append(sent)
    return lost, regrouped


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--source", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--json", dest="json_out")
    ap.add_argument("--ignore-added")
    ap.add_argument("--max-missing", type=int, default=0,
                    help="missing sentences tolerated before failing (default 0)")
    ap.add_argument("--show", type=int, default=8, help="examples printed per category")
    args = ap.parse_args()

    src_path, out_path = Path(args.source), Path(args.output)
    for p in (src_path, out_path):
        if not p.exists():
            print("not found: %s" % p, file=sys.stderr)
            return 2

    src_text, out_text = read_text(src_path), read_text(out_path)
    ignore = load_ignore(args.ignore_added)

    s_sent, o_sent = sentences(src_text), sentences(out_text)
    missing, added, altered = diff_sentences(s_sent, o_sent, ignore)

    s_tok, o_tok = tokens(src_text), tokens(out_text)
    tok_missing = s_tok - o_tok
    tok_added = o_tok - s_tok
    lost, regrouped = split_missing(missing, tok_missing)

    s_num, o_num = numbers(src_text), numbers(out_text)
    num_missing = s_num - o_num
    num_added = o_num - s_num

    s_cit, o_cit = citations(src_text), citations(out_text)
    cit_missing = s_cit - o_cit
    cit_added = o_cit - s_cit

    s_struct, o_struct = structure(src_text), structure(out_text)

    s_words, o_words = len(src_text.split()), len(out_text.split())

    report = {
        "source": str(src_path),
        "output": str(out_path),
        "words": {"source": s_words, "output": o_words,
                  "delta_pct": round(100.0 * (o_words - s_words) / max(s_words, 1), 2)},
        "sentences": {
            "source": len(s_sent), "output": len(o_sent),
            "lost": lost, "regrouped": regrouped, "added": added, "altered": altered,
        },
        "content_words": {"missing": dict(tok_missing), "added": dict(tok_added)},
        "numbers": {"missing": dict(num_missing), "added": dict(num_added)},
        "citations": {"source_distinct": len(s_cit), "output_distinct": len(o_cit),
                      "missing": dict(cit_missing), "added": dict(cit_added)},
        "structure": {"source": s_struct, "output": o_struct},
    }
    failed = (len(lost) > args.max_missing or bool(tok_missing) or bool(num_missing)
              or bool(cit_missing))
    report["status"] = "drift" if failed else "clean"

    if args.json_out:
        Path(args.json_out).write_text(json.dumps(report, indent=2, ensure_ascii=False),
                                       encoding="utf-8")

    print("fidelity check: %s -> %s" % (src_path.name, out_path.name))
    for note in READER_NOTES:
        print("  READER      %s" % note)
    print("  words       %d -> %d (%+0.2f%%)" % (s_words, o_words, report["words"]["delta_pct"]))
    print("  content     missing %d word tokens, added %d"
          % (sum(tok_missing.values()), sum(tok_added.values())))
    print("  sentences   %d -> %d | lost %d, regrouped %d, altered %d, added %d"
          % (len(s_sent), len(o_sent), len(lost), len(regrouped), len(altered), len(added)))
    print("  numbers     missing %d, added %d" % (sum(num_missing.values()), sum(num_added.values())))
    print("  citations   missing %d, added %d" % (sum(cit_missing.values()), sum(cit_added.values())))
    print("  structure   source %s" % s_struct)
    print("              output %s" % o_struct)

    def dump(label, items, fmt=lambda x: x):
        if not items:
            return
        print("\n%s (%d):" % (label, len(items)))
        for it in items[:args.show]:
            print("  - " + fmt(it)[:220])
        if len(items) > args.show:
            print("  ... %d more" % (len(items) - args.show))

    if tok_missing:
        dump("CONTENT WORDS missing from output", sorted(tok_missing.elements()))
    dump("LOST sentences (words absent from the output entirely)", lost)
    dump("REGROUPED sentences (words survive elsewhere; usually a reflowed table "
         "or merged paragraph, verify once)", regrouped)
    dump("ALTERED", altered,
         lambda x: "sim=%.3f\n    src: %s\n    out: %s" % (x["similarity"], x["source"][:160],
                                                           x["output"][:160]))
    dump("ADDED in output", added)
    if num_missing:
        dump("NUMERIC tokens missing", sorted(num_missing.elements()))
    if num_added:
        dump("NUMERIC tokens added", sorted(num_added.elements()))
    if cit_missing:
        dump("CITATIONS missing", sorted(cit_missing.elements()))

    print("\nstatus: %s" % report["status"].upper())
    if failed:
        print("resolve every item above: fix it in the output, or record a written "
              "justification in FORMAT_REPORT.md")
    return 1 if failed else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except BrokenPipeError:
        sys.exit(0)
