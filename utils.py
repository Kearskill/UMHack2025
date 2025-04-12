import yfinance as yf
import os
from dotenv import load_dotenv

# test yfinance
try:
    data = yf.Ticker("BTC-USD")
    hist = data.history(period="10d",interval="1h")
    print(hist)

except Exception as e:
    print("Error:", e)

# test api
load_dotenv()
API_KEY = os.getenv("X-API-KEY")
print(API_KEY)