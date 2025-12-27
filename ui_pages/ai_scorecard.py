import streamlit as st
import pandas as pd
import numpy as np
from model.run_model import run_model
st.subheader("📂 Run Model")

uploaded = st.file_uploader("Upload Excel (2 companies)", type=["xlsx"])

if uploaded:
    df_tmp = pd.read_excel(uploaded)
    companies = df_tmp["Company Name"].dropna().unique()

    selected_company = st.selectbox("Select Company", companies)

    if st.button("Run AI Model"):
        with st.spinner("Running model..."):
            result = run_model(uploaded, selected_company)
            st.session_state["MODEL_RESULT"] = result
            st.success("Model executed successfully")


def render_ai_scorecard():

    st.markdown("## 🤖 AI Model Feedback & Scorecard")
    st.divider()

    # -------------------------------------------------
    # SAFE FALLBACK DATA (NO RESTRICTIONS)
    # -------------------------------------------------
    result = st.session_state.get("MODEL_RESULT", {})

    fh_score = float(result.get("fh_score", 30))
    sb_code = result.get("sb_code", "SB13")
    sb_text = result.get("sb_text", "Poor")
    sb_range = result.get("sb_range", "30–34")
    risk_band = result.get("risk_band", "High")

    drivers = result.get(
        "drivers",
        [
            ("DSCR", -6.0),
            ("Debt–Equity", -4.5),
            ("EBITDA Margin", 3.2),
            ("Revenue Growth", 2.1),
            ("Loan Type EWS", -1.8),
        ],
    )

    # -------------------------------------------------
    # SCORE CARD
    # -------------------------------------------------
    left, right = st.columns([1.2, 2])

    with left:
        st.markdown(
            f"""
            <div style="background:#f3f4ff;padding:26px;border-radius:14px;text-align:center">
                <h1 style="color:#4f46e5;margin-bottom:0">{fh_score:.0f}</h1>
                <p>Risk Score</p>
                <b>{sb_code} · {sb_text}</b>
                <div style="font-size:12px;color:gray">{sb_range}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with right:
        st.markdown("### Risk Band Classification")

        bands = [
            ("SB1","Excellent","90–100"),
            ("SB2","Very Good","85–89"),
            ("SB3","Good","80–84"),
            ("SB4","Good","75–79"),
            ("SB5","Satisfactory","70–74"),
            ("SB6","Acceptable","60–69"),
            ("SB9","Marginal","50–59"),
            ("SB13","Poor","30–49"),
        ]

        for b, t, r in bands:
            st.markdown(
                f"**{b}** — {t} <span style='float:right'>{r}</span>",
                unsafe_allow_html=True
            )

    # -------------------------------------------------
    # DECISION
    # -------------------------------------------------
    st.divider()

    if risk_band == "Low":
        decision, color = "Approve", "#16a34a"
    elif risk_band == "Moderate":
        decision, color = "Review", "#f59e0b"
    else:
        decision, color = "Reject", "#dc2626"

    st.markdown(
        f"""
        <div style="background:#fff1f0;padding:20px;border-radius:12px">
            <h4 style="color:{color}">Decision Recommendation</h4>
            <h2>{decision}</h2>
        </div>
        """,
        unsafe_allow_html=True
    )

    # -------------------------------------------------
    # KEY RISK DRIVERS (STREAMLIT NATIVE)
    # -------------------------------------------------
    st.divider()
    st.markdown("### 📉 Key Risk Drivers")

    driver_df = pd.DataFrame(drivers, columns=["Feature", "Impact"])
    driver_df = driver_df.sort_values("Impact")

    st.bar_chart(
        driver_df.set_index("Feature"),
        height=350
    )

    # -------------------------------------------------
    # SUMMARY
    # -------------------------------------------------
    st.divider()
    st.markdown("### 📋 Risk Assessment Summary")

    positives = driver_df[driver_df["Impact"] > 0].tail(3)
    negatives = driver_df[driver_df["Impact"] < 0].head(3)

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("**✅ Positive Factors**")
        for _, r in positives.iterrows():
            st.write(f"• {r['Feature']}")

    with c2:
        st.markdown("**❌ Risk Concerns**")
        for _, r in negatives.iterrows():
            st.write(f"• {r['Feature']}")
