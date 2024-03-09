import os
from langchain.tools import StructuredTool
from langchain_openai import ChatOpenAI
from langchain_community.utilities import SerpAPIWrapper
import yfinance as yf
from typing import Dict
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.tools.convert_to_openai import format_tool_to_openai_function
from langchain.agents.format_scratchpad import format_to_openai_function_messages
from langchain.agents.format_scratchpad.openai_tools import ( format_to_openai_tool_messages )
from langchain.agents.output_parsers.openai_tools import OpenAIToolsAgentOutputParser
from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser
from langchain.agents import AgentExecutor, load_tools
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain, SequentialChain
from langchain.memory import SimpleMemory
from langchain.pydantic_v1 import BaseModel, Field
from langchain_community.tools.google_finance import GoogleFinanceQueryRun
from langchain_community.utilities.google_finance import GoogleFinanceAPIWrapper
from app.views import create_portfolio_openAI, add_to_portfolio, get_portfolios, edit_portfolio_name, delete_portfolio, remove_from_portfolio
import numpy as np
from pypfopt.expected_returns import mean_historical_return
from pypfopt.risk_models import CovarianceShrinkage
from pypfopt.efficient_frontier import EfficientFrontier
from pypfopt.discrete_allocation import DiscreteAllocation, get_latest_prices

NOT_AVAILABLE_CONSTANT = 'Not Available'

def get_user_risk_level():
    """Returns the user's risk level"""
    return 'Moderate'

def get_user_expected_market_return():
    """Returns the user's expected market return"""
    return 0.05

def get_user_risk_free_rate():
    """Returns the user's risk free rate"""
    return 0.03

def get_asset_price_yahoo(ticker):
    """Make a request to the yfinance API to get the asset price using asset's ticker symbol as input."""
    ticker_data = yf.Ticker(ticker)
    recent = ticker_data.history(period="1d")
    price = recent.iloc[0]["Close"]
    currency = ticker_data.info["currency"]
    if recent.iloc[0]["Close"] == None:
        price = NOT_AVAILABLE_CONSTANT
    if currency == None:
        currency = NOT_AVAILABLE_CONSTANT
    return {"price": price, "currency": currency}

def get_asset_beta_yahoo(ticker):
    """Make a request to the yfinance API to get the asset beta using asset's ticker symbol as input."""
    ticker_data = yf.Ticker(ticker)
    beta = ticker_data.info.get('beta')
    if beta == None:
        beta = NOT_AVAILABLE_CONSTANT
    return beta

def get_asset_stddev_yahoo(ticker):
    """Returns the asset's standard deviation. Display it as a percentage."""
    tickerData = yf.download(ticker, start='2020-01-01', end='2023-12-31')
    returns = tickerData['Close'].pct_change()
    volatility = returns.std()
    if volatility == None:
        volatility = NOT_AVAILABLE_CONSTANT
    return volatility

def calculate_asset_expected_return(risk_free_rate, beta, market_return):
    """Calculates the asset's expected return"""
    if risk_free_rate != None or beta != None or market_return != None:
        return risk_free_rate + beta * (market_return - risk_free_rate)
    return NOT_AVAILABLE_CONSTANT

def calculate_asset_sharpe_ratio(expected_asset_return, risk_free_rate, standard_deviation):
    """Calculate the asset's sharpe ratio."""
    if expected_asset_return != None or risk_free_rate != None or standard_deviation != None:
        return (expected_asset_return - risk_free_rate)/standard_deviation
    return NOT_AVAILABLE_CONSTANT

def get_portfolio_stddev(portfolio_assets):
    stock_list = [k for k in portfolio_assets]
    weight_list = [v["weight"] for k,v in portfolio_assets.items()]
    data = yf.download(
        tickers = stock_list,
        start = '2020-01-01',
        end = '2023-12-31'
    )
    prices = data['Adj Close']
    returns = prices.pct_change()

    portfolio = np.array([weight_list])

    covariance = np.cov(returns.fillna(0).T)
    portfolio_standard_deviation = np.sqrt(np.dot(np.dot(portfolio, covariance), portfolio.T))
    return portfolio_standard_deviation

