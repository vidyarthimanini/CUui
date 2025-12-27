import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from model.ews_model import analyze_company


# --------------------------------------------------
# SMALL, CLEAN TIMESERIES STYLE (COLAB-LIKE)
# --------------------------------------------------
def style_timeseries(ax, title):
    ax.set_title(title, fontsize=10)
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax.tick_params(axis="both", labelsize=8)
    ax.grid(alpha=0.3)

    # ✅ Only show legend if labels exist (removes warning)
    handles, labels = ax.get_legend_handles_labels()
    if labels:
        ax.legend(fontsize=8)

    plt.tight_layout(pad=0.8)


# --------------------------------------------------
# IMPACT SCORING (EXPLAINABLE)
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
    forecast_scores = list(res["forecast"]) if isinstance(res["forecast"], (list, tuple)) else [res["forecast"]] * 3

    _, mid, _ = st.columns([1, 3, 1])
    with mid:
        fig, ax = plt.subplots(figsize=(6, 2))
        ax.plot(hist_fy, hist_score, marker="o", linewidth=2, label="Historical")
        ax.plot(
            [last_fy] + forecast_years,
            [last_score] + forecast_scores,
            "--s", linewidth=2, label="Forecast (3Y)"
        )
        style_timeseries(ax, "Financial Health Score (3-Year Forecast)")
        st.pyplot(fig, width="stretch")

    st.divider()

    # --------------------------------------------------
    # 🔍 KEY RISK DRIVERS (FIXED + COLOR-CODED)
    # --------------------------------------------------
    st.markdown("### 🔍 Key Risk Drivers (Explainable)")

    drivers = [
        ("DSCR Ratio", score_to_impact(last.get("DSCR"), 1.5, 0.9, 8)),
        ("Debt–Equity Ratio", score_to_impact(
            last.get("Net Worth (₹ Crore)", 0) / (last.get("Total Debt (₹ Crore)", 0) + 1e-6),
            0.6, 0.25, 6
        )),
        ("Current Ratio", score_to_impact(last.get("Current Ratio"), 1.5, 1.0, 5)),
        ("EBITDA Margin", score_to_impact(last.get("EBITDA_Margin", 0) * 100, 20, 5, 4)),
        ("Revenue Growth (YoY)", score_to_impact(
            last.get("Growth_1Y") * 100 if pd.notna(last.get("Growth_1Y")) else None,
            10, -5, 3
        )),
    ]

    for name, val in drivers:
        c1, c2 = st.columns([2, 6])

        with c1:
            st.write(name)

        with c2:
            st.progress(min(abs(val) / 8, 1.0))

            if val == 0:
                st.markdown(
                    "<span style='color:#2ca02c;font-weight:600'>✔ No risk impact</span>",
                    unsafe_allow_html=True
                )
            elif val < 0:
                st.markdown(
                    f"<span style='color:#d62728;font-weight:600'>✖ {val:+.1f} points</span>",
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f"<span style='color:#2ca02c;font-weight:600'>▲ {val:+.1f} points</span>",
                    unsafe_allow_html=True
                )

    st.divider()

    # --------------------------------------------------
    # NAVIGATION
    # --------------------------------------------------
    n1, n2, n3 = st.columns(3)
    with n1: st.button("← Back to Documents")
    with n2: st.button("⬇ Export Report")
    with n3: st.button("Continue to Tools →")
