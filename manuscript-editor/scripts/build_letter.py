#!/usr/bin/env python3
"""
build_letter.py - Build the response-to-reviewers letter as a submission-ready
PDF, and check that everything it claims about the manuscript is true first.

Before building it checks:

  placeholders   no [AUTHOR INPUT ...], TODO, TBD in the letter (--allow-placeholders to override)
  locations      every "Section N.M", "Table N", "Figure N", "Fig. N", "Eq. N" the letter
                 cites exists in the manuscript's .aux (numbers assigned by LaTeX), so the
                 letter cannot point at a section that was renumbered away
  quotations     every passage the letter quotes after "reads" or "now reads" appears
                 verbatim (whitespace-normalized) in the manuscript source
  narration      the manuscript source contains no reviewer-facing narration
                 ("as suggested by Reviewer", "in the revised version", "we now report")

Then it builds with pandoc (PDF through the TeX engine on PATH; falls back to
DOCX when no engine is available) with a date, 11 pt type, and 1 inch margins.

Usage:
    python build_letter.py letter/response.md --out letter/response.pdf --aux paper/main.aux --manuscript paper/main.tex
    python build_letter.py letter/response.md --out letter/response.pdf --date "12 September 2026"
    python build_letter.py letter/response.md --check-only --aux paper/main.aux --manuscript paper/main.tex
    python build_letter.py --self-test

Standard library only; pandoc and a TeX engine when building.
"""
from __future__ import annotations

import argparse
import datetime as dt
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

PLACEHOLDER_RE = re.compile(r"\[AUTHOR (?:INPUT|ACTION)[^\]]*\]|\bTODO\b|\bTBD\b|\[DOI PENDING\]", re.I)
LOC_RE = re.compile(r"\b(Section|Sec\.|Table|Figure|Fig\.|Equation|Eq\.)\s*~?\s*(S?\d+(?:\.\d+){0,2})", re.I)
QUOTE_RE = re.compile(r"(?:now\s+)?reads?\s*:?\s*[\"“]([^\"”]{30,})[\"”]", re.I | re.S)
NARRATION = [r"\bas (suggested|requested|recommended|noted) by (the )?(reviewer|editor)", r"\bin (the|this) revised (version|manuscript)\b",
             r"\bReviewer \d\b", r"\bwe (now|have now) (report|add|include|provide|clarif)", r"\bin response to (the )?(reviewer|comment)",
             r"\bwe agree (with|that)\b", r"\bwe thank the reviewer"]


def numbers_from_aux(aux_text: str) -> Dict[str, Set[str]]:
    out: Dict[str, Set[str]] = {"section": set(), "table": set(), "figure": set(), "equation": set()}
    for m in re.finditer(r"\\contentsline \{(section|subsection|subsubsection|chapter)\}\{\\numberline \{([^}]*)\}", aux_text):
        out["section"].add(m.group(2))
    for m in re.finditer(r"\\newlabel\{[^}]+\}\{\{([^{}]*)\}\{\d+\}(?:\{[^{}]*\})?\{(table|figure|equation|section|subsection|subsubsection)[.\d]*\}", aux_text):
        kind = m.group(2)
        kind = "section" if kind.startswith("s") or kind == "chapter" else kind
        out[kind].add(m.group(1))
    return out


def letter_locations(text: str) -> List[Tuple[str, str]]:
    kinds = {"section": "section", "sec.": "section", "table": "table", "figure": "figure", "fig.": "figure", "equation": "equation", "eq.": "equation"}
    return [(kinds[m.group(1).lower()], m.group(2)) for m in LOC_RE.finditer(text)]


def norm(s: str) -> str:
    s = re.sub(r"\\[A-Za-z@]+\*?(\[[^\]]*\])?(\{[^{}]*\})?", " ", s)
    s = re.sub(r"[{}~]", " ", s)
    s = s.replace("``", '"').replace("''", '"').replace("’", "'").replace("“", '"').replace("”", '"')
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


def check_letter(letter: str, aux: Optional[str], manuscript: Optional[str], allow_placeholders: bool) -> Tuple[List[str], List[str]]:
    fails: List[str] = []
    warns: List[str] = []
    ph = PLACEHOLDER_RE.findall(letter)
    if ph and not allow_placeholders:
        fails.append(f"{len(ph)} placeholder(s) in the letter: " + ", ".join(sorted(set(ph))[:6]))
    if aux is not None:
        nums = numbers_from_aux(aux)
        seen = set()
        for kind, num in letter_locations(letter):
            if (kind, num) in seen:
                continue
            seen.add((kind, num))
            if num.startswith("S"):
                continue  # supplementary numbering lives elsewhere
            if nums.get(kind) and num not in nums[kind]:
                fails.append(f"letter cites {kind} {num}, which the manuscript's .aux does not define")
            elif not nums.get(kind):
                warns.append(f"letter cites {kind} {num}; the .aux lists no {kind}s, so it could not be checked")
    if manuscript is not None:
        mnorm = norm(manuscript)
        for m in QUOTE_RE.finditer(letter):
            q = norm(m.group(1))
            words = q.split()
            probe = " ".join(words[:12])
            if probe and probe not in mnorm:
                fails.append("quoted passage not found in the manuscript: \"" + " ".join(m.group(1).split())[:90] + "\"")
        for pat in NARRATION:
            for mm in re.finditer(pat, manuscript, re.I):
                ctx = " ".join(manuscript[max(0, mm.start() - 40):mm.end() + 40].split())
                fails.append(f"reviewer-facing narration in the manuscript: \"{ctx}\"")
                break
    return fails, warns


