import streamlit as st
import pandas as pd
import numpy as np

from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer

# ---------------------------------------
# PAGE ENTRY
# ---------------------------------------
def render_ai_scorecard():

    st.markdown("## 🤖 AI Credit Scorecard (Auto Engine)")
    st.caption("Independent ML-powered credit assessment")
    st.divider()

    # ---------------------------------------
    # FILE UPLOAD
    # ---------------------------------------
    file = st.file_uploader(
        "Upload Financial Excel",
        type=["xlsx"],
        key="ai_excel"
    )

    if file is None:
        st.info("Upload an Excel file to begin.")
        return

    # ---------------------------------------
    # LOAD DATA
    # ---------------------------------------
    df = pd.read_excel(file)
    df.columns = [c.strip() for c in df.columns]

    df["FY"] = pd.to_numeric(df["FY"], errors="coerce")
    df = df.dropna(subset=["Company Name", "FY"])

    # ---------------------------------------
    # SAFE NUM PARSER
    # ---------------------------------------
    def num(x):
        try:
            return float(str(x).replace(",", "").replace("₹", ""))
        except:
            return np.nan

    NUM_COLS = [
        "Turnover (₹ Crore)", "EBITDA (₹ Crore)", "Net Profit (₹ Crore)",
        "Net Worth (₹ Crore)", "Total Debt (₹ Crore)",
        "DSCR", "Current Ratio", "ROCE (%)", "ROE (%)",
        "Credit Utilization (%)", "Loan Amount", "Collateral Value",
        "LTV Ratio", "Maximum DPD Observed"
    ]

    for c in NUM_COLS:
        if c in df.columns:
            df[c] = df[c].apply(num)

    # ---------------------------------------
    # DOCUMENT SCORE
    # ---------------------------------------
    doc_cols = [c for c in df.columns if c.endswith("Uploaded")]
    df["Document_Score"] = (
        df[doc_cols].astype(str)
        .apply(lambda x: x.str.lower().str.contains("yes|true|uploaded"))
        .mean(axis=1) * 100
        if doc_cols else 50
    )

    # ---------------------------------------
    # LOAN TYPE EWS
    # ---------------------------------------
    def score_behavior(v, g, m, b):
        try: v = float(v)
        except: v = m
        if v <= g: return 100
        if v <= m: return 70
        if v <= b: return 40
        return 20

    def loan_ews(r):
        wc = np.mean([
            score_behavior(r.get("Credit Utilization (%)", 90), 70, 90, 110),
            score_behavior(r.get("Bounced Cheques (Count)", 0), 0, 1, 2)
        ])
        tl = np.mean([
            score_behavior(r.get("LTV Ratio", 70), 60, 70, 80)
        ])
        return wc if str(r.get("Loan Type", "")).upper() == "WORKING CAPITAL" else tl

    df["Loan_Type_EWS"] = df.apply(loan_ews, axis=1)

    # ---------------------------------------
    # FINANCIAL HEALTH SCORE
    # ---------------------------------------
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

        return np.clip(
            0.35 * leverage +
            0.20 * liquidity +
            0.20 * coverage +
            0.15 * profitability +
            0.10 * r["Loan_Type_EWS"],
            0, 100
        )

    df["FH_Score"] = df.apply(compute_fh, axis=1)

    # ---------------------------------------
    # ML PREP
    # ---------------------------------------
    df = df.sort_values(["Company Name", "FY"])
    df["EBITDA_Margin"] = df["EBITDA (₹ Crore)"] / (df["Turnover (₹ Crore)"] + 1e-6)
    df["Growth_1Y"] = df.groupby("Company Name")["Turnover (₹ Crore)"].pct_change()
    df["Trend_Slope"] = df.groupby("Company Name")["FH_Score"].transform(
        lambda x: np.polyfit(range(len(x)), x, 1)[0] if len(x) > 1 else 0
    )

    df["FH_Next"] = df.groupby("Company Name")["FH_Score"].shift(-1)
    train = df.dropna(subset=["FH_Next"])

    FEATURES = [
        "FH_Score", "Trend_Slope", "Growth_1Y",
        "EBITDA_Margin", "Loan_Type_EWS", "Document_Score"
    ]

    pipe = Pipeline([
        ("imp", SimpleImputer(strategy="median")),
        ("model", Ridge(alpha=1.2))
    ])

    pipe.fit(train[FEATURES], train["FH_Next"])

    # ---------------------------------------
    # COMPANY DROPDOWN
    # ---------------------------------------
    company = st.selectbox(
        "Select Company",
        sorted(df["Company Name"].unique())
    )

    row = df[df["Company Name"] == company].iloc[-1]
    fh_ml = pipe.predict(pd.DataFrame([row[FEATURES]]))[0]

    # ---------------------------------------
    # OUTPUT
    # ---------------------------------------
    st.divider()
    c1, c2 = st.columns(2)

    c1.metric("FH Score (Formula)", f"{row['FH_Score']:.2f}")
    c2.metric("FH Score (AI)", f"{fh_ml:.2f}")

    if fh_ml >= 75:
        st.success("Low Risk")
    elif fh_ml >= 50:
        st.warning("Moderate Risk")
    else:
        st.error("High Risk")
