import streamlit as st

def render_loan_request():
    st.markdown("### 💼 Loan Request Details")

    # -------------------------------
    # LOAN REQUIREMENTS
    # -------------------------------
    st.markdown("#### Loan Requirements")

    left, right = st.columns([2, 1.2])

    with left:
        loan_amount = st.number_input(
            "Loan Amount *",
            min_value=0.0,
            step=0.1,
            format="%.2f",
            help="Amount in ₹ Crore"
        )

        loan_type = st.selectbox(
            "Loan Type *",
            ["Select loan type", "Term Loan", "Working Capital", "CC", "OD"]
        )

        t1, t2 = st.columns(2)

        with t1:
            tenure = st.number_input(
                "Tenure * (Months)",
                min_value=1,
                step=1
            )

        with t2:
            repayment_mode = st.selectbox(
                "Repayment Mode",
                ["Select mode", "EMI", "Structured", "Bullet"]
            )

        purpose = st.text_area(
            "Purpose of Loan *",
            placeholder="Describe the purpose of loan (working capital, CAPEX, acquisition, etc.)"
        )

        utilization = st.text_area(
            "Proposed Utilization Plan",
            placeholder="How will the loan amount be utilized?"
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
            ]
        )

        c1, c2 = st.columns(2)

        with c1:
            collateral_value = st.number_input(
                "Collateral Value (₹ Cr)",
                min_value=0.0,
                step=0.1
            )

        with c2:
            ltv_ratio = st.number_input(
                "LTV Ratio (%)",
                min_value=0.0,
                max_value=100.0,
                step=0.1,
                help="Auto-calculated or manual override"
            )

        guarantors = st.text_area(
            "Guarantors / Co-applicants",
            placeholder="List promoters, directors, or corporate guarantors"
        )

        interest_type = st.radio(
            "Interest Type Preference",
            ["Fixed", "Floating", "Hybrid"],
            horizontal=True
        )

        business_plan = st.text_area(
            "Business Plan & Cash Flow Projections",
            placeholder="Provide details about business growth plans and projected cash flows"
        )

    st.divider()

    # -------------------------------
    # EXISTING LOAN DETAILS
    # -------------------------------
    st.markdown("#### Existing Loan Details")

    with st.container():
        e1, e2, e3, e4, e5, e6 = st.columns([2, 1.5, 1, 1, 1, 1.5])

        with e1:
            lender = st.text_input("Bank / NBFC")

        with e2:
            ex_loan_type = st.selectbox(
                "Loan Type",
                ["TL", "WC", "CC", "OD"]
            )

        with e3:
            sanctioned = st.number_input(
                "Sanctioned (₹ Cr)",
                min_value=0.0,
                step=0.1
            )

        with e4:
            outstanding = st.number_input(
                "Outstanding (₹ Cr)",
                min_value=0.0,
                step=0.1
            )

        with e5:
            emi = st.number_input(
                "EMI (₹ L)",
                min_value=0.0,
                step=0.1
            )

        with e6:
            ex_security = st.text_input("Security")

    st.button("➕ Add Existing Loan")

    st.divider()

    # -------------------------------
    # LOAN REQUEST SUMMARY
    # -------------------------------
    st.markdown("#### Loan Request Summary")

    s1, s2, s3, s4 = st.columns(4)

    with s1:
        st.metric("Requested Amount", f"₹ {loan_amount:.2f} Cr")

    with s2:
        st.metric("Total Exposure", "₹ 0.00 Cr")

    with s3:
        st.metric("LTV Ratio", f"{ltv_ratio:.1f} %")

    with s4:
        st.metric("Tenure", f"{tenure} M")

    st.divider()

    # -------------------------------
    # NAVIGATION
    # -------------------------------
    nav1, nav2 = st.columns([1, 1])

    with nav1:
        if st.button("← Back to Banking Conduct"):
            st.session_state.page = "Banking Conduct"

    with nav2:
        if st.button("Continue to Assessment →"):
            st.session_state.page = "Assessment"
