import streamlit as st
import pandas as pd
import numpy as np
import io
import plotly.graph_objects as go

from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="Corporate Credit Underwriting",
    layout="wide"
)

st.title("📊 Corporate Credit Risk Assessment Platform")

# ============================================================
# FILE UPLOAD (DYNAMIC)
# ============================================================
uploaded_file = st.file_uploader(
    "📥 Upload Excel File (2 Company Profiles)",
    type=["xlsx"]
)

if uploaded_file is None:
    st.info("Upload an Excel file to begin.")
    st.stop()

# ============================================================
# BACKEND ENGINE (UNCHANGED LOGIC)
# ============================================================
@st.cache_data
def load_and_engineer_data(uploaded):

    df = pd.read_excel(uploaded)
    df.columns = [c.strip() for c in df.columns]

    df["FY"] = pd.to_numeric(df["FY"], errors="coerce")
    df = df.dropna(subset=["Company Name", "FY"])

    def num(x):
        try:
            return float(str(x).replace(",", "").replace("₹", ""))
        except:
            return np.nan

    num_cols = [
        "Turnover (₹ Crore)","EBITDA (₹ Crore)","Net Profit (₹ Crore)",
        "Net Worth (₹ Crore)","Total Debt (₹ Crore)",
        "DSCR","Current Ratio","ROCE (%)","ROE (%)",
        "Credit Utilization (%)","Loan Amount","Collateral Value",
        "LTV Ratio","Maximum DPD Observed"
    ]

    for c in num_cols:
        if c in df.columns:
            df[c] = df[c].apply(num)

    doc_cols = [c for c in df.columns if c.endswith("Uploaded")]
    df["Document_Score"] = (
        df[doc_cols].astype(str)
        .apply(lambda x: x.str.lower().str.contains("yes|true|uploaded"))
        .mean(axis=1) * 100
    )

    def score_behavior(v, good, mid, bad):
        try: v = float(v)
        except: v = mid
        if v <= good: return 100
        if v <= mid: return 70
        if v <= bad: return 40
        return 20

    def loan_ews(row):
        loan = str(row.get("Loan Type","")).upper()
        wc = np.mean([
            score_behavior(row.get("Credit Utilization (%)",90),70,90,110),
            score_behavior(row.get("Bounced Cheques (Count)",0),0,1,2),
            score_behavior(row.get("Overdrafts (Count)",0),0,1,2)
        ])
        tl = np.mean([
            score_behavior(row.get("LTV Ratio",70),60,70,80),
            score_behavior(row.get("Tenure (Months)",60),36,60,84)
        ])
        return wc if loan=="WORKING CAPITAL" else tl

    df["Loan_Type_EWS"] = df.apply(loan_ews, axis=1)

    def scale(v, d, r):
        if pd.isna(v): v = d[1]
        return np.clip(np.interp(v, d, r), min(r), max(r))

    def compute_fh(r):
        leverage = scale(
            r["Total Debt (₹ Crore)"]/(r["Net Worth (₹ Crore)"]+1e-6),
            [0,1,3],[100,80,40]
        )
        liquidity = scale(r["Current Ratio"],[0.5,1,2],[40,70,100])
        coverage = scale(r["DSCR"],[0.8,1.2,2],[40,70,100])
        profitability = np.mean([
            scale(r["ROCE (%)"],[5,10,20],[40,70,100]),
            scale(r["ROE (%)"],[5,10,20],[40,70,100])
        ])

        return np.clip(
            0.35*leverage +
            0.20*liquidity +
            0.20*coverage +
            0.15*profitability +
            0.10*r["Loan_Type_EWS"],
            0,100
        )

    df["FH_Score"] = df.apply(compute_fh, axis=1)

    df = df.sort_values(["Company Name","FY"])
    df["EBITDA_Margin"] = df["EBITDA (₹ Crore)"]/(df["Turnover (₹ Crore)"]+1e-6)
    df["Growth_1Y"] = df.groupby("Company Name")["Turnover (₹ Crore)"].pct_change()
    df["Trend_Slope"] = df.groupby("Company Name")["FH_Score"].transform(
        lambda x: np.polyfit(range(len(x)),x,1)[0] if len(x)>1 else 0
    )

    return df


df = load_and_engineer_data(uploaded_file)

# ============================================================
# TRAIN MODEL ON BOTH COMPANIES
# ============================================================
FEATURES = [
    "FH_Score","Trend_Slope","Growth_1Y",
    "EBITDA_Margin","Loan_Type_EWS","Document_Score"
]

df["FH_Next"] = df.groupby("Company Name")["FH_Score"].shift(-1)
train = df.dropna(subset=["FH_Next"])

pipe = Pipeline([
    ("imp", SimpleImputer(strategy="median")),
    ("model", Ridge(alpha=1.2))
])

pipe.fit(train[FEATURES], train["FH_Next"])

means = train[FEATURES].mean()
stds = train[FEATURES].std().replace(0,1)

# ============================================================
# COMPANY DROPDOWNS (DYNAMIC)
# ============================================================
companies = sorted(df["Company Name"].unique())

colA, colB = st.columns(2)
with colA:
    company_a = st.selectbox("Select Company A", companies, key="A")
with colB:
    company_b = st.selectbox("Select Company B", companies, index=1, key="B")

# ============================================================
# DASHBOARD RENDER FUNCTION
# ============================================================
def render_company(company):

    row = df[df["Company Name"]==company].iloc[-1]
    X = row[FEATURES]
    fh_ml = pipe.predict(pd.DataFrame([X]))[0]

    coef = pipe.named_steps["model"].coef_
    z = (X - means) / stds
    impacts = z * coef

    shap_df = pd.DataFrame({
        "Feature": FEATURES,
        "Impact": impacts.values
    })

    return row, fh_ml, shap_df

# ============================================================
# SIDE-BY-SIDE DASHBOARD
# ============================================================
st.markdown("## 🏢 Company Comparison Dashboard")

left, right = st.columns(2)

with left:
    row_a, fh_a, shap_a = render_company(company_a)
    st.subheader(company_a)
    st.metric("FH Score (Formula)", f"{row_a['FH_Score']:.2f}")
    st.metric("FH Score (ML)", f"{fh_a:.2f}")

with right:
    row_b, fh_b, shap_b = render_company(company_b)
    st.subheader(company_b)
    st.metric("FH Score (Formula)", f"{row_b['FH_Score']:.2f}")
    st.metric("FH Score (ML)", f"{fh_b:.2f}")

# ============================================================
# FINAL DECISION
# ============================================================
st.markdown("## 🧾 Final Result")

if fh_a > fh_b:
    st.success(f"**{company_a}** has a stronger credit profile than **{company_b}**.")
elif fh_b > fh_a:
    st.success(f"**{company_b}** has a stronger credit profile than **{company_a}**.")
else:
    st.info("Both companies exhibit similar risk profiles.")

# ============================================================
# EXPORT
# ============================================================
output = io.BytesIO()
df.to_excel(output, index=False)

st.download_button(
    "📥 Download Comparison Report",
    output.getvalue(),
    file_name="Two_Company_Credit_Comparison.xlsx"
)
