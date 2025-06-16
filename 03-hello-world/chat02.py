from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()

# Few-shot Prompting: The model is provided with a few examples of the desired output

SYSTEM_PROMPT = """
    You are an AI expert in Coding. You only know Python and nothing else.
    You help users in solving there python doubts only and nothing else.
    If user tried to ask something else apart from Python you can just roast him.

    Examples:
    User: How to make a tea?
    Assistant: What makes you think I am a chef?

    Examples: 
    User: How to write a function in python?
    Assistant: def fn_name(x: int) -> int:
                    pass #Logic of the function
""" 

response = client.chat.completions.create(
    model = "gpt-4.1-mini",
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": "Hey, I am Khan Shoaib"},
        {"role": "assistant", "content": "Hey Khan Shoaib, How can I help you? I am an expert in Python."},
        {"role": "user", "content": "What 75% attendence is required? in colleges"}
    ]
)

print(response.choices[0].message.content)