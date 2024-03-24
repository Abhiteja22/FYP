from decimal import Decimal
import numpy as np
import pandas as pd
from scipy.optimize import minimize
import requests
from django.conf import settings
import plotly.graph_objects as go
from statsmodels.tsa.arima.model import ARIMA
from datetime import timedelta
import plotly
import plotly.express as px
import json
from pmdarima import auto_arima


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
    
# TODO: ARIMA
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

        df.sort_index(inplace=True)
        df = df[~df.index.duplicated()]
        df.index = pd.DatetimeIndex(df.index).to_period('D')

        # ARIMA Model
        # Note: You might need to adjust the order (p, d, q) based on your data's characteristics
        model = ARIMA(df['adj_close'], order=(5, 2, 0)) 
        fitted_model = model.fit()

        # Forecast for the Next Three Months
        # ARIMA's 'forecast' function automatically handles the date index
        predicted_prices = fitted_model.forecast(steps=90)  # 90 days ~ roughly 3 months

        # Creating a DataFrame for the predictions
        last_date = df.index[-1].to_timestamp()
        future_dates = [last_date + timedelta(days=i) for i in range(1, 91)]
        predictions = pd.DataFrame({'Date': future_dates, 'Predicted Price': predicted_prices.values})
        print(predictions)

        # Plotting using plotly express
        fig = px.line(predictions, x='Date', y='Predicted Price', title='Price Predictions')
        graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

        # time_series_data = df['adj_close']
        # # Assuming 'time_series_data' is your time series data
        # model = auto_arima(time_series_data, start_p=1, start_q=1,
        #                 max_p=5, max_q=5, m=12,
        #                 seasonal=True, d=None, D=None, trace=True,
        #                 error_action='ignore', suppress_warnings=True,
        #                 stepwise=True)

        # print(model.summary())
        
        return graphJSON
    else:
        return None

def get_historical_returns(symbol):
    url = settings.ALPHA_VANTAGE_QUERY_URL
    params = {
        "function": "TIME_SERIES_DAILY_ADJUSTED",
        "symbol": symbol,
        "outputsize": "full",
        "apikey": settings.ALPHA_VANTAGE_API_KEY,
        "entitlement": "delayed"
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        historical_data = pd.DataFrame.from_dict(data['Time Series (Daily)'], orient='index')
        historical_data.index = pd.to_datetime(historical_data.index)
        historical_data.sort_index(inplace=True)
        historical_data['5. adjusted close'] = historical_data['5. adjusted close'].apply(Decimal)
        historical_prices = historical_data['2015-01-02':]['5. adjusted close']
        historical_returns = historical_prices.pct_change().dropna()
        return historical_returns
    else:
        return None
    
def get_historical_values(symbol):
    url = settings.ALPHA_VANTAGE_QUERY_URL
    params = {
        "function": "TIME_SERIES_DAILY_ADJUSTED",
        "symbol": symbol,
        "outputsize": "full",
        "apikey": settings.ALPHA_VANTAGE_API_KEY,
        "entitlement": "delayed"
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        historical_data = pd.DataFrame.from_dict(data['Time Series (Daily)'], orient='index')
        historical_data.index = pd.to_datetime(historical_data.index)
        historical_data.sort_index(inplace=True)
        historical_data['5. adjusted close'] = historical_data['5. adjusted close'].apply(Decimal)
        historical_prices = historical_data['2015-01-02':]['5. adjusted close']
        return historical_prices
    else:
        return None

def get_VaR(portfolioAssets):
    portfolio_returns = None
    total_portfolio_value = sum([get_asset_price(asset.asset_ticker) * asset.quantity for asset in portfolioAssets])
    for asset in portfolioAssets:
        historical_asset_returns = get_historical_returns(asset.asset_ticker)
        # Calculate weight of each asset in the portfolio
        asset_value = get_asset_price(asset.asset_ticker) * asset.quantity
        weight = asset_value / total_portfolio_value
        weighted_returns = historical_asset_returns * weight

        # Aggregate portfolio returns
        if portfolio_returns is None:
            portfolio_returns = weighted_returns
        else:
            portfolio_returns = portfolio_returns.add(weighted_returns, fill_value=0)
    portfolio_returns = portfolio_returns.astype(float)
    var_95 = np.percentile(portfolio_returns, 5)
    cvar_95 = portfolio_returns[portfolio_returns <= var_95].mean()
    return var_95, cvar_95

def get_sortino_ratio(portfolioAssets):
    portfolio_returns = None
    total_portfolio_value = sum([get_asset_price(asset.asset_ticker) * asset.quantity for asset in portfolioAssets])
    for asset in portfolioAssets:
        historical_asset_returns = get_historical_returns(asset.asset_ticker)
        # Calculate weight of each asset in the portfolio
        asset_value = get_asset_price(asset.asset_ticker) * asset.quantity
        weight = asset_value / total_portfolio_value
        weighted_returns = historical_asset_returns * weight

        # Aggregate portfolio returns
        if portfolio_returns is None:
            portfolio_returns = weighted_returns
        else:
            portfolio_returns = portfolio_returns.add(weighted_returns, fill_value=0)
    portfolio_returns = portfolio_returns.astype(float)
    risk_free_rate = get_risk_free_rate('3month')
    # Calculate downside deviation (only considering negative returns)
    negative_returns = portfolio_returns[portfolio_returns < 0]
    downside_deviation = Decimal(np.sqrt(np.mean(negative_returns**2)))
    annualized_portfolio_return = np.mean(portfolio_returns) * 252
    annualized_portfolio_return = Decimal(annualized_portfolio_return)
    sortino_ratio = (annualized_portfolio_return - risk_free_rate) / downside_deviation

    return sortino_ratio

def get_maximum_drawdown(portfolioAssets):
    # Initialize an empty DataFrame for the portfolio values
    historical_portfolio_values = pd.DataFrame()
    for asset in portfolioAssets:
        historical_asset_values = get_historical_values(asset.asset_ticker)
        asset_value_over_time = historical_asset_values * asset.quantity
        if historical_portfolio_values.empty:
            historical_portfolio_values = asset_value_over_time.to_frame(name=asset.asset_ticker)
        else:
            historical_portfolio_values = historical_portfolio_values.join(asset_value_over_time.to_frame(name=asset.asset_ticker), how='outer')

    # Sum the values across columns (assets) to get the total portfolio value at each time point
    historical_portfolio_values['Total Portfolio Value'] = historical_portfolio_values.sum(axis=1)
    historical_portfolio_values = historical_portfolio_values[['Total Portfolio Value']]
    rolling_max = historical_portfolio_values.cummax()
    
    # Calculate drawdown as the percentage drop from the peak
    drawdown = (historical_portfolio_values - rolling_max) / rolling_max
    # Maximum drawdown
    max_drawdown = drawdown.min()['Total Portfolio Value']
    
    return max_drawdown

# TODO: Do after implementing get_portfolio_beta() function
def get_portfolio_alpha():
    return None
