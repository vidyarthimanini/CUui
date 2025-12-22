# validation/aadhaar_validator.py

def validate_aadhaar(aadhaar: str):
    """
    Validates Aadhaar number using Verhoeff checksum
    Returns (bool, message)
    """

    if not aadhaar:
        return False, "Aadhaar number is mandatory"

    aadhaar = aadhaar.strip().replace(" ", "")

    if not aadhaar.isdigit():
        return False, "Aadhaar must contain digits only"

    if len(aadhaar) != 12:
        return False, "Aadhaar must be exactly 12 digits"

    if aadhaar[0] in {"0", "1"}:
        return False, "Aadhaar cannot start with 0 or 1"

    # ---------------- Verhoeff algorithm ----------------
    d = [
        [0,1,2,3,4,5,6,7,8,9],
        [1,2,3,4,0,6,7,8,9,5],
        [2,3,4,0,1,7,8,9,5,6],
        [3,4,0,1,2,8,9,5,6,7],
        [4,0,1,2,3,9,5,6,7,8],
        [5,9,8,7,6,0,4,3,2,1],
        [6,5,9,8,7,1,0,4,3,2],
        [7,6,5,9,8,2,1,0,4,3],
        [8,7,6,5,9,3,2,1,0,4],
        [9,8,7,6,5,4,3,2,1,0]
    ]

    p = [
        [0,1,2,3,4,5,6,7,8,9],
        [1,5,7,6,2,8,3,0,9,4],
        [5,8,0,3,7,9,6,1,4,2],
        [8,9,1,6,0,4,3,5,2,7],
        [9,4,5,3,1,2,6,8,7,0],
        [4,2,8,6,5,7,3,9,0,1],
        [2,7,9,3,8,0,6,4,1,5],
        [7,0,4,6,9,1,3,2,5,8]
    ]

    c = 0
    for i, digit in enumerate(reversed(aadhaar)):
        c = d[c][p[i % 8][int(digit)]]

    if c != 0:
        return False, "Invalid Aadhaar number (checksum failed)"

    return True, "Valid Aadhaar"
