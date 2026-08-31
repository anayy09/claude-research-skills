#!/usr/bin/env python3
"""Translate one concept-block search into every database's syntax, and emit a
PRISMA-S compliant record of it.

Searches get retyped by hand for each database, drift apart in the process, and
then cannot be reproduced from the published paper. This script keeps one
source of truth (a small YAML file) and generates the rest, so the strategy in
the appendix is provably the strategy that ran.

It renders the federated indexes (PubMed, Scopus, Web of Science, Cochrane
CENTRAL, Ovid Embase, Europe PMC) and the publisher-native platforms (IEEE
Xplore, SpringerLink and the Nature portfolio, Elsevier ScienceDirect, the ACM
Digital Library, Wiley Online Library), plus a Crossref REST query for scripted
supplementary searching.

Usage
-----
    python search_builder.py --spec search.yaml                 # all platforms
    python search_builder.py --spec search.yaml --db pubmed scopus ieee
    python search_builder.py --spec search.yaml --peer-reviewed-only
    python search_builder.py --example > search.yaml            # starter spec
    python search_builder.py --spec search.yaml --prisma-s      # reporting record
    python search_builder.py --self-test                        # check the renderers

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
judgment and this script does not pretend to make it. What it does check is the
mechanical failures that silently return the wrong result set, which it reports
as platform warnings rather than fixing behind your back.
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Dict, List, Tuple

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


def all_terms(spec: Dict[str, Any]) -> List[str]:
    out: List[str] = []
    for b in spec.get("blocks", []):
        out.extend(b.get("terms", []))
        out.extend(b.get("mesh", []))
    return out


def block_uses_truncation(spec: Dict[str, Any]) -> bool:
    return any(b.get("truncate") for b in spec.get("blocks", []))


def connector_count(spec: Dict[str, Any]) -> int:
    """Boolean connectors the strategy needs, which is what the platforms with a
    connector ceiling actually count."""
    n = 0
    for b in spec.get("blocks", []):
        n += max(len(b.get("terms", [])) + len(b.get("mesh", [])) - 1, 0)
    return n + max(len(spec.get("blocks", [])) - 1, 0)


# --------------------------------------------------------------------------
# per-database renderers
#
# Each takes (spec, peer_reviewed_only) and returns the query as the platform
# expects it. Where a platform expresses the peer-reviewed restriction as a UI
# facet rather than as query syntax, the restriction appears in the platform
# warnings instead, because emitting a filter the platform will not parse is
# worse than saying where to click.
# --------------------------------------------------------------------------

def pubmed(spec: Dict[str, Any], pr_only: bool = False) -> str:
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
    if pr_only:
        # PubMed carries preprints from funder-mandated deposits and types them.
        q += " NOT preprint[pt]"
    return q


def scopus(spec: Dict[str, Any], pr_only: bool = False) -> str:
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
    if pr_only:
        q += " AND (DOCTYPE(ar) OR DOCTYPE(re) OR DOCTYPE(cp))"
    return q


def wos(spec: Dict[str, Any], pr_only: bool = False) -> str:
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
    if pr_only:
        q += ' AND DT=(Article OR Review OR "Proceedings Paper")'
    return q


def ieee(spec: Dict[str, Any], pr_only: bool = False) -> str:
    parts = []
    for b in spec["blocks"]:
        terms = [f'("All Metadata":{t})' for t in
                 quote_terms(b.get("terms", []) + b.get("mesh", []),
                             b.get("truncate", False))]
        parts.append("(" + " OR ".join(terms) + ")")
    return " AND ".join(parts)


def springer(spec: Dict[str, Any], pr_only: bool = False) -> str:
    """SpringerLink advanced search, which also covers the Nature portfolio.

    SpringerLink has no truncation operator, so any truncated token is expanded
    back to the quoted stem here and the warning tells you to list the variants
    yourself. Emitting `neoplas*` would return a result set that looks plausible
    and is wrong.
    """
    parts = []
    for b in spec["blocks"]:
        terms = quote_terms(b.get("terms", []) + b.get("mesh", []),
                            truncate=False)
        parts.append("(" + " OR ".join(terms) + ")")
    return " AND ".join(parts)


def sciencedirect(spec: Dict[str, Any], pr_only: bool = False) -> str:
    """Elsevier ScienceDirect advanced search, 'Title, abstract, keywords' field."""
    parts = []
    for b in spec["blocks"]:
        terms = quote_terms(b.get("terms", []) + b.get("mesh", []),
                            b.get("truncate", False))
        parts.append("(" + " OR ".join(terms) + ")")
    return " AND ".join(parts)


def acm(spec: Dict[str, Any], pr_only: bool = False) -> str:
    parts = []
    for b in spec["blocks"]:
        terms = quote_terms(b.get("terms", []) + b.get("mesh", []),
                            b.get("truncate", False))
        parts.append("AllField:(" + " OR ".join(terms) + ")")
    return " AND ".join(parts)


def wiley(spec: Dict[str, Any], pr_only: bool = False) -> str:
    parts = []
    for b in spec["blocks"]:
        terms = quote_terms(b.get("terms", []) + b.get("mesh", []),
                            b.get("truncate", False))
        parts.append('"all":(' + " OR ".join(terms) + ")")
    return " AND ".join(parts)


def europepmc(spec: Dict[str, Any], pr_only: bool = False) -> str:
    """Europe PMC, which is free and keyless and therefore the one platform here
    a script can actually run without an institutional subscription."""
    parts = []
    for b in spec["blocks"]:
        terms = []
        for t in quote_terms(b.get("terms", []), b.get("truncate", False)):
            terms.append(f"(TITLE:{t} OR ABSTRACT:{t} OR KW:{t})")
        for m in b.get("mesh", []):
            terms.append(f'MESH:"{m}"')
        parts.append("(" + " OR ".join(terms) + ")")
    q = " AND ".join(parts)
    lim = spec.get("limits", {})
    if lim.get("years"):
        y0, y1 = lim["years"]
        q += f" AND (FIRST_PDATE:[{y0} TO {y1}])"
    for lang in lim.get("languages", []):
        q += f' AND LANG:"{lang.lower()[:3]}"'
    if pr_only:
        # SRC:PPR is the preprint corpus; excluding it leaves the reviewed record.
        q += " NOT SRC:PPR"
    return q


def crossref(spec: Dict[str, Any], pr_only: bool = False) -> str:
    """A Crossref REST URL for scripted supplementary searching.

    Crossref is a registration agency, not a bibliographic database: subject
    indexing is thin and relevance ranking is not a controlled-vocabulary
    search. Use this to sweep a specific publisher's peer-reviewed output as a
    supplement, never as the primary strategy.
    """
    terms = " ".join(t for t in all_terms(spec))
    filters = ["type:journal-article"] if pr_only else []
    lim = spec.get("limits", {})
    if lim.get("years"):
        y0, y1 = lim["years"]
        filters += [f"from-pub-date:{y0}-01-01", f"until-pub-date:{y1}-12-31"]
    lines = [
        "https://api.crossref.org/works"
        f"?query.bibliographic={terms.replace(' ', '+')}"
        + (f"&filter={','.join(filters)}" if filters else "")
        + "&rows=100&mailto=YOUR_EMAIL",
        "",
        "# Scope to one publisher by adding a member ID to the filter:",
        "#   IEEE 263 | Elsevier 78 | Springer Nature 297 | ACM 320 | Wiley 311",
        "# Always pair member with type:journal-article. Member 78 also returns",
        "# SSRN working papers and member 263 also returns TechRxiv preprints.",
    ]
    return "\n".join(lines)


def generic(spec: Dict[str, Any], pr_only: bool = False) -> str:
    parts = []
    for b in spec["blocks"]:
        terms = quote_terms(b.get("terms", []) + b.get("mesh", []),
                            b.get("truncate", False))
        parts.append("(" + " OR ".join(terms) + ")")
    return " AND ".join(parts)


RENDERERS = {"pubmed": pubmed, "scopus": scopus, "wos": wos, "ieee": ieee,
             "springer": springer, "sciencedirect": sciencedirect, "acm": acm,
             "wiley": wiley, "europepmc": europepmc, "cochrane": None,
             "embase": None, "crossref": crossref, "generic": generic}

LABELS = {"pubmed": "PubMed (NLM interface)", "scopus": "Scopus (Elsevier)",
          "wos": "Web of Science Core Collection (Clarivate)",
          "ieee": "IEEE Xplore (command search)",
          "springer": "SpringerLink / Nature portfolio (Springer Nature)",
          "sciencedirect": "ScienceDirect (Elsevier, full text)",
          "acm": "ACM Digital Library",
          "wiley": "Wiley Online Library",
          "europepmc": "Europe PMC (free REST API)",
          "cochrane": "Cochrane CENTRAL (Wiley, line-numbered)",
          "embase": "Embase (Ovid, line-numbered)",
          "crossref": "Crossref REST (scripted supplement)",
          "generic": "Generic Boolean (adapt to platform)"}


def cochrane_lines(spec: Dict[str, Any], pr_only: bool = False) -> str:
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


def embase_ovid(spec: Dict[str, Any], pr_only: bool = False) -> str:
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
    if pr_only:
        n += 1
        lines.append(f'{n}. limit {n - 1} to (article or "article in press" '
                     f"or conference paper)")
    return "\n".join(lines)


RENDERERS["cochrane"] = cochrane_lines
RENDERERS["embase"] = embase_ovid


# --------------------------------------------------------------------------
# platform warnings
# --------------------------------------------------------------------------

def platform_warnings(spec: Dict[str, Any], db: str,
                      pr_only: bool) -> List[str]:
    """Mechanical failure modes that return a plausible but wrong result set.

    These are worth more than the rendered strings. A syntax error is visible;
    a strategy that silently matches nothing on one platform is what makes a
    review unreproducible.
    """
    w: List[str] = []
    truncated = block_uses_truncation(spec)
    connectors = connector_count(spec)
    longest_block = max((len(b.get("terms", [])) + len(b.get("mesh", []))
                         for b in spec.get("blocks", [])), default=0)

    if db == "springer":
        if truncated:
            w.append("SpringerLink has no truncation operator. Truncated tokens "
                     "were expanded back to quoted stems here; list the "
                     "morphological variants explicitly (neoplasm OR neoplasms "
                     "OR neoplastic) and report the expanded version as the "
                     "strategy actually run.")
        w.append("MeSH terms were folded in as keywords; SpringerLink has no "
                 "controlled vocabulary.")
        if pr_only:
            w.append("Restrict to peer-reviewed content with the 'Article' and "
                     "'Conference Paper' content-type facets. SpringerLink has "
                     "no query-syntax equivalent.")
    if db == "sciencedirect":
        if connectors > 8:
            w.append(f"This strategy needs about {connectors} Boolean "
                     f"connectors. ScienceDirect caps connectors per field and "
                     f"will reject or truncate it. Run the strategy in Scopus "
                     f"and use ScienceDirect for full-text follow-up, or split "
                     f"it into separately run blocks and report the split.")
        if pr_only:
            w.append("Restrict with the 'Research articles' and 'Review "
                     "articles' article-type facets.")
    if db == "ieee":
        if longest_block > 20:
            w.append(f"The largest block has {longest_block} terms. IEEE Xplore "
                     f"command search has a term ceiling and can truncate a long "
                     f"OR-chain silently; split the block and report the split.")
        w.append("IEEE Xplore indexes IEEE-published peer-reviewed content and "
                 "does not include TechRxiv, so no preprint filter is needed. "
                 "Early Access articles are peer reviewed but not final; record "
                 "which version you extracted from.")
    if db == "acm" and pr_only:
        w.append("Restrict with the content-type facets; the ACM DL also "
                 "indexes non-reviewed material such as magazine columns.")
    if db == "scopus":
        w.append("MeSH terms were folded in as keywords; Scopus has no "
                 "controlled vocabulary.")
    if db == "cochrane":
        w.append("CENTRAL is a trials register. Absence here is not absence of "
                 "evidence for a non-trial question.")
    if db == "crossref":
        w.append("Supplement only. Crossref relevance ranking is not a "
                 "controlled-vocabulary search and its subject indexing is thin.")
    if db == "europepmc" and not pr_only:
        w.append("Europe PMC includes preprints under SRC:PPR. Add "
                 "--peer-reviewed-only to exclude them, or keep them and "
                 "deduplicate preprint-and-published pairs at screening.")
    if db in ("pubmed", "scopus", "wos", "embase") and truncated:
        w.append("Check what the platform expands each truncated token to; "
                 "nurs* also matches nursery.")
    return w


def prisma_s_record(spec: Dict[str, Any], dbs: List[str], pr_only: bool) -> str:
    """PRISMA-S asks for the elements below; leaving explicit blanks is better
    than omitting the items, because a blank is visibly unfinished."""
    lim = spec.get("limits", {})
    years = lim.get("years", ["", ""])
    rows = "\n".join(
        f"| {LABELS[d]} | <date run> | <n records> | see strategy above |"
        for d in dbs)
    pr_line = ("peer-reviewed publication types only; preprint servers excluded"
               if pr_only else
               "<state whether preprints and grey literature were eligible>")
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
| Publication type | {pr_line} |
| Limits and restrictions | years {years[0]}-{years[1]}; languages {lim.get('languages', ['none'])} |
| Search filters | <named published filters used, with citation, or 'none'> |
| Prior work | <adapted from an existing review? cite it> |
| Updates | <date of last search; rerun before submission> |
| Dedup method | <software and settings; state how preprint/published pairs were merged> |
| Total records | <before and after deduplication> |
| Peer review of strategy | <PRESS-reviewed by whom, or 'not peer reviewed'> |

| Source | Date run | Records | Strategy |
|---|---|---|---|
{rows}

Note that language restrictions must be justified in the eligibility criteria.
Restricting to English is a decision with a known risk of bias, not a neutral
convenience, and reviewers increasingly ask for the justification.

A preprint and its published version are one study, not two. State how the pair
was identified and merged, because counting both inflates the flow diagram and
citing the preprint reports numbers that changed during review.
""".rstrip()


