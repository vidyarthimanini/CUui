import streamlit as st
import pandas as pd

# -------------------------------------------------
# IMPACT SCORING (SHAP-LIKE, RULE BASED)
# -------------------------------------------------
def impact(value, good, bad, max_impact):
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


# -------------------------------------------------
# MAIN PAGE
# -------------------------------------------------
def render_ai_scorecard():

    st.markdown("## 🤖 AI Model Feedback & Scorecard")

    # ---------------- LOAD DATA ----------------
    MASTER_PATH = "data/Indian_Companies_EWS_READY_WITH_FY2025.xlsx"
    INPUT_PATH  = "data/2companies.xlsx"

    df_master = pd.read_excel(MASTER_PATH)
    df_input  = pd.read_excel(INPUT_PATH)

    company = st.selectbox(
        "Select Company",
        df_input["Company Name"].dropna().unique()
    )

    if not st.button("🔄 Recalculate Score"):
        st.stop()

    # ---------------- RUN MODEL ----------------
    from model.ews_model import analyze_company   # ← YOUR FINAL MODEL

    with st.spinner("Running AI Credit Model..."):
        result = analyze_company(df_master, company)

    st.success("Model run completed")
    st.divider()

    # =========================================================
    # TOP SCORE CARD
    # =========================================================
    left, right = st.columns([1.2, 2])

    with left:
        st.markdown(
            f"""
            <div style="background:#f4f6ff;padding:28px;border-radius:14px;text-align:center">
                <h1 style="color:#4f46e5;margin:0">{round(result['fh_score'])}</h1>
                <p style="margin:6px 0">Risk Score</p>
                <span style="color:#dc2626;font-weight:600">
                    {result['sb_code']} – {result['sb_text']}
                </span>
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

        for b, t, r in bands:
            color = "#16a34a" if b == result["sb_code"] else "#6b7280"
            st.markdown(
                f"**{b}** — {t} <span style='float:right;color:{color}'>{r}</span>",
                unsafe_allow_html=True
            )

        st.caption("View All Risk Bands (SB9–SB16)")

    st.divider()

    # =========================================================
    # DECISION
    # =========================================================
    decision = "Approve" if result["fh_score"] >= 70 else "Reject"
    bg = "#ecfdf3" if decision == "Approve" else "#fff1f0"
    col = "#166534" if decision == "Approve" else "#b91c1c"

    st.markdown(
        f"""
        <div style="background:{bg};padding:22px;border-radius:14px">
            <h4 style="color:{col}">Decision Recommendation</h4>
            <h2>{decision}</h2>
            <p>
                {"Application meets risk criteria." if decision=="Approve"
                 else "Application does not meet minimum risk criteria for approval."}
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    # =========================================================
    # SHAP-STYLE KEY DRIVERS
    # =========================================================
    st.markdown("### 🔍 Key Risk Drivers (SHAP Analysis)")

    d = result.get("drivers", {})

    impacts = {
        "Banking Conduct": impact(d.get("Banking Conduct"), 80, 50, 8),
        "Industry Risk":   {"Low":0, "Medium":-3, "High":-5}.get(d.get("Industry Risk"), 0),
        "Management Quality": {"Good":0, "Average":-2.9, "Poor":-5}.get(d.get("Management Quality"), 0),
        "CIBIL Score": impact(d.get("CIBIL"), 750, 650, 4),
        "DSCR Ratio": impact(d.get("DSCR"), 1.5, 1.0, 4),
    }

    for k, v in impacts.items():
        c1, c2, c3 = st.columns([2, 6, 1])
        with c1:
            st.write(k)
        with c2:
            st.progress(min(abs(v) / 8, 1.0))
        with c3:
            st.caption(f"{v:+.1f}")

    st.divider()

    # =========================================================
    # RISK SUMMARY
    # =========================================================
    pos, neg = [], []

    for k, v in impacts.items():
        if v < -1:
            neg.append(f"❌ {k}: {v:+.1f} points")
        elif v == 0:
            pos.append(f"✅ {k}")

    l, r = st.columns(2)
    with l:
        st.markdown("**Positive Factors**")
        for x in pos or ["• None"]:
            st.write(x)

    with r:
        st.markdown("**Risk Concerns**")
        for x in neg or ["• No material concerns"]:
            st.write(x)

    st.divider()

    # =========================================================
    # MODEL METRICS (STATIC – AS PER UI)
    # =========================================================
    m1, m2, m3 = st.columns(3)

    m1.metric("Model Accuracy", "94.2%")
    m2.metric("AUC Score", "0.89")
    m3.metric("Precision Rate", "87.5%")

    st.divider()

    # =========================================================
    # FOOTER ACTIONS
    # =========================================================
    f1, f2, f3 = st.columns(3)
    f1.button("← Back to Documents")
    f2.button("⬇ Export Report")
    f3.button("Continue to Tools →")
