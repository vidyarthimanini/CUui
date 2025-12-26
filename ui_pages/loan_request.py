import streamlit as st

def render_loan_request():

    st.markdown("### 💼 Loan Request Details")

    # --------------------------------------------------
    # INIT CENTRAL SESSION STORE
    # --------------------------------------------------
    if "data" not in st.session_state:
        st.session_state.data = {}

    if "loan_request" not in st.session_state.data:
        st.session_state.data["loan_request"] = {}

    lr = st.session_state.data["loan_request"]

    # -------------------------------
    # LOAN REQUIREMENTS
    # -------------------------------
    st.markdown("#### Loan Requirements")

    left, right = st.columns([2, 1.2])

    with left:
        loan_amount = st.number_input(
            "Loan Amount * (₹ Cr)",
            min_value=0.0,
            value=float(lr.get("loan_amount_cr", 0.0)),
            step=0.1
        )

        loan_type = st.selectbox(
            "Loan Type *",
            ["Select loan type", "Term Loan", "Working Capital", "CC", "OD"],
            index=["Select loan type", "Term Loan", "Working Capital", "CC", "OD"]
            .index(lr.get("loan_type", "Select loan type"))
        )

        t1, t2 = st.columns(2)

        with t1:
            tenure = st.number_input(
                "Tenure (Months)",
                min_value=1,
                value=int(lr.get("tenure_months", 1))
            )

        with t2:
            repayment_mode = st.selectbox(
                "Repayment Mode",
                ["Select mode", "EMI", "Structured", "Bullet"],
                index=["Select mode", "EMI", "Structured", "Bullet"]
                .index(lr.get("repayment_mode", "Select mode"))
            )

        purpose = st.text_area(
            "Purpose of Loan *",
            value=lr.get("loan_purpose", "")
        )

        utilization = st.text_area(
            "Proposed Utilization Plan",
            value=lr.get("utilization_plan", "")
        )

    # -------------------------------
    # SECURITY & GUARANTORS
    # -------------------------------
    with right:
        st.markdown("#### Security & Guarantors")

        securities = st.multiselect(
            "Security Offered *",
            [
                "Hypothecation of Stock",
                "Mortgage of Property",
                "Pledge of Securities",
                "Personal Guarantee",
                "Corporate Guarantee",
                "Fixed Deposit",
                "Insurance Policy",
                "Unsecured"
            ],
            default=lr.get("securities", [])
        )

        c1, c2 = st.columns(2)

        with c1:
            collateral_value = st.number_input(
                "Collateral Value (₹ Cr)",
                min_value=0.0,
                value=float(lr.get("collateral_value_cr", 0.0)),
                step=0.1
            )

        with c2:
            ltv_ratio = st.number_input(
                "LTV Ratio (%)",
                min_value=0.0,
                max_value=100.0,
                value=float(lr.get("ltv_ratio_pct", 0.0)),
                step=0.1
            )

        guarantors = st.text_area(
            "Guarantors / Co-applicants",
            value=lr.get("guarantors", "")
        )

        interest_type = st.radio(
            "Interest Type Preference",
            ["Fixed", "Floating", "Hybrid"],
            index=["Fixed", "Floating", "Hybrid"]
            .index(lr.get("interest_type", "Fixed")),
            horizontal=True
        )

        business_plan = st.text_area(
            "Business Plan & Cash Flow Projections",
            value=lr.get("business_plan", "")
        )

    st.divider()

    # -------------------------------
    # SAVE ONLY
    # -------------------------------
    if st.button("Save & Continue ➡️", width="stretch"):

        st.session_state.data["loan_request"] = {
            "loan_amount_cr": loan_amount,
            "loan_type": loan_type,
            "tenure_months": tenure,
            "repayment_mode": repayment_mode,
            "loan_purpose": purpose,
            "utilization_plan": utilization,

            "securities": securities,
            "collateral_value_cr": collateral_value,
            "ltv_ratio_pct": ltv_ratio,
            "guarantors": guarantors,
            "interest_type": interest_type,
            "business_plan": business_plan,
        }

        st.success("Loan Request details saved successfully ✅")
        st.session_state.page = "Assessment"
