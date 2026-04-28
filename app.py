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

# Define Merchant Services (Debit transactions to merchants)
MERCHANT_SERVICES = [
    'MERCHANT CHECKOUT', 'MERCHANT LOAD', 'NEPALPAY QR PAYMENTS', 'FONEPAY QR PAYMENTS',
    'AIRLINES MYPAY', 'BUS SEWA', 'COMMUNITY KHANEPANI', 'CREDIT CARD PAYMENT',
    'INSURANCE ASIAN LIFE', 'INSURANCE CITIZEN LIFE', 'INSURANCE HIMALAYAN LIFE',
    'INSURANCE IME LIFE', 'INSURANCE NATIONAL LIFE', 'INSURANCE NEPAL LIFE',
    'INSURANCE PRABHU MAHALAXMI LIFE', 'INSURANCE RELIABLE LIFE', 'INSURANCE RELIANCE',
    'INSURANCE SUNLIFE', 'INTERNATIONALFLIGHT', 'INTERNET ADSL', 'INTERNET ARROWNET',
    'INTERNET DISHHOME FTTH', 'INTERNET NT FTTH', 'INTERNET SUBISU NEW',
    'INTERNET TECHMINDS', 'INTERNET VIANET', 'INTERNET WIFINEPAL', 'INTERNET WORLDLINK',
    'KBS SAMAJ', 'MORANG COMMUNITY ELECTRICITY', 'MyPay Events', 'Other Services',
    'PSTN LANDLINE', 'SADHAIN ON', 'SAMUDAYIK GRAMIN BIDHUT PANCHKHAL',
    'SAMUDAYIK GRAMIN BIDYUT SAHAKARI', 'SMART QR PAYMENT', 'SWARGADWARI COMMUNITY ELECTRICITY',
    'TV DISHHOME', 'TV MAXTV', 'TV PRABHUTV', 'TV SIMTV', 'Voting', 'XRsGame',
    'SHREE MAA BADIMALIKA GRAMIN BIDHUT SAHAKARI', 'INTERNET WEBSURFER', 'MeroShare',
    'Office of the Company Registrar', 'INTERNET CLASSICTECH', 'INSURANCE RASTRYA BEEMA SASTHAN',
    'BHATTARAI KULBANSHA', 'DOFE', 'Inland Revenue Department', 'Public Service Commission',
    'SOCIAL SECURITY FUND', 'Traffic fine', 'AMOUNT HOLD BY ADMIN', 'WALLETUPDATE BY ADMIN'
]

