from tool_handler.tool_bank import ToolBank
from tool_handler.tool import Tool, Param
from agent_handler.agent import Agent
from agent_handler.task import Task

import json


# example
tool_bank = ToolBank()

def get_current_weather(location, unit="fahrenheit"):
    """Get the current weather in a given location"""
    if "tokyo" in location.lower():
        return json.dumps({"location": "Tokyo", "temperature": "10", "unit": "celsius"})
    elif "san francisco" in location.lower():
        return json.dumps({"location": "San Francisco", "temperature": "72", "unit": "fahrenheit"})
    elif "paris" in location.lower():
        return json.dumps({"location": "Paris", "temperature": "22", "unit": "celsius"})
    else:
        return json.dumps({"location": location, "temperature": "unknown"})
    
def get_current_time(location):
    """Get the current time in a given location"""
    if "tokyo" in location.lower():
        return json.dumps({"location": "Tokyo", "time": "12:00"})
    elif "san francisco" in location.lower():
        return json.dumps({"location": "San Francisco", "time": "00:00"})
    elif "paris" in location.lower():
        return json.dumps({"location": "Paris", "time": "09:00"})
    else:
        return json.dumps({"location": location, "time": "unknown"})

get_current_weather_tool = Tool("get_current_weather", "Get the current weather in a given location", get_current_weather)
get_current_weather_tool.define_function_param([
    Param("location", "string", "The location to get the weather for", True),
    Param("unit", "string", "The unit to get the temperature in", False)
])
tool_bank.add_tool(get_current_weather_tool)


get_current_time_tool = Tool("get_current_time", "Get the current time in a given location", get_current_time)
get_current_time_tool.define_function_param([
    Param("location", "string", "The location to get the time for", True)
])
tool_bank.add_tool(get_current_time_tool)


weather_agent = Agent("weather getter", "you give the user access to the current weather", "this agent will give the user access to the current weather", True)
weather_agent.add_tool(get_current_weather_tool)
weather_agent.add_tool(get_current_time_tool)

task = Task("get the current weather and time in tokyo", "a json object with the current weather and time in tokyo")
weather_agent.set_task(task)

print(weather_agent.execute_task())


