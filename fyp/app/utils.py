import numpy as np
import yfinance as yf
from .models import *
import pyfredapi as pf
from datetime import datetime

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

def get_long_name(market_index):
    index = yf.Ticker(market_index)
    return index.info.get('longName')

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
    hist_asset = get_historical_prices(ticker, period, interval)
    daily_returns_asset = hist_asset['Close'].pct_change().dropna()
    return daily_returns_asset

def get_asset_beta(asset, time_period, market_index):
    yf_period, yf_interval = get_period_and_interval(time_period)
    returns_market_index = get_daily_returns(market_index, yf_period, yf_interval)
    returns_asset = get_daily_returns(asset, yf_period, yf_interval)
    start_date = max(returns_asset.index.min(), returns_market_index.index.min())
    aligned_returns_asset = returns_asset[returns_asset.index >= start_date]
    aligned_returns_market_index = returns_market_index[returns_market_index.index >= start_date]
    print(aligned_returns_asset)
    print(aligned_returns_market_index)
    covariance = np.cov(aligned_returns_asset, aligned_returns_market_index)[0][1]
    variance_market_index = np.var(aligned_returns_market_index)

    beta_asset = covariance / variance_market_index

    return beta_asset

def get_asset_price(ticker):
    asset = yf.Ticker(ticker)
    hist = asset.history(period="1d")
    latest_price = hist['Close'].iloc[-1]
    
    return latest_price

def get_asset_stddev(ticker, period):
    yf_period, yf_interval = get_period_and_interval(period)
    daily_returns = get_daily_returns(ticker, yf_period, yf_interval)
    stddev = daily_returns.std()
    
    return stddev

def get_asset_expected_return(beta, market_return, risk_free_rate):
    risk_premium = market_return - risk_free_rate
    asset_risk_premium = beta * risk_premium
    expected_return = risk_free_rate + asset_risk_premium
    
    return expected_return

def get_sharpe_ratio(expected_return, std_dev, risk_free_rate):
    if std_dev == 0:
        return 0
    sharpe_ratio = (expected_return - risk_free_rate) / std_dev
    return sharpe_ratio

def get_asset_details_general(ticker):
    time_period = '1year'
    market_index = '^GSPC'
    risk_free_rate = get_risk_free_rate(time_period)
    market_return = get_expected_market_return(market_index, time_period)
    price = get_asset_price(ticker)
    beta = get_asset_beta(ticker, time_period, market_index)
    # historical_prices = get_historical_prices(ticker, time_period, interval)
    standard_deviation = get_asset_stddev(ticker, time_period)
    expected_return = get_asset_expected_return(beta, market_return, risk_free_rate)
    sharpe_ratio = get_sharpe_ratio(expected_return, standard_deviation, risk_free_rate)
    return_dict = {
        'current_price': price,
        'beta': beta,
        # 'price_history': historical_prices,
        'sharpe_ratio': sharpe_ratio,
        'standard_deviation': standard_deviation,
        'expected_return': expected_return
    }
    return return_dict

def get_portfolio_value(assets):
    values = {}
    total_value = 0

    for asset, quantity in assets.items():
        current_price = get_asset_price(asset)
        asset_total_value = current_price * float(quantity)
        if asset in values:
            values[asset] += asset_total_value
        else:
            values[asset] = asset_total_value
        total_value += asset_total_value
    
    return values, total_value

def get_portfolio_beta(asset_tickers, time_period, market_index, weights):
    # Fetch historical data for the assets and the benchmark
    if not asset_tickers:
        return 0
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

def get_portfolio_stddev(tickers, time_period, weights, initial_period):
    if not tickers:
        return 0
    if len(tickers) == 1:
        return get_asset_stddev(tickers[0], initial_period)
    data = yf.download(tickers, period=time_period)['Adj Close']
    
    daily_returns = data.pct_change().dropna()
    cov_matrix = daily_returns.cov()
    weights = np.array(weights)
    portfolio_variance = np.dot(weights.T, np.dot(cov_matrix, weights))
    portfolio_stddev = np.sqrt(portfolio_variance)
    
    return portfolio_stddev

