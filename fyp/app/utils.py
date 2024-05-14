import random
from typing import List
import numpy as np
import yfinance as yf
from .models import *
import pyfredapi as pf
from datetime import datetime, timedelta
from scipy.optimize import minimize
from langchain.tools import StructuredTool
from langchain_openai import ChatOpenAI
from langchain_community.utilities import SerpAPIWrapper
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, HumanMessagePromptTemplate
from langchain_community.tools.convert_to_openai import format_tool_to_openai_function
from langchain.agents.format_scratchpad import format_to_openai_function_messages
from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser
from langchain.output_parsers import PydanticOutputParser
from langchain.agents import AgentExecutor
from langchain_experimental.tools import PythonREPLTool
from langchain.pydantic_v1 import BaseModel, Field

def get_series_fred_api(series_id):
    data = pf.get_series(series_id=series_id, api_key='86163e766108151080f7c69c5a76b5f1')
    latest_data = data.iloc[-1]
    
    return latest_data['value']

def get_risk_free_rate(time_period):
    """
    Helps to calculate the risk free rate based on intended time period to invest.
    :param time_period: investment_time_period (one of these values: 1month, 3month, 6month, 1year, 3year, 5year, 10year, 30year)
    :return risk_free_rate: risk free rate for the given time period
    """
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

def get_long_name(ticker):
    """
    returns name of the asset by ticker
    :param ticker: Ticker symbol of asset
    :return Name of the corresponding asset
    """
    index = yf.Ticker(ticker)
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

def get_historical_prices(ticker, time_period):
    """
    Returns historical prices of an asset for a specific time period
    :param ticker: Ticker symbol of asset
    :param time_period: Time period of historical prices needed
    :return hist_asset: Pandas dataframe of asset's pricing history
    """
    yf_period, yf_interval = get_period_and_interval(time_period)
    asset = yf.Ticker(ticker)
    hist_asset = asset.history(period=yf_period,interval=yf_interval)

    return hist_asset

def get_daily_returns(ticker, time_period):
    """
    Returns historical returns of an asset for a specific time period
    :param ticker: Ticker symbol of asset
    :param time_period: Time period of historical prices needed
    :return hist_asset: Pandas dataframe of asset's daily returns history
    """
    hist_asset = get_historical_prices(ticker, time_period)
    daily_returns_asset = hist_asset['Close'].pct_change().dropna()
    return daily_returns_asset

def get_asset_beta(asset, time_period, market_index):
    returns_market_index = get_daily_returns(market_index, time_period)
    returns_asset = get_daily_returns(asset, time_period)
    start_date = max(returns_asset.index.min(), returns_market_index.index.min())
    aligned_returns_asset = returns_asset[returns_asset.index >= start_date]
    aligned_returns_market_index = returns_market_index[returns_market_index.index >= start_date]
    covariance = np.cov(aligned_returns_asset, aligned_returns_market_index)[0][1]
    variance_market_index = np.var(aligned_returns_market_index)

    beta_asset = covariance / variance_market_index

    return beta_asset

def get_asset_price(ticker):
    """
    Returns latest price of an asset
    :param ticker: ticker symbol of asset
    :return latest_price: latest trading price of the asset
    """
    asset = yf.Ticker(ticker)
    hist = asset.history(period="1d")
    latest_price = hist['Close'].iloc[-1]
    
    return latest_price

