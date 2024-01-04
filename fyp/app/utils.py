from decimal import Decimal
import numpy as np
import pandas as pd
from scipy.optimize import minimize
import requests
from django.conf import settings
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from datetime import datetime, timedelta

def calculate_expected_asset_return(beta, risk_free_rate, expected_market_return):
    if beta is None or risk_free_rate is None or expected_market_return is None:
        return None
    risk_premium = expected_market_return - risk_free_rate
    asset_risk_premium = beta * risk_premium
    expected_return = risk_free_rate + asset_risk_premium
    
    return expected_return

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
        return Decimal(latest_rate) / 100  # Convert percentage to decimal
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
            adjusted_closing_prices = [Decimal(day_data['5. adjusted close']) for date, day_data in data[data_feature].items()]
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
            return Decimal(data["Beta"])
    else:
        return None
    return None

def get_asset_name(symbol):
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
        if data and "Name" in data:
            return data["Name"]
    else:
        return None
    return None

def get_asset_price(symbol):
    url = settings.ALPHA_VANTAGE_QUERY_URL
    params = {
        "function": "GLOBAL_QUOTE",
        "symbol": symbol,
        "apikey": settings.ALPHA_VANTAGE_API_KEY
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data and "Global Quote" in data:
            return Decimal(data["Global Quote"]['05. price'])
    else:
        return None
    return None
    
def get_asset_stddev(symbol):
    url = settings.ALPHA_VANTAGE_ANALYTICS_URL
    params = {
        "SYMBOLS": symbol,
        "RANGE": "full",
        "INTERVAL": "DAILY", # TODO: DAILY data can be noisy, decide later based on investor's goals
        "CALCULATIONS": "STDDEV",
        "apikey": settings.ALPHA_VANTAGE_API_KEY,
        "entitlement": "delayed"
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        std_dev = data["payload"]["RETURNS_CALCULATIONS"]["STDDEV"][symbol]
        return Decimal(std_dev)
    else:
        return None

def get_asset_details(symbol, profile):
    risk_free_rate = get_risk_free_rate(profile.investment_time_period)
    expected_market_return = get_expected_market_return(profile.market_index, profile.investment_time_period)
    data = {}
    data['Price'] = get_asset_price(symbol)
    data['Beta'] = get_asset_beta(symbol)
    data['Stddev'] = get_asset_stddev(symbol)
    data['Name'] = get_asset_name(symbol)
    data['Expected_return'] = calculate_expected_asset_return(data["Beta"], risk_free_rate, expected_market_return)
    data['Sharpe_ratio'] = (data['Expected_return'] - risk_free_rate) / data['Stddev']

    return data
    
# Adjust function to use get_covariance_matrix to avoid repetition
def get_portfolio_stddev(asset_details):
    asset_symbols = [asset for asset in asset_details]
    symbols = ','.join(asset_symbols)
    url = settings.ALPHA_VANTAGE_ANALYTICS_URL
    params = {
        "SYMBOLS": symbols,
        "RANGE": "full",
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
        asset_weight_dict = {asset:dict["Weight"] for asset,dict in asset_details.items()}
        asset_order = data['payload']['RETURNS_CALCULATIONS']['COVARIANCE']["index"]
        sorted_weights = [asset_weight_dict[asset] for asset in asset_order if asset in asset_weight_dict]
        weights = np.array(sorted_weights)

        decimal_cov_matrix = [[Decimal(value) for value in row] for row in cov_matrix]

        # Step 3: Calculate portfolio variance
        portfolio_variance = np.dot(weights, np.dot(decimal_cov_matrix, weights.T))
        portfolio_stddev = portfolio_variance ** Decimal(0.5)

        return portfolio_stddev
    else:
        return None
    
def calculate_portfolio_details(portfolioAssets, profile):
    risk_free_rate = get_risk_free_rate(profile.investment_time_period)
    portfolio_details = {}
    portfolio_details["Portfolio"] = {}
    portfolio_details["Portfolio"]["Asset_value"] = 0
    portfolio_details["Portfolio"]["Expected_return"] = 0
    for asset, quantity in portfolioAssets.items():
        portfolio_details[asset] = get_asset_details(asset, profile)
        portfolio_details[asset]["Quantity"] = quantity
        # Calculate the total value of the asset in the portfolio
        portfolio_details[asset]["Asset_value"] = portfolio_details[asset]["Price"] * quantity
        portfolio_details["Portfolio"]["Asset_value"] += portfolio_details[asset]["Asset_value"]

    # Calculate weight, expected portfolio return, and standard deviation
    for asset in portfolio_details:
        if asset != "Portfolio":
            # Calculate weight of each asset
            portfolio_details[asset]["Weight"] = portfolio_details[asset]["Price"] * portfolio_details[asset]["Quantity"] / portfolio_details["Portfolio"]["Asset_value"]

            # Add to expected portfolio return
            portfolio_details["Portfolio"]["Expected_return"] += portfolio_details[asset]["Expected_return"] * portfolio_details[asset]["Weight"]
        else:
            portfolio_details[asset]["Weight"] = 1
    
    portfolio_assets = {k : v for k, v in portfolio_details.items() if k != "Portfolio"}
    portfolio_details["Portfolio"]["Stddev"] = get_portfolio_stddev(portfolio_assets)

    if portfolio_details["Portfolio"]["Stddev"] is not None:
        portfolio_details["Portfolio"]["Sharpe_ratio"] = (portfolio_details["Portfolio"]["Expected_return"] - risk_free_rate) / portfolio_details["Portfolio"]["Stddev"]
        # portfolio_details.standard_deviation = f"{float(portfolio_details.standard_deviation):.3%}"
        # portfolio_details.sharpe_ratio = f"{float(portfolio_details.sharpe_ratio):.5f}"
    else:
        portfolio_details.sharpe_ratio = "NA"
    # portfolio_details.total_value = f"USD ${portfolio_details.total_value:.2f}"
    # portfolio_details.expected_return = f"{portfolio_details.expected_return:.3%}"

    return portfolio_details

def sharpe_ratio(weights, expected_returns, cov_matrix, risk_free_rate):
    portfolio_return = np.dot(weights, expected_returns)
    portfolio_standard_deviation = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
    return (portfolio_return - risk_free_rate) / portfolio_standard_deviation

def maximize_sharpe_ratio(expected_returns, cov_matrix, risk_free_rate):
    num_assets = len(expected_returns)
    args = (expected_returns, cov_matrix, risk_free_rate)
    
    constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})  # The sum of weights is 1
    # bound = (0, 1)
    # bounds = tuple(bound for asset in range(num_assets)) # No short shelling
    initial_weights = [1.0 / num_assets] * num_assets
    
    result = minimize(lambda weights: -sharpe_ratio(weights, *args), 
                      initial_weights, 
                      method='SLSQP', constraints=constraints)

    return result.x

def get_covariance_matrix(symbols):
    url = settings.ALPHA_VANTAGE_ANALYTICS_URL
    params = {
        "SYMBOLS": symbols,
        "RANGE": "full",
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
                value = data['payload']['RETURNS_CALCULATIONS']['COVARIANCE']["covariance"][i][j]
                cov_matrix[i, j] = value
                cov_matrix[j, i] = value
        
        asset_order = data['payload']['RETURNS_CALCULATIONS']['COVARIANCE']["index"]

        return cov_matrix, asset_order
    else:
        return None

def calculate_optimal_weights_portfolio(profile, portfolio_assets):
    risk_free_rate = get_risk_free_rate(profile.investment_time_period)
    expected_market_return = get_expected_market_return(profile.market_index, profile.investment_time_period)
    expected_returns = []
    asset_symbols = []
    for asset_ticker in portfolio_assets:
        beta = get_asset_beta(asset_ticker)
        expected_return = calculate_expected_asset_return(beta, risk_free_rate, expected_market_return)
        expected_returns.append(expected_return)
        asset_symbols.append(asset_ticker)
    
    symbols = ','.join(asset_symbols)
    cov_matrix, asset_order = get_covariance_matrix(symbols)

    # Sorting logic
    sorted_indices = [asset_symbols.index(asset) for asset in asset_order]
    sorted_expected_returns = [float(expected_returns[i]) for i in sorted_indices]
    risk_free_rate = float(risk_free_rate)
    sorted_asset_symbols = [asset_symbols[i] for i in sorted_indices]   
    sorted_expected_returns = np.array(sorted_expected_returns)
    cov_matrix = np.array(cov_matrix)
    
    weights = maximize_sharpe_ratio(sorted_expected_returns, cov_matrix, risk_free_rate)

    return zip(sorted_asset_symbols, weights)

def get_simple_moving_average(symbol):
    url = settings.ALPHA_VANTAGE_QUERY_URL
    params = {
        "function": "SMA",
        "symbol": symbol,
        "interval": "daily",
        "time_period": 10,
        "series_type": "close",
        "apikey": settings.ALPHA_VANTAGE_API_KEY,
        "entitlement": "delayed"
    }
    response = requests.get(url, params)
    if response.status_code == 200:
        data = response.json()
        # Convert the SMA data to a DataFrame
        df = pd.DataFrame([(date, values['SMA']) for date, values in data['Technical Analysis: SMA'].items()], columns=['Date', 'SMA'])
        df['Date'] = pd.to_datetime(df['Date'])
        
        # Plotting
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df['Date'], y=df['SMA'], mode='lines', name='SMA'))
        fig.update_layout(title='Simple Moving Average (SMA)',
                        xaxis_title='Date',
                        yaxis_title='SMA Value',
                        template='plotly_dark')  # Choose a template that suits your style
        chart = fig.to_html()
        return chart
    else:
        return None
    
