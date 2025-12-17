import streamlit as st
from validation.borrower_profile_rules import validate_borrower_profile

def render_borrower_profile():

    st.subheader("📁 Borrower Profile")

    # --- Company Info ---
    c1, c2 = st.columns(2)
    with c1:
        company_name = st.text_input("Company Name *")
        entity_type = st.selectbox(
            "Type of Entity *",
            ["Select entity type", "Pvt Ltd", "LLP", "Partnership", "Proprietorship"]
        )
        sector = st.selectbox(
            "Sector *",
            ["Select sector", "Manufacturing", "Trading", "Services"]
        )
    with c2:
        group_name = st.text_input("Group Name")
        cin = st.text_input("CIN Number *")
        industry = st.text_input("Industry / Sub-sector")

    # --- Address ---
    address = st.text_area("Registered Address *")
    c3, c4, c5 = st.columns(3)

city = c3.text_input(
    "City",
    value=st.session_state.get("city", ""),
    disabled=True
)

state = c4.text_input(
    "State",
    value=st.session_state.get("state", ""),
    disabled=True
)

pincode = c5.text_input(
    "Pincode *",
    max_chars=6,
    help="6-digit India Post PIN code"
)


    # --- Contact ---
    c6, c7, c8 = st.columns(3)
    contact_person = c6.text_input("Contact Person *")
    email = c7.text_input("Email *")
    phone = c8.text_input("Phone *")

    if st.button("Continue to Financial Data ➡️"):

        form_data = {
            "company_name": company_name,
            "entity_type": entity_type,
            "sector": sector,
            "cin": cin,
            "address": address,
            "city": city,
            "state": state,
            "pincode": pincode,
            "contact_person": contact_person,
            "email": email,
            "phone": phone,
        }

        errors = validate_borrower_profile(form_data)

        if errors:
            st.warning("⚠ Please review the following:")
            for e in errors:
                st.write("•", e)
        else:
            st.success("✅ Borrower Profile validated successfully")
