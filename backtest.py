# file kosong
# backtesting historical data
#try
#import hmmlearn
#pip install hmmlearn
#pip install yfinance pandas numpy scikit-learn hmmlearn matplotlib
import yfinance as yf
import numpy as np
import pandas as pd
from hmmlearn import hmm
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# ====================
# Data Preparation
# ====================
def fetch_crypto_data(tickers, start_date, end_date):
    data = yf.download(tickers, start=start_date, end=end_date, interval='1d')
    return data['Close']

end_date = datetime.now()
start_date = end_date - timedelta(days=365*3)  # 3 years of data
btc_eth_data = fetch_crypto_data(['BTC-USD', 'ETH-USD'], start_date, end_date)

# ====================
# Feature Engineering
# ====================
def create_features(data):
    returns = data.pct_change().dropna()
    volatility = returns.rolling(window=30).std().shift(1)  # Prevent lookahead bias
    mean_return = returns.rolling(window=30).mean().shift(1)
    
    features = pd.concat([
        returns.rename('return'),
        volatility.rename('volatility'),
        mean_return.rename('mean_return')
    ], axis=1).dropna()
    
    return features

btc_features = create_features(btc_eth_data['BTC-USD'])
eth_features = create_features(btc_eth_data['ETH-USD'])

# ====================
# HMM Modeling
# ====================
def fit_hmm(features, n_components=3):
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(features)
    
    model = hmm.GaussianHMM(
        n_components=n_components,
        covariance_type="diag",
        n_iter=1000,
        random_state=42
    )
    model.fit(scaled_features)
    hidden_states = model.predict(scaled_features)
    
    return model, hidden_states, scaler

btc_model, btc_states, _ = fit_hmm(btc_features)
eth_model, eth_states, _ = fit_hmm(eth_features)

# ====================
# State Interpretation
# ====================
def interpret_states(features, states):
    state_df = features.copy()
    state_df['state'] = states
    
    state_means = state_df.groupby('state').mean()
    ordered_states = state_means['volatility'].sort_values().index
    state_mapping = {ordered_states[0]: 0, ordered_states[1]: 1, ordered_states[2]: 2}
    state_df['mapped_state'] = state_df['state'].map(state_mapping)
    
    return state_df

btc_state_df = interpret_states(btc_features, btc_states)
eth_state_df = interpret_states(eth_features, eth_states)

# ====================
# Signal Generation
# ====================
def generate_signals(btc_states, eth_states, btc_prices, eth_prices):
    signals = pd.DataFrame(index=btc_states.index)
    signals['btc_state'] = btc_states
    signals['eth_state'] = eth_states
    signals['btc_price'] = btc_prices
    signals['eth_price'] = eth_prices
    
    # Initialize positions
    signals['btc_position'] = 0
    signals['eth_position'] = 0
    
    for i in range(1, len(signals)):
        # BTC Rules
        current_btc_state = signals['btc_state'].iloc[i]
        prev_btc_state = signals['btc_state'].iloc[i-1]
        
        if current_btc_state == 0 and prev_btc_state != 0:
            signals.at[signals.index[i], 'btc_position'] = 1
        elif current_btc_state == 2:
            signals.at[signals.index[i], 'btc_position'] = 0
        else:
            signals.at[signals.index[i], 'btc_position'] = signals['btc_position'].iloc[i-1]
        
        # ETH Rules
        current_eth_state = signals['eth_state'].iloc[i]
        prev_eth_state = signals['eth_state'].iloc[i-1]
        
        if current_eth_state == 0 and prev_eth_state != 0:
            signals.at[signals.index[i], 'eth_position'] = 1
        elif current_eth_state == 2:
            signals.at[signals.index[i], 'eth_position'] = 0
        else:
            signals.at[signals.index[i], 'eth_position'] = signals['eth_position'].iloc[i-1]
    
    # Shift positions forward (execute next day)
    signals['btc_position'] = signals['btc_position'].shift(1).fillna(0)
    signals['eth_position'] = signals['eth_position'].shift(1).fillna(0)
    
    return signals

signals = generate_signals(
    btc_state_df['mapped_state'],
    eth_state_df['mapped_state'],
    btc_eth_data['BTC-USD'],
    btc_eth_data['ETH-USD']
)

