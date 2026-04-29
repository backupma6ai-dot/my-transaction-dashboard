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

# Define Transaction Categories
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

# Value Range Function
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

# File uploaders
st.sidebar.header("📁 Upload Files")

uploaded_file = st.sidebar.file_uploader("Upload Transaction Excel File", type=["xlsx", "xls"])
agent_file = st.sidebar.file_uploader("Upload Agent List Excel File", type=["xlsx", "xls"])

@st.cache_data
def load_transaction_data(file):
    df = pd.read_excel(file)
    df['CreatedDate'] = pd.to_datetime(df['CreatedDate'], errors='coerce')
    df['Display Service'] = df.apply(
        lambda row: f"{row.get('Service', '')} ({row.get('Sign', '')})", 
        axis=1
    )
    return df

@st.cache_data
def load_agent_list(file):
    if file is not None:
        df = pd.read_excel(file)
        st.sidebar.write("📋 Agent File Columns Found:", list(df.columns))
        
        # Try to find the Agent code column - look for 'Agent code' or 'ContactNumber'
        agent_col = None
        for col in df.columns:
            col_lower = col.lower()
            if 'agent code' in col_lower or 'agent_code' in col_lower or 'agent' in col_lower:
                agent_col = col
                break
            elif 'contact' in col_lower or 'phone' in col_lower or 'mobile' in col_lower:
                agent_col = col
                break
        
        # If still not found, use first column
        if agent_col is None:
            agent_col = df.columns[0]
            st.sidebar.warning(f"⚠️ Using first column as Agent identifier: {agent_col}")
        else:
            st.sidebar.success(f"✅ Using column '{agent_col}' for Agent identification")
        
        # Get agent identifiers (Contact numbers)
        agent_ids = set(df[agent_col].astype(str).str.strip().unique())
        st.sidebar.success(f"✅ Loaded {len(agent_ids):,} agents")
        
        # Show sample of first 5 agent IDs
        sample_ids = list(agent_ids)[:5]
        st.sidebar.write(f"📌 Sample Agent Codes: {', '.join(sample_ids)}")
        
        # Also show agent names if available
        name_col = None
        for col in df.columns:
            if 'name' in col.lower():
                name_col = col
                break
        
        if name_col:
            agent_names = df.set_index(agent_col)[name_col].to_dict()
            st.sidebar.write(f"📌 Found Agent Names in column: {name_col}")
            return agent_ids, agent_names
        else:
            return agent_ids, {}
    
    return set(), {}

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

