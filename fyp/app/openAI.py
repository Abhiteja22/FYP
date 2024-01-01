import json
import os
from openai import OpenAI
from dotenv import load_dotenv

GPT_MODEL = "gpt-3.5-turbo"

load_dotenv()
client = OpenAI()

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "Get the current weather",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA",
                    },
                    "format": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "The temperature unit to use. Infer this from the users location.",
                    },
                },
                "required": ["location", "format"],
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_n_day_weather_forecast",
            "description": "Get an N-day weather forecast",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA",
                    },
                    "format": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "The temperature unit to use. Infer this from the users location.",
                    },
                    "num_days": {
                        "type": "integer",
                        "description": "The number of days to forecast",
                    }
                },
                "required": ["location", "format", "num_days"]
            },
        }
    },
]

def get_current_weather(location, format):
    if location == "Beijing" and format == "celsius":
        return "WOW CORRECT"
    else:
        return "WRONG"
    
def execute_function_call(message):
    if message.tool_calls[0].function.name == "get_current_weather":
        results = get_current_weather(json.loads(message.tool_calls[0].function.arguments)["location"], json.loads(message.tool_calls[0].function.arguments)["format"])
    else:
        results = f"Error: function {message['tool_calls'][0]['function']['name']} does not exist"
    return results

completion = client.chat.completions.create(
  model="gpt-3.5-turbo",
  messages=[
    {"role": "system", "content": "Don't make assumptions about what values to plug into functions. Ask for clarification if a user request is ambiguous."},
    {"role": "user", "content": "What's the weather like today in Beijing in celcius?"}
  ],
  tools=tools
)
message = completion.choices[0].message
message.content = str(message.tool_calls[0].function)
if message.tool_calls:
    results = execute_function_call(message)

print(results)
