import streamlit as st

# -------------------------------------------------
# DOCUMENT DEFINITIONS
# -------------------------------------------------
DOCUMENT_SECTIONS = {
    "KYC Documents": [
        ("PAN", True),
        ("Aadhaar", True),
    ],
    "Financial Documents": [
        ("Audited Financial Statements", True),
        ("Provisional Financial Statements", False),
        ("Management Accounts", False),
        ("Cash Flow Statements", True),
    ],
    "Tax & Compliance": [
        ("GST Returns", True),
        ("Income Tax Returns", True),
        ("TDS Certificates", False),
        ("Tax Audit Reports", False),
    ],
    "Banking Documents": [
        ("Bank Statements", True),
        ("Credit Bureau Reports", True),
        ("CRILC Confirmation Letter", True),
        ("Existing Loan Sanction Letters", False),
        ("NOC from Existing Lenders", False),
    ],
    "Legal Documents": [
        ("Certificate of Incorporation", True),
        ("MOA & AOA", True),
        ("Board Resolutions", True),
        ("Power of Attorney", False),
        ("Directors KYC Documents", True),
    ],
}

ALLOWED_TYPES = ["pdf", "docx", "xlsx"]
MAX_SIZE_MB = 25


def render_documents():

    st.subheader("📄 Document Upload")
    st.caption("Upload required documents to proceed")

    # -------------------------------------------------
    # INIT SESSION
    # -------------------------------------------------
    if "data" not in st.session_state:
        st.session_state.data = {}

    if "documents" not in st.session_state.data:
        st.session_state.data["documents"] = {}

    docs_state = st.session_state.data["documents"]

    uploaded_required = 0
    total_required = 0

    # -------------------------------------------------
    # DOCUMENT SECTIONS
    # -------------------------------------------------
    for section, docs in DOCUMENT_SECTIONS.items():
        st.markdown(f"### {section}")
        cols = st.columns(2)

        for idx, (doc_name, required) in enumerate(docs):
            col = cols[idx % 2]

            with col:
                key = f"{section}_{doc_name}"

                uploaded_file = st.file_uploader(
                    f"{doc_name} {'*' if required else '(Optional)'}",
                    type=ALLOWED_TYPES,
                    key=key
                )

                # required count
                if required:
                    total_required += 1

                if uploaded_file:
                    size_mb = uploaded_file.size / (1024 * 1024)

                    if size_mb > MAX_SIZE_MB:
                        st.error("❌ File exceeds 25MB")
                        docs_state[doc_name] = False
                    else:
                        st.success("✅ Uploaded")
                        docs_state[doc_name] = True
                        if required:
                            uploaded_required += 1
                else:
                    docs_state.setdefault(doc_name, False)

        st.divider()

    # -------------------------------------------------
    # PROGRESS
    # -------------------------------------------------
    st.markdown("### 📊 Upload Progress")

    progress = uploaded_required / max(total_required, 1)
    st.progress(progress)

    st.write(f"**Uploaded Required:** {uploaded_required}")
    st.write(f"**Total Required:** {total_required}")

    # -------------------------------------------------
    # NAVIGATION
    # -------------------------------------------------
    st.divider()
    c1, c2 = st.columns(2)

    with c1:
        if st.button("⬅ Back to Assessment", use_container_width=True):
            st.session_state.page = "Assessment"

    with c2:
        if st.button("Continue to AI Scorecard ➡️", use_container_width=True):
            st.session_state.page = "AI Scorecard"
