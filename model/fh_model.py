# model/fh_model.py
import pandas as pd
import numpy as np
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer

from engine.engine import engineer_dataframe

def run_model(master_df: pd.DataFrame, input_df: pd.DataFrame):
    """
    EXACT SAME LOGIC AS YOUR COLAB MODEL
    Just wrapped as a function.
    """

    # ------------------------------
    # ENGINEER DATA
    # ------------------------------
    master_eng = engineer_dataframe(master_df)
    input_eng = engineer_dataframe(input_df)

    # ------------------------------
    # FEATURES (UNCHANGED)
    # ------------------------------
    FEATURES = [
        "FH_Score","Trend_Slope","Growth_1Y",
        "EBITDA_Margin","Loan_Type_EWS",
        "Document_Score","Maximum DPD Observed"
    ]

    # ------------------------------
    # TRAIN MODEL
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
    # STATS FOR SHAP STYLE
    # ------------------------------
    means = X_train.mean()
    stds = X_train.std().replace(0, 1)

    return {
        "model": pipe,
        "features": FEATURES,
        "means": means,
        "stds": stds,
        "engineered_input": input_eng
    }
