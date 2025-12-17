import streamlit as st
import re
from datetime import date

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

page = st.sidebar.radio("", PAGES)

# -------------------------------------------------
# HEADER
# -------------------------------------------------
col1, col2 = st.columns([6, 2])
with col1:
    st.markdown("## Corporate Credit Underwriting")
    st.caption("Comprehensive credit assessment platform")
with col2:
    st.button("💾 Save Application")
    st.button("📤 Submit for Review")

st.divider()

# =================================================
# BORROWER PROFILE PAGE
# =================================================
if page == "Borrower Profile":

    st.subheader("📁 Borrower Profile")

    # ------------------------------
    # COMPANY INFORMATION
    # ------------------------------
    st.markdown("### Company Information")

    c1, c2 = st.columns(2)
    with c1:
        company_name = st.text_input("Company Name *", placeholder="Enter legal entity name")
        entity_type = st.selectbox(
            "Type of Entity *",
            ["Select entity type", "Pvt Ltd", "LLP", "Partnership", "Proprietorship", "Public Ltd"]
        )
        sector = st.selectbox(
            "Sector *",
            ["Select sector", "Manufacturing", "Trading", "Services", "Infrastructure", "Others"]
        )
    with c2:
        group_name = st.text_input("Group Name (if applicable)", placeholder="Parent company or group")
        cin = st.text_input("CIN Number *", placeholder="Company Identification Number")
        industry = st.text_input("Industry / Sub-sector", placeholder="Specific industry")

    registration_date = st.date_input(
        "Registration Date",
        value=None,
        format="DD-MM-YYYY"
    )

    # ------------------------------
    # MSME CLASSIFICATION
    # ------------------------------
    st.markdown("### MSME Classification")
    is_msme = st.radio("Is this an MSME? *", ["Yes", "No"], horizontal=True)

    # ------------------------------
    # REGISTERED ADDRESS
    # ------------------------------
    st.markdown("### Registered Address")

    address = st.text_area("Address *", placeholder="Complete registered address")

    c3, c4, c5 = st.columns(3)
    with c3:
        city = st.text_input("City *")
    with c4:
        state = st.selectbox(
            "State *",
            ["Select state", "Maharashtra", "Delhi", "Karnataka", "Tamil Nadu", "Gujarat", "Other"]
        )
    with c5:
        pincode = st.text_input("Pincode *", placeholder="6-digit pincode")

    # ------------------------------
    # CONTACT INFORMATION
    # ------------------------------
    st.markdown("### Contact Information")

    c6, c7, c8 = st.columns(3)
    with c6:
        contact_person = st.text_input("Contact Person *", placeholder="Primary contact name")
    with c7:
        email = st.text_input("Email *", placeholder="contact@company.com")
    with c8:
        phone = st.text_input("Phone *", placeholder="+91 XXXXXXXXXX")

    # ------------------------------
    # VALIDATION
    # ------------------------------
    def validate_borrower_profile():
        errors = []

        if not company_name:
            errors.append("Company Name is mandatory")
        if entity_type == "Select entity type":
            errors.append("Type of Entity is mandatory")
        if sector == "Select sector":
            errors.append("Sector is mandatory")
        if not cin or len(cin) < 8:
            errors.append("Invalid CIN Number")
        if not address:
            errors.append("Registered Address is mandatory")
        if not city:
            errors.append("City is mandatory")
        if state == "Select state":
            errors.append("State is mandatory")
        if not re.fullmatch(r"\d{6}", pincode or ""):
            errors.append("Invalid Pincode")
        if not contact_person:
            errors.append("Contact Person is mandatory")
        if not re.fullmatch(r"[^@]+@[^@]+\.[^@]+", email or ""):
            errors.append("Invalid Email")
        if not re.fullmatch(r"\+91\d{10}", phone or ""):
            errors.append("Invalid Phone Number")

        return errors

    st.divider()

    col_btn1, col_btn2 = st.columns([6, 2])

    with col_btn2:
        if st.button("Continue to Financial Data ➡️"):
            errors = validate_borrower_profile()
            if errors:
                st.error("Please fix the following issues:")
                for e in errors:
                    st.write("•", e)
            else:
                st.success("Borrower Profile validated successfully ✔")

# =================================================
# OTHER PAGES (PLACEHOLDERS)
# =================================================
elif page == "Financial Data":
    st.subheader("📊 Financial Data")
    st.info("Financial data input & validation will go here")

elif page == "Banking Conduct":
    st.subheader("🏦 Banking Conduct")
    st.info("Bank statement analysis & conduct rules")

elif page == "Loan Request":
    st.subheader("💼 Loan Request")
    st.info("Loan amount, tenure, purpose")

elif page == "Assessment":
    st.subheader("🧮 Assessment")
    st.info("Credit analyst observations & mitigants")

elif page == "Documents":
    st.subheader("📎 Documents")
    st.file_uploader("Upload Documents", type=["pdf"])

elif page == "AI Scorecard":
    st.subheader("🤖 AI Scorecard")
    st.metric("AI Risk Score", "74 / 100")
    st.progress(0.74)
    st.success("Risk Band: LOW")

elif page == "Tools":
    st.subheader("🧰 Tools")
    st.button("Run Full Validation")
    st.button("Generate Credit Memo")
    st.button("Export Data")
