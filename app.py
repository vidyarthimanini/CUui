import streamlit as st

from pages.borrower_profile import render_borrower_profile
from pages.financial_data import render_financial_data
from pages.banking_conduct import render_banking_conduct
from pages.loan_request import render_loan_request
from pages.assessment import render_assessment
from pages.documents import render_documents
from pages.ai_scorecard import render_ai_scorecard
from pages.tools import render_tools

st.set_page_config(
    page_title="Corporate Credit Underwriting",
    layout="wide"
)

st.sidebar.title("📂 Corporate Credit Underwriting")

PAGES = {
    "Borrower Profile": render_borrower_profile,
    "Financial Data": render_financial_data,
    "Banking Conduct": render_banking_conduct,
    "Loan Request": render_loan_request,
    "Assessment": render_assessment,
    "Documents": render_documents,
    "AI Scorecard": render_ai_scorecard,
    "Tools": render_tools,
}

# ---- Sidebar Navigation (Button-based) ----
if "page" not in st.session_state:
    st.session_state.page = "Borrower Profile"

nav_items = [
    "Borrower Profile",
    "Financial Data",
    "Banking Conduct",
    "Loan Request",
    "Assessment",
    "Documents",
    "AI Scorecard",
    "Tools",
]

for item in nav_items:
    if st.sidebar.button(
        item,
        use_container_width=True,
        key=f"nav_{item}"
    ):
        st.session_state.page = item

page = st.session_state.page

# Header
col1, col2 = st.columns([6, 2])
with col1:
    st.markdown("## Corporate Credit Underwriting")
    st.caption("Comprehensive credit assessment platform")
with col2:
    st.button("💾 Save Application")
    st.button("📤 Submit for Review")

st.divider()

# Render selected page
PAGES[page]()
