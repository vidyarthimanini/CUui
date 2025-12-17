import streamlit as st
from validation.borrower_profile_rules import validate_borrower_profile
from validation.pincode_validator import validate_and_resolve_pincode

# ------------------ Helpers ------------------
def handle_pincode_change():
    raw = st.session_state.get("pincode", "")

    # digits only
    cleaned = "".join(c for c in raw if c.isdigit())[:6]
    st.session_state.pincode = cleaned

    if len(cleaned) != 6:
        st.session_state.city = ""
        st.session_state.state = ""
        return

    ok, _, city, state = validate_and_resolve_pincode(cleaned)

    if ok:
        st.session_state.city = city
        st.session_state.state = state
    else:
        st.session_state.city = ""
        st.session_state.state = ""


def handle_phone_change():
    raw = st.session_state.get("phone", "")
    st.session_state.phone = "".join(c for c in raw if c.isdigit())[:10]


# ------------------ Page ------------------
def render_borrower_profile():

    st.subheader("📁 Borrower Profile")

    # ---- Init session state ----
    for k in ["city", "state", "pincode", "phone"]:
        if k not in st.session_state:
            st.session_state[k] = ""

    # ---------------- Company ----------------
    c1, c2 = st.columns(2)
    with c1:
        company_name = st.text_input("Company Name *")
        entity_type = st.selectbox(
            "Type of Entity *",
            ["Select entity type", "Pvt Ltd", "LLP", "Partnership", "Proprietorship", "Public Sector Undertaking (PSU)", "Unlisted Compant", "Listed Company" ]
        )
        sector = st.selectbox(
            "Sector *",
            ["Select sector", "Manufacturing", "Trading", "Services", "Agriculture", "Real Estate", "Healthcare", "IT & Technology", "Retail", "Hospitality", "Transportation"]
        )
    with c2:
        cin = st.text_input("CIN Number *")
        industry = st.text_input("Industry / Sub-sector")
     registration_date = st.date_input(
            "Registration Date *",
            max_value=date.today()
     )
    # ---------------- Address ----------------
    address = st.text_area("Registered Address *")

    c3, c4, c5 = st.columns(3)

    c3.text_input("City *", key="city")
    c4.text_input("State *", key="state")

    c5.text_input(
        "Pincode *",
        key="pincode",
        max_chars=6,
        on_change=handle_pincode_change,
        help="6-digit India Post PIN"
    )

    # ---------------- Tax IDs ----------------
    st.markdown("### Legal Identifiers")

    c9, c10 = st.columns(2)
    pan = c9.text_input("PAN *", max_chars=10)
    gstin = c10.text_input("GSTIN", max_chars=15)
    # ---------------- Contact ----------------
    c6, c7, c8 = st.columns(3)

    contact_person = c6.text_input("Contact Person *")
    email = c7.text_input("Email *")

    c8.text_input(
        "Phone Number *",
        key="phone",
        max_chars=10,
        on_change=handle_phone_change,
        help="10-digit mobile number"
    )

    # ---------------- Submit ----------------
    if st.button("Continue ➡️"):

        form_data = {
            "company_name": company_name,
            "entity_type": entity_type,
            "sector": sector,
            "cin": cin,
            "pan": pan,
            "gstin": gstin,
            "registration_date": registration_date,
            "address": address,
            "city": st.session_state.city,
            "state": st.session_state.state,
            "pincode": st.session_state.pincode,
            "contact_person": contact_person,
            "email": email,
            "phone": st.session_state.phone,
        }

        errors, _ = validate_borrower_profile(form_data)

        if errors:
            st.error("Please fix the following:")
            for e in errors:
                st.write("•", e)
        else:
            st.success("Borrower Profile validated successfully ✅")
