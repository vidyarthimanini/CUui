import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from model.fh_model import run_model
from engine.engine import sb_label, categorize_score_numeric

def render_ai_scorecard():

    st.markdown("## 🤖 AI Model Feedback & Scorecard")
    st.divider()

    # -----------------------------
    # UPLOAD FILES
    # -----------------------------
    master_file = st.file_uploader(
        "Upload Master Dataset (Training)",
        type=["xlsx"],
        key="master"
    )

    input_file = st.file_uploader(
        "Upload Input Dataset (Prediction)",
        type=["xlsx"],
        key="input"
    )

    if not master_file or not input_file:
        st.info("Upload both files to continue.")
        return

    master_df = pd.read_excel(master_file)
    input_df = pd.read_excel(input_file)

    # -----------------------------
    # RUN MODEL (ONCE)
    # -----------------------------
    if st.button("🚀 Calculate Risk"):

        with st.spinner("Running AI model..."):
            result = run_model(master_df, input_df)

        st.session_state["AI_RESULT"] = result

    if "AI_RESULT" not in st.session_state:
        return

    res = st.session_state["AI_RESULT"]
    df = res["engineered_input"]
    model = res["model"]
    FEATURES = res["features"]
    means = res["means"]
    stds = res["stds"]

    # -----------------------------
    # COMPANY SELECTION
    # -----------------------------
    company = st.selectbox(
        "Select Company",
        df["Company Name"].dropna().unique()
    )

    row = df[df["Company Name"] == company].iloc[-1]
    X = row[FEATURES]

    fh_pred = model.predict(pd.DataFrame([X]))[0]
    sb_code, sb_text, sb_range = sb_label(fh_pred)
    risk_band = categorize_score_numeric(fh_pred)

    # -----------------------------
    # SCORE CARD
    # -----------------------------
    c1, c2, c3 = st.columns(3)
    c1.metric("FH Score (Formula)", f"{row['FH_Score']:.2f}")
    c2.metric("FH Score (AI)", f"{fh_pred:.2f}")
    c3.metric("Risk Band", risk_band)

    st.divider()

    # -----------------------------
    # SHAP-STYLE DRIVER ANALYSIS
    # -----------------------------
    coef = model.named_steps["model"].coef_
    z = (X - means) / stds
    impacts = z * coef

    driver_df = pd.DataFrame({
        "Feature": FEATURES,
        "Impact": impacts.values
    }).sort_values("Impact")

    colors = ["#dc2626" if v < 0 else "#16a34a" for v in driver_df["Impact"]]

    fig = go.Figure(go.Bar(
        x=driver_df["Impact"],
        y=driver_df["Feature"],
        orientation="h",
        marker_color=colors,
        text=[f"{v:.2f}" for v in driver_df["Impact"]],
        textposition="auto"
    ))

    fig.update_layout(
        title="Key Risk Drivers (Explainable AI)",
        height=400
    )

    st.plotly_chart(fig, use_container_width=True)
