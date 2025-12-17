import pandas as pd
import os

def load_pincode_master():
    base_dir = os.path.dirname(os.path.dirname(__file__))
    file_path = os.path.join(base_dir, "data", "india_pincode.csv")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Pincode master not found at: {file_path}")

    try:
        df = pd.read_csv(
            file_path,
            dtype={"pincode": str},
            encoding="utf-8",
            on_bad_lines="skip"
        )
    except pd.errors.EmptyDataError:
        raise ValueError(
            "Pincode CSV is empty or unreadable. "
            "Ensure it contains data rows and is a valid CSV."
        )

    if df.empty:
        raise ValueError("Pincode CSV loaded but contains zero rows.")

    # Normalize column names
    df.columns = [c.strip().lower() for c in df.columns]

    required = {"pincode", "officename", "statename"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Pincode CSV missing columns: {missing}")

    # Standardize names
    df = df.rename(columns={
        "officename": "city",
        "statename": "state"
    })

    return df
