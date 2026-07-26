#!/usr/bin/env python3
"""Translate one concept-block search into every database's syntax, and emit a
PRISMA-S compliant record of it.

Searches get retyped by hand for each database, drift apart in the process, and
then cannot be reproduced from the published paper. This script keeps one
source of truth (a small YAML file) and generates the rest, so the strategy in
the appendix is provably the strategy that ran.

Usage
-----
    python search_builder.py --spec search.yaml                 # all databases
    python search_builder.py --spec search.yaml --db pubmed scopus
    python search_builder.py --example > search.yaml            # starter spec
    python search_builder.py --spec search.yaml --prisma-s      # reporting record

Spec format (YAML or JSON):

    question: Does AI-assisted triage reduce pathologist workload?
    framework: PICO
    blocks:
      - name: Population
        terms: ["colorectal cancer", "colorectal neoplasm", colorectal]
        mesh: ["Colorectal Neoplasms"]
        truncate: true
      - name: Intervention
        terms: ["deep learning", "machine learning", "artificial intelligence"]
        mesh: ["Artificial Intelligence"]
    limits:
      years: [2015, 2026]
      languages: [English]

Blocks are OR'd internally and AND'd together, which is the standard structure.
Nothing here validates that your terms are the right terms: that is a librarian
judgment and this script does not pretend to make it.
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Dict, List

try:
    import yaml  # type: ignore
except ImportError:
    yaml = None

EXAMPLE = """# Concept-block search specification.
# One block per concept. Blocks are combined with AND; terms within a block with OR.
question: Does AI-assisted triage reduce pathologist workload in colorectal screening?
framework: PICO

blocks:
  - name: Population
    terms: ["colorectal cancer", "colorectal neoplasm", "colorectal carcinoma"]
    mesh: ["Colorectal Neoplasms"]
    truncate: true

  - name: Intervention
    terms: ["deep learning", "machine learning", "artificial intelligence",
            "convolutional neural network", "foundation model"]
    mesh: ["Artificial Intelligence", "Deep Learning"]

  - name: Context
    terms: ["histopathology", "whole slide imaging", "digital pathology",
            "triage", "workload"]
    mesh: ["Pathology, Clinical"]

limits:
  years: [2015, 2026]
  languages: [English]
  # Exclusions belong in eligibility criteria, not in the search string.
  # Over-filtering the search hides what you excluded and why.
