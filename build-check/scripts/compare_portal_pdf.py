#!/usr/bin/env python3
"""Compare the PDF a submission portal built with the local build.

    python compare_portal_pdf.py local.pdf portal.pdf [--context 40] [--max 40]

Reports page counts, image counts, unresolved-reference marks, numbers and
words present in one file and absent from the other, and the first lines of
each file's first page. Exit code 1 when numbers from the local build are
missing in the portal copy, 0 otherwise. Needs PyMuPDF, or pdftotext on PATH.
"""
from __future__ import annotations

import argparse
import collections
import re
import shutil
import subprocess
import sys


def read_pdf(path: str):
    """Return (pages_text, image_count or None)."""
    try:
        import fitz  # PyMuPDF
    except ImportError:
        fitz = None
    if fitz is not None:
        doc = fitz.open(path)
        pages = [p.get_text("text") for p in doc]
        images = sum(len(p.get_images(full=True)) for p in doc)
        return pages, images
    exe = shutil.which("pdftotext")
    if not exe:
        sys.exit("Neither PyMuPDF nor pdftotext is available.")
    out = subprocess.run([exe, "-enc", "UTF-8", path, "-"], capture_output=True, check=True)
    text = out.stdout.decode("utf-8", errors="replace")
    return text.split("\f"), None


NUM = re.compile(r"(?<![\w.])[-+]?\d+(?:[.,]\d+)*%?(?![\w])")
WORD = re.compile(r"[A-Za-z][A-Za-z\-']{3,}")


def normalise(text: str) -> str:
    text = text.replace("­", "").replace("ﬁ", "fi").replace("ﬂ", "fl")
    text = re.sub(r"-\n(?=[a-z])", "", text)  # undo line-end hyphenation
    return re.sub(r"\s+", " ", text)


def counts(text: str, pattern: re.Pattern) -> collections.Counter:
    return collections.Counter(m.group(0).lower().rstrip(".,") for m in pattern.finditer(text))


def context(text: str, token: str, width: int) -> str:
    i = text.lower().find(token.lower())
    if i < 0:
        return ""
    return text[max(0, i - width): i + len(token) + width].strip()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("local")
    ap.add_argument("portal")
    ap.add_argument("--context", type=int, default=40, help="characters of context around a missing token")
    ap.add_argument("--max", type=int, default=40, help="most items to list per section")
    args = ap.parse_args()
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, OSError):
            pass

    lp, li = read_pdf(args.local)
    pp, pi = read_pdf(args.portal)
    lt, pt = normalise(" ".join(lp)), normalise(" ".join(pp))

    print("# Portal PDF against local build\n")
    print("| | local | portal |\n|---|---|---|")
    print(f"| pages | {len(lp)} | {len(pp)} |")
    print(f"| embedded images | {li if li is not None else 'n/a'} | {pi if pi is not None else 'n/a'} |")
    print(f"| characters of text | {len(lt)} | {len(pt)} |")
    for mark in ("??", "[?]", "Error! Reference source not found"):
        print(f"| `{mark}` | {lt.count(mark)} | {pt.count(mark)} |")
    if len(pp) != len(lp):
        print(f"\nPage count differs by {len(pp) - len(lp)}. A portal cover page or line numbering explains a small "
              "increase; a decrease usually means dropped content.")
    if li is not None and pi is not None and pi < li:
        print(f"\nThe portal copy has {li - pi} fewer embedded images. Look for a missing figure. "
              "(Vector figures are not counted as images, so equal counts do not prove every figure is present.)")

    ln, pn = counts(lt, NUM), counts(pt, NUM)
    missing_nums = sorted(((t, c - pn[t]) for t, c in ln.items() if c > pn[t] and len(t) > 1),
                          key=lambda x: (-x[1], x[0]))
    print(f"\n## Numbers in the local build that are missing or fewer in the portal copy: {len(missing_nums)}\n")
    for tok, n in missing_nums[: args.max]:
        print(f"- `{tok}` (short by {n}): ...{context(lt, tok, args.context)}...")
    if len(missing_nums) > args.max:
        print(f"- and {len(missing_nums) - args.max} more")

    lw, pw = counts(lt, WORD), counts(pt, WORD)
    only_local = sorted((t for t in lw if t not in pw), key=lambda t: -lw[t])
    only_portal = sorted((t for t in pw if t not in lw), key=lambda t: -pw[t])
    print(f"\n## Words only in the local build: {len(only_local)}\n")
    print(", ".join(only_local[: args.max * 2]) or "none")
    print(f"\n## Words only in the portal copy: {len(only_portal)}\n")
    print(", ".join(only_portal[: args.max * 2]) or "none")
    print("\nWords only in the portal copy are usually its cover page, watermark, or line numbers. Words only in the "
          "local build point at dropped text, a missing supplement, or a font the portal could not map.")

    print("\n## First page, first lines\n")
    for name, pages in (("local", lp), ("portal", pp)):
        first = [ln_ for ln_ in (pages[0] if pages else "").splitlines() if ln_.strip()][:12]
        print(f"**{name}**\n")
        print("\n".join("> " + x.strip() for x in first) or "> (no text)")
        print()
    print("Read the portal copy's pages before reporting. This script compares text; it does not see a reflowed "
          "table, a substituted font, or a figure rendered at low resolution.")
    return 1 if missing_nums else 0


if __name__ == "__main__":
    raise SystemExit(main())
