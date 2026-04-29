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

# Define Transaction Categories for Report
TRANSACTION_CATEGORIES = {
    'Cash in': ['BANK TRANSFER', 'MERCHANT BANK LOAD', 'Mobile Banking', 'AGENT CASHIN',
                'AGENT CASHOUT', 'USER P2P', 'MERCHANT LOAD', 'NEPALPAY QR PAYMENTS',
                'FONEPAY QR PAYMENTS', 'CASHBACK', 'TRANSFER BY PHONE', 'DEPOSIT BY CONNECTIPS',
                'DEPOSIT BY LINKED BANK', 'CREDIT BY LINKED BANK', 'INTERNET BANKING',
                'AGENT P2P', 'WALLETUPDATE BY ADMIN', 'AMOUNT RELEASE FROM ADMIN', 'Credit'],
    
    'Government payment (P2G)': ['DOFE', 'Inland Revenue Department', 'Public Service Commission',
                                  'SOCIAL SECURITY FUND', 'Traffic fine', 'KUKL', 'No Objection Certificate'],
    
    'Merchant payment': ['MERCHANT CHECKOUT', 'MERCHANT LOAD', 'NEPALPAY QR PAYMENTS', 'FONEPAY QR PAYMENTS',
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
                          'TV DISHHOME', 'TV MAXTV', 'TV PRABHUTV', 'TV SIMTV', 'Voting', 'XRsGame'],
    
    'Topup': ['NCELL', 'NTC', 'DATAPACK NCELL', 'DATAPACK NTC', 'VOICEPACK NCELL', 'VOICEPACK NTC',
              'COMBOPACK NTC', 'RECOMMENDEDPACK NCELL', 'RECOMMENDPACK NTC', 'SMSPACK NTC', 'NPL Pack'],
    
    'Transfer to bank A/C (P2P)': ['BANK TRANSFER', 'MYBANK BANK TRANSFER']
}

# Define Merchant Services
MERCHANT_SERVICES = []
for cat in ['Merchant payment', 'Government payment (P2G)', 'Topup']:
    MERCHANT_SERVICES.extend(TRANSACTION_CATEGORIES[cat])

# Define Cash-In services
CASHIN_SERVICES = TRANSACTION_CATEGORIES['Cash in']

# Define Bank Transfer Out services
BANK_TRANSFER_SERVICES = TRANSACTION_CATEGORIES['Transfer to bank A/C (P2P)']

def get_display_name(service, sign):
    key = (service, sign)
    if key in SERVICE_MAPPING:
        return SERVICE_MAPPING[key]
    if sign == 'Credit':
        return f"💰 {service}"
    else:
        return f"💸 {service}"

def get_value_range(amount):
    if amount <= 1000:
        return 'Up to 1000'
    elif amount <= 5000:
        return '1001 to 5000'
    elif amount <= 10000:
        return '5001 to 10000'
    elif amount <= 20000:
        return '10001 to 20000'
    elif amount <= 25000:
        return '20001 to 25000'
    else:
        return 'greater than 25000'

def get_transaction_category(service, sign):
    for category, services in TRANSACTION_CATEGORIES.items():
        if service in services and sign == 'Credit' and category == 'Cash in':
            return category
        elif service in services and sign == 'Debit' and category == 'Transfer to bank A/C (P2P)':
            return category
        elif service in services and sign == 'Debit' and category == 'Government payment (P2G)':
            return category
        elif service in services and sign == 'Debit' and category == 'Merchant payment':
            return category
        elif service in services and sign == 'Debit' and category == 'Topup':
            return category
    return '#N/A'

# File uploaders
st.sidebar.header("📁 Upload Files")

uploaded_file = st.sidebar.file_uploader("Upload Transaction Excel File", type=["xlsx", "xls"])
agent_file = st.sidebar.file_uploader("Upload Agent List Excel File (Optional)", type=["xlsx", "xls"])

@st.cache_data
def load_transaction_data(file):
    df = pd.read_excel(file)
    df['CreatedDate'] = pd.to_datetime(df['CreatedDate'], errors='coerce')
    df['Display Service'] = df.apply(
        lambda row: get_display_name(row.get('Service', ''), row.get('Sign', '')), 
        axis=1
    )
    return df

