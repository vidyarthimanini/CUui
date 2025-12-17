import re
from .pincode_master import load_pincode_master

def validate_and_resolve_pincode(pincode: str):
    """
    Returns:
    is_valid, message, city, state
    """

    if not pincode:
        return False, "Pincode is mandatory", None, None

    if not re.fullmatch(r"\d{6}", pincode):
        return False, "Pincode must be exactly 6 digits", None, None

    df = load_pincode_master()
    row = df[df["pincode"] == pincode]

    if row.empty:
        return False, "Pincode not found in India Post records", None, None

    city = row.iloc[0]["city"].title()
    state = row.iloc[0]["state"].title()

    return True, None, city, state
