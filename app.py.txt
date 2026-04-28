import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="Transaction Dashboard", layout="wide")
st.title("📊 Wallet Transaction Analytics")

@st.cache_data
def load_data():
    uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx", "xls"])
    if uploaded_file is not None:
        df = pd.read_excel(uploaded_file)
        df['CreatedDate'] = pd.to_datetime(df['CreatedDate'])
        return df
    return None

df = load_data()

if df is not None:
    st.sidebar.header("🔍 Filters")
    start_date = st.sidebar.date_input("Start Date", datetime.today().replace(day=1))
    end_date = st.sidebar.date_input("End Date", datetime.today())
    
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    df_filtered = df[(df['CreatedDate'] >= start_date) & (df['CreatedDate'] <= end_date)]
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("💰 Total Volume (Rs)", f"{df_filtered['Amount (Rs)'].sum():,.0f}")
    col2.metric("📦 Total Transactions", f"{len(df_filtered):,}")
    col3.metric("👥 Unique Users", df_filtered['MemberId'].nunique())
    col4.metric("✅ Success Rate", f"{(df_filtered['Gateway Status'].eq('Success').mean()*100):.1f}%")
    
    st.subheader("📈 Most Used Services")
    col1, col2 = st.columns(2)
    service_count = df_filtered['Service'].value_counts().head(10).reset_index()
    service_count.columns = ['Service', 'Count']
    fig1 = px.bar(service_count, x='Service', y='Count', title='Top 10 by Count')
    col1.plotly_chart(fig1, use_container_width=True)
    
    service_volume = df_filtered.groupby('Service')['Amount (Rs)'].sum().sort_values(ascending=False).head(10).reset_index()
    fig2 = px.bar(service_volume, x='Service', y='Amount (Rs)', title='Top 10 by Volume (Rs)')
    col2.plotly_chart(fig2, use_container_width=True)
    
    st.subheader("🔎 Look up a User")
    member_id_input = st.text_input("Enter MemberId or Subscriber Id")
    if member_id_input:
        user_data = df_filtered[(df_filtered['MemberId'].astype(str) == member_id_input) | 
                                 (df_filtered['Subscriber Id'].astype(str) == member_id_input)]
        if len(user_data) > 0:
            st.dataframe(user_data[['CreatedDate', 'Service', 'Sign', 'Amount (Rs)', 'Available Balance(Rs)', 'Remarks', 'Gateway Status']])
        else:
            st.warning("No transactions found")