import pandas as pd
import os
import re

def load_pincode_master():
    base_dir = os.path.dirname(os.path.dirname(__file__))
    file_path = os.path.join(base_dir, "data", "india_pincode.csv")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Pincode master not found at: {file_path}")

    df = pd.read_csv(
        file_path,
        dtype=str,
        encoding="utf-8-sig",
        on_bad_lines="skip"
    )

    if df.empty:
        raise ValueError("Pincode CSV loaded but contains zero rows")

    # 🔍 LOG WHAT PANDAS ACTUALLY SEES
    print("PINCODE CSV COLUMNS:", list(df.columns))

    # Normalize column names
    df.columns = [
        re.sub(r"\s+", "", c.strip().lower())
        for c in df.columns
    ]

    print("NORMALIZED COLUMNS:", list(df.columns))

    return df
