import os
from dotenv import load_dotenv

load_dotenv()
key = os.getenv("GROQ_API_TOKEN")

if key is None:
    print("Key is None — .env isn't being found, or the variable name doesn't match")
else:
    print(f"Length: {len(key)}")
    print(f"Starts with: {key[:5]}")
    print(f"Has leading/trailing whitespace: {key != key.strip()}")
    print(f"Contains a quote character: {chr(34) in key or chr(39) in key}")