def get_linear_regression(symbol):
    url = settings.ALPHA_VANTAGE_QUERY_URL
    params = {
        "function": "TIME_SERIES_DAILY_ADJUSTED",
        "symbol": symbol,
        "outputsize": "full",
        "apikey": settings.ALPHA_VANTAGE_API_KEY,
        "entitlement": "delayed"
    }
    response = requests.get(url, params)
    if response.status_code == 200:
        data = response.json()
        # Convert data to DataFrame
        df = pd.DataFrame(data["Time Series (Daily)"]).T
        df['date'] = pd.to_datetime(df.index)
        df['adj_close'] = df['5. adjusted close'].astype(float)

        # Convert date to ordinal
        df['date_ordinal'] = pd.to_datetime(df['date']).map(datetime.toordinal)

        # Prepare the features (X) and target (y)
        X = df[['date_ordinal']]
        y = df['adj_close']
        print(X.head())
        print(y.head())

        # Create and train the model
        model = LinearRegression()
        model.fit(X, y)

        # Predict for the Next Three Months
        last_date = df['date'].max()
        future_dates = [last_date + timedelta(days=i) for i in range(1, 91)]  # 90 days ~ roughly 3 months
        future_dates_ordinal = [date.toordinal() for date in future_dates]
        future_dates_df = pd.DataFrame(future_dates_ordinal, columns=['date_ordinal'])
        print(future_dates_df.head())

        # Predict future prices
        predicted_prices = model.predict(future_dates_df)

        predictions = pd.DataFrame({'Date': future_dates, 'Predicted Price': predicted_prices})
        print(predictions.head())
        
        return predictions
    else:
        return None
