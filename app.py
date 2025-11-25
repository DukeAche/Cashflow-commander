import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
import calendar
from database import CashflowDatabase

# Page configuration
st.set_page_config(
    page_title="Cashflow Commander",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database
db = CashflowDatabase()

# Currency symbols
CURRENCIES = {
    "USD ($)": "$",
    "EUR (€)": "€",
    "GBP (£)": "£",
    "GHS (GH₵)": "GH₵",
    "NGN (₦)": "₦",
    "ZAR (R)": "R",
    "JPY (¥)": "¥",
    "CNY (¥)": "¥",
    "INR (₹)": "₹",
    "AUD (A$)": "A$",
    "CAD (C$)": "C$"
}

# Custom CSS for professional styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #64748b;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #1e293b;
    }
    .metric-label {
        font-size: 0.875rem;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .stButton > button {
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(59, 130, 246, 0.3);
    }
    .success-message {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'transactions_df' not in st.session_state:
    st.session_state.transactions_df = pd.DataFrame()
if 'form_submitted' not in st.session_state:
    st.session_state.form_submitted = False
if 'currency' not in st.session_state:
    st.session_state.currency = "USD ($)"
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_role' not in st.session_state:
    st.session_state.user_role = None
if 'username' not in st.session_state:
    st.session_state.username = None

def refresh_data():
    """Refresh the transaction data"""
    if st.session_state.username:
        st.session_state.transactions_df = db.get_all_transactions(st.session_state.username)

def format_currency(amount, currency_key):
    """Format amount with selected currency symbol"""
    symbol = CURRENCIES.get(currency_key, "$")
    # For currencies with symbol after amount
    if currency_key in ["EUR (€)"]:
        return f"{amount:,.2f}{symbol}"
    else:
        return f"{symbol}{amount:,.2f}"

def login_page():
    """Display login and signup page"""
    st.markdown('<h1 class="main-header" style="text-align: center;">💰 Cashflow Commander</h1>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        tab1, tab2 = st.tabs(["Login", "Sign Up"])
        
        with tab1:
            with st.form("login_form"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                submit = st.form_submit_button("Login", use_container_width=True)
                
                if submit:
                    success, role = db.verify_user(username, password)
                    if success:
                        st.session_state.logged_in = True
                        st.session_state.user_role = role
                        st.session_state.username = username
                        db.log_login(username, "Success")
                        refresh_data() # Load user data
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        db.log_login(username, "Failure")
                        st.error("Invalid username or password")
        
        with tab2:
            with st.form("signup_form"):
                new_user = st.text_input("New Username")
                new_pass = st.text_input("New Password", type="password")
                confirm_pass = st.text_input("Confirm Password", type="password")
                submit = st.form_submit_button("Sign Up", use_container_width=True)
                
                if submit:
                    if new_pass != confirm_pass:
                        st.error("Passwords do not match")
                    elif len(new_pass) < 6:
                        st.error("Password must be at least 6 characters")
                    else:
                        success, msg = db.add_user(new_user, new_pass)
                        if success:
                            st.success("Account created! Please login.")
                        else:
                            st.error(msg)

def admin_dashboard():
    """Display admin dashboard"""
    st.markdown("## 🔐 Admin Dashboard")
    
    tab1, tab2 = st.tabs(["👥 User Management", "📝 Login Logs"])
    
    with tab1:
        st.markdown("### Users")
        users_df = db.get_all_users()
        st.dataframe(users_df, use_container_width=True)
        
        st.markdown("### Add User")
        with st.form("admin_add_user"):
            col1, col2, col3 = st.columns(3)
            with col1:
                new_user = st.text_input("Username")
            with col2:
                new_pass = st.text_input("Password", type="password")
            with col3:
                role = st.selectbox("Role", ["user", "admin"])
            
            if st.form_submit_button("Add User"):
                success, msg = db.add_user(new_user, new_pass, role)
                if success:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)
        
        st.markdown("### 🔑 Reset Password")
        with st.form("admin_reset_password"):
            col1, col2 = st.columns(2)
            with col1:
                # Get list of users for dropdown
                user_list = users_df['username'].tolist() if not users_df.empty else []
                reset_username = st.selectbox("Select User", user_list)
            with col2:
                reset_new_pass = st.text_input("New Password", type="password", key="reset_pass")
            
            if st.form_submit_button("Reset Password"):
                if len(reset_new_pass) < 6:
                    st.error("Password must be at least 6 characters")
                else:
                    success, msg = db.update_password(reset_username, reset_new_pass)
                    if success:
                        st.success(f"Password for {reset_username} updated successfully!")
                    else:
                        st.error(msg)
    
    with tab2:
        st.markdown("### Login Logs")
        logs_df = db.get_login_logs()
        st.dataframe(logs_df, use_container_width=True)

# Header
st.markdown('<h1 class="main-header">💰 Cashflow Commander</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Your intelligent financial management dashboard for micro-business success</p>', unsafe_allow_html=True)

# Sidebar navigation
# Sidebar navigation
if not st.session_state.logged_in:
    login_page()
    st.stop()

st.sidebar.markdown(f"👤 **{st.session_state.username}** ({st.session_state.user_role})")
if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.session_state.user_role = None
    st.session_state.username = None
    st.rerun()

st.sidebar.markdown("## 📊 Navigation")
nav_options = ["📈 Dashboard", "💳 Add Transaction", "📋 Ledger", "📊 Reports"]
if st.session_state.user_role == 'admin':
    nav_options.append("🔐 Admin")

selected_section = st.sidebar.radio(
    "Select Section",
    nav_options,
    label_visibility="collapsed"
)

# Reset Dashboard Button
st.sidebar.markdown("---")
st.sidebar.markdown("### ⚠️ Danger Zone")
confirm_reset = st.sidebar.checkbox("Enable Dashboard Reset")
if st.sidebar.button("🗑️ Reset Dashboard", disabled=not confirm_reset, help="Delete all your transactions"):
    try:
        db.delete_all_user_transactions(st.session_state.username)
        refresh_data()
        st.sidebar.success("Dashboard reset!")
        st.rerun()
    except Exception as e:
        st.sidebar.error(f"Error: {str(e)}")

# Currency selector in sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("### 💱 Currency")
st.session_state.currency = st.sidebar.selectbox(
    "Select Currency",
    options=list(CURRENCIES.keys()),
    index=list(CURRENCIES.keys()).index(st.session_state.currency) if st.session_state.currency in CURRENCIES.keys() else 0,
    label_visibility="collapsed"
)
currency_symbol = CURRENCIES[st.session_state.currency]

# Date filter in sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("### 📅 Date Filter")
current_year = datetime.now().year
current_month = datetime.now().month

selected_year = st.sidebar.selectbox(
    "Year",
    options=list(range(current_year - 2, current_year + 1)),
    index=2
)

selected_month = st.sidebar.selectbox(
    "Month",
    options=list(range(1, 13)),
    format_func=lambda x: calendar.month_name[x],
    index=current_month - 1
)

# Dashboard Section
if selected_section == "📈 Dashboard":
    st.markdown("## 📈 Financial Dashboard")
    
    # Get filtered data
    df = st.session_state.transactions_df.copy()
    if not df.empty:
        df['year'] = df['date'].dt.year
        df['month'] = df['date'].dt.month
        filtered_df = df[(df['year'] == selected_year) & (df['month'] == selected_month)]
    else:
        filtered_df = pd.DataFrame()
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    if not filtered_df.empty:
        total_income = filtered_df[filtered_df['type'] == 'Income']['amount'].sum()
        total_expenses = filtered_df[filtered_df['type'] == 'Expense']['amount'].sum()
        net_flow = total_income - total_expenses
        
        # Calculate cumulative balance
        cumulative_df = db.get_cumulative_balance(st.session_state.username)
        current_balance = cumulative_df['cumulative_balance'].iloc[-1] if not cumulative_df.empty else 0
    else:
        total_income = total_expenses = net_flow = current_balance = 0
    
    with col1:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{format_currency(total_income, st.session_state.currency)}</div>
                <div class="metric-label">Total Income</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{format_currency(total_expenses, st.session_state.currency)}</div>
                <div class="metric-label">Total Expenses</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        net_color = "#10b981" if net_flow >= 0 else "#ef4444"
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value" style="color: {net_color}">{format_currency(net_flow, st.session_state.currency)}</div>
                <div class="metric-label">Net Cash Flow</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        balance_color = "#10b981" if current_balance >= 0 else "#ef4444"
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value" style="color: {balance_color}">{format_currency(current_balance, st.session_state.currency)}</div>
                <div class="metric-label">Current Balance</div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Visualizations
    if not st.session_state.transactions_df.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📊 Cash Flow Over Time")
            cumulative_df = db.get_cumulative_balance(st.session_state.username)
            if not cumulative_df.empty:
                fig_line = px.line(
                    cumulative_df, 
                    x='date', 
                    y='cumulative_balance',
                    title='Cumulative Balance Trend',
                    labels={'cumulative_balance': f'Balance ({currency_symbol})', 'date': 'Date'}
                )
                fig_line.update_traces(line_color='#3b82f6', line_width=3)
                fig_line.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(family="Arial", size=12),
                    title_font_size=16
                )
                st.plotly_chart(fig_line, use_container_width=True)
        
        with col2:
            st.markdown("### 💧 Income vs Expenses Waterfall")
            monthly_summary = db.get_monthly_summary(st.session_state.username, selected_year, selected_month)
            if not monthly_summary.empty:
                # Prepare waterfall data
                income_data = monthly_summary[monthly_summary['type'] == 'Income']
                expense_data = monthly_summary[monthly_summary['type'] == 'Expense']
                
                categories = list(income_data['category']) + list(expense_data['category'])
                values = list(income_data['total']) + list(-expense_data['total'])
                colors = ['#10b981'] * len(income_data) + ['#ef4444'] * len(expense_data)
                
                fig_waterfall = go.Figure(data=[
                    go.Bar(
                        x=categories,
                        y=values,
                        marker_color=colors,
                        text=[f'{currency_symbol}{abs(v):,.0f}' for v in values],
                        textposition='outside'
                    )
                ])
                fig_waterfall.update_layout(
                    title='Monthly Cash Flow by Category',
                    xaxis_title='Category',
                    yaxis_title=f'Amount ({currency_symbol})',
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(family="Arial", size=12),
                    title_font_size=16
                )
                st.plotly_chart(fig_waterfall, use_container_width=True)
    
    else:
        st.info("💡 Add your first transaction to see the dashboard in action!")

# Add Transaction Section
elif selected_section == "💳 Add Transaction":
    st.markdown("## 💳 Add New Transaction")
    
    with st.form("transaction_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            transaction_date = st.date_input(
                "Date",
                value=date.today(),
                max_value=date.today()
            )
            
            transaction_type = st.selectbox(
                "Type",
                options=["Income", "Expense"],
                index=0
            )
        
        with col2:
            categories = db.get_categories(transaction_type)
            category = st.selectbox(
                "Category",
                options=categories,
                index=0
            )
            
            amount = st.number_input(
                f"Amount ({currency_symbol})",
                min_value=0.01,
                value=100.00,
                step=0.01,
                format="%.2f"
            )
        
        description = st.text_area(
            "Description (Optional)",
            placeholder="Enter transaction details...",
            height=100
        )
        
        submitted = st.form_submit_button("💾 Save Transaction", use_container_width=True)
        
        if submitted:
            try:
                db.add_transaction(
                    st.session_state.username,
                    transaction_date.strftime('%Y-%m-%d'),
                    transaction_type,
                    category,
                    amount,
                    description
                )
                refresh_data()
                st.success("✅ Transaction saved successfully!")
                st.balloons()
            except Exception as e:
                st.error(f"❌ Error saving transaction: {str(e)}")

# Ledger Section
elif selected_section == "📋 Ledger":
    st.markdown("## 📋 Transaction Ledger")
    
    if not st.session_state.transactions_df.empty:
        # Filter controls
        col1, col2, col3 = st.columns(3)
        
        with col1:
            filter_type = st.selectbox(
                "Filter by Type",
                options=["All", "Income", "Expense"],
                index=0
            )
        
        with col2:
            all_categories = db.get_categories()
            filter_category = st.selectbox(
                "Filter by Category",
                options=["All"] + all_categories,
                index=0
            )
        
        with col3:
            sort_order = st.selectbox(
                "Sort Order",
                options=["Newest First", "Oldest First"],
                index=0
            )
        
        # Apply filters
        filtered_df = st.session_state.transactions_df.copy()
        
        if filter_type != "All":
            filtered_df = filtered_df[filtered_df['type'] == filter_type]
        
        if filter_category != "All":
            filtered_df = filtered_df[filtered_df['category'] == filter_category]
        
        if sort_order == "Oldest First":
            filtered_df = filtered_df.sort_values(['date', 'id'], ascending=[True, True])
        
        # Display editable data editor
        st.markdown("### 📝 Edit Transactions")
        edited_df = st.data_editor(
            filtered_df[['id', 'date', 'type', 'category', 'amount', 'description']],
            use_container_width=True,
            num_rows="fixed",
            key="ledger_editor",
            column_config={
                "id": st.column_config.NumberColumn(disabled=True),
                "date": st.column_config.DateColumn(required=True),
                "type": st.column_config.SelectboxColumn(
                    options=["Income", "Expense"],
                    required=True
                ),
                "category": st.column_config.TextColumn(required=True),
                "amount": st.column_config.NumberColumn(required=True, min_value=0.01),
                "description": st.column_config.TextColumn()
            }
        )
        
        # Check for changes
        if not filtered_df.equals(edited_df):
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("💾 Save Changes", use_container_width=True):
                    try:
                        for idx, row in edited_df.iterrows():
                            db.update_transaction(
                                int(row['id']),
                                row['date'].strftime('%Y-%m-%d'),
                                row['type'],
                                row['category'],
                                float(row['amount']),
                                row['description']
                            )
                        refresh_data()
                        st.success("✅ Changes saved successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error saving changes: {str(e)}")
            
            with col2:
                if st.button("🔄 Reset Changes", use_container_width=True):
                    if "ledger_editor" in st.session_state:
                        del st.session_state.ledger_editor
                    st.rerun()
        
        # Delete functionality
        st.markdown("---")
        st.markdown("### 🗑️ Delete Transaction")
        
        col1, col2 = st.columns([2, 1])
        with col1:
            delete_id = st.number_input(
                "Enter Transaction ID to delete",
                min_value=1,
                max_value=int(filtered_df['id'].max()) if not filtered_df.empty else 1,
                step=1
            )
        with col2:
            st.write("") # Spacer
            st.write("") # Spacer
            confirm_delete = st.checkbox("⚠️ Enable Deletion")
        
        if st.button("🗑️ Delete Transaction", use_container_width=True, disabled=not confirm_delete):
            try:
                db.delete_transaction(delete_id)
                refresh_data()
                st.success("✅ Transaction deleted successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error deleting transaction: {str(e)}")
    
    else:
        st.info("💡 No transactions found. Add your first transaction to get started!")

# Reports Section
elif selected_section == "📊 Reports":
    st.markdown("## 📊 Monthly Reports")
    
    if not st.session_state.transactions_df.empty:
        # Monthly summary pivot table
        st.markdown(f"### 📈 {calendar.month_name[selected_month]} {selected_year} Summary")
        
        monthly_summary = db.get_monthly_summary(st.session_state.username, selected_year, selected_month)
        
        if not monthly_summary.empty:
            # Create pivot table
            pivot_df = monthly_summary.pivot(index='category', columns='type', values='total').fillna(0)
            pivot_df['Net'] = pivot_df.get('Income', 0) - pivot_df.get('Expense', 0)
            pivot_df = pivot_df.round(2)
            
            # Format currency symbol for column config
            currency_format = f"{currency_symbol}%.2f" if currency_symbol not in ["€"] else f"%.2f{currency_symbol}"
            
            st.dataframe(
                pivot_df,
                use_container_width=True,
                column_config={
                    "Income": st.column_config.NumberColumn(format=currency_format),
                    "Expense": st.column_config.NumberColumn(format=currency_format),
                    "Net": st.column_config.NumberColumn(format=currency_format)
                }
            )
            
            # Export functionality
            st.markdown("---")
            st.markdown("### 📤 Export Data")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Export monthly summary
                csv_summary = pivot_df.to_csv()
                st.download_button(
                    label="📊 Download Monthly Summary (CSV)",
                    data=csv_summary,
                    file_name=f"monthly_summary_{selected_year}_{selected_month:02d}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            
            with col2:
                # Export all transactions
                csv_transactions = st.session_state.transactions_df.to_csv(index=False)
                st.download_button(
                    label="📋 Download All Transactions (CSV)",
                    data=csv_transactions,
                    file_name="all_transactions.csv",
                    mime="text/csv",
                    use_container_width=True
                )
        
        else:
            st.info(f"💡 No transactions found for {calendar.month_name[selected_month]} {selected_year}")
    
    else:
        st.info("💡 No transactions found. Add some transactions to generate reports!")

# Admin Section
elif selected_section == "🔐 Admin":
    if st.session_state.user_role == 'admin':
        admin_dashboard()
    else:
        st.error("⛔ Access Denied")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: #64748b; padding: 1rem;">
        💰 Cashflow Commander - Empowering micro-business financial management
    </div>
    """,
    unsafe_allow_html=True
)