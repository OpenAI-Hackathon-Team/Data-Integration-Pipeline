"""Schema-driven validation for Store Pulse source datasets."""

from pathlib import Path

import pandas as pd
import yaml


BASE_DIR = Path(__file__).resolve().parent.parent
SCHEMA_FILE = BASE_DIR / "Config" / "schema.yaml"


def _sample_rows(mask: pd.Series, limit: int = 5) -> str:
    """Return CSV-style row numbers for a failing validation mask."""

    rows = (mask[mask].index[:limit] + 2).tolist()
    return ", ".join(map(str, rows))


def _missing_values(series: pd.Series) -> pd.Series:
    """Treat nulls and blank strings as missing values."""

    missing = series.isna()
    if pd.api.types.is_string_dtype(series) or series.dtype == object:
        missing |= series.astype("string").str.strip().eq("").fillna(False)
    return missing


def _invalid_type_values(series: pd.Series, expected_type: str) -> pd.Series:
    """Return a mask for non-null values that do not match a schema type."""

    present = ~_missing_values(series)
    invalid = pd.Series(False, index=series.index)

    if expected_type == "integer":
        numeric = pd.to_numeric(series.where(present), errors="coerce")
        invalid = present & (numeric.isna() | numeric.mod(1).ne(0))
    elif expected_type == "float":
        invalid = present & pd.to_numeric(series.where(present), errors="coerce").isna()
    elif expected_type == "date":
        invalid = present & pd.to_datetime(series.where(present), errors="coerce").isna()
    elif expected_type == "boolean":
        invalid = present & ~series.isin([True, False])
    elif expected_type == "string":
        invalid = pd.Series(False, index=series.index)
    else:
        raise ValueError(f"Unsupported schema type: {expected_type}")

    return invalid.fillna(False)


def load_schema(schema_file: Path = SCHEMA_FILE) -> dict:
    """Load the dataset validation rules from the project YAML file."""

    with schema_file.open(encoding="utf-8") as file:
        schema = yaml.safe_load(file) or {}

    datasets = schema.get("datasets")
    if not isinstance(datasets, dict):
        raise ValueError("Schema must contain a top-level 'datasets' mapping.")
    return datasets


def validate_dataset(name: str, dataframe: pd.DataFrame, rules: dict) -> list[str]:
    """Validate one DataFrame and return human-readable rule violations."""

    errors = []
    for column, rule in rules.get("columns", {}).items():
        if column not in dataframe.columns:
            errors.append(f"{name}.{column}: required schema column is missing")
            continue

        series = dataframe[column]
        missing = _missing_values(series)
        if rule.get("required") and missing.any():
            errors.append(
                f"{name}.{column}: {missing.sum()} required value(s) missing "
                f"(CSV rows: {_sample_rows(missing)})"
            )

        expected_type = rule.get("type")
        if expected_type:
            invalid_type = _invalid_type_values(series, expected_type)
            if invalid_type.any():
                errors.append(
                    f"{name}.{column}: {invalid_type.sum()} value(s) are not {expected_type} "
                    f"(CSV rows: {_sample_rows(invalid_type)})"
                )

        if rule.get("unique"):
            duplicates = series.notna() & series.duplicated(keep=False)
            if duplicates.any():
                errors.append(
                    f"{name}.{column}: {duplicates.sum()} duplicate value(s) "
                    f"(CSV rows: {_sample_rows(duplicates)})"
                )

        if "min_value" in rule:
            numeric = pd.to_numeric(series, errors="coerce")
            below_minimum = numeric.notna() & numeric.lt(rule["min_value"])
            if below_minimum.any():
                errors.append(
                    f"{name}.{column}: {below_minimum.sum()} value(s) below {rule['min_value']} "
                    f"(CSV rows: {_sample_rows(below_minimum)})"
                )

        allowed_values = rule.get("allowed_values")
        if allowed_values is not None:
            invalid_value = ~missing & ~series.isin(allowed_values)
            if invalid_value.any():
                errors.append(
                    f"{name}.{column}: values outside {allowed_values} "
                    f"(CSV rows: {_sample_rows(invalid_value)})"
                )

    return errors


def validate_sources(sources: dict[str, pd.DataFrame]) -> None:
    """Validate configured source DataFrames, raising one actionable error report."""

    schema = load_schema()
    errors = []
    for name, rules in schema.items():
        if name not in sources:
            errors.append(f"{name}: configured dataset was not provided to validation")
            continue
        errors.extend(validate_dataset(name, sources[name], rules))

    if errors:
        raise ValueError("Schema validation failed:\n - " + "\n - ".join(errors))

    print("Schema validation passed.")
