import streamlit as st

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


def render_ai_scorecard(calculating=False):
    st.markdown("## 🤖 AI Model Feedback & Scorecard")

    # -----------------------------------
    # HEADER ACTIONS
    # -----------------------------------
    top_l, top_r = st.columns([4, 1])
    with top_r:
        if calculating:
            st.button("⏳ Calculating...", disabled=True)
        else:
            st.button("🔄 Recalculate Score")

    st.divider()

    # -----------------------------------
    # CALCULATING STATE
    # -----------------------------------
    if calculating:
        st.markdown("### AI Model Processing")
        st.caption("Analyzing financial data and risk factors...")
        st.progress(0.65)
        st.divider()

    # -----------------------------------
    # SCORE + RISK BAND
    # -----------------------------------
    left, right = st.columns([1, 2])

    with left:
        st.markdown(
            """
            <div style="background:#f3f4ff;padding:30px;border-radius:12px;text-align:center">
                <h1 style="color:#5b5ff2;margin-bottom:0">30</h1>
                <p>Risk Score</p>
                <span style="color:#d9534f;font-weight:600">SB13 · Poor</span>
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

        for b, label, rng in bands:
            st.markdown(
                f"**{b}** — {label} <span style='float:right;color:gray'>{rng}</span>",
                unsafe_allow_html=True
            )

        st.markdown("<small><a href='#'>View All Risk Bands (SB9–SB16)</a></small>",
                    unsafe_allow_html=True)

    st.divider()

    # -----------------------------------
    # DECISION
    # -----------------------------------
    st.markdown(
        """
        <div style="background:#fff1f0;padding:20px;border-radius:12px">
            <h4 style="color:#d9534f">Decision Recommendation</h4>
            <h2>Reject</h2>
            <p>Application does not meet minimum risk criteria for approval.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    # -----------------------------------
    # 🔍 DYNAMIC SHAP DRIVERS
    # -----------------------------------
    st.markdown("### 🔍 Key Risk Drivers (SHAP Analysis)")

    financials = st.session_state.get("financials", {})
    banking = st.session_state.get("banking_conduct", {})
    assessment = st.session_state.get("assessment", {})

    dscr = financials.get("dscr")
    current_ratio = financials.get("current_ratio")
    debt_equity = financials.get("debt_equity")
    ebitda_margin = financials.get("ebitda_margin")
    revenue_growth = financials.get("revenue_growth_yoy")

    dscr_impact = score_to_impact(dscr, good=1.5, bad=0.9, max_impact=8)
    cr_impact = score_to_impact(current_ratio, good=1.5, bad=1.0, max_impact=5)

    de_impact = score_to_impact(
        (1 / debt_equity) if debt_equity and debt_equity > 0 else None,
        good=0.6, bad=0.25, max_impact=4
    )

    ebitda_impact = score_to_impact(ebitda_margin, good=20, bad=5, max_impact=4)
    growth_impact = score_to_impact(revenue_growth, good=10, bad=-5, max_impact=3)

    banking_score = 0
    banking_score += 2 if banking.get("max_dpd_entity", 0) > 60 else 0
    banking_score += 2 if banking.get("dpd60_12m", 0) > 0 else 0
    banking_score += 1.5 if banking.get("bounced", 0) > 1 else 0
    banking_score += 1 if banking.get("gst_compliance") == "Irregular" else 0
    banking_score += 1 if banking.get("cross_bank_npa") == "Yes" else 0

    banking_impact = -min(banking_score, 8)

    industry_map = {"Low": -1, "Medium": -3, "High": -5}
    industry_impact = industry_map.get(assessment.get("industry_risk"), 0)

    drivers = [
        ("DSCR Ratio", dscr_impact),
        ("Banking Conduct", banking_impact),
        ("Industry Risk", industry_impact),
        ("Debt–Equity Ratio", de_impact),
        ("Current Ratio", cr_impact),
        ("EBITDA Margin", ebitda_impact),
        ("Revenue Growth (YoY)", growth_impact),
    ]

    for name, val in drivers:
        c1, c2 = st.columns([2, 6])
        with c1:
            st.write(name)
        with c2:
            st.progress(min(abs(val) / 8, 1.0))
            st.caption(f"{val:+.1f}")

    st.divider()
    # -----------------------------------
    # 📋 DYNAMIC RISK SUMMARY
    # -----------------------------------
    st.markdown("### 📋 Risk Assessment Summary")

    positive_factors = []
    risk_concerns = []

    for name, val in drivers:
        if val <= -1.0:
            risk_concerns.append(f"❌ {name}: {val:+.1f} points")
        elif val > -0.5:
            positive_factors.append(f"✅ {name}")

    r1, r2 = st.columns(2)

    with r1:
        st.markdown("**Positive Factors**")
        if positive_factors:
            for p in positive_factors:
                st.write(p)
        else:
            st.write("• None identified")

    with r2:
        st.markdown("**Risk Concerns**")
        if risk_concerns:
            for r in risk_concerns:
                st.write(r)
        else:
            st.write("• No material concerns")

    # -----------------------------------
    # MODEL METRICS
    # -----------------------------------
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

    # -----------------------------------
    # NAVIGATION
    # -----------------------------------
    nav1, nav2, nav3 = st.columns([1, 1, 1])

    with nav1:
        st.button("← Back to Documents")

    with nav2:
        st.button("⬇ Export Report")

    with nav3:
        st.button("Continue to Tools →")
