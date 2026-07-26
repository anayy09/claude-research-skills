#!/usr/bin/env python3
"""Normalize the five publisher spreadsheets into a single catalog CSV.

Run this only when a source spreadsheet is replaced with a newer edition. The
shipped assets/journals.csv is the output of this script against the bundled
sources, so the catalog is always reconstructible and every row keeps a pointer
back to the file, sheet, and row it came from.

    python scripts/build_catalog.py                     # rebuild in place
    python scripts/build_catalog.py --out /tmp/new.csv  # rebuild elsewhere

Parsing rules per source are documented inline below and summarized in
references/catalog-schema.md. The governing principle: never synthesize a value
that is absent from the source. A missing quartile stays empty rather than being
filled from another metric or from memory.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
SRC = HERE.parent / "assets" / "sources"
DEFAULT_OUT = HERE.parent / "assets" / "journals.csv"

COLUMNS = [
    "publisher", "journal_title", "acronym", "issn", "eissn",
    "oa_model", "subject_area", "imprint", "scope", "journal_url",
    "index_wos", "scopus_covered",
    "jif_2024", "jif_quartile", "citescore_2024", "citescore_quartile",
    "sjr_2024", "sjr_quartile", "best_quartile", "quartile_basis",
    "list_context", "source_file", "source_sheet", "source_row",
]

# What each uploaded list actually is. This matters: none of them is "every
# journal the publisher owns", so a title's absence is not evidence that the
# journal does not exist, only that it is outside the permitted set.
LIST_CONTEXT = {
    "IEEE": "IEEE title list with open-access type and 2024 JCR/CiteScore metrics; "
            "data stated accurate as of 1 January 2026",
    "Springer Nature": "Journals eligible under a Springer Nature fully-open-access "
                       "agreement; discipline and imprint only, no citation metrics",
    "Elsevier": "Institutional eligible publication list (MUJ 2025); hybrid titles "
                "with CiteScore 2024 quartile only",
    "ACM": "ACM journal list; ACM journals are open access as of 1 January 2026 per "
           "the ACM publications overview cited in the workbook Notes sheet",
    "Taylor & Francis": "Taylor & Francis open-access title list with 2024 JCR, "
                        "CiteScore, SNIP and SJR metrics",
}


def clean(v) -> str:
    """Collapse embedded newlines and non-breaking spaces. Springer's export
    wraps long cell text with hard newlines, which would otherwise split titles
    like 'Acta Neuropathologica\\nCommunications' during matching."""
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return ""
    s = str(v).replace("\xa0", " ").replace("\n", " ").replace("\r", " ")
    s = re.sub(r"\s+", " ", s).strip()
    return "" if s.lower() in {"nan", "none", "-", "n/a", "na"} else s


def q(v) -> str:
    """Normalize a quartile cell to Q1..Q4 or empty. Anything unrecognized is
    dropped rather than guessed."""
    s = clean(v).upper().replace(" ", "")
    return s if s in {"Q1", "Q2", "Q3", "Q4"} else ""


def num(v) -> str:
    s = clean(v)
    try:
        return f"{float(s):g}"
    except ValueError:
        return ""


def best_quartile(jif: str, cite: str, sjr: str) -> tuple[str, str]:
    """Best available quartile with the metric it came from named.

    Different publishers report different metrics, so a single comparable field
    is needed for ranking. Naming the basis keeps the comparison honest: a Q1 on
    CiteScore and a Q1 on JIF are not the same claim.
    """
    options = [(jif, "JIF 2024"), (cite, "CiteScore 2024"), (sjr, "SJR 2024")]
    present = [(v, b) for v, b in options if v]
    if not present:
        return "", "not stated in source list"
    val, basis = min(present, key=lambda t: int(t[0][1]))
    return val, basis


def row(**kw) -> dict:
    r = {c: "" for c in COLUMNS}
    r.update(kw)
    return r


# --------------------------------------------------------------------------
# per-publisher parsers
# --------------------------------------------------------------------------

def parse_ieee() -> list[dict]:
    """Header is on the second row; the first is a banner. The last eight rows
    are footnotes about JCR sourcing and renamed titles, identified by a missing
    Publication Title rather than by row position."""
    f = SRC / "IEEE.xlsx"
    df = pd.read_excel(f, sheet_name="Title List", header=1)
    out = []
    for i, r in df.iterrows():
        title = clean(r.get("Publication Title"))
        if not title:
            continue
        jq = q(r.get("Quartile (JIF)"))
        bq, basis = best_quartile(jq, "", "")
        out.append(row(
            publisher="IEEE",
            journal_title=title,
            acronym=clean(r.get("Publication Acronym")),
            issn=clean(r.get("ISSN")),
            eissn=clean(r.get("eISSN")),
            oa_model=clean(r.get("Open Access Type")),
            index_wos=clean(r.get("Index")),
            jif_2024=num(r.get("Journal Impact Factor (JIF)*")),
            jif_quartile=jq,
            citescore_2024=num(r.get("CiteScore")),
            sjr_2024="",
            best_quartile=bq, quartile_basis=basis,
            list_context=LIST_CONTEXT["IEEE"],
            source_file="IEEE.xlsx", source_sheet="Title List", source_row=i + 3,
        ))
    return out


def parse_springer() -> list[dict]:
    """Six banner rows precede the header. No citation metrics are present in
    this list at all, so quartile stays empty for every Springer row."""
    f = SRC / "Springer_Nature.xlsx"
    df = pd.read_excel(f, sheet_name="FOA Agreement Journals List", header=6)
    out = []
    for i, r in df.iterrows():
        title = clean(r.get("Journal Title"))
        if not title:
            continue
        out.append(row(
            publisher="Springer Nature",
            journal_title=title,
            eissn=clean(r.get("eISSN")),
            oa_model=clean(r.get("Publishing Model")),
            subject_area=clean(r.get("Main Discipline")),
            imprint=clean(r.get("Imprint")),
            best_quartile="", quartile_basis="not stated in source list",
            list_context=LIST_CONTEXT["Springer Nature"],
            source_file="Springer_Nature.xlsx",
            source_sheet="FOA Agreement Journals List", source_row=i + 8,
        ))
    return out


def parse_elsevier() -> list[dict]:
    """Four columns only. Quartile is CiteScore-based; nine rows carry '-' and
    are normalized to empty rather than to Q4."""
    f = SRC / "Elsevier.xlsx"
    df = pd.read_excel(f, sheet_name="MUJ 2025 eligible pub list")
    cq_col = [c for c in df.columns if "Quartile" in str(c)][0]
    oa_col = [c for c in df.columns if "OA Type" in str(c)][0]
    out = []
    for i, r in df.iterrows():
        title = clean(r.get("Journal_Title"))
        if not title:
            continue
        cq = q(r.get(cq_col))
        bq, basis = best_quartile("", cq, "")
        out.append(row(
            publisher="Elsevier",
            journal_title=title,
            issn=clean(r.get("ISSN")),
            oa_model=clean(r.get(oa_col)),
            citescore_quartile=cq,
            best_quartile=bq, quartile_basis=basis,
            list_context=LIST_CONTEXT["Elsevier"],
            source_file="Elsevier.xlsx",
            source_sheet="MUJ 2025 eligible pub list", source_row=i + 2,
        ))
    return out


def parse_acm() -> list[dict]:
    """Scope text is present for 18 of 70 titles; the workbook Notes sheet says
    blank fields were absent from the source, so they stay blank."""
    f = SRC / "ACM.xlsx"
    df = pd.read_excel(f, sheet_name="ACM Journals")
    out = []
    for i, r in df.iterrows():
        title = clean(r.get("Publication Title"))
        if not title:
            continue
        out.append(row(
            publisher="ACM",
            journal_title=title,
            acronym=clean(r.get("Publication Acronym")),
            issn=clean(r.get("ISSN")),
            eissn=clean(r.get("eISSN")),
            oa_model=clean(r.get("Open Access Type")),
            scope=clean(r.get("Description / Scope")),
            journal_url=clean(r.get("Journal URL")),
            best_quartile="", quartile_basis="not stated in source list",
            list_context=LIST_CONTEXT["ACM"],
            source_file="ACM.xlsx", source_sheet="ACM Journals", source_row=i + 2,
        ))
    return out


def parse_tf() -> list[dict]:
    """The richest list: WoS/Scopus coverage plus JIF, CiteScore and SJR
    quartiles. Best quartile prefers JIF, then CiteScore, then SJR."""
    f = SRC / "T_F.xlsx"
    df = pd.read_excel(f, sheet_name="Open Access")
    out = []
    for i, r in df.iterrows():
        title = clean(r.get("Title"))
        if not title:
            continue
        jq = q(r.get("2024 Impact Factor Best Quartile"))
        cq = q(r.get("2024 CiteScore Best Quartile"))
        sq = q(r.get("2024 SJR Quartile"))
        bq, basis = best_quartile(jq, cq, sq)
        out.append(row(
            publisher="Taylor & Francis",
            journal_title=title,
            acronym=clean(r.get("Acronym")),
            issn=clean(r.get("Print ISSN")),
            eissn=clean(r.get("Online ISSN")),
            oa_model=clean(r.get("Open Access Model")),
            subject_area=clean(r.get("Subject Area")),
            imprint=clean(r.get("Major Imprint")),
            index_wos=clean(r.get("Web of Science Covered")),
            scopus_covered=clean(r.get("Scopus covered?")),
            jif_2024=num(r.get("2024 Impact Factor")), jif_quartile=jq,
            citescore_2024=num(r.get("2024 CiteScore")), citescore_quartile=cq,
            sjr_2024=num(r.get("2024 SJR")), sjr_quartile=sq,
            best_quartile=bq, quartile_basis=basis,
            list_context=LIST_CONTEXT["Taylor & Francis"],
            source_file="T_F.xlsx", source_sheet="Open Access", source_row=i + 2,
        ))
    return out


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--out", default=str(DEFAULT_OUT))
    a = p.parse_args()

    rows: list[dict] = []
    for name, fn in [("IEEE", parse_ieee), ("Springer Nature", parse_springer),
                     ("Elsevier", parse_elsevier), ("ACM", parse_acm),
                     ("Taylor & Francis", parse_tf)]:
        got = fn()
        print(f"{name:<18} {len(got):>5} titles")
        rows.extend(got)

    df = pd.DataFrame(rows, columns=COLUMNS)
    dupes = df.duplicated(subset=["publisher", "journal_title"]).sum()
    if dupes:
        print(f"note: {dupes} duplicate publisher+title rows retained "
              f"(they exist in the source lists)")
    df.to_csv(a.out, index=False)
    print(f"\nwrote {len(df)} rows to {a.out}")
    print("\nquartile coverage by publisher:")
    cov = df.groupby("publisher").apply(
        lambda g: f"{(g.best_quartile != '').sum()}/{len(g)}", include_groups=False)
    for k, v in cov.items():
        print(f"  {k:<18} {v}")


if __name__ == "__main__":
    main()
