import streamlit as st
import pandas as pd


def render_financial_data():

    st.subheader("📊 Financial Input Section")

    # ---------------- INITIALIZE SESSION STATE ----------------
    if "financials" not in st.session_state:
        st.session_state.financials = {
            "FY 2021": {},
            "FY 2022": {},
            "FY 2023": {},
        }

    # ---------------- FY SELECTION ----------------
    fy = st.radio(
        "Select Financial Year",
        ["FY 2021", "FY 2022", "FY 2023"],
        horizontal=True
    )

    st.markdown(f"### Financial Year: {fy}")

    # Ensure year dict exists
    year_data = st.session_state.financials.setdefault(fy, {})

    # ---------------- LAYOUT ----------------
    left, right = st.columns([2, 1])

    # ---------------- INPUTS ----------------
    with left:
        turnover = st.number_input(
            "Turnover (₹ Cr)", min_value=0.0,
            value=float(year_data.get("turnover", 0.0))
        )
        ebitda = st.number_input(
            "EBITDA (₹ Cr)", min_value=0.0,
            value=float(year_data.get("ebitda", 0.0))
        )
        net_profit = st.number_input(
            "Net Profit (₹ Cr)",
            value=float(year_data.get("net_profit", 0.0))
        )
        net_worth = st.number_input(
            "Net Worth (₹ Cr)", min_value=0.0,
            value=float(year_data.get("net_worth", 0.0))
        )
        total_debt = st.number_input(
            "Total Debt (₹ Cr)", min_value=0.0,
            value=float(year_data.get("total_debt", 0.0))
        )
        dscr = st.number_input(
            "DSCR", min_value=0.0,
            value=float(year_data.get("dscr", 0.0))
        )
        current_ratio = st.number_input(
            "Current Ratio", min_value=0.0,
            value=float(year_data.get("current_ratio", 0.0))
        )

    # Save values
    year_data.update({
        "turnover": turnover,
        "ebitda": ebitda,
        "net_profit": net_profit,
        "net_worth": net_worth,
        "total_debt": total_debt,
        "dscr": dscr,
        "current_ratio": current_ratio,
    })

    # ---------------- CALCULATIONS ----------------
    def safe_div(a, b):
        return round(a / b, 2) if b > 0 else None

    debt_equity = safe_div(total_debt, net_worth)
    ebitda_margin = safe_div(ebitda * 100, turnover)
    net_margin = safe_div(net_profit * 100, turnover)

    # ---------------- SUMMARY ----------------
    with right:
        st.markdown("### Financial Summary")
        st.metric("Turnover", f"₹ {turnover:.2f} Cr")
        st.metric("EBITDA", f"₹ {ebitda:.2f} Cr")
        st.metric("Net Profit", f"₹ {net_profit:.2f} Cr")

        st.markdown("### Key Ratios")
        st.metric("Debt-to-Equity", debt_equity if debt_equity is not None else "N/A")
        st.metric("EBITDA Margin", f"{ebitda_margin}%" if ebitda_margin else "N/A")
        st.metric("Net Profit Margin", f"{net_margin}%" if net_margin else "N/A")

        st.markdown("### Risk Indicators")
        st.write("DSCR:", "🟥 Poor" if dscr < 1 else "🟩 Healthy")
        st.write("Liquidity:", "🟥 Weak" if current_ratio < 1 else "🟩 Adequate")

    # ---------------- 3-YEAR COMPARISON ----------------
    st.markdown("### 3-Year Financial Comparison")

    rows = ["Turnover", "EBITDA", "Net Profit", "Net Worth", "Total Debt"]
    table = {"Particulars": rows}

    for y in ["FY 2021", "FY 2022", "FY 2023"]:
        d = st.session_state.financials.get(y, {})
        table[y] = [
            d.get("turnover", "-"),
            d.get("ebitda", "-"),
            d.get("net_profit", "-"),
            d.get("net_worth", "-"),
            d.get("total_debt", "-"),
        ]

    def cagr(start, end, years=2):
        if not start or not end or start <= 0:
            return "-"
        return f"{((end / start) ** (1 / years) - 1) * 100:.1f}%"

    table["CAGR"] = [
        cagr(
            st.session_state.financials["FY 2021"].get("turnover"),
            st.session_state.financials["FY 2023"].get("turnover"),
        ),
        cagr(
            st.session_state.financials["FY 2021"].get("ebitda"),
            st.session_state.financials["FY 2023"].get("ebitda"),
        ),
        cagr(
            st.session_state.financials["FY 2021"].get("net_profit"),
            st.session_state.financials["FY 2023"].get("net_profit"),
        ),
        "-",
        "-",
    ]

    st.dataframe(pd.DataFrame(table), width="stretch")
