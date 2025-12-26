import streamlit as st
from datetime import date

from validation.borrower_profile_rules import validate_borrower_profile
from validation.borrower_profile import validate_borrower_profile
from validation.pincode_validator import validate_and_resolve_pincode
from validation.cin_validator import validate_cin
from validation.pan_validator import validate_pan
from validation.gstin_validator import validate_gstin
from validation.aadhaar_validator import validate_aadhaar


# ------------------ Helpers ------------------
def handle_pincode_change():
    raw = st.session_state.get("pincode", "")
@@ -100,8 +101,8 @@ def render_borrower_profile():
    address = st.text_area("Registered Address *")

    c3, c4, c5 = st.columns(3)
    c3.text_input("City *", key="city")
    c4.text_input("State *", key="state")
    c3.text_input("City *", key="city", disabled=True)
    c4.text_input("State *", key="state", disabled=True)
    c5.text_input(
        "Pincode *",
        key="pincode",
@@ -115,7 +116,6 @@ def render_borrower_profile():

    c9, c10, c11 = st.columns(3)

    # PAN
    pan = c9.text_input("PAN *", max_chars=10)
    if pan:
        pan_ok, pan_msg = validate_pan(pan)
@@ -124,7 +124,6 @@ def render_borrower_profile():
        else:
            c9.success("✔ Valid PAN")

    # GSTIN
    gstin = c10.text_input("GSTIN", max_chars=15)
    if gstin:
        gstin_ok, gstin_msg = validate_gstin(gstin, pan)
@@ -133,7 +132,6 @@ def render_borrower_profile():
        else:
            c10.success("✔ Valid GSTIN")

    # Aadhaar
    aadhaar = c11.text_input(
        "Aadhaar Number *",
        max_chars=12,
@@ -187,11 +185,12 @@ def render_borrower_profile():
            "phone": st.session_state.phone,
        }

        errors = validate_borrower_profile(form_data)
        result = validate_borrower_profile(form_data)

        if errors:
        if not result["is_valid"]:
            st.error("Please fix the following:")
            for e in errors:
            for e in result["errors"]:
                st.write("•", e)
        else:
            st.session_state.borrower_profile = result["normalized_data"]
            st.success("Borrower Profile validated successfully ✅")
