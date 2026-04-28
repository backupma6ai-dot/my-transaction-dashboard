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
    # NEW SECTION: MERCHANT PAYMENT ANALYSIS
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
        col1.metric("🏪 Total Merchants Served", f"{merchant_data['Service'].nunique():,}")
        col2.metric("💳 Total Merchant Transactions", f"{len(merchant_data):,}")
        col3.metric("💰 Total Merchant Volume", f"Rs. {merchant_data['Amount (Rs)'].sum():,.2f}")
        col4.metric("👥 Unique Paying Users", f"{merchant_data['MemberId'].nunique():,}")
        
        # Merchant ranking by COUNT
        st.write("### 📊 Merchant Ranking by Transaction Count")
        merchant_by_count = merchant_data.groupby('Service').agg({
            'TxnId': 'count',
            'Amount (Rs)': 'sum',
            'MemberId': 'nunique'
        }).reset_index()
        merchant_by_count.columns = ['Merchant', 'Transaction Count', 'Total Volume (Rs)', 'Unique Users']
        merchant_by_count = merchant_by_count.sort_values('Transaction Count', ascending=False)
        
        col1, col2 = st.columns(2)
        
        # Bar chart - Top 15 by Count
        fig_count = px.bar(merchant_by_count.head(15), 
                           x='Merchant', y='Transaction Count', 
                           title='Top 15 Merchants by Transaction Count',
                           color='Transaction Count', 
                           text='Transaction Count')
        fig_count.update_layout(xaxis_tickangle=-45)
        col1.plotly_chart(fig_count, use_container_width=True)
        
        # Bar chart - Top 15 by Volume
        fig_volume = px.bar(merchant_by_count.head(15), 
                            x='Merchant', y='Total Volume (Rs)', 
                            title='Top 15 Merchants by Transaction Volume (Rs)',
                            color='Total Volume (Rs)', 
                            text='Total Volume (Rs)')
        fig_volume.update_layout(xaxis_tickangle=-45)
        col2.plotly_chart(fig_volume, use_container_width=True)
        
        # Detailed Merchant Table
        st.write("### 📋 Detailed Merchant Performance")
        st.dataframe(merchant_by_count.head(20).style.format({
            'Transaction Count': '{:,}',
            'Total Volume (Rs)': 'Rs. {:,.2f}',
            'Unique Users': '{:,}'
        }), use_container_width=True)
        
        # Merchant category breakdown
        st.write("### 🏷️ Merchant Category Breakdown")
        
        # Categorize merchants
        def categorize_merchant(merchant):
            merchant_upper = str(merchant).upper()
            if 'INSURANCE' in merchant_upper:
                return '🛡️ Insurance'
            elif 'INTERNET' in merchant_upper or 'WIFI' in merchant_upper or 'FIBER' in merchant_upper:
                return '🌐 Internet Service'
            elif 'TV' in merchant_upper or 'DISSHOME' in merchant_upper or 'MAXTV' in merchant_upper:
                return '📺 Television'
            elif 'NEA' in merchant_upper or 'ELECTRICITY' in merchant_upper or 'KUKL' in merchant_upper or 'WATER' in merchant_upper:
                return '⚡ Utilities'
            elif 'AIRLINES' in merchant_upper or 'FLIGHT' in merchant_upper or 'INTERNATIONALFLIGHT' in merchant_upper:
                return '✈️ Travel/Airlines'
            elif 'QR' in merchant_upper:
                return '📱 QR Payments'
            elif 'MERCHANT' in merchant_upper:
                return '🏪 General Merchant'
            elif 'GOVERNMENT' in merchant_upper or 'DOFE' in merchant_upper or 'TAX' in merchant_upper or 'FINE' in merchant_upper or 'COMMISSION' in merchant_upper:
                return '🏛️ Government'
            else:
                return '📌 Other'
        
        merchant_by_count['Category'] = merchant_by_count['Merchant'].apply(categorize_merchant)
        category_summary = merchant_by_count.groupby('Category').agg({
            'Transaction Count': 'sum',
            'Total Volume (Rs)': 'sum',
            'Merchant': 'count'
        }).reset_index()
        category_summary.columns = ['Category', 'Total Transactions', 'Total Volume (Rs)', 'Number of Merchants']
        category_summary = category_summary.sort_values('Total Volume (Rs)', ascending=False)
        
        col1, col2 = st.columns(2)
        fig_category_count = px.pie(category_summary, values='Total Transactions', names='Category', title='Transactions by Merchant Category')
        col1.plotly_chart(fig_category_count, use_container_width=True)
        
        fig_category_volume = px.pie(category_summary, values='Total Volume (Rs)', names='Category', title='Volume by Merchant Category')
        col2.plotly_chart(fig_category_volume, use_container_width=True)
        
        # Top Paying Users (Users who pay merchants the most)
        st.write("### 💎 Top Paying Users (Highest Merchant Payment Volume)")
        top_paying_users = merchant_data.groupby('MemberId').agg({
            'Amount (Rs)': 'sum',
            'TxnId': 'count',
            'Service': lambda x: x.nunique()
        }).reset_index()
        top_paying_users.columns = ['MemberId', 'Total Paid (Rs)', 'Transaction Count', 'Unique Merchants']
        
        # Get user names
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
        
        st.dataframe(top_paying_users.head(20).style.format({
            'Total Paid (Rs)': 'Rs. {:,.2f}',
            'Transaction Count': '{:,}'
        }), use_container_width=True)
        
        # Download buttons
        csv_merchant = merchant_by_count.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Merchant Summary as CSV", csv_merchant, "merchant_summary.csv", "text/csv")
        
        # Daily merchant payment trend
        st.write("### 📅 Daily Merchant Payment Trend")
        daily_merchant = merchant_data.groupby(merchant_data['CreatedDate'].dt.date)['Amount (Rs)'].sum().reset_index()
        daily_merchant.columns = ['Date', 'Merchant Volume']
        fig_daily = px.line(daily_merchant, x='Date', y='Merchant Volume', title='Daily Merchant Payment Volume')
        st.plotly_chart(fig_daily, use_container_width=True)
        
    else:
        st.info("No merchant payment transactions found in selected date range")
    
    # ============================================
    # CASH-IN MODES ANALYSIS (Keep from before)
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
        fig_count = px.bar(cash_in_summary.head(10), x='Cash-In Mode', y='Transaction Count', title='Top 10 Cash-In Modes by Count', color='Transaction Count')
        col1.plotly_chart(fig_count, use_container_width=True)
        fig_volume = px.bar(cash_in_summary.head(10), x='Cash-In Mode', y='Total Volume (Rs)', title='Top 10 Cash-In Modes by Volume', color='Total Volume (Rs)')
        col2.plotly_chart(fig_volume, use_container_width=True)
        
        st.dataframe(cash_in_summary.style.format({'Transaction Count': '{:,}', 'Total Volume (Rs)': 'Rs. {:,.2f}'}))
        
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
                'Net Flow': user_cashin['Amount (Rs)'].sum() - user_p2p['Amount (Rs)'].sum()
            })
        
        power_users_df = pd.DataFrame(user_summaries).sort_values('Total Cash-In (Rs)', ascending=False)
        st.dataframe(power_users_df.head(20).style.format({
            'Total Cash-In (Rs)': 'Rs. {:,.2f}',
            'Total P2P Debit (Rs)': 'Rs. {:,.2f}',
            'Net Flow': 'Rs. {:,.2f}'
        }))
        
        csv_power = power_users_df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Power Users as CSV", csv_power, "power_users.csv", "text/csv")
    else:
        st.info("No power users found")
    
    # ============================================
    # USER LOOKUP
    # ============================================
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
            
            col1, col2, col3 = st.columns(3)
            col1.metric("💰 Total Credit", f"Rs. {total_credit:,.2f}")
            col2.metric("💸 Total Debit", f"Rs. {total_debit:,.2f}")
            col3.metric("📈 Net Flow", f"Rs. {total_credit - total_debit:,.2f}")
            
            display_cols = ['CreatedDate', 'Display Service', 'Sign', 'Amount (Rs)', 'Available Balance(Rs)', 'Remarks', 'Gateway Status']
            st.dataframe(user_data[display_cols].sort_values('CreatedDate', ascending=False))
        else:
            st.warning("No transactions found")
    
    # ============================================
    # CHARTS
    # ============================================
    st.subheader("📈 Most Used Services")
    col1, col2 = st.columns(2)
    service_count = df_filtered['Display Service'].value_counts().head(10).reset_index()
    service_count.columns = ['Service', 'Count']
    fig1 = px.bar(service_count, x='Service', y='Count', title='Top 10 by Transaction Count', color='Count')
    col1.plotly_chart(fig1, use_container_width=True)
    
    service_volume = df_filtered.groupby('Display Service')['Amount (Rs)'].sum().sort_values(ascending=False).head(10).reset_index()
    service_volume.columns = ['Service', 'Volume']
    fig2 = px.bar(service_volume, x='Service', y='Volume', title='Top 10 by Volume', color='Volume')
    col2.plotly_chart(fig2, use_container_width=True)
    
    st.subheader("📅 Daily Transaction Trend")
    daily_trend = df_filtered.groupby(df_filtered['CreatedDate'].dt.date)['Amount (Rs)'].sum().reset_index()
    daily_trend.columns = ['Date', 'Volume']
    fig3 = px.line(daily_trend, x='Date', y='Volume', title='Daily Transaction Volume')
    st.plotly_chart(fig3, use_container_width=True)
    
    st.subheader("💳 Credit vs Debit Analysis")
    sign_data = df_filtered.groupby('Sign')['Amount (Rs)'].sum().reset_index()
    fig_sign = px.pie(sign_data, values='Amount (Rs)', names='Sign', title='Credit vs Debit', hole=0.4)
    st.plotly_chart(fig_sign, use_container_width=True)
    
else:
    st.info("👈 Please upload your Excel file to get started")
