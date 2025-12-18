import re
from datetime import date


# Valid Indian State Codes used in CIN
VALID_STATE_CODES = {
    "AN","AP","AR","AS","BR","CH","CG","DD","DL","DN","GA","GJ",
    "HP","HR","JH","JK","KA","KL","LA","LD","MH","ML","MN","MP",
    "MZ","NL","OD","PB","PY","RJ","SK","TN","TR","TS","UK","UP",
    "WB"
}

# Valid company classification codes
VALID_COMPANY_TYPES = {
    "PTC",  # Private Limited
    "PLC",  # Public Limited
    "GOI",  # Govt of India
    "SGC",  # State Govt Company
    "NPL",  # Not-for-Profit
    "OPC",  # One Person Company
    "LLP"   # Limited Liability Partnership
}


def validate_cin(cin: str):
    """
    Validates Corporate Identification Number (CIN)
    Returns: (bool, message)
    """

    if not cin:
        return False, "CIN is mandatory"

    cin = cin.strip().upper()

    if len(cin) != 21:
        return False, "CIN must be exactly 21 characters"

    # ---------------- Overall pattern ----------------
    pattern = r"^[LU]\d{5}[A-Z]{2}\d{4}[A-Z]{3}\d{6}$"
    if not re.fullmatch(pattern, cin):
        return False, "CIN format is invalid"

    # ---------------- 1st character ----------------
    listing_status = cin[0]
    if listing_status not in {"L", "U"}:
        return False, "CIN must start with L (Listed) or U (Unlisted)"

    # ---------------- Industry code ----------------
    industry_code = cin[1:6]
    if not industry_code.isdigit():
        return False, "Invalid industry code in CIN"

    # ---------------- State code ----------------
    state_code = cin[6:8]
    if state_code not in VALID_STATE_CODES:
        return False, f"Invalid state code in CIN: {state_code}"

    # ---------------- Year of incorporation ----------------
    year = int(cin[8:12])
    current_year = date.today().year

    if year < 1950 or year > current_year:
        return False, f"Invalid year of incorporation in CIN: {year}"

    # ---------------- Company classification ----------------
    company_type = cin[12:15]
    if company_type not in VALID_COMPANY_TYPES:
        return False, f"Invalid company classification in CIN: {company_type}"

    # ---------------- ROC number ----------------
    roc_number = cin[15:]
    if not roc_number.isdigit():
        return False, "Invalid ROC registration number in CIN"

    return True, "Valid CIN"
