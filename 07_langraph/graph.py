from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(
    api_key = os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

class State(TypedDict):
    query: str
    llm_result: str | None


def chat_bot(state: State):
    query = state['query']

    #llm call with query
    llm_response = client.chat.completions.create(
        model = "gemini-2.0-flash",
        messages = [
            {"role": "user", "content": query}
        ]
    )

    result = llm_response.choices[0].message.content
    state['llm_result'] = result

    return state


graph_builder = StateGraph(State)

graph_builder.add_node("chat_bot", chat_bot)

graph_builder.add_edge(START, "chat_bot")
graph_builder.add_edge("chat_bot", END)

graph = graph_builder.compile()

def main():
    user = input("> ")

    # invoke the graph
    _state = {
        "query": user,
        "llm_result": None
    }
    graph_result = graph.invoke(_state)
    print("Graph result: ", graph_result)


main()