import streamlit as st
from ui_pages.borrower_profile import render_borrower_profile
from ui_pages.documents import render_documents
from ui_pages.financial_data import render_financial_data
from ui_pages.banking_conduct import render_banking_conduct


# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="Corporate Credit Underwriting",
    layout="wide"
)

# -------------------------------------------------
# SIDEBAR NAVIGATION (BUTTON PANE)
# -------------------------------------------------
st.sidebar.title("Home")

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

# Initialize page state
if "page" not in st.session_state:
    st.session_state.page = "Borrower Profile"

# Render navigation buttons
for p in PAGES:
    if st.sidebar.button(p, use_container_width=True):
        st.session_state.page = p

page = st.session_state.page

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
    render_financial_data()

elif page == "Banking Conduct":
    render_banking_conduct()

elif page == "Loan Request":
    st.info("Loan Request page (to be implemented)")

elif page == "Assessment":
    st.info("Assessment page (to be implemented)")

elif page == "Documents":
    render_documents()

elif page == "AI Scorecard":
    st.info("AI Scorecard page (to be implemented)")

elif page == "Tools":
    st.info("Tools page (to be implemented)")
