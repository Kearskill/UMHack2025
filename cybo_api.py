# import api key
# pip install cybotrade-datasource
import os
import cybotrade_datasource
import pandas as pd
import asyncio
from dotenv import load_dotenv
from datetime import datetime, timezone

# load from .env
load_dotenv()
API_KEY = os.getenv("X-API-KEY")

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
