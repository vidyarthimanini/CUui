import re
from datetime import date


# ---------------- Constants ----------------

VALID_LISTING_STATUS = {
    "L": "Listed Company",
    "U": "Unlisted Company"
}

VALID_STATE_CODES = {
    "AN","AP","AR","AS","BR","CH","CG","DD","DL","DN","GA","GJ",
    "HP","HR","JH","JK","KA","KL","LA","LD","MH","ML","MN","MP",
    "MZ","NL","OD","PB","PY","RJ","SK","TN","TR","TS","UK","UP",
    "WB"
}

VALID_COMPANY_TYPES = {
    "PTC",  # Private Limited
    "PLC",  # Public Limited
    "GOI",  # Govt of India
    "SGC",  # State Govt Company
    "NPL",  # Not-for-Profit
    "OPC",  # One Person Company
    "LLP"   # Limited Liability Partnership
}


# ---------------- Validator ----------------

def validate_cin(cin: str):
    """
    Validates Corporate Identification Number (CIN)

    Returns:
        (bool, message)
    """

    if not cin:
        return False, "CIN is mandatory"

    cin = cin.strip().upper()

    # ---------------- Length ----------------
    if len(cin) != 21:
        return False, "CIN must be exactly 21 characters"

    # ---------------- Structural Pattern ----------------
    pattern = r"^[LU]\d{5}[A-Z]{2}\d{4}[A-Z]{3}\d{6}$"
    if not re.fullmatch(pattern, cin):
        return False, "CIN format is invalid"

    # ---------------- Listing Status ----------------
    listing_status = cin[0]
    if listing_status not in VALID_LISTING_STATUS:
        return False, "CIN must start with L (Listed) or U (Unlisted)"

    # ---------------- Industry Code ----------------
    industry_code = cin[1:6]
    if not industry_code.isdigit():
        return False, "Invalid industry code in CIN"

    # ---------------- State Code ----------------
    state_code = cin[6:8]
    if state_code not in VALID_STATE_CODES:
        return False, f"Invalid state code in CIN: {state_code}"

    # ---------------- Year of Incorporation ----------------
    year_str = cin[8:12]

    if not year_str.isdigit():
        return False, "Year of incorporation in CIN must be numeric"

    year = int(year_str)
    current_year = date.today().year

    if year < 1950:
        return False, "Year of incorporation cannot be before 1950"

    if year > current_year:
        return False, f"Year of incorporation cannot be in the future ({year})"

    # ---------------- Company Classification ----------------
    company_type = cin[12:15]
    if company_type not in VALID_COMPANY_TYPES:
        return False, f"Invalid company classification in CIN: {company_type}"

    # ---------------- ROC Number ----------------
    roc_number = cin[15:]
    if not roc_number.isdigit():
        return False, "Invalid ROC registration number in CIN"

    return True, "Valid CIN"
