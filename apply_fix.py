"""
Fix application module for the self-healing pipeline.

Applies fixes proposed by the diagnosis agent to a DataFrame.
Each fix is a dict with an 'action' key and action-specific parameters.
"""

import logging
import re

import pandas as pd

logger = logging.getLogger(__name__)


class EscalateError(Exception):
    """Raised when a fix requires human escalation."""

    def __init__(self, reason: str):
        self.reason = reason
        super().__init__(f"Escalation required: {reason}")


def _clean_numeric(series: pd.Series) -> pd.Series:
    """Strip currency symbols, commas, and whitespace from a series for numeric casting."""
    return series.astype(str).apply(
        lambda x: re.sub(r"[^\d.\-eE]", "", x) if x and x != "nan" else x
    )


def apply_fix(df: pd.DataFrame, fix: dict) -> pd.DataFrame:
    """
    Apply a single fix to a DataFrame.

    Args:
        df: The DataFrame to modify (a copy is made).
        fix: Dict with 'action' key and action-specific parameters.

    Returns:
        Modified DataFrame.

    Raises:
        EscalateError: If the fix action is 'escalate'.
        ValueError: If the fix action is unknown or parameters are invalid.
    """
    df = df.copy()
    action = fix.get("action")

    if action == "rename_column":
        old_name = fix["from"]
        new_name = fix["to"]
        if old_name not in df.columns:
            raise ValueError(f"Column '{old_name}' not found for renaming")
        df = df.rename(columns={old_name: new_name})
        logger.info(f"✅ Renamed column '{old_name}' → '{new_name}'")

    elif action == "cast_type":
        column = fix["column"]
        target_type = fix["type"]
        if column not in df.columns:
            raise ValueError(f"Column '{column}' not found for type casting")

        if target_type in ("int", "float"):
            df[column] = _clean_numeric(df[column])
            df[column] = pd.to_numeric(df[column], errors="coerce")
            if target_type == "int":
                df[column] = df[column].astype("Int64")  # Nullable int
            logger.info(f"✅ Cast column '{column}' to {target_type}")

        elif target_type == "date":
            df[column] = pd.to_datetime(df[column], errors="coerce", format="mixed")
            logger.info(f"✅ Cast column '{column}' to datetime")

        else:
            df[column] = df[column].astype(str)
            logger.info(f"✅ Cast column '{column}' to str")

    elif action == "drop_duplicates":
        column = fix["column"]
        if column not in df.columns:
            raise ValueError(f"Column '{column}' not found for deduplication")
        before = len(df)
        df = df.drop_duplicates(subset=[column], keep="first")
        after = len(df)
        logger.info(f"✅ Dropped {before - after} duplicate rows on '{column}'")

    elif action == "fill_nulls":
        column = fix["column"]
        value = fix["value"]
        if column not in df.columns:
            raise ValueError(f"Column '{column}' not found for null filling")
        count = int(df[column].isna().sum())
        df[column] = df[column].fillna(value)
        logger.info(f"✅ Filled {count} nulls in '{column}' with {value!r}")

    elif action == "drop_null_rows":
        column = fix["column"]
        if column not in df.columns:
            raise ValueError(f"Column '{column}' not found for null row dropping")
        before = len(df)
        df = df.dropna(subset=[column])
        after = len(df)
        logger.info(f"✅ Dropped {before - after} rows with nulls in '{column}'")

    elif action == "escalate":
        reason = fix.get("reason", "No reason provided")
        logger.warning(f"⚠️ Escalation: {reason}")
        raise EscalateError(reason)

    else:
        raise ValueError(f"Unknown fix action: {action}")

    return df

