import streamlit as st
import pandas as pd
import numpy as np
import io
import plotly.graph_objects as go
import matplotlib.pyplot as plt

from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer

st.set_page_config("Corporate Credit Comparison", layout="wide")
st.title("🏦 Corporate Credit Risk Comparison Dashboard")

# ============================================================
# UPLOAD FILE (2 COMPANIES)
# ============================================================
uploaded = st.file_uploader(
    "Upload Excel File (2 Companies)",
    type=["xlsx"]
)

if uploaded is None:
    st.stop()

# ============================================================
# BACKEND ENGINE (YOUR LOGIC – COMPRESSED, SAME OUTPUT)
# ============================================================
def num(x):
    try:
        return float(str(x).replace(",", "").replace("₹", ""))
    except:
        return np.nan

df = pd.read_excel(uploaded)
df.columns = [c.strip() for c in df.columns]
df["FY"] = pd.to_numeric(df["FY"], errors="coerce")
df = df.dropna(subset=["Company Name", "FY"])

num_cols = [
    "Turnover (₹ Crore)","EBITDA (₹ Crore)","Net Worth (₹ Crore)",
    "Total Debt (₹ Crore)","DSCR","Current Ratio",
    "ROCE (%)","ROE (%)","Maximum DPD Observed"
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
        0.35*leverage + 0.20*liquidity + 0.20*coverage +
        0.15*profitability + 0.10*r["Document_Score"]/100,
        0,100
    )

df["FH_Score"] = df.apply(compute_fh, axis=1)

df = df.sort_values(["Company Name","FY"])
df["EBITDA_Margin"] = df["EBITDA (₹ Crore)"]/(df["Turnover (₹ Crore)"]+1e-6)
df["Growth_1Y"] = df.groupby("Company Name")["Turnover (₹ Crore)"].pct_change()
df["Trend_Slope"] = df.groupby("Company Name")["FH_Score"].transform(
    lambda x: np.polyfit(range(len(x)),x,1)[0] if len(x)>1 else 0
)

# ============================================================
# TRAIN ML MODEL ON BOTH COMPANIES
# ============================================================
FEATURES = [
    "FH_Score","Trend_Slope","Growth_1Y","EBITDA_Margin","Document_Score"
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
# COMPANY SELECTION
# ============================================================
companies = sorted(df["Company Name"].unique())

col1, col2 = st.columns(2)
with col1:
    comp_a = st.selectbox("Select Company A", companies, key="A")
with col2:
    comp_b = st.selectbox("Select Company B", companies, key="B", index=1)

# ============================================================
# DASHBOARD RENDER FUNCTION
# ============================================================
def render_company(company):

    hist = df[df["Company Name"]==company]
    row = hist.iloc[-1]
    X = row[FEATURES]
    fh_ml = pipe.predict(pd.DataFrame([X]))[0]

    st.subheader(company)
    st.metric("FH Score (Formula)", f"{row['FH_Score']:.2f}")
    st.metric("FH Score (ML)", f"{fh_ml:.2f}")

    # SHAP-style
    z = (X - means) / stds
    impact = z * pipe.named_steps["model"].coef_

    shap_df = pd.DataFrame({
        "Driver": FEATURES,
        "Impact": impact.values
    })

    pos = shap_df[shap_df["Impact"]>0]
    neg = shap_df[shap_df["Impact"]<0]

    st.write("**Positive Factors**")
    for _, r in pos.iterrows():
        st.write(f"• {r['Driver']} : +{r['Impact']:.2f}")

    st.write("**Risk Concerns**")
    for _, r in neg.iterrows():
        st.write(f"• {r['Driver']} : {r['Impact']:.2f}")

    # Trend
    fig, ax = plt.subplots()
    ax.plot(hist["FY"], hist["FH_Score"], marker="o")
    ax.set_title("FH Trend")
    ax.grid(True)
    st.pyplot(fig)

    return fh_ml

# ============================================================
# SIDE-BY-SIDE VIEW
# ============================================================
st.markdown("## 📊 Company Comparison")

left, right = st.columns(2)

with left:
    fh_a = render_company(comp_a)

with right:
    fh_b = render_company(comp_b)

# ============================================================
# FINAL RESULT
# ============================================================
st.markdown("## 🧾 Final Result")

if fh_a > fh_b:
    st.success(f"**{comp_a}** has a stronger credit profile than **{comp_b}**.")
elif fh_b > fh_a:
    st.success(f"**{comp_b}** has a stronger credit profile than **{comp_a}**.")
else:
    st.info("Both companies have similar risk profiles.")

# ============================================================
# EXPORT
# ============================================================
out = io.BytesIO()
df.to_excel(out, index=False)

st.download_button(
    "📥 Download Full Result File",
    out.getvalue(),
    file_name="2_Company_Credit_Comparison.xlsx"
)