def calculate_portfolio_details(ticker_symbols):
    """
    Returns all the required details of a portfolio to display to user
    :param ticker_symbols: A dictionary of symbols and quantities of the assets in a portfolio
    :return: A dictionary of relevant information of the stock and the entire portfolio
    """
    risk_free_rate = get_user_risk_free_rate()
    portfolio_details = {}
    portfolio_details["Portfolio"] = {}
    portfolio_details["Portfolio"]["asset_value"] = 0
    portfolio_details["Portfolio"]["expected_return"] = 0
    for asset, quantity in ticker_symbols.items():
        portfolio_details[asset] = get_asset_details(asset)
        portfolio_details[asset]["quantity"] = quantity
        # Calculate the total value of the asset in the portfolio
        portfolio_details[asset]["asset_value"] = portfolio_details[asset]["price"] * quantity
        portfolio_details["Portfolio"]["asset_value"] += portfolio_details[asset]["asset_value"]

    # Calculate weight, expected portfolio return, and standard deviation
    for asset in portfolio_details:
        if asset != "Portfolio":
            # Calculate weight of each asset
            portfolio_details[asset]["weight"] = portfolio_details[asset]["price"] * portfolio_details[asset]["quantity"] / portfolio_details["Portfolio"]["asset_value"]

            # Add to expected portfolio return
            portfolio_details["Portfolio"]["expected_return"] += portfolio_details[asset]["expected_asset_return"] * portfolio_details[asset]["weight"]
        else:
            portfolio_details[asset]["weight"] = 1
    
    portfolio_assets = {k : v for k, v in portfolio_details.items() if k != "Portfolio"}
    portfolio_details["Portfolio"]["standard_deviation"] = get_portfolio_stddev(portfolio_assets)

    if portfolio_details["Portfolio"]["standard_deviation"] is not None:
        portfolio_details["Portfolio"]["sharpe_ratio"] = (portfolio_details["Portfolio"]["expected_return"] - risk_free_rate) / portfolio_details["Portfolio"]["standard_deviation"]
    else:
        portfolio_details.sharpe_ratio = "NA"

    return portfolio_details

def get_asset_details(ticker: str) -> dict:
    """
    Returns all the required details of a stock to display to user
    :param ticker: Stock ticker symbol
    :return: A dictionary of information of the stock with keys and their description:
    beta: Beta of the stock
    price: Current price of the stock
    currency: Currency of the stock in the market
    standard_deviation: Standard deviation of the stock
    expected_asset_return: Expected asset return of the stock based on user's risk profile
    sharpe_ratio: Sharpe ratio of the stock
    user_risk_level: User's risk level
    user_market_return: User's expected market return
    user_risk_free_rate: User's risk free rate
    """
    beta = get_asset_beta_yahoo(ticker)
    price = get_asset_price_yahoo(ticker)
    standard_deviation = get_asset_stddev_yahoo(ticker)
    risk_level = get_user_risk_level()
    market_return = get_user_expected_market_return()
    risk_free_rate = get_user_risk_free_rate()
    expected_asset_return = calculate_asset_expected_return(risk_free_rate, beta, market_return)
    sharpe_ratio = calculate_asset_sharpe_ratio(expected_asset_return, risk_free_rate, standard_deviation)
    return_dict = {
        "beta": beta, 
        "price": price['price'], 
        "currency": price['currency'],
        "standard_deviation": standard_deviation,
        "expected_asset_return": expected_asset_return,
        "sharpe_ratio": sharpe_ratio,
        "user_risk_level": risk_level, 
        "user_market_return": market_return,
        "user_risk_free_rate": risk_free_rate
    }
    return return_dict

def suggest_portfolio(tickers):
    """
    Returns weights, allocation and performance of a portfolio with a budget of $10000
    :param tickers: List of ticker symbols of stocks to include in the portfolio
    :return: A dictionary of information of the portfolio with keys and their description:
    weights: Ordered dictionary of weights of each stocks
    performance: a set of three floats with description (Expected annual return, Annual volatility, Sharpe Ratio)
    allocation: Dictionary of number of stocks to purchase for each asset
    leftover_cash: Leftover sum of cash after allocation of stock
    """
    data = yf.download(
        tickers = tickers,
        start = '2020-01-01',
        end = '2024-1-1'
    )
    prices = data['Adj Close']
    
    mu = mean_historical_return(prices)
    S = CovarianceShrinkage(prices).ledoit_wolf()
    ef = EfficientFrontier(mu, S)
    weights = ef.max_sharpe()
    cleaned_weights = ef.clean_weights()
    performance = ef.portfolio_performance()
    latest_prices = get_latest_prices(prices)

    da = DiscreteAllocation(weights, latest_prices, total_portfolio_value=10000)

    allocation, leftover = da.greedy_portfolio()
    
    return_dict = {
        'weights': cleaned_weights,
        'performance': performance,
        'allocation': allocation,
        'leftover_cash': leftover,
    }

    return return_dict

class TickerInput(BaseModel):
    ticker: str = Field(description="Stock ticker symbol of a particular stock")

class UserInput(BaseModel):
    username: str = Field(description="Username of user")

class QuantityInput(BaseModel):
    quantity: float = Field(description="Quantity of the asset")

class PortfolioInput(BaseModel):
    ticker_symbols: Dict[TickerInput, QuantityInput]

