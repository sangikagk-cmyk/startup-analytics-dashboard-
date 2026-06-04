import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="Startup Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)

# -----------------------------
# CUSTOM CSS
# -----------------------------
st.markdown("""
<style>
.main {
    background-color: #f8f9fc;
}

.metric-card {
    background: white;
    padding: 20px;
    border-radius: 15px;
    box-shadow: 0px 2px 8px rgba(0,0,0,0.1);
    text-align: center;
}

h1, h2, h3 {
    color: #1f2937;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# TITLE
# -----------------------------
st.title("🚀 Startup Analytics Dashboard")
st.markdown("Interactive Data Analytics Dashboard for Startup Dataset")

# -----------------------------
# LOAD DATA
# -----------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("startup_data.csv")
    return df

df = load_data()

# -----------------------------
# DATA CLEANING
# -----------------------------
df.columns = df.columns.str.strip()

numeric_cols = df.select_dtypes(include=np.number).columns

for col in numeric_cols:
    df[col] = df[col].fillna(df[col].median())

# -----------------------------
# SIDEBAR FILTERS
# -----------------------------
st.sidebar.header("🔍 Filters")

categorical_cols = df.select_dtypes(include="object").columns.tolist()

selected_filters = {}

for col in categorical_cols:
    options = df[col].dropna().unique().tolist()

    selected = st.sidebar.multiselect(
        f"Select {col}",
        options=options,
        default=options
    )

    selected_filters[col] = selected

filtered_df = df.copy()

for col, selected in selected_filters.items():
    filtered_df = filtered_df[filtered_df[col].isin(selected)]

# -----------------------------
# KPI SECTION
# -----------------------------
st.subheader("📌 Key Performance Indicators")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Startups", len(filtered_df))

with col2:
    if "Funding_Amount" in filtered_df.columns:
        st.metric(
            "Avg Funding",
            f"${filtered_df['Funding_Amount'].mean():,.0f}"
        )

with col3:
    if "Valuation" in filtered_df.columns:
        st.metric(
            "Avg Valuation",
            f"${filtered_df['Valuation'].mean():,.0f}"
        )

with col4:
    if "Revenue" in filtered_df.columns:
        st.metric(
            "Avg Revenue",
            f"${filtered_df['Revenue'].mean():,.0f}"
        )

st.markdown("---")

# -----------------------------
# CHARTS
# -----------------------------

col1, col2 = st.columns(2)

# Industry Distribution
with col1:
    if "Industry" in filtered_df.columns:
        fig = px.histogram(
            filtered_df,
            x="Industry",
            title="Industry Distribution",
            color="Industry"
        )
        st.plotly_chart(fig, use_container_width=True)

# Region Distribution
with col2:
    if "Region" in filtered_df.columns:
        fig = px.pie(
            filtered_df,
            names="Region",
            title="Regional Startup Distribution"
        )
        st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# FUNDING ANALYSIS
# -----------------------------
col1, col2 = st.columns(2)

with col1:
    if (
        "Funding_Amount" in filtered_df.columns
        and "Industry" in filtered_df.columns
    ):
        fig = px.box(
            filtered_df,
            x="Industry",
            y="Funding_Amount",
            color="Industry",
            title="Funding Distribution by Industry"
        )
        st.plotly_chart(fig, use_container_width=True)

with col2:
    if (
        "Valuation" in filtered_df.columns
        and "Revenue" in filtered_df.columns
    ):
        fig = px.scatter(
            filtered_df,
            x="Revenue",
            y="Valuation",
            color="Industry"
            if "Industry" in filtered_df.columns
            else None,
            size="Employees"
            if "Employees" in filtered_df.columns
            else None,
            hover_data=filtered_df.columns,
            title="Revenue vs Valuation"
        )
        st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# YEAR TREND
# -----------------------------
if "Founded_Year" in filtered_df.columns:
    yearly = (
        filtered_df["Founded_Year"]
        .value_counts()
        .reset_index()
    )

    yearly.columns = ["Year", "Count"]

    fig = px.line(
        yearly.sort_values("Year"),
        x="Year",
        y="Count",
        markers=True,
        title="Startup Founded Trend"
    )

    st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# CORRELATION HEATMAP
# -----------------------------
st.subheader("📈 Correlation Heatmap")

corr = filtered_df[numeric_cols].corr()

fig = px.imshow(
    corr,
    text_auto=True,
    aspect="auto",
    color_continuous_scale="Viridis"
)

st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# DATA TABLE
# -----------------------------
st.subheader("📄 Dataset Preview")
st.dataframe(filtered_df)

# -----------------------------
# DOWNLOAD BUTTON
# -----------------------------
csv = filtered_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="⬇ Download Filtered Data",
    data=csv,
    file_name="filtered_startup_data.csv",
    mime="text/csv"
)

# -----------------------------
# AUTO INSIGHTS
# -----------------------------
st.subheader("💡 Business Insights")

insights = []

if "Industry" in filtered_df.columns:
    top_industry = (
        filtered_df["Industry"]
        .value_counts()
        .idxmax()
    )

    insights.append(
        f"🏆 Top industry is **{top_industry}**."
    )

if "Funding_Amount" in filtered_df.columns:
    insights.append(
        f"💰 Average funding amount is "
        f"**${filtered_df['Funding_Amount'].mean():,.0f}**."
    )

if "Revenue" in filtered_df.columns:
    top_revenue = filtered_df["Revenue"].max()

    insights.append(
        f"📈 Highest startup revenue is "
        f"**${top_revenue:,.0f}**."
    )

for item in insights:
    st.write(item)

st.success("Dashboard Loaded Successfully 🚀")
