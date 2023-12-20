from decimal import Decimal
import numpy as np
import requests
from django.conf import settings
from .models import PortfolioDetails

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
    
# Modify this function to get a different rate based on factors: Time investment is going to be held, historical performance, interest rate environment
def get_risk_free_rate():
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "TREASURY_YIELD",
        "interval": "monthly",
        "maturity": "10year",
        "apikey": settings.ALPHA_VANTAGE_API_KEY,
        "entitlement": "delayed"
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        # The latest yield is the risk-free rate
        # Assuming the JSON structure has the dates as keys
        latest_rate = data['data'][0]['value']
        return float(latest_rate) / 100  # Convert percentage to decimal
    else:
        return None  # Or handle the error as appropriate

# symbol is the market index we want to track
def get_expected_market_return(symbol):
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": symbol,
        "outputsize": "full",
        "apikey": settings.ALPHA_VANTAGE_API_KEY,
        "entitlement": "delayed"
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data and 'Time Series (Daily)' in data:
            # Extract closing prices
            closing_prices = [float(day_data['4. close']) for date, day_data in data['Time Series (Daily)'].items()]

            # Calculate daily returns
            daily_returns = [(closing_prices[i] / closing_prices[i + 1] - 1) for i in range(len(closing_prices) - 1)]

            # Compute the average annual return
            # Assuming 252 trading days in a year
            average_daily_return = sum(daily_returns) / len(daily_returns)
            average_annual_return = (1 + average_daily_return) ** 252 - 1

            return average_annual_return
    else:
        return None
    return None

def get_asset_beta(symbol):
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "OVERVIEW",
        "symbol": symbol,
        "outputsize": "full",
        "apikey": settings.ALPHA_VANTAGE_API_KEY,
        "entitlement": "delayed"
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data and "Beta" in data:
            return data["Beta"]
    else:
        return None
    return None


def get_expected_stock_return(symbol, risk_free_rate, expected_market_return):
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "OVERVIEW",
        "symbol": symbol,
        "outputsize": "full",
        "apikey": settings.ALPHA_VANTAGE_API_KEY,
        "entitlement": "delayed"
    }
    response = requests.get(url, params=params)
    if response.status_code == 200 and risk_free_rate and expected_market_return:
        data = response.json()
        beta = data["Beta"]
        risk_premium = expected_market_return - risk_free_rate
        stock_risk_premium = float(beta) * risk_premium
        expected_return = risk_free_rate + stock_risk_premium
        return expected_return
    else:
        return None
    
