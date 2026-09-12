#!/usr/bin/env python3
"""
prose_lint.py - Count the mechanical tells of machine-written prose in a
manuscript, per section, so the tell sweep in research-paper-writing has
numbers instead of impressions.

It reads .md, .tex, and .txt, strips code, math, tables, citations, and
LaTeX commands, and reports:

  dashes        em and en dashes, and spaced or double hyphens used as dashes
  stock         stock vocabulary per 1,000 words (delve, leverage, robust,
                pivotal, landscape, underscore, showcase, ...), with the counts
  contrast      "not X but Y" and "it is not X, it is Y" constructions
  triads        sentences built on exactly three coordinated items
  openers       three or more consecutive paragraphs, or sentences, starting
                with the same word
  labels        list items that open with a bold label and a colon
  announce      sentences that announce the next point instead of making it
                ("In this section we", "It is worth noting", "Notably,")
  closers       one-sentence paragraphs of twelve words or fewer that follow
                a longer paragraph (aphoristic closers; review, not a fail)
  hedges        sentences carrying two or more hedges (may, might, could,
                potentially, possibly, arguably, perhaps, likely)
  residue       chatbot residue ("I hope this helps", "Great question")
  narration     revision narration in a manuscript ("in the revised version",
                "as suggested by the reviewer", "we now report")

It is a counter, not a judge: every line it reports is a candidate for the
read in SKILL.md. --strict exits 1 when a dash, chatbot residue, or revision
narration remains, since those three are never intended in a manuscript.

Usage:
    python prose_lint.py paper.md
    python prose_lint.py sections/*.md --report lint.md
    python prose_lint.py main.tex --strict
    python prose_lint.py paper.md --json lint.json
    python prose_lint.py paper.md --allow-dashes      # the author's own style uses them
    python prose_lint.py --self-test

Standard library only.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Dict, List, Tuple

STOCK = [
    "delve", "delves", "delving", "leverage", "leverages", "leveraging", "utilize", "utilizes",
    "utilizing", "utilization", "robust", "robustly", "pivotal", "crucial", "crucially", "landscape",
    "tapestry", "underscore", "underscores", "underscoring", "showcase", "showcases", "showcasing",
    "testament", "meticulous", "meticulously", "intricate", "intricacies", "interplay", "enduring",
    "vibrant", "fostering", "foster", "garner", "bolster", "bolstered", "seamless", "seamlessly",
    "groundbreaking", "revolutionary", "cutting-edge", "state-of-the-art", "paradigm",
    "unprecedented", "holistic", "synergy", "synergies", "vital", "notably", "importantly",
    "additionally", "furthermore", "moreover", "actually", "align", "aligns", "enhance", "enhances",
    "enhancing", "highlight", "highlights", "highlighting", "emphasize", "emphasizes",
    "emphasizing", "key", "valuable", "comprehensive", "novel",
]
STOCK_PHRASES = [
    r"sheds? light on", r"plays? a (vital|key|crucial|pivotal|significant) role", r"in order to",
    r"it is worth noting", r"it is important to note", r"a wide range of", r"in the realm of",
    r"at its core", r"the real question is", r"paves? the way", r"in today's", r"ever-evolving",
]
HEDGES = r"\b(may|might|could|potentially|possibly|arguably|perhaps|likely|seem(s|ed)? to|appear(s|ed)? to)\b"
ANNOUNCE = [
    r"^\s*in this (section|paper|work|article|chapter),? we", r"^\s*this (section|subsection|chapter) (describes|presents|discusses|introduces|outlines)",
    r"^\s*(the )?(remainder|rest) of (this|the) (paper|section) is organi[sz]ed", r"\bit is worth (noting|mentioning)\b",
    r"^\s*notably,", r"^\s*importantly,", r"^\s*interestingly,", r"\blet'?s (dive|explore|break)", r"\bhere'?s what\b",
]
RESIDUE = [r"i hope this helps", r"great question", r"certainly!", r"of course!", r"let me know if", r"would you like",
           r"as an ai", r"you'?re absolutely right"]
NARRATION = [r"\bin (the|this) revised (version|manuscript)\b", r"\bas (suggested|requested|recommended|noted) by (the )?(reviewer|editor)",
             r"\breviewer \d\b", r"\bwe (now|have now) (report|add|include|provide|clarif)", r"\bin response to (the )?(reviewer|comment)",
             r"\bwe agree (with|that)\b", r"\bwe thank the reviewer"]
CONTRAST = [r"\bnot (just|only|merely|simply) [^.;:]{1,80}\bbut\b", r"\b(is|are|was|were) not [^.;:,]{1,50}, (it|this|that|they) (is|are|was|were)\b",
            r"\bnot [^.;:,]{1,40}, but (rather )?\b", r"\brather than\b [^.;:]{1,40}, (it|this|we)\b"]

WORD = re.compile(r"[A-Za-z][A-Za-z'-]+")


# ---------------------------------------------------------------------------
# cleaning
# ---------------------------------------------------------------------------

def strip_tex(text: str) -> str:
    text = re.sub(r"(?<!\\)%.*", "", text)
    text = re.sub(r"\\begin\{(equation|align|gather|multline|eqnarray|displaymath|tabular|tabularx|longtable|table|figure|algorithm|lstlisting|verbatim|thebibliography)\*?\}.*?\\end\{\1\*?\}", " ", text, flags=re.S)
    text = re.sub(r"\$\$.*?\$\$", " ", text, flags=re.S)
    text = re.sub(r"\\\[.*?\\\]", " ", text, flags=re.S)
    text = re.sub(r"(?<!\\)\$[^$]*\$", " ", text)
    text = re.sub(r"\\(cite[tp]?|citet|citep|ref|cref|Cref|autoref|eqref|label|url|href|includegraphics|input|include|bibliography|bibliographystyle)\*?(\[[^\]]*\])?\{[^}]*\}", " ", text)
    text = re.sub(r"\\(section|subsection|subsubsection|paragraph|chapter)\*?\{([^}]*)\}", r"\n\n# \2\n\n", text)
    text = re.sub(r"\\(textbf|textit|emph|texttt|textsc)\{([^}]*)\}", r"\2", text)
    text = re.sub(r"\\[A-Za-z@]+\*?(\[[^\]]*\])?(\{[^}]*\})?", " ", text)
    text = text.replace("~", " ")
    return text


def strip_md(text: str) -> str:
    text = re.sub(r"^---\n.*?\n---\n", "", text, flags=re.S)
    text = re.sub(r"```.*?```", " ", text, flags=re.S)
    text = re.sub(r"`[^`\n]*`", " ", text)
    text = re.sub(r"^\s*\|.*$", "", text, flags=re.M)          # tables
    text = re.sub(r"^\s*(-{3,}|\*{3,}|_{3,})\s*$", "", text, flags=re.M)  # rules
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", text)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"https?://\S+", " ", text)
    text = re.sub(r"\$\$.*?\$\$", " ", text, flags=re.S)
    text = re.sub(r"\$[^$\n]*\$", " ", text)
    text = re.sub(r"\[[^\]]{1,40}\]", " ", text)                # [citekey]
    return text


def clean(text: str, suffix: str) -> str:
    return strip_tex(text) if suffix == ".tex" else strip_md(text)


def sections(text: str) -> List[Tuple[str, str]]:
    parts = re.split(r"^(#{1,3} .*)$", text, flags=re.M)
    out: List[Tuple[str, str]] = []
    if parts[0].strip():
        out.append(("(front)", parts[0]))
    for i in range(1, len(parts), 2):
        out.append((parts[i].lstrip("# ").strip(), parts[i + 1] if i + 1 < len(parts) else ""))
    return out or [("(all)", text)]


def paragraphs(text: str) -> List[str]:
    return [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip() and not p.strip().startswith("#")]


def sentences(text: str) -> List[str]:
    text = re.sub(r"\s+", " ", text)
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+(?=[A-Z(\"'])", text) if s.strip()]


# ---------------------------------------------------------------------------
# checks
# ---------------------------------------------------------------------------

def lint_section(name: str, body: str) -> Dict[str, object]:
    words = WORD.findall(body)
    n = max(len(words), 1)
    res: Dict[str, object] = {"section": name, "words": len(words)}

    dashes = [m.start() for m in re.finditer(r"[—–]|(?<=\S) -- (?=\S)| - (?=[a-z])", body)]
    res["dashes"] = len(dashes)
    res["dash_examples"] = [snippet(body, p) for p in dashes[:5]]

    stock_counts: Counter = Counter()
    low = body.lower()
    for w in STOCK:
        c = len(re.findall(r"\b" + re.escape(w) + r"\b", low))
        if c:
            stock_counts[w] += c
    for ph in STOCK_PHRASES:
        c = len(re.findall(ph, low))
        if c:
            stock_counts[ph] += c
    res["stock_per_1k"] = round(1000 * sum(stock_counts.values()) / n, 1)
    res["stock"] = dict(stock_counts.most_common(12))

    res["contrast"] = sum(len(re.findall(p, low)) for p in CONTRAST)
    res["contrast_examples"] = [m.group(0)[:100] for p in CONTRAST for m in re.finditer(p, body, re.I)][:5]

    tri = [s for s in sentences(body) if re.search(r"\b[\w-]+, [\w-]+,? and [\w-]+\b", s) and s.count(",") == 2]
    res["triads"] = len(tri)
    res["triad_examples"] = [t[:110] for t in tri[:4]]

    paras = paragraphs(body)
    firsts = [p.split()[0].strip("*_\"'(").lower() for p in paras if p.split()]
    runs = 0
    i = 0
    while i < len(firsts):
        j = i
        while j + 1 < len(firsts) and firsts[j + 1] == firsts[i]:
            j += 1
        if j - i + 1 >= 3:
            runs += 1
        i = j + 1
    sent_runs = 0
    for p in paras:
        sf = [s.split()[0].strip("*_\"'(").lower() for s in sentences(p) if s.split()]
        k = 0
        while k < len(sf):
            j = k
            while j + 1 < len(sf) and sf[j + 1] == sf[k]:
                j += 1
            if j - k + 1 >= 3:
                sent_runs += 1
            k = j + 1
    res["openers"] = runs + sent_runs

    res["labels"] = len(re.findall(r"^\s*[-*]\s+\*\*[^*]{1,60}:?\*\*:?", body, re.M))

    ann = [s for s in sentences(body) if any(re.search(p, s, re.I) for p in ANNOUNCE)]
    res["announce"] = len(ann)
    res["announce_examples"] = [s[:100] for s in ann[:4]]

    closers = 0
    closer_examples = []
    for prev, cur in zip(paras, paras[1:]):
        cw = cur.split()
        if len(cw) <= 12 and len(prev.split()) > 40 and cur.endswith(".") and len(sentences(cur)) == 1:
            closers += 1
            closer_examples.append(cur[:100])
    res["closers"] = closers
    res["closer_examples"] = closer_examples[:4]

    hs = [s for s in sentences(body) if len(re.findall(HEDGES, s, re.I)) >= 2]
    res["hedges"] = len(hs)
    res["hedge_examples"] = [s[:110] for s in hs[:4]]

    res["residue"] = sum(len(re.findall(p, low)) for p in RESIDUE)
    nar = [m.group(0) for p in NARRATION for m in re.finditer(p, body, re.I)]
    res["narration"] = len(nar)
    res["narration_examples"] = nar[:5]
    return res


def snippet(body: str, pos: int, width: int = 40) -> str:
    return re.sub(r"\s+", " ", body[max(0, pos - width):pos + width]).strip()


def lint_file(path: Path) -> List[Dict[str, object]]:
    text = clean(path.read_text(encoding="utf-8", errors="replace"), path.suffix.lower())
    return [lint_section(name, body) for name, body in sections(text)]


# ---------------------------------------------------------------------------
# report
# ---------------------------------------------------------------------------

COLS = ["words", "dashes", "stock_per_1k", "contrast", "triads", "openers", "labels", "announce", "closers", "hedges", "residue", "narration"]


def totals(rows: List[Dict[str, object]]) -> Dict[str, object]:
    t: Dict[str, object] = {"section": "TOTAL"}
    for c in COLS:
        if c == "stock_per_1k":
            continue
        t[c] = sum(int(r[c]) for r in rows)
    w = max(int(t["words"]), 1)
    stock_total = sum(sum(r["stock"].values()) for r in rows)  # type: ignore[union-attr]
    t["stock_per_1k"] = round(1000 * stock_total / w, 1)
    return t


def render(files: Dict[str, List[Dict[str, object]]], allow_dashes: bool) -> Tuple[str, bool]:
    lines = ["# Prose lint", ""]
    fail = False
    for fname, rows in files.items():
        lines.append(f"## {fname}")
        lines.append("")
        lines.append("| Section | Words | Dashes | Stock/1k | Contrast | Triads | Openers | Labels | Announce | Closers | Hedges | Residue | Narration |")
        lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
        allrows = rows + [totals(rows)]
        for r in allrows:
            lines.append("| " + str(r["section"])[:40] + " | " + " | ".join(str(r[c]) for c in COLS) + " |")
        lines.append("")
        t = allrows[-1]
        if (int(t["dashes"]) and not allow_dashes) or int(t["residue"]) or int(t["narration"]):
            fail = True
        stock: Counter = Counter()
        for r in rows:
            stock.update(r["stock"])  # type: ignore[arg-type]
        if stock:
            lines.append("Stock words: " + ", ".join(f"{w} ({c})" for w, c in stock.most_common(15)))
            lines.append("")
        for key, label in (("dash_examples", "Dashes"), ("contrast_examples", "Contrasts"), ("triad_examples", "Triads"),
                           ("announce_examples", "Announcing"), ("closer_examples", "Closers"), ("hedge_examples", "Hedge stacks"),
                           ("narration_examples", "Revision narration")):
            ex = [e for r in rows for e in r[key]][:8]  # type: ignore[union-attr]
            if ex:
                lines.append(f"{label}:")
                lines += [f"- {e}" for e in ex]
                lines.append("")
    lines.append("Read: dashes, residue, and revision narration are never intended in a manuscript and fail --strict. "
                 "Everything else is a count to read against the section; a Methods section with three real triads is fine, "
                 "a Discussion with twelve is a rhythm by rule.")
    return "\n".join(lines), fail


def self_test() -> int:
    ok = True

    def check(desc: str, cond: bool) -> None:
        nonlocal ok
        print(("  ok   " if cond else "  FAIL ") + desc)
        ok = ok and cond

    md = """# Introduction