if uploaded_file is not None:
    # Load data
    df = load_transaction_data(uploaded_file)
    agent_ids, agent_names = load_agent_list(agent_file)
    
    # IMPORTANT: Convert ContactNumber to string and clean for matching
    if 'ContactNumber' in df.columns:
        df['ContactNumber_clean'] = df['ContactNumber'].astype(str).str.strip()
    else:
        st.error("❌ Transaction file must have 'ContactNumber' column to match with agents")
        st.stop()
    
    # Show transaction data sample
    st.sidebar.write("📋 Transaction Data Columns:", list(df.columns))
    st.sidebar.write(f"📊 Total Transactions: {len(df):,}")
    st.sidebar.write(f"👥 Unique ContactNumbers: {df['ContactNumber_clean'].nunique():,}")
    
    # Show sample ContactNumbers from transaction data
    sample_contacts = df['ContactNumber_clean'].unique()[:5]
    st.sidebar.write(f"📌 Sample ContactNumbers from transactions: {', '.join(sample_contacts)}")
    
    # Check if any agent IDs match transaction ContactNumbers
    if agent_ids:
        matching_agents = agent_ids.intersection(set(df['ContactNumber_clean'].unique()))
        st.sidebar.write(f"🔗 Matching Agents in transactions: {len(matching_agents):,} out of {len(agent_ids):,}")
        
        if len(matching_agents) > 0:
            st.sidebar.success(f"✅ Found {len(matching_agents):,} agents with transactions!")
            sample_matches = list(matching_agents)[:3]
            st.sidebar.write(f"📌 Matching sample: {', '.join(sample_matches)}")
        else:
            st.sidebar.error("❌ No matching Agent ContactNumbers found in transaction data!")
            st.sidebar.info("💡 Make sure the Agent Code in agent file matches the ContactNumber in transaction file")
    
    # Add User Type column (match based on ContactNumber)
    df['User Type'] = df['ContactNumber_clean'].apply(
        lambda x: 'Agent' if x in agent_ids else 'User'
    )
    
    # Add Agent Name if available
    if agent_names:
        df['Agent Name'] = df['ContactNumber_clean'].map(agent_names).fillna('')
    
    # Show user type distribution
    user_type_counts = df['User Type'].value_counts()
    st.sidebar.write("📊 User Type Distribution:")
    for user_type, count in user_type_counts.items():
        st.sidebar.write(f"   {user_type}: {count:,} transactions")
    
    # Add Value Range column
    df['Value Range'] = df['Amount (Rs)'].apply(get_value_range)
    
    # Add Transaction Category column
    df['Transaction Category'] = df.apply(
        lambda row: get_transaction_category(row.get('Service', ''), row.get('Sign', '')),
        axis=1
    )
    
    # Only include relevant transactions
    relevant_transactions = df[
        ((df['Transaction Category'] == 'Cash in') & (df['Sign'] == 'Credit')) |
        ((df['Transaction Category'] == 'Transfer to bank A/C (P2P)') & (df['Sign'] == 'Debit')) |
        ((df['Transaction Category'] == 'Government payment (P2G)') & (df['Sign'] == 'Debit')) |
        ((df['Transaction Category'] == 'Merchant payment') & (df['Sign'] == 'Debit')) |
        ((df['Transaction Category'] == 'Topup') & (df['Sign'] == 'Debit'))
    ]
    
    # Sidebar date filters
    st.sidebar.header("🔍 Date Filters")
    if len(relevant_transactions) > 0:
        min_date = relevant_transactions['CreatedDate'].min().date()
        max_date = relevant_transactions['CreatedDate'].max().date()
    else:
        min_date = datetime.today().date()
        max_date = datetime.today().date()
    
    start_date = st.sidebar.date_input("Start Date", min_date, min_value=min_date, max_value=max_date)
    end_date = st.sidebar.date_input("End Date", max_date, min_value=min_date, max_value=max_date)
    
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    
    if len(relevant_transactions) > 0:
        df_filtered = relevant_transactions[(relevant_transactions['CreatedDate'] >= start_date) & (relevant_transactions['CreatedDate'] <= end_date)]
    else:
        df_filtered = relevant_transactions
    
    # ============================================
    # AGENT/USER SEGMENTATION REPORT (Pivot Table Style)
    # ============================================
    st.subheader("📊 Agent vs User Transaction Report")
    
    # Show agent count info
    col1, col2 = st.columns(2)
    col1.metric("👥 Total Agents in List", f"{len(agent_ids):,}" if agent_ids else "0 (No agent list uploaded)")
    col2.metric("👤 Users in Transactions", f"{df_filtered[df_filtered['User Type'] == 'User']['ContactNumber_clean'].nunique():,}" if len(df_filtered) > 0 else "0")
    
    if agent_ids:
        matching_agents = agent_ids.intersection(set(df['ContactNumber_clean'].unique()))
        st.success(f"✅ Agent list loaded with {len(agent_ids):,} agents | Found {len(matching_agents):,} agents with transactions")
        
        if len(matching_agents) == 0:
            st.error("❌ No matching agents found! Please check that:")
            st.markdown("""
            1. The **Agent Code** column in your agent file contains phone numbers
            2. The **ContactNumber** column in your transaction file contains the same phone numbers
            3. Both have the same format (e.g., both have country code or both don't)
            """)
    else:
        st.info("ℹ️ No agent list uploaded. All transactions will be categorized as 'User'. Upload an agent list Excel file to enable Agent/User segmentation.")
    
    if len(df_filtered) > 0:
        # Create the pivot table report
        report_data = df_filtered.groupby(['User Type', 'Value Range', 'Transaction Category']).agg({
            'Amount (Rs)': ['count', 'sum']
        }).reset_index()
        
        report_data.columns = ['User Type', 'Value Range', 'Transaction Category', 'Transaction Count', 'Total Amount (Rs)']
        
        # Pivot to get categories as columns
        pivot_report = report_data.pivot_table(
            index=['User Type', 'Value Range'],
            columns='Transaction Category',
            values=['Transaction Count', 'Total Amount (Rs)'],
            fill_value=0
        )
        
        # Flatten column names
        pivot_report.columns = [f'{col[1]}_{col[0]}' for col in pivot_report.columns]
        pivot_report = pivot_report.reset_index()
        
        # Ensure all expected columns exist
        expected_categories = ['Cash in', 'Government payment (P2G)', 'Merchant payment', 'Topup', 'Transfer to bank A/C (P2P)', '#N/A']
        for cat in expected_categories:
            if f'{cat}_Transaction Count' not in pivot_report.columns:
                pivot_report[f'{cat}_Transaction Count'] = 0
            if f'{cat}_Total Amount (Rs)' not in pivot_report.columns:
                pivot_report[f'{cat}_Total Amount (Rs)'] = 0
        
        # Calculate totals per row
        pivot_report['Total Transaction Count'] = pivot_report[[f'{cat}_Transaction Count' for cat in expected_categories if cat != '#N/A']].sum(axis=1)
        pivot_report['Total Amount (Rs)'] = pivot_report[[f'{cat}_Total Amount (Rs)' for cat in expected_categories if cat != '#N/A']].sum(axis=1)
        
        # Order value ranges properly
        range_order = ['Up to 1000', '1001 to 5000', '5001 to 10000', '10001 to 20000', '20001 to 25000', 'greater than 25000']
        pivot_report['Value Range'] = pd.Categorical(pivot_report['Value Range'], categories=range_order, ordered=True)
        pivot_report = pivot_report.sort_values(['User Type', 'Value Range'])
        
        # Display the report
        st.write("### 📋 Transaction Report by User Type and Value Range")
        
        # Display for Agents
        st.write("#### 👨‍💼 AGENTS")
        agent_report = pivot_report[pivot_report['User Type'] == 'Agent']
        if len(agent_report) > 0:
            display_agent = agent_report[['Value Range', 
                                            'Cash in_Transaction Count', 'Cash in_Total Amount (Rs)',
                                            'Government payment (P2G)_Transaction Count', 'Government payment (P2G)_Total Amount (Rs)',
                                            'Merchant payment_Transaction Count', 'Merchant payment_Total Amount (Rs)',
                                            'Topup_Transaction Count', 'Topup_Total Amount (Rs)',
                                            'Transfer to bank A/C (P2P)_Transaction Count', 'Transfer to bank A/C (P2P)_Total Amount (Rs)',
                                            'Total Transaction Count', 'Total Amount (Rs)']]
            
            st.dataframe(
                display_agent.style.format({
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
        
        # Display for Users
        st.write("#### 👤 USERS")
        user_report = pivot_report[pivot_report['User Type'] == 'User']
        if len(user_report) > 0:
            display_user = user_report[['Value Range', 
                                         'Cash in_Transaction Count', 'Cash in_Total Amount (Rs)',
                                         'Government payment (P2G)_Transaction Count', 'Government payment (P2G)_Total Amount (Rs)',
                                         'Merchant payment_Transaction Count', 'Merchant payment_Total Amount (Rs)',
                                         'Topup_Transaction Count', 'Topup_Total Amount (Rs)',
                                         'Transfer to bank A/C (P2P)_Transaction Count', 'Transfer to bank A/C (P2P)_Total Amount (Rs)',
                                         'Total Transaction Count', 'Total Amount (Rs)']]
            
            st.dataframe(
                display_user.style.format({
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
            if cat != '#N/A':
                grand_total_by_category[f'{cat}_Transaction Count'] = pivot_report[f'{cat}_Transaction Count'].sum()
                grand_total_by_category[f'{cat}_Total Amount (Rs)'] = pivot_report[f'{cat}_Total Amount (Rs)'].sum()
        
        grand_df = pd.DataFrame([{
            'Category': 'Cash in',
            'Transaction Count': grand_total_by_category.get('Cash in_Transaction Count', 0),
            'Total Amount (Rs)': grand_total_by_category.get('Cash in_Total Amount (Rs)', 0)
        }, {
            'Category': 'Government payment (P2G)',
            'Transaction Count': grand_total_by_category.get('Government payment (P2G)_Transaction Count', 0),
            'Total Amount (Rs)': grand_total_by_category.get('Government payment (P2G)_Total Amount (Rs)', 0)
        }, {
            'Category': 'Merchant payment',
            'Transaction Count': grand_total_by_category.get('Merchant payment_Transaction Count', 0),
            'Total Amount (Rs)': grand_total_by_category.get('Merchant payment_Total Amount (Rs)', 0)
        }, {
            'Category': 'Topup',
            'Transaction Count': grand_total_by_category.get('Topup_Transaction Count', 0),
            'Total Amount (Rs)': grand_total_by_category.get('Topup_Total Amount (Rs)', 0)
        }, {
            'Category': 'Transfer to bank A/C (P2P)',
            'Transaction Count': grand_total_by_category.get('Transfer to bank A/C (P2P)_Transaction Count', 0),
            'Total Amount (Rs)': grand_total_by_category.get('Transfer to bank A/C (P2P)_Total Amount (Rs)', 0)
        }])
        
        col1, col2 = st.columns(2)
        with col1:
            st.dataframe(grand_df.style.format({
                'Transaction Count': '{:,}',
                'Total Amount (Rs)': 'Rs. {:,.2f}'
            }), use_container_width=True)
        
        with col2:
            st.metric("📦 Total Transactions", f"{pivot_report['Total Transaction Count'].sum():,.0f}")
            st.metric("💰 Total Volume", f"Rs. {pivot_report['Total Amount (Rs)'].sum():,.2f}")
        
        # Download button
        export_agent = agent_report.copy() if len(agent_report) > 0 else pd.DataFrame()
        export_user = user_report.copy() if len(user_report) > 0 else pd.DataFrame()
        
        if len(export_agent) > 0:
            export_agent['User Type'] = 'Agent'
        if len(export_user) > 0:
            export_user['User Type'] = 'User'
        
        export_df = pd.concat([export_agent, export_user]) if len(export_agent) > 0 or len(export_user) > 0 else pd.DataFrame()
        
        if len(export_df) > 0:
            csv_report = export_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📥 Download Agent/User Report (CSV)", 
                csv_report, 
                f"agent_user_report_{start_date.date()}_to_{end_date.date()}.csv", 
                "text/csv"
            )
        
        # ============================================
        # CHARTS
        # ============================================
        st.subheader("📊 Transaction Category Distribution")
        
        col1, col2 = st.columns(2)
        
        category_count = df_filtered.groupby('Transaction Category').size().reset_index(name='Count')
        fig_count = px.pie(category_count, values='Count', names='Transaction Category', title='Transactions by Category')
        col1.plotly_chart(fig_count, use_container_width=True)
        
        category_volume = df_filtered.groupby('Transaction Category')['Amount (Rs)'].sum().reset_index()
        fig_volume = px.pie(category_volume, values='Amount (Rs)', names='Transaction Category', title='Volume by Category')
        col2.plotly_chart(fig_volume, use_container_width=True)
        
        st.subheader("👥 Agent vs User Transaction Volume")
        user_type_volume = df_filtered.groupby('User Type')['Amount (Rs)'].sum().reset_index()
        fig_type = px.bar(user_type_volume, x='User Type', y='Amount (Rs)', title='Transaction Volume by User Type',
                          color='User Type', text='Amount (Rs)')
        st.plotly_chart(fig_type, use_container_width=True)
        
    else:
        st.warning("No transactions found in selected date range")
    
else:
    st.info("👈 Please upload your Transaction Excel file to get started")
    st.markdown("""
    ### 📋 Instructions:
    
    1. **Upload Transaction Excel File** - Your main transaction data (must have **ContactNumber** column)
    
    2. **Upload Agent List Excel File** - Your agent list with **Agent code** column (phone numbers)
       - The dashboard will match Agent Code from agent file with ContactNumber in transaction file
    
    3. **Expected Agent File Format:**
       | Agent code* | Agent name* | ContactNumber | ... |
       |-------------|-------------|---------------|-----|
       | 9810510933  | Siddhant Enterprises | 9810510933 | ... |
    
    4. The dashboard will automatically generate:
       - Agent vs User transaction report by value range
       - Transaction category breakdown
       - Downloadable CSV reports
    """)
