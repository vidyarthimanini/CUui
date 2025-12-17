import pandas as pd
import os
import re

def load_pincode_master():
    base_dir = os.path.dirname(os.path.dirname(__file__))
    file_path = os.path.join(base_dir, "data", "india_pincode.csv")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Pincode master not found at: {file_path}")

    # Try common delimiters used in govt CSVs
    delimiters = [",", ";", "|", "\t"]
    df = None

    for sep in delimiters:
        try:
            temp = pd.read_csv(
                file_path,
                sep=sep,
                dtype=str,
                encoding="utf-8-sig",
                on_bad_lines="skip"
            )
            if not temp.empty and temp.shape[1] > 1:
                df = temp
                break
        except Exception:
            continue

    if df is None or df.empty:
        raise ValueError(
            "Pincode CSV could not be parsed. "
            "Likely delimiter issue or file has no data rows."
        )

    # Normalize column names
    df.columns = [
        re.sub(r"\s+", "", c.strip().lower())
        for c in df.columns
    ]

    # Flexible column mapping (based on India Post schema)
    column_map = {
        "pincode": ["pincode", "pin", "postalcode"],
        "city": ["officename", "office", "city"],
        "state": ["statename", "state"]
    }

    resolved = {}
    for target, options in column_map.items():
        for opt in options:
            if opt in df.columns:
                resolved[target] = opt
                break

    missing = set(column_map.keys()) - set(resolved.keys())
    if missing:
        raise ValueError(
            f"Pincode CSV missing required columns: {missing}. "
            f"Found columns: {list(df.columns)}"
        )

    df = df.rename(columns={
        resolved["pincode"]: "pincode",
        resolved["city"]: "city",
        resolved["state"]: "state"
    })

    df["pincode"] = df["pincode"].str.strip()

    return df[["pincode", "city", "state"]]