def get_asset_stddev(ticker, period):
    daily_returns = get_daily_returns(ticker, period)
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
    """
    Returns a dictionary of details of a particular asset such as current price, beta, standard deviation, expected asset return, sharpe ratio
    :param ticker: Ticker symbol of asset
    :return return_dict: Dictionary of asset details such as current price, beta, standard deviation, expected asset return, sharpe ratio
    """
    time_period = '1year'
    market_index = '^GSPC'
    risk_free_rate = get_risk_free_rate(time_period)
    market_return = get_expected_market_return(market_index, time_period)
    price = get_asset_price(ticker)
    beta = get_asset_beta(ticker, time_period, market_index)
    standard_deviation = get_asset_stddev(ticker, time_period)
    expected_return = get_asset_expected_return(beta, market_return, risk_free_rate)
    sharpe_ratio = get_sharpe_ratio(expected_return, standard_deviation, risk_free_rate)
    return_dict = {
        'current_price': price,
        'beta': beta,
        'standard_deviation': standard_deviation,
        'expected_return': expected_return,
        'sharpe_ratio': sharpe_ratio,
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
    yf_period, yf_interval = get_period_and_interval(time_period)
    if not asset_tickers:
        return 0
    data = yf.download(asset_tickers + [market_index], period=yf_period)['Adj Close']
    daily_returns = data.pct_change().dropna()
    portfolio_returns = (daily_returns[asset_tickers] * weights).sum(axis=1)
    covariance_matrix = np.cov(portfolio_returns, daily_returns[market_index])
    portfolio_benchmark_covariance = covariance_matrix[0][1]
    benchmark_variance = daily_returns[market_index].var()
    portfolio_beta = portfolio_benchmark_covariance / benchmark_variance
    
    return portfolio_beta

def get_portfolio_stddev(tickers, time_period, weights):
    yf_period, yf_interval = get_period_and_interval(time_period)
    if not tickers:
        return 0
    if len(tickers) == 1:
        return get_asset_stddev(tickers[0], time_period)
    data = yf.download(tickers, period=yf_period)['Adj Close']
    
    daily_returns = data.pct_change().dropna()
    cov_matrix = daily_returns.cov()
    weights = np.array(weights)
    portfolio_variance = np.dot(weights.T, np.dot(cov_matrix, weights))
    portfolio_stddev = np.sqrt(portfolio_variance)
    
    return portfolio_stddev

def get_portfolio_expected_return(tickers, time_period, weights, beta, market_return, risk_free_rate):
    yf_period, yf_interval = get_period_and_interval(time_period)
    if not tickers:
        return 0
    if len(tickers) == 1:
        return get_asset_expected_return(beta, market_return, risk_free_rate)
    data = yf.download(tickers, period=yf_period)['Adj Close']
    daily_returns = data.pct_change()
    annual_returns = daily_returns.mean() * 252
    portfolio_return = np.dot(annual_returns, weights)

    return portfolio_return

def get_expected_returns(tickers, time_period):
    yf_period, yf_interval = get_period_and_interval(time_period)
    data = yf.download(tickers, period=yf_period)['Adj Close']
    daily_returns = data.pct_change()
    expected_returns = daily_returns.mean()
    return expected_returns

def maximize_sharpe_ratio(tickers, time_period):
    """
    Returns a list of weights of assets (ordered by asset parameter passed) that maximises the sharpe ratio of a portfolio with the assets
    :param tickers: list of asset ticker symbols that consist the portfolio
    :param time_period: investment time period
    """
    risk_free_rate = get_risk_free_rate(time_period)
    expected_returns = get_expected_returns(tickers, time_period)

    def objective(weights):
        portfolio_return = np.dot(weights, expected_returns)
        portfolio_stddev = get_portfolio_stddev(tickers, time_period, weights)
        sharpe_ratio = (portfolio_return - risk_free_rate) / portfolio_stddev
        return -sharpe_ratio

    constraints = ({'type': 'eq', 'fun': lambda weights: np.sum(weights) - 1})
    bounds = tuple((0, 1) for _ in tickers)
    initial_guess = np.array(len(tickers) * [1. / len(tickers)])

    result = minimize(objective, initial_guess, method='SLSQP', bounds=bounds, constraints=constraints)
    
    return result.x

def get_asset_price_by_date(ticker, date):
    stock = yf.Ticker(ticker)
    end_date = date
    start_date = end_date - timedelta(days=7)
    data = stock.history(start=start_date, end=end_date)
    if not data.empty:
        return data['Close'].iloc[0]
    else:
        return None
    
def get_transaction_details(transactions):
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
        transaction_date = transaction.transaction_date
        if transaction.transaction_type == 'BUY':
            money_invested += transaction.value
            if asset in assets_held:
                assets_held[asset] += transaction.quantity
                if transaction_date < oldest_date_asset_bought[asset]:
                    oldest_date_asset_bought[asset] = transaction_date
            else:
                assets_held[asset] = transaction.quantity
                oldest_date_asset_bought[asset] = transaction_date
        elif transaction.transaction_type == 'SELL':
            money_withdrawn += transaction.value
            assets_held[asset] -= transaction.quantity
            if assets_held[asset] == 0:
                del assets_held[asset]
                del oldest_date_asset_bought[asset]
    return trans_dict, assets_held, oldest_date_asset_bought, money_invested, money_withdrawn

def optimize_portfolio(transactions, time_period):
    trans_dict, assets_held, oldest_date_asset_bought, money_invested, money_withdrawn = get_transaction_details(transactions)
    values, total_value = get_portfolio_value(assets_held)
    
    tickers = list(assets_held.keys())
    optimal_weights = maximize_sharpe_ratio(tickers, time_period)

    optimized_portfolio_details = []
    for ticker, optimal_weight in zip(tickers, optimal_weights):
        asset_name = Asset.objects.get(ticker=ticker).name
        id = Asset.objects.get(ticker=ticker).id
        current_asset_value = values[ticker]
        optimal_weight = round(optimal_weight)
        target_value = total_value * optimal_weight
        value_difference = target_value - current_asset_value
        quantity_to_adjust = value_difference / get_asset_price(ticker)
        quantity_to_adjust = round(quantity_to_adjust)
        quantity_to_adjust = random.randint(1,10)
        quantity = '-' + str(abs(quantity_to_adjust)) if quantity_to_adjust < 0 else '+' + str(abs(quantity_to_adjust))
        optimized_portfolio_details.append({
            'asset_ticker': ticker,
            'name': asset_name,
            'id': id,
            'weight': optimal_weight,
            'adjustment': 'SELL' if quantity_to_adjust < 0 else 'BUY',
            'positive': False if quantity_to_adjust < 0 else True,
            'quantity': quantity,
            'quantity_numerical': abs(quantity_to_adjust)
        })

    return optimized_portfolio_details

def get_portfolio_details_general(transactions, time_period, market_index):
    risk_free_rate = get_risk_free_rate(time_period)
    market_return = get_expected_market_return(market_index, time_period)
    trans_dict, assets_held, oldest_date_asset_bought, money_invested, money_withdrawn = get_transaction_details(transactions)
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
    
    beta = get_portfolio_beta(asset_tickers, time_period, market_index, weights)
    standard_deviation = get_portfolio_stddev(asset_tickers, time_period, weights)
    expected_return = get_portfolio_expected_return(asset_tickers, time_period, weights, beta, market_return, risk_free_rate)
    sharpe_ratio = get_sharpe_ratio(expected_return, standard_deviation, risk_free_rate)
    invested_currently = float(money_invested - money_withdrawn)
    profit_to_date = total_value - invested_currently
    if invested_currently > 0:
        percentage_profit = profit_to_date/invested_currently
    else:
        percentage_profit = 0
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
        'expected_return': expected_return,
        'invested_currently': invested_currently,
        'profit_to_date': profit_to_date,
        'percentage_profit': percentage_profit
    }
    return return_dict

