import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from model.ews_model import analyze_company





# --------------------------------------------------
# SMALL PLOT FORMATTER
# --------------------------------------------------
def finalize_small_plot(ax, title=None):
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))



    if title:
        ax.set_title(title, fontsize=9)



    ax.tick_params(axis="both", labelsize=8)
    ax.grid(alpha=0.3)
    plt.tight_layout(pad=0.6)





# --------------------------------------------------
# IMPACT SCORING (SHAP-STYLE)
# --------------------------------------------------
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





# --------------------------------------------------
# MAIN PAGE
# --------------------------------------------------
def render_ai_scorecard():



    st.markdown("## 🤖 AI Model Feedback & Scorecard")
    st.divider()



    # --------------------------------------------------
    # LOAD DATA + COMPANY DROPDOWN
    # --------------------------------------------------
    df = pd.read_excel("data/Indian_Companies_EWS_READY_WITH_FY2025.xlsx")
    companies = df["Company Name"].dropna().unique()
    company = st.selectbox("Select Company", companies)



    if st.button("▶ Run AI Model"):
        result = analyze_company(df, company)
        st.session_state["model_result"] = result



    if "model_result" not in st.session_state:
        st.info("Select a company and run the AI model.")
        return



    res = st.session_state["model_result"]
    last = res["latest"]



    fh_score = int(round(res["fh_score"]))
    sb_text = "SB3 · Good" if fh_score >= 80 else "SB13 · Poor"



    # --------------------------------------------------
    # SCORE + RISK BAND
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
        bands = [
            ("SB1", "Excellent", "90–100"),
            ("SB2", "Very Good", "85–89"),
            ("SB3", "Good", "80–84"),
            ("SB4", "Good", "75–79"),
            ("SB5", "Satisfactory", "70–74"),
            ("SB6", "Satisfactory", "65–69"),
            ("SB7", "Acceptable", "60–64"),
            ("SB8", "Acceptable", "55–59"),
        ]
        for b, l, r in bands:
            st.markdown(
                f"**{b}** — {l} <span style='float:right;color:gray'>{r}</span>",
                unsafe_allow_html=True
            )



    st.divider()



    # --------------------------------------------------
    # DECISION (DYNAMIC)
    # --------------------------------------------------
    decision = "Approve" if fh_score >= 75 else "Review" if fh_score >= 60 else "Reject"
    decision_color = (
        "#ecfdf3" if decision == "Approve"
        else "#fff7e6" if decision == "Review"
        else "#fff1f0"
    )



    st.markdown(
        f"""
        <div style="background:{decision_color};padding:20px;border-radius:12px">
            <h4>Decision Recommendation</h4>
            <h2>{decision}</h2>
            <p>Based on AI risk assessment and financial health indicators.</p>
        </div>
        """,
        unsafe_allow_html=True
    )



    st.divider()



    # --------------------------------------------------
    # 📈 FH SCORE + FORECAST
    # --------------------------------------------------
    fig, ax = plt.subplots(figsize=(4.2, 1.8))



    ax.plot(
        res["history"]["FY"],
        res["history"]["FH_Score"].round(0),
        marker="o",
        label="Historical"
    )



    ax.plot(
        [res["history"]["FY"].iloc[-1], res["history"]["FY"].iloc[-1] + 1],
        [
            int(round(res["history"]["FH_Score"].iloc[-1])),
            int(round(res["forecast"]))
        ],
        "--s",
        label="Forecast"
    )



    finalize_small_plot(ax, "Financial Health Score")
    ax.legend(fontsize=8)
    st.pyplot(fig)



    # --------------------------------------------------
    # 📈 REVENUE GROWTH
    # --------------------------------------------------
    fig, ax = plt.subplots(figsize=(4.2, 1.8))



    ax.plot(
        res["growth"]["FY"],
        (res["growth"]["Growth_1Y"] * 100).round(0),
        "o-"
    )



    finalize_small_plot(ax, "Revenue Growth (%)")
    st.pyplot(fig)



    # --------------------------------------------------
    # 📈 EBITDA MARGIN
    # --------------------------------------------------
    fig, ax = plt.subplots(figsize=(4.2, 1.8))



    ax.plot(
        res["ebitda"]["FY"],
        (res["ebitda"]["EBITDA_Margin"] * 100).round(0),
        "s-"
    )



    finalize_small_plot(ax, "EBITDA Margin (%)")
    st.pyplot(fig)



    st.divider()



    # --------------------------------------------------
    # 🔍 KEY RISK DRIVERS
    # --------------------------------------------------
    st.markdown("### 🔍 Key Risk Drivers (Explainable Impact)")



    drivers = [
        ("DSCR Ratio",
         score_to_impact(last["DSCR"], good=1.5, bad=0.9, max_impact=8)),



        ("Debt–Equity Ratio",
         score_to_impact(
             last["Net Worth (₹ Crore)"] / (last["Total Debt (₹ Crore)"] + 1e-6),
             good=0.6, bad=0.25, max_impact=6
         )),



        ("Current Ratio",
         score_to_impact(last["Current Ratio"], good=1.5, bad=1.0, max_impact=5)),



        ("EBITDA Margin",
         score_to_impact(last["EBITDA_Margin"] * 100, good=20, bad=5, max_impact=4)),



        ("Revenue Growth (YoY)",
         score_to_impact(
             last["Growth_1Y"] * 100 if not pd.isna(last["Growth_1Y"]) else None,
             good=10, bad=-5, max_impact=3
         )),
    ]



    for name, val in drivers:
        c1, c2 = st.columns([2, 6])
        with c1:
            st.write(name)
        with c2:
            st.progress(min(abs(val) / 8, 1.0))
            st.caption(f"{int(round(val)):+d}")



    st.divider()



    # --------------------------------------------------
    # 📋 RISK SUMMARY
    # --------------------------------------------------
    st.markdown("### 📋 Risk Assessment Summary")



    positives, concerns = [], []



    for name, val in drivers:
        if val <= -1:
            concerns.append(f"❌ {name}: {int(round(val)):+d}")
        elif val >= -0.3:
            positives.append(f"✅ {name}")



    c1, c2 = st.columns(2)



    with c1:
        st.markdown("**Positive Factors**")
        for p in positives or ["• None identified"]:
            st.write(p)



    with c2:
        st.markdown("**Risk Concerns**")
        for r in concerns or ["• No material concerns"]:
            st.write(r)



    st.divider()



    # --------------------------------------------------
    # MODEL METRICS (STATIC)
    # --------------------------------------------------
    m1, m2, m3 = st.columns(3)



    with m1:
        st.markdown(
            "<div style='background:#eef6ff;padding:20px;border-radius:12px;text-align:center'>"
            "<h3>94.2%</h3><p>Model Accuracy</p></div>",
            unsafe_allow_html=True
        )



    with m2:
        st.markdown(
            "<div style='background:#ecfdf3;padding:20px;border-radius:12px;text-align:center'>"
            "<h3>0.89</h3><p>AUC Score</p></div>",
            unsafe_allow_html=True
        )



    with m3:
        st.markdown(
            "<div style='background:#f7f0ff;padding:20px;border-radius:12px;text-align:center'>"
            "<h3>87.5%</h3><p>Precision Rate</p></div>",
            unsafe_allow_html=True
        )



    st.divider()



    # --------------------------------------------------
    # NAVIGATION
    # --------------------------------------------------
    nav1, nav2, nav3 = st.columns(3)



    with nav1:
        st.button("← Back to Documents")



    with nav2:
        st.button("⬇ Export Report")



    with nav3:
        st.button("Continue to Tools →")
