from agents.script import call_script
from dotenv import load_dotenv, find_dotenv
from agents.classify import classify
from database import get_cached_authority

def call_authority(issue):
    """
    Android-Compatible Voice Agent Simulator.
    Generates a script for the IN-APP voice agent (TTS).
    Does NOT make real calls.
    Returns: JSON with action "START_VOICE_AGENT".
    """
    load_dotenv(find_dotenv(), override=True)
    
    # 0. Enrich issue (Missing in original implementation)
    if "authority" not in issue:
        # 1. Classify if description exists
        if "description" in issue:
            meta = classify(issue["description"])
            issue.update(meta)
            
        # 2. Resolve Authority Name (Keep it simple for Call Agent)
        cat = issue.get("category", "General")
        loc = issue.get("location", "Bangalore")
        
        cached = get_cached_authority(cat, loc)
        if cached:
            issue["authority"] = cached.get("name", "Municipal Authority")
        else:
             mapping = {"pothole": "Municipal Corporation", "garbage": "Municipal Corporation", "water": "Water Board"}
             issue["authority"] = mapping.get(cat.lower(), "Municipal Authority")

    # 1. Generate Call Script
    # Uses LLM to generate a natural, polite, <60s script
    script = call_script(issue)
    
    # 2. Return Android Action
    # Backend acts as Planner; Android acts as Executor.
    return {
        "action": "START_VOICE_AGENT",
        "payload": {
            "script": script,
            "authority_name": issue.get("authority", "Authority"),
            "location": issue.get("location", "Location")
        },
        "info": "Voice script generated. Client should execute START_VOICE_AGENT (In-App)."
    }
