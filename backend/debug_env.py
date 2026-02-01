import os
from dotenv import load_dotenv, find_dotenv

print(f"Current working directory: {os.getcwd()}")
env_path = find_dotenv()
print(f"Searching for .env: {env_path}")
load_dotenv(env_path)
key = os.getenv("OPENROUTER_API_KEY")
if key:
    print("Key FOUND!")
    print(f"Key starts with: {key[:5]}...")
else:
    print("Key NOT found.")
