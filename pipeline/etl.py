"""Simple ETL: CSV -> validate -> DuckDB. Fail hone par structured PipelineError."""
import json
import duckdb
import pandas as pd
from pathlib import Path

EXPECTED = {"order_id": "int", "customer_id": "int", "amount": "float",
            "order_date": "date", "city": "str"}
NOT_NULL = ["order_id", "customer_id", "amount"]
UNIQUE = ["order_id"]
FIXES_PATH = Path("logs/fixes.json")   # agent ke approved fixes yaha persist hote hain
DB_PATH = "warehouse.duckdb"


class PipelineError(Exception):
    def __init__(self, error_type, message, details=None):
        super().__init__(message)
        self.error_type, self.message, self.details = error_type, message, details or {}

    def to_dict(self):
        return {"error_type": self.error_type, "message": self.message, "details": self.details}


def load_fixes():
    return json.loads(FIXES_PATH.read_text()) if FIXES_PATH.exists() else []

def add_fix(fix):
    fixes = load_fixes()
    if fix not in fixes:
        fixes.append(fix)
    FIXES_PATH.parent.mkdir(exist_ok=True)
    FIXES_PATH.write_text(json.dumps(fixes, indent=2))

def reset_fixes():
    FIXES_PATH.unlink(missing_ok=True)

def _clean_numeric(s):
    return pd.to_numeric(s.astype(str).str.replace(r"[^0-9.\-]", "", regex=True), errors="coerce")

def apply_fixes(df, fixes):
    for f in fixes:
        a = f.get("action")
        if a == "rename_column" and f["from"] in df.columns:
            df = df.rename(columns={f["from"]: f["to"]})
        elif a == "cast_type" and f["column"] in df.columns:
            t = f["type"]
            df[f["column"]] = pd.to_datetime(df[f["column"]], errors="coerce") if t == "date" \
                else _clean_numeric(df[f["column"]])
        elif a == "drop_duplicates" and f["column"] in df.columns:
            df = df.drop_duplicates(subset=[f["column"]])
        elif a == "fill_nulls" and f["column"] in df.columns:
            df[f["column"]] = df[f["column"]].fillna(f["value"])
        elif a == "drop_null_rows" and f["column"] in df.columns:
            df = df.dropna(subset=[f["column"]])
    return df


def validate(df):
    missing = [c for c in EXPECTED if c not in df.columns]
    if missing:
        raise PipelineError("schema_mismatch", f"Missing columns: {missing}",
                            {"missing": missing,
                             "unexpected": [c for c in df.columns if c not in EXPECTED],
                             "found_columns": list(df.columns)})
    for col, t in EXPECTED.items():
        if t in ("int", "float"):
            coerced = pd.to_numeric(df[col], errors="coerce")
        elif t == "date":
            coerced = pd.to_datetime(df[col], errors="coerce")
        else:
            continue
        bad = df[col][coerced.isna() & df[col].notna()]
        if len(bad):
            raise PipelineError("type_mismatch", f"Column '{col}' expected {t}, got non-parsable values",
                                {"column": col, "expected_type": t, "bad_count": len(bad),
                                 "bad_samples": bad.head(3).tolist()})
    for col in NOT_NULL:
        n = int(df[col].isna().sum())
        if n:
            raise PipelineError("null_violation", f"Column '{col}' has {n} NULLs", {"column": col, "null_count": n})
    for col in UNIQUE:
        d = int(df[col].duplicated().sum())
        if d:
            raise PipelineError("duplicate_violation", f"Column '{col}' has {d} duplicate values",
                                {"column": col, "duplicate_count": d})


def run_pipeline(csv_path="data/incoming/orders.csv"):
    raw = pd.read_csv(csv_path)
    try:
        df = apply_fixes(raw.copy(), load_fixes())
        validate(df)
    except PipelineError as e:
        e.details["sample_rows"] = raw.head(3).to_dict("records")
        raise
    for col, t in EXPECTED.items():
        if t in ("int", "float"):
            df[col] = pd.to_numeric(df[col])
        elif t == "date":
            df[col] = pd.to_datetime(df[col])
    con = duckdb.connect(DB_PATH)
    con.execute("CREATE OR REPLACE TABLE orders AS SELECT * FROM df")
    n = con.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
    con.close()
    return n
