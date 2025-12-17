import re

CIN_PATTERN = r"^[LU][0-9]{5}[A-Z]{2}[0-9]{4}[A-Z]{3}[0-9]{6}$"

def validate_cin(cin):
    if not cin:
        return False
    return bool(re.fullmatch(CIN_PATTERN, cin))
