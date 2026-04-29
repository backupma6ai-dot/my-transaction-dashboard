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

# Define Bank Transfer Out services (P2P to Bank)
BANK_TRANSFER_SERVICES = [
    'BANK TRANSFER', 'MYBANK BANK TRANSFER'
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
    # TTR REPORTING - High Value Transactions (Exceeds 10 Lakhs)
    # ============================================
    st.subheader("📋 TTR Reporting - High Value Users (Debit/Credit > Rs. 10,00,000)")
    
    # Calculate total debit and credit per user
    user_credit_summary = df_filtered[df_filtered['Sign'] == 'Credit'].groupby('MemberId')['Amount (Rs)'].sum().reset_index()
    user_credit_summary.columns = ['MemberId', 'Total Credit (Rs)']
    
    user_debit_summary = df_filtered[df_filtered['Sign'] == 'Debit'].groupby('MemberId')['Amount (Rs)'].sum().reset_index()
    user_debit_summary.columns = ['MemberId', 'Total Debit (Rs)']
    
    # Merge credit and debit
    ttr_report = pd.merge(user_credit_summary, user_debit_summary, on='MemberId', how='outer').fillna(0)
    
    # Add user names and contacts
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
    
    # Calculate net flow
    ttr_report['Net Flow (Rs)'] = ttr_report['Total Credit (Rs)'] - ttr_report['Total Debit (Rs)']
    
    # Filter users where credit OR debit exceeds 10,00,000
    HIGH_VALUE_THRESHOLD = 1000000
    high_value_users = ttr_report[
        (ttr_report['Total Credit (Rs)'] > HIGH_VALUE_THRESHOLD) | 
        (ttr_report['Total Debit (Rs)'] > HIGH_VALUE_THRESHOLD)
    ]
    
    # Sort by highest total volume
    high_value_users['Total Volume (Rs)'] = high_value_users['Total Credit (Rs)'] + high_value_users['Total Debit (Rs)']
    high_value_users = high_value_users.sort_values('Total Volume (Rs)', ascending=False)
    
    if len(high_value_users) > 0:
        # Summary metrics for TTR
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("⚠️ High Value Users", f"{len(high_value_users):,}")
        col2.metric("💰 Total Credit (High Value)", f"Rs. {high_value_users['Total Credit (Rs)'].sum():,.2f}")
        col3.metric("💸 Total Debit (High Value)", f"Rs. {high_value_users['Total Debit (Rs)'].sum():,.2f}")
        col4.metric("📊 Total Volume", f"Rs. {high_value_users['Total Volume (Rs)'].sum():,.2f}")
        
        # Tabs for different views
        tab1, tab2, tab3 = st.tabs(["📊 All High Value Users", "💰 High Credit Users", "💸 High Debit Users"])
        
        with tab1:
            st.write("### All Users with Debit or Credit > Rs. 10,00,000")
            st.dataframe(
                high_value_users[['MemberId', 'Name', 'Contact', 'Total Credit (Rs)', 'Total Debit (Rs)', 'Net Flow (Rs)', 'Total Volume (Rs)']].style.format({
                    'Total Credit (Rs)': 'Rs. {:,.2f}',
                    'Total Debit (Rs)': 'Rs. {:,.2f}',
                    'Net Flow (Rs)': 'Rs. {:,.2f}',
                    'Total Volume (Rs)': 'Rs. {:,.2f}'
                }),
                use_container_width=True
            )
        
        with tab2:
            # Users with high credit only (above threshold)
            high_credit_users = ttr_report[ttr_report['Total Credit (Rs)'] > HIGH_VALUE_THRESHOLD].sort_values('Total Credit (Rs)', ascending=False)
            st.write("### Users with Total Credit > Rs. 10,00,000")
            st.dataframe(
                high_credit_users[['MemberId', 'Name', 'Contact', 'Total Credit (Rs)', 'Total Debit (Rs)', 'Net Flow (Rs)']].style.format({
                    'Total Credit (Rs)': 'Rs. {:,.2f}',
                    'Total Debit (Rs)': 'Rs. {:,.2f}',
                    'Net Flow (Rs)': 'Rs. {:,.2f}'
                }),
                use_container_width=True
            )
        
        with tab3:
            # Users with high debit only (above threshold)
            high_debit_users = ttr_report[ttr_report['Total Debit (Rs)'] > HIGH_VALUE_THRESHOLD].sort_values('Total Debit (Rs)', ascending=False)
            st.write("### Users with Total Debit > Rs. 10,00,000")
            st.dataframe(
                high_debit_users[['MemberId', 'Name', 'Contact', 'Total Credit (Rs)', 'Total Debit (Rs)', 'Net Flow (Rs)']].style.format({
                    'Total Credit (Rs)': 'Rs. {:,.2f}',
                    'Total Debit (Rs)': 'Rs. {:,.2f}',
                    'Net Flow (Rs)': 'Rs. {:,.2f}'
                }),
                use_container_width=True
            )
        
        # Download TTR Report
        csv_ttr = high_value_users.to_csv(index=False).encode('utf-8')
        st.download_button(
            "📥 Download TTR Report (CSV)", 
            csv_ttr, 
            f"ttr_report_{start_date.date()}_to_{end_date.date()}.csv", 
            "text/csv"
        )
        
        # Visual - Top 10 High Value Users
        st.write("### 📊 Top 10 High Value Users by Total Volume")
        fig_ttr = px.bar(high_value_users.head(10), 
                         x='Name', 
                         y=['Total Credit (Rs)', 'Total Debit (Rs)'],
                         title='Top 10 Users by Total Transaction Volume',
                         barmode='group',
                         labels={'value': 'Amount (Rs)', 'variable': 'Transaction Type', 'Name': 'User Name'},
                         color_discrete_map={'Total Credit (Rs)': 'green', 'Total Debit (Rs)': 'red'})
        fig_ttr.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_ttr, use_container_width=True)
        
        # Expandable section for transaction details of high value users
        with st.expander("🔍 View Transaction Details for High Value Users"):
            selected_user_ttr = st.selectbox("Select User to View Transactions", high_value_users['MemberId'].head(20))
            if selected_user_ttr:
                user_ttr_data = df_filtered[df_filtered['MemberId'] == selected_user_ttr]
                user_ttr_name = high_value_users[high_value_users['MemberId'] == selected_user_ttr]['Name'].iloc[0]
                
                st.write(f"#### Transaction History for {user_ttr_name} (ID: {selected_user_ttr})")
                display_cols = ['CreatedDate', 'Display Service', 'Sign', 'Amount (Rs)', 'Remarks']
                available_cols = [col for col in display_cols if col in user_ttr_data.columns]
                st.dataframe(user_ttr_data[available_cols].sort_values('CreatedDate', ascending=False), use_container_width=True)
        
    else:
        st.info(f"No users found with total Debit or Credit exceeding Rs. {HIGH_VALUE_THRESHOLD:,} in the selected date range")
    
    # ============================================
    # MERCHANT PAYMENT ANALYSIS
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
            use_container_width=True
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
        
        # Daily merchant payment trend
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
    # POWER USERS (Cash-In + P2P Debit + Bank Transfer Out)
    # ============================================
    st.subheader("👑 Top Power Users (Cash-In + P2P Debit + Bank Transfer)")
    
    # Get all relevant user groups
    cashin_users = set(cash_in_data['MemberId'].unique())
    p2p_debit_data = df_filtered[(df_filtered['Service'] == 'USER P2P') & (df_filtered['Sign'] == 'Debit')]
    p2p_debit_users = set(p2p_debit_data['MemberId'].unique())
    
    # Bank Transfer Out data
    bank_transfer_data = df_filtered[
        (df_filtered['Sign'] == 'Debit') & 
        (df_filtered['Service'].isin(BANK_TRANSFER_SERVICES))
    ]
    bank_transfer_users = set(bank_transfer_data['MemberId'].unique())
    
    # All power users (Cash-In + either P2P or Bank)
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
                'MemberId': user_id,
                'Name': user_name,
                'Contact': user_contact,
                'Total Cash-In (Rs)': user_cashin['Amount (Rs)'].sum(),
                'Cash-In Count': len(user_cashin),
                'Total P2P Debit (Rs)': user_p2p['Amount (Rs)'].sum(),
                'P2P Debit Count': len(user_p2p),
                'Total Bank Transfer Out (Rs)': user_bank['Amount (Rs)'].sum(),
                'Bank Transfer Count': len(user_bank),
                'Total Outflow (P2P + Bank)': user_p2p['Amount (Rs)'].sum() + user_bank['Amount (Rs)'].sum(),
                'Net Flow (Rs)': user_cashin['Amount (Rs)'].sum() - (user_p2p['Amount (Rs)'].sum() + user_bank['Amount (Rs)'].sum()),
                'User Type': 'P2P + Bank' if (user_id in p2p_debit_users and user_id in bank_transfer_users) else ('P2P Only' if user_id in p2p_debit_users else 'Bank Only')
            })
        
        power_users_df = pd.DataFrame(user_summaries).sort_values('Total Cash-In (Rs)', ascending=False)
        
        # Display metrics
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("👥 Total Power Users", f"{len(all_power_users):,}")
        col2.metric("💰 Total Cash-In", f"Rs. {power_users_df['Total Cash-In (Rs)'].sum():,.2f}")
        col3.metric("💸 Total P2P Debit", f"Rs. {power_users_df['Total P2P Debit (Rs)'].sum():,.2f}")
        col4.metric("🏦 Total Bank Transfer", f"Rs. {power_users_df['Total Bank Transfer Out (Rs)'].sum():,.2f}")
        
        # Filter options
        st.write("### 🔍 Filter Power Users")
        user_type_filter = st.selectbox("Select User Type", ["All Users", "P2P Only", "Bank Only", "P2P + Bank"])
        
        if user_type_filter == "P2P Only":
            filtered_df = power_users_df[power_users_df['User Type'] == 'P2P Only']
        elif user_type_filter == "Bank Only":
            filtered_df = power_users_df[power_users_df['User Type'] == 'Bank Only']
        elif user_type_filter == "P2P + Bank":
            filtered_df = power_users_df[power_users_df['User Type'] == 'P2P + Bank']
        else:
            filtered_df = power_users_df
        
        # Display table
        st.write(f"### 📋 Power Users List ({user_type_filter})")
        st.dataframe(
            filtered_df[['MemberId', 'Name', 'Contact', 'Total Cash-In (Rs)', 'Cash-In Count', 
                         'Total P2P Debit (Rs)', 'P2P Debit Count', 'Total Bank Transfer Out (Rs)', 
                         'Bank Transfer Count', 'Total Outflow (P2P + Bank)', 'Net Flow (Rs)', 'User Type']].head(50).style.format({
                'Total Cash-In (Rs)': 'Rs. {:,.2f}',
                'Cash-In Count': '{:,}',
                'Total P2P Debit (Rs)': 'Rs. {:,.2f}',
                'P2P Debit Count': '{:,}',
                'Total Bank Transfer Out (Rs)': 'Rs. {:,.2f}',
                'Bank Transfer Count': '{:,}',
                'Total Outflow (P2P + Bank)': 'Rs. {:,.2f}',
                'Net Flow (Rs)': 'Rs. {:,.2f}'
            }),
            use_container_width=True
        )
        
        # Download button
        csv_power = filtered_df.to_csv(index=False).encode('utf-8')
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
            
            # Calculate P2P and Bank transfers for this user
            user_p2p = user_data[(user_data['Service'] == 'USER P2P') & (user_data['Sign'] == 'Debit')]['Amount (Rs)'].sum()
            user_bank = user_data[(user_data['Service'].isin(BANK_TRANSFER_SERVICES)) & (user_data['Sign'] == 'Debit')]['Amount (Rs)'].sum()
            
            col1, col2, col3, col4, col5 = st.columns(5)
            col1.metric("💰 Total Credit", f"Rs. {total_credit:,.2f}")
            col2.metric("💸 Total Debit", f"Rs. {total_debit:,.2f}")
            col3.metric("👤 P2P Sent", f"Rs. {user_p2p:,.2f}")
            col4.metric("🏦 Bank Transfer", f"Rs. {user_bank:,.2f}")
            col5.metric("📈 Net Flow", f"Rs. {total_credit - total_debit:,.2f}")
            
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
