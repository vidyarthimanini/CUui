import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
import warnings
warnings.filterwarnings("ignore")


# =========================================================
# MAIN RENDER FUNCTION (CALLED BY app.py)
# =========================================================
def render_ai_scorecard():

    st.subheader("🧠 AI Financial Health Scorecard")

    # -------------------------------------------------
    # DATA SOURCE (shared across app if needed later)
    # -------------------------------------------------
    uploaded = st.file_uploader(
        "Upload Financial Dataset (Excel)",
        type=["xlsx"],
        key="ai_scorecard_upload"
    )

    if uploaded is None:
        st.info("Upload file to calculate AI score")
        return

    df = pd.read_excel(uploaded)
    df.columns = [c.strip() for c in df.columns]
    df["FY"] = pd.to_numeric(df["FY"], errors="coerce")
    df = df.dropna(subset=["Company Name", "FY"])

    # -------------------------------------------------
    # HELPERS (UNCHANGED LOGIC)
    # -------------------------------------------------
    def num(x):
        try:
            return float(str(x).replace(",", "").replace("₹", ""))
        except:
            return np.nan

    num_cols = [
        "Turnover (₹ Crore)", "EBITDA (₹ Crore)", "Net Profit (₹ Crore)",
        "Net Worth (₹ Crore)", "Total Debt (₹ Crore)", "DSCR",
        "Current Ratio", "ROCE (%)", "ROE (%)",
        "Credit Utilization (%)", "Loan Amount",
        "Collateral Value", "LTV Ratio", "Maximum DPD Observed"
    ]

    for c in num_cols:
        if c in df.columns:
            df[c] = df[c].apply(num)

    # -------------------------------------------------
    # DOCUMENT SCORE
    # -------------------------------------------------
    doc_cols = [c for c in df.columns if c.endswith("Uploaded")]
    df["Document_Score"] = (
        df[doc_cols].astype(str)
        .apply(lambda x: x.str.lower().str.contains("yes|true|uploaded"))
        .mean(axis=1) * 100
    ) if doc_cols else 50

    # -------------------------------------------------
    # LOAN TYPE EWS
    # -------------------------------------------------
    def score_behavior(v, good, mid, bad):
        try: v = float(v)
        except: v = mid
        if v <= good: return 100
        if v <= mid: return 70
        if v <= bad: return 40
        return 20

    def loan_ews(r):
        wc = np.mean([
            score_behavior(r.get("Credit Utilization (%)",90),70,90,110),
            score_behavior(r.get("Bounced Cheques (Count)",0),0,1,2),
        ])
        return wc

    df["Loan_Type_EWS"] = df.apply(loan_ews, axis=1)

    # -------------------------------------------------
    # FINANCIAL HEALTH SCORE
    # -------------------------------------------------
    def scale(v, d, r):
        if pd.isna(v): v = d[1]
        return np.clip(np.interp(v, d, r), min(r), max(r))

    def compute_fh(r):
        leverage = scale(
            r["Total Debt (₹ Crore)"]/(r["Net Worth (₹ Crore)"]+1e-6),
            [0,1,3],[100,80,40]
        )
        liquidity = scale(r["Current Ratio"], [0.5,1,2], [40,70,100])
        coverage = scale(r["DSCR"], [0.8,1.2,2], [40,70,100])
        profitability = np.mean([
            scale(r["ROCE (%)"], [5,10,20], [40,70,100]),
            scale(r["ROE (%)"], [5,10,20], [40,70,100])
        ])
        return np.clip(
            0.35*leverage + 0.20*liquidity +
            0.20*coverage + 0.15*profitability +
            0.10*r["Loan_Type_EWS"],
            0, 100
        )

    df["FH_Score"] = df.apply(compute_fh, axis=1)

    # -------------------------------------------------
    # TRENDS
    # -------------------------------------------------
    df = df.sort_values(["Company Name","FY"])
    df["EBITDA_Margin"] = df["EBITDA (₹ Crore)"]/(df["Turnover (₹ Crore)"]+1e-6)
    df["Growth_1Y"] = df.groupby("Company Name")["Turnover (₹ Crore)"].pct_change()
    df["Trend_Slope"] = df.groupby("Company Name")["FH_Score"].transform(
        lambda x: np.polyfit(range(len(x)), x, 1)[0] if len(x)>1 else 0
    )

    # -------------------------------------------------
    # ML MODEL
    # -------------------------------------------------
    df["FH_Next"] = df.groupby("Company Name")["FH_Score"].shift(-1)
    train = df.dropna(subset=["FH_Next"])

    FEATURES = [
        "FH_Score","Trend_Slope","Growth_1Y",
        "EBITDA_Margin","Loan_Type_EWS",
        "Document_Score","Maximum DPD Observed"
    ]

    pipe = Pipeline([
        ("imp", SimpleImputer(strategy="median")),
        ("model", Ridge(alpha=1.2))
    ])
    pipe.fit(train[FEATURES], train["FH_Next"])

    # -------------------------------------------------
    # UI — COMPANY SELECT
    # -------------------------------------------------
    company = st.selectbox(
        "Select Company",
        sorted(df["Company Name"].unique())
    )

    h = df[df["Company Name"] == company]
    last = h.iloc[-1]

    fh_formula = last["FH_Score"]
    fh_ml = pipe.predict(pd.DataFrame([last[FEATURES]]))[0]

    c1, c2, c3 = st.columns(3)
    c1.metric("FH Score (Formula)", f"{fh_formula:.2f}")
    c2.metric("FH Score (AI)", f"{fh_ml:.2f}")
    c3.metric(
        "Risk Band",
        "Low" if fh_ml>=75 else "Moderate" if fh_ml>=50 else "High"
    )

    # -------------------------------------------------
    # TREND PLOT
    # -------------------------------------------------
    st.markdown("### 📈 Financial Health Trend")

    fig, ax = plt.subplots()
    ax.plot(h["FY"], h["FH_Score"], marker="o", label="Historical")

    forecast=[]
    for i in range(1,4):
        p = pipe.predict(pd.DataFrame([last[FEATURES]]))[0]
        forecast.append((last["FY"]+i, p))

    ax.plot(
        [h["FY"].iloc[-1]]+[x[0] for x in forecast],
        [h["FH_Score"].iloc[-1]]+[x[1] for x in forecast],
        "--s", label="Forecast"
    )
    ax.legend()
    ax.grid(True)

    st.pyplot(fig)
