import streamlit as st
import pandas as pd
import plotly.graph_objects as go

def render_ai_scorecard():

    st.subheader("🤖 AI Model Scorecard")

    REQUIRED = ["ENGINEERED_DF","MODEL","FEATURES","FEATURE_MEANS","FEATURE_STDS"]

    if not all(k in st.session_state for k in REQUIRED):
        st.warning("Run Assessment first.")
        return

    df = st.session_state["ENGINEERED_DF"]
    model = st.session_state["MODEL"]
    FEATURES = st.session_state["FEATURES"]
    means = st.session_state["FEATURE_MEANS"]
    stds = st.session_state["FEATURE_STDS"]

    company = st.selectbox(
        "Select Company",
        sorted(df["Company Name"].unique())
    )

    row = df[df["Company Name"] == company].iloc[-1]
    X = row[FEATURES]
    fh_pred = model.predict(pd.DataFrame([X]))[0]

    # ------------------ SCORE ------------------
    c1, c2, c3 = st.columns(3)
    c1.metric("FH Score", f"{row['FH_Score']:.2f}")
    c2.metric("AI Score", f"{fh_pred:.2f}")
    c3.metric("Risk Band", "Low" if fh_pred>=75 else "Moderate" if fh_pred>=50 else "High")

    # ------------------ SHAP STYLE ------------------
    z = (X - means) / stds
    impacts = z * model.coef_

    driver_df = pd.DataFrame({
        "Driver": FEATURES,
        "Impact": impacts
    }).sort_values("Impact")

    fig = go.Figure(go.Bar(
        x=driver_df["Impact"],
        y=driver_df["Driver"],
        orientation="h",
        marker_color=["#dc2626" if v<0 else "#16a34a" for v in driver_df["Impact"]],
        text=driver_df["Impact"].round(2),
        textposition="auto"
    ))

    st.plotly_chart(fig, use_container_width=True)
