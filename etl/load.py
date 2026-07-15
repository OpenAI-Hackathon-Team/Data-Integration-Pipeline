"""
load.py
--------

Loads the transformed Walmart Sales dataset into PostgreSQL.

Steps:
1. Read environment variables
2. Connect to Supabase PostgreSQL
3. Execute schema.sql
4. Transform data
5. Save processed CSV
6. Load data into PostgreSQL
7. Verify data load

Author: Store Pulse Team
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

from etl.extract import extract_data
from etl.transform import transform_data


# ==========================================================
# Load Environment Variables
# ==========================================================

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

if not all([DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD]):
    raise ValueError("One or more database environment variables are missing.")


# ==========================================================
# Project Paths
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

SQL_FILE = BASE_DIR / "sql" / "schema.sql"

PROCESSED_DIR = BASE_DIR / "data" / "processed"
PROCESSED_DIR.mkdir(exist_ok=True)

OUTPUT_CSV = PROCESSED_DIR / "clean_sales.csv"


# ==========================================================
# Database Engine
# ==========================================================

DATABASE_URL = URL.create(
    drivername="postgresql+psycopg2",
    username=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=int(DB_PORT),
    database=DB_NAME,
)

engine = create_engine(DATABASE_URL)


# ==========================================================
# Test Connection
# ==========================================================

def test_connection():
    """Tests PostgreSQL connection."""

    print("\n" + "=" * 60)
    print("TESTING DATABASE CONNECTION")
    print("=" * 60)

    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT version();"))

            print("✓ Connected Successfully")
            print(result.fetchone()[0])

    except Exception as e:
        print("✗ Connection Failed")
        raise e


# ==========================================================
# Execute Schema
# ==========================================================

def execute_schema():
    """Executes schema.sql."""

    print("\n" + "=" * 60)
    print("CREATING DATABASE TABLE")
    print("=" * 60)

    try:
        with open(SQL_FILE, "r", encoding="utf-8") as file:
            sql = file.read()

        with engine.begin() as connection:
            connection.execute(text(sql))

        print("✓ Table created successfully")

    except Exception as e:
        print("✗ Failed creating table")
        raise e


# ==========================================================
# Save Processed CSV
# ==========================================================

def save_processed_csv(df):
    """Saves transformed dataset."""

    print("\n" + "=" * 60)
    print("SAVING PROCESSED DATASET")
    print("=" * 60)

    try:
        df.to_csv(OUTPUT_CSV, index=False)
        print(f"✓ Saved to:\n{OUTPUT_CSV}")

    except Exception as e:
        print("✗ Failed to save CSV!")
        raise e


# ==========================================================
# Load Data
# ==========================================================

def load_to_database(df):
    """Loads dataframe into PostgreSQL."""

    print("\n" + "=" * 60)
    print("LOADING DATA INTO POSTGRESQL")
    print("=" * 60)

    try:
        # Convert DataFrame column names to lowercase
        # so they match PostgreSQL table columns
        df = df.copy()
        df.columns = df.columns.str.lower()

        df.to_sql(
            name="clean_sales",
            con=engine,
            if_exists="append",
            index=False,
            chunksize=500
        )

        print(f"✓ {len(df):,} rows inserted.")

    except Exception as e:
        print("✗ Data load failed")
        print(type(e))
        print(str(e))
        raise

   
# ==========================================================
# Verify Load
# ==========================================================

def verify_load():
    """Verifies inserted rows."""

    print("\n" + "=" * 60)
    print("VERIFYING DATA")
    print("=" * 60)

    with engine.connect() as connection:

        result = connection.execute(
            text("SELECT COUNT(*) FROM clean_sales")
        )

        rows = result.scalar()

    print(f"Rows in database : {rows:,}")


# ==========================================================
# Main Pipeline
# ==========================================================

def main():

    # Step 1
    test_connection()

    # Step 2
    execute_schema()

    # Step 3
    train_df, stores_df, features_df = extract_data()

    # Step 4
    final_df = transform_data(
        train_df,
        stores_df,
        features_df
    )

    # Step 5
    save_processed_csv(final_df)

    # Step 6
    load_to_database(final_df)

    # Step 7
    verify_load()

    print("\n" + "=" * 60)
    print("ETL PIPELINE COMPLETED SUCCESSFULLY")
    print("=" * 60)


# ==========================================================
# Entry Point
# ==========================================================

if __name__ == "__main__":
    main()