# --------------------------------------------------------------------------
# self test
# --------------------------------------------------------------------------

SELF_TEST_SPEC = {
    "question": "self test",
    "framework": "PICO",
    "blocks": [
        {"name": "A", "terms": ["deep learning", "neural"], "mesh": ["Deep Learning"],
         "truncate": True},
        {"name": "B", "terms": ["histopathology"], "mesh": []},
    ],
    "limits": {"years": [2015, 2026], "languages": ["English"]},
}


def self_test() -> int:
    failures = 0

    def check(desc: str, ok: bool) -> None:
        nonlocal failures
        failures += (not ok)
        print(f"  [{'pass' if ok else 'FAIL'}] {desc}")

    print("renderers produce output for every registered platform")
    for db, fn in RENDERERS.items():
        out = fn(SELF_TEST_SPEC, False)
        check(f"{db} renders a non-empty query", bool(out and out.strip()))

    print("\nphrases are never truncated")
    for db in ("pubmed", "scopus", "ieee", "springer", "sciencedirect", "acm"):
        out = RENDERERS[db](SELF_TEST_SPEC, False)
        check(f"{db} has no truncated phrase", 'learn*"' not in out
              and '"deep learning*' not in out)

    print("\ntruncation is applied to single tokens where the platform allows it")
    check("pubmed truncates 'neural'", "neural*" in pubmed(SELF_TEST_SPEC))
    check("springer does NOT truncate", "neural*" not in springer(SELF_TEST_SPEC))

    print("\npeer-reviewed-only changes the query where the platform supports it")
    cases = [("pubmed", "preprint[pt]"), ("scopus", "DOCTYPE(ar)"),
             ("wos", "DT="), ("europepmc", "NOT SRC:PPR"),
             ("crossref", "filter=type:journal-article"),
             ("embase", "limit")]
    for db, needle in cases:
        out = RENDERERS[db](SELF_TEST_SPEC, True)
        check(f"{db} adds {needle!r}", needle in out)
        plain = RENDERERS[db](SELF_TEST_SPEC, False)
        check(f"{db} omits it without the flag", needle not in plain)

    print("\nplatform warnings fire on the failure modes they exist for")
    big = {"blocks": [{"name": "A", "terms": [f"t{i}" for i in range(30)],
                       "mesh": [], "truncate": True}], "limits": {}}
    check("springer warns about truncation",
          any("truncation" in w for w in platform_warnings(big, "springer", False)))
    check("sciencedirect warns about connector count",
          any("connector" in w for w in platform_warnings(big, "sciencedirect", True)))
    check("ieee warns about a 30-term block",
          any("ceiling" in w for w in platform_warnings(big, "ieee", False)))

    print(f"\n{'all checks passed' if not failures else str(failures) + ' check(s) FAILED'}")
    return 1 if failures else 0


