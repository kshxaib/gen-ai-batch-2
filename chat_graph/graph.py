#flake8: noqa
from typing_extensions import TypedDict
from typing import Annotated
from langgraph.graph.message import add_messages
from langchain.chat_models import init_chat_model
from langgraph.graph import StateGraph, START, END
from dotenv import load_dotenv
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.mongodb import MongoDBSaver

load_dotenv()

class State(TypedDict):
    messages: Annotated[list, add_messages]

llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=os.getenv("GEMINI_API_KEY"))

def chat_node(state: State):
    response = llm.invoke(state["messages"])
    return {"messages": response}

graph_builder = StateGraph(State)

graph_builder.add_node("chat_node", chat_node)

graph_builder.add_edge(START, "chat_node")
graph_builder.add_edge("chat_node", END)


def compile_graph_with_checkpointer(checkpointer):
    graph_with_checkpointer = graph_builder.compile(checkpointer=checkpointer)
    return graph_with_checkpointer


def main():
    # mongodb://<username>:<password>@<host>:<port>
    DB_URI="mongodb://admin:admin@localhost:27017"
    config = {"configurable": {"thread_id": 1}}
    with MongoDBSaver.from_conn_string(DB_URI) as mongo_checkpointer:

        graph_with_mongo = compile_graph_with_checkpointer(mongo_checkpointer)

        user = input("> ")

        _state = {"messages": [{"role": "user", "content": user}]}

        # This creates a fresh state / chat (jab tak execute hoga tab tak state mainted hoga)
        result = graph_with_mongo.invoke(_state, config)
        # This deletes the state after the graph is executed / END

        print("Graph result: ", result)

main()