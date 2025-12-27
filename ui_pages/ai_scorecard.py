import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from model.ews_model import analyze_company


def score_to_impact(value, good, bad, max_impact):
    if value is None:
        return 0.0
    try:
        value = float(value)
    except:
        return 0.0

    if value >= good:
        return 0.0
    if value <= bad:
        return -max_impact
    return -max_impact * (good - value) / (good - bad)


def render_ai_scorecard():

    st.markdown("## 🤖 AI Model Feedback & Scorecard")
    st.divider()

    # ---------------- LOAD DATA ----------------
    df = pd.read_excel("data/Indian_Companies_EWS_READY_WITH_FY2025.xlsx")
    companies = df["Company Name"].dropna().unique()
    company = st.selectbox("Select Company", companies)

    if st.button("▶ Run AI Model"):
        result = analyze_company(df, company)
        st.session_state["model_result"] = result

    if "model_result" not in st.session_state:
        st.info("Select company and run model")
        return

    res = st.session_state["model_result"]

    # ---------------- SCORE CARD ----------------
    left, right = st.columns([1, 2])

    with left:
        st.markdown(
            f"""
            <div style="background:#f3f4ff;padding:30px;border-radius:12px;text-align:center">
                <h1 style="color:#5b5ff2;margin-bottom:0">{res["fh_score"]}</h1>
                <p>Risk Score</p>
                <span style="color:#d9534f;font-weight:600">
                    {"SB3 · Good" if res["fh_score"] >= 80 else "SB13 · Poor"}
                </span>
            </div>
            """,
            unsafe_allow_html=True
        )

    with right:
        st.markdown("### Risk Band Classification")
        bands = [
            ("SB1","Excellent","90–100"),("SB2","Very Good","85–89"),
            ("SB3","Good","80–84"),("SB4","Good","75–79"),
            ("SB5","Satisfactory","70–74"),("SB6","Satisfactory","65–69"),
            ("SB7","Acceptable","60–64"),("SB8","Acceptable","55–59"),
        ]
        for b,l,r in bands:
            st.markdown(f"**{b}** — {l} <span style='float:right;color:gray'>{r}</span>",
                        unsafe_allow_html=True)

    st.divider()

    # ---------------- FORECAST GRAPH ----------------
    fig, ax = plt.subplots(figsize=(5,2))
    ax.plot(res["history"]["FY"], res["history"]["FH_Score"], marker="o", label="Historical")
    ax.plot(
        [res["history"]["FY"].iloc[-1], res["history"]["FY"].iloc[-1]+1],
        [res["history"]["FH_Score"].iloc[-1], res["forecast"]],
        "--s", label="Forecast"
    )
    ax.legend(); ax.grid()
    st.pyplot(fig)

    # ---------------- REVENUE ----------------
    fig, ax = plt.subplots(figsize=(5,2))
    ax.plot(res["growth"]["FY"], res["growth"]["Growth_1Y"]*100, "o-")
    ax.set_title("Revenue Growth (%)")
    ax.grid()
    st.pyplot(fig)

    # ---------------- EBITDA ----------------
    fig, ax = plt.subplots(figsize=(5,2))
    ax.plot(res["ebitda"]["FY"], res["ebitda"]["EBITDA_Margin"]*100, "s-")
    ax.set_title("EBITDA Margin (%)")
    ax.grid()
    st.pyplot(fig)
