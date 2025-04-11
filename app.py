import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from cybo_api import get_data
from datetime import datetime, timedelta

# Page configuration
st.set_page_config(
    page_title="Financial Dashboard",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        background-color: #F5F5F5;
    }
    .sidebar .sidebar-content {
        background-color: #2C3E50;
        color: white;
    }
    .widget-label {
        color: white !important;
    }
    h1, h2, h3 {
        color: #2C3E50;
    }
    </style>
    """, unsafe_allow_html=True)


# Sample data generation functions
def generate_portfolio_data():
    np.random.seed(42)
    assets = ['Stocks', 'Bonds', 'Real Estate', 'Cash', 'Commodities']
    allocations = np.random.dirichlet(np.ones(5), size=1)[0] * 100
    returns = np.random.normal(0.05, 0.15, 5)
    data = {
        'Asset': assets,
        'Allocation (%)': allocations.round(2),
        'Annual Return (%)': (returns * 100).round(2)
    }
    return pd.DataFrame(data)


def generate_transaction_history():
    np.random.seed(42)
    dates = pd.date_range(end=datetime.today(), periods=30).date
    categories = ['Salary', 'Investment', 'Groceries', 'Utilities', 'Entertainment', 'Transport']
    amounts = np.random.randint(50, 2000, 30) * np.random.choice([1, -1], 30)
    descriptions = [f"Transaction {i + 1}" for i in range(30)]

    data = {
        'Date': dates,
        'Description': descriptions,
        'Category': np.random.choice(categories, 30),
        'Amount': amounts
    }
    return pd.DataFrame(data).sort_values('Date', ascending=False)


def generate_stock_data():
    np.random.seed(42)
    dates = pd.date_range(start='2023-01-01', end=datetime.today())
    stocks = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA']
    data = []

    for stock in stocks:
        prices = np.cumprod(1 + np.random.normal(0.001, 0.02, len(dates))) * 100
        for date, price in zip(dates, prices):
            data.append({
                'Date': date,
                'Stock': stock,
                'Price': round(price, 2)
            })

    return pd.DataFrame(data)


# Sidebar
with st.sidebar:
    st.title("Financial Dashboard")

    st.header("Navigation")
    page = st.radio("Go to", ["Overview", "Portfolio", "Transactions", "Investments", "Budget"])

    st.header("Settings")
    currency = st.selectbox("Currency", ["USD", "EUR", "GBP", "JPY"])
    start_date = st.date_input("Start Date", datetime.today() - timedelta(days=365))
    end_date = st.date_input("End Date", datetime.today())

    st.header("Account")
    st.metric("Total Balance", "$45,678.90")
    st.progress(75)
    st.caption("75% of annual savings goal")

# Main content
if page == "Overview":
    st.title("Financial Overview")

    # KPI cards
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Net Worth", "$125,432.10", "5.2%")
    with col2:
        st.metric("Monthly Income", "$5,200.00", "3.1%")
    with col3:
        st.metric("Monthly Expenses", "$3,850.50", "-2.4%")

    # Charts
    st.subheader("Monthly Cash Flow")
    cash_flow_data = pd.DataFrame({
        'Month': pd.date_range(start='2023-01-01', periods=12, freq='M').strftime('%b %Y'),
        'Income': np.random.randint(4000, 6000, 12),
        'Expenses': np.random.randint(3000, 4500, 12)
    })
    fig = px.bar(cash_flow_data, x='Month', y=['Income', 'Expenses'], barmode='group')
    st.plotly_chart(fig, use_container_width=True)

    # Net worth trend
    st.subheader("Net Worth Trend")
    net_worth_data = pd.DataFrame({
        'Date': pd.date_range(start='2023-01-01', periods=12, freq='ME'),
        'Net Worth': np.cumsum(np.random.normal(5000, 2000, 12)) + 100000
    })
    fig = px.line(net_worth_data, x='Date', y='Net Worth')
    st.plotly_chart(fig, use_container_width=True)

elif page == "Portfolio":
    st.title("Investment Portfolio")

    portfolio_data = generate_portfolio_data()

    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader("Asset Allocation")
        fig = px.pie(portfolio_data, values='Allocation (%)', names='Asset')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Portfolio Performance")
        fig = px.bar(portfolio_data, x='Asset', y='Annual Return (%)')
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Portfolio Details")
    st.dataframe(portfolio_data.style.format({
        'Allocation (%)': '{:.2f}%',
        'Annual Return (%)': '{:.2f}%'
    }))

elif page == "Transactions":
    st.title("Transaction History")

    transaction_data = generate_transaction_history()

    # Filters
    col1, col2 = st.columns(2)
    with col1:
        category_filter = st.multiselect(
            "Filter by Category",
            options=transaction_data['Category'].unique(),
            default=transaction_data['Category'].unique()
        )
    with col2:
        date_filter = st.date_input(
            "Filter by Date Range",
            value=[start_date, end_date]
        )

    filtered_data = transaction_data[
        (transaction_data['Category'].isin(category_filter)) &
        (transaction_data['Date'].between(date_filter[0], date_filter[1]))
        ]

    # Summary stats
    income = filtered_data[filtered_data['Amount'] > 0]['Amount'].sum()
    expenses = filtered_data[filtered_data['Amount'] < 0]['Amount'].sum()

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Income", f"${income:,.2f}")
    with col2:
        st.metric("Total Expenses", f"${abs(expenses):,.2f}")

    # Transaction table
    st.subheader("Transaction Details")
    st.dataframe(filtered_data.style.format({
        'Amount': '${:,.2f}'
    }))

    # Spending by category
    st.subheader("Spending by Category")
    spending_data = filtered_data[filtered_data['Amount'] < 0].groupby('Category')['Amount'].sum().reset_index()
    spending_data['Amount'] = spending_data['Amount'].abs()
    fig = px.bar(spending_data, x='Category', y='Amount')
    st.plotly_chart(fig, use_container_width=True)

elif page == "Investments":
    st.title("Investment Performance")

    stock_data = generate_stock_data()
    selected_stocks = st.multiselect(
        "Select Stocks",
        options=stock_data['Stock'].unique(),
        default=stock_data['Stock'].unique()[:3]
    )

    filtered_data = stock_data[
        (stock_data['Stock'].isin(selected_stocks)) &
        (stock_data['Date'].between(pd.to_datetime(start_date), pd.to_datetime(end_date)))
        ]

    # Price trends
    st.subheader("Price Trends")
    fig = px.line(filtered_data, x='Date', y='Price', color='Stock')
    st.plotly_chart(fig, use_container_width=True)

    # Returns calculation
    st.subheader("Returns Analysis")
    returns_data = filtered_data.pivot(index='Date', columns='Stock', values='Price')
    returns_data = returns_data.pct_change().dropna()

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Average Daily Return", f"{returns_data.mean().mean():.2%}")
    with col2:
        st.metric("Volatility", f"{returns_data.std().mean():.2%}")

    # Correlation matrix
    st.subheader("Correlation Matrix")
    fig = px.imshow(returns_data.corr(), text_auto=True)
    st.plotly_chart(fig, use_container_width=True)

elif page == "Budget":
    st.title("Budget Planner")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Income Sources")
        income_sources = pd.DataFrame({
            'Source': ['Salary', 'Freelance', 'Investments', 'Other'],
            'Amount': [4000, 800, 500, 200]
        })
        st.dataframe(income_sources.style.format({
            'Amount': '${:,.2f}'
        }))

        new_source = st.text_input("Add New Income Source")
        new_amount = st.number_input("Amount", min_value=0.0, format="%.2f")
        if st.button("Add Income Source"):
            st.success(f"Added {new_source}: ${new_amount:,.2f}")

    with col2:
        st.subheader("Expense Categories")
        expense_categories = pd.DataFrame({
            'Category': ['Housing', 'Food', 'Transport', 'Entertainment', 'Utilities'],
            'Budget': [1200, 600, 300, 200, 150],
            'Actual': [1250, 550, 320, 180, 160]
        })
        st.dataframe(expense_categories.style.format({
            'Budget': '${:,.2f}',
            'Actual': '${:,.2f}'
        }))

        new_category = st.text_input("Add New Expense Category")
        new_budget = st.number_input("Budget Amount", min_value=0.0, format="%.2f")
        if st.button("Add Expense Category"):
            st.success(f"Added {new_category}: ${new_budget:,.2f}")

    # Budget vs Actual
    st.subheader("Budget vs Actual")
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=expense_categories['Category'],
        y=expense_categories['Budget'],
        name='Budget'
    ))
    fig.add_trace(go.Bar(
        x=expense_categories['Category'],
        y=expense_categories['Actual'],
        name='Actual'
    ))
    st.plotly_chart(fig, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("""
    *Financial Dashboard Template*  
    *Created with Streamlit*  
    *Data is simulated for demonstration purposes*
""")