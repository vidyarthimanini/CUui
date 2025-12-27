import streamlit as st
import pandas as pd
import numpy as np
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer

# ---------------- SAFE PLOTLY ----------------
try:
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False


def render_ai_scorecard():

    st.markdown("## 🤖 AI Credit Risk Scorecard")
    st.caption("Excel-driven, explainable AI scoring")
    st.divider()

    # =====================================================
    # 1. EXCEL UPLOAD
    # =====================================================
    uploaded = st.file_uploader(
        "📥 Upload Excel file (Company Financials)",
        type=["xlsx"]
    )

    if uploaded is None:
        st.info("Upload an Excel file to begin AI scoring.")
        return

    df = pd.read_excel(uploaded)
    df.columns = [c.strip() for c in df.columns]

    # =====================================================
    # 2. BASIC CLEANING
    # =====================================================
    df["FY"] = pd.to_numeric(df["FY"], errors="coerce")
    df = df.dropna(subset=["Company Name", "FY"])

    def num(x):
        try:
            return float(str(x).replace(",", "").replace("₹", ""))
        except:
            return np.nan

    NUM_COLS = [
        "Turnover (₹ Crore)", "EBITDA (₹ Crore)",
        "Net Worth (₹ Crore)", "Total Debt (₹ Crore)",
        "DSCR", "Current Ratio", "ROCE (%)", "ROE (%)"
    ]

    for c in NUM_COLS:
        if c in df.columns:
            df[c] = df[c].apply(num)

    # =====================================================
    # 3. FEATURE ENGINEERING
    # =====================================================
    df = df.sort_values(["Company Name", "FY"])

    df["Debt_Equity"] = df["Total Debt (₹ Crore)"] / (df["Net Worth (₹ Crore)"] + 1e-6)
    df["EBITDA_Margin"] = df["EBITDA (₹ Crore)"] / (df["Turnover (₹ Crore)"] + 1e-6)
    df["Growth_1Y"] = df.groupby("Company Name")["Turnover (₹ Crore)"].pct_change()

    def scale(v, d, r):
        if pd.isna(v): v = d[1]
        return np.clip(np.interp(v, d, r), min(r), max(r))

    def compute_fh(r):
        return np.mean([
            scale(r["Debt_Equity"], [0,1,3], [100,80,40]),
            scale(r["Current Ratio"], [0.5,1,2], [40,70,100]),
            scale(r["DSCR"], [0.8,1.2,2], [40,70,100]),
            scale(r["ROCE (%)"], [5,10,20], [40,70,100]),
            scale(r["ROE (%)"], [5,10,20], [40,70,100])
        ])

    df["FH_Score"] = df.apply(compute_fh, axis=1)

    # =====================================================
    # 4. TRAIN AI MODEL (AUTO)
    # =====================================================
    FEATURES = [
        "FH_Score", "Debt_Equity", "EBITDA_Margin",
        "Growth_1Y", "DSCR", "Current Ratio"
    ]

    df["FH_Next"] = df.groupby("Company Name")["FH_Score"].shift(-1)
    train = df.dropna(subset=["FH_Next"])

    if len(train) < 3:
        st.error("Not enough data to train AI model.")
        return

    pipe = Pipeline([
        ("imp", SimpleImputer(strategy="median")),
        ("model", Ridge(alpha=1.2))
    ])

    pipe.fit(train[FEATURES], train["FH_Next"])

    means = train[FEATURES].mean()
    stds = train[FEATURES].std().replace(0, 1)

    # =====================================================
    # 5. COMPANY DROPDOWN
    # =====================================================
    companies = sorted(df["Company Name"].unique())
    company = st.selectbox("Select Company", companies)

    row = df[df["Company Name"] == company].iloc[-1]
    X = row[FEATURES]
    fh_ai = pipe.predict(pd.DataFrame([X]))[0]

    # =====================================================
    # 6. SCORE SUMMARY
    # =====================================================
    c1, c2, c3 = st.columns(3)

    c1.metric("FH Score (Formula)", f"{row['FH_Score']:.1f}")
    c2.metric("FH Score (AI)", f"{fh_ai:.1f}")

    risk_band = "Low" if fh_ai >= 75 else "Moderate" if fh_ai >= 50 else "High"
    c3.metric("Risk Band", risk_band)

    # =====================================================
    # 7. SHAP-STYLE EXPLANATION
    # =====================================================
    coef = pipe.named_steps["model"].coef_
    z = (X - means) / stds
    impacts = z * coef

    driver_df = pd.DataFrame({
        "Driver": FEATURES,
        "Impact": impacts.values
    }).sort_values("Impact")

    st.markdown("### 📉 Key Risk Drivers")

    if PLOTLY_AVAILABLE:
        fig = go.Figure()
        fig.add_bar(
            x=driver_df["Impact"],
            y=driver_df["Driver"],
            orientation="h",
            marker_color=["#dc2626" if v < 0 else "#16a34a" for v in driver_df["Impact"]],
            text=driver_df["Impact"].round(2),
            textposition="auto"
        )
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.dataframe(driver_df)

    # =====================================================
    # 8. POSITIVE / NEGATIVE SUMMARY
    # =====================================================
    pos = driver_df[driver_df["Impact"] > 0]
    neg = driver_df[driver_df["Impact"] < 0]

    cpos, cneg = st.columns(2)

    with cpos:
        st.markdown("#### ✅ Positive Factors")
        for _, r in pos.iterrows():
            st.write(f"• {r['Driver']} (+{r['Impact']:.2f})")

    with cneg:
        st.markdown("#### ❌ Risk Concerns")
        for _, r in neg.iterrows():
            st.write(f"• {r['Driver']} ({r['Impact']:.2f})")
