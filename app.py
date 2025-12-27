import streamlit as st
from ui_pages.borrower_profile import render_borrower_profile
from ui_pages.documents import render_documents
from ui_pages.financial_data import render_financial_data
from ui_pages.banking_conduct import render_banking_conduct
from ui_pages.loan_request import render_loan_request
from ui_pages.assessment import render_assessment
from ui_pages.ai_scorecard import render_ai_scorecard
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
    render_loan_request()
    
elif page == "Assessment":
    render_assessment()
    
elif page == "Documents":
    render_documents()

elif page == "AI Scorecard":
    render_ai_scorecard()
elif page == "Tools":
    st.info("Tools page (to be implemented)")
