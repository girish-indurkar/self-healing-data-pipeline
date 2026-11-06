"""
Data validation module for the self-healing pipeline.

Validates DataFrames against an expected schema, detecting:
- Schema mismatches (missing/unexpected columns)
- Type mismatches (wrong data types)
- Null violations (nulls in non-nullable columns)
- Duplicate violations (duplicates in unique columns)
"""

import logging
from typing import Any

import pandas as pd

logger = logging.getLogger(__name__)

# Default expected schema for demo/testing
DEFAULT_SCHEMA = {
    "order_id": {"type": "int", "nullable": False, "unique": True},
    "customer_name": {"type": "str", "nullable": False, "unique": False},
    "amount": {"type": "float", "nullable": False, "unique": False},
    "order_date": {"type": "date", "nullable": True, "unique": False},
}

# Map schema type names to pandas-compatible checks
TYPE_CHECKERS = {
    "int": lambda s: pd.to_numeric(s, errors="coerce").notna().all(),
    "float": lambda s: pd.to_numeric(s, errors="coerce").notna().all(),
    "str": lambda s: True,  # Everything can be a string
    "date": lambda s: pd.to_datetime(s, errors="coerce", format="mixed").notna().all(),
}


def validate_schema(
    df: pd.DataFrame,
    expected_schema: dict[str, dict[str, Any]] | None = None,
) -> list[dict]:
    """
    Validate a DataFrame against an expected schema.

    Args:
        df: The DataFrame to validate.
        expected_schema: Dict mapping column names to their constraints.
            Each value is a dict with keys: type, nullable, unique.
            If None, uses DEFAULT_SCHEMA.

    Returns:
        List of error dicts. Empty list means validation passed.
        Each error: {"error_type": str, "details": dict}
    """
    if expected_schema is None:
        expected_schema = DEFAULT_SCHEMA

    errors = []
    expected_cols = set(expected_schema.keys())
    actual_cols = set(df.columns)

    # --- Schema mismatch: missing or unexpected columns ---
    missing = list(expected_cols - actual_cols)
    unexpected = list(actual_cols - expected_cols)
    if missing or unexpected:
        errors.append({
            "error_type": "schema_mismatch",
            "details": {
                "missing": sorted(missing),
                "unexpected": sorted(unexpected),
                "expected": sorted(expected_cols),
                "actual": sorted(actual_cols),
            },
        })
        logger.warning(f"Schema mismatch: missing={missing}, unexpected={unexpected}")

    # --- Type, null, and unique checks (only for columns that exist) ---
    for col_name, constraints in expected_schema.items():
        if col_name not in actual_cols:
            continue  # Already caught by schema mismatch

        series = df[col_name]
        col_type = constraints.get("type", "str")
        nullable = constraints.get("nullable", True)
        unique = constraints.get("unique", False)

        # Type mismatch check
        non_null = series.dropna()
        if len(non_null) > 0 and col_type in TYPE_CHECKERS:
            if not TYPE_CHECKERS[col_type](non_null):
                # Find bad samples
                if col_type in ("int", "float"):
                    bad_mask = pd.to_numeric(non_null, errors="coerce").isna()
                elif col_type == "date":
                    bad_mask = pd.to_datetime(non_null, errors="coerce", format="mixed").isna()
                else:
                    bad_mask = pd.Series([False] * len(non_null), index=non_null.index)

                bad_samples = non_null[bad_mask].head(5).tolist()
                errors.append({
                    "error_type": "type_mismatch",
                    "details": {
                        "column": col_name,
                        "expected_type": col_type,
                        "bad_samples": bad_samples,
                        "bad_count": int(bad_mask.sum()),
                        "total_count": len(non_null),
                    },
                })
                logger.warning(
                    f"Type mismatch in '{col_name}': expected {col_type}, "
                    f"found {len(bad_samples)} bad samples"
                )

        # Null violation check
        if not nullable:
            null_count = int(series.isna().sum())
            if null_count > 0:
                errors.append({
                    "error_type": "null_violation",
                    "details": {
                        "column": col_name,
                        "null_count": null_count,
                        "total_count": len(series),
                    },
                })
                logger.warning(f"Null violation in '{col_name}': {null_count} nulls found")

        # Duplicate violation check
        if unique:
            dup_count = int(series.duplicated().sum())
            if dup_count > 0:
                dup_samples = series[series.duplicated(keep=False)].head(10).tolist()
                errors.append({
                    "error_type": "duplicate_violation",
                    "details": {
                        "column": col_name,
                        "duplicate_count": dup_count,
                        "duplicate_samples": dup_samples,
                    },
                })
                logger.warning(f"Duplicate violation in '{col_name}': {dup_count} duplicates")

    logger.info(f"Validation complete: {len(errors)} error(s) found")
    return errors

