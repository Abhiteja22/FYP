from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from langchain.tools import StructuredTool
from langchain.agents import initialize_agent, AgentType
from langchain.chat_models import ChatOpenAI
from langchain.utilities import SerpAPIWrapper
import yfinance as yf
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.tools.convert_to_openai import format_tool_to_openai_function
from langchain.agents.format_scratchpad import format_to_openai_function_messages
from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser
from langchain.agents import AgentExecutor

def home(requests):
    return HttpResponse("Hello Chatbot!")

import yfinance as yf

def get_user_risk_level():
    pass

def get_user_expected_market_return():
    pass

def get_user_risk_free_rate():
    pass

def get_asset_price_yahoo(ticker):
    """Make a request to the yfinance API to get the asset price using asset's ticker symbol as input."""
    ticker_data = yf.Ticker(ticker)
    recent = ticker_data.history(period="1d")
    return {"price": recent.iloc[0]["Close"], "currency": ticker_data.info["currency"]}

def get_asset_beta_yahoo(ticker):
    """Make a request to the yfinance API to get the asset beta using asset's ticker symbol as input."""
    ticker_data = yf.Ticker(ticker)
    beta = ticker_data.info.get('beta')
    return beta

def get_asset_stddev_yahoo():
    pass

def get_asset_expected_return():
    pass

def get_asset_sharpe_ratio():
    pass

def get_portfolio_details():
    pass

def get_asset_details(ticker):
    """Gets all the required details of a stock to display to user using asset's ticker symbol as input."""
    beta = get_asset_beta_yahoo(ticker)
    price = get_asset_price_yahoo(ticker)
    return {"beta": beta, "price": price['price'], "currency": price['currency']}

@api_view(['POST'])
def chatbot(request):
    message = request.data['message']

    # Tools
    search = SerpAPIWrapper(serpapi_api_key="f0627549432dff35aa32fa8aa1f1e606b22aa354d42b459ef7bf42ae4e3fa9e7")
    serp_api_tool = StructuredTool.from_function(search.run)
    get_asset_details_tool = StructuredTool.from_function(get_asset_details)
    tools = [serp_api_tool, get_asset_details_tool]

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are very powerful assistant specialising in financial information",
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
            "agent_scratchpad": lambda x: format_to_openai_function_messages(
                x["intermediate_steps"]
            ),
        }
        | prompt
        | llm_with_tools
        | OpenAIFunctionsAgentOutputParser()
    )

    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

    response = agent_executor.invoke({"input":message})["output"]
    return Response({'message': response})