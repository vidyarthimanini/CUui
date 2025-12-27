import streamlit as st
import pandas as pd
from model.run_model import run_model


def render_ai_scorecard():

    st.markdown("## 🤖 AI Model Feedback & Scorecard")
    st.divider()

    # -----------------------------------
    # RUN MODEL SECTION
    # -----------------------------------
    st.subheader("📂 Run Model")

# ============================================================
#   LOAD DATA DIRECTLY FROM GITHUB /data FOLDER
# ============================================================

st.subheader("📂 Data Source")
st.caption("Data is loaded directly from the GitHub repository")

MASTER_PATH = "data/master_data.xlsx"
INPUT_PATH  = "data/input_data.xlsx"

# ---------------- MASTER DATA ----------------
try:
    df_master_raw = pd.read_excel(MASTER_PATH, engine="openpyxl", dtype=object)
    st.success(f"✅ Master dataset loaded — {len(df_master_raw)} rows")

    with st.spinner("Engineering master dataset..."):
        df_master_eng = engineer_dataframe(df_master_raw)

    st.session_state["MASTER_ENG"] = df_master_eng

except Exception as e:
    st.error("❌ Failed to load master_data.xlsx from /data folder")
    st.exception(e)
    st.stop()

# ---------------- INPUT DATA ----------------
try:
    df_input_raw = pd.read_excel(INPUT_PATH, engine="openpyxl", dtype=object)
    st.success(f"✅ Input dataset loaded — {len(df_input_raw)} rows")

    st.session_state["INPUT_RAW"] = df_input_raw

except Exception as e:
    st.error("❌ Failed to load input_data.xlsx from /data folder")
    st.exception(e)
    st.stop()


    if uploaded:
        df_tmp = pd.read_excel(uploaded)

        if "Company Name" not in df_tmp.columns:
            st.error("Excel must contain a 'Company Name' column")
            return

        companies = df_tmp["Company Name"].dropna().unique()

        company = st.selectbox(
            "Select Company",
            companies
        )

        if st.button("▶ Run AI Model"):
            with st.spinner("Running Financial Health Model..."):
                result = run_model(uploaded, company)
                st.session_state["MODEL_RESULT"] = result
                st.success("Model run completed")

    st.divider()

    # -----------------------------------
    # DISPLAY RESULTS
    # -----------------------------------
    res = st.session_state.get("MODEL_RESULT")

    if res:
        st.subheader("📊 Result")

        c1, c2, c3 = st.columns(3)

        c1.metric("FH Score", f"{res['fh_score']}")
        c2.metric("SB Band", f"{res['sb_code']} – {res['sb_text']}")
        c3.metric("Risk Band", res["risk_band"])

        st.divider()

        st.markdown("### 🔍 Key Drivers")

        for name, val in res["drivers"]:
            st.write(f"- **{name}** : {val:.2f}")
