import requests
import pandas as pd

def fetch_historical_data(symbol, start_date):
    api_url = "https://historicalapi-js.onrender.com/historical"
    #api_url = "https://4d23edcc-c01a-4fa1-843c-d10f5859c722-00-13kh8zyk0cgze.riker.replit.dev/historicalapi/historical"
    params = {"symbol": symbol, "from": start_date.strftime("%d-%m-%Y")}
    response = requests.get(api_url, params=params)
    if response.status_code == 200:
        data = response.json().get("data", [])
        return pd.DataFrame(data)
    else:
        return pd.DataFrame()
