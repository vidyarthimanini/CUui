import streamlit as st
import pandas as pd
import warnings

from model.engine import (
    engineer_dataframe,
    sb_label,
    categorize_score_numeric,
    parse_num
)

warnings.filterwarnings("ignore")

# ============================================================
# CACHE HELPERS
# ============================================================
@st.cache_data(show_spinner=False)
def load_and_engineer_master(path):
    df = pd.read_excel(path, engine="openpyxl", dtype=object)
    return engineer_dataframe(df)

@st.cache_data(show_spinner=False)
def load_input(path):
    return pd.read_excel(path, engine="openpyxl", dtype=object)

# ============================================================
# MAIN UI FUNCTION
# ============================================================
def render_ai_scorecard():

    st.markdown("## 🤖 AI Model Feedback & Scorecard")
    st.divider()

    # ============================================================
    # LOAD DATA FROM /data FOLDER
    # ============================================================
    st.subheader("📂 Data Source")
    st.caption("Data is loaded directly from the GitHub repository")

    MASTER_PATH = "data/Indian_Companies_EWS_READY_WITH_FY2025.xlsx"
    INPUT_PATH  = "data/2companies.xlsx"

    # ---------------- MASTER DATA ----------------
    try:
        with st.spinner("Loading & engineering master dataset..."):
            df_master_eng = load_and_engineer_master(MASTER_PATH)
        st.success(f"✅ Master dataset loaded — {len(df_master_eng)} rows")
        st.session_state["MASTER_ENG"] = df_master_eng
    except Exception as e:
        st.error("❌ Failed to load master dataset from /data folder")
        st.exception(e)
        return

    # ---------------- INPUT DATA ----------------
    try:
        df_input_raw = load_input(INPUT_PATH)
        st.success(f"✅ Input dataset loaded — {len(df_input_raw)} rows")
        st.session_state["INPUT_RAW"] = df_input_raw
    except Exception as e:
        st.error("❌ Failed to load input dataset from /data folder")
        st.exception(e)
        return

    st.divider()

    # ============================================================
    # COMPANY SELECTION
    # ============================================================
    companies = (
        df_input_raw["Company Name"]
        .dropna()
        .astype(str)
        .unique()
    )

    selected_company = st.selectbox(
        "🏢 Select Company",
        companies
    )

    st.session_state["SELECTED_COMPANY"] = selected_company

    # ============================================================
    # RUN MODEL
    # ============================================================
    if st.button("▶ Run AI Model"):

        with st.spinner("Running Financial Health Model..."):

            df_input_eng = engineer_dataframe(df_input_raw)

            row = df_input_eng[
                df_input_eng["Company Name"] == selected_company
            ].iloc[-1]

            fh_score = float(row["FH_Score"])
            sb_code, sb_text, sb_range = sb_label(fh_score)
            risk_band = categorize_score_numeric(fh_score)

            st.session_state["MODEL_RESULT"] = {
                "fh_score": round(fh_score, 2),
                "sb_code": sb_code,
                "sb_text": sb_text,
                "sb_range": sb_range,
                "risk_band": risk_band
            }

        st.success("Model execution completed")

    # ============================================================
    # DISPLAY RESULT
    # ============================================================
    result = st.session_state.get("MODEL_RESULT")

    if result:

        st.divider()
        st.subheader("📊 Result Summary")

        c1, c2, c3 = st.columns(3)
        c1.metric("FH Score", result["fh_score"])
        c2.metric("SB Band", f"{result['sb_code']} – {result['sb_text']}")
        c3.metric("Risk Band", result["risk_band"])

        st.markdown(
            f"""
            <div style="background:#f5f3ff;padding:24px;border-radius:14px;text-align:center">
                <h2 style="color:#4f46e5;margin:0">{result['fh_score']}</h2>
                <p style="margin:0">{result['sb_code']} · {result['sb_text']}</p>
                <small>Range {result['sb_range']}</small>
            </div>
            """,
            unsafe_allow_html=True
        )
