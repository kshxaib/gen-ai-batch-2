import tiktoken

encoder = tiktoken.encoding_for_model("gpt-4o")

text = "Hello, I am Khan Shoaib"
tokens = encoder.encode(text)

print("Tokens: ", tokens)

encodedTokens = [13225, 11, 357, 939, 39894, 24635, 64, 526]

print(encoder.decode(encodedTokens))