"""
extract.py
----------

Extracts the Walmart Sales datasets from the raw data folder.

Input:
    - train.csv
    - stores.csv
    - features.csv

Output:
    - Pandas DataFrames

Author: Store Pulse Team
"""

from pathlib import Path
import pandas as pd


# ==========================================================
# Project Paths
# ==========================================================

# Root directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Raw data directory
RAW_DATA_DIR = BASE_DIR / "data" / "raw"


# ==========================================================
# Extraction Functions
# ==========================================================

def read_train_data():
    """
    Reads the Walmart training dataset.

    Returns:
        pandas.DataFrame
    """
    file_path = RAW_DATA_DIR / "train.csv"
    return pd.read_csv(file_path)


def read_store_data():
    """
    Reads the store metadata.

    Returns:
        pandas.DataFrame
    """
    file_path = RAW_DATA_DIR / "stores.csv"
    return pd.read_csv(file_path)


def read_features_data():
    """
    Reads the store features dataset.

    Returns:
        pandas.DataFrame
    """
    file_path = RAW_DATA_DIR / "features.csv"
    return pd.read_csv(file_path)


def extract_data():
    """
    Extracts all datasets.

    Returns:
        tuple:
            train_df,
            stores_df,
            features_df
    """

    print("=" * 60)
    print("Starting Data Extraction...")
    print("=" * 60)

    train_df = read_train_data()
    stores_df = read_store_data()
    features_df = read_features_data()

    print(f"Train Dataset    : {train_df.shape}")
    print(f"Stores Dataset   : {stores_df.shape}")
    print(f"Features Dataset : {features_df.shape}")

    print("\nData extraction completed successfully.\n")

    return train_df, stores_df, features_df


# ==========================================================
# Testing
# ==========================================================

if __name__ == "__main__":

    train_df, stores_df, features_df = extract_data()

    print("TRAIN DATA")
    print(train_df.head())

    print("\n" + "-" * 60)

    print("STORES DATA")
    print(stores_df.head())

    print("\n" + "-" * 60)

    print("FEATURES DATA")
    print(features_df.head())

    print("\nExtraction module executed successfully.")