import streamlit as st
import plotly.express as px
import pandas as pd
import os
import warnings

# Suppress warnings
warnings.filterwarnings('ignore')

# Streamlit Page Configuration
st.set_page_config(page_title="Superstore Analysis", page_icon=":bar_chart:", layout="wide")

# Title and Styling
st.title(":bar_chart: Sample Superstore EDA")
st.markdown('<style>div.block-container{padding-top:2.5rem;}</style>', unsafe_allow_html=True)

# File Uploader
fl = st.file_uploader(":file_folder: Upload a file", type=['csv', 'txt', 'xlsx', 'xls'])

try:
    if fl is not None:
        filename = fl.name
        st.write(f"Uploaded file: `{filename}`")
        if filename.endswith('.csv') or filename.endswith('.txt'):
            df = pd.read_csv(fl, encoding="ISO-8859-1")
        else:
            df = pd.read_excel(fl)
    else:
        # Default file if no file is uploaded
        default_path = os.path.join(os.getcwd(), "Superstore.csv")
        st.info("Using default dataset: `Superstore.csv`")
        df = pd.read_csv(default_path, encoding="utf-8")

    # Convert Order Date to datetime
    df["Order Date"] = pd.to_datetime(df["Order Date"], errors='coerce')

    # Handle missing or invalid date entries
    if df["Order Date"].isnull().any():
        st.warning("Some rows have invalid dates. These rows will be excluded.")
        df = df.dropna(subset=["Order Date"])

    # Get date range for filtering
    StartDate = df["Order Date"].min()
    EndDate = df["Order Date"].max()

    # Date Range Selection
    col1, col2 = st.columns(2)
    with col1:
        date1 = pd.to_datetime(st.date_input("Start Date", StartDate))
    with col2:
        date2 = pd.to_datetime(st.date_input("End Date", EndDate))

    # Filter by date range
    df = df[(df["Order Date"] >= date1) & (df["Order Date"] <= date2)].copy()

    # Sidebar Filters
    st.sidebar.header("Choose Your Filters")
    region = st.sidebar.multiselect("Pick your Region", df["Region"].unique())
    state = st.sidebar.multiselect("Pick the State", df["State"].unique())
    city = st.sidebar.multiselect("Pick the City", df["City"].unique())

    # Apply Filters
    filtered_df = df.copy()
    if region:
        filtered_df = filtered_df[filtered_df["Region"].isin(region)]
    if state:
        filtered_df = filtered_df[filtered_df["State"].isin(state)]
    if city:
        filtered_df = filtered_df[filtered_df["City"].isin(city)]

    # Sales by Category
    category_df = filtered_df.groupby("Category", as_index=False)["Sales"].sum()

    # Visualization Columns
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Category-wise Sales")
        fig = px.bar(category_df, x="Category", y="Sales",
                     text=category_df["Sales"].apply(lambda x: f"${x:,.2f}"),
                     template="seaborn")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Region-wise Sales")
        fig = px.pie(filtered_df, values="Sales", names="Region", hole=0.5)
        st.plotly_chart(fig, use_container_width=True)

    # Time Series Analysis
    st.subheader("Time Series Analysis")
    filtered_df["Month-Year"] = filtered_df["Order Date"].dt.to_period("M")
    linechart = (filtered_df.groupby(filtered_df["Month-Year"].dt.strftime("%Y-%b"))["Sales"]
                 .sum()
                 .reset_index())
    fig2 = px.line(linechart, x="Month-Year", y="Sales", labels={"Sales": "Amount"}, template="plotly_white")
    st.plotly_chart(fig2, use_container_width=True)

    # Hierarchical TreeMap
    st.subheader("Hierarchical View of Sales")
    fig3 = px.treemap(filtered_df, path=["Region", "Category", "Sub-Category"],
                      values="Sales", color="Sub-Category")
    st.plotly_chart(fig3, use_container_width=True)

    # Segment and Category Pie Charts
    chart1, chart2 = st.columns(2)
    with chart1:
        st.subheader("Segment-wise Sales")
        fig = px.pie(filtered_df, values="Sales", names="Segment", template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

    with chart2:
        st.subheader("Category-wise Sales")
        fig = px.pie(filtered_df, values="Sales", names="Category", template="seaborn")
        st.plotly_chart(fig, use_container_width=True)

    # Scatter Plot
    st.subheader("Scatter Plot: Sales vs. Profit")
    fig = px.scatter(filtered_df, x="Sales", y="Profit", size="Quantity",
                     title="Relationship between Sales and Profit")
    st.plotly_chart(fig, use_container_width=True)

    # Download Options
    st.subheader("Download Processed Data")
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button("Download Data", data=csv, file_name="FilteredData.csv", mime="text/csv")

except Exception as e:
    st.error(f"An error occurred: {e}")
