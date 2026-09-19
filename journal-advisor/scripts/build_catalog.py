#!/usr/bin/env python3
"""Combine original institution workbooks and researched fee-route CSVs.

Read the workbooks and CSVs in assets/sources. The master keeps separate
funding-route evidence linked by journal identity; its rows are not unique
journals. Every record retains its source locator and policy links.

    python scripts/build_catalog.py                     # rebuild in place
    python scripts/build_catalog.py --out /tmp/new.csv  # rebuild elsewhere

Parsing rules per source are documented inline below and summarized in
references/catalog-schema.md. The governing principle: never synthesize a value
that is absent from the source. A missing quartile stays empty rather than being
filled from another metric or from memory.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
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
    "list_context", "list_kind", "coverage_note", "fee_note",
    "source_file", "source_sheet", "source_row",
]

PROVENANCE_FILE = HERE.parent / "assets" / "list-provenance.yaml"

# The fee-route CSVs in assets/sources share this header. Every route carries
# its own cost terms, its own eligibility, and its own provenance, because a
# journal reached by two routes is two different offers to the author.
ROUTE_COLUMNS = [
    "publisher", "journal_title", "issn", "eissn", "journal_url",
    "subject_area", "scope", "oa_model",
    "fee_route", "institution", "apc_payable", "other_fees", "eligibility",
    "agreement_start", "agreement_end", "annual_cap", "article_types",
    "evidence_status", "record_status",
    "source_url", "policy_url", "checked_on", "source_updated",
    "source_file", "source_row", "source_record_id",
    "license", "languages", "country",
    "doaj_url", "instructions_url", "apc_information_url", "other_fees_url",
    "notes",
]
COLUMNS += [c for c in ROUTE_COLUMNS if c not in COLUMNS] + ["journal_id", "route_id"]

# The researched fee-route CSVs, in the order they enter the master.
ROUTE_SOURCES = [
    ("uf_100_percent_apc.csv", "UF agreements stating full APC coverage"),
    ("no_apc_open_access.csv", "DOAJ APC=No declarations plus checked publisher policies"),
    ("subscribe_to_open.csv", "Subscribe to Open titles with their funded year"),
    ("subscription_no_apc.csv", "non-OA publication carrying no OA APC"),
]


def load_provenance() -> dict:
    """Per-publisher kind, scope, institution, agreement, and fee note from
    assets/list-provenance.yaml. The report quotes these so a user knows
    whether an absent journal is absent from the publisher or from an
    institution's agreement."""
    if not PROVENANCE_FILE.exists():
        return {}
    import yaml  # type: ignore
    return yaml.safe_load(PROVENANCE_FILE.read_text(encoding="utf-8")) or {}


def assign_ids(rows):
    """Link p/e-ISSNs transitively; retain each independent fee route."""
    parent = list(range(len(rows)))
    def root(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i
    def union(a, b):
        parent[root(b)] = root(a)
    issns, titles = {}, {}
    for i, r in enumerate(rows):
        ids = [re.sub(r"[^0-9X]", "", r.get(k, "").upper()) for k in ("issn", "eissn")]
        for ident in filter(None, ids):
            if ident in issns:
                union(i, issns[ident])
            issns[ident] = i
        title = re.sub(r"\W+", "", r["journal_title"].casefold())
        # Avoid joining different journals with a generic title and distinct ISSNs.
        for j, has_issn in titles.get(title, []):
            if not any(ids) or not has_issn:
                union(i, j)
        titles.setdefault(title, []).append((i, any(ids)))
    groups = {}
    for i, r in enumerate(rows):
        groups.setdefault(root(i), []).append(r)
    for group in groups.values():
        ids = sorted({re.sub(r"[^0-9X]", "", r.get(k, "").upper()) for r in group for k in ("issn", "eissn")} - {""})
        key = ids[0] if ids else min(r["publisher"] + ":" + r["journal_title"] for r in group).casefold()
        jid = "j-" + hashlib.sha256(key.encode()).hexdigest()[:16]
        for r in group:
            r["journal_id"] = jid
            key = "|".join(str(r.get(k, "")) for k in ("journal_id", "fee_route", "institution", "source_file", "source_row", "source_record_id"))
            r["route_id"] = "r-" + hashlib.sha256(key.encode()).hexdigest()[:16]


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
# institution workbook parsers: one per bundled .xlsx
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
            source_file="T_F.xlsx", source_sheet="Open Access", source_row=i + 2,
        ))
    return out


