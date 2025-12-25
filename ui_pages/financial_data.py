import streamlit as st
import pandas as pd

# -------------------------------------------------
# PAGE
# -------------------------------------------------
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

    # ================= LEFT: INPUT FORM =================
    with left:
        turnover = st.number_input("Turnover (₹ Crore) *", min_value=0.0)
        ebitda = st.number_input("EBITDA (₹ Crore) *", min_value=0.0)
        net_profit = st.number_input("Net Profit (₹ Crore) *", min_value=-10000.0)
        net_worth = st.number_input("Net Worth (₹ Crore) *", min_value=0.0)
        total_debt = st.number_input("Total Debt (₹ Crore) *", min_value=0.0)
        dscr = st.number_input("DSCR (Ratio) *", min_value=0.0)
        current_ratio = st.number_input("Current Ratio *", min_value=0.0)
        roce = st.number_input("ROCE (%)", min_value=0.0)
        roe = st.number_input("ROE (%)", min_value=0.0)
        credit_util = st.number_input(
            "Credit Utilization (%) *",
            min_value=0.0,
            max_value=100.0
        )

    # ================= RIGHT: SUMMARY =================
    with right:
        st.markdown("### Financial Summary")
        st.metric("Turnover", f"₹ {turnover:.2f} Cr")
        st.metric("EBITDA", f"₹ {ebitda:.2f} Cr")
        st.metric("Net Profit", f"₹ {net_profit:.2f} Cr")

        st.markdown("---")

        st.markdown("### Key Ratios")
        debt_equity = total_debt / net_worth if net_worth else None
        ebitda_margin = (ebitda / turnover * 100) if turnover else None
        net_margin = (net_profit / turnover * 100) if turnover else None

        st.write(f"**Debt-to-Equity:** {debt_equity:.2f}" if debt_equity else "Debt-to-Equity: N/A")
        st.write(f"**EBITDA Margin:** {ebitda_margin:.2f}%" if ebitda_margin else "EBITDA Margin: N/A")
        st.write(f"**Net Profit Margin:** {net_margin:.2f}%" if net_margin else "Net Profit Margin: N/A")

        st.markdown("---")

        st.markdown("### Risk Indicators")
        st.write("**DSCR Status:**", "🟥 Poor" if dscr < 1 else "🟩 Healthy")
        st.write("**Liquidity:**", "🟥 Weak" if current_ratio < 1 else "🟩 Adequate")

    # ================= SNAPSHOT TABLE =================
    st.markdown("### Financial Snapshot")

    data = {
        "Metric": [
            "Turnover",
            "EBITDA",
            "Net Profit",
            "Net Worth",
            "Total Debt",
            "DSCR",
            "Current Ratio",
        ],
        fy: [
            turnover,
            ebitda,
            net_profit,
            net_worth,
            total_debt,
            dscr,
            current_ratio,
        ],
    }

    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True)

    # ================= NAVIGATION =================
    c1, c2 = st.columns(2)
    c1.button("⬅ Back to Borrower Profile", use_container_width=True)
    c2.button("Continue to Banking Conduct ➡️", use_container_width=True)