"""


def load_spec(path: str) -> Dict[str, Any]:
    text = open(path, encoding="utf-8").read()
    if path.endswith((".yaml", ".yml")):
        if yaml is None:
            sys.exit("PyYAML needed for YAML specs: pip install pyyaml "
                     "(or write the spec as JSON)")
        return yaml.safe_load(text)
    return json.loads(text)


def quote_terms(terms: List[str], truncate: bool, star: str = "*") -> List[str]:
    """Phrases stay quoted and untruncated; single words may be truncated.

    Most platforms do not apply truncation inside a quoted phrase, so
    "deep learn*" either errors or silently matches nothing. Truncating only
    single tokens avoids a class of searches that look fine and return zero.
    """
    out = []
    for t in terms:
        t = t.strip()
        if " " in t:
            out.append(f'"{t}"')
        elif truncate:
            out.append(f"{t}{star}")
        else:
            out.append(f'"{t}"')
    return out


# --------------------------------------------------------------------------
# per-database renderers
# --------------------------------------------------------------------------

def pubmed(spec: Dict[str, Any]) -> str:
    parts = []
    for b in spec["blocks"]:
        terms = [f"{t}[tiab]" for t in quote_terms(b.get("terms", []),
                                                   b.get("truncate", False))]
        terms += [f'"{m}"[mh]' for m in b.get("mesh", [])]
        parts.append("(" + " OR ".join(terms) + ")")
    q = " AND ".join(parts)
    lim = spec.get("limits", {})
    if lim.get("years"):
        y0, y1 = lim["years"]
        q += f' AND ("{y0}"[dp] : "{y1}"[dp])'
    for lang in lim.get("languages", []):
        q += f" AND {lang}[la]"
    return q


def scopus(spec: Dict[str, Any]) -> str:
    parts = []
    for b in spec["blocks"]:
        # Scopus has no controlled vocabulary equivalent to MeSH; folding the
        # MeSH labels in as keywords is the usual compromise, and is reported.
        terms = quote_terms(b.get("terms", []) + b.get("mesh", []),
                            b.get("truncate", False))
        parts.append("TITLE-ABS-KEY(" + " OR ".join(terms) + ")")
    q = " AND ".join(parts)
    lim = spec.get("limits", {})
    if lim.get("years"):
        y0, y1 = lim["years"]
        q += f" AND PUBYEAR > {int(y0) - 1} AND PUBYEAR < {int(y1) + 1}"
    for lang in lim.get("languages", []):
        q += f' AND LANGUAGE("{lang}")'
    return q


def wos(spec: Dict[str, Any]) -> str:
    parts = []
    for b in spec["blocks"]:
        terms = quote_terms(b.get("terms", []) + b.get("mesh", []),
                            b.get("truncate", False))
        parts.append("TS=(" + " OR ".join(terms) + ")")
    q = " AND ".join(parts)
    lim = spec.get("limits", {})
    if lim.get("years"):
        y0, y1 = lim["years"]
        q += f" AND PY=({y0}-{y1})"
    return q


def ieee(spec: Dict[str, Any]) -> str:
    parts = []
    for b in spec["blocks"]:
        terms = [f'("All Metadata":{t})' for t in
                 quote_terms(b.get("terms", []) + b.get("mesh", []),
                             b.get("truncate", False))]
        parts.append("(" + " OR ".join(terms) + ")")
    return " AND ".join(parts)


def cochrane(spec: Dict[str, Any]) -> str:
    lines, refs = [], []
    n = 0
    for b in spec["blocks"]:
        ids = []
        for m in b.get("mesh", []):
            n += 1
            lines.append(f"#{n} MeSH descriptor: [{m}] explode all trees")
            ids.append(f"#{n}")
        terms = quote_terms(b.get("terms", []), b.get("truncate", False))
        if terms:
            n += 1
            lines.append(f"#{n} " + " OR ".join(f"({t}):ti,ab,kw" for t in terms))
            ids.append(f"#{n}")
        n += 1
        lines.append(f"#{n} " + " OR ".join(ids) + f"    [{b['name']}]")
        refs.append(f"#{n}")
    n += 1
    lines.append(f"#{n} " + " AND ".join(refs))
    return "\n".join(lines)


def embase_ovid(spec: Dict[str, Any]) -> str:
    lines, refs = [], []
    n = 0
    for b in spec["blocks"]:
        ids = []
        for m in b.get("mesh", []):
            n += 1
            lines.append(f"{n}. exp {m}/")
            ids.append(str(n))
        for t in b.get("terms", []):
            n += 1
            token = t if " " not in t else f'"{t}"'
            if " " not in t and b.get("truncate"):
                token = f"{t}*"
            lines.append(f"{n}. ({token}).ti,ab,kw.")
            ids.append(str(n))
        n += 1
        lines.append(f"{n}. " + " or ".join(ids) + f"    [{b['name']}]")
        refs.append(str(n))
    n += 1
    lines.append(f"{n}. " + " and ".join(refs))
    return "\n".join(lines)


def generic(spec: Dict[str, Any]) -> str:
    parts = []
    for b in spec["blocks"]:
        terms = quote_terms(b.get("terms", []) + b.get("mesh", []),
                            b.get("truncate", False))
        parts.append("(" + " OR ".join(terms) + ")")
    return " AND ".join(parts)


RENDERERS = {"pubmed": pubmed, "scopus": scopus, "wos": wos, "ieee": ieee,
             "cochrane": cochrane, "embase": embase_ovid, "generic": generic}

LABELS = {"pubmed": "PubMed (NLM interface)", "scopus": "Scopus (Elsevier)",
          "wos": "Web of Science Core Collection (Clarivate)",
          "ieee": "IEEE Xplore (command search)",
          "cochrane": "Cochrane CENTRAL (Wiley, line-numbered)",
          "embase": "Embase (Ovid, line-numbered)",
          "generic": "Generic Boolean (adapt to platform)"}


def prisma_s_record(spec: Dict[str, Any], dbs: List[str]) -> str:
    """PRISMA-S asks for the elements below; leaving explicit blanks is better
    than omitting the items, because a blank is visibly unfinished."""
    lim = spec.get("limits", {})
    years = lim.get("years", ["", ""])
    rows = "\n".join(
        f"| {LABELS[d]} | <date run> | <n records> | see strategy above |"
        for d in dbs)
    return f"""
