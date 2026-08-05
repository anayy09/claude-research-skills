#!/usr/bin/env python3
"""Compile a LaTeX submission and package it, whether or not the build succeeds.

Publisher classes are usually absent from a minimal TeX installation, so a local
compile failure is a normal outcome, not a defect in the manuscript. This script
separates the two cases: it reports missing-dependency failures distinctly from
real LaTeX errors, and it always produces the submission archive so the author
can upload it or open it in Overleaf.

Usage:
    python compile_tex.py build/main.tex
    python compile_tex.py build/main.tex --package report/submission.zip
    python compile_tex.py build/main.tex --engine xelatex --outdir build/out
    python compile_tex.py build/main.tex --package sub.zip --no-compile

Exit status: 0 if the PDF was produced or only a missing dependency blocked it,
1 if the source itself has errors, 2 on usage errors.
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

PACKAGE_EXT = {".tex", ".cls", ".sty", ".bst", ".bib", ".bbl", ".pdf", ".png",
               ".jpg", ".jpeg", ".eps", ".tif", ".tiff", ".svg", ".txt"}

ERROR_RE = re.compile(r"^! (.+)$", re.M)
MISSING_FILE_RE = re.compile(r"File `([^']+)' not found|LaTeX Error: File `([^']+)' not found")
UNDEF_CTRL_RE = re.compile(r"Undefined control sequence")
CITE_WARN_RE = re.compile(r"Citation `([^']+)' (?:on page \d+ )?undefined")
REF_WARN_RE = re.compile(r"Reference `([^']+)' (?:on page \d+ )?undefined")
OVERFULL_RE = re.compile(r"Overfull \\hbox \(([\d.]+)pt too wide\)")


def have(tool: str) -> bool:
    return shutil.which(tool) is not None


def detect_engine(tex: str) -> str:
    """Pick the engine the source implies. pdflatex unless something forces otherwise."""
    if re.search(r"\\usepackage(\[[^\]]*\])?\{(fontspec|unicode-math|xeCJK|polyglossia)\}", tex):
        return "xelatex"
    if re.search(r"\\usepackage(\[[^\]]*\])?\{luacode|luatextra\}", tex):
        return "lualatex"
    return "pdflatex"


def documentclass(tex: str) -> str | None:
    m = re.search(r"\\documentclass\s*(?:\[[^\]]*\])?\s*\{([^}]*)\}", tex)
    return m.group(1) if m else None


def class_available(name: str, src_dir: Path) -> bool:
    if (src_dir / (name + ".cls")).exists():
        return True
    if not have("kpsewhich"):
        return False
    p = subprocess.run(["kpsewhich", name + ".cls"], capture_output=True, text=True)
    return p.returncode == 0 and bool(p.stdout.strip())


def triage(log: str) -> dict:
    missing = set()
    for m in MISSING_FILE_RE.finditer(log):
        missing.add(m.group(1) or m.group(2))
    return {
        "errors": ERROR_RE.findall(log)[:12],
        "missing_files": sorted(missing),
        "undefined_citations": sorted(set(CITE_WARN_RE.findall(log)))[:20],
        "undefined_references": sorted(set(REF_WARN_RE.findall(log)))[:20],
        "overfull_boxes": len(OVERFULL_RE.findall(log)),
    }


def collect_files(main: Path) -> list:
    """Everything the submission archive needs, from the main file's directory."""
    root = main.parent
    out = []
    for f in sorted(root.rglob("*")):
        if not f.is_file():
            continue
        if any(part in {"_build", ".git", "__pycache__"} for part in f.parts):
            continue
        if f.suffix.lower() in PACKAGE_EXT:
            out.append(f)
    return out


