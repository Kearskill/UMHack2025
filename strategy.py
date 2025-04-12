import yfinance as yf
from sklearn.preprocessing import StandardScaler  # Add this at the top
import numpy as np
import pandas as pd
from hmmlearn import hmm
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# Fetch data from Yahoo Finance
def fetch_crypto_data(tickers, start_date, end_date):
    data = yf.download(tickers, start=start_date, end=end_date, interval='1d')
    return data['Close']

# Example usage
end_date = datetime.now()
start_date = end_date - timedelta(days=365*3)  # 3 years of data
btc_eth_data = fetch_crypto_data(['BTC-USD', 'ETH-USD'], start_date, end_date)

def create_features(data):
    # Calculate daily returns
    returns = data.pct_change().dropna()
    
    # Calculate rolling volatility (30-day)
    volatility = returns.rolling(window=30).std().shift(1)  # Add shift(1)
    mean_return = returns.rolling(window=30).mean().shift(1)
    
    # Combine features
    features = pd.concat([
        returns.rename('return'),
        volatility.rename('volatility'),
        mean_return.rename('mean_return')
    ], axis=1).dropna()
    
    return features

btc_features = create_features(btc_eth_data['BTC-USD'])
eth_features = create_features(btc_eth_data['ETH-USD'])
def fit_hmm(features, n_components=3):
    # Standardize features
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(features)
    
    # Fit Gaussian HMM
    model = hmm.GaussianHMM(
        n_components=n_components,
        covariance_type="diag",
        n_iter=1000,
        random_state=42
    )
    model.fit(scaled_features)
    
    # Predict hidden states
    hidden_states = model.predict(scaled_features)
    
    return model, hidden_states, scaler

# Fit models for BTC and ETH
btc_model, btc_states, btc_scaler = fit_hmm(btc_features)
eth_model, eth_states, eth_scaler = fit_hmm(eth_features)

def interpret_states(features, states, model):
    # Create DataFrame with states
    state_df = features.copy()
    state_df['state'] = states
    
    # Calculate mean metrics per state
    state_means = state_df.groupby('state').mean()
    
    # Order states by volatility (assuming 3 states: low, medium, high volatility)
    ordered_states = state_means['volatility'].sort_values().index
    
    # Create state mapping (0=low volatility, 1=medium, 2=high)
    state_mapping = {ordered_states[0]: 0, ordered_states[1]: 1, ordered_states[2]: 2}
    state_df['mapped_state'] = state_df['state'].map(state_mapping)
    
    return state_df

btc_state_df = interpret_states(btc_features, btc_states, btc_model)
eth_state_df = interpret_states(eth_features, eth_states, eth_model)

def generate_signals(btc_states, eth_states, btc_prices, eth_prices):
    signals = pd.DataFrame(index=btc_states.index)
    signals['btc_state'] = btc_states
    signals['eth_state'] = eth_states
    signals['btc_price'] = btc_prices
    signals['eth_price'] = eth_prices
    
    # Initialize positions and actions
    signals['btc_position'] = 0
    signals['eth_position'] = 0
    signals['btc_action'] = 'hold'
    signals['eth_action'] = 'hold'
    
    for i in range(1, len(signals)):
        # BTC Rules
        prev_btc_state = signals['btc_state'].iloc[i-1]
        current_btc_state = signals['btc_state'].iloc[i]
        
        if current_btc_state == 0 and prev_btc_state != 0:  # Transition to low volatility
            signals.at[signals.index[i], 'btc_position'] = 1
            signals.at[signals.index[i], 'btc_action'] = 'buy'
        elif current_btc_state == 2:  # High volatility
            signals.at[signals.index[i], 'btc_position'] = 0
            signals.at[signals.index[i], 'btc_action'] = 'sell'
        else:  # Maintain position
            signals.at[signals.index[i], 'btc_position'] = signals['btc_position'].iloc[i-1]
            signals.at[signals.index[i], 'btc_action'] = 'hold'
        
        # ETH Rules
        prev_eth_state = signals['eth_state'].iloc[i-1]
        current_eth_state = signals['eth_state'].iloc[i]
        
        if current_eth_state == 0 and prev_eth_state != 0:  # Transition to low volatility
            signals.at[signals.index[i], 'eth_position'] = 1
            signals.at[signals.index[i], 'eth_action'] = 'buy'
        elif current_eth_state == 2:  # High volatility
            signals.at[signals.index[i], 'eth_position'] = 0
            signals.at[signals.index[i], 'eth_action'] = 'sell'
        else:  # Maintain position
            signals.at[signals.index[i], 'eth_position'] = signals['eth_position'].iloc[i-1]
            signals.at[signals.index[i], 'eth_action'] = 'hold'
    
    # Combine actions into a single column
    signals['action'] = signals.apply(
        lambda x: ' | '.join([f"BTC:{x['btc_action']}", f"ETH:{x['eth_action']}"]), 
        axis=1
    )
    
    # Simplify action display
    signals['action'] = signals['action'].replace({
        'BTC:hold | ETH:hold': 'hold',
        'BTC:buy | ETH:hold': 'buy BTC',
        'BTC:sell | ETH:hold': 'sell BTC',
        'BTC:hold | ETH:buy': 'buy ETH',
        'BTC:hold | ETH:sell': 'sell ETH',
        'BTC:buy | ETH:buy': 'buy both',
        'BTC:sell | ETH:sell': 'sell both',
        'BTC:buy | ETH:sell': 'buy BTC & sell ETH',
        'BTC:sell | ETH:buy': 'sell BTC & buy ETH'
    })
    
    return signals