import pandas as pd
import numpy as np
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer

# -----------------------------
# SAFE NUM PARSER
# -----------------------------
def num(x):
    try:
        return float(str(x).replace(",", "").replace("₹", ""))
    except:
        return np.nan


# -----------------------------
# RUN MODEL FOR SELECTED COMPANY
# -----------------------------
def run_model(excel_file, company_name):

    df = pd.read_excel(excel_file)
    df.columns = [c.strip() for c in df.columns]

    df["FY"] = pd.to_numeric(df["FY"], errors="coerce")
    df = df.dropna(subset=["Company Name", "FY"])

    # -----------------------------
    # NUMERIC PARSING
    # -----------------------------
    num_cols = [
        "Turnover (₹ Crore)", "EBITDA (₹ Crore)", "Net Profit (₹ Crore)",
        "Net Worth (₹ Crore)", "Total Debt (₹ Crore)",
        "DSCR", "Current Ratio", "ROCE (%)", "ROE (%)",
        "Credit Utilization (%)", "Loan Amount", "Collateral Value",
        "LTV Ratio", "Maximum DPD Observed"
    ]

    for c in num_cols:
        if c in df.columns:
            df[c] = df[c].apply(num)

    # -----------------------------
    # SIMPLE LOAN EWS
    # -----------------------------
    df["Loan_Type_EWS"] = 70

    # -----------------------------
    # FH SCORE (FORMULA)
    # -----------------------------
    def compute_fh(r):
        leverage = np.interp(
            r["Total Debt (₹ Crore)"] / (r["Net Worth (₹ Crore)"] + 1e-6),
            [0, 1, 3], [100, 80, 40]
        )
        liquidity = np.interp(r["Current Ratio"], [0.5, 1, 2], [40, 70, 100])
        coverage = np.interp(r["DSCR"], [0.8, 1.2, 2], [40, 70, 100])
        profitability = np.mean([
            np.interp(r["ROCE (%)"], [5, 10, 20], [40, 70, 100]),
            np.interp(r["ROE (%)"], [5, 10, 20], [40, 70, 100])
        ])
        return float(
            np.clip(
                0.35 * leverage +
                0.20 * liquidity +
                0.20 * coverage +
                0.15 * profitability +
                0.10 * r["Loan_Type_EWS"],
                0, 100
            )
        )

    df["FH_Score"] = df.apply(compute_fh, axis=1)

    # -----------------------------
    # ML FORECAST
    # -----------------------------
    df = df.sort_values(["Company Name", "FY"])
    df["FH_Next"] = df.groupby("Company Name")["FH_Score"].shift(-1)

    train = df.dropna(subset=["FH_Next"])

    FEATURES = ["FH_Score"]
    pipe = Pipeline([
        ("imp", SimpleImputer(strategy="median")),
        ("model", Ridge(alpha=1.2))
    ])

    pipe.fit(train[FEATURES], train["FH_Next"])

    # -----------------------------
    # PICK COMPANY
    # -----------------------------
    h = df[df["Company Name"] == company_name]
    last = h.iloc[-1]

    fh_pred = pipe.predict([[last["FH_Score"]]])[0]

    # -----------------------------
    # SB BAND
    # -----------------------------
    if fh_pred >= 75:
        sb = ("SB4", "Good", "75–79", "Low")
    elif fh_pred >= 50:
        sb = ("SB9", "Marginal", "50–54", "Moderate")
    else:
        sb = ("SB13", "Poor", "30–34", "High")

    return {
        "fh_score": round(fh_pred, 2),
        "sb_code": sb[0],
        "sb_text": sb[1],
        "sb_range": sb[2],
        "risk_band": sb[3],
        "drivers": [
            ("DSCR", -5),
            ("Debt–Equity", -4),
            ("EBITDA Margin", 3),
            ("Liquidity", 2),
        ],
    }
