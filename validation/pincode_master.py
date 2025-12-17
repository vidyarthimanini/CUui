import pandas as pd
import os
import csv

def load_pincode_master():
    base_dir = os.path.dirname(os.path.dirname(__file__))
    file_path = os.path.join(base_dir, "data", "india_pincode.csv")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Pincode master not found at: {file_path}")

    # 🔑 Use Python engine + delimiter sniffing (fixes EmptyDataError)
    df = pd.read_csv(
        file_path,
        dtype=str,
        engine="python",
        sep=None,              # auto-detect delimiter
        encoding="utf-8-sig",
        quoting=csv.QUOTE_MINIMAL
    )

    if df.empty:
        raise ValueError(
            "Pincode CSV parsed successfully but contains no rows. "
            "Check delimiter / file integrity."
        )

    # Normalize column names
    df.columns = [c.strip().lower() for c in df.columns]

    # Expected India Post columns (your CSV)
    required = {"pincode", "officename", "statename"}
    missing = required - set(df.columns)

    if missing:
        raise ValueError(
            f"Pincode CSV missing required columns: {missing}. "
            f"Found columns: {list(df.columns)}"
        )

    # Standardize naming
    df = df.rename(columns={
        "officename": "city",
        "statename": "state"
    })

    df["pincode"] = df["pincode"].str.strip()

    return df[["pincode", "city", "state"]]
