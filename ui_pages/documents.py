import streamlit as st

# -------------------------------------------------
# DOCUMENT DEFINITIONS
# -------------------------------------------------

DOCUMENT_SECTIONS = {
    "Financial Documents": [
        ("Audited Financial Statements (Last 3 Years)", True),
        ("Provisional Financial Statements (Current Year)", False),
        ("Management Accounts", False),
        ("Cash Flow Statements", True),
    ],
    "Tax & Compliance": [
        ("GST Returns (Last 12 Months)", True),
        ("Income Tax Returns (Last 3 Years)", True),
        ("TDS Certificates", False),
        ("Tax Audit Reports", False),
    ],
    "Banking Documents": [
        ("Bank Statements (Last 12 Months)", True),
        ("CIBIL / Credit Bureau Reports", True),
        ("CRILC Confirmation Letters", True),
        ("Existing Loan Sanction Letters", False),
        ("NOC from Existing Lenders", False),
    ],
    "Legal & KYC Documents": [
        ("Certificate of Incorporation", True),
        ("MOA & AOA", True),
        ("Board Resolutions", True),
        ("Power of Attorney", False),
        ("Partnership Deed (if applicable)", False),
        ("Directors KYC Documents", True),
    ],
    " KYC Documents": [
        ("PAN", True),
        ("Aadhar", True),
    ],
    "Operational Documents": [
        ("Stock & Inventory Statements", False),
        ("Debtors & Creditors Aging", False),
        ("Insurance Policies", False),
        ("Property Documents (if mortgaged)", False),
        ("Valuation Reports", False),
    ],
    "Project Documents": [
        ("Project Feasibility Report", False),
        ("Technical Feasibility Study", False),
        ("Market Research Reports", False),
        ("Environmental Clearances", False),
        ("Regulatory Approvals", False),
    ],
}

ALLOWED_TYPES = ["pdf", "docx", "xlsx"]
MAX_SIZE_MB = 25


# -------------------------------------------------
# PAGE RENDER
# -------------------------------------------------

def render_documents():

    st.subheader("📄 Document Upload")
    st.caption("Upload required documents to proceed with assessment")

    uploaded_count = 0
    required_count = 0

    for section, docs in DOCUMENT_SECTIONS.items():
        st.markdown(f"### {section}")

        cols = st.columns(2)

        for idx, (doc_name, required) in enumerate(docs):
            col = cols[idx % 2]

            with col:
                label = f"{doc_name} {'*' if required else '(Optional)'}"

                uploaded_file = st.file_uploader(
                    label,
                    type=ALLOWED_TYPES,
                    key=f"{section}_{doc_name}",
                    help="PDF, DOCX, XLSX | Max 25MB"
                )

                if required:
                    required_count += 1

                if uploaded_file:
                    uploaded_count += 1
                    size_mb = uploaded_file.size / (1024 * 1024)

                    if size_mb > MAX_SIZE_MB:
                        st.error("❌ File exceeds 25MB")
                    else:
                        st.success("✅ Uploaded")

        st.divider()

    # -------------------------------------------------
    # FOOTER SUMMARY
    # -------------------------------------------------
    st.markdown("### 📊 Upload Progress")

    st.progress(uploaded_count / max(required_count, 1))

    st.write(f"**Uploaded:** {uploaded_count}")
    st.write(f"**Required:** {required_count}")

    st.divider()

    c1, c2 = st.columns(2)
    c1.button("⬅ Back to Assessment", use_container_width=True)
    c2.button("Continue to AI Scorecard ➡️", use_container_width=True)
