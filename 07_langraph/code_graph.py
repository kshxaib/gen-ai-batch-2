#flake8: noqa

from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from openai import OpenAI
from dotenv import load_dotenv
import os
from pydantic import BaseModel
from typing import Literal

load_dotenv()

client = OpenAI(
    api_key = os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

class ClassifyMessageResponse(BaseModel):
    is_coding_question: bool

class CodeAccuracyResponse(BaseModel):
    accuracy_percentage: str

class State(TypedDict):
    user_query: str
    llm_result: str | None
    accuracy_percentage: str | None
    is_coding_question: bool | None


def classify_message(state: State):
    query = state['user_query']

    SYSTEM_PROMPT = """
        You are an AI assistant. Your job is to detect if the user's query is related
        to coding question or not.
        Return the response in specified JSON boolean only.
    """
    
    # Structured response / Output
    response = client.beta.chat.completions.parse(
        model = "gemini-1.5-flash",
        response_format = ClassifyMessageResponse,
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": query}
        ]
    )

    is_coding_question  = response.choices[0].message.parsed.is_coding_question
    state["is_coding_question"] = is_coding_question

    return state


def route_query(state: State) -> Literal["general_query", "coding_query"]:
    is_coding = state["is_coding_question"]

    if is_coding:
        return "coding_query"
    else:
        return "general_query"


def general_query(state: State):
    query = state["user_query"]

    response = client.chat.completions.create(
        model = "gemini-1.5-flash",
        messages = [
            {"role": "user", "content": query}
        ]
    )

    result = response.choices[0].message.content
    state["llm_result"] = result

    return state

def coding_query(state: State):
    query = state["user_query"]

    SYSTEM_PROMPT = """
        You are a Coding Expert Agent, just answer the user's coding question no comments.
    """

    response = client.chat.completions.create(
        model = "gemini-2.0-flash",
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": query}
        ]
    )

    result = response.choices[0].message.content
    state["llm_result"] = result

    return state


def coding_validate_query(state: State):
    query = state["user_query"]
    llm_code = state["llm_result"]

    SYSTEM_PROMPT = f"""
        You are expert in calculating accuracy of code. 
        according to the query and code, return the accuracy percentage.
        
        User Query: {query},
        Code: {llm_code}
    """

    response = client.beta.chat.completions.parse(
        model = "gemini-2.0-flash",
        response_format = CodeAccuracyResponse,
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": query}
        ]
    )

    accuracy_percentage = response.choices[0].message.parsed.accuracy_percentage
    state["accuracy_percentage"] = accuracy_percentage

    return state


def check_accuracy(state: State) -> Literal["coding_query", "__end__"]:
    accuracy_percentage = state["accuracy_percentage"]

    if float(accuracy_percentage.strip('%')) > 95:
        return "__end__"
    else:
        return "coding_query"
    


graph_builder = StateGraph(State)

# Define nodes
graph_builder.add_node("classify_message", classify_message)
graph_builder.add_node("route_query", route_query)
graph_builder.add_node("general_query", general_query)
graph_builder.add_node("coding_query", coding_query)
graph_builder.add_node("coding_validate_query", coding_validate_query)

# Define edges
graph_builder.add_edge(START, "classify_message")
graph_builder.add_conditional_edges("classify_message", route_query)

graph_builder.add_edge("general_query", END)

graph_builder.add_edge("coding_query", "coding_validate_query")
graph_builder.add_conditional_edges("coding_validate_query", check_accuracy)

graph = graph_builder.compile()

def main():
    user = input("> ")

    _state = {
        "user_query": user,
        "llm_result": None,
        "accuracy_percentage": None,
        "is_coding_question": False
    }

    for event in graph.stream(_state):
        print("Event: ", event)

    # response = graph.invoke(_state)
    # print("Graph result: ", response)

main()