import streamlit as st

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
            st.markdown(f"**{b}** — {label} <span style='float:right;color:gray'>{rng}</span>", unsafe_allow_html=True)

        st.markdown("<small><a href='#'>View All Risk Bands (SB9–SB16)</a></small>", unsafe_allow_html=True)

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
    # SHAP DRIVERS
    # -----------------------------------
    st.markdown("### 🔍 Key Risk Drivers (SHAP Analysis)")

    drivers = [
        ("Banking Conduct", -6.4),
        ("Industry Risk", -3.8),
        ("Management Quality", -2.9),
        ("CIBIL Score", 0.0),
        ("DSCR Ratio", 0.0),
    ]

    for name, val in drivers:
        col1, col2 = st.columns([2, 6])
        with col1:
            st.write(name)
        with col2:
            st.progress(min(abs(val) / 7, 1.0))
            st.caption(f"{val:+}")

    st.divider()

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
    # RISK SUMMARY
    # -----------------------------------
    st.markdown("### 📋 Risk Assessment Summary")

    r1, r2 = st.columns(2)

    with r1:
        st.markdown("**Positive Factors**")
        st.write("• None identified")

    with r2:
        st.markdown("**Risk Concerns**")
        st.write("❌ Banking Conduct: -6.4 points")
        st.write("❌ Industry Risk: -3.8 points")
        st.write("❌ Management Quality: -2.9 points")

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
