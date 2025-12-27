import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from model.ews_model import analyze_company


# --------------------------------------------------
# SMALL, CLEAN TIMESERIES STYLE
# --------------------------------------------------
def style_timeseries(ax, title):
    ax.set_title(title, fontsize=10)
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax.tick_params(axis="both", labelsize=8)
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8)
    plt.tight_layout(pad=0.8)


# --------------------------------------------------
# IMPACT SCORING (SHAP-LIKE)
# --------------------------------------------------
def score_to_impact(value, good, bad, max_impact):
    if value is None or pd.isna(value):
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


# --------------------------------------------------
# MAIN PAGE
# --------------------------------------------------
def render_ai_scorecard():

    st.markdown("## 🤖 AI Model Feedback & Scorecard")

    # -----------------------------------
    # HEADER ACTIONS
    # -----------------------------------
    top_l, top_r = st.columns([4, 1])
    with top_r:
        st.button("🔄 Recalculate Score")

    st.divider()

    # --------------------------------------------------
    # LOAD DATA + COMPANY DROPDOWN
    # --------------------------------------------------
    df = pd.read_excel("data/Indian_Companies_EWS_READY_WITH_FY2025.xlsx")
    companies = df["Company Name"].dropna().unique()
    company = st.selectbox("Select Company", companies)

    if st.button("▶ Run AI Model"):
        st.session_state["model_result"] = analyze_company(df, company)

    if "model_result" not in st.session_state:
        st.info("Select a company and run the AI model.")
        return

    res = st.session_state["model_result"]
    last = res["latest"]

    fh_score = int(round(res["fh_score"]))
    sb_text = "SB3 · Good" if fh_score >= 80 else "SB13 · Poor"

    # --------------------------------------------------
    # SCORE CARD
    # --------------------------------------------------
    left, right = st.columns([1, 2])

    with left:
        st.markdown(
            f"""
            <div style="background:#f3f4ff;padding:30px;border-radius:12px;text-align:center">
                <h1 style="color:#5b5ff2;margin-bottom:0">{fh_score}</h1>
                <p>Risk Score</p>
                <span style="color:#d9534f;font-weight:600">{sb_text}</span>
            </div>
            """,
            unsafe_allow_html=True
        )

    with right:
        st.markdown("### Risk Band Classification")
        for b, l, r in [
            ("SB1","Excellent","90–100"),
            ("SB2","Very Good","85–89"),
            ("SB3","Good","80–84"),
            ("SB4","Good","75–79"),
            ("SB5","Satisfactory","70–74"),
            ("SB6","Satisfactory","65–69"),
            ("SB7","Acceptable","60–64"),
            ("SB8","Acceptable","55–59"),
        ]:
            st.markdown(
                f"**{b}** — {l} <span style='float:right;color:gray'>{r}</span>",
                unsafe_allow_html=True
            )

    st.divider()

    # --------------------------------------------------
    # DECISION SUMMARY
    # --------------------------------------------------
    decision = "Approve" if fh_score >= 75 else "Review" if fh_score >= 60 else "Reject"
    color = "#ecfdf3" if decision=="Approve" else "#fff7e6" if decision=="Review" else "#fff1f0"

    st.markdown(
        f"""
        <div style="background:{color};padding:20px;border-radius:12px">
            <h4>Decision Recommendation</h4>
            <h2>{decision}</h2>
            <p>Based on AI-driven financial health assessment.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    # --------------------------------------------------
    # 📈 FH SCORE + 3Y FORECAST
    # --------------------------------------------------
    hist_fy = res["history"]["FY"].tolist()
    hist_score = res["history"]["FH_Score"].tolist()

    last_fy = hist_fy[-1]
    last_score = hist_score[-1]

    forecast_years = [last_fy + i for i in range(1, 4)]
    forecast_scores = (
        list(res["forecast"]) if isinstance(
