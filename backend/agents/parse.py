import re

def reference(text: str):
    match = re.search(r"\b\d{4,}\b", text)
    return match.group() if match else None
