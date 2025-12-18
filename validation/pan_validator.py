import re

PAN_REGEX = r"^[A-Z]{3}[PCHFTABGJKLE][A-Z][0-9]{4}[A-Z]$"

def validate_pan(pan: str):
    if not pan:
        return False, "PAN is mandatory"

    pan = pan.strip().upper()

    if not re.fullmatch(PAN_REGEX, pan):
        return False, "Invalid PAN format (e.g. AAACR5055K)"

    return True, "VALID"
