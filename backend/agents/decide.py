from agents.llm import llm

def decide_channel(issue, preference):
    prompt = f"""
    Decide best channel for complaint.

    Category: {issue['category']}
    User preference: {preference}
    Available: EMAIL, WEB, APP, CALL

    Return ONE word.
    """
    return llm(prompt)