def get_tools():
    SERPAPI_KEY = "f0627549432dff35aa32fa8aa1f1e606b22aa354d42b459ef7bf42ae4e3fa9e7"
    search = SerpAPIWrapper(serpapi_api_key=SERPAPI_KEY)
    serp_api_tool = StructuredTool.from_function(
        func=search.run,
        name="search",
        description="useful to descriptive information of an asset such as company description, company industry, company products"
    )
    get_asset_details_tool = StructuredTool.from_function(
        func=get_asset_details,
        name="get_asset_details",
        description="useful for obtaining details of an asset (price, beta, currency, standard_deviation, expected_asset_return, expected_asset_return, sharpe_ratio, user_risk_level, user_market_return, user_risk_free_rate,)",
        args_schema=TickerInput
    )
    get_portfolios_tool = StructuredTool.from_function(
        func=get_portfolios,
        name="get_portfolios",
        description="useful for obtaining user's portfolios",
        args_schema=UserInput
    )
    # Calculates a portfolio's detail on the spot (Not needed, rethink entire model again)
    # calculate_portfolio_details_tool = StructuredTool.from_function(
    #     func=calculate_portfolio_details,
    #     name="calculate_portfolio_details",
    #     description="useful for calculating details about a given portfolio",
    #     args_schema=PortfolioInput
    # )

    tools = [
        serp_api_tool,
        get_asset_details_tool,
        get_portfolios_tool
    ]

    return tools

# TODO: Only allow logged in user to create portfolios
def chatbot(input, user):
    # Tools
    # get_portfolios_tool = StructuredTool.from_function(get_portfolios)
    # create_portfolio_tool = StructuredTool.from_function(create_portfolio_openAI)
    # add_to_portfolio_tool = StructuredTool.from_function(add_to_portfolio)
    # edit_portfolio_name_tool = StructuredTool.from_function(edit_portfolio_name)
    # delete_portfolio_tool = StructuredTool.from_function(delete_portfolio)
    # remove_from_portfolio_tool = StructuredTool.from_function(remove_from_portfolio)
    # suggest_portfolio_tool = StructuredTool.from_function(suggest_portfolio)
    
    tools =  get_tools() #[serp_api_tool, get_asset_details_tool, calculate_portfolio_details_tool, create_portfolio_tool, get_portfolios_tool, edit_portfolio_name_tool, add_to_portfolio_tool, delete_portfolio_tool, remove_from_portfolio_tool, suggest_portfolio_tool, google_finance_tool]

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
                You are very powerful assistant specialising in financial information.
                First of all, you are required to find out what is the stock ticker symbol given a stock/asset name and use this as an input to all tools.

                When a user is querying about a specific stock/asset, you must provide the user with the stock name, stock ticker symbol, a basic description of the company, their industry and the product, 
                stock price, stock beta, stock's standard deviation, stock's expected returns, and stock's sharpe ratio. You should also state that the metrics were calculated based on user's defined
                details such as user's risk level, user's expected market return and user's risk free rate. List all the details in a nice readable structure.
                
                You must also be able to handle user's queries regarding their portfolios such as retrieving a list of portfolios, 
                
                You should also help to calculate details about a provided portfolio taking the assets and their quantities as inputs.

                Output should always be formatted in a readable and neat manner with markdown.
                
                """,
            ),
            ('human', "My username is {user}"),
            MessagesPlaceholder("chat_history", optional=True),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
            
        ]
    )
    llm = ChatOpenAI(temperature = 0.0, openai_api_key="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")
    llm_with_tools = llm.bind(functions=[format_tool_to_openai_function(t) for t in tools])
    agent = (
        {
            "input": lambda x: x["input"],
            "user": lambda x: x["user"],
            "agent_scratchpad": lambda x: format_to_openai_function_messages(
                x["intermediate_steps"]
            ),
        }
        | prompt
        | llm_with_tools
        | OpenAIFunctionsAgentOutputParser()
    )

    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)
    # CHAIN ONE: Getting what stocks to invest in
    # template = """You are a financial assistant specialising in suggesting a portfolio of stocks to invest in such that they are well diversified based on their industries.
    # You are required to suggest a list of stocks (number of stocks to be defined by the user's input). If not defined, suggest a portfolio of minimum 5 stocks. Input: {input}"""
    # prompt_template = PromptTemplate(input_variables=["input"], template=template)
    # chain_one = LLMChain(llm=llm,prompt=prompt_template)

    # chain_two = agent

    # overall_chain = SequentialChain(chains=[chain_one, chain_two], input_variables=["input"], verbose=True, memory=SimpleMemory(memories={"user": user}))
    response = agent_executor.invoke({"input":input, "user": user})["output"]
    print(response)
    # response = overall_chain.invoke({"input": input})["output"]
    
    return response