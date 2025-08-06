import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime

# Set page configuration
st.set_page_config(page_title="Sales Pipeline Analysis", layout="wide")

# Title
st.title("Sales Pipeline Analysis Dashboard")

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv('sales_pipeline_data.csv')
    return df

df = load_data()

# Sidebar with custom styling
st.sidebar.markdown("""
    <style>
    .sidebar-filter {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

st.sidebar.markdown("""
    <div class='sidebar-filter'>
    <h2 style='text-align: center; color: #1f77b4;'> Dashboard Filters</h2>
    </div>
    """, unsafe_allow_html=True)

# Date range filter
st.sidebar.markdown("<h3 style='text-align: left; color: #2e4f4f;'> Date Range</h3>", unsafe_allow_html=True)
all_dates = pd.to_datetime(df['Stage_Entry_Date'])
min_date = all_dates.min().date()
max_date = all_dates.max().date()

col1, col2 = st.sidebar.columns(2)
with col1:
    start_date = st.date_input('Start Date', min_date, min_value=min_date, max_value=max_date)
with col2:
    end_date = st.date_input('End Date', max_date, min_value=min_date, max_value=max_date)

# Region filter with metrics
st.sidebar.markdown("<h3 style='text-align: left; color: #2e4f4f;'> Region Filter</h3>", unsafe_allow_html=True)
region_counts = df['Region'].value_counts()
selected_region = st.sidebar.multiselect(
    "Select Regions",
    options=df['Region'].unique(),
    default=df['Region'].unique(),
    help="Filter data by selecting one or more regions"
)

# Show region metrics
if selected_region:
    st.sidebar.markdown("<div class='sidebar-filter'>", unsafe_allow_html=True)
    total_regions = len(selected_region)
    st.sidebar.markdown(f" Selected Regions: {total_regions}")
    for region in selected_region:
        st.sidebar.markdown(f"- {region}: {region_counts[region]} deals")
    st.sidebar.markdown("</div>", unsafe_allow_html=True)

# Product filter with metrics
st.sidebar.markdown("<h3 style='text-align: left; color: #2e4f4f;'> Product Filter</h3>", unsafe_allow_html=True)
product_counts = df['Product'].value_counts()
selected_product = st.sidebar.multiselect(
    "Select Products",
    options=df['Product'].unique(),
    default=df['Product'].unique(),
    help="Filter data by selecting one or more products"
)

# Show product metrics
if selected_product:
    st.sidebar.markdown("<div class='sidebar-filter'>", unsafe_allow_html=True)
    total_products = len(selected_product)
    st.sidebar.markdown(f" Selected Products: {total_products}")
    for product in selected_product:
        st.sidebar.markdown(f"- {product}: {product_counts[product]} deals")
    st.sidebar.markdown("</div>", unsafe_allow_html=True)

# Deal stage filter
st.sidebar.markdown("<h3 style='text-align: left; color: #2e4f4f;'> Stage Filter</h3>", unsafe_allow_html=True)
selected_stages = st.sidebar.multiselect(
    "Select Stages",
    options=df['Stage'].unique(),
    default=df['Stage'].unique(),
    help="Filter data by deal stages"
)

# Apply all filters
filtered_df = df[
    (df['Region'].isin(selected_region)) & 
    (df['Product'].isin(selected_product)) & 
    (df['Stage'].isin(selected_stages)) &
    (pd.to_datetime(df['Stage_Entry_Date']).dt.date.between(start_date, end_date))
]

# Show active filters summary
st.sidebar.markdown("---")
st.sidebar.markdown("<h3 style='text-align: left; color: #2e4f4f;'> Active Filters</h3>", unsafe_allow_html=True)
st.sidebar.markdown(f"""
    - Date Range: {start_date} to {end_date}
    - Regions: {len(selected_region)} selected
    - Products: {len(selected_product)} selected
    - Stages: {len(selected_stages)} selected
    - **Total Deals:** {len(filtered_df)}
""")

# Main content
tab1, tab2, tab3, tab4 = st.tabs(["Pipeline Conversion", "Deal Size Analysis", "Sales Performance", "Revenue Analysis"])

with tab1:
    st.header("Pipeline Conversion Analysis")
    
    # Calculate stage counts
    stage_counts = filtered_df['Stage'].value_counts().sort_index()
    
    # Create funnel chart
    fig_funnel = go.Figure(go.Funnel(
        y=stage_counts.index,
        x=stage_counts.values,
        textinfo="value+percent initial"
    ))
    
    fig_funnel.update_layout(title="Sales Pipeline Funnel")
    st.plotly_chart(fig_funnel, use_container_width=True)
    
    # Calculate and display conversion rates
    conversion_rates = []
    for i in range(len(stage_counts)-1):
        conversion_rate = (stage_counts.iloc[i+1] / stage_counts.iloc[i]) * 100
        conversion_rates.append({
            'From Stage': stage_counts.index[i],
            'To Stage': stage_counts.index[i+1],
            'Conversion Rate': f"{conversion_rate:.2f}%"
        })
    
    st.dataframe(pd.DataFrame(conversion_rates))

with tab2:
    st.header("Deal Size Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Average deal size by product
        avg_by_product = filtered_df.groupby('Product')['Deal_Amount'].mean().sort_values(ascending=False).reset_index()
        fig_product = px.bar(
            data_frame=avg_by_product,
            x='Product',
            y='Deal_Amount',
            title="Average Deal Size by Product"
        )
        st.plotly_chart(fig_product, use_container_width=True)
    
    with col2:
        # Average deal size by region
        avg_by_region = filtered_df.groupby('Region')['Deal_Amount'].mean().sort_values(ascending=False).reset_index()
        fig_region = px.bar(
            data_frame=avg_by_region,
            x='Region',
            y='Deal_Amount',
            title="Average Deal Size by Region"
        )
        st.plotly_chart(fig_region, use_container_width=True)
    
    # Average deal size by sales rep
    avg_by_rep = filtered_df.groupby('Sales_Rep')['Deal_Amount'].mean().sort_values(ascending=False).reset_index()
    fig_rep = px.bar(
        data_frame=avg_by_rep,
        x='Sales_Rep',
        y='Deal_Amount',
        title="Average Deal Size by Sales Representative"
    )
    st.plotly_chart(fig_rep, use_container_width=True)

with tab3:
    st.header("Sales Representative Performance")
    
    # Calculate win rates
    win_rates = filtered_df.groupby('Sales_Rep').agg({
        'Stage': lambda x: (x == 'Closed Won').mean() * 100,
        'Deal_Amount': ['count', 'sum', 'mean']
    })
    
    win_rates.columns = ['Win Rate %', 'Total Deals', 'Total Revenue', 'Avg Deal Size']
    win_rates = win_rates.round(2)
    
    # Display performance metrics
    st.dataframe(win_rates)
    
    # Create win rate visualization
    win_rates_reset = win_rates.reset_index()
    fig_win_rate = px.bar(
        data_frame=win_rates_reset,
        x='Sales_Rep',
        y='Win Rate %',
        title="Win Rate by Sales Representative"
    )
    st.plotly_chart(fig_win_rate, use_container_width=True)

with tab4:
    st.header("Revenue Analysis")
    
    # Total revenue by product
    revenue_by_product = filtered_df.groupby('Product')['Deal_Amount'].sum().sort_values(ascending=False)
    
    # Create revenue visualization
    fig_revenue = px.pie(
        values=revenue_by_product.values,
        names=revenue_by_product.index,
        title="Revenue Distribution by Product"
    )
    st.plotly_chart(fig_revenue, use_container_width=True)
    
    # Revenue trend over time
    filtered_df['Close_Date'] = pd.to_datetime(filtered_df['Close_Date'])
    monthly_revenue = filtered_df.groupby(filtered_df['Close_Date'].dt.to_period('M'))['Deal_Amount'].sum()
    
    fig_trend = px.line(
        x=monthly_revenue.index.astype(str),
        y=monthly_revenue.values,
        title="Monthly Revenue Trend"
    )
    st.plotly_chart(fig_trend, use_container_width=True)