def get_portfolio_expected_return(tickers, time_period, weights, beta, market_return, risk_free_rate):
    if not tickers:
        return 0
    if len(tickers) == 1:
        return get_asset_expected_return(beta, market_return, risk_free_rate)
    data = yf.download(tickers, period=time_period)['Adj Close']
    daily_returns = data.pct_change()
    annual_returns = daily_returns.mean() * 252
    portfolio_return = np.dot(annual_returns, weights)

    return portfolio_return

def get_asset_price_by_date(ticker, date):
    stock = yf.Ticker(ticker)
    start_date = date
    end_date = datetime.today()
    data = stock.history(start=start_date, end=end_date)
    if not data.empty:
        return data['Close'].iloc[0]
    else:
        return None

def get_portfolio_details_general(transactions, time_period, market_index):
    yf_period, yf_interval = get_period_and_interval(time_period)
    risk_free_rate = get_risk_free_rate(time_period)
    market_return = get_expected_market_return(market_index, time_period)
    money_invested = 0
    money_withdrawn = 0
    oldest_date_asset_bought = {}
    assets_held = {}
    trans_dict = []
    for transaction in transactions:
        trans_dict.append({
            "id": transaction.id,
            "asset_name": transaction.asset.name,
            "asset_ticker": transaction.asset.ticker,
            "transaction_type": transaction.transaction_type,
            "quantity": transaction.quantity,
            "transaction_date": transaction.transaction_date,
            "value": "${:,.2f}".format(transaction.value)
        })
        asset = transaction.asset.ticker
        price = get_asset_price_by_date(asset, transaction.transaction_date)
        value = price * float(transaction.quantity)
        transaction_date = transaction.transaction_date
        if transaction.transaction_type == 'BUY':
            money_invested += value
            if asset in assets_held:
                assets_held[asset] += transaction.quantity
                if transaction_date < oldest_date_asset_bought[asset]:
                    oldest_date_asset_bought[asset] = transaction_date
            else:
                assets_held[asset] = transaction.quantity
                oldest_date_asset_bought[asset] = transaction_date
        elif transaction.transaction_type == 'SELL':
            money_withdrawn += value
            assets_held[asset] -= transaction.quantity
            if assets_held[asset] == 0:
                del assets_held[asset]
                del oldest_date_asset_bought[asset]

    values, total_value = get_portfolio_value(assets_held)
    asset_tickers = []
    weights = []
    current_assets_held = []
    for asset_ticker, value in values.items():
        asset_tickers.append(asset_ticker)
        weight = value / total_value
        weights.append(weight)
        current_assets_held.append({
            "ticker": asset_ticker,
            "name": get_long_name(asset_ticker),
            "quantity": assets_held[asset_ticker],
            "weight": weight,
            "purchase_price": "${:,.2f}".format(get_asset_price_by_date(asset_ticker, oldest_date_asset_bought[asset_ticker])),
            "current_price": "${:,.2f}".format(get_asset_price(asset_ticker))
        })

    beta = get_portfolio_beta(asset_tickers, yf_period, market_index, weights)
    standard_deviation = get_portfolio_stddev(asset_tickers, yf_period, weights, time_period)
    expected_return = get_portfolio_expected_return(asset_tickers, yf_period, weights, beta, market_return, risk_free_rate)
    sharpe_ratio = get_sharpe_ratio(expected_return, standard_deviation, risk_free_rate)
    
    return_dict = {
        'transactions': trans_dict,
        'current_assets_held': current_assets_held,
        'money_invested': money_invested,
        'oldest_date_asset_bought': oldest_date_asset_bought,
        'money_withdrawn': money_withdrawn,
        'total_value': total_value,
        'beta': beta,
        'sharpe_ratio': sharpe_ratio,
        'standard_deviation': standard_deviation,
        'expected_return': expected_return
    }
    return return_dict
