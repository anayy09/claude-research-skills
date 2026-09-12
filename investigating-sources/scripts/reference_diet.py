#!/usr/bin/env python3
"""
reference_diet.py - Bring a reference list down to a cap without cutting the
citations that carry the argument, and replace preprints with their version
of record.

Reads the manuscript to count where every key is cited, reads the source log
(if given) for peer-review status and superseding DOIs written by
check_citations.py, and produces a ranked plan:

  1. upgrade   preprints whose peer-reviewed version exists (cite that instead)
  2. remove    sources that failed verification or are still unconfirmed
  3. remove    preprints with no published version, cited only in related work
  4. remove    once-cited sources that appear only in the related-work section,
               oldest first, until the cap is met
  5. stop      anything else is the author's call: a source cited in Methods,
               Results, or Discussion, or more than once, is never cut by rule

The plan is printed; nothing in the manuscript is edited. --write-bib writes
a copy of the .bib with the removed entries dropped (upgraded entries keep
their old key and gain a `note = {UPGRADE TO <doi>}` so the author, or
--fetch-vor-bibtex, replaces them).

Usage:
    python reference_diet.py refs.bib paper.tex --cap 40
    python reference_diet.py refs.bib sections/*.md --cap 40 --sources sources.json
    python reference_diet.py refs.bib paper.tex --cap 40 --keep smith2021,lee2020 --write-bib refs.pruned.bib
    python reference_diet.py refs.bib paper.tex --cap 40 --fetch-vor-bibtex --mailto you@uni.edu
    python reference_diet.py --self-test

Standard library only. --fetch-vor-bibtex uses DOI content negotiation over
urllib and says so when offline.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.request
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

CITE_TEX = re.compile(r"\\(?:cite|citep|citet|citealp|citealt|citeauthor|citeyear|parencite|textcite|autocite|footcite|Cite|Citep|Citet)\*?(?:\[[^\]]*\]){0,2}\{([^}]+)\}")
CITE_MD = re.compile(r"\[(@?[A-Za-z][A-Za-z0-9_:.+-]*(?:\s*[,;]\s*@?[A-Za-z][A-Za-z0-9_:.+-]*)*)\]")
HEADING = re.compile(r"^(?:#{1,3}\s+(.*?)\s*$|\s*\\(?:section|subsection|chapter)\*?\s*\{([^}]*)\})", re.M)
RELATED = re.compile(r"related work|background|prior work|literature|state of the art", re.I)
PREPRINT_PREFIXES = ("10.48550", "10.1101", "10.21203", "10.2139", "10.31234", "10.31235", "10.36227", "10.20944", "10.26434", "10.31219")


def parse_bib(text: str) -> Dict[str, Dict[str, str]]:
    entries: Dict[str, Dict[str, str]] = {}
    for m in re.finditer(r"@(\w+)\s*\{\s*([^,\s]+)\s*,(.*?)\n\}", text, re.S):
        kind, key, body = m.group(1).lower(), m.group(2), m.group(3)
        fields: Dict[str, str] = {"_type": kind, "_raw": m.group(0)}
        for fm in re.finditer(r"(\w+)\s*=\s*(\{(?:[^{}]|\{[^{}]*\})*\}|\"[^\"]*\"|[^,\n]+)", body):
            v = fm.group(2).strip().strip("{}\"").strip()
            fields[fm.group(1).lower()] = re.sub(r"\s+", " ", v)
        entries[key] = fields
    return entries


def parse_reflist(text: str) -> Dict[str, Dict[str, str]]:
    """A markdown reference list of the form `[key] Author (year). Title. ...`."""
    entries: Dict[str, Dict[str, str]] = {}
    for m in re.finditer(r"^\s*\[([A-Za-z][A-Za-z0-9_:.+-]*)\]\s*(.+)$", text, re.M):
        raw = m.group(2)
        doi = re.search(r"10\.\d{4,9}/[^\s,;]+", raw)
        year = re.search(r"\b(19|20)\d{2}\b", raw)
        entries[m.group(1)] = {"_type": "misc", "_raw": m.group(0), "doi": doi.group(0) if doi else "",
                               "year": year.group(0) if year else "", "title": raw[:120]}
    return entries


def citations_by_section(paths: List[Path]) -> Dict[str, Dict[str, int]]:
    """key -> {section title: count}."""
    out: Dict[str, Dict[str, int]] = {}
    for p in paths:
        text = p.read_text(encoding="utf-8", errors="replace")
        if p.suffix.lower() == ".tex":
            text = re.sub(r"(?<!\\)%.*", "", text)
        parts = HEADING.split(text)
        # split yields [pre, g1, g2, body, g1, g2, body, ...]
        section = "(front)"
        chunks: List[Tuple[str, str]] = [(section, parts[0])]
        i = 1
        while i + 2 < len(parts) + 1 and i < len(parts):
            title = parts[i] or parts[i + 1] or "(untitled)"
            body = parts[i + 2] if i + 2 < len(parts) else ""
            chunks.append((title.strip(), body))
            i += 3
        for title, body in chunks:
            keys: List[str] = []
            if p.suffix.lower() == ".tex":
                for m in CITE_TEX.finditer(body):
                    keys += [k.strip() for k in m.group(1).split(",")]
            else:
                for m in CITE_MD.finditer(body):
                    keys += [k.strip().lstrip("@") for k in re.split(r"[,;]", m.group(1))]
            for k in keys:
                if not k:
                    continue
                out.setdefault(k, {})
                out[k][title] = out[k].get(title, 0) + 1
    return out


def status_of(key: str, entry: Dict[str, str], sources: Dict[str, dict]) -> Tuple[str, str]:
    """(status, superseded_by). status: peer-reviewed | preprint | preprint-vor | unverified | failed | unknown."""
    s = sources.get(key)
    doi = (entry.get("doi") or "").lower()
    if s:
        if s.get("verified") == "fail":
            return "failed", ""
        if s.get("superseded_by"):
            return "preprint-vor", s["superseded_by"]
        pr = s.get("peer_reviewed", "")
        if pr == "preprint":
            return "preprint", ""
        if pr == "peer-reviewed":
            return "peer-reviewed", ""
        if s.get("verified") != "confirmed":
            return "unverified", ""
        return "unknown", ""
    if doi.startswith(PREPRINT_PREFIXES) or "arxiv" in (entry.get("journal", "") + entry.get("eprint", "") + entry.get("url", "")).lower():
        return "preprint", ""
    return "unknown", ""


def plan(entries: Dict[str, Dict[str, str]], cites: Dict[str, Dict[str, int]], sources: Dict[str, dict],
         cap: int, keep: Set[str]) -> Tuple[List[dict], int]:
    rows: List[dict] = []
    for key, e in entries.items():
        secs = cites.get(key, {})
        n = sum(secs.values())
        related_only = bool(secs) and all(RELATED.search(t) for t in secs)
        st, sup = status_of(key, e, sources)
        rows.append({"key": key, "cites": n, "sections": sorted(secs), "related_only": related_only,
                     "status": st, "superseded_by": sup, "year": e.get("year", ""), "keep": key in keep,
                     "action": "keep", "reason": ""})
    uncited = [r for r in rows if r["cites"] == 0]
    for r in uncited:
        r["action"], r["reason"] = "remove", "not cited anywhere"
    for r in rows:
        if r["action"] != "keep" or r["keep"]:
            continue
        if r["status"] == "preprint-vor":
            r["action"], r["reason"] = "upgrade", f"cite the version of record {r['superseded_by']}"
        elif r["status"] == "failed":
            r["action"], r["reason"] = "remove", "failed verification"
        elif r["status"] == "unverified":
            r["action"], r["reason"] = "remove", "not confirmed to exist; confirm it or remove the claim that rests on it"
    count = sum(1 for r in rows if r["action"] in ("keep", "upgrade"))
    if count > cap:
        cands = [r for r in rows if r["action"] == "keep" and not r["keep"] and r["status"] == "preprint" and r["related_only"]]
        cands.sort(key=lambda r: (r["cites"], r["year"]))
        for r in cands:
            if count <= cap:
                break
            r["action"], r["reason"] = "remove", "preprint with no published version, cited only in related work"
            count -= 1
    if count > cap:
        cands = [r for r in rows if r["action"] == "keep" and not r["keep"] and r["cites"] == 1 and r["related_only"]]
        cands.sort(key=lambda r: (r["year"] or "0000"))
        for r in cands:
            if count <= cap:
                break
            r["action"], r["reason"] = "remove", "cited once, in related work only"
            count -= 1
    return rows, count


def render(rows: List[dict], cap: int, after: int, before: int) -> str:
    lines = ["# Reference diet", "", f"Before: {before} references. Cap: {cap}. After this plan: {after}.", ""]
    if after > cap:
        lines.append(f"**Still {after - cap} over the cap.** Every remaining reference is cited more than once, "
                     "outside related work, or protected. Cutting further is an editorial decision "
                     "(`manuscript-editor`), not a rule; candidates are listed at the end.")
        lines.append("")
    order = {"upgrade": 0, "remove": 1, "keep": 2}
    lines.append("| Key | Action | Reason | Cites | Sections | Status | Year |")
    lines.append("|---|---|---|---:|---|---|---|")
    for r in sorted(rows, key=lambda r: (order[r["action"]], -r["cites"], r["key"])):
        lines.append(f"| `{r['key']}` | **{r['action']}** | {r['reason']} | {r['cites']} | {'; '.join(r['sections'])[:60]} | {r['status']} | {r['year']} |")
    lines.append("")
    if after > cap:
        nxt = [r for r in rows if r["action"] == "keep" and not r["keep"]]
        nxt.sort(key=lambda r: (r["cites"], r["year"] or "0000"))
        lines.append("Next candidates, for the author to rule on (fewest citations, oldest first):")
        lines += [f"- `{r['key']}`: {r['cites']} citation(s) in {'; '.join(r['sections'])}" for r in nxt[:12]]
        lines.append("")
    lines.append("Rules applied: upgrade preprints with a version of record; remove failed or unconfirmed sources; "
                 "remove related-work-only preprints, then related-work-only once-cited sources oldest first; "
                 "never cut a source cited in Methods, Results, or Discussion, or cited more than once, by rule. "
                 "After applying the plan, re-run audit_report.py and the prose in related work still has to read as a synthesis.")
    return "\n".join(lines)


def fetch_bibtex(doi: str, mailto: str) -> Optional[str]:
    req = urllib.request.Request(f"https://doi.org/{doi}", headers={"Accept": "application/x-bibtex",
                                                                    "User-Agent": f"reference_diet.py (mailto:{mailto or 'none'})"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.read().decode("utf-8", errors="replace")
    except Exception:
        return None


def write_bib(entries: Dict[str, Dict[str, str]], rows: List[dict], path: Path, fetched: Dict[str, str]) -> None:
    out = []
    by_key = {r["key"]: r for r in rows}
    for key, e in entries.items():
        r = by_key.get(key)
        if r and r["action"] == "remove":
            continue
        raw = e["_raw"]
        if r and r["action"] == "upgrade":
            if key in fetched:
                new = fetched[key]
                new = re.sub(r"@(\w+)\s*\{\s*[^,]+,", lambda m: f"@{m.group(1)}{{{key},", new, count=1)
                out.append(new.strip())
                continue
            raw = raw.rstrip().rstrip("}").rstrip().rstrip(",") + f",\n  note = {{UPGRADE TO {r['superseded_by']}}}\n}}"
        out.append(raw.strip())
    path.write_text("\n\n".join(out) + "\n", encoding="utf-8", newline="\n")


def self_test() -> int:
    ok = True

    def check(desc: str, cond: bool) -> None:
        nonlocal ok
        print(("  ok   " if cond else "  FAIL ") + desc)
        ok = ok and cond

    bib = """@article{good2020,
  title = {A real paper},
  year = {2020},
  doi = {10.1000/good}
}

