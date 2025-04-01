import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta
import calendar

# Set page config
st.set_page_config(layout="wide", page_title="Translation Quality Analysis", page_icon="📊")

# Custom CSS for styling
st.markdown("""
<style>
    .big-button {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        margin: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
    .big-button h1 {
        font-size: 2.5rem;
        margin: 0;
    }
    .big-button p {
        font-size: 1.2rem;
        color: #636363;
    }
    .highlight-box {
        background-color: #f8f9fa;
        border-left: 5px solid #5c6bc0;
        padding: 15px;
        margin: 15px 0;
        border-radius: 0 5px 5px 0;
    }
    .error-detail {
        border: 1px solid #e0e0e0;
        border-radius: 5px;
        padding: 15px;
        margin: 10px 0;
        background-color: #ffffff;
    }
    .stExpander {
        border: none !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1) !important;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.title("Translation Quality Analysis Dashboard")
st.markdown("### Interactive visualization of translation quality errors")

# File uploader
uploaded_file = st.sidebar.file_uploader("Upload Excel File", type=['xlsx', 'xls'])

# Demo data generation if no file is uploaded
@st.cache_data
def generate_demo_data():
    owners = ["Owner A", "Owner B", "Owner C", "Owner D", "Owner E"]
    content_types = ["Documentation", "UI", "Marketing", "Technical", "Legal"]
    products = ["Product X", "Product Y", "Product Z"]
    service_types = ["Translation", "Review", "Proofreading"]
    issue_types = ["Grammar", "Terminology", "Consistency", "Formatting", "Omission"]
    factors = ["Internal", "External"]
    categories = ["Major", "Minor", "Critical"]
    sub_categories = ["Linguistic", "Technical", "Stylistic"]
    
    # Generate 100 random entries
    data = {
        "Month": np.random.choice(["January", "February", "March", "April", "May"], 100),
        "LQE Date": [datetime(2023, np.random.randint(1, 6), np.random.randint(1, 28)) for _ in range(100)],
        "Week": np.random.randint(1, 53, 100),
        "Owner": np.random.choice(owners, 100),
        "Task ID": [f"TASK-{np.random.randint(1000, 9999)}" for _ in range(100)],
        "Project": [f"Project-{np.random.randint(1, 10)}" for _ in range(100)],
        "Content Type": np.random.choice(content_types, 100),
        "Product": np.random.choice(products, 100),
        "Service Type": np.random.choice(service_types, 100),
        "Source Text": [f"Source text sample {i}" for i in range(100)],
        "Translated Text": [f"Translated text sample {i}" for i in range(100)],
        "Corrected Text Show Edits": [f"Corrected <span style='color:red;text-decoration:line-through;'>text</span> <span style='color:green;'>translation</span> sample {i}" for i in range(100)],
        "Error Type & comment": [f"Error type {np.random.choice(['A', 'B', 'C'])} - Comment {i}" for i in range(100)],
        "Issue Type": np.random.choice(issue_types, 100),
        "Internal/External factor validated by LL": np.random.choice(factors, 100),
        "Category": np.random.choice(categories, 100),
        "Sub - cateogory": np.random.choice(sub_categories, 100),
        "Clarification": [f"Clarification {i % 5}" for i in range(100)],
        "Sub-clarification": [f"Sub-clarification {i % 3}" for i in range(100)],
        "Repeat": np.random.choice(["Yes", "No"], 100),
        "Reason": [f"Reason {i % 7}" for i in range(100)],
        "Final action": np.random.choice(["Fixed", "Rejected", "Pending"], 100),
        "Final status": np.random.choice(["Closed", "Open"], 100),
        "Remark": [f"Remark {i}" for i in range(100)],
        "Global categories": np.random.choice(["Cat A", "Cat B", "Cat C"], 100)
    }
    
    return pd.DataFrame(data)

# Load data
if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)
    except Exception as e:
        st.error(f"Error loading file: {str(e)}")
        df = generate_demo_data()
        st.sidebar.info("Using demo data due to error. Please check your Excel file.")
else:
    df = generate_demo_data()
    st.sidebar.info("Using demo data. Upload your Excel file for actual analysis.")

# Convert date column to datetime if needed
if 'LQE Date' in df.columns:
    try:
        df['LQE Date'] = pd.to_datetime(df['LQE Date'])
        df['Month'] = df['LQE Date'].dt.strftime('%B')
        df['Year'] = df['LQE Date'].dt.year
    except Exception as e:
        st.warning(f"Error converting dates: {str(e)}")

# Sidebar filters
st.sidebar.header("Filters")

# Owner selection with "All" option
# Fix for mixed data types in Owner column
owners_list = df['Owner'].unique()
# Convert any NaN values to strings
owners_list = [str(owner) if not pd.isna(owner) else "Unknown" for owner in owners_list]
all_owners = sorted(owners_list)
selected_owner = st.sidebar.selectbox("Select Owner", ["All Owners"] + all_owners)

# Date range filter
date_min = df['LQE Date'].min().date()
date_max = df['LQE Date'].max().date()
date_range = st.sidebar.date_input("Select Date Range", [date_min, date_max])

# Apply filters
filtered_df = df.copy()
if selected_owner != "All Owners":
    filtered_df = filtered_df[filtered_df['Owner'] == selected_owner]

if len(date_range) == 2:
    start_date, end_date = date_range
    filtered_df = filtered_df[(filtered_df['LQE Date'].dt.date >= start_date) & 
                              (filtered_df['LQE Date'].dt.date <= end_date)]

# Main dashboard area
if selected_owner == "All Owners":
    st.markdown("## Overview of All Owners")
else:
    st.markdown(f"## Analysis for: {selected_owner}")

# Metrics in big buttons
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="big-button">
        <p>Total Errors</p>
        <h1>{}</h1>
    </div>
    """.format(len(filtered_df)), unsafe_allow_html=True)

