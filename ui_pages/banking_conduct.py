import streamlit as st

def render_banking_conduct():
    st.markdown("### 🏦 Banking & Repayment Conduct")

    # -------------------------------
    # CREDIT BUREAU INFORMATION
    # -------------------------------
    st.markdown("#### Credit Bureau Information")
    col1, col2 = st.columns(2)

    with col1:
        cibil = st.number_input("CIBIL Score *", min_value=300, max_value=900, step=1)
        dpd = st.text_area(
            "DPD Flags & History",
            placeholder="Enter any Days Past Due flags, closed loan history, etc."
        )
        avg_balance = st.number_input(
            "Average Bank Balance (Last 6 Months) *",
            min_value=0.0,
            step=1.0,
            format="%.2f",
            help="Amount in lakhs"
        )

    with col2:
        crif = st.number_input("CRIF Score", min_value=300, max_value=900, step=1)
        bounced = st.number_input("Bounced Cheques (Count)", min_value=0, step=1)
        overdrafts = st.number_input("Overdrafts (Count)", min_value=0, step=1)

    st.divider()

    # -------------------------------
    # COMPLIANCE & EXPOSURE
    # -------------------------------
    st.markdown("#### Compliance & Exposure")
    col3, col4 = st.columns(2)

    with col3:
        gst_compliance = st.radio(
            "GST Filing Compliance *",
            ["Regular", "Irregular"],
            horizontal=True
        )
        sma_class = st.selectbox(
            "SMA Classification *",
            ["Select SMA classification", "Standard", "SMA-0", "SMA-1", "SMA-2", "NPA"]
        )

    with col4:
        crilc = st.number_input(
            "CRILC Exposure (₹5 Cr+ loans)",
            min_value=0.0,
            step=1.0,
            format="%.2f",
            help="Total bank-wise exposure in ₹ Crore"
        )
        npa_tag = st.radio(
            "Cross-Bank NPA Tag",
            ["No", "Yes"],
            horizontal=True
        )
        relationship_vintage = st.text_input(
            "Banking Relationship Vintage",
            placeholder="e.g., 5 years with primary banker"
        )

    st.divider()

    # -------------------------------
    # BANK ACCOUNT DETAILS
    # -------------------------------
    st.markdown("#### Bank Account Details")

    with st.container():
        c1, c2, c3, c4, c5 = st.columns([2, 2, 1, 1, 2])

        with c1:
            bank_name = st.text_input("Bank Name")

        with c2:
            account_type = st.selectbox(
                "Account Type",
                ["Select", "Current", "Savings", "CC", "OD"]
            )

        with c3:
            vintage_years = st.number_input("Vintage (Years)", min_value=0, step=1)

        with c4:
            avg_bal = st.number_input("Avg Balance (₹L)", min_value=0.0, step=1.0)

        with c5:
            conduct = st.selectbox(
                "Conduct",
                ["Select", "Satisfactory", "Average", "Poor"]
            )

    st.button("➕ Add Bank Account")

    st.divider()

    # -------------------------------
    # BANKING CONDUCT RISK ASSESSMENT
    # -------------------------------
    st.markdown("#### Banking Conduct Risk Assessment")

    r1, r2, r3 = st.columns(3)

    with r1:
        st.metric("Credit Score", "N/A")

    with r2:
        st.metric("SMA Status", "N/A")

    with r3:
        st.metric("Bounced Cheques", bounced if bounced else 0)

    st.divider()

    # -------------------------------
    # NAVIGATION
    # -------------------------------
    nav1, nav2 = st.columns([1, 1])

    with nav1:
        st.button("← Back to Financial Data")

    with nav2:
        st.button("Continue to Loan Request →")