@misc{pre2024,
  title = {A preprint},
  year = {2024},
  doi = {10.48550/arXiv.2401.00001}
}

@article{old2010,
  title = {Old related work},
  year = {2010},
  doi = {10.1000/old}
}

@article{never2019,
  title = {Uncited},
  year = {2019}
}
"""
    entries = parse_bib(bib)
    check("bib parsed", set(entries) == {"good2020", "pre2024", "old2010", "never2019"})
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        tex = Path(td) / "p.tex"
        tex.write_text(r"""\section{Introduction} x \cite{good2020}.
\section{Related work} y \citep{pre2024, old2010} and \cite{good2020}.
\section{Methods} z \cite{good2020}.""", encoding="utf-8")
        cites = citations_by_section([tex])
        check("citations by section", cites["good2020"]["Methods"] == 1 and set(cites["pre2024"]) == {"Related work"})
        sources = {"pre2024": {"verified": "confirmed", "peer_reviewed": "preprint", "superseded_by": ""}}
        rows, after = plan(entries, cites, sources, cap=2, keep=set())
        by = {r["key"]: r for r in rows}
        check("uncited removed", by["never2019"]["action"] == "remove")
        check("related-only preprint removed under cap", by["pre2024"]["action"] == "remove")
        check("methods-cited source kept", by["good2020"]["action"] == "keep")
        check("count after plan", after == 2)
        sources["pre2024"]["superseded_by"] = "10.1000/vor"
        rows, after = plan(entries, cites, sources, cap=10, keep=set())
        check("preprint with VoR is an upgrade, not a removal", {r["key"]: r["action"] for r in rows}["pre2024"] == "upgrade")
        out = Path(td) / "out.bib"
        write_bib(entries, rows, out, {})
        txt = out.read_text(encoding="utf-8")
        check("write-bib drops removed and annotates upgrade", "never2019" not in txt and "UPGRADE TO 10.1000/vor" in txt)
    print("\nself-test " + ("passed" if ok else "FAILED"))
    return 0 if ok else 1


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, OSError):
            pass
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("bib", nargs="?", help=".bib file, or a markdown reference list with [key] lines")
    p.add_argument("manuscript", nargs="*", help=".tex or .md files that cite the keys")
    p.add_argument("--cap", type=int, default=0, help="target number of references")
    p.add_argument("--sources", help="source log JSON written by check_citations.py (status, superseded_by)")
    p.add_argument("--keep", default="", help="comma-separated keys never to remove")
    p.add_argument("--write-bib", help="write the pruned .bib here")
    p.add_argument("--fetch-vor-bibtex", action="store_true", help="fetch BibTeX for each version-of-record DOI (network)")
    p.add_argument("--mailto", default="")
    p.add_argument("--report", help="write the plan here instead of stdout")
    p.add_argument("--self-test", action="store_true")
    a = p.parse_args()
    if a.self_test:
        return self_test()
    if not a.bib or not a.manuscript:
        p.error("give the .bib and at least one manuscript file (or --self-test)")
    bib_path = Path(a.bib)
    text = bib_path.read_text(encoding="utf-8", errors="replace")
    entries = parse_bib(text) if bib_path.suffix.lower() == ".bib" else parse_reflist(text)
    if not entries:
        print("error: no entries found", file=sys.stderr)
        return 2
    cites = citations_by_section([Path(m) for m in a.manuscript])
    sources: Dict[str, dict] = {}
    if a.sources:
        log = json.loads(Path(a.sources).read_text(encoding="utf-8"))
        sources = {s.get("key"): s for s in log.get("sources", [])}
    keep = {k.strip() for k in a.keep.split(",") if k.strip()}
    cap = a.cap or len(entries)
    rows, after = plan(entries, cites, sources, cap, keep)
    report = render(rows, cap, after, len(entries))
    if a.report:
        Path(a.report).write_text(report, encoding="utf-8", newline="\n")
        print(f"wrote {a.report}")
    else:
        print(report)
    fetched: Dict[str, str] = {}
    if a.fetch_vor_bibtex:
        for r in rows:
            if r["action"] == "upgrade":
                bt = fetch_bibtex(r["superseded_by"], a.mailto)
                if bt:
                    fetched[r["key"]] = bt
                else:
                    print(f"note: could not fetch BibTeX for {r['superseded_by']} (offline?)", file=sys.stderr)
    if a.write_bib:
        write_bib(entries, rows, Path(a.write_bib), fetched)
        print(f"wrote {a.write_bib}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
