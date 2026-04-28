import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="Transaction Dashboard", layout="wide")
st.title("📊 Wallet Transaction Analytics")

# Service Mapping Dictionary
SERVICE_MAPPING = {
    ('NCELL', 'Debit'): '📱 NCELL Topup',
    ('NCELL', 'Credit'): '💰 Cashback/NCELL',
    ('NTC', 'Debit'): '📱 NTC Topup',
    ('NTC', 'Credit'): '💰 Cashback/NTC',
    ('BANK TRANSFER', 'Debit'): '🏦 Bank Transfer Out',
    ('BANK TRANSFER', 'Credit'): '💰 Bank Load',
    ('MERCHANT BANK LOAD', 'Credit'): '💰 Merchant Bank Load',
    ('CASHBACK', 'Credit'): '🎁 Cashback Reward',
    ('USER P2P', 'Debit'): '👤 P2P Transfer Sent',
    ('USER P2P', 'Credit'): '👤 P2P Transfer Received',
    ('AGENT CASHIN', 'Credit'): '🏪 Agent Cash In',
    ('AGENT CASHIN', 'Debit'): '👤 Agent Transfer Out',
    ('AGENT CASHOUT', 'Credit'): '🏪 Agent Cash Out',
    ('AGENT CASHOUT', 'Debit'): '👤 Agent Transfer Out',
    ('AGENT P2P', 'Credit'): '🏪 Agent P2P Credit',
    ('AGENT P2P', 'Debit'): '👤 Agent P2P Debit',
    ('TRANSFER BY PHONE', 'Credit'): '📞 Phone Transfer Received',
    ('TRANSFER BY PHONE', 'Debit'): '📞 Phone Transfer Sent',
    ('Mobile Banking', 'Credit'): '📱 Mobile Banking Load',
    ('Mobile Banking', 'Debit'): '📱 Mobile Banking Debit',
    ('MERCHANT LOAD', 'Credit'): '🏪 Merchant Load',
    ('MERCHANT LOAD', 'Debit'): '💳 Merchant Payment',
    ('MERCHANT CHECKOUT', 'Debit'): '💳 Merchant Checkout',
    ('NEPALPAY QR PAYMENTS', 'Debit'): '📱 QR Payment',
    ('NEPALPAY QR PAYMENTS', 'Credit'): '💰 QR Cashback',
    ('FONEPAY QR PAYMENTS', 'Debit'): '📱 Fonepay QR',
    ('FONEPAY QR PAYMENTS', 'Credit'): '💰 Fonepay Cashback',
    ('NEA', 'Debit'): '⚡ Electricity Bill',
    ('NEA', 'Credit'): '💰 Electricity Refund',
    ('KUKL', 'Debit'): '💧 Water Bill',
    ('KUKL', 'Credit'): '💰 Water Refund',
}

def get_display_name(service, sign):
    key = (service, sign)
    if key in SERVICE_MAPPING:
        return SERVICE_MAPPING[key]
    if sign == 'Credit':
        return f"💰 {service}"
    else:
        return f"💸 {service}"

# File uploader
uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx", "xls"])

@st.cache_data
def load_data(file):
    df = pd.read_excel(file)
    df['CreatedDate'] = pd.to_datetime(df['CreatedDate'], errors='coerce')
    
    df['Display Service'] = df.apply(
        lambda row: get_display_name(row.get('Service', ''), row.get('Sign', '')), 
        axis=1
    )
    return df

