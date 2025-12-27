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
# LOAD DATA (BACKEND INTEGRATION)
# ============================================================
@st.cache_data
def load_and_engineer_data(file_path):

    df = pd.read_excel(file_path)
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


FILE_PATH = r"C:\Users\vidya\Downloads\Indian_Companies_EWS_READY_WITH_FY2025.xlsx"
df = load_and_engineer_data(FILE_PATH)

# ============================================================
# TRAIN MODEL
# ============================================================
FEATURES = [
    "FH_Score","Trend_Slope","Growth_1Y",
    "EBITDA_Margin","Loan_Type_EWS","Document_Score"
]

df["FH_Next"] = df.groupby("Company Name")["FH_Score"].shift(-1)
train = df.dropna(subset=["FH_Next"])

X = train[FEATURES]
y = train["FH_Next"]

pipe = Pipeline([
    ("imp", SimpleImputer(strategy="median")),
    ("model", Ridge(alpha=1.2))
])

pipe.fit(X, y)

feature_means = X.mean()
feature_stds = X.std().replace(0,1)

# ============================================================
# UI — COMPANY SELECTION
# ============================================================
st.subheader("🏢 Company Dashboard")

company = st.selectbox(
    "Select a company",
    sorted(df["Company Name"].unique())
)

row = df[df["Company Name"]==company].iloc[-1]
X_row = row[FEATURES]

fh_pred = pipe.predict(pd.DataFrame([X_row]))[0]

# ============================================================
# SCORE SUMMARY
# ============================================================
c1, c2, c3 = st.columns(3)
c1.metric("FH Score (Formula)", f"{row['FH_Score']:.2f}")
c2.metric("FH Score (ML)", f"{fh_pred:.2f}")
c3.metric("Risk Band", "Low" if fh_pred>=75 else "Moderate" if fh_pred>=50 else "High")

# ============================================================
# SHAP-STYLE DRIVER ANALYSIS
# ============================================================
BUSINESS_DRIVERS = {
    "DSCR": "DSCR Ratio",
    "Loan_Type_EWS": "Banking Conduct",
    "Document_Score": "Industry Risk",
    "FH_Score": "Debt–Equity Ratio",
    "EBITDA_Margin": "EBITDA Margin",
    "Growth_1Y": "Revenue Growth (YoY)"
}

coef = pipe.named_steps["model"].coef_
z = (X_row - feature_means) / feature_stds
impacts = z * coef

shap_df = pd.DataFrame({
    "Feature": FEATURES,
    "Impact": impacts.values
})

driver_rows = []
for k, v in BUSINESS_DRIVERS.items():
    m = shap_df[shap_df["Feature"].str.contains(k, case=False)]
    driver_rows.append({
        "Driver": v,
        "Impact": round(m["Impact"].sum() if not m.empty else 0, 2)
    })

driver_df = pd.DataFrame(driver_rows)

# ============================================================
# RISK ASSESSMENT SUMMARY
# ============================================================
st.subheader("📋 Risk Assessment Summary")

pos = driver_df[driver_df["Impact"]>0]
neg = driver_df[driver_df["Impact"]<0]

c1, c2 = st.columns(2)

with c1:
    st.write("#### ✅ Positive Factors")
    if pos.empty:
        st.write("• None")
    for _, r in pos.iterrows():
        st.write(f"• **{r['Driver']}**  +{r['Impact']}")

with c2:
    st.write("#### ❌ Risk Concerns")
    if neg.empty:
        st.write("• No material concerns")
    for _, r in neg.iterrows():
        st.write(f"• **{r['Driver']}**  {r['Impact']}")

# ============================================================
# SHAP BAR CHART
# ============================================================
fig = go.Figure()
fig.add_bar(
    x=driver_df["Impact"],
    y=driver_df["Driver"],
    orientation="h",
    marker_color=["#dc2626" if v<0 else "#16a34a" for v in driver_df["Impact"]],
    text=driver_df["Impact"],
    textposition="auto"
)

fig.update_layout(
    title="Key Risk Drivers (SHAP Analysis)",
    height=350
)

st.plotly_chart(fig, use_container_width=True)

# ============================================================
# EXPORT
# ============================================================
st.subheader("📥 Export Risk Report")

export_df = pd.concat([
    pd.DataFrame([{
        "Company": company,
        "FH Score (Formula)": row["FH_Score"],
        "FH Score (ML)": fh_pred
    }]),
    driver_df
], axis=1)

buffer = io.BytesIO()
export_df.to_excel(buffer, index=False)

st.download_button(
    "Download Risk Report",
    buffer.getvalue(),
    file_name=f"{company}_Risk_Report.xlsx"
)
