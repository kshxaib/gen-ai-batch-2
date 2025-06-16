from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()

# Zero-shot Prompting

SYSTEM_PROMPT = """
    You are an AI expert in Coding. You only know Python and nothing else.
    You help users in solving there python doubts only and nothing else.
    If user tried to ask something else apart from Python you can just roast him.
""" 

response = client.chat.completions.create(
    model = "gpt-4.1-mini",
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": "Hey, I am Khan Shoaib"},
        {"role": "assistant", "content": "Hey Khan Shoaib, How can I help you? I am an expert in Python."},
        {"role": "user", "content": "How to write a code in python for adding two numbers?"}
    ]
)

print(response.choices[0].message.content)