import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from model.fh_model import run_fh_model


def render_ai_scorecard():

    st.markdown("## 🤖 AI Model Feedback & Scorecard")
    st.divider()

    # ============================================================
    # LOAD DATA FROM /data FOLDER
    # ============================================================
    MASTER_PATH = "data/Indian_Companies_EWS_READY_WITH_FY2025.xlsx"
    INPUT_PATH = "data/2companies.xlsx"

    try:
        df_master = pd.read_excel(MASTER_PATH)
        df_input = pd.read_excel(INPUT_PATH)
    except Exception as e:
        st.error("❌ Failed to load Excel files from /data folder")
        st.exception(e)
        return

    # ============================================================
    # COMPANY SELECTION
    # ============================================================
    if "Company Name" not in df_input.columns:
        st.error("Input file must contain 'Company Name' column")
        return

    companies = df_input["Company Name"].dropna().unique()
    company = st.selectbox("Select Company", companies)

    # ============================================================
    # RUN MODEL
    # ============================================================
    if st.button("▶ Run AI Model"):

        with st.spinner("Running Financial Health Model..."):
            input_df = df_input[df_input["Company Name"] == company]
            result = run_fh_model(df_master, input_df)

        st.success("Model run completed")
        st.divider()

        # ============================================================
        # SCORE CARDS
        # ============================================================
        c1, c2, c3 = st.columns(3)
        c1.metric("FH Score", result["fh_score"])
        c2.metric("SB Band", f"{result['sb_code']} – {result['sb_text']}")
        c3.metric("Risk Band", result["risk_band"])

        st.divider()

        # ============================================================
        # HISTORICAL FH GRAPH
        # ============================================================
        st.markdown("### 📈 Historical Financial Health Trend")

        hist = result["history"]

        fig, ax = plt.subplots()
        ax.plot(hist["FY"], hist["FH_Score"], marker="o")
        ax.set_xlabel("Financial Year")
        ax.set_ylabel("FH Score")
        ax.set_title(f"FH Score Trend – {company}")
        ax.grid(alpha=0.3)

        st.pyplot(fig)

        # ============================================================
        # FORECAST
        # ============================================================
        st.markdown("### 🔮 Next Year Forecast")

        last_year = hist["FY"].max()
        forecast_year = last_year + 1

        fig2, ax2 = plt.subplots()
        ax2.plot(hist["FY"], hist["FH_Score"], marker="o", label="Historical")
        ax2.plot(
            [last_year, forecast_year],
            [hist["FH_Score"].iloc[-1], result["forecast"]],
            linestyle="--",
            marker="s",
            label="Forecast"
        )
        ax2.set_xlabel("Financial Year")
        ax2.set_ylabel("FH Score")
        ax2.set_title(f"FH Forecast – {company}")
        ax2.legend()
        ax2.grid(alpha=0.3)

        st.pyplot(fig2)