# --------------------------------------------------------------------------
# researched fee-route CSVs: already in ROUTE_COLUMNS shape
# --------------------------------------------------------------------------

def parse_route_csv(name: str) -> list[dict]:
    """Read one researched fee-route CSV as written.

    These files are the research record, so nothing is recomputed here. The
    three display fields the report quotes are mirrored from the route's own
    evidence, and the quartile basis says plainly that no metric was supplied.
    """
    out = []
    with (SRC / name).open(encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            r.update(list_kind=r["evidence_status"], coverage_note=r["eligibility"],
                     fee_note=r["notes"],
                     quartile_basis="not stated in source list")
            out.append(r)
    return out


def apply_institution_routes(rows: list[dict], prov: dict) -> None:
    """Turn the bundled workbook titles into `institutional_oa` route records.

    The MUJ and JKLU mapping came from the user on 2026-09-19 and no contract
    was supplied with it, so every row says `user_confirmed_mapping` and keeps
    the conditions in `eligibility`. Zero APC here describes the route if its
    conditions hold, never an approval for a particular author.
    """
    for r in rows:
        pv = prov.get(r["publisher"], {})
        inst = pv.get("institution", "")
        named = inst and not inst.startswith("[AUTHOR")
        r["list_kind"] = pv.get("kind", "")
        r["list_context"] = pv.get("scope", "")
        r["coverage_note"] = (r["list_context"] + (f" [{inst}]" if named else "")).strip()
        r["fee_note"] = pv.get("fee_note", "")
        r.update(
            fee_route="institutional_oa",
            institution="JKLU" if r["publisher"] == "ACM" else "MUJ",
            apc_payable="0", other_fees="unknown",
            evidence_status="user_confirmed_mapping", record_status="listed",
            checked_on="2026-09-19", source_updated=pv.get("exported", ""),
            eligibility="User identifies this bundled list as institution-sponsored. "
                        "Confirm corresponding-author eligibility, current term, "
                        "article type and allocation.",
            notes="Institution mapping confirmed by user 2026-09-19; current contract "
                  "and per-author approval not independently established.",
        )


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

    prov = load_provenance()
    if prov:
        print("provenance: " + "; ".join(f"{k}: {v.get('kind', '?')}"
                                         for k, v in prov.items()))
    else:
        print("note: assets/list-provenance.yaml not read (missing or no PyYAML); "
              "list_kind left empty")
    apply_institution_routes(rows, prov)

    for name, what in ROUTE_SOURCES:
        got = parse_route_csv(name)
        print(f"{name:<26} {len(got):>5} routes  ({what})")
        rows.extend(got)

    assign_ids(rows)
    df = pd.DataFrame(rows, columns=COLUMNS).fillna("")
    dupes = df.duplicated(subset=["publisher", "journal_title"]).sum()
    if dupes:
        print(f"note: {dupes} repeated publisher+title rows retained as separate fee routes/evidence")
    df.to_csv(a.out, index=False)
    print(f"\nwrote {len(df)} rows to {a.out}")
    summary = {"built_from_snapshot": "2026-09-19", "route_rows": len(df),
               "distinct_journal_ids": df.journal_id.nunique(),
               "routes": df.fee_route.value_counts().to_dict(),
               "record_status": df.record_status.value_counts().to_dict()}
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
