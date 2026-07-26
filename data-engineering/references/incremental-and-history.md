# Incremental load and history

The hard parts of a pipeline that reruns forever: process only what changed,
survive late and out-of-order data, backfill without a separate code path, and
track history on purpose. Contents:

- [High-water-mark extraction](#high-water-mark-extraction)
- [Trailing-window reprocessing for late data](#trailing-window-reprocessing-for-late-data)
- [Backfill on the same code path](#backfill-on-the-same-code-path)
- [History tracking: pick one on purpose](#history-tracking-pick-one-on-purpose)
- [SCD Type 2 merge](#scd-type-2-merge)
- [Change-data-capture notes](#change-data-capture-notes)

## High-water-mark extraction

Track the last successfully loaded position and pull only rows beyond it. Two
things make this correct rather than merely working:

1. Advance the mark only after the load validates. If the process dies mid-load,
   the next run reprocesses the window instead of skipping it.
2. Combine the mark with an idempotent write (upsert or partition overwrite) so
   reprocessing the overlap does not duplicate.

```python
def run_incremental(con, stream: str, safety_days: int = 2) -> None:
    (mark,) = con.execute(
        "SELECT watermark FROM etl_state WHERE stream = ?", [stream]
    ).fetchone() or (None,)

    lower = "'1900-01-01'" if mark is None else f"'{mark}'::timestamp - INTERVAL '{safety_days}' DAY"

    con.execute(f"""
        CREATE OR REPLACE TEMP TABLE window_rows AS
        SELECT * FROM source WHERE updated_at >= {lower}
    """)

    # validate window_rows here (see validation.md) BEFORE the upsert

    con.execute("""
        INSERT INTO target SELECT * FROM window_rows
        ON CONFLICT (id) DO UPDATE SET
            updated_at = EXCLUDED.updated_at, amount = EXCLUDED.amount
        WHERE target.updated_at < EXCLUDED.updated_at
    """)

    # advance the mark ONLY now, after a validated, committed load
    new_mark = con.execute("SELECT max(updated_at) FROM window_rows").fetchone()[0]
    if new_mark is not None:
        con.execute(
            "UPDATE etl_state SET watermark = ? WHERE stream = ?", [new_mark, stream]
        )
```

## Trailing-window reprocessing for late data

Sources deliver corrections and late-arriving rows after their event time. Every
run reprocessing a trailing window (the `safety_days` above) lets those land
without a full rebuild. The window's width is a decision: wide enough to catch
your real lateness distribution, narrow enough to stay cheap. Because the write
is idempotent, reprocessing the overlap is free of side effects.

## Backfill on the same code path

A historical range should reuse the daily code, not a bespoke script that drifts
from it. Parameterize by window and loop.

```python
from datetime import date, timedelta

def daterange(start: date, end: date):
    d = start
    while d <= end:
        yield d
        d += timedelta(days=1)

# Daily run: process_window(day, day). Backfill: the same function per day.
for day in daterange(date(2024, 1, 1), date(2024, 3, 31)):
    process_window(con, start=day, end=day)   # idempotent per partition
```

Backfilling per partition (rather than one giant range) keeps each unit
restartable and bounds memory. If a partition fails, you rerun that one.

## History tracking: pick one on purpose

State the strategy before writing the table; it determines the grain and key.

- **Overwrite** (no history): current-state table, one row per key. Cheapest.
  Use when consumers never ask "what was it on date X".
- **Append event log**: one immutable row per event, never updated. History is
  implicit in the log. Grain is the event, not the entity.
- **Slowly changing dimension Type 2**: one row per key per version, with
  `valid_from`, `valid_to`, and an `is_current` flag. Use when you must
  reconstruct the entity's state as of any past date.

## SCD Type 2 merge

Close the current row and open a new version only when a tracked attribute
actually changes. Late and out-of-order records are the trap: a change with an
older effective date must be inserted into the correct position, not appended as
if it were the newest.

```sql
-- Step 1: close current versions whose tracked attributes changed.
UPDATE dim_customer d
SET valid_to = s.effective_from, is_current = FALSE
FROM staging s
WHERE d.customer_id = s.customer_id
  AND d.is_current
  AND (d.tier, d.region) IS DISTINCT FROM (s.tier, s.region);

-- Step 2: insert the new current version for changed or new keys.
INSERT INTO dim_customer (customer_id, tier, region, valid_from, valid_to, is_current)
SELECT s.customer_id, s.tier, s.region, s.effective_from, DATE '9999-12-31', TRUE
FROM staging s
LEFT JOIN dim_customer d
  ON d.customer_id = s.customer_id AND d.is_current
WHERE d.customer_id IS NULL
   OR (d.tier, d.region) IS DISTINCT FROM (s.tier, s.region);
```

`IS DISTINCT FROM` is the NULL-safe comparison; plain `<>` treats a NULL change
as "no change" and misses it. For out-of-order effective dates, sort the staging
history by `effective_from` and apply oldest first, or rebuild the affected
key's version chain in one pass rather than incrementally.

## Change-data-capture notes

When the source exposes CDC (a change feed with insert/update/delete markers),
prefer it over diffing snapshots: it captures deletes and intermediate states a
snapshot diff loses. Handle the three operations explicitly. A delete marker
must soft-delete or tombstone in the target, not be dropped, or the target
diverges from the source. Order changes by the source's commit sequence, not by
arrival time.