with col2:
    internal_count = filtered_df[filtered_df['Internal/External factor validated by LL'] == 'Internal'].shape[0]
    st.markdown("""
    <div class="big-button">
        <p>Internal Factors</p>
        <h1>{}</h1>
    </div>
    """.format(internal_count), unsafe_allow_html=True)

with col3:
    external_count = filtered_df[filtered_df['Internal/External factor validated by LL'] == 'External'].shape[0]
    st.markdown("""
    <div class="big-button">
        <p>External Factors</p>
        <h1>{}</h1>
    </div>
    """.format(external_count), unsafe_allow_html=True)

# Trend over time - Determine if we should show daily or monthly trend
st.markdown("## Error Trend Over Time")

if len(date_range) == 2:
    start_date, end_date = date_range
    # Check if the range is within a single month
    same_month = (start_date.year == end_date.year) and (start_date.month == end_date.month)
    
    if same_month:
        # Use daily trend for a single month
        time_trend = filtered_df.groupby(filtered_df['LQE Date'].dt.date)['Task ID'].count().reset_index()
        fig_trend = px.line(time_trend, x='LQE Date', y='Task ID', 
                           labels={'Task ID': 'Number of Errors', 'LQE Date': 'Date'},
                           markers=True)
    else:
        # Use monthly trend for multi-month period
        time_trend = filtered_df.groupby([filtered_df['LQE Date'].dt.to_period('M')])['Task ID'].count().reset_index()
        time_trend['LQE Date'] = time_trend['LQE Date'].dt.to_timestamp()
        fig_trend = px.line(time_trend, x='LQE Date', y='Task ID', 
                           labels={'Task ID': 'Number of Errors', 'LQE Date': 'Month'},
                           markers=True)
