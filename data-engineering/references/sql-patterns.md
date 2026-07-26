# SQL patterns

Copyable, dialect-aware idioms for the SQL practices in SKILL.md. Confirm the
exact syntax against your engine's current docs; the semantics below are stable
but keywords vary. Contents:

- [Idempotent write: upsert / merge](#idempotent-write-upsert--merge)
- [Idempotent write: overwrite by partition](#idempotent-write-overwrite-by-partition)
- [Deduplicate to one row per key](#deduplicate-to-one-row-per-key)
- [Assert join cardinality](#assert-join-cardinality)
- [NULL-safe anti-join (NOT IN trap)](#null-safe-anti-join-not-in-trap)
- [Incremental filter on a high-water mark](#incremental-filter-on-a-high-water-mark)
- [Safe type and NULL handling](#safe-type-and-null-handling)

## Idempotent write: upsert / merge

Rerunning must not duplicate. Upsert on the stable key instead of blind INSERT.

**Postgres / DuckDB** (`ON CONFLICT`):

```sql
INSERT INTO target (id, updated_at, amount)
SELECT id, updated_at, amount FROM staging
ON CONFLICT (id) DO UPDATE
SET updated_at = EXCLUDED.updated_at,
    amount     = EXCLUDED.amount
-- Only overwrite when the incoming row is newer; prevents an out-of-order
-- replay from clobbering a fresher value.
WHERE target.updated_at < EXCLUDED.updated_at;
```

**Snowflake / BigQuery / Spark SQL** (`MERGE`):

```sql
MERGE INTO target t
USING staging s ON t.id = s.id
WHEN MATCHED AND s.updated_at > t.updated_at THEN UPDATE SET
    t.updated_at = s.updated_at,
    t.amount     = s.amount
WHEN NOT MATCHED THEN INSERT (id, updated_at, amount)
    VALUES (s.id, s.updated_at, s.amount);
```

If `staging` can contain more than one row per key, deduplicate it to one row
per key first (next section but one). A MERGE that matches multiple source rows
to one target row errors or is non-deterministic depending on engine.

## Idempotent write: overwrite by partition

When the grain is a partition (usually a date), replacing the whole partition is
simpler and safer than row-level upsert. Do it atomically.

**Spark / lakehouse** (dynamic partition overwrite):

```sql
-- Only the partitions present in the SELECT are replaced; others untouched.
INSERT OVERWRITE TABLE target PARTITION (dt)
SELECT col1, col2, dt FROM staging WHERE dt = DATE '2024-01-07';
```

**Warehouse without partition overwrite** (delete-and-insert in one transaction):

```sql
BEGIN;
DELETE FROM target WHERE dt = DATE '2024-01-07';
INSERT INTO target SELECT * FROM staging WHERE dt = DATE '2024-01-07';
COMMIT;
```

## Deduplicate to one row per key

Keep the latest row per key. `QUALIFY` is the clean form where supported
(Snowflake, BigQuery, DuckDB); the subquery form is portable everywhere.

**QUALIFY:**

```sql
SELECT *
FROM staging
QUALIFY row_number() OVER (
    PARTITION BY id ORDER BY updated_at DESC, ingested_at DESC
) = 1;
```

**Portable (Postgres, Spark, any engine with window functions):**

```sql
SELECT * EXCEPT (rn)  -- or list columns explicitly
FROM (
    SELECT s.*,
           row_number() OVER (
               PARTITION BY id ORDER BY updated_at DESC, ingested_at DESC
           ) AS rn
    FROM staging s
) WHERE rn = 1;
```

Always include a deterministic tiebreaker in `ORDER BY`. `ORDER BY updated_at`
alone is nondeterministic when two rows share a timestamp.

## Assert join cardinality

Fan-out from a non-unique key on the "one" side silently multiplies rows and
inflates every downstream aggregate. Assert the key is unique before joining, or
check the row count after.

```sql
-- Guard: fail loudly if the dimension key is not unique before you join on it.
SELECT customer_id, count(*) AS n
FROM dim_customer
GROUP BY customer_id
HAVING count(*) > 1;   -- must return zero rows
```

If the join is meant to be many-to-one, the fact row count must be unchanged by
the join. Capture `count(*)` before and after and compare; a difference means an
unintended fan-out or a dropped-row filter.

## NULL-safe anti-join (NOT IN trap)

`NOT IN` returns no rows if the subquery yields a single NULL, because
`x <> NULL` is UNKNOWN. Use `NOT EXISTS`, which is NULL-safe and usually plans
better.

```sql
-- Wrong: silently empty if any dropped.customer_id is NULL.
SELECT * FROM orders o
WHERE o.customer_id NOT IN (SELECT customer_id FROM dropped);

-- Right:
SELECT * FROM orders o
WHERE NOT EXISTS (
    SELECT 1 FROM dropped d WHERE d.customer_id = o.customer_id
);
```

## Incremental filter on a high-water mark

Process only rows past the last successfully loaded marker. Use a closed lower
bound and reprocess a trailing window so late or corrected rows are picked up
(see incremental-and-history.md for the full pattern).

```sql
SELECT *
FROM source
WHERE updated_at >= (
    -- last committed mark, minus a safety window for late arrivals
    SELECT max(watermark) - INTERVAL '2' DAY FROM etl_state WHERE stream = 'orders'
);
```

Advance the stored watermark only after the load validates. Storing it before
the load means a mid-run failure skips rows on the next run.

## Safe type and NULL handling

- Cast at the boundary, not repeatedly mid-query. A single typed staging layer
  beats scattered `CAST`s that each defeat an index or zone map.
- Avoid functions on filter/join columns: `WHERE date_trunc('day', ts) = ...`
  cannot use an index on `ts`. Rewrite as a range: `WHERE ts >= d AND ts < d+1`.
- `COALESCE` a nullable key column before grouping only when NULL is a real
  category; otherwise a NULL key usually signals a data-quality problem to
  quarantine, not to bucket.
- `sum`, `avg`, and friends skip NULLs but `count(col)` also skips them while
  `count(*)` does not. Choose deliberately; the difference is a common
  reconciliation bug.
