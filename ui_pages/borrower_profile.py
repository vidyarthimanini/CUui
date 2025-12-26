import re
import streamlit as st
from datetime import date

from validation.borrower_profile_rules import validate_borrower_profile
from validation.pincode_validator import validate_and_resolve_pincode
from validation.cin_validator import validate_cin
from validation.pan_validator import validate_pan
from validation.gstin_validator import validate_gstin
from validation.aadhaar_validator import validate_aadhaar

# ------------------ Helpers ------------------
def handle_pincode_change():
    raw = st.session_state.get("pincode", "")
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

    st.subheader(" Borrower Profile")

    for k in ["city", "state", "pincode", "phone"]:
        if k not in st.session_state:
            st.session_state[k] = ""

    # ---------------- Company ----------------
    c1, c2 = st.columns(2)

    with c1:
        company_name = st.text_input("Company Name *")

        entity_type = st.selectbox(
            "Type of Entity *",
            [
                "Select entity type",
                "Pvt Ltd",
                "LLP",
                "Partnership",
                "Proprietorship",
                "Public Sector Undertaking (PSU)",
                "Unlisted Company",
                "Listed Company",
            ],
        )

        sector = st.selectbox(
            "Sector *",
            [
                "Select sector",
                "Manufacturing",
                "Trading",
                "Services",
                "Agriculture",
                "Real Estate",
                "Healthcare",
                "IT & Technology",
                "Retail",
                "Hospitality",
                "Transportation",
            ],
        )

    with c2:
        cin = st.text_input("CIN Number *")
        industry = st.text_input("Industry / Sub-sector")

        if cin:
            cin_ok, cin_msg = validate_cin(cin)
            if not cin_ok:
                st.error(cin_msg)
            else:
                st.success("✔ Valid CIN")

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

    # ---------------- Legal Identifiers ----------------
    st.markdown("### Legal Identifiers")

    c9, c10, c11 = st.columns(3)

    # PAN
    pan = c9.text_input("PAN *", max_chars=10)
    if pan:
        pan_ok, pan_msg = validate_pan(pan)
        if not pan_ok:
            c9.error(pan_msg)
        else:
            c9.success("✔ Valid PAN")

    # GSTIN
    gstin = c10.text_input("GSTIN", max_chars=15)
    if gstin:
        gstin_ok, gstin_msg = validate_gstin(gstin, pan)
        if not gstin_ok:
            c10.error(gstin_msg)
        else:
            c10.success("✔ Valid GSTIN")

    # Aadhaar
    aadhaar = c11.text_input(
        "Aadhaar Number *",
        max_chars=12,
        help="12-digit Aadhaar number (numeric only)"
    )
    if aadhaar:
        aadhaar_ok, aadhaar_msg = validate_aadhaar(aadhaar)
        if not aadhaar_ok:
            c11.error(aadhaar_msg)
        else:
            c11.success(f"✔ Aadhaar verified (XXXX-XXXX-{aadhaar[-4:]})")

    # ---------------- Contact ----------------
    st.markdown("### Contact")
    c6, c7, c8 = st.columns(3)

    contact_person = c6.text_input("Contact Person *")
    email = c7.text_input("Email *")

    if email:
        email_regex = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
        if not re.fullmatch(email_regex, email.strip()):
            c7.error("Invalid email format")

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
            "aadhaar": aadhaar,
            "registration_date": registration_date,
            "address": address,
            "city": st.session_state.city,
            "state": st.session_state.state,
            "pincode": st.session_state.pincode,
            "contact_person": contact_person,
            "email": email,
            "phone": st.session_state.phone,
        }

        errors = validate_borrower_profile(form_data)

        if errors:
            st.error("Please fix the following:")
            for e in errors:
                st.write("•", e)
        else:
            st.success("Borrower Profile validated successfully ✅")

