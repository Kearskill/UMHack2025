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
        
        def get_value_or_na(value, default=0):
            return value if value and value != 0 else "N/A"
        
        # Try different possible keys for max supply
        max_supply = info.get('maxSupply', 
                    info.get('totalSupply', 
                    info.get('circulatingSupply', 0)))
        
        return {
            'symbol': symbol,
            'name': CRYPTO_SYMBOLS.get(symbol, 'Unknown'),
            'current_price': get_value_or_na(info.get('currentPrice')),
            'market_cap': get_value_or_na(info.get('marketCap')),
            'total_supply': get_value_or_na(info.get('totalSupply', info.get('circulatingSupply'))),
            'max_supply': get_value_or_na(max_supply),
            'circulating_supply': get_value_or_na(info.get('circulatingSupply')),
            'volume_24h': get_value_or_na(info.get('volume24Hr')),
            'price_change_24h': get_value_or_na(info.get('priceChange24Hr')),
            'price_change_percent_24h': get_value_or_na(info.get('priceChangePercent24Hr')),
            'all_time_high': get_value_or_na(info.get('fiftyTwoWeekHigh', info.get('allTimeHigh'))),
            'all_time_low': get_value_or_na(info.get('fiftyTwoWeekLow', info.get('allTimeLow'))),
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

# Only run main() if this file is executed directly
if __name__ == "__main__":
    asyncio.run(main()) # test if api key ok