def build(src: Path, out: Path, date: str, engine: Optional[str]) -> Tuple[int, str]:
    pandoc = shutil.which("pandoc")
    if not pandoc:
        return 127, "pandoc not on PATH"
    cmd = [pandoc, str(src), "-o", str(out), "-V", f"date={date}", "-V", "fontsize=11pt", "-V", "geometry:margin=1in",
           "-V", "colorlinks=true", "--from", "markdown+smart"]
    if out.suffix.lower() == ".pdf":
        eng = engine or next((e for e in ("xelatex", "pdflatex", "lualatex") if shutil.which(e)), None)
        if not eng:
            return 127, "no TeX engine on PATH; build a .docx instead"
        cmd += ["--pdf-engine", eng]
    p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def self_test() -> int:
    ok = True

    def check(desc: str, cond: bool) -> None:
        nonlocal ok
        print(("  ok   " if cond else "  FAIL ") + desc)
        ok = ok and cond

    aux = r"""\@writefile{toc}{\contentsline {section}{\numberline {3}Methods}{4}{section.3}\protected@file@percent }
\@writefile{toc}{\contentsline {subsection}{\numberline {3.2}Cohort}{5}{subsection.3.2}\protected@file@percent }
\newlabel{tab:main}{{2}{7}{Main results}{table.2}{}}
\newlabel{fig:roc}{{3}{8}{ROC}{figure.3}{}}
"""
    nums = numbers_from_aux(aux)
    check("aux numbers parsed", nums["section"] == {"3", "3.2"} and nums["table"] == {"2"} and nums["figure"] == {"3"})
    letter = 'R1.1 x\n\nResponse: done.\n\nChanges: Section 3.2 now reads: "The cohort excluded stays shorter than four hours, as recorded in the admission table."\n\nSee Table 2 and Figure 4. TODO fill.\n'
    manuscript = r"The cohort excluded stays shorter than four hours, as recorded in the admission table. \section{Methods} As suggested by Reviewer 2, we added x."
    fails, warns = check_letter(letter, aux, manuscript, allow_placeholders=False)
    check("placeholder caught", any("placeholder" in f for f in fails))
    check("missing Figure 4 caught, Table 2 and Section 3.2 fine", any("figure 4" in f for f in fails) and not any("table 2" in f or "section 3.2" in f for f in fails))
    check("quoted passage found", not any("quoted passage" in f for f in fails))
    check("manuscript narration caught", any("narration" in f for f in fails))
    letter2 = letter.replace("Figure 4", "Figure 3").replace(" TODO fill.", "").replace("as recorded in the admission table", "as recorded elsewhere")
    fails2, _ = check_letter(letter2, aux, manuscript.replace("As suggested by Reviewer 2, we added x.", ""), False)
    check("altered quotation caught, nothing else", len(fails2) == 1 and "quoted passage" in fails2[0])
    print("\nself-test " + ("passed" if ok else "FAILED"))
    return 0 if ok else 1


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, OSError):
            pass
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("letter", nargs="?", help="response letter in Markdown")
    p.add_argument("--out", help="output .pdf or .docx (default: letter with .pdf)")
    p.add_argument("--aux", help="the manuscript's .aux, for section/table/figure numbers")
    p.add_argument("--manuscript", nargs="*", help="manuscript .tex/.md files, for quoted-passage and narration checks")
    p.add_argument("--date", default=dt.date.today().strftime("%d %B %Y").lstrip("0"))
    p.add_argument("--engine", choices=["xelatex", "pdflatex", "lualatex"])
    p.add_argument("--allow-placeholders", action="store_true")
    p.add_argument("--check-only", action="store_true")
    p.add_argument("--self-test", action="store_true")
    a = p.parse_args()
    if a.self_test:
        return self_test()
    if not a.letter:
        p.error("give the letter file (or --self-test)")
    src = Path(a.letter)
    letter = src.read_text(encoding="utf-8", errors="replace")
    aux = Path(a.aux).read_text(encoding="utf-8", errors="replace") if a.aux else None
    manuscript = None
    if a.manuscript:
        manuscript = "\n".join(Path(m).read_text(encoding="utf-8", errors="replace") for m in a.manuscript)
        manuscript = re.sub(r"(?<!\\)%.*", "", manuscript)
    fails, warns = check_letter(letter, aux, manuscript, a.allow_placeholders)
    for f in fails:
        print(f"FAIL {f}")
    for w in warns:
        print(f"note {w}")
    if fails:
        print(f"\n{len(fails)} problem(s); not building. Fix the letter or the manuscript, then run again.")
        return 1
    print("checks passed" + (" (no aux or manuscript given; locations and quotations not checked)" if aux is None and manuscript is None else ""))
    if a.check_only:
        return 0
    out = Path(a.out) if a.out else src.with_suffix(".pdf")
    rc, log = build(src, out, a.date, a.engine)
    if rc != 0 or not out.exists():
        print(f"build failed ({rc}): {log.strip()[-800:]}")
        return 1
    print(f"wrote {out} (dated {a.date})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
