import re
from .cin_validator import validate_cin
from .pincode_validator import validate_and_resolve_pincode

def validate_borrower_profile(data: dict):

    errors = []

    # ---------------- Company ----------------
    if not data.get("company_name"):
        errors.append("Company Name is mandatory")

    if data.get("entity_type") == "Select entity type":
        errors.append("Type of Entity is mandatory")

    if data.get("sector") == "Select sector":
        errors.append("Sector is mandatory")

    # ---------------- CIN ----------------
    cin_ok, cin_msg = validate_cin(data.get("cin"))
    if not cin_ok:
        errors.append(cin_msg)

    # ---------------- Address ----------------
    if not data.get("address"):
        errors.append("Registered Address is mandatory")

    # ---------------- PINCODE (India Post Master) ----------------
    pin_ok, pin_msg, city, state = validate_and_resolve_pincode(
        data.get("pincode")
    )

    if not pin_ok:
        errors.append(pin_msg)
    else:
        # auto-derive city & state (single source of truth)
        data["city"] = city
        data["state"] = state

    # ❌ DO NOT validate city/state manually anymore
    # They come only from the pincode master

    # ---------------- Contact ----------------
    if not data.get("contact_person"):
        errors.append("Contact Person is mandatory")

    if not re.fullmatch(r"[^@]+@[^@]+\.[^@]+", data.get("email") or ""):
        errors.append("Invalid Email format")

    # Phone stored as digits only (10-digit India number)
    if not re.fullmatch(r"\d{10}", data.get("phone") or ""):
        errors.append("Phone number must be exactly 10 digits")

    return errors, data

