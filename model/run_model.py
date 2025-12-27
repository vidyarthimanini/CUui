import pandas as pd
import numpy as np

# -----------------------------------
# SAFE NUM PARSER
# -----------------------------------
def num(x):
    try:
        return float(str(x).replace(",", "").replace("₹", ""))
    except:
        return np.nan


# -----------------------------------
# SB BAND
# -----------------------------------
def sb_band(score):
    if score >= 90: return ("SB1", "Excellent", "90–100", "Low")
    if score >= 85: return ("SB2", "Very Good", "85–89", "Low")
    if score >= 80: return ("SB3", "Good", "80–84", "Low")
    if score >= 75: return ("SB4", "Good", "75–79", "Low")
    if score >= 70: return ("SB5", "Satisfactory", "70–74", "Moderate")
    if score >= 60: return ("SB6", "Acceptable", "60–69", "Moderate")
    if score >= 50: return ("SB9", "Marginal", "50–54", "High")
    return ("SB13", "Poor", "30–34", "High")


# -----------------------------------
# MAIN MODEL RUNNER
# -----------------------------------
def run_model(excel_file, company_name):

    df = pd.read_excel(excel_file)
    df.columns = [c.strip() for c in df.columns]

    df["FY"] = pd.to_numeric(df["FY"], errors="coerce")
    df = df.dropna(subset=["Company Name", "FY"])

    # ---------------- NUMERIC CLEANING ----------------
    num_cols = [
        "Turnover (₹ Crore)", "EBITDA (₹ Crore)", "Net Profit (₹ Crore)",
        "Net Worth (₹ Crore)", "Total Debt (₹ Crore)",
        "DSCR", "Current Ratio", "ROCE (%)", "ROE (%)",
        "Credit Utilization (%)", "LTV Ratio", "Maximum DPD Observed"
    ]

    for c in num_cols:
        if c in df.columns:
            df[c] = df[c].apply(num)

    # ---------------- LOAN TYPE EWS (FIXED FOR NOW) ----------------
    df["Loan_Type_EWS"] = 70

    # ---------------- FH SCORE (YOUR EXACT LOGIC) ----------------
    def compute_fh(r):
        leverage = np.interp(
            r["Total Debt (₹ Crore)"] / (r["Net Worth (₹ Crore)"] + 1e-6),
            [0, 1, 3], [100, 80, 40]
        )
        liquidity = np.interp(r["Current Ratio"], [0.5, 1, 2], [40, 70, 100])
        coverage = np.interp(r["DSCR"], [0.8, 1.2, 2], [40, 70, 100])
        profitability = np.mean([
            np.interp(r["ROCE (%)"], [5, 10, 20], [40, 70, 100]),
            np.interp(r["ROE (%)"], [5, 10, 20], [40, 70, 100])
        ])

        fh = (
            0.35 * leverage +
            0.20 * liquidity +
            0.20 * coverage +
            0.15 * profitability +
            0.10 * r["Loan_Type_EWS"]
        )
        return float(np.clip(fh, 0, 100))

    df["FH_Score"] = df.apply(compute_fh, axis=1)

    # ---------------- SELECT COMPANY ----------------
    h = df[df["Company Name"] == company_name].sort_values("FY")
    last = h.iloc[-1]

    score = round(last["FH_Score"], 2)
    sb_code, sb_text, sb_range, risk = sb_band(score)

    return {
        "fh_score": score,
        "sb_code": sb_code,
        "sb_text": sb_text,
        "sb_range": sb_range,
        "risk_band": risk,
        "drivers": [
            ("DSCR", last["DSCR"]),
            ("Debt–Equity", last["Total Debt (₹ Crore)"] / (last["Net Worth (₹ Crore)"] + 1e-6)),
            ("Current Ratio", last["Current Ratio"]),
            ("ROCE", last["ROCE (%)"]),
            ("ROE", last["ROE (%)"]),
        ]
    }
