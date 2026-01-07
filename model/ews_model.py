import pandas as pd
import numpy as np
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer

# --------------------------------------------------
# SAFE NUMERIC PARSER
# --------------------------------------------------
def num(x):
    try:
        return float(str(x).replace(",", "").replace("₹", ""))
    except:
        return np.nan


# --------------------------------------------------
# PENALTIES (EXACT COLAB LOGIC)
# --------------------------------------------------
def dpd_penalty(dpd):
    if pd.isna(dpd): return 0
    if dpd >= 90: return 40
    if dpd >= 60: return 25
    if dpd >= 30: return 15
    if dpd > 0: return 5
    return 0

def sma_penalty(sma):
    s = str(sma).upper()
    return 25 if s == "SMA-2" else 15 if s == "SMA-1" else 0

def npa_penalty(tag):
    return 40 if str(tag).upper() == "YES" else 0


# --------------------------------------------------
# LOAN TYPE EWS (EXACT COLAB LOGIC)
# --------------------------------------------------
def score_behavior(v, good, mid, bad):
    try: v = float(v)
    except: v = mid
    if v <= good: return 100
    if v <= mid: return 70
    if v <= bad: return 40
    return 20

def loan_ews(row):
    loan = str(row.get("Loan Type", "")).upper()

    wc = np.mean([
        score_behavior(row.get("Credit Utilization (%)", 90), 70, 90, 110),
        score_behavior(row.get("Bounced Cheques (Count)", 0), 0, 1, 2),
        score_behavior(row.get("Overdrafts (Count)", 0), 0, 1, 2)
    ])

    tl = np.mean([
        score_behavior(row.get("LTV Ratio", 70), 60, 70, 80),
        score_behavior(row.get("Tenure (Months)", 60), 36, 60, 84)
    ])

    sl = np.mean([
        score_behavior(row.get("Group Risk Level", 1), 1, 2, 3),
        score_behavior(row.get("Cross-Bank NPA Tag", "No") == "Yes", 0, 1, 1)
    ])

    return wc if loan == "WORKING CAPITAL" else (tl if loan == "TERM LOAN" else sl)


# --------------------------------------------------
# MAIN ANALYSIS FUNCTION (USED BY UI)
# --------------------------------------------------
#READ EXCEL FOR MODEL

def analyze_company(company: str, df_company: pd.DataFrame):
    df_all=pd.read_excel("data/Indian_Companies_EWS_READY_WITH_FY2025.xlsx")
  
    df_all.columns = [c.strip() for c in df_all.columns]
    df_all["FY"] = pd.to_numeric(df_all["FY"], errors="coerce")
    df_all = df_all.dropna(subset=["Company Name", "FY"])

    num_cols = [
        "Turnover (₹ Crore)", "EBITDA (₹ Crore)", "Net Profit (₹ Crore)",
        "Net Worth (₹ Crore)", "Total Debt (₹ Crore)",
        "DSCR", "Current Ratio", "ROCE (%)", "ROE (%)",
        "Credit Utilization (%)", "LTV Ratio", "Maximum DPD Observed"
    ]

    for c in num_cols:
        if c in df_company.columns:
            df_company[c] = df_company[c].apply(num)

    # ---------------- DOCUMENT SCORE ----------------
    doc_cols = [c for c in df_company.columns if c.endswith("Uploaded")]
    df_company["Document_Score"] = (
        df_company[doc_cols].astype(str)
        .apply(lambda x: x.str.lower().str.contains("yes|true|uploaded"))
        .mean(axis=1) * 100
        if doc_cols else 50
    )

    # ---------------- LOAN TYPE EWS ----------------
    df_company["Loan_Type_EWS"] = df_company.apply(loan_ews, axis=1)

    # ---------------- FINANCIAL HEALTH (EXACT COLAB) ----------------
    def scale(v, d, r):
        if pd.isna(v): v = d[1]
        return np.clip(np.interp(v, d, r), min(r), max(r))

    def compute_fh(r):
        leverage = scale(
            r["Total Debt (₹ Crore)"] / (r["Net Worth (₹ Crore)"] + 1e-6),
            [0, 1, 3], [100, 80, 40]
        )
        liquidity = scale(r["Current Ratio"], [0.5, 1, 2], [40, 70, 100])
        coverage = scale(r["DSCR"], [0.8, 1.2, 2], [40, 70, 100])
        profitability = np.mean([
            scale(r["ROCE (%)"], [5, 10, 20], [40, 70, 100]),
            scale(r["ROE (%)"], [5, 10, 20], [40, 70, 100])
        ])

        fh_raw = (
            0.35 * leverage +
            0.20 * liquidity +
            0.20 * coverage +
            0.15 * profitability +
            0.10 * r["Loan_Type_EWS"]
        )

        penalty = (
            dpd_penalty(r["Maximum DPD Observed"]) +
            sma_penalty(r.get("SMA Classification")) +
            npa_penalty(r.get("Cross-Bank NPA Tag"))
        )

        return np.clip(fh_raw - penalty, 0, 100)

    df_company["FH_Score"] = df_company.apply(compute_fh, axis=1)

    # ---------------- TRENDS ----------------
    df_company = df_company.sort_values(["Company Name", "FY"])
    df_company["EBITDA_Margin"] = df_company["EBITDA (₹ Crore)"] / (df_company["Turnover (₹ Crore)"] + 1e-6)
    df_company["Growth_1Y"] = df_company.groupby("Company Name")["Turnover (₹ Crore)"].pct_change()
    df_company["Trend_Slope"] = df_company.groupby("Company Name")["FH_Score"].transform(
        lambda x: np.polyfit(range(len(x)), x, 1)[0] if len(x) > 1 else 0
    )

    # ---------------- ML FORECAST ----------------
    df_all["FH_Next"] = df_all.groupby("Company Name")["FH_Score"].shift(-1)
    train = df_all.dropna(subset=["FH_Next"])

    FEATURES = [
        "FH_Score", "Trend_Slope", "Growth_1Y",
        "EBITDA_Margin", "Loan_Type_EWS",
        "Document_Score", "Maximum DPD Observed"
    ]

    pipe = Pipeline([
        ("imp", SimpleImputer(strategy="median")),
        ("model", Ridge(alpha=1.2))
    ])

    pipe.fit(train[FEATURES], train["FH_Next"])
    df_company = df_company.copy()
    df_company.columns = [c.strip() for c in df_company.columns]
    df_company = df_company.sort_values("FY")
    last = df_company.iloc[-1]
    forecast = pipe.predict(pd.DataFrame([last[FEATURES]]))[0]

    return {
        "fh_score": round(last["FH_Score"], 2),
        "history": df_company[["FY", "FH_Score"]],
        "forecast": round(float(forecast), 2),
        "ebitda": df_company[["FY", "EBITDA_Margin"]],
        "growth": df_company[["FY", "Growth_1Y"]],
        "latest": last
    }
