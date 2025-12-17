import re
from .pan_validator import validate_pan

GSTIN_REGEX = (
    r"(0[1-9]|1[0-9]|2[0-9]|3[0-8]|97|99)"
    r"[A-Z]{3}[PCHFTABGJKLE][A-Z][0-9]{4}[A-Z]"
    r"[0-9A-Z]Z[0-9A-Z]"
)

def validate_gstin(gstin: str, pan: str):
    if not gstin:
        return True, "OPTIONAL"

    gstin = gstin.upper().strip()

    if not re.fullmatch(GSTIN_REGEX, gstin):
        return False, "Invalid GSTIN format"

    embedded_pan = gstin[2:12]
    if embedded_pan != pan.upper():
        return False, "GSTIN PAN does not match PAN entered"

    return True, "VALID"
