import streamlit as st

def render_assessment():

    st.markdown("### 🧠 Qualitative Assessment")

    # --------------------------------------------------
    # INIT CENTRAL SESSION STORE
    # --------------------------------------------------
    if "data" not in st.session_state:
        st.session_state.data = {}

    if "assessment" not in st.session_state.data:
        st.session_state.data["assessment"] = {}

    a = st.session_state.data["assessment"]

    # ==================================================
    # PROMOTER & MANAGEMENT
    # ==================================================
    st.markdown("#### Promoter & Management")

    left, right = st.columns(2)

    with left:
        promoter_bg = st.text_area(
            "Promoter Background Check *",
            value=a.get("promoter_background", "")
        )

        promoter_exp = st.text_area(
            "Promoter Experience & Track Record",
            value=a.get("promoter_experience", "")
        )

        mgmt_rating = st.selectbox(
            "Management Track Record Rating *",
            ["Select rating", "Strong", "Average", "Weak"],
            index=["Select rating", "Strong", "Average", "Weak"]
            .index(a.get("management_rating", "Select rating"))
        )

        mgmt_notes = st.text_area(
            "Management Track Record Notes",
            value=a.get("management_notes", "")
        )

        group_exposure = st.text_area(
            "Group Exposure Risk Assessment",
            value=a.get("group_exposure_notes", "")
        )

        group_risk = st.radio(
            "Group Risk Level",
            ["Low", "Medium", "High", "N/A"],
            index=["Low", "Medium", "High", "N/A"]
            .index(a.get("group_risk_level", "N/A")),
            horizontal=True
        )

    # ==================================================
    # INDUSTRY & BUSINESS
    # ==================================================
    with right:
        industry_outlook = st.selectbox(
            "Industry Risk Outlook *",
            ["Select risk category", "Low", "Moderate", "High"],
            index=["Select risk category", "Low", "Moderate", "High"]
            .index(a.get("industry_risk", "Select risk category"))
        )

        industry_notes = st.text_area(
            "Industry Outlook Notes",
            value=a.get("industry_notes", "")
        )

        market_position = st.text_area(
            "Market Position & Competitive Advantage",
            value=a.get("market_position", "")
        )

        customer_base = st.text_area(
            "Customer Base Analysis",
            value=a.get("customer_base", "")
        )

        supplier_risk = st.text_area(
            "Supplier Relations & Dependencies",
            value=a.get("supplier_risk", "")
        )

        operational_risk = st.text_area(
            "Operational Risk Assessment",
            value=a.get("operational_risk", "")
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
            ["Select ESG risk level", "Low", "Medium", "High"],
            index=["Select ESG risk level", "Low", "Medium", "High"]
            .index(a.get("esg_risk_level", "Select ESG risk level"))
        )

        esg_notes = st.text_area(
            "ESG Compliance Notes",
            value=a.get("esg_notes", "")
        )

        regulatory_status = st.text_area(
            "Regulatory Compliance Status",
            value=a.get("regulatory_status", "")
        )

    # ==================================================
    # SAVE ONLY
    # ==================================================
    st.divider()

    if st.button("Save & Continue ➡️", width="stretch"):

        st.session_state.data["assessment"] = {
            "promoter_background": promoter_bg,
            "promoter_experience": promoter_exp,
            "management_rating": mgmt_rating,
            "management_notes": mgmt_notes,

            "group_exposure_notes": group_exposure,
            "group_risk_level": group_risk,

            "industry_risk": industry_outlook,
            "industry_notes": industry_notes,
            "market_position": market_position,
            "customer_base": customer_base,
            "supplier_risk": supplier_risk,
            "operational_risk": operational_risk,

            "esg_risk_level": esg_level,
            "esg_notes": esg_notes,
            "regulatory_status": regulatory_status,
        }

        st.success("Qualitative Assessment saved successfully ✅")
        st.session_state.page = "Documents"
