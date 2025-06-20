from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.mongodb import MongoDBSaver
from langgraph.types import interrupt, Command
import json
import os


load_dotenv()

@tool()
def human_assistance(query: str) -> str:
    """Request assistance from a human."""
    human_response = interrupt({"query": query}) # this saves the state in DB and kills the graph
    return human_response["data"]

tools = [human_assistance]

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
graph_builder.add_edge("chatbot", END)


def create_chat_graph(checkpointer):
    return graph_builder.compile(checkpointer=checkpointer)

def user_chat():
    DB_URI="mongodb://admin:admin@localhost:27017"
    config = {"configurable": {"thread_id": 12}}

    with MongoDBSaver.from_conn_string(DB_URI) as mongo_checkpointer:
        graph_with_mongo = create_chat_graph(mongo_checkpointer)

        while True:
            user_input = input("> ")

            _state = State(
                messages=[{"role": "user", "content": user_input}]
            )

            for event in graph_with_mongo.stream(_state, config, stream_mode="values"):
                if "messages" in event:
                    event["messages"][-1].pretty_print()


def admin_call():
    DB_URI = "mongodb://admin:admin@localhost:27017"
    config = {"configurable": {"thread_id": 12}}

    with MongoDBSaver.from_conn_string(DB_URI) as mongo_checkpointer:
        graph_with_mongo = create_chat_graph(mongo_checkpointer)

        state = graph_with_mongo.get_state(config)
        last_message = state.values["messages"][-1]

        user_query = None
        for call in last_message.tool_calls:
            if call.get("name") == "human_assistance":
                args = call.get("args", {})
                user_query = args.get("query")

        print("User Has a Query: ", user_query)
        solution = input("> ")

        resume_command = Command(resume={"data": solution})

        for event in graph_with_mongo.stream(resume_command, config, stream_mode="values"):
            if "messages" in event:
                event["messages"][-1].pretty_print()
  

user_chat()