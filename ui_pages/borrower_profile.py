import re
import streamlit as st
from datetime import date

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

    st.subheader("Borrower Profile")

    # 🔑 Central session store
    if "data" not in st.session_state:
        st.session_state.data = {}

    if "borrower_profile" not in st.session_state.data:
        st.session_state.data["borrower_profile"] = {}

    bp = st.session_state.data["borrower_profile"]

    for k in ["city", "state", "pincode", "phone"]:
        if k not in st.session_state:
            st.session_state[k] = ""

    # ---------------- Company ----------------
    c1, c2 = st.columns(2)

    with c1:
        company_name = st.text_input(
            "Company Name *",
            value=bp.get("company_name", "")
        )

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
        cin = st.text_input(
            "CIN Number *",
            value=bp.get("cin", "")
        )
        industry = st.text_input(
            "Industry / Sub-sector",
            value=bp.get("industry", "")
        )

        if cin:
            ok, msg = validate_cin(cin)
            if not ok:
                st.warning(msg)

    registration_date = st.date_input(
        "Registration Date *",
        value=bp.get("registration_date", date.today()),
        max_value=date.today()
    )

    # ---------------- Address ----------------
    address = st.text_area(
        "Registered Address *",
        value=bp.get("address", "")
    )

    c3, c4, c5 = st.columns(3)
    c3.text_input("City *", key="city", disabled=True)
    c4.text_input("State *", key="state", disabled=True)
    c5.text_input(
        "Pincode *",
        key="pincode",
        max_chars=6,
        on_change=handle_pincode_change
    )

    # ---------------- Legal Identifiers ----------------
    st.markdown("### Legal Identifiers")

    c9, c10, c11 = st.columns(3)

    pan = c9.text_input(
        "PAN *",
        max_chars=10,
        value=bp.get("pan", "")
    )
    if pan:
        ok, msg = validate_pan(pan)
        if not ok:
            c9.warning(msg)

    gstin = c10.text_input(
        "GSTIN",
        max_chars=15,
        value=bp.get("gstin", "")
    )
    if gstin:
        ok, msg = validate_gstin(gstin, pan)
        if not ok:
            c10.warning(msg)

    aadhaar = c11.text_input(
        "Aadhaar Number *",
        max_chars=12,
        value=bp.get("aadhaar", "")
    )
    if aadhaar:
        ok, msg = validate_aadhaar(aadhaar)
        if not ok:
            c11.warning(msg)

    # ---------------- Contact ----------------
    st.markdown("### Contact")
    c6, c7, c8 = st.columns(3)

    contact_person = c6.text_input(
        "Contact Person *",
        value=bp.get("contact_person", "")
    )

    email = c7.text_input(
        "Email *",
        value=bp.get("email", "")
    )

    c8.text_input(
        "Phone Number *",
        key="phone",
        max_chars=10,
        on_change=handle_phone_change
    )

    # ---------------- SAVE ONLY ----------------
    if st.button("Save & Continue ➡️"):

        st.session_state.data["borrower_profile"] = {
            "company_name": company_name,
            "entity_type": entity_type,
            "sector": sector,
            "cin": cin,
            "industry": industry,
            "pan": pan,
            "gstin": gstin,
            "aadhaar": aadhaar,
            "registration_date": registration_date,
            "address": address,
            "city": st.session_state.get("city"),
            "state": st.session_state.get("state"),
            "pincode": st.session_state.get("pincode"),
            "contact_person": contact_person,
            "email": email,
            "phone": st.session_state.get("phone"),
        }

        st.success("Borrower Profile saved successfully ✅")
