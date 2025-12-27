import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from model.ews_model import analyze_company


# --------------------------------------------------
# COLAB-LIKE TIME SERIES STYLE
# --------------------------------------------------
def style_timeseries(ax, title):
    ax.set_title(title, fontsize=10)
    ax.grid(alpha=0.35)
    ax.tick_params(axis="both", labelsize=8)
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.legend(fontsize=8)


# --------------------------------------------------
# IMPACT SCORING
# --------------------------------------------------
def score_to_impact(value, good, bad, max_impact):
    if value is None or pd.isna(value):
        return 0.0
    value = float(value)

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
    st.divider()

    # ---------------- DATA ----------------
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

    # ---------------- SCORE CARD ----------------
    l, r = st.columns([1, 2])

    with l:
        st.markdown(
            f"""
            <div style="background:#f3f4ff;padding:30px;border-radius:12px;text-align:center">
                <h1 style="color:#5b5ff2">{fh_score}</h1>
                <p>Risk Score</p>
                <b>{sb_text}</b>
            </div>
            """,
            unsafe_allow_html=True
        )

    with r:
        st.markdown("### Risk Band Classification")
        for b, l, r in [
            ("SB1","Excellent","90–100"),("SB2","Very Good","85–89"),
            ("SB3","Good","80–84"),("SB4","Good","75–79"),
            ("SB5","Satisfactory","70–74"),("SB6","Satisfactory","65–69"),
            ("SB7","Acceptable","60–64"),("SB8","Acceptable","55–59")
        ]:
            st.markdown(f"**{b}** — {l} <span style='float:right'>{r}</span>", unsafe_allow_html=True)

    st.divider()

    # ---------------- DECISION ----------------
    decision = "Approve" if fh_score >= 75 else "Review" if fh_score >= 60 else "Reject"
    color = "#ecfdf3" if decision=="Approve" else "#fff7e6" if decision=="Review" else "#fff1f0"

    st.markdown(
        f"""
        <div style="background:{color};padding:20px;border-radius:12px">
            <h4>Decision Recommendation</h4>
            <h2>{decision}</h2>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    # ==================================================
    # 📈 FINANCIAL HEALTH SCORE (COLAB-STYLE FORECAST)
    # ==================================================
    hist_fy = res["history"]["FY"].astype(int).tolist()
    hist_score = res["history"]["FH_Score"].tolist()

    last_fy = hist_fy[-1]
    last_score = hist_score[-1]

    forecast_years = [last_fy + i for i in range(1, 4)]
    forecast_scores = res["forecast"]  # LIST OF 3 VALUES

    fig, ax = plt.subplots(figsize=(5.5, 2.5))

    ax.plot(hist_fy, hist_score, marker="o", linewidth=2, label="Historical")
    ax.plot(
        [last_fy] + forecast_years,
        [last_score] + forecast_scores,
        "--s",
        linewidth=2,
        label="Forecast"
    )

    style_timeseries(ax, "Financial Health Score")
    st.pyplot(fig)

    # ==================================================
    # 📈 REVENUE & EBITDA (SIDE BY SIDE, SMALL)
    # ==================================================
    c1, c2 = st.columns(2)

    with c1:
        fig, ax = plt.subplots(figsize=(4.5, 2.2))
        ax.plot(
            res["growth"]["FY"].astype(int),
            res["growth"]["Growth_1Y"] * 100,
            marker="o",
            linewidth=2,
            label="Revenue Growth"
        )
        style_timeseries(ax, "Revenue Growth (%)")
        st.pyplot(fig)

    with c2:
        fig, ax = plt.subplots(figsize=(4.5, 2.2))
        ax.plot(
            res["ebitda"]["FY"].astype(int),
            res["ebitda"]["EBITDA_Margin"] * 100,
            marker="s",
            linewidth=2,
            label="EBITDA Margin"
        )
        style_timeseries(ax, "EBITDA Margin (%)")
        st.pyplot(fig)

    st.divider()

    # ---------------- KEY DRIVERS ----------------
    st.markdown("### 🔍 Key Risk Drivers")

    drivers = [
        ("DSCR Ratio", score_to_impact(last["DSCR"], 1.5, 0.9, 8)),
        ("Debt–Equity Ratio", score_to_impact(
            last["Net Worth (₹ Crore)"]/(last["Total Debt (₹ Crore)"]+1e-6),
            0.6, 0.25, 6)),
        ("Current Ratio", score_to_impact(last["Current Ratio"], 1.5, 1.0, 5)),
        ("EBITDA Margin", score_to_impact(last["EBITDA_Margin"]*100, 20, 5, 4)),
        ("Revenue Growth (YoY)", score_to_impact(last["Growth_1Y"]*100, 10, -5, 3))
    ]

    for name, val in drivers:
        c1, c2 = st.columns([2, 6])
        with c1:
            st.write(name)
        with c2:
            st.progress(min(abs(val)/8, 1))
            st.caption(f"{int(round(val)):+d}")

    st.divider()

    # ---------------- NAV ----------------
    a, b, c = st.columns(3)
    with a: st.button("← Back to Documents")
    with b: st.button("⬇ Export Report")
    with c: st.button("Continue to Tools →")
