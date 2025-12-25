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

        st.divider()
        st.markdown("### Key Ratios")

        st.metric("Debt-to-Equity", f"{debt_equity:.2f}" if debt_equity else "N/A")
        st.metric("EBITDA Margin", f"{ebitda_margin:.2f}%" if ebitda_margin else "N/A")
        st.metric("Net Profit Margin", f"{net_profit_margin:.2f}%" if net_profit_margin else "N/A")

        st.divider()
        st.markdown("### Risk Indicators")
        st.write("DSCR Status:", "🟥 Poor" if dscr < 1 else "🟩 Healthy")
        st.write("Liquidity:", "🟥 Weak" if current_ratio < 1 else "🟩 Adequate")

    # ================= CAGR BOX (PLACEHOLDER, SAFE) =================
    st.markdown("### 📈 CAGR (Indicative)")

    c1, c2, c3 = st.columns(3)
    c1.metric("Turnover CAGR", "N/A")
    c2.metric("EBITDA CAGR", "N/A")
    c3.metric("Profit CAGR", "N/A")

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

    st.dataframe(df, use_container_width=True)

    # ================= NAV =================
    b1, b2 = st.columns(2)
    b1.button("⬅ Back to Borrower Profile", use_container_width=True)
    b2.button("Continue to Banking Conduct ➡️", use_container_width=True)
