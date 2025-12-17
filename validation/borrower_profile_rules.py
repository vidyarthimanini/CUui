import re
from .cin_validator import validate_cin

def validate_borrower_profile(data: dict):

    errors = []

    if not data["company_name"]:
        errors.append("Company Name is mandatory")

    if data["entity_type"] == "Select entity type":
        errors.append("Type of Entity is mandatory")

    if data["sector"] == "Select sector":
        errors.append("Sector is mandatory")

    cin_ok, cin_msg = validate_cin(data["cin"])
    if not cin_ok:
        errors.append(cin_msg)

    if not data["address"]:
        errors.append("Registered Address is mandatory")

    if not data["city"]:
        errors.append("City is mandatory")

    if data["state"] == "Select state":
        errors.append("State is mandatory")

    if not re.fullmatch(r"\d{6}", data["pincode"] or ""):
        errors.append("Invalid Pincode")

    if not data["contact_person"]:
        errors.append("Contact Person is mandatory")

    if not re.fullmatch(r"[^@]+@[^@]+\.[^@]+", data["email"] or ""):
        errors.append("Invalid Email")

    if not re.fullmatch(r"\+91\d{10}", data["phone"] or ""):
        errors.append("Invalid Phone Number")

    return errors