def get_market_index_details(ticker, time_period):
    """
    Returns beta, sharpe_ratio, standard_deviation, expected_return of a market_index
    :param ticker: Ticker symbol of market index
    :param time_period: investment time period
    :return return_dict: returns a dictionary of beta, sharpe_ratio, standard_deviation, expected_return
    """
    risk_free_rate = get_risk_free_rate(time_period)
    market_return = get_expected_market_return(ticker, time_period)
    beta = get_asset_beta(ticker, time_period, ticker)
    standard_deviation = get_asset_stddev(ticker, time_period)
    expected_return = get_asset_expected_return(beta, market_return, risk_free_rate)
    sharpe_ratio = get_sharpe_ratio(expected_return, standard_deviation, risk_free_rate)
    return_dict = {
        'beta': beta,
        'sharpe_ratio': sharpe_ratio,
        'standard_deviation': standard_deviation,
        'expected_return': expected_return
    }
    return return_dict

def portfolio_details_AI(assets, value, beta, invested, standard_deviation, expected_return, sharpe_ratio, sector, investment_time_period, risk_aversion, market_index, market_index_long_name):
    SERPAPI_KEY = "f0627549432dff35aa32fa8aa1f1e606b22aa354d42b459ef7bf42ae4e3fa9e7"
    search = SerpAPIWrapper(serpapi_api_key=SERPAPI_KEY)
    serp_api_tool = StructuredTool.from_function(
        func=search.run,
        name="search",
        description="useful to descriptive information of an asset such as company description, company industry, company products"
    )
    get_market_index_details_tool = StructuredTool.from_function(
        func=get_market_index_details,
        name="get_market_index_details",
        description="useful for obtaining details about a market index"
    )
    get_risk_free_rate_tool = StructuredTool.from_function(
        func=get_risk_free_rate,
        name="get_risk_free_rate",
        description="useful for obtaining the risk free return"
    )
    
    tools =  [serp_api_tool, get_market_index_details_tool, get_risk_free_rate_tool]

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
                You are very powerful assistant specialising in financial information.
                You will be provided with a list of financial metrics about a user's portfolio such as beta, standard deviation, expected portfolio return,
                assets in the portfolio, sharpe ratio, portfolio's intended time period to be held.
                You are to take these details and provide the user with detailed information of the risk of their portfolio.
                """,
            ),
            (
                "human", 
                """
                    I am going to give you my portfolio in a dictionary of asset_ticker:quantity. My portfolio consists of :{assets}
                    Current value of my portfolio is {value}.
                    Beta of my portfolio is {beta}.
                    How much I have invested in my portfolio is {invested}.
                    Standard deviation of my portfolio is {standard_deviation}.
                    Expected Return of my portfolio is {expected_return}.
                    Sharpe Ratio of my portfolio is {sharpe_ratio}.
                    Sector of my portfolio is {sector}.
                    My investment time period goals are {investment_time_period}.
                    My portfolio's risk aversion is {risk_aversion}.

                    I want you to compare with a benchmark and the risk free rate. Use this as market index: {market_index} and time period: {investment_time_period} and the appropriate tools to calculate its details.
                    When displaying, use this {market_index_long_name} which is the name of {market_index}
                """
            ),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
            
        ]
    )
    llm = ChatOpenAI(temperature = 0.0) # , openai_api_key=""
    llm_with_tools = llm.bind(functions=[format_tool_to_openai_function(t) for t in tools])
    agent = (
        {
            "assets": lambda x: x["assets"],
            "value": lambda x: x["value"],
            "beta": lambda x: x["beta"],
            "invested": lambda x: x["invested"],
            "standard_deviation": lambda x: x["standard_deviation"],
            "expected_return": lambda x: x["expected_return"],
            "sharpe_ratio": lambda x: x["sharpe_ratio"],
            "sector": lambda x: x["sector"],
            "investment_time_period": lambda x: x["investment_time_period"],
            "risk_aversion": lambda x: x["risk_aversion"],
            "market_index": lambda x: x["market_index"],
            "market_index_long_name": lambda x: x["market_index_long_name"],
            "agent_scratchpad": lambda x: format_to_openai_function_messages(
                x["intermediate_steps"]
            ),
        }
        | prompt
        | llm_with_tools
        | OpenAIFunctionsAgentOutputParser()
    )

    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)
    inputs = {
        "assets": assets,
        "value": value,
        "beta": beta,
        "invested": invested,
        "standard_deviation": standard_deviation,
        "expected_return": expected_return,
        "sharpe_ratio": sharpe_ratio,
        "sector": sector,
        "investment_time_period": investment_time_period,
        "risk_aversion": risk_aversion,
        "market_index": market_index,
        "market_index_long_name": market_index_long_name,
    }
    
    response = agent_executor.invoke(inputs)["output"]
    
    return response

class TickerInput(BaseModel):
    ticker: str = Field(description="Stock ticker symbol of a particular stock")

class HistoricalInput(BaseModel):
    ticker: str = Field(description="Stock ticker symbol of a particular stock")
    time_period: str = Field(description="Investment Time Period")

class SharpeRatioInput(BaseModel):
    tickers: list = Field(description="List of stock ticker symbols in a portfolio. Should have a minimum length of 3.")
    time_period: str = Field(description="Investment Time Period")

class SuggestPortfolioOutput(BaseModel):
    answer: str = Field(description="detailed answer to the user prompt to display to user")
    assets: List[dict] = Field(description="list of dictionaries with key of asset ticker symbol and value of its associated weight")

class AssetOutput(BaseModel):
    ticker: str = Field(description="Stock ticker symbol of a particular stock")
    weight: float = Field(description="Associated weight of the asset")

class AssetsOutput(BaseModel):
    assets: List[AssetOutput]

def suggest_portfolio_ai(assets, sector, assets_held, risk_aversion, time_period):
    SERPAPI_KEY = "f0627549432dff35aa32fa8aa1f1e606b22aa354d42b459ef7bf42ae4e3fa9e7"
    search = SerpAPIWrapper(serpapi_api_key=SERPAPI_KEY)
    serp_api_tool = StructuredTool.from_function(
        func=search.run,
        name="search",
        description="useful to descriptive information of an asset such as company description, company industry, company products"
    )
    get_historical_prices_tool = StructuredTool.from_function(
        func=get_historical_prices,
        name="get_historical_prices",
        description="useful for obtaining historical prices of a ticker",
        args_schema=HistoricalInput
    )
    get_daily_returns_tool = StructuredTool.from_function(
        func=get_daily_returns,
        name="get_daily_returns",
        description="useful for obtaining historical daily returns of a ticker",
        args_schema=HistoricalInput
    )
    get_asset_details_general_tool = StructuredTool.from_function(
        func=get_asset_details_general,
        name="get_asset_details_general",
        description="useful for obtaining financial metric details about a ticker(beta, current price, standard deviation, expected asset return, sharpe ratio)",
        args_schema=TickerInput
    )
    get_long_name_tool = StructuredTool.from_function(
        func=get_long_name,
        name="get_long_name",
        description="useful for obtaining name of a ticker to be used to display to user.",
        args_schema=TickerInput
    )
    maximize_sharpe_ratio_tool = StructuredTool.from_function(
        func=maximize_sharpe_ratio,
        name="maximize_sharpe_ratio",
        description="useful for finding weights that maximise the sharpe ratio of a portfolio of an asset.",
        args_schema=SharpeRatioInput
    )
    tools =  [serp_api_tool, get_historical_prices_tool, get_daily_returns_tool, get_asset_details_general_tool, get_long_name_tool, maximize_sharpe_ratio_tool, PythonREPLTool()]

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
                You are very powerful assistant specialising in financial information.
                You are solely required to suggest a portfolio using information and tools provided.
                You should choose a portfolio consisting of minimum 3 assets and a maximum of 10 assets. List the assets to buy as well as the weightage of each asset.
                You should run through at least 100 different combinations of assets chosen from the list and choose the best one.
                You will be provided with a list of assets (which is a model containing the fields: ticker, name, exchange, ipoYear, country, sector, industry, asset_type),
                a list of assets currently in the portfolio. You must only choose assets that exist in the list.
                You will also be provided with a list of tools to use to calculate metrics like current price, historical prices, beta, standard deviation, expected asset return, sharpe ratio.
                
                You are to also use the optimize_portfolio_tool to aid in finding the best portfolio.
                Display to the user in a list format of the assets with their corresponding names, ticker, weights, quantity of each asset to buy.
                Investment Time Period parameter for any tool should always be {time_period} or '1year'.
                The portfolio
                """,
            ),
            (
                "human", 
                """
                    Here is the list of assets: {assets}.
                    The sector that my portfolio should be in: {sector}.
                    Here is what my portfolio already consists (dictionary of asset_ticker:quantity): {assets_held}.
                    My risk aversion is {risk_aversion}.
                    
                """
            ),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
            
        ]
    )
    llm = ChatOpenAI(temperature = 0.0) # , openai_api_key=OPENAI_KEY
    llm_with_tools = llm.bind(functions=[format_tool_to_openai_function(t) for t in tools])
    agent = (
        {
            "assets": lambda x: x["assets"],
            "assets_held": lambda x: x["assets_held"],
            "sector": lambda x: x["sector"],
            "risk_aversion": lambda x: x["risk_aversion"],
            "time_period": lambda x: x["time_period"],
            "agent_scratchpad": lambda x: format_to_openai_function_messages(
                x["intermediate_steps"]
            ),
        }
        | prompt
        | llm_with_tools
        | OpenAIFunctionsAgentOutputParser()
    )

    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)
    inputs = {
        "assets": assets,
        "sector": sector,
        "assets_held": assets_held,
        "risk_aversion": risk_aversion,
        "time_period": time_period,
    }
    
    response = agent_executor.invoke(inputs)["output"]
    print(response)
    parser = PydanticOutputParser(pydantic_object=AssetsOutput)
    prompt = ChatPromptTemplate(
    messages=[
        HumanMessagePromptTemplate.from_template(
            "Convert this to json.\n{format_instructions}\n{question}"
        )
    ],
    input_variables=["question"],
    partial_variables={
        "format_instructions": parser.get_format_instructions(),
    },
    )
    chat_model = ChatOpenAI(
        model="gpt-3.5-turbo", # , openai_api_key=OPENAI_KEY
        max_tokens=1000
    )
    _input = prompt.format_prompt(question=response)
    output = chat_model(_input.to_messages())
    parsed = parser.parse(output.content)
    print(parsed)
    return response, parsed