The model is not just accurate but also fast — it leverages a robust pipeline. Notably, this is a pivotal result. It could potentially perhaps generalize.

This is a paragraph of more than forty words that goes on for a while so that the next one-liner counts as a closer; it keeps going and going with words words words words words words words words words words words words words words.

That is the real win.

The method uses speed, accuracy, and scale. The method is fast. The method is small.

- **Speed:** it is fast.

In the revised manuscript we now report the calibration index, as suggested by Reviewer 2.
"""
    rows = lint_file_text(md, ".md")
    r = rows[0]
    check("dash counted", r["dashes"] == 1)
    check("stock words counted", r["stock"].get("leverages", 0) == 1 and r["stock"].get("robust", 0) == 1)
    check("contrast counted", r["contrast"] >= 1)
    check("triad counted", r["triads"] >= 1)
    check("sentence openers run counted", r["openers"] >= 1)
    check("bold label counted", r["labels"] == 1)
    check("announcing counted", r["announce"] >= 1)
    check("closer counted", r["closers"] == 1)
    check("hedge stack counted", r["hedges"] == 1)
    check("revision narration counted", r["narration"] >= 2)
    tex = r"""\section{Methods}
We fit the model. % a comment with an em dash — ignored
\begin{table}\caption{A -- B}\end{table}
The rate was $x - y$ and the interval [1--2] in the table\cite{a--b}.
"""
    rows2 = lint_file_text(tex, ".tex")
    check("tex: dashes in comments, tables, math, cites ignored", rows2[0]["dashes"] == 0)
    check("tex: section heading found", rows2[0]["section"] == "Methods")
    print("\nself-test " + ("passed" if ok else "FAILED"))
    return 0 if ok else 1


def lint_file_text(text: str, suffix: str) -> List[Dict[str, object]]:
    return [lint_section(name, body) for name, body in sections(clean(text, suffix))]


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, OSError):
            pass
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("files", nargs="*")
    p.add_argument("--report", help="write the markdown report here")
    p.add_argument("--json", dest="json_path", help="write a JSON report here")
    p.add_argument("--strict", action="store_true", help="exit 1 if a dash, chatbot residue, or revision narration remains")
    p.add_argument("--allow-dashes", action="store_true", help="the author's own writing uses dashes; do not fail on them")
    p.add_argument("--self-test", action="store_true")
    a = p.parse_args()
    if a.self_test:
        return self_test()
    if not a.files:
        p.error("give at least one .md, .tex, or .txt file")
    files: Dict[str, List[Dict[str, object]]] = {}
    for f in a.files:
        path = Path(f)
        if not path.exists():
            print(f"error: {f} not found", file=sys.stderr)
            return 2
        files[str(path)] = lint_file(path)
    text, fail = render(files, a.allow_dashes)
    if a.report:
        Path(a.report).write_text(text, encoding="utf-8", newline="\n")
        print(f"wrote {a.report}")
    else:
        print(text)
    if a.json_path:
        Path(a.json_path).write_text(json.dumps(files, indent=2), encoding="utf-8")
    return 1 if (a.strict and fail) else 0


if __name__ == "__main__":
    raise SystemExit(main())