def get_stock_stddev(symbol):
    url = "https://alphavantageapi.co/timeseries/analytics"
    params = {
        "SYMBOLS": symbol,
        "RANGE": "2023-07-01",
        "RANGE": "2023-08-31",
        "INTERVAL": "DAILY",
        "CALCULATIONS": "STDDEV",
        "apikey": settings.ALPHA_VANTAGE_API_KEY,
        "entitlement": "delayed"
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        std_dev = data["payload"]["RETURNS_CALCULATIONS"]["STDDEV"][symbol]
        return std_dev
    else:
        return None
    
def get_asset_price(symbol):
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "GLOBAL_QUOTE",
        "symbol": symbol,
        "outputsize": "full",
        "apikey": settings.ALPHA_VANTAGE_API_KEY
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data and "Global Quote" in data:
            return data["Global Quote"]['05. price']
    else:
        return None
    return None
    
def fetch_asset_details(symbol):
    # Construct the URL for detailed stock info
    # This example assumes you're using IEX Cloud's API; adjust as needed for your actual data source
    #url = f"https://cloud.iexapis.com/stable/stock/{symbol}/quote?token={settings.IEX_API_KEY}"
    url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={symbol}&apikey={settings.ALPHA_VANTAGE_API_KEY}&entitlement=delayed"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        risk_free_rate = get_risk_free_rate()
        expected_market_return = get_expected_market_return('SPY')
        stock_price = float(get_asset_price(symbol))
        std_dev = get_stock_stddev(symbol)
        data['Risk_free_rate'] = f"{risk_free_rate:.3%}"
        data['Expected_market_return'] = f"{expected_market_return:.3%}"
        data['Expected_return'] = f"{get_expected_stock_return(symbol, risk_free_rate, expected_market_return):.3%}"
        data['Asset_price'] = f"USD ${stock_price:.2f}"
        data['Std_dev'] = std_dev

        return data # JSON with detailed stock info
    else:
        return None
    
def get_portfolio_stddev(asset_details):
    asset_symbols = [asset.symbol for asset in asset_details]
    symbols = ','.join(asset_symbols)
    url = "https://alphavantageapi.co/timeseries/analytics"
    params = {
        "SYMBOLS": symbols,
        "RANGE": "2023-07-01", # Update range
        "RANGE": "2023-08-31",
        "INTERVAL": "DAILY",
        "CALCULATIONS": "COVARIANCE",
        "apikey": settings.ALPHA_VANTAGE_API_KEY,
        "entitlement": "delayed"
    }
    response = requests.get(url, params)
    print(response)
    if response.status_code == 200:
        data = response.json()
        size = len(data['payload']['RETURNS_CALCULATIONS']['COVARIANCE']["index"])
        cov_matrix = np.zeros((size, size))
        for i in range(size):
            for j in range(i + 1):
                cov_matrix[i, j] = data['payload']['RETURNS_CALCULATIONS']['COVARIANCE']["covariance"][i][j]
                cov_matrix[j, i] = data['payload']['RETURNS_CALCULATIONS']['COVARIANCE']["covariance"][i][j]


        # Step 2: Define portfolio weights
        weights_list = [asset.weight for asset in asset_details]
        weights = np.array(weights_list)

        decimal_cov_matrix = [[Decimal(value) for value in row] for row in cov_matrix]

        # Step 3: Calculate portfolio variance
        portfolio_variance = np.dot(weights, np.dot(decimal_cov_matrix, weights.T))
        portfolio_stddev = float(portfolio_variance) ** 0.5

        return portfolio_stddev
    else:
        return None
    
def calculate_portfolio_details(portfolioAssets):
    portfolio_details = PortfolioDetails()
    risk_free_rate = get_risk_free_rate()
    expected_market_return = get_expected_market_return('SPY')

    for asset_ticker, quantity in portfolioAssets.items():
        # Here, you need to fetch or calculate the asset's price, std_dev, expected_return, and beta
        # For example, using a function get_asset_data(symbol) that returns these values
        quan = quantity

        price = get_asset_price(asset_ticker)
        std_dev = get_stock_stddev(asset_ticker)
        expected_return = get_expected_stock_return(asset_ticker, risk_free_rate, expected_market_return)
        beta = get_asset_beta(asset_ticker)

        # Calculate the total value of the asset in the portfolio
        total_asset_value = Decimal(price) * quan
        portfolio_details.total_value += total_asset_value

        # Append the asset details to the portfolio
        asset_details = PortfolioDetails.AssetDetails(
            asset_ticker, quan, price, std_dev, expected_return, beta, 0  # Weight to be calculated later
        )
        portfolio_details.assets_details.append(asset_details)

    # Calculate weight, expected portfolio return, and standard deviation
    for asset_detail in portfolio_details.assets_details:
        # Calculate weight of each asset
        asset_detail.weight = (Decimal(asset_detail.price) * asset_detail.quantity) / portfolio_details.total_value

        # Add to expected portfolio return
        portfolio_details.expected_return += Decimal(asset_detail.expected_return) * asset_detail.weight
    
    portfolio_details.standard_deviation = get_portfolio_stddev(portfolio_details.assets_details)

    if portfolio_details.standard_deviation is not None:
        portfolio_details.sharpe_ratio = (portfolio_details.expected_return - Decimal(risk_free_rate))/Decimal(portfolio_details.standard_deviation)
        portfolio_details.standard_deviation = f"{float(portfolio_details.standard_deviation):.3%}"
        portfolio_details.sharpe_ratio = f"{float(portfolio_details.sharpe_ratio):.5f}"
    else:
        portfolio_details.sharpe_ratio = "NA"
    portfolio_details.total_value = f"USD ${portfolio_details.total_value:.2f}"
    portfolio_details.expected_return = f"{portfolio_details.expected_return:.3%}"

    return portfolio_details