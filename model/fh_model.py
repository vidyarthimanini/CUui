# model/fh_model.py
import pandas as pd
import numpy as np
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer

from model.engine import engineer_dataframe, sb_label, categorize_score_numeric


def run_fh_model(master_df: pd.DataFrame, input_df: pd.DataFrame):
    """
    EXACT COLAB MODEL LOGIC – backend-safe
    """

    # ------------------------------
    # ENGINEER DATA
    # ------------------------------
    master_eng = engineer_dataframe(master_df)
    input_eng = engineer_dataframe(input_df)

    # ------------------------------
    # FEATURES (FROM COLAB)
    # ------------------------------
    FEATURES = [
        "FH_Score",
        "Trend_Slope",
        "Growth_1Y",
        "EBITDA_Margin",
        "Loan_Type_EWS",
        "Document_Score",
        "Maximum DPD Observed"
    ]

    # ------------------------------
    # TRAIN ML MODEL
    # ------------------------------
    master_eng["FH_Next"] = master_eng.groupby(
        "Company Name"
    )["FH_Score"].shift(-1)

    train = master_eng.dropna(subset=["FH_Next"])

    X_train = train[FEATURES]
    y_train = train["FH_Next"]

    pipe = Pipeline([
        ("imp", SimpleImputer(strategy="median")),
        ("model", Ridge(alpha=1.2))
    ])
    pipe.fit(X_train, y_train)

    # ------------------------------
    # SELECT COMPANY
    # ------------------------------
    row = input_eng.iloc[0]
    fh = float(row["FH_Score"])

    sb_code, sb_text, sb_range = sb_label(fh)
    risk_band = categorize_score_numeric(fh)

    forecast = pipe.predict(row[FEATURES].to_frame().T)[0]

    history = master_eng[
        master_eng["Company Name"] == row["Company Name"]
    ][["FY", "FH_Score"]]

    return {
        "fh_score": round(fh, 2),
        "sb_code": sb_code,
        "sb_text": sb_text,
        "sb_range": sb_range,
        "risk_band": risk_band,
        "history": history,
        "forecast": forecast
    }
