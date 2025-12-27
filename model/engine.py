# model/engine.py
import pandas as pd
import numpy as np
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer

# --------------------------------------------------
# Helpers
# --------------------------------------------------
def num(x):
    try:
        return float(str(x).replace(",", "").replace("₹", ""))
    except:
        return np.nan


def sb_label(score):
    s = float(score)
    if s >= 90: return ("SB1", "Excellent", "90–100")
    if s >= 85: return ("SB2", "Very Good", "85–89")
    if s >= 80: return ("SB3", "Good", "80–84")
    if s >= 75: return ("SB4", "Good", "75–79")
    if s >= 70: return ("SB5", "Satisfactory", "70–74")
    if s >= 60: return ("SB6", "Acceptable", "60–69")
    if s >= 50: return ("SB9", "Marginal", "50–59")
    return ("SB13", "Poor", "0–49")


def categorize_score_numeric(score):
    if score >= 75: return "Low"
    if score >= 50: return "Moderate"
    return "High"


# --------------------------------------------------
# CORE MODEL RUNNER
# --------------------------------------------------
def run_model(df: pd.DataFrame, company: str):
    df = df.copy()
    df.columns = [c.strip() for c in df.columns]

    df["FY"] = pd.to_numeric(df["FY"], errors="coerce")
    df = df.dropna(subset=["Company Name", "FY"])

    # numeric parsing
    num_cols = [
        "Turnover (₹ Crore)", "EBITDA (₹ Crore)", "Net Worth (₹ Crore)",
        "Total Debt (₹ Crore)", "DSCR", "Current Ratio",
        "ROCE (%)", "ROE (%)"
    ]
    for c in num_cols:
        if c in df.columns:
            df[c] = df[c].apply(num)

    # ---------------- FH Formula ----------------
    def compute_fh(r):
        leverage = 100 - min((r["Total Debt (₹ Crore)"] / (r["Net Worth (₹ Crore)"] + 1e-6)) * 20, 60)
        liquidity = min(r["Current Ratio"] * 50, 100)
        coverage = min(r["DSCR"] * 50, 100)
        profitability = np.mean([r["ROCE (%)"], r["ROE (%)"]])
        return np.clip(
            0.35 * leverage +
            0.25 * liquidity +
            0.20 * coverage +
            0.20 * profitability,
            0, 100
        )

    df["FH_Score"] = df.apply(compute_fh, axis=1)

    hist = df[df["Company Name"].str.lower() == company.lower()].sort_values("FY")
    if hist.empty:
        raise ValueError("Company not found")

    # ---------------- ML Forecast ----------------
    df["FH_Next"] = df.groupby("Company Name")["FH_Score"].shift(-1)
    train = df.dropna(subset=["FH_Next"])

    FEATURES = ["FH_Score"]
    pipe = Pipeline([
        ("imp", SimpleImputer(strategy="median")),
        ("model", Ridge(alpha=1.2))
    ])
    pipe.fit(train[FEATURES], train["FH_Next"])

    last = hist.iloc[-1]
    forecast = pipe.predict(pd.DataFrame([[last["FH_Score"]]], columns=FEATURES))[0]

    sb_code, sb_text, sb_range = sb_label(last["FH_Score"])
    risk_band = categorize_score_numeric(last["FH_Score"])

    return {
        "fh_score": round(last["FH_Score"], 2),
        "sb_code": sb_code,
        "sb_text": sb_text,
        "sb_range": sb_range,
        "risk_band": risk_band,
        "history": hist[["FY", "FH_Score"]],
        "forecast": forecast
    }
# --------------------------------------------------
# DATAFRAME ENGINEERING (FROM COLAB MODEL)
# --------------------------------------------------
def engineer_dataframe(df: pd.DataFrame):

    df = df.copy()
    df.columns = [c.strip() for c in df.columns]

    # ---------------- NUMERIC CLEANING ----------------
    def num(x):
        try:
            return float(str(x).replace(",", "").replace("₹", ""))
        except:
            return np.nan

    num_cols = [
        "Turnover (₹ Crore)", "EBITDA (₹ Crore)", "Net Profit (₹ Crore)",
        "Net Worth (₹ Crore)", "Total Debt (₹ Crore)",
        "DSCR", "Current Ratio", "ROCE (%)", "ROE (%)",
        "Credit Utilization (%)", "Loan Amount",
        "Collateral Value", "LTV Ratio", "Maximum DPD Observed"
    ]

    for c in num_cols:
        if c in df.columns:
            df[c] = df[c].apply(num)

    # ---------------- DOCUMENT SCORE ----------------
    doc_cols = [c for c in df.columns if c.endswith("Uploaded")]
    df["Document_Score"] = (
        df[doc_cols].astype(str)
        .apply(lambda x: x.str.lower().str.contains("yes|true|uploaded"))
        .mean(axis=1) * 100
        if doc_cols else 50
    )

    # ---------------- LOAN TYPE EWS ----------------
    df["Loan_Type_EWS"] = 70  # fixed placeholder (as in your backend)

    # ---------------- FH SCORE ----------------
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

        fh = (
            0.35 * leverage +
            0.20 * liquidity +
            0.20 * coverage +
            0.15 * profitability +
            0.10 * r["Loan_Type_EWS"]
        )
        return float(np.clip(fh, 0, 100))

        df["FH_Score"] = df.apply(compute_fh, axis=1)
    
        # ---------------- TRENDS ----------------
        df = df.sort_values(["Company Name", "FY"])
        df["EBITDA_Margin"] = df["EBITDA (₹ Crore)"] / (df["Turnover (₹ Crore)"] + 1e-6)
        df["Growth_1Y"] = df.groupby("Company Name")["Turnover (₹ Crore)"].pct_change()
        df["Trend_Slope"] = df.groupby("Company Name")["FH_Score"].transform(
            lambda x: np.polyfit(range(len(x)), x, 1)[0] if len(x) > 1 else 0
        )

        return df

