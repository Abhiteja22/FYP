import numpy as np
import yfinance as yf
from .models import *
import pyfredapi as pf

def get_series_fred_api(series_id):
    data = pf.get_series(series_id=series_id, api_key='86163e766108151080f7c69c5a76b5f1')
    latest_data = data.iloc[-1]
    
    return latest_data['value']

def get_risk_free_rate(time_period):
    risk_free_rate = 2 # Default value

    if time_period == '1month':
        series_id = 'DGS1MO'
        risk_free_rate = get_series_fred_api(series_id)
    elif time_period == '3month':
        series_id = 'DGS3MO'
        risk_free_rate = get_series_fred_api(series_id)
    elif time_period == '6month':
        series_id = 'DGS6MO'
        risk_free_rate = get_series_fred_api(series_id)
    elif time_period == '1year':
        series_id = 'DGS1'
        risk_free_rate = get_series_fred_api(series_id)
    elif time_period == '3year':
        series_id = 'DGS3'
        risk_free_rate = get_series_fred_api(series_id)
    elif time_period == '5year':
        series_id = 'DGS5'
        risk_free_rate = get_series_fred_api(series_id)
    elif time_period == '10year':
        series_id = 'DGS10'
        risk_free_rate = get_series_fred_api(series_id)
    elif time_period == '30year':
        series_id = 'DGS30'
        risk_free_rate = get_series_fred_api(series_id)
    else:
        series_id = 'DGS1'
        risk_free_rate = get_series_fred_api(series_id)
    
    return risk_free_rate/100

def get_period_and_interval(time_period):
    period_to_yf = {
        '1month': ('1mo', '1d'),
        '3month': ('3mo', '1d'),
        '6month': ('6mo', '1d'),
        '1year': ('1y', '1d'),
        '3year': ('3y', '1wk'),
        '5year': ('5y', '1wk'),
        '10year': ('10y', '1mo'),
        '30year': ('max', '1mo'),
    }

    yf_period, yf_interval = period_to_yf[time_period]
    return yf_period, yf_interval

def get_expected_market_return(market_index, time_period):
    yf_period, yf_interval = get_period_and_interval(time_period)
    market_data = yf.download(market_index, period=yf_period, interval=yf_interval)

    returns = market_data['Adj Close'].pct_change().dropna()
    
    if time_period in ['1month', '3month', '6month']:
        expected_return = returns.mean() * returns.shape[0]
    else:
        if yf_interval == '1d':
            annualized_return = (1 + returns.mean()) ** 252 - 1  # 252 trading days in a year
        elif yf_interval == '1wk':
            annualized_return = (1 + returns.mean()) ** 52 - 1   # 52 weeks in a year
        elif yf_interval == '1mo':
            annualized_return = (1 + returns.mean()) ** 12 - 1   # 12 months in a year
        expected_return = annualized_return
    
    return expected_return

def get_historical_prices(ticker, period, interval):
    asset = yf.Ticker(ticker)
    hist_asset = asset.history(period=period,interval=interval)

    return hist_asset

def get_daily_returns(ticker, period, interval):
    asset = yf.Ticker(ticker)
    hist_asset = asset.history(period=period,interval=interval)
    daily_returns_asset = hist_asset['Close'].pct_change().dropna()

    daily_returns_asset

def get_asset_beta(asset, time_period, market_index):
    yf_period, yf_interval = get_period_and_interval(time_period)

    returns_market_index = get_daily_returns(market_index, yf_period, yf_interval)
    returns_asset = get_daily_returns(asset, yf_period, yf_interval)

    covariance = np.cov(returns_asset, returns_market_index)[0][1]
    variance_market_index = np.var(returns_market_index)

    beta_asset = covariance / variance_market_index

    return beta_asset

def get_asset_price(ticker):
    asset = yf.Ticker(ticker)
    hist = asset.history(period="1d")
    latest_price = hist['Close'].iloc[-1]
    
    return latest_price

def get_asset_stddev(ticker):
    daily_returns = get_daily_returns(ticker)
    stddev = daily_returns.std()
    
    return stddev

def get_asset_expected_return(beta, market_return, risk_free_rate):
    risk_premium = market_return - risk_free_rate
    asset_risk_premium = beta * risk_premium
    expected_return = risk_free_rate + asset_risk_premium
    
    return expected_return

def get_sharpe_ratio(expected_return, std_dev, risk_free_rate):
    sharpe_ratio = (expected_return - risk_free_rate) / std_dev
    return sharpe_ratio

def get_asset_details_general(ticker):
    time_period = '1year'
    interval = '1d'
    market_index = '^GSPC'
    risk_free_rate = get_risk_free_rate(time_period)
    market_return = get_expected_market_return(market_index, time_period)
    price = get_asset_price(ticker)
    beta = get_asset_beta(ticker, time_period, market_index)
    historical_prices = get_historical_prices(ticker, time_period, interval)
    standard_deviation = get_asset_stddev(ticker)
    expected_return = get_asset_expected_return(ticker, market_return, risk_free_rate)
    sharpe_ratio = get_sharpe_ratio(expected_return, standard_deviation, risk_free_rate)
    return_dict = {
        'current_price': price,
        'beta': beta,
        'price_history': historical_prices,
        'sharpe_ratio': sharpe_ratio,
        'standard_deviation': standard_deviation,
        'expected_return': expected_return
    }
    return return_dict

def get_portfolio_value(assets):
    values = {}
    total_value = 0

    for asset, quantity in assets.items():
        price = get_asset_price(asset)
        value = price * quantity
        values[asset] = value
        total_value += value

    return values, total_value

def get_portfolio_beta(asset_tickers, time_period, market_index, weights):
    # Fetch historical data for the assets and the benchmark
    data = yf.download(asset_tickers + [market_index], period=time_period)['Adj Close']
    
    # Calculate daily returns
    daily_returns = data.pct_change().dropna()
    
    # Calculate portfolio returns as weighted average of asset returns
    portfolio_returns = (daily_returns[asset_tickers] * weights).sum(axis=1)
    
    # Calculate covariance between portfolio returns and benchmark returns
    covariance_matrix = np.cov(portfolio_returns, daily_returns[market_index])
    portfolio_benchmark_covariance = covariance_matrix[0][1]
    
    # Calculate variance of benchmark returns
    benchmark_variance = daily_returns[market_index].var()
    
    # Calculate beta of the portfolio
    portfolio_beta = portfolio_benchmark_covariance / benchmark_variance
    
    return portfolio_beta

def get_portfolio_stddev(tickers, time_period):
    # Download historical data
    data = yf.download(tickers, period=time_period)['Adj Close']
    
    # Calculate daily returns
    daily_returns = data.pct_change().dropna()
    
    # Calculate covariance matrix of daily returns
    cov_matrix = daily_returns.cov()
    
    # Convert weights to a numpy array
    weights = np.array(weights)
    
    # Portfolio variance
    portfolio_variance = np.dot(weights.T, np.dot(cov_matrix, weights))
    
    # Portfolio standard deviation
    portfolio_stddev = np.sqrt(portfolio_variance)
    
    return portfolio_stddev

def get_portfolio_expected_return(tickers, time_period, weights):
    # Fetch historical data for each ticker
    data = yf.download(tickers, period=time_period)['Adj Close']
    
    # Calculate daily returns
    daily_returns = data.pct_change()
    
    # Calculate annualized average return for each asset
    annual_returns = daily_returns.mean() * 252
    
    # Calculate the portfolio's expected return as the weighted sum of the individual expected returns
    portfolio_return = np.dot(annual_returns, weights)
    
    return portfolio_return