def make_zip(main: Path, dest: Path, extra_note: str) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    files = collect_files(main)
    with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in files:
            zf.write(f, f.relative_to(main.parent))
        zf.writestr("BUILD_NOTES.txt", extra_note)
    return dest


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("tex")
    ap.add_argument("--engine", default="auto",
                    choices=["auto", "pdflatex", "xelatex", "lualatex"])
    ap.add_argument("--outdir", default=None, help="build directory (default: alongside source)")
    ap.add_argument("--package", help="write the submission zip to this path")
    ap.add_argument("--no-compile", action="store_true", help="package only")
    ap.add_argument("--passes", type=int, default=0,
                    help="force N plain engine passes instead of latexmk")
    args = ap.parse_args()

    main_tex = Path(args.tex)
    if not main_tex.exists():
        print("not found: %s" % main_tex, file=sys.stderr)
        return 2

    source = main_tex.read_text(encoding="utf-8", errors="replace")
    engine = detect_engine(source) if args.engine == "auto" else args.engine
    cls = documentclass(source)
    available = class_available(cls, main_tex.parent) if cls else True

    print("main       %s" % main_tex)
    print("class      %s (%s)" % (cls, "available" if available else "NOT INSTALLED LOCALLY"))
    print("engine     %s" % engine)

    status, notes = "not built", []
    pdf = main_tex.with_suffix(".pdf")
    log_text = ""

    if args.no_compile:
        status = "skipped"
    elif not available:
        status = "blocked: missing document class"
        notes.append(
            "The document class '%s.cls' is not installed in this environment and is "
            "not bundled next to the source. This blocks the local build only. Upload "
            "the archive to Overleaf, or copy the class file from the publisher "
            "template into the same directory as the main .tex." % cls)
        print("\nlocal compile skipped: %s.cls not found" % cls)
    elif not have("latexmk") and not have(engine):
        status = "blocked: no TeX engine"
        notes.append("No TeX engine found in this environment.")
    else:
        # resolve: latexmk runs with cwd set to the source directory, so a
        # relative -outdir would be interpreted twice
        outdir = (Path(args.outdir) if args.outdir else main_tex.parent).resolve()
        outdir.mkdir(parents=True, exist_ok=True)
        if have("latexmk") and not args.passes:
            flag = {"pdflatex": "-pdf", "xelatex": "-xelatex", "lualatex": "-lualatex"}[engine]
            cmd = ["latexmk", flag, "-interaction=nonstopmode", "-file-line-error",
                   "-outdir=" + str(outdir), main_tex.name]
        else:
            cmd = None
        if cmd:
            proc = subprocess.run(cmd, cwd=main_tex.parent, capture_output=True, text=True)
            rc = proc.returncode
            log_text = proc.stdout + proc.stderr
        else:
            rc = 0
            for _ in range(max(args.passes, 3)):
                proc = subprocess.run(
                    [engine, "-interaction=nonstopmode", "-file-line-error",
                     "-output-directory", str(outdir), main_tex.name],
                    cwd=main_tex.parent, capture_output=True, text=True)
                log_text += proc.stdout
                rc = proc.returncode
        log_file = outdir / (main_tex.stem + ".log")
        if log_file.exists():
            log_text += log_file.read_text(encoding="utf-8", errors="replace")
        pdf = outdir / (main_tex.stem + ".pdf")
        status = "built" if pdf.exists() else "failed"

        t = triage(log_text)
        print("\nresult     %s%s" % (status, "  -> " + str(pdf) if pdf.exists() else ""))
        if t["missing_files"]:
            print("missing    %s" % ", ".join(t["missing_files"][:10]))
        if t["errors"]:
            print("errors:")
            for e in t["errors"]:
                print("  ! " + e[:160])
        if t["undefined_citations"]:
            print("undefined citations: %s" % ", ".join(t["undefined_citations"][:10]))
            notes.append("Undefined citations: run the bibliography pass, or check "
                         "that every \\cite key exists in the .bib file.")
        if t["undefined_references"]:
            print("undefined refs:      %s" % ", ".join(t["undefined_references"][:10]))
        if t["overfull_boxes"]:
            print("overfull hboxes:     %d (check for text running into the margin)"
                  % t["overfull_boxes"])

    if args.package:
        note = "\n".join([
            "Submission archive built by submission-formatter.",
            "main file: %s" % main_tex.name,
            "document class: %s" % cls,
            "engine: %s" % engine,
            "local build status: %s" % status,
            "",
        ] + notes)
        z = make_zip(main_tex, Path(args.package), note)
        print("\npackaged   %s (%d files)"
              % (z, len(collect_files(main_tex))))

    if status == "failed":
        print("\nthe source has real LaTeX errors: fix them before delivery")
        return 1
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except BrokenPipeError:
        sys.exit(0)