if uploaded_file is not None:
    df = load_data(uploaded_file)
    
    # Sidebar filters
    st.sidebar.header("🔍 Filters")
    min_date = df['CreatedDate'].min().date()
    max_date = df['CreatedDate'].max().date()
    
    start_date = st.sidebar.date_input("Start Date", min_date, min_value=min_date, max_value=max_date)
    end_date = st.sidebar.date_input("End Date", max_date, min_value=min_date, max_value=max_date)
    
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    df_filtered = df[(df['CreatedDate'] >= start_date) & (df['CreatedDate'] <= end_date)]
    
    # Top metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("💰 Total Volume (Rs)", f"{df_filtered['Amount (Rs)'].sum():,.2f}")
    col2.metric("📦 Total Transactions", f"{len(df_filtered):,}")
    col3.metric("👥 Unique Users", df_filtered['MemberId'].nunique())
    success_rate = (df_filtered['Gateway Status'].eq('Success').mean() * 100) if 'Gateway Status' in df.columns else 0
    col4.metric("✅ Success Rate", f"{success_rate:.1f}%")
    
    # ============================================
    # NEW SECTION 1: CASH-IN MODES with Count & Volume
    # ============================================
    st.subheader("💰 Cash-In Analysis by Mode")
    
    # Define Cash-In services (Credit transactions from various sources)
    cash_in_services = [
        'BANK TRANSFER', 'MERCHANT BANK LOAD', 'Mobile Banking', 'AGENT CASHIN',
        'AGENT CASHOUT', 'USER P2P', 'MERCHANT LOAD', 'NEPALPAY QR PAYMENTS',
        'FONEPAY QR PAYMENTS', 'CASHBACK', 'TRANSFER BY PHONE', 'DEPOSIT BY CONNECTIPS',
        'DEPOSIT BY LINKED BANK', 'CREDIT BY LINKED BANK', 'INTERNET BANKING'
    ]
    
    # Filter Credit transactions with Cash-In services
    cash_in_data = df_filtered[
        (df_filtered['Sign'] == 'Credit') & 
        (df_filtered['Service'].isin(cash_in_services))
    ]
    
    if len(cash_in_data) > 0:
        # Group by Service mode
        cash_in_summary = cash_in_data.groupby('Service').agg({
            'TxnId': 'count',  # Count of transactions
            'Amount (Rs)': 'sum'  # Total volume
        }).reset_index()
        cash_in_summary.columns = ['Cash-In Mode', 'Transaction Count', 'Total Volume (Rs)']
        cash_in_summary = cash_in_summary.sort_values('Total Volume (Rs)', ascending=False)
        
        col1, col2 = st.columns(2)
        
        # Bar chart - Transaction Count
        fig_count = px.bar(cash_in_summary.head(10), 
                           x='Cash-In Mode', y='Transaction Count', 
                           title='Top 10 Cash-In Modes by Transaction Count',
                           color='Transaction Count', text='Transaction Count')
        col1.plotly_chart(fig_count, use_container_width=True)
        
        # Bar chart - Volume
        fig_volume = px.bar(cash_in_summary.head(10), 
                            x='Cash-In Mode', y='Total Volume (Rs)', 
                            title='Top 10 Cash-In Modes by Volume (Rs)',
                            color='Total Volume (Rs)', text='Total Volume (Rs)')
        col2.plotly_chart(fig_volume, use_container_width=True)
        
        # Display table
        st.write("### Cash-In Modes Summary Table")
        st.dataframe(cash_in_summary.style.format({
            'Transaction Count': '{:,}',
            'Total Volume (Rs)': 'Rs. {:,.2f}'
        }), use_container_width=True)
        
        # Download button for Cash-In data
        csv_cashin = cash_in_summary.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Cash-In Summary as CSV", csv_cashin, "cashin_summary.csv", "text/csv")
        
    else:
        st.info("No Cash-In transactions found in selected date range")
    
    # ============================================
    # NEW SECTION 2: Top Users who Cash-In AND do P2P Debit
    # ============================================
    st.subheader("👑 Top Users: Cash-In + P2P Debit Transactions")
    
    # Identify users who do BOTH:
    # 1. Cash-In (Credit from any cash-in mode)
    # 2. P2P Debit (USER P2P with Debit sign)
    
    # Users who did Cash-In
    cashin_users = set(cash_in_data['MemberId'].unique())
    
    # Users who did P2P Debit
    p2p_debit_data = df_filtered[
        (df_filtered['Service'] == 'USER P2P') & 
        (df_filtered['Sign'] == 'Debit')
    ]
    p2p_debit_users = set(p2p_debit_data['MemberId'].unique())
    
    # Users who did BOTH
    power_users = cashin_users.intersection(p2p_debit_users)
    
    if len(power_users) > 0:
        # Build summary for each power user
        user_summaries = []
        
        for user_id in power_users:
            # Cash-In stats for this user
            user_cashin = cash_in_data[cash_in_data['MemberId'] == user_id]
            total_cashin_volume = user_cashin['Amount (Rs)'].sum()
            total_cashin_count = len(user_cashin)
            
            # Cash-In modes used by this user
            modes_used = user_cashin['Service'].nunique()
            top_mode = user_cashin['Service'].value_counts().index[0] if len(user_cashin) > 0 else 'None'
            
            # P2P Debit stats for this user
            user_p2p = p2p_debit_data[p2p_debit_data['MemberId'] == user_id]
            total_p2p_volume = user_p2p['Amount (Rs)'].sum()
            total_p2p_count = len(user_p2p)
            
            # Get user name and contact if available
            user_name = df_filtered[df_filtered['MemberId'] == user_id]['Name'].iloc[0] if 'Name' in df.columns else 'N/A'
            user_contact = df_filtered[df_filtered['MemberId'] == user_id]['ContactNumber'].iloc[0] if 'ContactNumber' in df.columns else 'N/A'
            
            user_summaries.append({
                'MemberId': user_id,
                'Name': user_name,
                'Contact': user_contact,
                'Total Cash-In (Rs)': total_cashin_volume,
                'Cash-In Count': total_cashin_count,
                'Cash-In Modes Used': modes_used,
                'Top Cash-In Mode': top_mode,
                'Total P2P Debit (Rs)': total_p2p_volume,
                'P2P Debit Count': total_p2p_count,
                'Net Flow (CashIn - P2P)': total_cashin_volume - total_p2p_volume
            })
        
        power_users_df = pd.DataFrame(user_summaries)
        power_users_df = power_users_df.sort_values('Total Cash-In (Rs)', ascending=False)
        
        # Display metrics
        col1, col2, col3 = st.columns(3)
        col1.metric("👥 Power Users Found", f"{len(power_users):,}")
        col2.metric("💰 Total Cash-In by Power Users", f"Rs. {power_users_df['Total Cash-In (Rs)'].sum():,.2f}")
        col3.metric("💸 Total P2P Debit by Power Users", f"Rs. {power_users_df['Total P2P Debit (Rs)'].sum():,.2f}")
        
        # Top 20 Power Users Table
        st.write("### Top Power Users (Cash-In + P2P Debit)")
        st.dataframe(power_users_df.head(20).style.format({
            'Total Cash-In (Rs)': 'Rs. {:,.2f}',
            'Total P2P Debit (Rs)': 'Rs. {:,.2f}',
            'Net Flow (CashIn - P2P)': 'Rs. {:,.2f}'
        }), use_container_width=True)
        
        # Bar chart - Top 10 Power Users by Cash-In Volume
        fig_power = px.bar(power_users_df.head(10), 
                           x='Name', y='Total Cash-In (Rs)', 
                           title='Top 10 Power Users by Cash-In Volume',
                           color='Total Cash-In (Rs)',
                           text='Total Cash-In (Rs)',
                           hover_data=['MemberId', 'P2P Debit Count'])
        st.plotly_chart(fig_power, use_container_width=True)
        
        # Download button for Power Users
        csv_power = power_users_df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Power Users List as CSV", csv_power, "power_users.csv", "text/csv")
        
        # Optional: Select a specific user to see details
        st.write("### 🔍 Drill Down into Specific Power User")
        selected_user = st.selectbox("Select a User to View Details", power_users_df['MemberId'].head(20))
        if selected_user:
            user_details = df_filtered[df_filtered['MemberId'] == selected_user]
            
            # Separate cash-in and P2P debit for this user
            user_cashin_details = user_details[(user_details['Sign'] == 'Credit') & (user_details['Service'].isin(cash_in_services))]
            user_p2p_details = user_details[(user_details['Service'] == 'USER P2P') & (user_details['Sign'] == 'Debit')]
            
            st.write(f"#### Cash-In Transactions for User {selected_user}")
            if len(user_cashin_details) > 0:
                st.dataframe(user_cashin_details[['CreatedDate', 'Service', 'Amount (Rs)', 'Remarks']])
            else:
                st.info("No cash-in transactions")
            
            st.write(f"#### P2P Debit Transactions for User {selected_user}")
            if len(user_p2p_details) > 0:
                st.dataframe(user_p2p_details[['CreatedDate', 'Service', 'Amount (Rs)', 'Remarks']])
            else:
                st.info("No P2P debit transactions")
        
    else:
        st.info("No users found who do both Cash-In and P2P Debit transactions in the selected date range")
    
    # ============================================
    # EXISTING SECTIONS (Keep as is)
    # ============================================
    
    # Most used services
    st.subheader("📈 Most Used Services")
    col1, col2 = st.columns(2)
    
    service_count = df_filtered['Display Service'].value_counts().head(10).reset_index()
    service_count.columns = ['Service', 'Count']
    fig1 = px.bar(service_count, x='Service', y='Count', title='Top 10 by Transaction Count', color='Count')
    col1.plotly_chart(fig1, use_container_width=True)
    
    service_volume = df_filtered.groupby('Display Service')['Amount (Rs)'].sum().sort_values(ascending=False).head(10).reset_index()
    service_volume.columns = ['Service', 'Volume']
    fig2 = px.bar(service_volume, x='Service', y='Volume', title='Top 10 by Volume (Rs)', color='Volume')
    col2.plotly_chart(fig2, use_container_width=True)
    
    # User Lookup
    st.subheader("🔎 User Wallet Lookup")
    member_id_input = st.text_input("Enter MemberId or Phone Number")
    
    if member_id_input:
        user_data = df_filtered[
            (df_filtered['MemberId'].astype(str) == member_id_input) | 
            (df_filtered['ContactNumber'].astype(str).str.contains(member_id_input, na=False))
        ]
        
        if len(user_data) > 0:
            total_credit = user_data[user_data['Sign'] == 'Credit']['Amount (Rs)'].sum()
            total_debit = user_data[user_data['Sign'] == 'Debit']['Amount (Rs)'].sum()
            net_flow = total_credit - total_debit
            
            col1, col2, col3 = st.columns(3)
            col1.metric("💰 Total Credit", f"Rs. {total_credit:,.2f}")
            col2.metric("💸 Total Debit", f"Rs. {total_debit:,.2f}")
            col3.metric("📈 Net Flow", f"Rs. {net_flow:,.2f}")
            
            display_cols = ['CreatedDate', 'Display Service', 'Sign', 'Amount (Rs)', 'Available Balance(Rs)', 'Remarks', 'Gateway Status']
            st.dataframe(user_data[display_cols].sort_values('CreatedDate', ascending=False))
        else:
            st.warning("No transactions found")
    
    # Daily trend
    st.subheader("📅 Daily Transaction Trend")
    daily_trend = df_filtered.groupby(df_filtered['CreatedDate'].dt.date)['Amount (Rs)'].sum().reset_index()
    daily_trend.columns = ['Date', 'Volume']
    fig3 = px.line(daily_trend, x='Date', y='Volume', title='Total Daily Transaction Volume')
    st.plotly_chart(fig3, use_container_width=True)
    
    # Credit vs Debit
    st.subheader("💳 Credit vs Debit Analysis")
    sign_data = df_filtered.groupby('Sign')['Amount (Rs)'].sum().reset_index()
    fig_sign = px.pie(sign_data, values='Amount (Rs)', names='Sign', title='Total Volume: Credit vs Debit', hole=0.4)
    st.plotly_chart(fig_sign, use_container_width=True)
    
else:
    st.info("👈 Please upload your Excel file to get started")
