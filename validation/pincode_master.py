import pandas as pd
import os

def load_pincode_master():
    base_dir = os.path.dirname(os.path.dirname(__file__))
    file_path = os.path.join(base_dir, "data", "india_pincode.csv")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Pincode master not found at: {file_path}")

    # India Post CSVs are usually comma-separated but may have BOM
    df = pd.read_csv(
        file_path,
        dtype=str,
        encoding="utf-8-sig"
    )

    if df.empty:
        raise ValueError("Pincode CSV loaded but contains no data rows")

    # Normalize column names
    df.columns = [c.strip().lower() for c in df.columns]

    # REQUIRED columns from your CSV
    required = {"pincode", "officename", "statename"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(
            f"Pincode CSV missing required columns: {missing}. "
            f"Found columns: {list(df.columns)}"
        )

    # Rename to internal standard
    df = df.rename(columns={
        "officename": "city",
        "statename": "state"
    })

    # Clean pincode
    df["pincode"] = df["pincode"].str.strip()

    # Keep only what we need
    return df[["pincode", "city", "state"]]
