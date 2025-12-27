import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from model.ews_model import analyze_company
from matplotlib.ticker import MaxNLocator


# --------------------------------------------------
# PLOT NORMALIZER (DO NOT TOUCH)
# --------------------------------------------------
def finalize_small_plot(ax, title=None, x_vals=None):
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))

    if x_vals is not None and len(x_vals) > 1:
        ax.set_xlim(min(x_vals) - 0.2, max(x_vals) + 0.2)

    if title:
        ax.set_title(title, fontsize=9)

    ax.tick_params(axis="both", labelsize=8)
    ax.grid(alpha=0.3)

    plt.subplots_adjust(left=0.10, right=0.98, top=0.85, bottom=0.25)


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
            ("SB1","Excellent","90–100"),
            ("SB2","Very Good","85–89"),
            ("SB3","Good","80–84"),
            ("SB4","Good","75–79"),
            ("SB5","Satisfactory","70–74"),
            ("SB6","Satisfactory","65–69"),
            ("SB7","Acceptable","60–64"),
            ("SB8","Acceptable","55–59"),
        ]
        for b, l, r in bands:
            st.markdown(
                f"**{b}** — {l} <span style='float:right;color:gray'>{r}</span>",
                unsafe_allow_html=True
            )

    st.divider()

    # --------------------------------------------------
    # DECISION
    # --------------------------------------------------
    decision = "Approve" if fh_score >= 75 else "Review" if fh_score >= 60 else "Reject"
    decision_color = "#ecfdf3" if decision == "Approve" else "#fff7e6" if decision == "Review" else "#fff1f0"

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
    # 📈 FINANCIAL HEALTH + FORECAST
    # --------------------------------------------------
    fig, ax = plt.subplots(figsize=(4.8, 1.8))

    x_hist = res["history"]["FY"].astype(int)
    y_hist = res["history"]["FH_Score"].round(0)

    ax.plot(x_hist, y_hist, marker="o", label="Historical")

    x_fc = [x_hist.iloc[-1], x_hist.iloc[-1] + 1]
    y_fc = [int(round(y_hist.iloc[-1])), int(round(res["forecast"]))]

    ax.plot(x_fc, y_fc, "--s", label="Forecast")

    finalize_small_plot(ax, "Financial Health Score", x_vals=list(x_hist) + x_fc)
    ax.legend(fontsize=8)

    st.pyplot(fig)

    # --------------------------------------------------
    # 📈 REVENUE GROWTH
    # --------------------------------------------------
    fig, ax = plt.subplots(figsize=(4.8, 1.8))

    x_rev = res["growth"]["FY"].astype(int)
    y_rev = (res["growth"]["Growth_1Y"] * 100).round(0)

    ax.plot(x_rev, y_rev, "o-")

    finalize_small_plot(ax, "Revenue Growth (%)", x_vals=x_rev)

    st.pyplot(fig)

    # --------------------------------------------------
    # 📈 EBITDA MARGIN
    # --------------------------------------------------
    fig, ax = plt.subplots(figsize=(4.8, 1.8))

    x_eb = res["ebitda"]["FY"].astype(int)
    y_eb = (res["ebitda"]["EBITDA_Margin"] * 100).round(0)

    ax.plot(x_eb, y_eb, "s-")

    finalize_small_plot(ax, "EBITDA Margin (%)", x_vals=x_eb)

    st.pyplot(fig)

    st.divider()

    # --------------------------------------------------
    # 🔍 KEY RISK DRIVERS
    # --------------------------------------------------
    st.markdown("### 🔍 Key Risk Drivers (Explainable Impact)")

    drivers = [
        ("DSCR Ratio", score_to_impact(last["DSCR"], 1.5, 0.9, 8)),
        ("Debt–Equity Ratio",
         score_to_impact(
             last["Net Worth (₹ Crore)"] / (last["Total Debt (₹ Crore)"] + 1e-6),
             0.6, 0.25, 6)),
        ("Current Ratio", score_to_impact(last["Current Ratio"], 1.5, 1.0, 5)),
        ("EBITDA Margin", score_to_impact(last["EBITDA_Margin"] * 100, 20, 5, 4)),
        ("Revenue Growth (YoY)",
         score_to_impact(last["Growth_1Y"] * 100 if not pd.isna(last["Growth_1Y"]) else None,
                         10, -5, 3)),
    ]

    for name, val in drivers:
        c1, c2 = st.columns([2, 6])
        with c1:
            st.write(name)
        with c2:
            st.progress(min(abs(val) / 8, 1.0))
            st.caption(f"{val:+.1f}")

    st.divider()
