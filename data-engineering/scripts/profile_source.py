#!/usr/bin/env python3
"""
Profile a data source before writing any transform.

This operationalizes step 1 of the data-engineering workflow: know the shape of
the input before you assume anything about it. It reports the facts that most
often turn into pipeline bugs when guessed: row count, per-column types and null
rates, candidate-key uniqueness, full-row duplicate rate, value ranges, and a
few real sample values per column.

Design goals:
- No hard dependency. It uses DuckDB if present (fast, streams larger-than-memory
  files, reads CSV/Parquet/JSON directly), falls back to pandas, then to a pure
  stdlib CSV reader. Backend is auto-selected but can be forced for testing.
- Read-only. It never writes to the source and never mutates it.
- Machine- and human-readable. Default output is a readable report; --format json
  emits a structured object you can diff across runs or feed to a check.

Usage:
    python profile_source.py <path> [options]
    python profile_source.py data.csv
    python profile_source.py 'events/*.parquet' --key event_id
    python profile_source.py orders.parquet --key order_id,line_no --format json
    python profile_source.py raw.tsv --delimiter '\\t' --sample 5

Options:
    --key COLS         Comma-separated column(s) to test as a (composite) key.
                       Reports uniqueness ratio and duplicate count. Repeatable.
    --sample N         Sample values shown per column (default 3).
    --top N            Top frequent values shown for low-cardinality columns
                       (default 0 = off).
    --format FMT       text (default) or json.
    --delimiter D      Field delimiter for delimited text (default: inferred).
    --backend B        auto (default), duckdb, pandas, or stdlib. For testing or
                       to pin behavior in a pipeline.
    --max-rows N       Cap rows scanned by the stdlib backend (default: all).
                       Ignored by duckdb/pandas backends.
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import sys
from dataclasses import dataclass, field, asdict
from typing import Any, Optional

# Extensions we know how to route. Anything else is treated as delimited text.
PARQUET_EXTS = {".parquet", ".pq"}
JSON_EXTS = {".json", ".ndjson", ".jsonl"}
DELIMITED_EXTS = {".csv", ".tsv", ".txt"}


# --------------------------------------------------------------------------- #
# Result model
# --------------------------------------------------------------------------- #
@dataclass
class ColumnProfile:
    name: str
    dtype: str
    null_count: int
    null_rate: float
    distinct_count: Optional[int]
    is_candidate_key: bool
    min: Any = None
    max: Any = None
    samples: list = field(default_factory=list)
    top_values: list = field(default_factory=list)  # list of [value, count]


@dataclass
class SourceProfile:
    source: str
    files: list
    total_bytes: int
    backend: str
    row_count: int
    column_count: int
    duplicate_row_count: Optional[int]
    duplicate_row_rate: Optional[float]
    columns: list  # list[ColumnProfile]
    key_checks: list = field(default_factory=list)  # list of dicts

    def to_dict(self) -> dict:
        d = asdict(self)
        return d


# --------------------------------------------------------------------------- #
# Path handling
# --------------------------------------------------------------------------- #
def resolve_files(path: str) -> list[str]:
    """Expand a path or glob into concrete files. Directories expand to their
    immediate data files. Fails loudly if nothing matches so a typo does not
    silently profile zero rows."""
    if any(ch in path for ch in "*?[") and not os.path.exists(path):
        files = sorted(glob.glob(path, recursive=True))
    elif os.path.isdir(path):
        files = sorted(
            os.path.join(path, f)
            for f in os.listdir(path)
            if os.path.splitext(f)[1].lower()
            in (PARQUET_EXTS | JSON_EXTS | DELIMITED_EXTS)
        )
    else:
        files = [path]
    files = [f for f in files if os.path.isfile(f)]
    if not files:
        raise FileNotFoundError(f"No files matched: {path}")
    return files


def infer_kind(files: list[str]) -> str:
    ext = os.path.splitext(files[0])[1].lower()
    if ext in PARQUET_EXTS:
        return "parquet"
    if ext in JSON_EXTS:
        return "json"
    return "delimited"


def sniff_delimiter(sample_path: str) -> str:
    """Guess a delimiter from the first non-empty line. Kept simple on purpose:
    tab, then the most frequent of comma/semicolon/pipe."""
    import csv

    with open(sample_path, "r", newline="", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            if line.strip():
                try:
                    return csv.Sniffer().sniff(line, delimiters=",\t;|").delimiter
                except csv.Error:
                    counts = {d: line.count(d) for d in [",", "\t", ";", "|"]}
                    return max(counts, key=counts.get) or ","
    return ","


# --------------------------------------------------------------------------- #
# Backend selection
# --------------------------------------------------------------------------- #
def pick_backend(requested: str) -> str:
    if requested != "auto":
        return requested
    if _has("duckdb"):
        return "duckdb"
    if _has("pandas"):
        return "pandas"
    return "stdlib"


def _has(mod: str) -> bool:
    try:
        __import__(mod)
        return True
    except Exception:
        return False


# --------------------------------------------------------------------------- #
# DuckDB backend (preferred: handles CSV/Parquet/JSON, streams big files)
# --------------------------------------------------------------------------- #
def profile_duckdb(files, kind, keys, sample_n, top_n, delimiter):
    import duckdb

    con = duckdb.connect()
    src = _duckdb_relation(files, kind, delimiter)
    con.execute(f"CREATE VIEW src AS SELECT * FROM {src}")

    cols = con.execute("DESCRIBE src").fetchall()  # (name, type, ...)
    row_count = con.execute("SELECT count(*) FROM src").fetchone()[0]

    columns = []
    for name, dtype, *_ in cols:
        q = con.execute(
            f'SELECT count(*) - count("{name}"), count(DISTINCT "{name}") FROM src'
        ).fetchone()
        null_count, distinct = int(q[0]), int(q[1])
        cmin = cmax = None
        try:
            cmin, cmax = con.execute(
                f'SELECT min("{name}"), max("{name}") FROM src WHERE "{name}" IS NOT NULL'
            ).fetchone()
        except Exception:
            pass  # types like nested/blob have no ordering; leave range empty
        samples = [
            r[0]
            for r in con.execute(
                f'SELECT "{name}" FROM src WHERE "{name}" IS NOT NULL LIMIT {sample_n}'
            ).fetchall()
        ]
        top = []
        if top_n and distinct <= 1000:
            top = [
                [r[0], int(r[1])]
                for r in con.execute(
                    f'SELECT "{name}", count(*) c FROM src GROUP BY 1 '
                    f"ORDER BY c DESC LIMIT {top_n}"
                ).fetchall()
            ]
        non_null = row_count - null_count
        columns.append(
            ColumnProfile(
                name=name,
                dtype=str(dtype),
                null_count=null_count,
                null_rate=_rate(null_count, row_count),
                distinct_count=distinct,
                is_candidate_key=(non_null == row_count and distinct == row_count and row_count > 0),
                min=_jsonable(cmin),
                max=_jsonable(cmax),
                samples=[_jsonable(s) for s in samples],
                top_values=[[_jsonable(v), c] for v, c in top],
            )
        )

    dup_count = _duckdb_full_dup(con, [c[0] for c in cols], row_count)
    key_checks = [_duckdb_key_check(con, k, row_count) for k in keys]
    con.close()
    return row_count, len(cols), dup_count, columns, key_checks


def _duckdb_relation(files, kind, delimiter):
    lst = "[" + ",".join(f"'{f}'" for f in files) + "]"
    if kind == "parquet":
        return f"read_parquet({lst})"
    if kind == "json":
        return f"read_json_auto({lst})"
    delim = f", delim='{delimiter}'" if delimiter else ""
    return f"read_csv_auto({lst}, sample_size=-1{delim})"


def _duckdb_full_dup(con, colnames, row_count):
    cols = ", ".join(f'"{c}"' for c in colnames)
    distinct_rows = con.execute(f"SELECT count(*) FROM (SELECT DISTINCT {cols} FROM src)").fetchone()[0]
    return row_count - int(distinct_rows)


def _duckdb_key_check(con, key_cols, row_count):
    cols = ", ".join(f'"{c}"' for c in key_cols)
    total, distinct, nulls = con.execute(
        f"SELECT count(*), count(DISTINCT ({cols})), "
        f"count(*) - count(({cols})) FROM src"
    ).fetchone()
    return _key_result(key_cols, int(total), int(distinct), int(nulls))


# --------------------------------------------------------------------------- #
# pandas backend
# --------------------------------------------------------------------------- #
def profile_pandas(files, kind, keys, sample_n, top_n, delimiter):
    import pandas as pd

    frames = [_pandas_read(f, kind, delimiter) for f in files]
    df = pd.concat(frames, ignore_index=True) if len(frames) > 1 else frames[0]
    row_count = len(df)

    columns = []
    for name in df.columns:
        s = df[name]
        null_count = int(s.isna().sum())
        distinct = int(s.nunique(dropna=True))
        non_null = row_count - null_count
        cmin = cmax = None
        try:
            if non_null:
                cmin, cmax = _jsonable(s.min()), _jsonable(s.max())
        except (TypeError, ValueError):
            pass
        samples = [_jsonable(v) for v in s.dropna().head(sample_n).tolist()]
        top = []
        if top_n and distinct <= 1000:
            vc = s.value_counts(dropna=True).head(top_n)
            top = [[_jsonable(v), int(c)] for v, c in vc.items()]
        columns.append(
            ColumnProfile(
                name=str(name),
                dtype=str(s.dtype),
                null_count=null_count,
                null_rate=_rate(null_count, row_count),
                distinct_count=distinct,
                is_candidate_key=(non_null == row_count and distinct == row_count and row_count > 0),
                min=cmin,
                max=cmax,
                samples=samples,
                top_values=top,
            )
        )

    dup_count = int(df.duplicated().sum())
    key_checks = []
    for k in keys:
        sub = df[list(k)]
        nulls = int(sub.isna().any(axis=1).sum())
        distinct = int(sub.drop_duplicates().shape[0])
        key_checks.append(_key_result(k, row_count, distinct, nulls))
    return row_count, df.shape[1], dup_count, columns, key_checks


def _pandas_read(path, kind, delimiter):
    import pandas as pd

    if kind == "parquet":
        return pd.read_parquet(path)
    if kind == "json":
        # ndjson/jsonl are line-delimited; a bare .json may be an array.
        lines = os.path.splitext(path)[1].lower() in {".ndjson", ".jsonl"}
        return pd.read_json(path, lines=lines)
    return pd.read_csv(path, sep=delimiter or None, engine="python")


# --------------------------------------------------------------------------- #
# stdlib backend (CSV/TSV only, streaming, zero dependencies)
# --------------------------------------------------------------------------- #
def profile_stdlib(files, keys, sample_n, top_n, delimiter, max_rows):
    import csv
    from collections import Counter

    delimiter = delimiter or sniff_delimiter(files[0])
    header = None
    null_counts, distinct_sets, samples, mins, maxes = {}, {}, {}, {}, {}
    top_counters = {}
    row_count = 0
    full_row_seen = Counter()
    key_seen = [Counter() for _ in keys]
    key_null = [0 for _ in keys]

    for path in files:
        with open(path, "r", newline="", encoding="utf-8", errors="replace") as fh:
            reader = csv.reader(fh, delimiter=delimiter)
            file_header = next(reader, None)
            if file_header is None:
                continue
            if header is None:
                header = file_header
                for c in header:
                    null_counts[c] = 0
                    distinct_sets[c] = set()
                    samples[c] = []
                    mins[c] = None
                    maxes[c] = None
                    top_counters[c] = Counter()
            for row in reader:
                if max_rows is not None and row_count >= max_rows:
                    break
                row_count += 1
                # pad/truncate ragged rows to header width
                row = (row + [""] * len(header))[: len(header)]
                full_row_seen[tuple(row)] += 1
                for i, c in enumerate(header):
                    v = row[i]
                    if v == "" or v is None:
                        null_counts[c] += 1
                        continue
                    if len(distinct_sets[c]) < 200_000:
                        distinct_sets[c].add(v)
                    if len(samples[c]) < sample_n:
                        samples[c].append(v)
                    if top_n:
                        top_counters[c][v] += 1
                    mn, mx = _numeric_or_str(v)
                    mins[c] = mn if mins[c] is None else min(mins[c], mn, key=_cmp_key)
                    maxes[c] = mx if maxes[c] is None else max(maxes[c], mx, key=_cmp_key)
                for j, kcols in enumerate(keys):
                    idxs = [header.index(kc) for kc in kcols]
                    vals = tuple(row[ix] for ix in idxs)
                    if any(x == "" for x in vals):
                        key_null[j] += 1
                    else:
                        key_seen[j][vals] += 1

    columns = []
    for c in header:
        distinct = len(distinct_sets[c])
        non_null = row_count - null_counts[c]
        columns.append(
            ColumnProfile(
                name=c,
                dtype="string",  # stdlib does not type-infer; report as read
                null_count=null_counts[c],
                null_rate=_rate(null_counts[c], row_count),
                distinct_count=distinct if distinct < 200_000 else None,
                is_candidate_key=(non_null == row_count and distinct == row_count and row_count > 0),
                min=mins[c],
                max=maxes[c],
                samples=samples[c],
                top_values=[[v, n] for v, n in top_counters[c].most_common(top_n)] if top_n else [],
            )
        )

    dup_count = sum(n - 1 for n in full_row_seen.values() if n > 1)
    key_checks = []
    for j, kcols in enumerate(keys):
        distinct = len(key_seen[j])
        key_checks.append(_key_result(kcols, row_count, distinct, key_null[j]))
    return row_count, len(header), dup_count, columns, key_checks


def _numeric_or_str(v):
    try:
        f = float(v)
        return f, f
    except (TypeError, ValueError):
        return v, v


def _cmp_key(x):
    # Order numbers before strings deterministically without raising on mixed types.
    return (0, x) if isinstance(x, (int, float)) else (1, str(x))


# --------------------------------------------------------------------------- #
# Shared helpers
# --------------------------------------------------------------------------- #
def _rate(part, whole):
    return round(part / whole, 4) if whole else 0.0


def _key_result(key_cols, total, distinct, nulls):
    non_null = total - nulls
    unique = non_null == distinct and nulls == 0 and total > 0
    return {
        "key": list(key_cols),
        "rows": total,
        "distinct": distinct,
        "null_rows": nulls,
        "uniqueness_ratio": _rate(distinct, non_null) if non_null else 0.0,
        "is_unique": unique,
        "duplicate_rows": non_null - distinct,
    }


def _jsonable(v):
    if v is None:
        return None
    if isinstance(v, (str, int, float, bool)):
        return v
    return str(v)


# --------------------------------------------------------------------------- #
# Reporting
# --------------------------------------------------------------------------- #
def render_text(p: SourceProfile) -> str:
    out = []
    out.append(f"Source:   {p.source}")
    out.append(f"Files:    {len(p.files)} ({_human_bytes(p.total_bytes)})  backend={p.backend}")
    out.append(f"Rows:     {p.row_count:,}    Columns: {p.column_count}")
    if p.duplicate_row_count is not None:
        out.append(
            f"Dup rows: {p.duplicate_row_count:,} "
            f"({_rate(p.duplicate_row_count, p.row_count) * 100:.2f}% of rows)"
        )
    out.append("")

    name_w = max((len(c["name"]) for c in _cols(p)), default=6)
    name_w = max(name_w, 6)
    out.append(f"{'column'.ljust(name_w)}  {'type':<12} {'null%':>7} {'distinct':>10}  key  range / samples")
    out.append("-" * (name_w + 52))
    for c in _cols(p):
        key = " PK " if c["is_candidate_key"] else "  . "
        dist = "n/a" if c["distinct_count"] is None else f"{c['distinct_count']:,}"
        rng = ""
        if c["min"] is not None or c["max"] is not None:
            rng = f"[{_short(c['min'])} .. {_short(c['max'])}]"
        elif c["samples"]:
            rng = "e.g. " + ", ".join(_short(s) for s in c["samples"][:3])
        out.append(
            f"{c['name'].ljust(name_w)}  {c['dtype'][:12]:<12} "
            f"{c['null_rate'] * 100:>6.2f}% {dist:>10}  {key} {rng}"
        )

    if p.key_checks:
        out.append("")
        out.append("Key checks:")
        for k in p.key_checks:
            verdict = "UNIQUE" if k["is_unique"] else "NOT UNIQUE"
            out.append(
                f"  ({', '.join(k['key'])}): {verdict}  "
                f"distinct={k['distinct']:,} dup_rows={k['duplicate_rows']:,} "
                f"null_rows={k['null_rows']:,} ratio={k['uniqueness_ratio']:.4f}"
            )

    # Actionable nudges tied to the workflow, not decoration.
    flags = _flags(p)
    if flags:
        out.append("")
        out.append("Flags:")
        out.extend(f"  - {f}" for f in flags)
    return "\n".join(out)


def _flags(p: SourceProfile) -> list[str]:
    flags = []
    if p.row_count == 0:
        flags.append("Zero rows. Verify the path/window before building on this.")
    if p.duplicate_row_count:
        flags.append(
            f"{p.duplicate_row_count:,} fully duplicated rows. Decide grain and dedup before load."
        )
    if not any(c["is_candidate_key"] for c in _cols(p)) and not any(
        k["is_unique"] for k in p.key_checks
    ):
        flags.append("No single-column candidate key found. Confirm the grain and composite key.")
    for c in _cols(p):
        if c["null_rate"] == 1.0 and p.row_count:
            flags.append(f"Column '{c['name']}' is entirely NULL. Drop or investigate.")
    return flags


def _cols(p):
    return p.columns if isinstance(p.columns[0], dict) else [asdict(c) for c in p.columns]


def _short(v, n=22):
    s = "NULL" if v is None else str(v)
    return s if len(s) <= n else s[: n - 1] + "\u2026"


def _human_bytes(n):
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if n < 1024 or unit == "TB":
            return f"{n:.0f} {unit}" if unit == "B" else f"{n:.1f} {unit}"
        n /= 1024


# --------------------------------------------------------------------------- #
# Entry point
# --------------------------------------------------------------------------- #
def parse_args(argv):
    ap = argparse.ArgumentParser(description="Profile a data source (read-only).")
    ap.add_argument("path", help="File, directory, or glob to profile.")
    ap.add_argument("--key", action="append", default=[], help="Comma-separated key column(s). Repeatable.")
    ap.add_argument("--sample", type=int, default=3)
    ap.add_argument("--top", type=int, default=0)
    ap.add_argument("--format", choices=["text", "json"], default="text")
    ap.add_argument("--delimiter", default=None)
    ap.add_argument("--backend", choices=["auto", "duckdb", "pandas", "stdlib"], default="auto")
    ap.add_argument("--max-rows", type=int, default=None)
    return ap.parse_args(argv)


def main(argv=None):
    args = parse_args(argv if argv is not None else sys.argv[1:])
    files = resolve_files(args.path)
    kind = infer_kind(files)
    keys = [tuple(c.strip() for c in k.split(",") if c.strip()) for k in args.key]
    backend = pick_backend(args.backend)

    if backend == "stdlib" and kind != "delimited":
        sys.exit(
            f"error: {kind} files need duckdb or pandas installed. "
            f"Install one (pip install duckdb) or point at delimited text."
        )

    if backend == "duckdb":
        rc, cc, dup, cols, kc = profile_duckdb(files, kind, keys, args.sample, args.top, args.delimiter)
    elif backend == "pandas":
        rc, cc, dup, cols, kc = profile_pandas(files, kind, keys, args.sample, args.top, args.delimiter)
    else:
        rc, cc, dup, cols, kc = profile_stdlib(files, keys, args.sample, args.top, args.delimiter, args.max_rows)

    profile = SourceProfile(
        source=args.path,
        files=files,
        total_bytes=sum(os.path.getsize(f) for f in files),
        backend=backend,
        row_count=rc,
        column_count=cc,
        duplicate_row_count=dup,
        duplicate_row_rate=_rate(dup, rc) if dup is not None else None,
        columns=cols,
        key_checks=kc,
    )

    if args.format == "json":
        print(json.dumps(profile.to_dict(), indent=2, default=_jsonable))
    else:
        print(render_text(profile))


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        # Downstream closed the pipe (e.g. `| head`); exit quietly.
        try:
            sys.stdout.close()
        except Exception:
            pass
        os._exit(0)
    except (FileNotFoundError, ValueError) as exc:
        sys.exit(f"error: {exc}")
