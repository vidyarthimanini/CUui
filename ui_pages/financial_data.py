import streamlit as st
import pandas as pd

def render_financial_data():

    st.subheader("📊 Financial Input Section")

    # ---------- INIT SESSION ----------
    if "financials" not in st.session_state:
        st.session_state.financials = {
            "FY 2022": {},
            "FY 2023": {},
            "FY 2024": {},
        }

    # ---------- FY SELECTION ----------
    fy = st.radio(
        "Select Financial Year",
        ["FY 2022", "FY 2023", "FY 2024"],
        horizontal=True
    )

    st.markdown(f"### Financial Year: {fy}")

    data = st.session_state.financials[fy]

    # ---------- LAYOUT ----------
    left, right = st.columns([2, 1])

    # ---------- INPUTS ----------
    with left:
        data["turnover"] = st.number_input(
            "Turnover (₹ Crore)",
            min_value=0.0,
            value=data.get("turnover", 0.0),
            key=f"{fy}_turnover"
        )

        data["ebitda"] = st.number_input(
            "EBITDA (₹ Crore)",
            min_value=0.0,
            value=data.get("ebitda", 0.0),
            key=f"{fy}_ebitda"
        )

        data["net_profit"] = st.number_input(
            "Net Profit (₹ Crore)",
            value=data.get("net_profit", 0.0),
            key=f"{fy}_net_profit"
        )

        data["net_worth"] = st.number_input(
            "Net Worth (₹ Crore)",
            min_value=0.0,
            value=data.get("net_worth", 0.0),
            key=f"{fy}_net_worth"
        )

        data["total_debt"] = st.number_input(
            "Total Debt (₹ Crore)",
            min_value=0.0,
            value=data.get("total_debt", 0.0),
            key=f"{fy}_total_debt"
        )

        data["dscr"] = st.number_input(
            "DSCR",
            min_value=0.0,
            value=data.get("dscr", 0.0),
            key=f"{fy}_dscr"
        )

        data["current_ratio"] = st.number_input(
            "Current Ratio",
            min_value=0.0,
            value=data.get("current_ratio", 0.0),
            key=f"{fy}_current_ratio"
        )
        data["credit_utilization"] = st.number_input(
            "Credit Utilization (%)",
            min_value=0.0,
            max_value=100.0,
            value=data.get("credit_utilization", 0.0),
            key=f"{fy}_credit_utilization"
        )
        
        data["roce"] = st.number_input(
            "ROCE (%)",
            value=data.get("roce", 0.0),
            key=f"{fy}_roce"
        )


    # ---------- CALCULATIONS ----------
    turnover = data["turnover"]
    ebitda = data["ebitda"]
    net_profit = data["net_profit"]
    net_worth = data["net_worth"]
    total_debt = data["total_debt"]
    dscr = data["dscr"]
    current_ratio = data["current_ratio"]

    debt_equity = total_debt / net_worth if net_worth > 0 else None
    ebitda_margin = (ebitda / turnover * 100) if turnover > 0 else None
    net_margin = (net_profit / turnover * 100) if turnover > 0 else None

    # ---------- SUMMARY ----------
    with right:
        st.markdown("### Financial Summary")
        st.metric("Turnover", f"₹ {turnover:.2f} Cr")
        st.metric("EBITDA", f"₹ {ebitda:.2f} Cr")
        st.metric("Net Profit", f"₹ {net_profit:.2f} Cr")

        st.divider()
        st.markdown("### Key Ratios")
        st.metric("Debt-to-Equity", f"{debt_equity:.2f}" if debt_equity else "N/A")
        st.metric("EBITDA Margin", f"{ebitda_margin:.2f}%" if ebitda_margin else "N/A")
        st.metric("Net Profit Margin", f"{net_margin:.2f}%" if net_margin else "N/A")

        st.divider()
        st.markdown("### Risk Indicators")
        st.write("DSCR Status:", "🟥 Poor" if dscr < 1 else "🟩 Healthy")
        st.write("Liquidity:", "🟥 Weak" if current_ratio < 1 else "🟩 Adequate")

    # ---------- CAGR (TURNOVER FY22–FY24) ----------
    st.markdown("### 📈 Growth Indicators (Turnover)")

    def calc_cagr(start, end, years=2):
        if start > 0 and end > 0:
            return ((end / start) ** (1 / years) - 1) * 100
        return None

    fy22 = st.session_state.financials["FY 2022"].get("turnover")
    fy24 = st.session_state.financials["FY 2024"].get("turnover")

    cagr = calc_cagr(fy22, fy24)

    c1, c2 = st.columns(2)
    c1.metric("Turnover CAGR (FY22–FY24)", f"{cagr:.2f}%" if cagr else "N/A")
    c2.metric("Growth Trend", "🟩 Positive" if cagr and cagr > 0 else "🟥 Negative" if cagr else "N/A")

    # ---------- 3-YEAR COMPARISON ----------
    st.markdown("### 3-Year Financial Comparison")

    df = pd.DataFrame({
        "Particulars": ["Turnover", "EBITDA", "Net Profit", "Net Worth", "Total Debt"],
        "FY 2022": [
            st.session_state.financials["FY 2022"].get("turnover", "-"),
            st.session_state.financials["FY 2022"].get("ebitda", "-"),
            st.session_state.financials["FY 2022"].get("net_profit", "-"),
            st.session_state.financials["FY 2022"].get("net_worth", "-"),
            st.session_state.financials["FY 2022"].get("total_debt", "-"),
        ],
        "FY 2023": [
            st.session_state.financials["FY 2023"].get("turnover", "-"),
            st.session_state.financials["FY 2023"].get("ebitda", "-"),
            st.session_state.financials["FY 2023"].get("net_profit", "-"),
            st.session_state.financials["FY 2023"].get("net_worth", "-"),
            st.session_state.financials["FY 2023"].get("total_debt", "-"),
        ],
        "FY 2024": [
            st.session_state.financials["FY 2024"].get("turnover", "-"),
            st.session_state.financials["FY 2024"].get("ebitda", "-"),
            st.session_state.financials["FY 2024"].get("net_profit", "-"),
            st.session_state.financials["FY 2024"].get("net_worth", "-"),
            st.session_state.financials["FY 2024"].get("total_debt", "-"),
        ],
    })

    st.dataframe(df, width="stretch")
     # ---------- NAV BUTTONS ----------
    st.divider()
    nav1, nav2 = st.columns(2)

    with nav1:
        if st.button("⬅ Back to Borrower Profile", width="stretch"):
            st.session_state.page = "Borrower Profile"

    with nav2:
        if st.button("Continue to Banking Conduct ➡️", width="stretch"):
            st.session_state.page = "Banking Conduct"
