"""
pipeline_logs.py
------------------

Tracks Pipeline Performance & Ops Metrics:
- How long the pipeline update took
- What changed: rows added, rows removed, or rows replaced/updated

This script only OBSERVES and REPORTS -- it doesn't run the ETL itself.
Wrap your pipeline call with this (see example at the bottom) to log
every run automatically.

Output: a JSON log entry per run, appended to pipeline_logs.jsonl,
plus printed to console. A teammate can later add a `pipeline_runs`
table in Supabase and insert these same fields as DB columns.
"""

import os
import json
import time
from pathlib import Path
from datetime import datetime, timezone

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

DATABASE_URL = URL.create(
    drivername="postgresql+psycopg2",
    username=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=int(DB_PORT),
    database=DB_NAME,
)
engine = create_engine(DATABASE_URL)

LOG_FILE = Path("pipeline_logs.jsonl")


def get_table_snapshot() -> dict:
    """Lightweight fingerprint of clean_sales, used to detect what changed."""

    with engine.connect() as connection:
        total_rows = connection.execute(text("SELECT COUNT(*) FROM clean_sales")).scalar()
        total_sales = connection.execute(text("SELECT SUM(weekly_sales) FROM clean_sales")).scalar()
        unique_stores = connection.execute(text("SELECT COUNT(DISTINCT store) FROM clean_sales")).scalar()

    return {
        "total_rows": total_rows,
        "total_sales_sum": float(total_sales) if total_sales else 0.0,
        "unique_stores": unique_stores,
    }


def diagnose_change(before: dict, after: dict) -> str:
    """
    Classifies what kind of change happened, based on row count and
    sales-sum movement between two snapshots.
    """

    row_delta = after["total_rows"] - before["total_rows"]
    sales_delta = after["total_sales_sum"] - before["total_sales_sum"]

    if row_delta == 0 and abs(sales_delta) < 0.01:
        return "no_change"
    elif row_delta > 0 and sales_delta > 0:
        return "rows_added"
    elif row_delta < 0:
        return "rows_removed"
    elif row_delta == 0 and abs(sales_delta) > 0.01:
        return "rows_replaced_or_updated"
    else:
        return "mixed_change"


def run_with_logging(pipeline_fn, run_label: str = "manual_run"):
    """
    Wraps a pipeline function call, timing it and logging what changed.

    Usage:
        from etl.load import main as run_etl
        run_with_logging(run_etl, run_label="etl_load")
    """

    print("=" * 60)
    print(f"PIPELINE RUN: {run_label}")
    print("=" * 60)

    before = get_table_snapshot()
    start_time = time.time()
    status = "success"
    error_message = None

    try:
        pipeline_fn()
    except Exception as e:
        status = "failed"
        error_message = str(e)
        print(f"✗ Pipeline failed: {e}")

    duration_seconds = round(time.time() - start_time, 2)
    after = get_table_snapshot()
    change_type = diagnose_change(before, after)

    log_entry = {
        "run_label": run_label,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "duration_seconds": duration_seconds,
        "status": status,
        "error_message": error_message,
        "rows_before": before["total_rows"],
        "rows_after": after["total_rows"],
        "row_delta": after["total_rows"] - before["total_rows"],
        "change_type": change_type,
    }

    # Append to local log file (one JSON object per line)
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(log_entry) + "\n")

    print(f"\nDuration     : {duration_seconds}s")
    print(f"Status       : {status}")
    print(f"Rows before  : {before['total_rows']:,}")
    print(f"Rows after   : {after['total_rows']:,}")
    print(f"Row delta    : {log_entry['row_delta']:+,}")
    print(f"Change type  : {change_type}")
    print(f"\n✓ Logged to {LOG_FILE}")

    return log_entry


if __name__ == "__main__":
    # Example: time a plain read (no actual pipeline change), just to test logging works
    def dummy_no_op():
        pass

    run_with_logging(dummy_no_op, run_label="test_run")

    print("\n--- To use this for real, wrap your actual pipeline call: ---")
    print("from etl.load import main as run_etl")
    print("run_with_logging(run_etl, run_label='etl_load')")