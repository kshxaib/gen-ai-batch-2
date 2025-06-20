# flake8: noqa

from dotenv import load_dotenv
from mem0 import Memory
import os
from openai import OpenAI
import json

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(
    api_key = os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

config = {
    "version": "v1.1",
    "embedder": {
        "provider": "openai",
        "config": {
            "api_key": OPENAI_API_KEY,
            "model": "text-embedding-3-small"
        }
    },
    "llm": {"provider": "openai", "config": {"api_key": OPENAI_API_KEY, "model": "gpt-4.1"}},
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "host": "vector-db",
            "port": "6333"
        }
    },
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "url": "http://localhost:6333",
            "port": 6333    
        }
    },
    "graph_store": {
        "provider": "neo4j",
        "config": {
            "url": "bolt://localhost:7687",
            "username": "neo4j",
            "password": "reform-william-center-vibrate-press-5829"
        }
    }
}

mem_client = Memory.from_config(config)

def chat():
    while True:
        user_query = input("> ")

        relevant_memories = mem_client.search(query=user_query, user_id="shoaib")
        memories = [f"ID: {mem.get('id')}, Memory: {mem.get('memory')}" for mem in relevant_memories.get("results")]
        SYSTEM_PROMPT = f"""
            You are an memory aware assistant which reponds to userwith context.
            You are given with past memories and facts about the user.

            Memory of the user:
            {json.dumps(memories)}
        """

        result = client.chat.completions.create(
            model = "gemini-2.0-flash",
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_query}
            ]
        )
        print("🤖: ", result.choices[0].message.content)

        mem_client.add([
            {"role": "user", "content": user_query},
            {"role": "assistant", "content": result.choices[0].message.content},
        ], user_id="shoaib")

chat()