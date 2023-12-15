import requests
from django.conf import settings

def fetch_stock_symbols():
    url = "https://cloud.iexapis.com/stable/ref-data/symbols"
    params = {
        "token": settings.IEX_API_KEY
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()  # A list of dictionaries with stock info
    else:
        return []
    
def fetch_asset_details(symbol):
    # Construct the URL for detailed stock info
    # This example assumes you're using IEX Cloud's API; adjust as needed for your actual data source
    url = f"https://cloud.iexapis.com/stable/stock/{symbol}/quote?token={settings.IEX_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()  # JSON with detailed stock info
    else:
        return None