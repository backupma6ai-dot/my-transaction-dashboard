import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="Transaction Dashboard", layout="wide")
st.title("📊 Wallet Transaction Analytics")

# File uploader
uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx", "xls"])

@st.cache_data
def load_data(file):
    df = pd.read_excel(file)
    
    # Display column names to help debug
    st.sidebar.write("📋 Detected Columns:", list(df.columns))
    
    # Rename columns if needed (remove spaces and special characters)
    df.columns = df.columns.str.strip()
    
    # Find the correct date column (try common names)
    date_column = None
    for col in df.columns:
        if 'date' in col.lower() or 'created' in col.lower():
            date_column = col
            break
    
    if date_column:
        df[date_column] = pd.to_datetime(df[date_column], errors='coerce')
        df = df.dropna(subset=[date_column])
    else:
        st.error("Could not find a date column in your file")
        return None
    
    # Find amount column
    amount_column = None
    for col in df.columns:
        if 'amount' in col.lower() or 'rs' in col.lower():
            amount_column = col
            break
    
    if not amount_column:
        st.error("Could not find an amount column")
        return None
    
    # Store column names for later use
    df.attrs['date_col'] = date_column
    df.attrs['amount_col'] = amount_column
    
    return df

if uploaded_file is not None:
    df = load_data(uploaded_file)
    
    if df is not None:
        date_col = df.attrs['date_col']
        amount_col = df.attrs['amount_col']
        
        st.sidebar.header("🔍 Filters")
        
        # Date range filter
        min_date = df[date_col].min().date()
        max_date = df[date_col].max().date()
        
        start_date = st.sidebar.date_input("Start Date", min_date, min_value=min_date, max_value=max_date)
        end_date = st.sidebar.date_input("End Date", max_date, min_value=min_date, max_value=max_date)
        
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)
        df_filtered = df[(df[date_col] >= start_date) & (df[date_col] <= end_date)]
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("💰 Total Volume (Rs)", f"{df_filtered[amount_col].sum():,.2f}")
        col2.metric("📦 Total Transactions", f"{len(df_filtered):,}")
        
        # Find Member ID column
        member_col = None
        for col in df.columns:
            if 'member' in col.lower() or 'user' in col.lower() or 'id' in col.lower():
                member_col = col
                break
        
        if member_col:
            col3.metric("👥 Unique Users", df_filtered[member_col].nunique())
        else:
            col3.metric("👥 Unique Users", "N/A")
        
        # Find Gateway Status column
        status_col = None
        for col in df.columns:
            if 'status' in col.lower() or 'gateway' in col.lower():
                status_col = col
                break
        
        if status_col and 'Success' in df_filtered[status_col].values:
            success_rate = (df_filtered[status_col] == 'Success').mean() * 100
            col4.metric("✅ Success Rate", f"{success_rate:.1f}%")
        else:
            col4.metric("✅ Success Rate", "N/A")
        
        # Most Used Services
        st.subheader("📈 Service Usage Analysis")
        
        # Find Service column
        service_col = None
        for col in df.columns:
            if 'service' in col.lower():
                service_col = col
                break
        
        if service_col:
            col1, col2 = st.columns(2)
            
            # By count
            service_count = df_filtered[service_col].value_counts().head(10).reset_index()
            service_count.columns = ['Service', 'Count']
            fig1 = px.bar(service_count, x='Service', y='Count', title='Top 10 Services by Transaction Count', color='Count')
            col1.plotly_chart(fig1, use_container_width=True)
            
            # By volume
            service_volume = df_filtered.groupby(service_col)[amount_col].sum().sort_values(ascending=False).head(10).reset_index()
            service_volume.columns = ['Service', 'Volume (Rs)']
            fig2 = px.bar(service_volume, x='Service', y='Volume (Rs)', title='Top 10 Services by Volume (Rs)', color='Volume (Rs)')
            col2.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("No 'Service' column found. Showing transaction types instead.")
        
        # User Lookup
        st.subheader("🔎 User Wallet Lookup")
        
        # Find Member ID or Subscriber ID column
        id_column = None
        for col in df.columns:
            if 'member' in col.lower() or 'subscriber' in col.lower() or 'wallet' in col.lower():
                id_column = col
                break
        
        if id_column:
            member_id_input = st.text_input(f"Enter {id_column} to search")
            
            if member_id_input:
                # Try exact match as string
                user_data = df_filtered[df_filtered[id_column].astype(str).str.contains(member_id_input, case=False, na=False)]
                
                if len(user_data) > 0:
                    # Show summary
                    total_credit = user_data[user_data['Sign'] == 'Credit'][amount_col].sum() if 'Sign' in user_data.columns else 0
                    total_debit = user_data[user_data['Sign'] == 'Debit'][amount_col].sum() if 'Sign' in user_data.columns else 0
                    net_flow = total_credit - total_debit
                    
                    st.metric("💰 Net Cash Flow", f"Rs. {net_flow:,.2f}")
                    
                    # Show transaction table
                    display_cols = [date_col, service_col if service_col else 'TxnId', amount_col]
                    if 'Sign' in df.columns:
                        display_cols.insert(2, 'Sign')
                    if 'Remarks' in df.columns:
                        display_cols.append('Remarks')
                    
                    st.dataframe(user_data[display_cols].sort_values(date_col, ascending=False))
                else:
                    st.warning(f"No transactions found for this {id_column}")
        else:
            st.info("No ID column found for user lookup")
        
        # Daily trend
        st.subheader("📅 Daily Transaction Trend")
        daily_trend = df_filtered.groupby(df_filtered[date_col].dt.date)[amount_col].sum().reset_index()
        daily_trend.columns = ['Date', 'Volume']
        fig3 = px.line(daily_trend, x='Date', y='Volume', title='Daily Transaction Volume')
        st.plotly_chart(fig3, use_container_width=True)
        
    else:
        st.error("Failed to load data. Please check your file format.")
else:
    st.info("👈 Please upload your Excel file to get started")
