import streamlit as st

# ============================================================
# BANKING CONDUCT — SAVE ONLY PAGE
# ============================================================

def render_banking_conduct():

    st.subheader("🏦 Banking Conduct")

    # --------------------------------------------------------
    # INIT CENTRAL SESSION STORE
    # --------------------------------------------------------
    if "data" not in st.session_state:
        st.session_state.data = {}

    if "banking_conduct" not in st.session_state.data:
        st.session_state.data["banking_conduct"] = {}

    bc = st.session_state.data["banking_conduct"]

    # --------------------------------------------------------
    # CREDIT BUREAU INFORMATION
    # --------------------------------------------------------
    st.markdown("### Credit Bureau Information")

    c1, c2 = st.columns(2)

    with c1:
        cibil_score = st.number_input(
            "CIBIL Score *",
            min_value=300,
            max_value=900,
            value=int(bc.get("cibil_score", 300)),
            step=1
        )

    with c2:
        crif_score = st.number_input(
            "CRIF Score",
            min_value=300,
            max_value=900,
            value=int(bc.get("crif_score", 300)),
            step=1
        )

    # --------------------------------------------------------
    # ACCOUNT CONDUCT
    # --------------------------------------------------------
    st.markdown("### Account Conduct")

    c3, c4 = st.columns(2)

    with c3:
        avg_bank_balance = st.number_input(
            "Average Bank Balance (Last 6 Months) * (₹ Lakh)",
            min_value=0.0,
            value=float(bc.get("avg_bank_balance_lakh", 0.0)),
            step=0.1
        )

    with c4:
        bounced_cheques = st.number_input(
            "Bounced Cheques (Count)",
            min_value=0,
            value=int(bc.get("bounced_cheques", 0)),
            step=1
        )

    overdrafts = st.number_input(
        "Overdrafts (Count)",
        min_value=0,
        value=int(bc.get("overdrafts", 0)),
        step=1
    )

    # --------------------------------------------------------
    # REPAYMENT BEHAVIOUR
    # --------------------------------------------------------
    st.markdown("### Repayment Behaviour")

    c5, c6 = st.columns(2)

    with c5:
        max_dpd = st.number_input(
            "Maximum DPD Observed",
            min_value=0,
            value=int(bc.get("max_dpd", 0)),
            step=1,
            help="Maximum days past due observed across accounts"
        )

    with c6:
        sma_classification = st.selectbox(
            "SMA Classification",
            ["SMA-0", "SMA-1", "SMA-2"],
            index=["SMA-0", "SMA-1", "SMA-2"].index(
                bc.get("sma_classification", "SMA-0")
            )
        )

    cross_bank_npa = st.selectbox(
        "Cross-Bank NPA Tag",
        ["No", "Yes"],
        index=["No", "Yes"].index(bc.get("cross_bank_npa", "No"))
    )

    # --------------------------------------------------------
    # BANKING USAGE & COMPLIANCE
    # --------------------------------------------------------
    st.markdown("### Banking Usage & Compliance")

    c7, c8 = st.columns(2)

    with c7:
        credit_utilization = st.number_input(
            "Credit Utilization (%)",
            min_value=0.0,
            max_value=100.0,
            value=float(bc.get("credit_utilization_pct", 0.0)),
            step=1.0
        )

    with c8:
        gst_filing = st.selectbox(
            "GST Filing Compliance",
            ["Regular", "Delayed", "Non-Compliant"],
            index=["Regular", "Delayed", "Non-Compliant"].index(
                bc.get("gst_filing_compliance", "Regular")
            )
        )

    # --------------------------------------------------------
    # BANKING RELATIONSHIP
    # --------------------------------------------------------
    st.markdown("### Banking Relationship")

    c9, c10 = st.columns(2)

    with c9:
        banking_vintage = st.number_input(
            "Banking Relationship Vintage (Years)",
            min_value=0,
            value=int(bc.get("banking_vintage_years", 0)),
            step=1
        )

    with c10:
        primary_bank = st.text_input(
            "Primary Bank Name",
            value=bc.get("primary_bank", "")
        )

    account_type = st.selectbox(
        "Account Type",
        ["Savings", "Current", "CC", "OD"],
        index=["Savings", "Current", "CC", "OD"].index(
            bc.get("account_type", "Current")
        )
    )

    # --------------------------------------------------------
    # SAVE ONLY
    # --------------------------------------------------------
    st.divider()

    if st.button("Save & Continue ➡️", width="stretch"):

        st.session_state.data["banking_conduct"] = {
            "cibil_score": cibil_score,
            "crif_score": crif_score,

            "avg_bank_balance_lakh": avg_bank_balance,
            "bounced_cheques": bounced_cheques,
            "overdrafts": overdrafts,

            "max_dpd": max_dpd,
            "sma_classification": sma_classification,
            "cross_bank_npa": cross_bank_npa,

            "credit_utilization_pct": credit_utilization,
            "gst_filing_compliance": gst_filing,

            "banking_vintage_years": banking_vintage,
            "primary_bank": primary_bank,
            "account_type": account_type,
        }

        st.success("Banking Conduct details saved successfully ✅")

        # navigation handled by app.py
        st.session_state.page = "Loan Request"
