import json
from agents.llm import llm

def classify(text: str):
    prompt = f"""
    Extract structured civic issue data.
    Return ONLY JSON with:
    category, location, urgency.

    Issue: {text}
    """
    response = llm(prompt)
    if "```" in response:
        response = response.replace("```json", "").replace("```", "")
    return json.loads(response)