@st.cache_data
def load_agent_list(file):
    if file is not None:
        df = pd.read_excel(file)
        
        # Try to find the Agent code column
        agent_col = None
        for col in df.columns:
            col_lower = col.lower()
            if 'agent code' in col_lower or 'agent_code' in col_lower or 'agent' in col_lower:
                agent_col = col
                break
            elif 'contact' in col_lower or 'phone' in col_lower or 'mobile' in col_lower:
                agent_col = col
                break
        
        if agent_col is None:
            agent_col = df.columns[0]
        
        # Get agent identifiers (Contact numbers)
        agent_ids = set(df[agent_col].astype(str).str.strip().unique())
        
        # Get agent names if available
        agent_names = {}
        name_col = None
        for col in df.columns:
            if 'name' in col.lower():
                name_col = col
                break
        
        if name_col:
            agent_names = df.set_index(agent_col)[name_col].to_dict()
        
        return agent_ids, agent_names, agent_col
    
    return set(), {}, None

if uploaded_file is not None:
    # Load data
    df = load_transaction_data(uploaded_file)
    agent_ids, agent_names, agent_col = load_agent_list(agent_file)
    
    # Prepare ContactNumber for matching
    if 'ContactNumber' in df.columns:
        df['ContactNumber_clean'] = df['ContactNumber'].astype(str).str.strip()
    else:
        st.warning("⚠️ 'ContactNumber' column not found. Agent matching will not work.")
        df['ContactNumber_clean'] = ''
    
    # Add User Type column
    if agent_ids:
        df['User Type'] = df['ContactNumber_clean'].apply(
            lambda x: 'Agent' if x in agent_ids else 'User'
        )
    else:
        df['User Type'] = 'User'
    
    # Add Agent Name if available
    if agent_names:
        df['Agent Name'] = df['ContactNumber_clean'].map(agent_names).fillna('')
    
    # Add Value Range column
    df['Value Range'] = df['Amount (Rs)'].apply(get_value_range)
    
    # Add Transaction Category column
    df['Transaction Category'] = df.apply(
        lambda row: get_transaction_category(row.get('Service', ''), row.get('Sign', '')),
        axis=1
    )
    
    # Sidebar filters
    st.sidebar.header("🔍 Filters")
    min_date = df['CreatedDate'].min().date()
    max_date = df['CreatedDate'].max().date()
    
    start_date = st.sidebar.date_input("Start Date", min_date, min_value=min_date, max_value=max_date)
    end_date = st.sidebar.date_input("End Date", max_date, min_value=min_date, max_value=max_date)
    
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    df_filtered = df[(df['CreatedDate'] >= start_date) & (df['CreatedDate'] <= end_date)]
    
    # ============================================
    # TOP METRICS
    # ============================================
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("💰 Total Volume (Rs)", f"{df_filtered['Amount (Rs)'].sum():,.2f}")
    col2.metric("📦 Total Transactions", f"{len(df_filtered):,}")
    col3.metric("👥 Unique Users", df_filtered['MemberId'].nunique())
    success_rate = (df_filtered['Gateway Status'].eq('Success').mean() * 100) if 'Gateway Status' in df.columns else 0
    col4.metric("✅ Success Rate", f"{success_rate:.1f}%")
    
    # ============================================
    # NEW SECTION: AGENT/USER SEGMENTATION REPORT
    # ============================================
    st.subheader("📊 Agent vs User Transaction Report (by Value Range)")
    
    if agent_ids:
        matching_agents = agent_ids.intersection(set(df['ContactNumber_clean'].unique()))
        st.success(f"✅ Agent list loaded with {len(agent_ids):,} agents | Found {len(matching_agents):,} agents with transactions")
    else:
        st.info("ℹ️ No agent list uploaded. Upload an agent list Excel file to enable Agent/User segmentation.")
    
    # Filter relevant transactions for the report
    report_transactions = df_filtered[
        ((df_filtered['Transaction Category'] == 'Cash in') & (df_filtered['Sign'] == 'Credit')) |
        ((df_filtered['Transaction Category'] == 'Transfer to bank A/C (P2P)') & (df_filtered['Sign'] == 'Debit')) |
        ((df_filtered['Transaction Category'] == 'Government payment (P2G)') & (df_filtered['Sign'] == 'Debit')) |
        ((df_filtered['Transaction Category'] == 'Merchant payment') & (df_filtered['Sign'] == 'Debit')) |
        ((df_filtered['Transaction Category'] == 'Topup') & (df_filtered['Sign'] == 'Debit'))
    ]
    
    if len(report_transactions) > 0:
        # Create pivot table report
        report_data = report_transactions.groupby(['User Type', 'Value Range', 'Transaction Category']).agg({
            'Amount (Rs)': ['count', 'sum']
        }).reset_index()
        
        report_data.columns = ['User Type', 'Value Range', 'Transaction Category', 'Transaction Count', 'Total Amount (Rs)']
        
        pivot_report = report_data.pivot_table(
            index=['User Type', 'Value Range'],
            columns='Transaction Category',
            values=['Transaction Count', 'Total Amount (Rs)'],
            fill_value=0
        )
        
        pivot_report.columns = [f'{col[1]}_{col[0]}' for col in pivot_report.columns]
        pivot_report = pivot_report.reset_index()
        
        expected_categories = ['Cash in', 'Government payment (P2G)', 'Merchant payment', 'Topup', 'Transfer to bank A/C (P2P)']
        for cat in expected_categories:
            if f'{cat}_Transaction Count' not in pivot_report.columns:
                pivot_report[f'{cat}_Transaction Count'] = 0
            if f'{cat}_Total Amount (Rs)' not in pivot_report.columns:
                pivot_report[f'{cat}_Total Amount (Rs)'] = 0
        
        pivot_report['Total Transaction Count'] = pivot_report[[f'{cat}_Transaction Count' for cat in expected_categories]].sum(axis=1)
        pivot_report['Total Amount (Rs)'] = pivot_report[[f'{cat}_Total Amount (Rs)' for cat in expected_categories]].sum(axis=1)
        
        range_order = ['Up to 1000', '1001 to 5000', '5001 to 10000', '10001 to 20000', '20001 to 25000', 'greater than 25000']
        pivot_report['Value Range'] = pd.Categorical(pivot_report['Value Range'], categories=range_order, ordered=True)
        pivot_report = pivot_report.sort_values(['User Type', 'Value Range'])
        
        # Display Agent section
        st.write("#### 👨‍💼 AGENTS")
        agent_report = pivot_report[pivot_report['User Type'] == 'Agent']
        if len(agent_report) > 0:
            st.dataframe(
                agent_report[['Value Range', 'Cash in_Transaction Count', 'Cash in_Total Amount (Rs)',
                              'Government payment (P2G)_Transaction Count', 'Government payment (P2G)_Total Amount (Rs)',
                              'Merchant payment_Transaction Count', 'Merchant payment_Total Amount (Rs)',
                              'Topup_Transaction Count', 'Topup_Total Amount (Rs)',
                              'Transfer to bank A/C (P2P)_Transaction Count', 'Transfer to bank A/C (P2P)_Total Amount (Rs)',
                              'Total Transaction Count', 'Total Amount (Rs)']].style.format({
                                'Cash in_Total Amount (Rs)': 'Rs. {:,.2f}',
                                'Government payment (P2G)_Total Amount (Rs)': 'Rs. {:,.2f}',
                                'Merchant payment_Total Amount (Rs)': 'Rs. {:,.2f}',
                                'Topup_Total Amount (Rs)': 'Rs. {:,.2f}',
                                'Transfer to bank A/C (P2P)_Total Amount (Rs)': 'Rs. {:,.2f}',
                                'Total Amount (Rs)': 'Rs. {:,.2f}'
                              }),
                use_container_width=True
            )
        else:
            st.info("No Agent transactions in selected date range")
        
        # Display User section
        st.write("#### 👤 USERS")
        user_report = pivot_report[pivot_report['User Type'] == 'User']
        if len(user_report) > 0:
            st.dataframe(
                user_report[['Value Range', 'Cash in_Transaction Count', 'Cash in_Total Amount (Rs)',
                             'Government payment (P2G)_Transaction Count', 'Government payment (P2G)_Total Amount (Rs)',
                             'Merchant payment_Transaction Count', 'Merchant payment_Total Amount (Rs)',
                             'Topup_Transaction Count', 'Topup_Total Amount (Rs)',
                             'Transfer to bank A/C (P2P)_Transaction Count', 'Transfer to bank A/C (P2P)_Total Amount (Rs)',
                             'Total Transaction Count', 'Total Amount (Rs)']].style.format({
                                'Cash in_Total Amount (Rs)': 'Rs. {:,.2f}',
                                'Government payment (P2G)_Total Amount (Rs)': 'Rs. {:,.2f}',
                                'Merchant payment_Total Amount (Rs)': 'Rs. {:,.2f}',
                                'Topup_Total Amount (Rs)': 'Rs. {:,.2f}',
                                'Transfer to bank A/C (P2P)_Total Amount (Rs)': 'Rs. {:,.2f}',
                                'Total Amount (Rs)': 'Rs. {:,.2f}'
                              }),
                use_container_width=True
            )
        else:
            st.info("No User transactions in selected date range")
        
        # Grand Total
        st.write("#### 📊 GRAND TOTAL")
        grand_total_by_category = {}
        for cat in expected_categories:
            grand_total_by_category[f'{cat}_Transaction Count'] = pivot_report[f'{cat}_Transaction Count'].sum()
            grand_total_by_category[f'{cat}_Total Amount (Rs)'] = pivot_report[f'{cat}_Total Amount (Rs)'].sum()
        
        grand_df = pd.DataFrame([
            {'Category': 'Cash in', 'Transaction Count': grand_total_by_category.get('Cash in_Transaction Count', 0), 'Total Amount (Rs)': grand_total_by_category.get('Cash in_Total Amount (Rs)', 0)},
            {'Category': 'Government payment (P2G)', 'Transaction Count': grand_total_by_category.get('Government payment (P2G)_Transaction Count', 0), 'Total Amount (Rs)': grand_total_by_category.get('Government payment (P2G)_Total Amount (Rs)', 0)},
            {'Category': 'Merchant payment', 'Transaction Count': grand_total_by_category.get('Merchant payment_Transaction Count', 0), 'Total Amount (Rs)': grand_total_by_category.get('Merchant payment_Total Amount (Rs)', 0)},
            {'Category': 'Topup', 'Transaction Count': grand_total_by_category.get('Topup_Transaction Count', 0), 'Total Amount (Rs)': grand_total_by_category.get('Topup_Total Amount (Rs)', 0)},
            {'Category': 'Transfer to bank A/C (P2P)', 'Transaction Count': grand_total_by_category.get('Transfer to bank A/C (P2P)_Transaction Count', 0), 'Total Amount (Rs)': grand_total_by_category.get('Transfer to bank A/C (P2P)_Total Amount (Rs)', 0)}
        ])
        
        col1, col2 = st.columns(2)
        with col1:
            st.dataframe(grand_df.style.format({'Transaction Count': '{:,}', 'Total Amount (Rs)': 'Rs. {:,.2f}'}), use_container_width=True)
        with col2:
            st.metric("📦 Total Transactions", f"{pivot_report['Total Transaction Count'].sum():,.0f}")
            st.metric("💰 Total Volume", f"Rs. {pivot_report['Total Amount (Rs)'].sum():,.2f}")
        
        # Download report
        export_agent = agent_report.copy() if len(agent_report) > 0 else pd.DataFrame()
        export_user = user_report.copy() if len(user_report) > 0 else pd.DataFrame()
        if len(export_agent) > 0:
            export_agent['User Type'] = 'Agent'
        if len(export_user) > 0:
            export_user['User Type'] = 'User'
        export_df = pd.concat([export_agent, export_user]) if len(export_agent) > 0 or len(export_user) > 0 else pd.DataFrame()
        
        if len(export_df) > 0:
            csv_report = export_df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download Agent/User Report (CSV)", csv_report, f"agent_user_report.csv", "text/csv")
    
    # ============================================
    # TTR REPORTING - High Value Users (Total Volume > 10 Lakhs)
    # ============================================
    st.subheader("📋 TTR Reporting - High Value Users (Total Debit + Credit > Rs. 10,00,000)")
    
    user_credit_summary = df_filtered[df_filtered['Sign'] == 'Credit'].groupby('MemberId')['Amount (Rs)'].sum().reset_index()
    user_credit_summary.columns = ['MemberId', 'Total Credit (Rs)']
    user_debit_summary = df_filtered[df_filtered['Sign'] == 'Debit'].groupby('MemberId')['Amount (Rs)'].sum().reset_index()
    user_debit_summary.columns = ['MemberId', 'Total Debit (Rs)']
    
    ttr_report = pd.merge(user_credit_summary, user_debit_summary, on='MemberId', how='outer').fillna(0)
    
    if 'Name' in df.columns:
        name_map = df_filtered.groupby('MemberId')['Name'].first().to_dict()
        ttr_report['Name'] = ttr_report['MemberId'].map(name_map)
    else:
        ttr_report['Name'] = 'N/A'
    
    if 'ContactNumber' in df.columns:
        contact_map = df_filtered.groupby('MemberId')['ContactNumber'].first().to_dict()
        ttr_report['Contact'] = ttr_report['MemberId'].map(contact_map)
    else:
        ttr_report['Contact'] = 'N/A'
    
    ttr_report['Total Volume (Rs)'] = ttr_report['Total Credit (Rs)'] + ttr_report['Total Debit (Rs)']
    ttr_report['Net Flow (Rs)'] = ttr_report['Total Credit (Rs)'] - ttr_report['Total Debit (Rs)']
    
    HIGH_VALUE_THRESHOLD = 1000000
    high_value_users = ttr_report[ttr_report['Total Volume (Rs)'] > HIGH_VALUE_THRESHOLD]
    high_value_users = high_value_users.sort_values('Total Volume (Rs)', ascending=False)
    
    if len(high_value_users) > 0:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("⚠️ High Value Users", f"{len(high_value_users):,}")
        col2.metric("💰 Total Credit", f"Rs. {high_value_users['Total Credit (Rs)'].sum():,.2f}")
        col3.metric("💸 Total Debit", f"Rs. {high_value_users['Total Debit (Rs)'].sum():,.2f}")
        col4.metric("📊 Total Volume", f"Rs. {high_value_users['Total Volume (Rs)'].sum():,.2f}")
        
        st.dataframe(high_value_users[['MemberId', 'Name', 'Contact', 'Total Credit (Rs)', 'Total Debit (Rs)', 'Total Volume (Rs)', 'Net Flow (Rs)']].head(100).style.format({
            'Total Credit (Rs)': 'Rs. {:,.2f}', 'Total Debit (Rs)': 'Rs. {:,.2f}',
            'Total Volume (Rs)': 'Rs. {:,.2f}', 'Net Flow (Rs)': 'Rs. {:,.2f}'
        }), use_container_width=True)
        
        csv_ttr = high_value_users.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download TTR Report (CSV)", csv_ttr, f"ttr_report.csv", "text/csv")
    else:
        st.info(f"No users found with total transaction volume exceeding Rs. {HIGH_VALUE_THRESHOLD:,}")
    
    # ============================================
    # MERCHANT PAYMENT ANALYSIS
    # ============================================
    st.subheader("🏪 Merchant Payment Analysis")
    
    merchant_data = df_filtered[(df_filtered['Sign'] == 'Debit') & (df_filtered['Service'].isin(MERCHANT_SERVICES))]
    
    if len(merchant_data) > 0:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("🏪 Total Merchants", f"{merchant_data['Service'].nunique():,}")
        col2.metric("💳 Total Transactions", f"{len(merchant_data):,}")
        col3.metric("💰 Total Volume", f"Rs. {merchant_data['Amount (Rs)'].sum():,.2f}")
        col4.metric("👥 Unique Payers", f"{merchant_data['MemberId'].nunique():,}")
        
        merchant_summary = merchant_data.groupby('Service').agg({'TxnId': 'count', 'Amount (Rs)': 'sum', 'MemberId': 'nunique'}).reset_index()
        merchant_summary.columns = ['Merchant Name', 'Transaction Count', 'Total Volume (Rs)', 'Unique Users']
        merchant_summary = merchant_summary.sort_values('Total Volume (Rs)', ascending=False)
        merchant_summary['Rank by Volume'] = merchant_summary['Total Volume (Rs)'].rank(ascending=False).astype(int)
        merchant_summary['Avg Transaction (Rs)'] = merchant_summary['Total Volume (Rs)'] / merchant_summary['Transaction Count']
        
        st.dataframe(merchant_summary[['Rank by Volume', 'Merchant Name', 'Transaction Count', 'Total Volume (Rs)', 'Avg Transaction (Rs)', 'Unique Users']].head(50).style.format({
            'Total Volume (Rs)': 'Rs. {:,.2f}', 'Avg Transaction (Rs)': 'Rs. {:,.2f}'
        }), use_container_width=True)
        
        csv_merchant = merchant_summary.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Merchant Summary (CSV)", csv_merchant, "merchant_summary.csv", "text/csv")
        
        # Top Paying Users
        st.write("### 💎 Top Paying Users")
        top_paying_users = merchant_data.groupby('MemberId').agg({'Amount (Rs)': 'sum', 'TxnId': 'count', 'Service': lambda x: x.nunique()}).reset_index()
        top_paying_users.columns = ['MemberId', 'Total Paid (Rs)', 'Transaction Count', 'Unique Merchants']
        if 'Name' in df.columns:
            name_map = df_filtered.groupby('MemberId')['Name'].first().to_dict()
            top_paying_users['Name'] = top_paying_users['MemberId'].map(name_map)
        top_paying_users = top_paying_users.sort_values('Total Paid (Rs)', ascending=False)
        st.dataframe(top_paying_users.head(30).style.format({'Total Paid (Rs)': 'Rs. {:,.2f}'}), use_container_width=True)
    else:
        st.info("No merchant payment transactions found")
    
    # ============================================
    # CASH-IN MODES ANALYSIS
    # ============================================
    st.subheader("💰 Cash-In Analysis by Mode")
    
    cash_in_data = df_filtered[(df_filtered['Sign'] == 'Credit') & (df_filtered['Service'].isin(CASHIN_SERVICES))]
    
    if len(cash_in_data) > 0:
        cash_in_summary = cash_in_data.groupby('Service').agg({'TxnId': 'count', 'Amount (Rs)': 'sum'}).reset_index()
        cash_in_summary.columns = ['Cash-In Mode', 'Transaction Count', 'Total Volume (Rs)']
        cash_in_summary = cash_in_summary.sort_values('Total Volume (Rs)', ascending=False)
        
        col1, col2 = st.columns(2)
        fig_count = px.bar(cash_in_summary.head(10), x='Cash-In Mode', y='Transaction Count', title='Top 10 Cash-In Modes by Count', color='Transaction Count')
        col1.plotly_chart(fig_count, use_container_width=True)
        fig_volume = px.bar(cash_in_summary.head(10), x='Cash-In Mode', y='Total Volume (Rs)', title='Top 10 Cash-In Modes by Volume', color='Total Volume (Rs)')
        col2.plotly_chart(fig_volume, use_container_width=True)
        
        st.dataframe(cash_in_summary.style.format({'Transaction Count': '{:,}', 'Total Volume (Rs)': 'Rs. {:,.2f}'}), use_container_width=True)
        csv_cashin = cash_in_summary.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Cash-In Summary (CSV)", csv_cashin, "cashin_summary.csv", "text/csv")
    else:
        st.info("No Cash-In transactions found")
    
    # ============================================
    # POWER USERS (Cash-In + P2P Debit + Bank Transfer Out)
    # ============================================
    st.subheader("👑 Top Power Users (Cash-In + P2P Debit + Bank Transfer)")
    
    cashin_users = set(cash_in_data['MemberId'].unique())
    p2p_debit_data = df_filtered[(df_filtered['Service'] == 'USER P2P') & (df_filtered['Sign'] == 'Debit')]
    p2p_debit_users = set(p2p_debit_data['MemberId'].unique())
    bank_transfer_data = df_filtered[(df_filtered['Sign'] == 'Debit') & (df_filtered['Service'].isin(BANK_TRANSFER_SERVICES))]
    bank_transfer_users = set(bank_transfer_data['MemberId'].unique())
    all_power_users = cashin_users.intersection(p2p_debit_users.union(bank_transfer_users))
    
    if len(all_power_users) > 0:
        user_summaries = []
        for user_id in all_power_users:
            user_cashin = cash_in_data[cash_in_data['MemberId'] == user_id]
            user_p2p = p2p_debit_data[p2p_debit_data['MemberId'] == user_id]
            user_bank = bank_transfer_data[bank_transfer_data['MemberId'] == user_id]
            user_name = df_filtered[df_filtered['MemberId'] == user_id]['Name'].iloc[0] if 'Name' in df.columns else 'N/A'
            user_contact = df_filtered[df_filtered['MemberId'] == user_id]['ContactNumber'].iloc[0] if 'ContactNumber' in df.columns else 'N/A'
            user_summaries.append({
                'MemberId': user_id, 'Name': user_name, 'Contact': user_contact,
                'Total Cash-In (Rs)': user_cashin['Amount (Rs)'].sum(), 'Cash-In Count': len(user_cashin),
                'Total P2P Debit (Rs)': user_p2p['Amount (Rs)'].sum(), 'P2P Debit Count': len(user_p2p),
                'Total Bank Transfer Out (Rs)': user_bank['Amount (Rs)'].sum(), 'Bank Transfer Count': len(user_bank),
                'Total Outflow': user_p2p['Amount (Rs)'].sum() + user_bank['Amount (Rs)'].sum(),
                'Net Flow (Rs)': user_cashin['Amount (Rs)'].sum() - (user_p2p['Amount (Rs)'].sum() + user_bank['Amount (Rs)'].sum()),
                'User Type': 'P2P + Bank' if (user_id in p2p_debit_users and user_id in bank_transfer_users) else ('P2P Only' if user_id in p2p_debit_users else 'Bank Only')
            })
        
        power_users_df = pd.DataFrame(user_summaries).sort_values('Total Cash-In (Rs)', ascending=False)
        st.dataframe(power_users_df.head(50).style.format({
            'Total Cash-In (Rs)': 'Rs. {:,.2f}', 'Total P2P Debit (Rs)': 'Rs. {:,.2f}',
            'Total Bank Transfer Out (Rs)': 'Rs. {:,.2f}', 'Total Outflow': 'Rs. {:,.2f}', 'Net Flow (Rs)': 'Rs. {:,.2f}'
        }), use_container_width=True)
        
        csv_power = power_users_df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Power Users as CSV", csv_power, "power_users.csv", "text/csv")
    else:
        st.info("No power users found")
    
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
            user_name = user_data['Name'].iloc[0] if 'Name' in user_data.columns else 'N/A'
            user_contact = user_data['ContactNumber'].iloc[0] if 'ContactNumber' in user_data.columns else 'N/A'
            user_member_id = user_data['MemberId'].iloc[0]
            user_type = 'Agent' if user_data['ContactNumber_clean'].iloc[0] in agent_ids else 'User' if agent_ids else 'User'
            
            st.write(f"### User: {user_name} | Type: {user_type}")
            st.write(f"**Member ID:** {user_member_id} | **Contact:** {user_contact}")
            
            total_credit = user_data[user_data['Sign'] == 'Credit']['Amount (Rs)'].sum()
            total_debit = user_data[user_data['Sign'] == 'Debit']['Amount (Rs)'].sum()
            user_p2p = user_data[(user_data['Service'] == 'USER P2P') & (user_data['Sign'] == 'Debit')]['Amount (Rs)'].sum()
            user_bank = user_data[(user_data['Service'].isin(BANK_TRANSFER_SERVICES)) & (user_data['Sign'] == 'Debit')]['Amount (Rs)'].sum()
            
            col1, col2, col3, col4, col5 = st.columns(5)
            col1.metric("💰 Total Credit", f"Rs. {total_credit:,.2f}")
            col2.metric("💸 Total Debit", f"Rs. {total_debit:,.2f}")
            col3.metric("👤 P2P Sent", f"Rs. {user_p2p:,.2f}")
            col4.metric("🏦 Bank Transfer", f"Rs. {user_bank:,.2f}")
            col5.metric("📈 Net Flow", f"Rs. {total_credit - total_debit:,.2f}")
            
            display_cols = ['CreatedDate', 'Display Service', 'Sign', 'Amount (Rs)', 'Available Balance(Rs)', 'Remarks', 'Gateway Status']
            available_cols = [col for col in display_cols if col in user_data.columns]
            st.dataframe(user_data[available_cols].sort_values('CreatedDate', ascending=False), use_container_width=True)
            
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
    
    # Footer
    st.caption(f"📅 Data from {start_date.date()} to {end_date.date()} | Total rows: {len(df_filtered):,}")
    
else:
    st.info("👈 Please upload your Transaction Excel file to get started")
    st.markdown("""
    ### 📋 Dashboard Sections:
    1. **Agent vs User Transaction Report** - NEW! Segregates transactions by Agent/User and value ranges
    2. **TTR Reporting** - Users with transaction volume > Rs. 10,00,000
    3. **Merchant Payment Analysis** - Top merchants by volume and count
    4. **Cash-In Modes Analysis** - How users load money
    5. **Power Users** - Users who load and send money
    6. **User Lookup** - Search any user's transactions
    7. **Most Used Services** - Overall transaction ranking
    8. **Daily Transaction Trend** - Volume over time
    """)
