from langchain.tools import StructuredTool
from langchain.chat_models import ChatOpenAI
from langchain.utilities import SerpAPIWrapper
import yfinance as yf
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.tools.convert_to_openai import format_tool_to_openai_function
from langchain.agents.format_scratchpad import format_to_openai_function_messages
from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser
from langchain.agents import AgentExecutor
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain, SequentialChain
from langchain.memory import SimpleMemory
from app.views import create_portfolio_openAI, add_to_portfolio, get_portfolios, edit_portfolio_name, delete_portfolio, remove_from_portfolio
import numpy as np

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
    """Returns various details of the portfolio taking a dictionary of key: asset ticker symbols and value: quantity"""
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

def get_asset_details(ticker):
    """Gets all the required details of a stock to display to user using asset's ticker symbol as input."""
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
        "user_risk_level": risk_level, 
        "user_market_return": market_return,
        "user_risk_free_rate": risk_free_rate,
        "expected_asset_return": expected_asset_return,
        "sharpe_ratio": sharpe_ratio
    }
    return return_dict

# TODO: Only allow logged in user to create portfolios
def chatbot(input, user):
    # Tools
    search = SerpAPIWrapper(serpapi_api_key="f0627549432dff35aa32fa8aa1f1e606b22aa354d42b459ef7bf42ae4e3fa9e7")
    serp_api_tool = StructuredTool.from_function(search.run)
    get_asset_details_tool = StructuredTool.from_function(get_asset_details)
    calculate_portfolio_details_tool = StructuredTool.from_function(calculate_portfolio_details)
    get_portfolios_tool = StructuredTool.from_function(get_portfolios)
    create_portfolio_tool = StructuredTool.from_function(create_portfolio_openAI)
    add_to_portfolio_tool = StructuredTool.from_function(add_to_portfolio)
    edit_portfolio_name_tool = StructuredTool.from_function(edit_portfolio_name)
    delete_portfolio_tool = StructuredTool.from_function(delete_portfolio)
    remove_from_portfolio_tool = StructuredTool.from_function(remove_from_portfolio)
    tools = [serp_api_tool, get_asset_details_tool, calculate_portfolio_details_tool, create_portfolio_tool, get_portfolios_tool, edit_portfolio_name_tool, add_to_portfolio_tool, delete_portfolio_tool, remove_from_portfolio_tool]

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
                You are very powerful assistant specialising in financial information.
                First of all, you should always find out what is the stock ticker symbol given a stock/asset name and use this as an input to all tools.
                You must give information about all the information of the stock/portfolio and the {user} including the financial risk metrics and also the industry and brief introduction of the company. 
                You must help {user} to create a portfolio taking the required name of the portfolio as input. 
                Username is always {user}.
                """,
            ),
            ("user", "{input}"),
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
    # CHAIN ONE: GETTING STOCK TICKER SYMBOL
    # template = """You are a financial assistant specialising in differentiating stock ticker symbols and names.
    # Given a stock's name, it is your job to retrieve the stock's ticker symbol.
    
    # Stock:
    # {input}
    # Ticker Symbol:"""
    # prompt_template = PromptTemplate(input_variables=["stock"], template=template)
    # chain_one = LLMChain(llm=llm,prompt=prompt_template)

    # chain_two = agent

    # overall_chain = SequentialChain(chains=[chain_one, chain_two], verbose=True, input_variables=["input"], memory=SimpleMemory(memories={"user": user}))

    response = agent_executor.invoke({"input":input, "user": user})["output"]
    # response = overall_chain.invoke({"input": input})["output"]
    print(response)
    return response