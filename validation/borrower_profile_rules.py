import re
from .cin_validator import validate_cin
from .pan_validator import validate_pan
from .gstin_validator import validate_gstin
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

    if not data.get("registration_date"):
        errors.append("Registration Date is mandatory")

    # ---------------- CIN ----------------
    cin_ok, cin_msg = validate_cin(data.get("cin"))
    if not cin_ok:
        errors.append(cin_msg)

    # ---------------- PAN ----------------
    pan_ok, pan_msg = validate_pan(data.get("pan"))
    if not pan_ok:
        errors.append(pan_msg)

    # ---------------- GSTIN ----------------
    gst_ok, gst_msg = validate_gstin(
        data.get("gstin"),
        data.get("pan")
    )
    if not gst_ok:
        errors.append(gst_msg)

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
        # auto-derive city & state
        data["city"] = city
        data["state"] = state

    # ---------------- Contact ----------------
    if not data.get("contact_person"):
        errors.append("Contact Person is mandatory")

    # ---------------- Email ----------------
    email = data.get("email")

    if not email:
        errors.append("Email is mandatory")
    else:
        email_regex = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
        if not re.fullmatch(email_regex, email.strip()):
            errors.append("Invalid Email format")

    # ---------------- Phone ----------------
    if not re.fullmatch(r"\d{10}", data.get("phone") or ""):
        errors.append("Phone number must be exactly 10 digits")

    return {
        "is_valid": len(errors) == 0,
        "errors": errors,
        "normalized_data": data
    }
