# Validation patterns

Concrete implementations of the five check families in SKILL.md, in SQL and in
Python, plus the hard-gate vs quarantine decision made explicit in code. Ship
these with the pipeline; do not treat them as a manual afterthought. Contents:

- [Where each check goes](#where-each-check-goes)
- [Hard gate: assert-or-fail](#hard-gate-assert-or-fail)
- [Soft gate: quarantine bad rows](#soft-gate-quarantine-bad-rows)
- [The five check families in SQL](#the-five-check-families-in-sql)
- [A minimal Python assertion helper](#a-minimal-python-assertion-helper)
- [When to reach for a framework](#when-to-reach-for-a-framework)

## Where each check goes

- Schema and type checks: at ingestion, before the first transform.
- Key uniqueness and referential integrity: after staging, before the load.
- Volume and distribution checks: after the load, compared to recent runs.
- Reconciliation: last, against a source total or control number.

Prefer hard gates on keys and volume (a wrong key corrupts everything
downstream), soft gates on individual dirty rows (one bad address should not
block a million good rows).

## Hard gate: assert-or-fail

A check that must pass or the run stops. Keep the failure message specific
enough to debug from the log alone.

```sql
-- Fails the step if the key is not unique. Wrap in your engine's assertion
-- mechanism, or run it and check that the result set is empty in the caller.
SELECT id, count(*) AS n
FROM staging
GROUP BY id
HAVING count(*) > 1;
```

```python
def assert_unique(con, table: str, key: str) -> None:
    dupes = con.execute(
        f"SELECT {key}, count(*) n FROM {table} GROUP BY {key} HAVING count(*) > 1"
    ).fetchall()
    if dupes:
        example = dupes[:5]
        raise ValueError(
            f"{table}.{key} not unique: {len(dupes)} duplicated keys, e.g. {example}"
        )
```

## Soft gate: quarantine bad rows

Route failing rows to a side table with the reason, keep the good rows flowing,
and never drop silently. The quarantine table is inspectable and replayable.

```sql
-- Good rows continue; bad rows land in quarantine with a reason and run id.
INSERT INTO orders_quarantine
SELECT s.*, 'amount_negative' AS reject_reason, :run_id AS run_id
FROM staging s
WHERE s.amount < 0;

INSERT INTO orders_clean
SELECT s.* FROM staging s
WHERE s.amount >= 0 OR s.amount IS NULL;  -- decide NULL handling explicitly
```

Emit the quarantine count per run. A quarantine rate that suddenly jumps is a
signal even when the load "succeeds".

## The five check families in SQL

```sql
-- 1. Schema: column presence and type. Engine-specific; against information_schema.
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'orders';
-- Compare the result to the expected contract in code.

-- 2. Key: primary key uniqueness + no orphaned foreign keys.
SELECT count(*) - count(DISTINCT id) AS dup_keys FROM orders;      -- expect 0
SELECT count(*) AS orphans
FROM orders o LEFT JOIN dim_customer c ON o.customer_id = c.id
WHERE o.customer_id IS NOT NULL AND c.id IS NULL;                  -- expect 0

-- 3. Volume: row count within an expected band vs recent runs.
SELECT count(*) AS rows FROM orders;   -- flag 0 rows, or a >N x swing vs prior run

-- 4. Distribution: null rate and domain on critical columns.
SELECT
    avg(CASE WHEN amount IS NULL THEN 1 ELSE 0 END) AS null_rate_amount,
    min(amount) AS min_amount, max(amount) AS max_amount,
    count(*) FILTER (WHERE status NOT IN ('shipped','pending','cancelled')) AS bad_status
FROM orders;

-- 5. Reconciliation: totals tie back to a source or control number.
SELECT abs(
    (SELECT sum(amount) FROM orders_clean) -
    (SELECT sum(amount) FROM source_totals WHERE dt = CURRENT_DATE)
) AS delta;   -- expect 0 (or within a documented tolerance)
```

## A minimal Python assertion helper

No framework needed for a small pipeline. This collects failures instead of
stopping at the first, so one run reports every problem.

```python
from dataclasses import dataclass, field


@dataclass
class CheckResult:
    name: str
    passed: bool
    detail: str = ""


class Validator:
    """Run named checks against a live connection. Hard checks raise on failure;
    soft checks record and continue."""

    def __init__(self, con):
        self.con = con
        self.results: list[CheckResult] = []

    def check(self, name: str, sql: str, expect_zero: bool = True, hard: bool = True):
        (value,) = self.con.execute(sql).fetchone()
        passed = (value == 0) if expect_zero else bool(value)
        self.results.append(CheckResult(name, passed, f"value={value}"))
        if hard and not passed:
            raise ValueError(f"hard check failed: {name} (value={value})")
        return self

    def summary(self) -> str:
        return "\n".join(
            f"[{'PASS' if r.passed else 'FAIL'}] {r.name} {r.detail}" for r in self.results
        )


# Usage
v = (
    Validator(con)
    .check("pk_unique", "SELECT count(*)-count(DISTINCT id) FROM staging")
    .check("no_negative_amount", "SELECT count(*) FROM staging WHERE amount < 0", hard=False)
    .check("row_count_nonzero", "SELECT count(*) FROM staging", expect_zero=False)
)
print(v.summary())
```

## When to reach for a framework

Hand-rolled checks are right for one pipeline. Reach for a validation framework
(Great Expectations, dbt tests, Pandera, Soda) when checks must be shared across
many pipelines, versioned as a suite, or surfaced in a data-quality dashboard.
Do not add the framework before that need exists; it is infrastructure, and
infrastructure has a carrying cost. See references.md for links.