# --------------------------------------------------------------------------

def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--spec", help="YAML or JSON concept-block spec")
    p.add_argument("--db", nargs="*", default=list(RENDERERS),
                   choices=list(RENDERERS), help="which platforms to render")
    p.add_argument("--example", action="store_true", help="print a starter spec")
    p.add_argument("--peer-reviewed-only", action="store_true",
                   help="restrict each platform to peer-reviewed publication "
                        "types, and say where the restriction is a UI facet")
    p.add_argument("--prisma-s", action="store_true",
                   help="also emit the PRISMA-S reporting record")
    p.add_argument("--self-test", action="store_true",
                   help="check the renderers against built-in fixtures")
    a = p.parse_args()

    if a.self_test:
        return self_test()
    if a.example:
        print(EXAMPLE)
        return 0
    if not a.spec:
        sys.exit("give --spec <file>, --example, or --self-test")

    spec = load_spec(a.spec)
    if not spec.get("blocks"):
        sys.exit("spec has no 'blocks'")

    n_terms = sum(len(b.get("terms", [])) + len(b.get("mesh", []))
                  for b in spec["blocks"])
    print(f"# Search strategy: {len(spec['blocks'])} concept blocks, "
          f"{n_terms} terms total"
          + (", peer-reviewed publication types only" if a.peer_reviewed_only
             else "") + "\n")

    for d in a.db:
        print(f"## {LABELS[d]}\n")
        print("```")
        print(RENDERERS[d](spec, a.peer_reviewed_only))
        print("```\n")
        for warn in platform_warnings(spec, d, a.peer_reviewed_only):
            print(f"> **Note.** {warn}\n")

    if a.prisma_s:
        print(prisma_s_record(spec, a.db, a.peer_reviewed_only))

    print("\n---\nBefore running these: have a librarian or a second reviewer "
          "check the strategy (PRESS). Test that known key papers are retrieved; "
          "a search that misses a paper you already know about is broken, and "
          "that check takes two minutes.")
    if not a.peer_reviewed_only:
        print("\nPreprints are in scope for these strategies. If the protocol "
              "restricts the review to the peer-reviewed record, rerun with "
              "--peer-reviewed-only and report the restriction as a PRISMA-S "
              "item rather than applying it silently.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
