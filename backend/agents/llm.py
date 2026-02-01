import os
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

client = OpenAI(
    base_url=os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

def llm(prompt: str) -> str:
    completion = client.chat.completions.create(
        extra_headers={
            "HTTP-Referer": "https://civic-backend.com", # Optional, for including your app on openrouter.ai rankings.
            "X-Title": "Civic Backend", # Optional. Shows in rankings on openrouter.ai.
        },
        model=os.getenv("OPENROUTER_MODEL", "google/gemini-2.0-flash-001"),
        messages=[
            {
                "role": "user",
                "content": prompt,
            },
        ],
    )
    return completion.choices[0].message.content.strip()
