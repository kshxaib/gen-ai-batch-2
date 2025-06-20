from typing_extensions import TypedDict
from typing import Annotated
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START, END
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os
import requests
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode, tools_condition

load_dotenv()

todos = []

@tool()
def add_todos(task: str):
    """Add the input to the DB"""
    todos.append(task)
    return True

@tool()
def get_all_todos():
    """Returns all the todos"""
    return todos

@tool()
def count_todos():
    """Returns the number of todos"""
    return len(todos)

@tool
def get_weather(city: str) -> str:
    """Get current weather for a given city."""
    url = f"https://wttr.in/{city}?format=%C+%t"
    response = requests.get(url)
    if response.status_code == 200:
        return f"The weather in {city} is {response.text.strip()}"
    return "Something went wrong."

tools = [get_weather, add_todos, get_all_todos, count_todos]

class State(TypedDict):
    messages: Annotated[list, add_messages]

llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=os.getenv("GEMINI_API_KEY"))
llm_with_tools = llm.bind_tools(tools)

def chatbot(state: State):
    message = llm_with_tools.invoke(state["messages"])
    return {"messages": [message]}
    
tool_node = ToolNode(tools=tools)

graph_builder = StateGraph(State)

graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("tools", tool_node)

graph_builder.add_edge(START, "chatbot")
graph_builder.add_conditional_edges("chatbot", tools_condition)
graph_builder.add_edge("tools", "chatbot")

graph = graph_builder.compile()


def main():
    while True:
        user_query = input("> ")

        state = State(
            messages=[{"role": "user", "content": user_query}]
        )

        for event in graph.stream(state, stream_mode="values"):
            if "messages" in event:
                event["messages"][-1].pretty_print()
main()