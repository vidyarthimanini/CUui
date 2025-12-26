import streamlit as st

def render_assessment():
    st.markdown("### 🧠 Qualitative Assessment")

    # ==================================================
    # PROMOTER & MANAGEMENT
    # ==================================================
    st.markdown("#### Promoter & Management")

    left, right = st.columns(2)

    with left:
        promoter_bg = st.text_area(
            "Promoter Background Check *",
            placeholder="KYC details, previous defaulter status, criminal background, etc."
        )

        promoter_exp = st.text_area(
            "Promoter Experience & Track Record",
            placeholder="Years of experience, previous ventures, industry expertise"
        )

        mgmt_rating = st.selectbox(
            "Management Track Record Rating *",
            ["Select rating", "Strong", "Average", "Weak"]
        )

        mgmt_notes = st.text_area(
            "Management Track Record Notes",
            placeholder="Financial prudence, decision-making capability, governance practices"
        )

        group_exposure = st.text_area(
            "Group Exposure Risk Assessment",
            placeholder="If part of conglomerate, assess inter-group transactions and risks"
        )

        group_risk = st.radio(
            "Group Risk Level",
            ["Low", "Medium", "High", "N/A"],
            horizontal=True
        )

    # ==================================================
    # INDUSTRY & BUSINESS
    # ==================================================
    with right:
        industry_outlook = st.selectbox(
            "Industry Risk Outlook *",
            ["Select risk category", "Low", "Moderate", "High"]
        )

        industry_notes = st.text_area(
            "Industry Outlook Notes",
            placeholder="Use RBI/ICRA categories, growth prospects, regulatory changes"
        )

        market_position = st.text_area(
            "Market Position & Competitive Advantage",
            placeholder="Market share, competitive moats, unique selling propositions"
        )

        customer_base = st.text_area(
            "Customer Base Analysis",
            placeholder="Customer concentration, quality, retention rates"
        )

        supplier_risk = st.text_area(
            "Supplier Relations & Dependencies",
            placeholder="Key supplier dependencies, payment terms, supply chain risks"
        )

        operational_risk = st.text_area(
            "Operational Risk Assessment",
            placeholder="Technology risks, process efficiency, key person dependencies"
        )

    st.divider()

    # ==================================================
    # ESG & COMPLIANCE
    # ==================================================
    st.markdown("#### ESG & Compliance")

    left2, right2 = st.columns(2)

    with left2:
        esg_level = st.selectbox(
            "ESG Compliance Risk Level",
            ["Select ESG risk level", "Low", "Medium", "High"]
        )

        esg_notes = st.text_area(
            "ESG Compliance Notes",
            placeholder="Environmental compliance, social responsibility, governance practices"
        )

        regulatory_status = st.text_area(
            "Regulatory Compliance Status",
            placeholder="Compliance with industry regulations, pending litigations, regulatory notices"
        )

    # ==================================================
    # SUPPORTING DOCUMENTS
    # ==================================================
    with right2:
        st.markdown("#### Supporting Documents")

        st.file_uploader(
            "Promoter KYC Documents",
            type=["pdf", "jpg", "png"],
            accept_multiple_files=True
        )

        st.file_uploader(
            "Management Background Reports",
            type=["pdf", "doc", "docx"],
            accept_multiple_files=True
        )

        st.file_uploader(
            "Industry Analysis Reports",
            type=["pdf", "doc", "docx"],
            accept_multiple_files=True
        )

    st.divider()

    # ==================================================
    # QUALITATIVE ASSESSMENT SUMMARY
    # ==================================================
    st.markdown("#### Qualitative Assessment Summary")

    s1, s2, s3, s4 = st.columns(4)

    with s1:
        st.metric("Management Rating", mgmt_rating if mgmt_rating != "Select rating" else "N/A")

    with s2:
        st.metric("Industry Risk", industry_outlook if industry_outlook != "Select risk category" else "N/A")

    with s3:
        st.metric("Group Risk", group_risk)

    with s4:
        st.metric("ESG Risk", esg_level if esg_level != "Select ESG risk level" else "N/A")

    st.divider()

    # ==================================================
    # NAVIGATION
    # ==================================================
    nav1, nav2 = st.columns([1, 1])

    with nav1:
        if st.button("← Back to Loan Request"):
            st.session_state.page = "Loan Request"

    with nav2:
        if st.button("Continue to Documents →"):
            st.session_state.page = "Documents"
