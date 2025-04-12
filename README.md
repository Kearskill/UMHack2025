# Crypto Trading Signal Dashboard

A streamlined cryptocurrency trading dashboard that provides real-time price data and trading signals for Bitcoin, Ethereum, and XRP. The application uses technical analysis to generate BUY, SELL, or HOLD signals based on Moving Average crossover strategy.

## Slides link
[Slide](https://github.com/Kearskill/UMHack2025/blob/main/UMHackathon_2025_presentation.pdf)

## Features

- Real-time cryptocurrency price data
- Interactive candlestick charts
- Technical indicators (20 and 50-period Moving Averages)
- Trading signals based on MA crossover
- Support for multiple timeframes (1D to 1Y)
- Key metrics display (Price, Change, Volume)

## Setup Instructions

1. Clone the repository:
```bash
git clone <repository-url>
cd <repository-name>
```

2. Create and activate a virtual environment:
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux/Mac
python -m venv venv
source venv/bin/activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

## Running the Application

1. Make sure your virtual environment is activated:
```bash
# Windows
.\venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

2. Run the Streamlit app:
```bash
streamlit run app.py
```

The application will open in your default web browser at `http://localhost:8501`.

## Usage

1. Select a cryptocurrency from the dropdown menu (Bitcoin, Ethereum, or XRP)
2. Choose your preferred timeframe
3. View the interactive price chart with technical indicators
4. Monitor the current trading signal and key metrics
5. Use the trading signals as part of your broader trading strategy

## Note

This is a prototype for demonstration purposes. The trading signals are based on a simple Moving Average crossover strategy and should not be used as the sole basis for trading decisions. Always conduct your own research and consider multiple factors before making trading decisions.

```
quant_trading_app/
│
├── app.py              # Streamlit frontend
├── strategy.py         # Your alpha logic
├── backtest.py         # Run backtests on historical data
├── cybo_api.py         # Wrap CyboTrade API calls (get price, place trade, etc.)
├── data/               # CSVs, cached data
└── utils.py            # Misc helpers (plotting, metrics)
```
