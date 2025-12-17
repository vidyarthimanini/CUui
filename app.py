import streamlit as st

from pages.borrower_profile import render_borrower_profile


# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="Corporate Credit Underwriting",
    layout="wide"
)

# -------------------------------------------------
# SIDEBAR NAVIGATION
# -------------------------------------------------
st.sidebar.title("📂 Corporate Credit Underwriting")

PAGES = [
    "Borrower Profile",
    "Financial Data",
    "Banking Conduct",
    "Loan Request",
    "Assessment",
    "Documents",
    "AI Scorecard",
    "Tools"
]

page = st.sidebar.button(
    "Navigate",
    PAGES
)

# -------------------------------------------------
# HEADER
# -------------------------------------------------
st.markdown("## Corporate Credit Underwriting")
st.caption("Comprehensive credit assessment platform")
st.divider()

# -------------------------------------------------
# PAGE ROUTING
# -------------------------------------------------
if page == "Borrower Profile":
    render_borrower_profile()

elif page == "Financial Data":
    st.info("Financial Data page (to be implemented)")

elif page == "Banking Conduct":
    st.info("Banking Conduct page (to be implemented)")

elif page == "Loan Request":
    st.info("Loan Request page (to be implemented)")

elif page == "Assessment":
    st.info("Assessment page (to be implemented)")

elif page == "Documents":
    st.info("Documents page (to be implemented)")

elif page == "AI Scorecard":
    st.info("AI Scorecard page (to be implemented)")

elif page == "Tools":
    st.info("Tools page (to be implemented)")