else:
    # Default to monthly view
    time_trend = filtered_df.groupby([filtered_df['LQE Date'].dt.to_period('M')])['Task ID'].count().reset_index()
    time_trend['LQE Date'] = time_trend['LQE Date'].dt.to_timestamp()
    fig_trend = px.line(time_trend, x='LQE Date', y='Task ID', 
                       labels={'Task ID': 'Number of Errors', 'LQE Date': 'Month'},
                       markers=True)

fig_trend.update_layout(height=400)
st.plotly_chart(fig_trend, use_container_width=True)

# Category and Sub-category trends over time
st.markdown("## Category and Sub-Category Trends")

cat_tabs = st.tabs(["Category Trends", "Sub-Category Trends"])

with cat_tabs[0]:
    # Category trend over time
    if len(date_range) == 2 and (start_date.year == end_date.year) and (start_date.month == end_date.month):
        # Daily trend for categories
        cat_time = filtered_df.groupby([filtered_df['LQE Date'].dt.date, 'Category'])['Task ID'].count().reset_index()
        fig_cat_trend = px.line(cat_time, x='LQE Date', y='Task ID', color='Category',
                               labels={'Task ID': 'Number of Errors', 'LQE Date': 'Date'},
                               markers=True)
    else:
        # Monthly trend for categories
        cat_time = filtered_df.groupby([filtered_df['LQE Date'].dt.to_period('M'), 'Category'])['Task ID'].count().reset_index()
        cat_time['LQE Date'] = cat_time['LQE Date'].dt.to_timestamp()
        fig_cat_trend = px.line(cat_time, x='LQE Date', y='Task ID', color='Category',
                               labels={'Task ID': 'Number of Errors', 'LQE Date': 'Month'},
                               markers=True)
    
    fig_cat_trend.update_layout(height=400)
    st.plotly_chart(fig_cat_trend, use_container_width=True)

with cat_tabs[1]:
    # Sub-category trend over time
    if len(date_range) == 2 and (start_date.year == end_date.year) and (start_date.month == end_date.month):
        # Daily trend for sub-categories
        subcat_time = filtered_df.groupby([filtered_df['LQE Date'].dt.date, 'Sub - cateogory'])['Task ID'].count().reset_index()
        fig_subcat_trend = px.line(subcat_time, x='LQE Date', y='Task ID', color='Sub - cateogory',
                                  labels={'Task ID': 'Number of Errors', 'LQE Date': 'Date'},
                                  markers=True)
    else:
        # Monthly trend for sub-categories
        subcat_time = filtered_df.groupby([filtered_df['LQE Date'].dt.to_period('M'), 'Sub - cateogory'])['Task ID'].count().reset_index()
        subcat_time['LQE Date'] = subcat_time['LQE Date'].dt.to_timestamp()
        fig_subcat_trend = px.line(subcat_time, x='LQE Date', y='Task ID', color='Sub - cateogory',
                                  labels={'Task ID': 'Number of Errors', 'LQE Date': 'Month'},
                                  markers=True)
    
    fig_subcat_trend.update_layout(height=400)
    st.plotly_chart(fig_subcat_trend, use_container_width=True)

# Top-level breakdowns
st.markdown("## Error Distribution")

col1, col2 = st.columns(2)

with col1:
    # Content Type breakdown
    fig_content = px.pie(filtered_df, names='Content Type', title='Errors by Content Type',
                         color_discrete_sequence=px.colors.qualitative.Pastel)
    fig_content.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig_content, use_container_width=True)
    
    # Service Type breakdown
    fig_service = px.pie(filtered_df, names='Service Type', title='Errors by Service Type',
                        color_discrete_sequence=px.colors.qualitative.Pastel1)
    fig_service.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig_service, use_container_width=True)

with col2:
    # Product breakdown
    fig_product = px.pie(filtered_df, names='Product', title='Errors by Product',
                         color_discrete_sequence=px.colors.qualitative.Pastel2)
    fig_product.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig_product, use_container_width=True)
    
    # Issue Type breakdown
    fig_issue = px.pie(filtered_df, names='Issue Type', title='Errors by Issue Type',
                      color_discrete_sequence=px.colors.qualitative.Set3)
    fig_issue.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig_issue, use_container_width=True)

