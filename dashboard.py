import streamlit as st
import plotly.express as px
import pandas as pd
import warnings
from io import StringIO

warnings.filterwarnings("ignore")

st.set_page_config(page_title="Superstore!!!", page_icon=":bar_chart:", layout="wide")

st.title(":bar_chart: Sample Superstore EDA")
st.markdown('<style>div.block-container{padding-top:2.5rem;}</style>', unsafe_allow_html=True)

# File upload section
fl = st.file_uploader(":file_folder: Upload a file", type=['csv', 'txt', 'xlsx', 'xls'])

# Load data
if fl is not None:
    try:
        if fl.name.endswith('.csv') or fl.name.endswith('.txt'):
            df = pd.read_csv(fl, encoding="ISO-8859-1")
        elif fl.name.endswith('.xlsx') or fl.name.endswith('.xls'):
            df = pd.read_excel(fl)
    except Exception as e:
        st.error(f"Error reading file: {e}")
        st.stop()
else:
    st.warning("Please upload a file to proceed.")
    st.stop()

# Check for necessary columns
required_columns = {"Order Date", "Region", "State", "City", "Sales", "Profit", "Category"}
if not required_columns.issubset(set(df.columns)):
    st.error("The uploaded file does not contain all the required columns.")
    st.stop()

# Convert date column
df["Order Date"] = pd.to_datetime(df["Order Date"], errors='coerce')

# Date Range Selection
col1, col2 = st.columns((2,))
StartDate = df["Order Date"].min()
EndDate = df["Order Date"].max()

with col1:
    date1 = st.date_input("Start Date", StartDate)

with col2:
    date2 = st.date_input("End Date", EndDate)

# Filter based on dates
df = df[(df["Order Date"] >= pd.to_datetime(date1)) & (df["Order Date"] <= pd.to_datetime(date2))]

# Sidebar Filters
st.sidebar.header("Choose your filters:")
region = st.sidebar.multiselect("Pick your Region", options=df["Region"].unique(), default=df["Region"].unique())
state = st.sidebar.multiselect("Pick your State", options=df[df["Region"].isin(region)]["State"].unique())
city = st.sidebar.multiselect("Pick your City", options=df[df["State"].isin(state)]["City"].unique())

# Apply filters
filtered_df = df[
    (df["Region"].isin(region)) &
    (df["State"].isin(state) if state else True) &
    (df["City"].isin(city) if city else True)
]

# Visualizations
st.subheader("Category wise Sales")
category_df = filtered_df.groupby("Category", as_index=False)["Sales"].sum()
fig1 = px.bar(category_df, x="Category", y="Sales", text=category_df["Sales"], template="seaborn")
st.plotly_chart(fig1, use_container_width=True)

st.subheader("Region wise Sales")
fig2 = px.pie(filtered_df, values="Sales", names="Region", hole=0.5, template="plotly_white")
st.plotly_chart(fig2, use_container_width=True)

# Time Series Analysis
filtered_df["month_year"] = filtered_df["Order Date"].dt.to_period("M")
time_series = filtered_df.groupby(filtered_df["month_year"].dt.strftime("%Y-%m"))["Sales"].sum().reset_index()
st.subheader("Time Series Analysis")
fig3 = px.line(time_series, x="month_year", y="Sales", template="plotly_dark")
st.plotly_chart(fig3, use_container_width=True)

# Download Button
st.subheader("Download Filtered Data")
csv = filtered_df.to_csv(index=False).encode('utf-8')
st.download_button(label="Download Data", data=csv, file_name="filtered_data.csv", mime="text/csv")
