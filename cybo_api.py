# import api key
# pip install cybotrade-datasource
import os
import cybotrade_datasource
import pandas as pd
import asyncio
import yfinance as yf
from dotenv import load_dotenv
from datetime import datetime, timezone

# load from .env
load_dotenv()
API_KEY = os.getenv("X-API-KEY")

# List of major cryptocurrencies to track
CRYPTO_SYMBOLS = {
    'BTC-USD': 'Bitcoin',
    'ETH-USD': 'Ethereum',
    'BNB-USD': 'Binance Coin',
    'SOL-USD': 'Solana',
    'XRP-USD': 'Ripple',
    'ADA-USD': 'Cardano',
    'AVAX-USD': 'Avalanche',
    'DOT-USD': 'Polkadot',
    'DOGE-USD': 'Dogecoin',
    'MATIC-USD': 'Polygon'
}

def get_crypto_info(symbol):
    """Get detailed information about a cryptocurrency using yfinance"""
    try:
        crypto = yf.Ticker(symbol)
        info = crypto.info
        
        return {
            'symbol': symbol,
            'name': CRYPTO_SYMBOLS.get(symbol, 'Unknown'),
            'current_price': info.get('currentPrice', 0),
            'market_cap': info.get('marketCap', 0),
            'total_supply': info.get('totalSupply', 0),
            'max_supply': info.get('maxSupply', 0),
            'circulating_supply': info.get('circulatingSupply', 0),
            'volume_24h': info.get('volume24Hr', 0),
            'price_change_24h': info.get('priceChange24Hr', 0),
            'price_change_percent_24h': info.get('priceChangePercent24Hr', 0),
            'all_time_high': info.get('allTimeHigh', 0),
            'all_time_low': info.get('allTimeLow', 0),
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    except Exception as e:
        print(f"Error fetching data for {symbol}: {str(e)}")
        return None

def get_all_crypto_info():
    """Get detailed information for all tracked cryptocurrencies"""
    results = []
    for symbol in CRYPTO_SYMBOLS.keys():
        info = get_crypto_info(symbol)
        if info:
            results.append(info)
    return pd.DataFrame(results)

# print(api_key) # testing
async def main():
    data = await cybotrade_datasource.query_paginated(
        api_key=API_KEY,
        topic='cryptoquant|btc/inter-entity-flows/miner-to-miner?from_miner=f2pool&to_miner=all_miner&window=hour',
        start_time=datetime(year=2023, month=1, day=1, tzinfo=timezone.utc),
        end_time=datetime(year=2024, month=1, day=1, tzinfo=timezone.utc)
    )
    df = pd.DataFrame(data)
    print(df)

async def get_data(startyear, startmonth,startday,endyear,endmonth,endday):
    data = await cybotrade_datasource.query_paginated(
        api_key=API_KEY,
        topic='cryptoquant|btc/inter-entity-flows/miner-to-miner?from_miner=f2pool&to_miner=all_miner&window=hour',
        start_time=datetime(year=startyear, month=startmonth, day=startday, tzinfo=timezone.utc),
        end_time=datetime(year=endyear, month=endmonth, day=endday, tzinfo=timezone.utc)
    )
    df = pd.DataFrame(data)
    print(df)

async def get_data_latest():
    data = await cybotrade_datasource.query_paginated(
        api_key=API_KEY,
        topic='cryptoquant|btc/inter-entity-flows/miner-to-miner?from_miner=f2pool&to_miner=all_miner&window=hour',
        limit=10000
    )
    df = pd.DataFrame(data)
    print(df)

asyncio.run(main()) # test if api key ok
