import streamlit as st
import pandas as pd
import numpy as np
import io
import warnings

from model.engine import (
    engineer_dataframe,
    sb_label,
    categorize_score_numeric,
    parse_num
)

warnings.filterwarnings("ignore")


def render_ai_scorecard():

    st.markdown("## 🤖 AI Model Feedback & Scorecard")
    st.divider()

    # ============================================================
    #   LOAD DATA DIRECTLY FROM /data FOLDER (GITHUB)
    # ============================================================
    st.subheader("📂 Data Source")
    st.caption("Data is loaded directly from the GitHub repository")

    MASTER_PATH = "data/Indian_Companies_EWS_READY_WITH_FY2025.xlsx"
    INPUT_PATH  = "data/2companies.xlsx"

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
        return   # ✅ LEGAL NOW

    # ---------------- INPUT DATA ----------------
    try:
        df_input_raw = pd.read_excel(INPUT_PATH, engine="openpyxl", dtype=object)
        st.success(f"✅ Input dataset loaded — {len(df_input_raw)} rows")

        st.session_state["INPUT_RAW"] = df_input_raw

    except Exception as e:
        st.error("❌ Failed to load input_data.xlsx from /data folder")
        st.exception(e)
        return   # ✅ LEGAL NOW

    st.divider()

    # ============================================================
    #   SELECT COMPANY
    # ============================================================
    companies = df_input_raw["Company Name"].dropna().unique()

    company = st.selectbox(
        "Select Company",
        companies
    )

    if st.button("▶ Run AI Model"):
        st.success("Model logic will run here next")

        # TEMP: show formula FH score
        row = df_input_raw[df_input_raw["Company Name"] == company].iloc[-1]
        fh_score = row.get("FH_Score", np.nan)

        sb_code, sb_text, _ = sb_label(fh_score)
        risk_band = categorize_score_numeric(fh_score)

        st.subheader("📊 Result")

        c1, c2, c3 = st.columns(3)
        c1.metric("FH Score", f"{fh_score:.2f}")
        c2.metric("SB Band", f"{sb_code} – {sb_text}")
        c3.metric("Risk Band", risk_band)
