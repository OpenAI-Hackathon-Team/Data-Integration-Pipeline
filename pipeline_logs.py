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
plus printed to console, plus saved into a `pipeline_logs` table in Supabase.
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


def ensure_pipeline_logs_table():
    """Creates pipeline_logs table if it doesn't exist yet -- safe to call every time."""

    create_sql = text("""
        CREATE TABLE IF NOT EXISTS pipeline_logs (
            id                  SERIAL PRIMARY KEY,
            run_label           TEXT NOT NULL,
            run_timestamp       TIMESTAMPTZ NOT NULL DEFAULT now(),
            duration_seconds    NUMERIC(10,2),
            status              TEXT,
            error_message       TEXT,
            rows_before         INTEGER,
            rows_after          INTEGER,
            row_delta           INTEGER,
            change_type         TEXT
        );
    """)
    with engine.begin() as connection:
        connection.execute(create_sql)


def save_log_to_supabase(log_entry: dict):
    """Inserts one log entry into the pipeline_logs table."""

    insert_sql = text("""
        INSERT INTO pipeline_logs
            (run_label, duration_seconds, status, error_message,
             rows_before, rows_after, row_delta, change_type)
        VALUES
            (:run_label, :duration_seconds, :status, :error_message,
             :rows_before, :rows_after, :row_delta, :change_type)
    """)

    with engine.begin() as connection:
        connection.execute(insert_sql, {
            "run_label": log_entry["run_label"],
            "duration_seconds": log_entry["duration_seconds"],
            "status": log_entry["status"],
            "error_message": log_entry["error_message"],
            "rows_before": log_entry["rows_before"],
            "rows_after": log_entry["rows_after"],
            "row_delta": log_entry["row_delta"],
            "change_type": log_entry["change_type"],
        })

    print(f"✓ Also saved to Supabase pipeline_logs table")


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

    # Also save to Supabase, so the team can query pipeline history there
    ensure_pipeline_logs_table()
    save_log_to_supabase(log_entry)

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