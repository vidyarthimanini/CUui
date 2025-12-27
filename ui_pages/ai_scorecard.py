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
# SYMMETRIC EXPLAINABLE IMPACT (KEY DRIVERS ONLY)
# --------------------------------------------------
def explainable_impact(value, good, bad, max_impact):
    """
    Symmetric explainability impact.
    -max_impact (worst) → 0 → +max_impact (best)
    """
    if value is None or pd.isna(value):
        return 0.0

    try:
        value = float(value)
    except:
        return 0.0

    if value <= bad:
        return -max_impact
    if value >= good:
        return +max_impact

    mid = (good + bad) / 2
    return (value - mid) / (good - mid) * max_impact


# --------------------------------------------------
# SB BAND DEFINITIONS
# --------------------------------------------------
SB_BANDS = [
    ("SB1", "Excellent", 90, 100),
    ("SB2", "Very Good", 85, 89),
    ("SB3", "Good", 80, 84),
    ("SB4", "Good", 75, 79),
    ("SB5", "Satisfactory", 70, 74),
    ("SB6", "Satisfactory", 65, 69),
    ("SB7", "Acceptable", 60, 64),
    ("SB8", "Acceptable", 55, 59),
    ("SB9", "Marginal", 50, 54),
    ("SB10", "Marginal", 45, 49),
    ("SB11", "Weak", 40, 44),
    ("SB12", "Poor", 35, 39),
    ("SB13", "Poor", 30, 34),
    ("SB14", "Very Poor", 25, 29),
    ("SB15", "Very Poor", 20, 24),
    ("SB16", "Unacceptable", 0, 19),
]


# --------------------------------------------------
# MAIN PAGE
# --------------------------------------------------
def render_ai_scorecard():

    st.markdown("## 🤖 AI Model Feedback & Scorecard")
    st.divider()

    # --------------------------------------------------
    # LOAD DATA
    # --------------------------------------------------
    df = pd.read_excel("data/Indian_Companies_EWS_READY_WITH_FY2025.xlsx")
    company = st.selectbox("Select Company", df["Company Name"].dropna().unique())

    if st.button("▶ Run AI Model"):
        st.session_state["model_result"] = analyze_company(df, company)

    if "model_result" not in st.session_state:
        st.info("Select a company and run the AI model.")
        return

    res = st.session_state["model_result"]
    last = res["latest"]

    fh_score = int(round(res["fh_score"]))

    # --------------------------------------------------
    # DERIVE SB BAND DYNAMICALLY
    # --------------------------------------------------
    sb_code, sb_label = "SB?", "Unknown"
    for b, label, low, high in SB_BANDS:
        if low <= fh_score <= high:
            sb_code, sb_label = b, label
            break

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
                <span style="color:#d9534f;font-weight:600">{sb_code} · {sb_label}</span>
            </div>
            """,
            unsafe_allow_html=True
        )

    with right:
        st.markdown("### Risk Band Classification")
        for b, label, low, high in SB_BANDS:
            highlight = (
                "background:#eef2ff;border-radius:6px;padding:4px;"
                if b == sb_code else ""
            )
            st.markdown(
                f"""
                <div style="{highlight}">
                    <b>{b}</b> {label}
                    <span style="float:right;color:gray">{low}–{high}</span>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.divider()

    # --------------------------------------------------
    # DECISION
    # --------------------------------------------------
    decision = "Approve" if fh_score >= 75 else "Review" if fh_score >= 60 else "Reject"
    color = "#ecfdf3" if decision == "Approve" else "#fff7e6" if decision == "Review" else "#fff1f0"

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

    # --------------------------------------------------
    # KEY RISK DRIVERS
    # --------------------------------------------------
    st.markdown("### 🔍 Key Risk Drivers (Explainable)")

    drivers = [
        ("DSCR Ratio", explainable_impact(last["DSCR"], 1.5, 0.9, 8)),
        ("Debt–Equity Ratio",
         explainable_impact(
             last["Net Worth (₹ Crore)"] / (last["Total Debt (₹ Crore)"] + 1e-6),
             0.6, 0.25, 6)),
        ("Current Ratio", explainable_impact(last["Current Ratio"], 1.5, 1.0, 5)),
        ("EBITDA Margin", explainable_impact(last["EBITDA_Margin"] * 100, 20, 5, 4)),
        ("Revenue Growth (YoY)",
         explainable_impact(
             last["Growth_1Y"] * 100 if not pd.isna(last["Growth_1Y"]) else None,
             10, -5, 3)),
    ]

    for name, val in drivers:
        c1, c2 = st.columns([2, 6])

        with c1:
            st.write(name)

        with c2:
            bar_val = min(abs(val) / 8, 1.0)
            st.progress(bar_val)

            if val < 0:
                st.markdown(
                    f"<span style='color:#d62728;font-weight:600'>🔴 {val:+.1f}</span>",
                    unsafe_allow_html=True
                )
            elif val > 0:
                st.markdown(
                    f"<span style='color:#1f77b4;font-weight:600'>🔵 +{val:.1f}</span>",
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    "<span style='color:#2ca02c;font-weight:600'>🟢 Neutral</span>",
                    unsafe_allow_html=True
                )

    st.divider()

    # --------------------------------------------------
    # RISK SUMMARY
    # --------------------------------------------------
    st.markdown("### 📋 Risk Assessment Summary")

    positives, risks = [], []
    for name, val in drivers:
        if val < -1:
            risks.append(f"❌ {name}: {val:+.1f}")
        elif val > 1:
            positives.append(f"✅ {name}: +{val:.1f}")

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("**Positive Factors**")
        for p in positives or ["• None"]:
            st.write(p)

    with c2:
        st.markdown("**Risk Concerns**")
        for r in risks or ["• No material concerns"]:
            st.write(r)

    st.divider()

    # --------------------------------------------------
    # NAVIGATION
    # --------------------------------------------------
    n1, n2, n3 = st.columns(3)
    with n1: st.button("← Back to Documents")
    with n2: st.button("⬇ Export Report")
    with n3: st.button("Continue to Tools →")
