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
# CUSTOM SIDEBAR STYLING
# -------------------------------------------------
st.markdown(
    """
    <style>
    .sidebar-nav button {
        background: transparent;
        border: none;
        padding: 10px 14px;
        width: 100%;
        text-align: left;
        font-size: 14px;
        border-radius: 8px;
        margin-bottom: 4px;
        color: #334155;
        cursor: pointer;
    }
    .sidebar-nav button:hover {
        background-color: #eef2ff;
    }
    .sidebar-active {
        background-color: #e0e7ff !important;
        color: #1d4ed8 !important;
        font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# -------------------------------------------------
# SIDEBAR NAVIGATION
# -------------------------------------------------
st.sidebar.markdown("## 🏠 Home")

NAV_ITEMS = [
    ("Borrower Profile", "📄"),
    ("Financial Data", "📊"),
    ("Banking Conduct", "🏦"),
    ("Loan Request", "💰"),
    ("Assessment", "🧠"),
    ("Documents", "📎"),
    ("AI Scorecard", "🤖"),
    ("Tools", "🛠️"),
]

# Initialize page state
if "page" not in st.session_state:
    st.session_state.page = "Borrower Profile"

st.sidebar.markdown('<div class="sidebar-nav">', unsafe_allow_html=True)

for label, icon in NAV_ITEMS:
    is_active = st.session_state.page == label
    btn_class = "sidebar-active" if is_active else ""

    clicked = st.sidebar.button(
        f"{icon}  {label}",
        key=f"nav_{label}",
        use_container_width=True
    )

    if clicked:
        st.session_state.page = label

st.sidebar.markdown("</div>", unsafe_allow_html=True)

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
    st.info("Financial Data page (to be implemented)")

elif page == "Banking Conduct":
    st.info("Banking Conduct page (to be implemented)")

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