# Categorical analysis
st.markdown("## Detailed Categorical Analysis")

# Heatmap by category and sub-category
cat_subcat = filtered_df.groupby(['Category', 'Sub - cateogory']).size().reset_index(name='count')
pivot_table = cat_subcat.pivot(index='Category', columns='Sub - cateogory', values='count').fillna(0)

fig_heatmap = px.imshow(pivot_table, 
                       labels=dict(x="Sub-category", y="Category", color="Count"),
                       text_auto=True, aspect="auto",
                       color_continuous_scale='Viridis')
fig_heatmap.update_layout(height=400)
st.plotly_chart(fig_heatmap, use_container_width=True)

# Advanced breakdowns in tabs
st.markdown("## Error Analysis by Categories")

tab1, tab2, tab3 = st.tabs(["Factor Analysis", "Category Breakdown", "Clarification Details"])

with tab1:
    # Internal/External factor analysis
    factor_df = filtered_df['Internal/External factor validated by LL'].value_counts().reset_index()
    factor_df.columns = ['Factor', 'Count']
    
    fig_factor = px.bar(factor_df, x='Factor', y='Count', 
                       title='Internal vs External Factors',
                       color='Factor', 
                       text='Count')
    fig_factor.update_layout(height=400)
    st.plotly_chart(fig_factor, use_container_width=True)

with tab2:
    # Category analysis
    cat_df = filtered_df['Category'].value_counts().reset_index()
    cat_df.columns = ['Category', 'Count']
    
    fig_cat = px.bar(cat_df, x='Category', y='Count',
                    title='Error Categories',
                    color='Category',
                    text='Count')
    fig_cat.update_layout(height=400)
    st.plotly_chart(fig_cat, use_container_width=True)
    
    # Sub-category analysis
    subcat_df = filtered_df['Sub - cateogory'].value_counts().reset_index()
    subcat_df.columns = ['Sub-category', 'Count']
    
    fig_subcat = px.bar(subcat_df, x='Sub-category', y='Count',
                       title='Error Sub-categories',
                       color='Sub-category',
                       text='Count')
    fig_subcat.update_layout(height=400)
    st.plotly_chart(fig_subcat, use_container_width=True)

with tab3:
    # Clarification analysis
    clarif_df = filtered_df['Clarification'].value_counts().reset_index()
    clarif_df.columns = ['Clarification', 'Count']
    
    fig_clarif = px.bar(clarif_df, x='Clarification', y='Count',
                       title='Error Clarifications',
                       color='Clarification',
                       text='Count')
    fig_clarif.update_layout(height=400)
    st.plotly_chart(fig_clarif, use_container_width=True)
    
    # Sub-clarification analysis
    subclarif_df = filtered_df['Sub-clarification'].value_counts().reset_index()
    subclarif_df.columns = ['Sub-clarification', 'Count']
    
    fig_subclarif = px.bar(subclarif_df, x='Sub-clarification', y='Count',
                          title='Error Sub-clarifications',
                          color='Sub-clarification',
                          text='Count')
    fig_subclarif.update_layout(height=400)
    st.plotly_chart(fig_subclarif, use_container_width=True)

# Individual error details with expandable view
st.markdown("## Individual Error Details")

# Add search filter for error details
search_term = st.text_input("Search in error details:", "")
if search_term:
    search_results = filtered_df[
        filtered_df['Source Text'].str.contains(search_term, case=False) |
        filtered_df['Translated Text'].str.contains(search_term, case=False) |
        filtered_df['Error Type & comment'].str.contains(search_term, case=False) |
        filtered_df['Task ID'].str.contains(search_term, case=False)
    ]
    display_df = search_results
else:
    display_df = filtered_df

# Sort by date, most recent first
display_df = display_df.sort_values('LQE Date', ascending=False)

