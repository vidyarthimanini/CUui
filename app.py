import streamlit as st
from ui_pages.borrower_profile import render_borrower_profile
from ui_pages.documents import render_documents

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="Corporate Credit Underwriting",
    layout="wide"
)

# -------------------------------------------------
# SIDEBAR CSS (CRITICAL)
# -------------------------------------------------
st.markdown(
    """
    <style>
    section[data-testid="stSidebar"] {
        background-color: #f8fafc;
    }
    .nav-item {
        padding: 10px 14px;
        margin: 4px 0;
        border-radius: 8px;
        font-size: 14px;
        color: #334155;
        cursor: pointer;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .nav-item:hover {
        background-color: #e5e7eb;
    }
    .nav-active {
        background-color: #e0e7ff;
        color: #1d4ed8;
        font-weight: 600;
        border-left: 4px solid #2563eb;
        padding-left: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# -------------------------------------------------
# NAV CONFIG
# -------------------------------------------------
NAV_ITEMS = [
    ("Borrower Profile"),
    ("Financial Data"),
    ("Banking Conduct"),
    ("Loan Request"),
    ("Assessment"),
    ("Documents"),
    ("AI Scorecard"),
    ("Tools"),
]

if "page" not in st.session_state:
    st.session_state.page = "Borrower Profile"

# -------------------------------------------------
# SIDEBAR RENDER
# -------------------------------------------------
st.sidebar.markdown("### Corporate Credit Underwriting")

for label, icon in NAV_ITEMS:
    active = st.session_state.page == label
    css_class = "nav-item nav-active" if active else "nav-item"

    if st.sidebar.button(
        f"{icon}  {label}",
        key=f"nav_{label}",
        use_container_width=True
    ):
        st.session_state.page = label

# -------------------------------------------------
# HEADER
# -------------------------------------------------
st.markdown("## Corporate Credit Underwriting")
st.caption("Comprehensive credit assessment platform")
st.divider()

# -------------------------------------------------
# ROUTING
# -------------------------------------------------
page = st.session_state.page

if page == "Borrower Profile":
    render_borrower_profile()

elif page == "Documents":
    render_documents()

else:
    st.info(f"{page} page coming soon.")