# Define Cash-In services
CASHIN_SERVICES = [
    'BANK TRANSFER', 'MERCHANT BANK LOAD', 'Mobile Banking', 'AGENT CASHIN',
    'AGENT CASHOUT', 'USER P2P', 'MERCHANT LOAD', 'NEPALPAY QR PAYMENTS',
    'FONEPAY QR PAYMENTS', 'CASHBACK', 'TRANSFER BY PHONE', 'DEPOSIT BY CONNECTIPS',
    'DEPOSIT BY LINKED BANK', 'CREDIT BY LINKED BANK', 'INTERNET BANKING',
    'AGENT P2P', 'WALLETUPDATE BY ADMIN', 'AMOUNT RELEASE FROM ADMIN'
]

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
    # MERCHANT PAYMENT ANALYSIS (Tabular Form)
    # ============================================
    st.subheader("🏪 Merchant Payment Analysis")
    
    # Filter merchant debit transactions
    merchant_data = df_filtered[
        (df_filtered['Sign'] == 'Debit') & 
        (df_filtered['Service'].isin(MERCHANT_SERVICES))
    ]
    
    if len(merchant_data) > 0:
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("🏪 Total Merchants", f"{merchant_data['Service'].nunique():,}")
        col2.metric("💳 Total Transactions", f"{len(merchant_data):,}")
        col3.metric("💰 Total Volume", f"Rs. {merchant_data['Amount (Rs)'].sum():,.2f}")
        col4.metric("👥 Unique Payers", f"{merchant_data['MemberId'].nunique():,}")
        
        # Merchant summary table
        merchant_summary = merchant_data.groupby('Service').agg({
            'TxnId': 'count',
            'Amount (Rs)': 'sum',
            'MemberId': 'nunique'
        }).reset_index()
        merchant_summary.columns = ['Merchant Name', 'Transaction Count', 'Total Volume (Rs)', 'Unique Users']
        merchant_summary = merchant_summary.sort_values('Total Volume (Rs)', ascending=False)
        
        # Add rank columns
        merchant_summary['Rank by Volume'] = merchant_summary['Total Volume (Rs)'].rank(ascending=False).astype(int)
        merchant_summary['Rank by Count'] = merchant_summary['Transaction Count'].rank(ascending=False).astype(int)
        
        # Calculate average transaction value
        merchant_summary['Avg Transaction (Rs)'] = merchant_summary['Total Volume (Rs)'] / merchant_summary['Transaction Count']
        
        # Display main merchant table
        st.write("### 📋 Merchant Payment Summary Table")
        st.dataframe(
            merchant_summary[['Rank by Volume', 'Merchant Name', 'Transaction Count', 'Total Volume (Rs)', 'Avg Transaction (Rs)', 'Unique Users', 'Rank by Count']].head(50),
            use_container_width=True,
            column_config={
                'Rank by Volume': st.column_config.NumberColumn('Rank', width='small'),
                'Merchant Name': st.column_config.TextColumn('Merchant', width='large'),
                'Transaction Count': st.column_config.NumberColumn('Count', format='%d'),
                'Total Volume (Rs)': st.column_config.NumberColumn('Total Volume', format='Rs. %.2f'),
                'Avg Transaction (Rs)': st.column_config.NumberColumn('Avg Transaction', format='Rs. %.2f'),
                'Unique Users': st.column_config.NumberColumn('Unique Users', format='%d'),
                'Rank by Count': st.column_config.NumberColumn('Count Rank', width='small')
            }
        )
        
        # Tabs for different views
        tab1, tab2, tab3 = st.tabs(["📊 Top by Volume", "📈 Top by Count", "👥 Top by Users"])
        
        with tab1:
            st.write("### Top 20 Merchants by Transaction Volume")
            st.dataframe(
                merchant_summary[['Merchant Name', 'Total Volume (Rs)', 'Transaction Count', 'Avg Transaction (Rs)']].head(20).style.format({
                    'Total Volume (Rs)': 'Rs. {:,.2f}',
                    'Transaction Count': '{:,}',
                    'Avg Transaction (Rs)': 'Rs. {:,.2f}'
                }),
                use_container_width=True
            )
        
        with tab2:
            st.write("### Top 20 Merchants by Transaction Count")
            st.dataframe(
                merchant_summary.sort_values('Transaction Count', ascending=False)[['Merchant Name', 'Transaction Count', 'Total Volume (Rs)', 'Avg Transaction (Rs)']].head(20).style.format({
                    'Total Volume (Rs)': 'Rs. {:,.2f}',
                    'Transaction Count': '{:,}',
                    'Avg Transaction (Rs)': 'Rs. {:,.2f}'
                }),
                use_container_width=True
            )
        
        with tab3:
            st.write("### Top 20 Merchants by Unique Users")
            st.dataframe(
                merchant_summary.sort_values('Unique Users', ascending=False)[['Merchant Name', 'Unique Users', 'Transaction Count', 'Total Volume (Rs)']].head(20).style.format({
                    'Total Volume (Rs)': 'Rs. {:,.2f}',
                    'Transaction Count': '{:,}',
                    'Unique Users': '{:,}'
                }),
                use_container_width=True
            )
        
        # Download full merchant summary
        csv_merchant = merchant_summary.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Complete Merchant Summary (CSV)", csv_merchant, "merchant_summary.csv", "text/csv")
        
        # Top Paying Users
        st.write("### 💎 Top Paying Users (Highest Merchant Payment Volume)")
        top_paying_users = merchant_data.groupby('MemberId').agg({
            'Amount (Rs)': 'sum',
            'TxnId': 'count',
            'Service': lambda x: x.nunique()
        }).reset_index()
        top_paying_users.columns = ['MemberId', 'Total Paid (Rs)', 'Transaction Count', 'Unique Merchants']
        
        # Add user names and contacts
        if 'Name' in df.columns:
            name_map = df_filtered.groupby('MemberId')['Name'].first().to_dict()
            top_paying_users['Name'] = top_paying_users['MemberId'].map(name_map)
        else:
            top_paying_users['Name'] = 'N/A'
        
        if 'ContactNumber' in df.columns:
            contact_map = df_filtered.groupby('MemberId')['ContactNumber'].first().to_dict()
            top_paying_users['Contact'] = top_paying_users['MemberId'].map(contact_map)
        else:
            top_paying_users['Contact'] = 'N/A'
        
        top_paying_users = top_paying_users.sort_values('Total Paid (Rs)', ascending=False)
        
        st.dataframe(
            top_paying_users[['MemberId', 'Name', 'Contact', 'Total Paid (Rs)', 'Transaction Count', 'Unique Merchants']].head(30).style.format({
                'Total Paid (Rs)': 'Rs. {:,.2f}',
                'Transaction Count': '{:,}',
                'Unique Merchants': '{:,}'
            }),
            use_container_width=True
        )
        
        # Daily merchant payment trend (simple chart)
        st.write("### 📅 Daily Merchant Payment Trend")
        daily_merchant = merchant_data.groupby(merchant_data['CreatedDate'].dt.date)['Amount (Rs)'].sum().reset_index()
        daily_merchant.columns = ['Date', 'Merchant Volume']
        fig_daily = px.line(daily_merchant, x='Date', y='Merchant Volume', title='Daily Merchant Payment Volume', markers=True)
        st.plotly_chart(fig_daily, use_container_width=True)
        
    else:
        st.info("No merchant payment transactions found in selected date range")
    
    # ============================================
    # CASH-IN MODES ANALYSIS
    # ============================================
    st.subheader("💰 Cash-In Analysis by Mode")
    
    cash_in_data = df_filtered[
        (df_filtered['Sign'] == 'Credit') & 
        (df_filtered['Service'].isin(CASHIN_SERVICES))
    ]
    
    if len(cash_in_data) > 0:
        cash_in_summary = cash_in_data.groupby('Service').agg({
            'TxnId': 'count',
            'Amount (Rs)': 'sum'
        }).reset_index()
        cash_in_summary.columns = ['Cash-In Mode', 'Transaction Count', 'Total Volume (Rs)']
        cash_in_summary = cash_in_summary.sort_values('Total Volume (Rs)', ascending=False)
        
        col1, col2 = st.columns(2)
        fig_count = px.bar(cash_in_summary.head(10), x='Cash-In Mode', y='Transaction Count', title='Top 10 Cash-In Modes by Transaction Count', color='Transaction Count', text='Transaction Count')
        fig_count.update_layout(xaxis_tickangle=-45)
        col1.plotly_chart(fig_count, use_container_width=True)
        
        fig_volume = px.bar(cash_in_summary.head(10), x='Cash-In Mode', y='Total Volume (Rs)', title='Top 10 Cash-In Modes by Volume (Rs)', color='Total Volume (Rs)', text='Total Volume (Rs)')
        fig_volume.update_layout(xaxis_tickangle=-45)
        col2.plotly_chart(fig_volume, use_container_width=True)
        
        st.write("### 📋 Cash-In Modes Summary Table")
        st.dataframe(
            cash_in_summary.style.format({
                'Transaction Count': '{:,}',
                'Total Volume (Rs)': 'Rs. {:,.2f}'
            }),
            use_container_width=True
        )
        
        csv_cashin = cash_in_summary.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Cash-In Summary as CSV", csv_cashin, "cashin_summary.csv", "text/csv")
    else:
        st.info("No Cash-In transactions found")
    
    # ============================================
    # POWER USERS (Cash-In + P2P Debit)
    # ============================================
    st.subheader("👑 Top Power Users (Cash-In + P2P Debit)")
    
    cashin_users = set(cash_in_data['MemberId'].unique())
    p2p_debit_data = df_filtered[(df_filtered['Service'] == 'USER P2P') & (df_filtered['Sign'] == 'Debit')]
    p2p_debit_users = set(p2p_debit_data['MemberId'].unique())
    power_users = cashin_users.intersection(p2p_debit_users)
    
    if len(power_users) > 0:
        user_summaries = []
        for user_id in power_users:
            user_cashin = cash_in_data[cash_in_data['MemberId'] == user_id]
            user_p2p = p2p_debit_data[p2p_debit_data['MemberId'] == user_id]
            
            user_name = df_filtered[df_filtered['MemberId'] == user_id]['Name'].iloc[0] if 'Name' in df.columns else 'N/A'
            user_contact = df_filtered[df_filtered['MemberId'] == user_id]['ContactNumber'].iloc[0] if 'ContactNumber' in df.columns else 'N/A'
            
            user_summaries.append({
                'MemberId': user_id,
                'Name': user_name,
                'Contact': user_contact,
                'Total Cash-In (Rs)': user_cashin['Amount (Rs)'].sum(),
                'Cash-In Count': len(user_cashin),
                'Total P2P Debit (Rs)': user_p2p['Amount (Rs)'].sum(),
                'P2P Debit Count': len(user_p2p),
                'Net Flow (Rs)': user_cashin['Amount (Rs)'].sum() - user_p2p['Amount (Rs)'].sum()
            })
        
        power_users_df = pd.DataFrame(user_summaries).sort_values('Total Cash-In (Rs)', ascending=False)
        
        col1, col2, col3 = st.columns(3)
        col1.metric("👥 Power Users", f"{len(power_users):,}")
        col2.metric("💰 Total Cash-In", f"Rs. {power_users_df['Total Cash-In (Rs)'].sum():,.2f}")
        col3.metric("💸 Total P2P Debit", f"Rs. {power_users_df['Total P2P Debit (Rs)'].sum():,.2f}")
        
        st.dataframe(
            power_users_df.head(20).style.format({
                'Total Cash-In (Rs)': 'Rs. {:,.2f}',
                'Cash-In Count': '{:,}',
                'Total P2P Debit (Rs)': 'Rs. {:,.2f}',
                'P2P Debit Count': '{:,}',
                'Net Flow (Rs)': 'Rs. {:,.2f}'
            }),
            use_container_width=True
        )
        
        csv_power = power_users_df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Power Users as CSV", csv_power, "power_users.csv", "text/csv")
    else:
        st.info("No power users found in selected date range")
    
    # ============================================
    # USER LOOKUP
    # ============================================
    st.subheader("🔎 User Wallet Lookup")
    
    search_input = st.text_input("Enter MemberId, Phone Number, or Name")
    
    if search_input:
        search_lower = search_input.lower()
        user_data = df_filtered[
            (df_filtered['MemberId'].astype(str) == search_input) | 
            (df_filtered['ContactNumber'].astype(str).str.contains(search_input, na=False)) |
            (df_filtered['Name'].astype(str).str.lower().str.contains(search_lower, na=False))
        ]
        
        if len(user_data) > 0:
            # User summary
            user_name = user_data['Name'].iloc[0] if 'Name' in user_data.columns else 'N/A'
            user_contact = user_data['ContactNumber'].iloc[0] if 'ContactNumber' in user_data.columns else 'N/A'
            user_member_id = user_data['MemberId'].iloc[0]
            
            st.write(f"### User: {user_name}")
            st.write(f"**Member ID:** {user_member_id} | **Contact:** {user_contact}")
            
            total_credit = user_data[user_data['Sign'] == 'Credit']['Amount (Rs)'].sum()
            total_debit = user_data[user_data['Sign'] == 'Debit']['Amount (Rs)'].sum()
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("💰 Total Credit", f"Rs. {total_credit:,.2f}")
            col2.metric("💸 Total Debit", f"Rs. {total_debit:,.2f}")
            col3.metric("📈 Net Flow", f"Rs. {total_credit - total_debit:,.2f}")
            col4.metric("📦 Transactions", f"{len(user_data):,}")
            
            # Show transactions
            st.write("### 📋 Transaction History")
            display_cols = ['CreatedDate', 'Display Service', 'Sign', 'Amount (Rs)', 'Available Balance(Rs)', 'Remarks', 'Gateway Status']
            available_cols = [col for col in display_cols if col in user_data.columns]
            st.dataframe(user_data[available_cols].sort_values('CreatedDate', ascending=False), use_container_width=True)
            
            # Download user data
            csv_user = user_data.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download User Transactions as CSV", csv_user, f"user_{user_member_id}_transactions.csv", "text/csv")
        else:
            st.warning("No transactions found for this search")
    
    # ============================================
    # OVERALL SERVICE CHARTS
    # ============================================
    st.subheader("📈 Most Used Services (Overall)")
    col1, col2 = st.columns(2)
    
    service_count = df_filtered['Display Service'].value_counts().head(10).reset_index()
    service_count.columns = ['Service', 'Count']
    fig1 = px.bar(service_count, x='Service', y='Count', title='Top 10 by Transaction Count', color='Count')
    fig1.update_layout(xaxis_tickangle=-45)
    col1.plotly_chart(fig1, use_container_width=True)
    
    service_volume = df_filtered.groupby('Display Service')['Amount (Rs)'].sum().sort_values(ascending=False).head(10).reset_index()
    service_volume.columns = ['Service', 'Volume']
    fig2 = px.bar(service_volume, x='Service', y='Volume', title='Top 10 by Volume (Rs)', color='Volume')
    fig2.update_layout(xaxis_tickangle=-45)
    col2.plotly_chart(fig2, use_container_width=True)
    
    # Daily trend
    st.subheader("📅 Daily Transaction Trend")
    daily_trend = df_filtered.groupby(df_filtered['CreatedDate'].dt.date)['Amount (Rs)'].sum().reset_index()
    daily_trend.columns = ['Date', 'Volume']
    fig3 = px.line(daily_trend, x='Date', y='Volume', title='Total Daily Transaction Volume', markers=True)
    st.plotly_chart(fig3, use_container_width=True)
    
    # Footer with date range info
    st.caption(f"📅 Data from {start_date.date()} to {end_date.date()} | Total rows: {len(df_filtered):,}")
    
else:
    st.info("👈 Please upload your Excel file to get started")
