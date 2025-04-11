import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
import time

from cybo_api import get_data
from datetime import datetime, timedelta

# Page configuration
st.set_page_config(

    page_title="Crypto Trading Signal Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main {
        padding: 20px;
    }
    .stSelectbox {
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# Title
st.title("🚀 Crypto Trading Signal Dashboard")

# Cryptocurrency selection
crypto_options = {
    "Bitcoin": "BTC-USD",  # Yahoo Finance format
    "Ethereum": "ETH-USD",  # Yahoo Finance format
    "XRP": "XRP-USD"       # Yahoo Finance format
}

selected_crypto = st.selectbox(
    "Select Cryptocurrency",
    list(crypto_options.keys())
)

# Time period selection
timeframe = st.selectbox(
    "Select Timeframe",
    ["1D", "5D", "1M", "3M", "6M", "1Y"]
)

# Convert timeframe to days
timeframe_days = {
    "1D": 1,
    "5D": 5,
    "1M": 30,
    "3M": 90,
    "6M": 180,
    "1Y": 365
}

@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_crypto_data(symbol, days):
    try:
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # For 1D and 5D, use 1h interval, otherwise use 1d
        interval = "1h" if days <= 5 else "1d"
        
        # Download data with retries
        for attempt in range(3):  # Try 3 times
            try:
                df = yf.download(
                    tickers=symbol,
                    start=start_date,
                    end=end_date,
                    interval=interval,
                    progress=False,
                    threads=False,  # Disable multi-threading to avoid potential issues
                    timeout=10
                )
                if not df.empty:
                    break
            except Exception as e:
                if attempt == 2:  # Last attempt
                    raise e
                time.sleep(1)  # Wait before retry
        
        if df.empty:
            st.error(f"No data available for {symbol}. Trying alternative symbol format...")
            # Try alternative symbol format
            alt_symbol = symbol.replace('-', '')  # Try without hyphen
            df = yf.download(
                tickers=alt_symbol,
                start=start_date,
                end=end_date,
                interval=interval,
                progress=False,
                threads=False
            )
        
        if df.empty:
            st.error(f"No data available for {symbol} or {alt_symbol}")
            return pd.DataFrame()
            
        # Ensure all required columns exist
        required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        if not all(col in df.columns for col in required_columns):
            st.error(f"Missing required price data for {symbol}")
            return pd.DataFrame()
            
        return df
        
    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")
        return pd.DataFrame()

# Get data
with st.spinner('Fetching cryptocurrency data...'):
    df = fetch_crypto_data(crypto_options[selected_crypto], timeframe_days[timeframe])

if not df.empty:
    # Calculate technical indicators
    def calculate_signals(df):
        # Simple example using Moving Averages
        df['SMA20'] = df['Close'].rolling(window=20, min_periods=1).mean()
        df['SMA50'] = df['Close'].rolling(window=50, min_periods=1).mean()
        
        # Generate trading signals (simple example)
        df['Signal'] = 'HOLD'
        df.loc[df['SMA20'] > df['SMA50'], 'Signal'] = 'BUY'
        df.loc[df['SMA20'] < df['SMA50'], 'Signal'] = 'SELL'
        
        return df

    df = calculate_signals(df)

    # Create the main price chart
    fig = go.Figure()

    # Add candlestick chart
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name='Price'
    ))

    # Add moving averages
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['SMA20'],
        name='20 Period MA',
        line=dict(color='orange')
    ))

    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['SMA50'],
        name='50 Period MA',
        line=dict(color='blue')
    ))

    # Update layout
    fig.update_layout(
        title=f"{selected_crypto} Price Chart",
        yaxis_title="Price (USD)",
        xaxis_title="Date",
        template="plotly_dark",
        height=600
    )

    # Display the chart
    st.plotly_chart(fig, use_container_width=True)

    # Display current trading signal
    current_signal = df['Signal'].iloc[-1]
    signal_color = {
        'BUY': 'green',
        'SELL': 'red',
        'HOLD': 'yellow'
    }

    st.markdown(f"""
        <div style='background-color: {signal_color[current_signal]}; padding: 20px; border-radius: 10px; text-align: center;'>
            <h2 style='color: black; margin: 0;'>Current Signal: {current_signal}</h2>
        </div>
    """, unsafe_allow_html=True)

    # Display key metrics
    col1, col2, col3 = st.columns(3)

    with col1:
        current_price = float(df['Close'].iloc[-1])  # Convert to float
        st.metric("Current Price", f"${current_price:.2f}")

    with col2:
        price_change = float(df['Close'].iloc[-1] - df['Close'].iloc[-2])  # Convert to float
        price_change_pct = float((price_change / df['Close'].iloc[-2]) * 100)  # Convert to float
        st.metric("Price Change", f"${price_change:.2f}", f"{price_change_pct:.2f}%")

    with col3:
        daily_volume = float(df['Volume'].iloc[-1])  # Convert to float
        st.metric("24h Volume", f"${daily_volume:,.0f}")

else:
    st.error("""
    Unable to fetch cryptocurrency data. This could be due to:
    1. Network connectivity issues
    2. Market hours (some data may not be available during certain hours)
    3. Invalid symbol
    
    Please try:
    1. Refreshing the page
    2. Selecting a different timeframe
    3. Checking your internet connection
    """)