# ====================
# Backtest Execution
# ====================
def run_backtest(signals, fee=0.001):
    # Calculate daily returns
    signals['btc_return'] = signals['btc_price'].pct_change()
    signals['eth_return'] = signals['eth_price'].pct_change()
    
    # Detect trades (position changes)
    btc_trades = signals['btc_position'].diff().abs().fillna(0)
    eth_trades = signals['eth_position'].diff().abs().fillna(0)
    
    # Calculate strategy returns (with fees)
    signals['strategy_return'] = (
        (signals['btc_position'] * signals['btc_return'] * (1 - fee * btc_trades)) +
        (signals['eth_position'] * signals['eth_return'] * (1 - fee * eth_trades)))
    
    # Cumulative returns
    signals['strategy_cumulative'] = (1 + signals['strategy_return']).cumprod()
    signals['btc_hold'] = (1 + signals['btc_return']).cumprod()
    signals['eth_hold'] = (1 + signals['eth_return']).cumprod()
    
    return signals

signals = run_backtest(signals, fee=0.001)  # 0.1% fee per trade

# ====================
# Performance Analysis
# ====================
def analyze_performance(signals):
    # Calculate key metrics
    total_days = len(signals)
    years = total_days / 365
    
    # Strategy metrics
    total_return = signals['strategy_cumulative'].iloc[-1] - 1
    cagr = (signals['strategy_cumulative'].iloc[-1] ** (1/years)) - 1
    sharpe = (signals['strategy_return'].mean() / signals['strategy_return'].std()) * np.sqrt(252)
    max_drawdown = (signals['strategy_cumulative'] / signals['strategy_cumulative'].cummax() - 1).min()
    
    # Benchmark metrics
    btc_return = signals['btc_hold'].iloc[-1] - 1
    eth_return = signals['eth_hold'].iloc[-1] - 1
    
    print(f"Strategy CAGR: {cagr:.2%}")
    print(f"Strategy Sharpe Ratio: {sharpe:.2f}")
    print(f"Strategy Max Drawdown: {max_drawdown:.2%}")
    print(f"Strategy Total Return: {total_return:.2%}")
    print(f"\nBTC Buy & Hold Return: {btc_return:.2%}")
    print(f"ETH Buy & Hold Return: {eth_return:.2%}")
    
    return {
        'cagr': cagr,
        'sharpe': sharpe,
        'max_drawdown': max_drawdown,
        'total_return': total_return
    }

metrics = analyze_performance(signals)

# ====================
# Visualization
# ====================
def plot_results(signals):
    plt.figure(figsize=(12, 8))
    
    plt.plot(signals['strategy_cumulative'], label='HMM Strategy', linewidth=2)
    plt.plot(signals['btc_hold'], label='BTC Buy & Hold', alpha=0.7)
    plt.plot(signals['eth_hold'], label='ETH Buy & Hold', alpha=0.7)
    
    plt.title('HMM Trading Strategy vs Buy & Hold', fontsize=16)
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Cumulative Return', fontsize=12)
    plt.legend(fontsize=12)
    plt.grid(True)
    
    plt.show()

plot_results(signals)

# ====================
# Trade Analysis
# ====================
def analyze_trades(signals):
    # Count trades
    btc_trades = signals['btc_position'].diff().abs().sum()
    eth_trades = signals['eth_position'].diff().abs().sum()
    
    print(f"\nBTC Trades: {btc_trades:.0f}")
    print(f"ETH Trades: {eth_trades:.0f}")
    print(f"Total Trades: {btc_trades + eth_trades:.0f}")

analyze_trades(signals)


if __name__ == "__main__":
    try:
        # Fetch data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365*3)
        btc_eth_data = fetch_crypto_data(['BTC-USD', 'ETH-USD'], start_date, end_date)
        
        # Generate and analyze signals
        signals = generate_signals(
            btc_state_df['mapped_state'],
            eth_state_df['mapped_state'],
            btc_eth_data['BTC-USD'],
            btc_eth_data['ETH-USD']
        )
        
        # Run backtest
        signals = run_backtest(signals, fee=0.001)
        
        # Display results
        metrics = analyze_performance(signals)
        plot_results(signals)
        analyze_trades(signals)
        
    except Exception as e:
        print(f"Error running backtest: {str(e)}")