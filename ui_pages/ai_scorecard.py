import streamlit as st
import pandas as pd
import numpy as np
import io

# OPTIONAL PLOTLY (SAFE)
try:
    import plotly.graph_objects as go
    PLOTLY = True
except:
    PLOTLY = False

# MODEL IMPORT (YOU ALREADY CREATED THIS)
from model.model import run_model


# -------------------------------------------------
# HELPER: SHAP-STYLE IMPACT
# -------------------------------------------------
def score_to_impact(value, good, bad, max_impact):
    try:
        value = float(value)
    except:
        return 0.0

    if value >= good:
        return 0.0
    if value <= bad:
        return -max_impact
    return -max_impact * (good - value) / (good - bad)


# -------------------------------------------------
# MAIN PAGE
# -------------------------------------------------
def render_ai_scorecard():

    st.markdown("## 🤖 AI Model Feedback & Scorecard")
    st.caption("Explainable credit risk assessment")
    st.divider()

    # -------------------------------------------------
    # FILE UPLOAD
    # -------------------------------------------------
    uploaded = st.file_uploader(
        "📥 Upload Financial Excel",
        type=["xlsx"],
        key="ai_excel"
    )

    if uploaded is None:
        st.info("Upload an Excel file to calculate AI score")
        return

    with st.spinner("Running AI credit model..."):
        df_raw = pd.read_excel(uploaded)
        df, model, FEATURES = run_model(df_raw)

    # -------------------------------------------------
    # COMPANY DROPDOWN
    # -------------------------------------------------
    companies = sorted(df["Company Name"].dropna().unique())

    company = st.selectbox(
        "🏢 Select Company",
        companies
    )

    hist = df[df["Company Name"] == company]
    latest = hist.iloc[-1]

    # -------------------------------------------------
    # MODEL PREDICTION
    # -------------------------------------------------
    fh_formula = latest["FH_Score"]
    fh_ai = model.predict(pd.DataFrame([latest[FEATURES]]))[0]

    # SB BAND
    if fh_ai >= 90:
        sb = "SB1 · Excellent"
    elif fh_ai >= 85:
        sb = "SB2 · Very Good"
    elif fh_ai >= 80:
        sb = "SB3 · Good"
    elif fh_ai >= 75:
        sb = "SB4 · Good"
    elif fh_ai >= 70:
        sb = "SB5 · Satisfactory"
    elif fh_ai >= 60:
        sb = "SB6 · Acceptable"
    elif fh_ai >= 50:
        sb = "SB9 · Marginal"
    else:
        sb = "SB13 · Poor"

    risk_band = "Low" if fh_ai >= 75 else "Moderate" if fh_ai >= 50 else "High"

    # -------------------------------------------------
    # SCORECARD
    # -------------------------------------------------
    c1, c2, c3 = st.columns(3)

    c1.metric("FH Score (Formula)", f"{fh_formula:.2f}")
    c2.metric("FH Score (AI)", f"{fh_ai:.2f}")
    c3.metric("Risk Band", risk_band)

    st.divider()

    # -------------------------------------------------
    # SHAP-STYLE DRIVER CALCULATION
    # -------------------------------------------------
    drivers = [
        ("DSCR Ratio",
         score_to_impact(latest["DSCR"], 1.5, 0.9, 8)),

        ("Debt–Equity Ratio",
         score_to_impact(
             1 / (latest["Total Debt (₹ Crore)"] /
                  (latest["Net Worth (₹ Crore)"] + 1e-6)),
             0.6, 0.25, 6
         )),

        ("Current Ratio",
         score_to_impact(latest["Current Ratio"], 1.5, 1.0, 5)),

        ("EBITDA Margin",
         score_to_impact(latest["EBITDA_Margin"] * 100, 20, 5, 4)),

        ("Revenue Growth (YoY)",
         score_to_impact(latest["Growth_1Y"] * 100, 10, -5, 3)),

        ("Banking Conduct",
         -min(8, 2 if latest["Maximum DPD Observed"] >= 60 else 0)),

        ("Industry Risk", 0.0)  # placeholder (static for now)
    ]

    driver_df = pd.DataFrame(drivers, columns=["Driver", "Impact"])

    # -------------------------------------------------
    # DRIVER BAR CHART
    # -------------------------------------------------
    st.markdown("### 📉 Key Risk Drivers")

    if PLOTLY:
        colors = ["#dc2626" if v < 0 else "#16a34a" for v in driver_df["Impact"]]

        fig = go.Figure(go.Bar(
            x=driver_df["Impact"],
            y=driver_df["Driver"],
            orientation="h",
            marker_color=colors,
            text=[f"{v:+.1f}" for v in driver_df["Impact"]],
            textposition="auto"
        ))

        fig.update_layout(
            height=350,
            xaxis_title="Impact on FH Score",
            margin=dict(l=80, r=40, t=30, b=40)
        )

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.dataframe(driver_df)

    st.divider()

    # -------------------------------------------------
    # POSITIVE / NEGATIVE SUMMARY
    # -------------------------------------------------
    pos = driver_df[driver_df["Impact"] >= 0]
    neg = driver_df[driver_df["Impact"] < 0]

    p1, p2 = st.columns(2)

    with p1:
        st.markdown("### ✅ Positive Factors")
        if pos.empty:
            st.write("• None identified")
        for _, r in pos.iterrows():
            st.write(f"• **{r['Driver']}**")

    with p2:
        st.markdown("### ❌ Risk Concerns")
        if neg.empty:
            st.write("• No material concerns")
        for _, r in neg.iterrows():
            st.write(f"• **{r['Driver']}** ({r['Impact']:+.1f})")

    st.divider()

    # -------------------------------------------------
    # EXPORT
    # -------------------------------------------------
    out = io.BytesIO()
    driver_df.to_excel(out, index=False)

    st.download_button(
        "⬇ Export AI Scorecard",
        data=out.getvalue(),
        file_name=f"{company}_AI_Scorecard.xlsx"
    )