# Pagination for errors
items_per_page = 10
total_pages = (len(display_df) + items_per_page - 1) // items_per_page

if total_pages > 0:
    page = st.slider("Page", 1, max(1, total_pages), 1)
    start_idx = (page - 1) * items_per_page
    end_idx = min(start_idx + items_per_page, len(display_df))
    
    page_df = display_df.iloc[start_idx:end_idx]
    
    for i, (idx, row) in enumerate(page_df.iterrows()):
        with st.expander(f"Error #{idx}: {row['Task ID']} - {row['LQE Date'].strftime('%Y-%m-%d')} - {row['Content Type']}"):
            cols = st.columns([1, 2])
            with cols[0]:
                st.markdown("#### Error Details")
                st.markdown(f"**Owner:** {row['Owner']}")
                st.markdown(f"**Project:** {row['Project']}")
                st.markdown(f"**Product:** {row['Product']}")
                st.markdown(f"**Service Type:** {row['Service Type']}")
                st.markdown(f"**Issue Type:** {row['Issue Type']}")
                st.markdown(f"**Factor:** {row['Internal/External factor validated by LL']}")
                st.markdown(f"**Category:** {row['Category']}")
                st.markdown(f"**Sub-category:** {row['Sub - cateogory']}")
                st.markdown(f"**Status:** {row['Final status']}")
            
            with cols[1]:
                st.markdown("#### Translation & Correction")
                st.markdown("**Source Text:**")
                if 'Source Text' in row and not pd.isna(row['Source Text']):
                    st.markdown(f"<div class='highlight-box'>{row['Source Text']}</div>", unsafe_allow_html=True)
                else:
                    st.markdown("<div class='highlight-box'>Not available</div>", unsafe_allow_html=True)
    
                st.markdown("**Translated Text:**")
                if 'Translated Text' in row and not pd.isna(row['Translated Text']):
                    st.markdown(f"<div class='highlight-box'>{row['Translated Text']}</div>", unsafe_allow_html=True)
                else:
                    st.markdown("<div class='highlight-box'>Not available</div>", unsafe_allow_html=True)
    
                st.markdown("**Corrected Text Show Edits:**")
                try:
                    # Try multiple approaches to handle the column correctly
                    if 'Corrected Text Show Edits' in row and row['Corrected Text Show Edits'] is not None:
                        if not pd.isna(row['Corrected Text Show Edits']):
                            st.markdown(f"<div class='highlight-box'>{row['Corrected Text Show Edits']}</div>", unsafe_allow_html=True)
                        else:
                            st.markdown("<div class='highlight-box'>Not available</div>", unsafe_allow_html=True)
                    else:
                        # Look for similar column names
                        possible_columns = [col for col in row.index if 'correct' in col.lower() and 'edit' in col.lower()]
                        if possible_columns:
                            st.markdown(f"<div class='highlight-box'>{row[possible_columns[0]]}</div>", unsafe_allow_html=True)
                        else:
                            st.markdown("<div class='highlight-box'>Not available</div>", unsafe_allow_html=True)
                except Exception as e:
                    st.markdown(f"<div class='highlight-box'>Error displaying Hindi text: {str(e)}</div>", unsafe_allow_html=True)
    
                st.markdown("**Error Type & Comment:**")
                if 'Error Type & comment' in row and not pd.isna(row['Error Type & comment']):
                    st.markdown(f"<div class='highlight-box'>{row['Error Type & comment']}</div>", unsafe_allow_html=True)
                else:
                    st.markdown("<div class='highlight-box'>Not available</div>", unsafe_allow_html=True)
    
                if 'Remark' in row and pd.notna(row['Remark']):
                    st.markdown("**Remarks:**")
                    st.markdown(f"<div class='highlight-box'>{row['Remark']}</div>", unsafe_allow_html=True)

else:
    st.info("No errors found matching the current filters.")

# Footer
st.markdown("---")
st.markdown("Translation Quality Analysis Dashboard • Created with Streamlit")