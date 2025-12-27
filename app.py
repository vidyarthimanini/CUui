import streamlit as st
import pandas as pd
import numpy as np

# -------------------------------------------------
# SAFE PLOTLY IMPORT (CRITICAL)
# -------------------------------------------------
try:
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False


# -------------------------------------------------
# MAIN RENDER FUNCTION
# -------------------------------------------------
def render_ai_scorecard():

    st.markdown("## 🤖 AI Model Feedback & Scorecard")
    st.caption("Explainable credit risk assessment using ML & business logic")
    st.divider()

    # -------------------------------------------------
    # SAFETY CHECK — REQUIRED DATA
    # -------------------------------------------------
    required_keys = [
        "ENGINEERED_DF",
        "MODEL",
        "FEATURES",
        "FEATURE_MEANS",
        "FEATURE_STDS"
    ]

    for k in required_keys:
        if k not in st.session_state:
            st.warning("Please complete earlier sections before viewing AI Scorecard.")
            return

    df = st.session_state["ENGINEERED_DF"]
    model = st.session_state["MODEL"]
    FEATURES = st.session_state["FEATURES"]
    means = st.session_state["FEATURE_MEANS"]
    stds = st.session_state["FEATURE_STDS"]

    # -------------------------------------------------
    # COMPANY SELECTION
    # -------------------------------------------------
    companies = sorted(df["Company Name"].dropna().unique())

    company = st.selectbox(
        "Select Company for AI Analysis",
        companies,
        key="ai_company"
    )

    row = df[df["Company Name"] == company].iloc[-1]
    X = row[FEATURES]

    # -------------------------------------------------
    # MODEL PREDICTION
    # -------------------------------------------------
    fh_pred = model.predict(pd.DataFrame([X]))[0]

    if fh_pred >= 75:
        risk_band = "Low"
    elif fh_pred >= 50:
        risk_band = "Moderate"
    else:
        risk_band = "High"

    # -------------------------------------------------
    # SCORECARD UI
    # -------------------------------------------------
    col1, col2, col3 = st.columns(3)

    col1.metric("FH Score (Formula)", f"{row['FH_Score']:.2f}")
    col2.metric("FH Score (AI)", f"{fh_pred:.2f}")
    col3.metric("Risk Band", risk_band)

    st.divider()

    # -------------------------------------------------
    # SHAP-STYLE LINEAR IMPACT
    # -------------------------------------------------
    coef = model.coef_
    z = (X - means) / stds
    impacts = z * coef

    shap_df = pd.DataFrame({
        "Feature": FEATURES,
        "Impact": impacts.values
    })

    # -------------------------------------------------
    # BUSINESS DRIVER MAPPING
    # -------------------------------------------------
    BUSINESS_DRIVERS = {
        "DSCR": "DSCR Ratio",
        "Current Ratio": "Current Ratio",
        "FH_Score": "Debt–Equity Ratio",
        "EBITDA_Margin": "EBITDA Margin",
        "Growth_1Y": "Revenue Growth (YoY)",
        "Loan_Type_EWS": "Banking Conduct",
        "Document_Score": "Industry Risk"
    }

    driver_rows = []

    for key, label in BUSINESS_DRIVERS.items():
        match = shap_df[shap_df["Feature"].str.contains(key, case=False)]
        impact = match["Impact"].sum() if not match.empty else 0.0

        driver_rows.append({
            "Driver": label,
            "Impact": round(float(impact), 2)
        })

    driver_df = pd.DataFrame(driver_rows)

    # -------------------------------------------------
    # POSITIVE / NEGATIVE FACTORS
    # -------------------------------------------------
    pos = driver_df[driver_df["Impact"] > 0]
    neg = driver_df[driver_df["Impact"] < 0]

    cpos, cneg = st.columns(2)

    with cpos:
        st.markdown("### ✅ Positive Factors")
        if pos.empty:
            st.write("• None")
        for _, r in pos.iterrows():
            st.write(f"• **{r['Driver']}**  +{r['Impact']}")

    with cneg:
        st.markdown("### ❌ Risk Concerns")
        if neg.empty:
            st.write("• No material concerns")
        for _, r in neg.iterrows():
            st.write(f"• **{r['Driver']}**  {r['Impact']}")

    st.divider()

    # -------------------------------------------------
    # SHAP BAR CHART (OPTIONAL)
    # -------------------------------------------------
    st.markdown("### 📉 Key Risk Drivers")

    if not PLOTLY_AVAILABLE:
        st.warning("Charts unavailable (Plotly not installed).")
        st.dataframe(driver_df)
        return

    colors = ["#dc2626" if v < 0 else "#16a34a" for v in driver_df["Impact"]]

    fig = go.Figure()
    fig.add_bar(
        x=driver_df["Impact"],
        y=driver_df["Driver"],
        orientation="h",
        marker_color=colors,
        text=driver_df["Impact"],
        textposition="auto"
    )

    fig.update_layout(
        height=350,
        title="Explainable AI – Risk Driver Impact",
        xaxis_title="Impact on FH Score",
        margin=dict(l=80, r=40, t=60, b=40)
    )

    st.plotly_chart(fig, use_container_width=True)
