import streamlit as st
import pandas as pd

def render_financial_data():

    st.subheader("📊 Financial Input Section")

    # ---------------- FY SELECTION MODE ----------------
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

    st.markdown(f"### Financial Year: {fy}")

    # ---------------- LAYOUT ----------------
    left, right = st.columns([2, 1])

    # ================= LEFT: INPUTS =================
    with left:
        turnover = st.number_input("Turnover (₹ Crore) *", min_value=0.0)
        ebitda = st.number_input("EBITDA (₹ Crore) *", min_value=0.0)
        net_profit = st.number_input("Net Profit (₹ Crore) *", min_value=-10000.0)
        net_worth = st.number_input("Net Worth (₹ Crore) *", min_value=0.0)
        total_debt = st.number_input("Total Debt (₹ Crore) *", min_value=0.0)
        dscr = st.number_input("DSCR (Ratio) *", min_value=0.0)
        current_ratio = st.number_input("Current Ratio *", min_value=0.0)
        roce = st.number_input("ROCE (%)", min_value=0.0)
        credit_utilization = st.number_input(
            "Credit Utilization (%)",
            min_value=0.0,
            max_value=100.0
        )

    # ---------------- AUTO CALCULATIONS ----------------
    debt_equity = None
    ebitda_margin = None
    net_profit_margin = None

    if net_worth > 0:
        debt_equity = total_debt / net_worth

    if turnover > 0:
        ebitda_margin = (ebitda / turnover) * 100
        net_profit_margin = (net_profit / turnover) * 100

    # ================= RIGHT: AUTO-FILLED =================
    with right:
        st.markdown("### Financial Summary")
        st.metric("Turnover", f"₹ {turnover:.2f} Cr")
        st.metric("EBITDA", f"₹ {ebitda:.2f} Cr")
        st.metric("Net Profit", f"₹ {net_profit:.2f} Cr")

        st.markdown("---")
        st.markdown("### Key Ratios")

        st.metric(
            "Debt-to-Equity",
            f"{debt_equity:.2f}" if debt_equity is not None else "N/A"
        )

        st.metric(
            "EBITDA Margin",
            f"{ebitda_margin:.2f}%" if ebitda_margin is not None else "N/A"
        )

        st.metric(
            "Net Profit Margin",
            f"{net_profit_margin:.2f}%" if net_profit_margin is not None else "N/A"
        )

        st.markdown("---")
        st.markdown("### Risk Indicators")
        st.write("**DSCR Status:**", "🟥 Poor" if dscr < 1 else "🟩 Healthy")
        st.write("**Liquidity:**", "🟥 Weak" if current_ratio < 1 else "🟩 Adequate")

    # ================= SNAPSHOT TABLE =================
    st.markdown("### 3-Year Financial Comparison")

    df = pd.DataFrame({
        "Metric": [
            "Turnover",
            "EBITDA",
            "Net Profit",
            "Net Worth",
            "Total Debt",
            "Debt-to-Equity",
            "EBITDA Margin (%)",
            "Net Profit Margin (%)",
        ],
        fy: [
            turnover,
            ebitda,
            net_profit,
            net_worth,
            total_debt,
            round(debt_equity, 2) if debt_equity else None,
            round(ebitda_margin, 2) if ebitda_margin else None,
            round(net_profit_margin, 2) if net_profit_margin else None,
        ],
    })

    st.dataframe(df, use_container_width=True)

    # ================= NAV =================
    c1, c2 = st.columns(2)
    c1.button("⬅ Back to Borrower Profile", use_container_width=True)
    c2.button("Continue to Banking Conduct ➡️", use_container_width=True)
