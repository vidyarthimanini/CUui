import streamlit as st
import pandas as pd


def render_financial_data():

    st.subheader("📊 Financial Input Section")

    # ---------------- FY SELECTION ----------------
    fy = st.radio(
        "Select Financial Year",
        ["FY 2021", "FY 2022", "FY 2023"],
        horizontal=True
    )

    st.markdown(f"### Financial Year: {fy}")

    # ---------------- LAYOUT ----------------
    left, right = st.columns([2, 1])

    # ================= LEFT: INPUTS =================
    with left:
        turnover = st.number_input("Turnover (₹ Crore)", min_value=0.0)
        ebitda = st.number_input("EBITDA (₹ Crore)", min_value=0.0)
        net_profit = st.number_input("Net Profit (₹ Crore)")
        net_worth = st.number_input("Net Worth (₹ Crore)", min_value=0.0)
        total_debt = st.number_input("Total Debt (₹ Crore)", min_value=0.0)
        dscr = st.number_input("DSCR", min_value=0.0)
        current_ratio = st.number_input("Current Ratio", min_value=0.0)

    # ---------------- AUTO CALCULATIONS ----------------
    debt_equity = total_debt / net_worth if net_worth > 0 else None
    ebitda_margin = (ebitda / turnover * 100) if turnover > 0 else None
    net_profit_margin = (net_profit / turnover * 100) if turnover > 0 else None

    # ================= RIGHT: SUMMARY =================
    with right:
        st.markdown("### Financial Summary")
        st.metric("Turnover", f"₹ {turnover:.2f} Cr")
        st.metric("EBITDA", f"₹ {ebitda:.2f} Cr")
        st.metric("Net Profit", f"₹ {net_profit:.2f} Cr")

        st.markdown("---")
        st.markdown("### Key Ratios")

        st.metric("Debt-to-Equity", f"{debt_equity:.2f}" if debt_equity else "N/A")
        st.metric("EBITDA Margin", f"{ebitda_margin:.2f}%" if ebitda_margin else "N/A")
        st.metric("Net Profit Margin", f"{net_profit_margin:.2f}%" if net_profit_margin else "N/A")

        st.markdown("---")
        st.markdown("### Risk Indicators")
        st.write("DSCR Status:", "🟥 Poor" if dscr < 1 else "🟩 Healthy")
        st.write("Liquidity:", "🟥 Weak" if current_ratio < 1 else "🟩 Adequate")

    # ================= CAGR BOX (SEPARATE) =================
    st.markdown("### 📈 CAGR (Indicative)")

    cagr_col1, cagr_col2, cagr_col3 = st.columns(3)

    def calc_cagr(end, start, years=2):
        if start > 0 and end > 0:
            return ((end / start) ** (1 / years) - 1) * 100
        return None

    # Since no persistence, CAGR only meaningful for FY 2023
    if fy == "FY 2023":
        turnover_cagr = calc_cagr(turnover, turnover)  # placeholder-safe
        ebitda_cagr = calc_cagr(ebitda, ebitda)
        profit_cagr = calc_cagr(net_profit, net_profit)
    else:
        turnover_cagr = ebitda_cagr = profit_cagr = None

    cagr_col1.metric(
        "Turnover CAGR",
        f"{turnover_cagr:.2f}%" if turnover_cagr is not None else "N/A"
    )
    cagr_col2.metric(
        "EBITDA CAGR",
        f"{ebitda_cagr:.2f}%" if ebitda_cagr is not None else "N/A"
    )
    cagr_col3.metric(
        "Profit CAGR",
        f"{profit_cagr:.2f}%" if profit_cagr is not None else "N/A"
    )

    # ================= 3-YEAR COMPARISON =================
    st.markdown("### 3-Year Financial Comparison")

    df = pd.DataFrame({
        "Particulars": [
            "Turnover",
            "EBITDA",
            "Net Profit",
            "Net Worth",
            "Total Debt",
        ],
        "FY 2021": ["-", "-", "-", "-", "-"],
        "FY 2022": ["-", "-", "-", "-", "-"],
        "FY 2023": [
            turnover if fy == "FY 2023" else "-",
            ebitda if fy == "FY 2023" else "-",
            net_profit if fy == "FY 2023" else "-",
            net_worth if fy == "FY 2023" else "-",
            total_debt if fy == "FY 2023" else "-",
        ],
    })

    st.dataframe(df, width="stretch")

    # ================= NAV =================
    c1, c2 = st.columns(2)
    c1.button("⬅ Back to Borrower Profile", width="stretch")
    c2.button("Continue to Banking Conduct ➡️", width="stretch")
