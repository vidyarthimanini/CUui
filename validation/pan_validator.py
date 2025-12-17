import re

PAN_REGEX = r"[A-Z]{3}[PCHFTABGJKLE][A-Z][0-9]{4}[A-Z]"

def validate_pan(pan: str):
    if not pan:
        return False, "PAN is mandatory"

    pan = pan.upper().strip()

    if not re.fullmatch(PAN_REGEX, pan):
        return False, "Invalid PAN format"

    return True, "VALID"
