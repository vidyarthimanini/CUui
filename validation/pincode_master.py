import pandas as pd
import os

_PINCODE_DF = None

def load_pincode_master():
    global _PINCODE_DF

    if _PINCODE_DF is None:
        base_dir = os.path.dirname(os.path.dirname(__file__))
        file_path = os.path.join(base_dir, "data", "india_pincode.csv")

        df = pd.read_csv(file_path, dtype={"pincode": str})

        # normalize column names
        df.columns = [c.lower().strip() for c in df.columns]

        # keep only what we need for validation & autofill
        df = df[["pincode", "district", "statename"]].drop_duplicates()

        # rename to internal standard names
        df = df.rename(
            columns={
                "district": "city",
                "statename": "state"
            }
        )

        _PINCODE_DF = df

    return _PINCODE_DF
