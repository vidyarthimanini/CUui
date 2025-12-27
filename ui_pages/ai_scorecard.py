import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from model.ews_model import analyze_company


# --------------------------------------------------
# SB RISK BAND DEFINITIONS (SINGLE SOURCE OF TRUTH)
# --------------------------------------------------
SB_BANDS = [
    ("SB1", 90, 100, "Excellent"),
    ("SB2", 85, 89, "Very Good"),
    ("SB3", 80, 84, "Good"),
    ("SB4", 75, 79, "Fair"),
    ("SB5", 70, 74, "Satisfactory"),
    ("SB6", 65, 69, "Below Satisfactory"),
    ("SB7", 60, 64, "Acceptable"),
    ("SB8", 55, 59, "Moderately Acceptable"),
    ("SB9", 50, 54, "Marginal"),
    ("SB10", 45, 49, "Slightly Weak"),
    ("SB11", 40, 44, "Weak"),
    ("SB12", 35, 39, "Poor"),
    ("SB13", 30, 34, "Very Poor"),
    ("SB14", 25, 29, "Extremely Poor"),
    ("SB15", 20, 24, "Critical"),
    ("SB16", 0, 19, "Unacceptable"),
]


# --------------------------------------------------
# TIMESERIES STYLE
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
# IMPACT SCORING (NEGATIVE ONLY – MODEL CONSISTENT)
# --------------------------------------------------
def score_to_impact(value, good, bad, max_impact):
    if value is None or pd.isna(value):
        return 0.0
    try:
        value = float(value)
    except Exception:
        return 0.0

    if value >= good:
        return 0.0
    if value <= bad:
        return -max_impact
    return -max_impact * (good - value) / (good - bad)


# --------------------------------------------------
# SB LOOKUP
# --------------------------------------------------
def get_sb_band(score):
    for sb, low, high, label in SB_BANDS:
        if low <= score <= high:
            return sb, label
    return "SB?", "Unknown"


# --------------------------------------------------
# MAIN PAGE
# --------------------------------------------------
def render_ai_scorecard():

    st.markdown("## 🤖 AI Model Feedback & Scorecard")
    st.divider()

    # ---------------- LOAD DATA ----------------
    df = pd.read_excel("data/2companies.xlsx")
    company = st.selectbox(
        "Select Company",
        df["Company Name"].dropna().unique()
    )

    if st.button("▶ Run AI Model"):
        st.session_state["model_result"] = analyze_company(df, company)

    if "model_result" not in st.session_state:
        st.info("Select a company and run the AI model.")
        return

    res = st.session_state["model_result"]
    last = res["latest"]

    fh_score = int(round(res["fh_score"]))
    sb_code, sb_label = get_sb_band(fh_score)
    sb_text = f"{sb_code} · {sb_label}"

    # ---------------- SCORE CARD ----------------
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
            unsafe_allow_html=True,
        )

    with right:
        st.markdown("### Risk Band Classification")
        for sb, low, high, label in SB_BANDS:
            st.markdown(
                f"**{sb}** — {label} "
                f"<span style='float:right;color:gray'>{low}–{high}</span>",
                unsafe_allow_html=True,
            )

    st.divider()

    # ---------------- DECISION ----------------
    decision = "Approve" if fh_score >= 75 else "Review" if fh_score >= 60 else "Reject"
    color = (
        "#ecfdf3" if decision == "Approve"
        else "#fff7e6" if decision == "Review"
        else "#fff1f0"
    )

    st.markdown(
        f"""
        <div style="background:{color};padding:20px;border-radius:12px">
            <h4>Decision Recommendation</h4>
            <h2>{decision}</h2>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    # ---------------- FH SCORE + 3Y FORECAST ----------------
    hist_fy = res["history"]["FY"].tolist()
    hist_score = res["history"]["FH_Score"].tolist()

    last_fy = hist_fy[-1]
    last_score = hist_score[-1]

    forecast_years = [last_fy + i for i in range(1, 4)]
    forecast_scores = (
        list(res["forecast"])
        if isinstance(res["forecast"], (list, tuple))
        else [res["forecast"]] * 3
    )

    _, mid, _ = st.columns([1, 3, 1])
    with mid:
        fig, ax = plt.subplots(figsize=(6, 2))
        ax.plot(hist_fy, hist_score, marker="o", linewidth=2, label="Historical")
        ax.plot(
            [last_fy] + forecast_years,
            [last_score] + forecast_scores,
            "--s",
            linewidth=2,
            label="Forecast (3Y)",
        )
        style_timeseries(ax, "Financial Health Score (3-Year Forecast)")
        st.pyplot(fig, width="stretch")

    st.divider()

    # ---------------- REVENUE & EBITDA ----------------
    c1, c2 = st.columns(2)

    with c1:
        fig, ax = plt.subplots(figsize=(4.5, 2.2))
        ax.plot(
            res["growth"]["FY"],
            res["growth"]["Growth_1Y"] * 100,
            marker="o",
        )
        style_timeseries(ax, "Revenue Growth (YoY %)")
        st.pyplot(fig)

    with c2:
        fig, ax = plt.subplots(figsize=(4.5, 2.2))
        ax.plot(
            res["ebitda"]["FY"],
            res["ebitda"]["EBITDA_Margin"] * 100,
            marker="s",
        )
        style_timeseries(ax, "EBITDA Margin (%)")
        st.pyplot(fig)

    st.divider()

    # ---------------- KEY RISK DRIVERS ----------------
    st.markdown("### 🔍 Key Risk Drivers (Explainable)")

    drivers = [
        ("DSCR Ratio", score_to_impact(last["DSCR"], 1.5, 0.9, 8)),
        (
            "Debt–Equity Ratio",
            score_to_impact(
                last["Net Worth (₹ Crore)"] / (last["Total Debt (₹ Crore)"] + 1e-6),
                0.6,
                0.25,
                6,
            ),
        ),
        ("Current Ratio", score_to_impact(last["Current Ratio"], 1.5, 1.0, 5)),
        ("EBITDA Margin", score_to_impact(last["EBITDA_Margin"] * 100, 20, 5, 4)),
        ("Revenue Growth (YoY)", score_to_impact(last["Growth_1Y"] * 100, 10, -5, 3)),
    ]

    positives, risks = [], []

    for name, val in drivers:
        c1, c2 = st.columns([2, 6])
        with c1:
            st.write(name)
        with c2:
            st.progress(min(abs(val) / 8, 1.0))
            st.caption(f"{val:+.1f}")

        if val < -1:
            risks.append(f"❌ {name}: {val:+.1f}")
        elif val == 0:
            positives.append(f"✅ {name}: No risk impact")

    st.divider()

    # ---------------- SUMMARY ----------------
    st.markdown("### 📋 Risk Assessment Summary")

    r1, r2 = st.columns(2)

    with r1:
        st.markdown("**Positive Factors**")
        for p in positives or ["• None identified"]:
            st.write(p)

    with r2:
        st.markdown("**Risk Concerns**")
        for r in risks or ["• No material concerns"]:
            st.write(r)

    st.divider()

    # ---------------- NAVIGATION ----------------
    n1, n2, n3 = st.columns(3)
    with n1:
        st.button("← Back to Documents")
    with n2:
        st.button("⬇ Export Report")
    with n3:
        st.button("Continue to Tools →")
