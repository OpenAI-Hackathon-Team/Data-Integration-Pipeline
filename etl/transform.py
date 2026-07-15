"""
transform.py
------------

Transforms the Walmart Sales datasets.

Steps:
1. Convert dates
2. Handle missing values
3. Merge datasets
4. Remove duplicate rows
5. Generate a data quality report

Author: Store Pulse Team
"""

import pandas as pd


# ==========================================================
# Convert Date Columns
# ==========================================================

def convert_dates(train_df, features_df):
    """
    Converts Date columns to datetime format.
    """

    train_df["Date"] = pd.to_datetime(train_df["Date"])
    features_df["Date"] = pd.to_datetime(features_df["Date"])

    return train_df, features_df


# ==========================================================
# Handle Missing Values
# ==========================================================

def handle_missing_values(features_df):
    """
    Replace missing values in MarkDown columns with 0.
    """

    markdown_columns = [
        "MarkDown1",
        "MarkDown2",
        "MarkDown3",
        "MarkDown4",
        "MarkDown5"
    ]

    features_df[markdown_columns] = features_df[markdown_columns].fillna(0)

    return features_df


# ==========================================================
# Merge Datasets
# ==========================================================

def merge_datasets(train_df, stores_df, features_df):
    """
    Merge train, stores and features datasets.
    """

    merged_df = pd.merge(
        train_df,
        stores_df,
        on="Store",
        how="left"
    )

    merged_df = pd.merge(
        merged_df,
        features_df,
        on=["Store", "Date", "IsHoliday"],
        how="left"
    )

    return merged_df


# ==========================================================
# Remove Duplicates
# ==========================================================

def remove_duplicates(df):
    """
    Removes duplicate rows.
    """

    before = len(df)

    df = df.drop_duplicates()

    after = len(df)

    print(f"\nDuplicates Removed: {before - after}")

    return df


# ==========================================================
# Data Quality Report
# ==========================================================

def quality_report(df):
    """
    Prints a basic quality report.
    """

    print("\n" + "=" * 60)
    print("DATA QUALITY REPORT")
    print("=" * 60)

    print(f"Rows    : {df.shape[0]}")
    print(f"Columns : {df.shape[1]}")

    print("\nMissing Values")
    print(df.isnull().sum())

    print("\nDuplicate Rows")
    print(df.duplicated().sum())

    print("\nData Types")
    print(df.dtypes)

    print("\nDataFrame Info")
    df.info()

    print("\nUnique Store Types")
    print(df["Type"].unique())

    print("=" * 60)


# ==========================================================
# Main Transformation Function
# ==========================================================

def transform_data(train_df, stores_df, features_df):
    """
    Executes the complete transformation pipeline.
    """

    print("=" * 60)
    print("Starting Data Transformation...")
    print("=" * 60)

    # Convert dates
    train_df, features_df = convert_dates(
        train_df,
        features_df
    )

    # Handle missing values
    features_df = handle_missing_values(features_df)

    # Merge datasets
    final_df = merge_datasets(
        train_df,
        stores_df,
        features_df
    )

    # Remove duplicates
    final_df = remove_duplicates(final_df)

    # Data quality report
    quality_report(final_df)

    print("\nData transformation completed successfully.")

    return final_df


# ==========================================================
# Test Module
# ==========================================================

if __name__ == "__main__":

    from etl.extract import extract_data

    train_df, stores_df, features_df = extract_data()

    final_df = transform_data(
        train_df,
        stores_df,
        features_df
    )

    print("\n" + "=" * 60)
    print("FINAL DATASET PREVIEW")
    print("=" * 60)

    print(final_df.head())