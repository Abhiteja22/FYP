from decimal import Decimal
import numpy as np
from scipy.optimize import minimize
import requests
from django.conf import settings
from .models import PortfolioDetails

# Modify this function to get a different rate based on factors: Time investment is going to be held, historical performance, interest rate environment
def get_risk_free_rate(time_period):
    url = settings.ALPHA_VANTAGE_QUERY_URL
    params = {
        "function": "TREASURY_YIELD",
        "interval": "monthly",
        "maturity": time_period,
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

# Get Expected Market Return (symbol: market index to track)
def get_expected_market_return(symbol, investment_time_period):
    if investment_time_period == '3month':
        func = "TIME_SERIES_DAILY_ADJUSTED"
        data_feature = 'Time Series (Daily)'
        annualising_factor = 252
    elif investment_time_period == '2year':
        func = "TIME_SERIES_WEEKLY_ADJUSTED"
        data_feature = 'Weekly Adjusted Time Series'
        annualising_factor = 52
    else:
        func = "TIME_SERIES_MONTHLY_ADJUSTED"
        data_feature = 'Monthly Adjusted Time Series'
        annualising_factor = 12
    url = settings.ALPHA_VANTAGE_QUERY_URL
    params = {
        "function": func,
        "symbol": symbol,
        "outputsize": "full",
        "apikey": settings.ALPHA_VANTAGE_API_KEY,
        "entitlement": "delayed"
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data and data_feature in data:
            # Extract closing prices
            adjusted_closing_prices = [float(day_data['5. adjusted close']) for date, day_data in data[data_feature].items()]
            # Calculate daily returns
            returns = [(adjusted_closing_prices[i] / adjusted_closing_prices[i + 1] - 1) for i in range(len(adjusted_closing_prices) - 1)]
            # Compute the average annual return
            # Assuming 252 trading days in a year
            average_return = sum(returns) / len(returns)
            average_annual_return = (1 + average_return) ** annualising_factor - 1
            return average_annual_return
    else:
        return None
    return None

def get_asset_beta(symbol):
    url = settings.ALPHA_VANTAGE_QUERY_URL
    params = {
        "function": "OVERVIEW",
        "symbol": symbol,
        "apikey": settings.ALPHA_VANTAGE_API_KEY,
        "entitlement": "delayed"
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data and "Beta" in data:
            return float(data["Beta"])
    else:
        return None
    return None

def get_asset_price(symbol):
    url = settings.ALPHA_VANTAGE_QUERY_URL
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

def calculate_expected_stock_return(beta, risk_free_rate, expected_market_return):
    risk_premium = expected_market_return - risk_free_rate
    stock_risk_premium = beta * risk_premium
    expected_return = risk_free_rate + stock_risk_premium
    
    return expected_return
    
def get_stock_stddev(symbol):
    url = settings.ALPHA_VANTAGE_ANALYTICS_URL
    params = {
        "SYMBOLS": symbol,
        "RANGE": "2020-01-01", # TODO: Handle error where stock is newer than this date
        "INTERVAL": "DAILY", # TODO: DAILY data can be noisy, decide later based on investor's goals
        "CALCULATIONS": "STDDEV",
        "apikey": settings.ALPHA_VANTAGE_API_KEY,
        "entitlement": "delayed"
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        print(data)
        std_dev = data["payload"]["RETURNS_CALCULATIONS"]["STDDEV"][symbol]
        return std_dev
    else:
        return None
    
def fetch_asset_details(symbol):
    url = settings.ALPHA_VANTAGE_QUERY_URL
    params = {
        "function": "OVERVIEW",
        "symbol": symbol,
        "apikey": settings.ALPHA_VANTAGE_API_KEY,
        "entitlement": "delayed"
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        risk_free_rate = get_risk_free_rate()
        expected_market_return = get_expected_market_return('SPY')
        stock_price = float(get_asset_price(symbol))
        std_dev = get_stock_stddev(symbol)
        beta = get_asset_beta(symbol)
        data['Risk_free_rate'] = f"{risk_free_rate:.3%}"
        data['Expected_market_return'] = f"{expected_market_return:.3%}"
        data['Expected_return'] = f"{calculate_expected_stock_return(beta, risk_free_rate, expected_market_return):.3%}"
        data['Asset_price'] = f"USD ${stock_price:.2f}"
        data['Std_dev'] = std_dev

        return data # JSON with detailed stock info
    else:
        return None
    
def get_portfolio_stddev(asset_details):
    asset_symbols = [asset.symbol for asset in asset_details]
    symbols = ','.join(asset_symbols)
    url = settings.ALPHA_VANTAGE_ANALYTICS_URL
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
    if response.status_code == 200:
        data = response.json()
        size = len(data['payload']['RETURNS_CALCULATIONS']['COVARIANCE']["index"])
        cov_matrix = np.zeros((size, size))
        for i in range(size):
            for j in range(i + 1):
                cov_matrix[i, j] = data['payload']['RETURNS_CALCULATIONS']['COVARIANCE']["covariance"][i][j]
                cov_matrix[j, i] = data['payload']['RETURNS_CALCULATIONS']['COVARIANCE']["covariance"][i][j]

        # Step 2: Define portfolio weights
        asset_weight_dict = {asset.symbol:asset.weight for asset in asset_details}
        asset_order = data['payload']['RETURNS_CALCULATIONS']['COVARIANCE']["index"]
        sorted_weights = [asset_weight_dict[asset] for asset in asset_order if asset in asset_weight_dict]
        weights = np.array(sorted_weights)

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
    print(portfolioAssets.items())
    for asset_ticker, quantity in portfolioAssets.items():
        # Here, you need to fetch or calculate the asset's price, std_dev, expected_return, and beta
        # For example, using a function get_asset_data(symbol) that returns these values
        quan = quantity

        price = get_asset_price(asset_ticker)
        std_dev = get_stock_stddev(asset_ticker)
        beta = get_asset_beta(asset_ticker)
        expected_return = calculate_expected_stock_return(beta, risk_free_rate, expected_market_return)
        
        print(f"Details of {asset_ticker}:")
        print(f"STDDEV: {std_dev}")
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

def sharpe_ratio(weights, expected_returns, cov_matrix, risk_free_rate):
    portfolio_return = np.dot(weights, expected_returns)
    portfolio_standard_deviation = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
    return (portfolio_return - risk_free_rate) / portfolio_standard_deviation

def maximize_sharpe_ratio(expected_returns, cov_matrix, risk_free_rate):
    num_assets = len(expected_returns)
    args = (expected_returns, cov_matrix, risk_free_rate)
    
    constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})  # The sum of weights is 1
    bound = (0, 1)
    bounds = tuple(bound for asset in range(num_assets))
    
    result = minimize(lambda weights: -sharpe_ratio(weights, *args), 
                      np.array(num_assets * [1. / num_assets]), 
                      method='SLSQP', bounds=bounds, constraints=constraints)

    print(result)
    return result.x

def get_covariance_matrix(symbols):
    url = settings.ALPHA_VANTAGE_ANALYTICS_URL
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
                value = data['payload']['RETURNS_CALCULATIONS']['COVARIANCE']["covariance"][i][j]
                cov_matrix[i, j] = value
                cov_matrix[j, i] = value

        return cov_matrix
    else:
        return None

def calculate_optimal_weights_portfolio(portfolio_assets):
    risk_free_rate = get_risk_free_rate()
    expected_market_return = get_expected_market_return('SPY')
    expected_returns = []
    asset_symbols = []
    for asset_ticker in portfolio_assets:
        expected_return = get_expected_stock_return(asset_ticker, risk_free_rate, expected_market_return)
        expected_returns.append(expected_return)
        asset_symbols.append(asset_ticker)
        
    expected_returns = np.array(expected_returns)

    symbols = ','.join(asset_symbols)
    cov_matrix = get_covariance_matrix(symbols)

    weights = maximize_sharpe_ratio(expected_returns, cov_matrix, risk_free_rate)

    return weights