## Search reporting record (PRISMA-S)

Fill the bracketed fields when the searches are run. Items map to the PRISMA-S
16-item checklist; anything left bracketed is an unreported item.

**Question.** {spec.get('question', '<state the question>')}
**Framework.** {spec.get('framework', '<PICO / PICo / SPIDER / other>')}

| Item | Entry |
|---|---|
| Database name and platform | see table below |
| Multi-database searching | strategies translated per platform, not reused verbatim |
| Study registries | <ClinicalTrials.gov, ICTRP, or 'none searched'> |
| Online resources / browsing | <preprint servers, org websites, or 'none'> |
| Citation searching | <forward/backward citation chasing performed? on which set?> |
| Contacts | <authors or experts contacted?> |
| Other methods | <hand searching, conference proceedings> |
| Full search strategies | reproduced verbatim below for every source |
| Limits and restrictions | years {years[0]}-{years[1]}; languages {lim.get('languages', ['none'])} |
| Search filters | <named published filters used, with citation, or 'none'> |
| Prior work | <adapted from an existing review? cite it> |
| Updates | <date of last search; rerun before submission> |
| Dedup method | <software and settings> |
| Total records | <before and after deduplication> |
| Peer review of strategy | <PRESS-reviewed by whom, or 'not peer reviewed'> |

| Source | Date run | Records | Strategy |
|---|---|---|---|
{rows}

Note that language restrictions must be justified in the eligibility criteria.
Restricting to English is a decision with a known risk of bias, not a neutral
convenience, and reviewers increasingly ask for the justification.
""".rstrip()


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--spec", help="YAML or JSON concept-block spec")
    p.add_argument("--db", nargs="*", default=list(RENDERERS),
                   choices=list(RENDERERS), help="which databases to render")
    p.add_argument("--example", action="store_true", help="print a starter spec")
    p.add_argument("--prisma-s", action="store_true",
                   help="also emit the PRISMA-S reporting record")
    a = p.parse_args()

    if a.example:
        print(EXAMPLE)
        return 0
    if not a.spec:
        sys.exit("give --spec <file> or --example")

    spec = load_spec(a.spec)
    if not spec.get("blocks"):
        sys.exit("spec has no 'blocks'")

    n_terms = sum(len(b.get("terms", [])) + len(b.get("mesh", []))
                  for b in spec["blocks"])
    print(f"# Search strategy: {len(spec['blocks'])} concept blocks, "
          f"{n_terms} terms total\n")
    for d in a.db:
        print(f"## {LABELS[d]}\n")
        print("```")
        print(RENDERERS[d](spec))
        print("```\n")

    if a.prisma_s:
        print(prisma_s_record(spec, a.db))

    print("\n---\nBefore running these: have a librarian or a second reviewer "
          "check the strategy (PRESS). Test that known key papers are retrieved; "
          "a search that misses a paper you already know about is broken, and "
          "that check takes two minutes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
