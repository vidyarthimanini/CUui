import streamlit as st
import pandas as pd

def render_financial_data():

    st.subheader("📊 Financial Input Section")

    # ---------- INIT STATE ----------
    if "financials" not in st.session_state:
        st.session_state.financials = {}

    # ---------- FY SELECTION MODE ----------
    fy_mode = st.radio(
        "Financial Year Selection",
        ["Select from list (Recommended)", "Enter custom financial year"],
        horizontal=True
    )

    if fy_mode == "Select from list (Recommended)":
        fy = st.radio(
            " ",
            ["FY 2021", "FY 2022", "FY 2023"],
            horizontal=True,
            label_visibility="collapsed"
        )
    else:
        fy = st.text_input(
            "Enter Financial Year",
            placeholder="e.g. FY 2020-21 or FY 2024"
        )
        st.warning(
            "⚠ Custom FY is outside the model training window. "
            "Risk scores may be indicative only."
        )

    if not fy:
        st.stop()

    st.markdown(f"### Financial Year: {fy}")

    if fy not in st.session_state.financials:
        st.session_state.financials[fy] = {}

    data = st.session_state.financials[fy]

    # ---------- LAYOUT ----------
    left, right = st.columns([2, 1])

    # ---------- INPUTS ----------
    with left:
        data["turnover"] = st.number_input("Turnover (₹ Cr)", 0.0, value=data.get("turnover", 0.0))
        data["ebitda"] = st.number_input("EBITDA (₹ Cr)", 0.0, value=data.get("ebitda", 0.0))
        data["net_profit"] = st.number_input("Net Profit (₹ Cr)", value=data.get("net_profit", 0.0))
        data["net_worth"] = st.number_input("Net Worth (₹ Cr)", 0.0, value=data.get("net_worth", 0.0))
        data["total_debt"] = st.number_input("Total Debt (₹ Cr)", 0.0, value=data.get("total_debt", 0.0))
        data["dscr"] = st.number_input("DSCR", 0.0, value=data.get("dscr", 0.0))
        data["current_ratio"] = st.number_input("Current Ratio", 0.0, value=data.get("current_ratio", 0.0))

    # ---------- CALCULATIONS ----------
    def safe_div(a, b):
        return round(a / b, 2) if b else None

    debt_equity = safe_div(data["total_debt"], data["net_worth"])
    ebitda_margin = safe_div(data["ebitda"] * 100, data["turnover"])
    net_margin = safe_div(data["net_profit"] * 100, data["turnover"])

    # ---------- SUMMARY ----------
    with right:
        st.markdown("### Financial Summary")
        st.metric("Turnover", f"₹ {data['turnover']:.2f} Cr")
        st.metric("EBITDA", f"₹ {data['ebitda']:.2f} Cr")
        st.metric("Net Profit", f"₹ {data['net_profit']:.2f} Cr")

        st.markdown("### Key Ratios")
        st.metric("Debt-to-Equity", debt_equity if debt_equity is not None else "N/A")
        st.metric("EBITDA Margin", f"{ebitda_margin}%" if ebitda_margin else "N/A")
        st.metric("Net Profit Margin", f"{net_margin}%" if net_margin else "N/A")

    # ---------- 3-YEAR COMPARISON ----------
    st.markdown("### 3-Year Financial Comparison")

    base_years = ["FY 2021", "FY 2022", "FY 2023"]
    rows = ["Turnover", "EBITDA", "Net Profit", "Net Worth", "Total Debt"]

    table = {"Particulars": rows}

    for y in base_years:
        fy_data = st.session_state.financials.get(y, {})
        table[y] = [
            fy_data.get("turnover", "-"),
            fy_data.get("ebitda", "-"),
            fy_data.get("net_profit", "-"),
            fy_data.get("net_worth", "-"),
            fy_data.get("total_debt", "-"),
        ]

    def cagr(start, end, n=2):
        if not start or not end:
            return "-"
        return f"{((end / start) ** (1 / n) - 1) * 100:.1f}%"

    table["CAGR"] = [
        cagr(
            st.session_state.financials.get("FY 2021", {}).get("turnover"),
            st.session_state.financials.get("FY 2023", {}).get("turnover")
        ),
        cagr(
            st.session_state.financials.get("FY 2021", {}).get("ebitda"),
            st.session_state.financials.get("FY 2023", {}).get("ebitda")
        ),
        cagr(
            st.session_state.financials.get("FY 2021", {}).get("net_profit"),
            st.session_state.financials.get("FY 2023", {}).get("net_profit")
        ),
        "-",
        "-",
    ]

    st.dataframe(pd.DataFrame(table), use_container_width=True)
