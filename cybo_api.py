# import api key
import os
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv("X-API-KEY")

print(api_key) # testing