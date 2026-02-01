import os
from agents.script import email_script
from dotenv import load_dotenv, find_dotenv
from services.authority import authority
from database import get_cached_authority
from agents.classify import classify

def send(issue, recipient=None):
    """
    Android-Compatible Email Agent.
    Does NOT execute any OS actions (no smtplib, no webbrowser).
    Returns a JSON Action Plan for the Android client.
    """
    load_dotenv(find_dotenv(), override=True)
    
    # 1. Enrich issue if missing metadata
    if "location" not in issue or "category" not in issue or "authority" not in issue:
        desc = issue.get("description", "")
        if desc:
            print("Enriching issue metadata...")
            meta = classify(desc)
            issue.update(meta)
            
            # Smart Authority Resolution
            cat = issue.get("category", "General")
            loc = issue.get("location", "Bangalore")
            
            # Try DB first
            cached = get_cached_authority(cat, loc)
            if cached:
                issue["authority"] = cached.get("name", "Municipal Authority")
            else:
                 mapping = {"pothole": "Municipal Corporation", "garbage": "Municipal Corporation", "water": "Water Board"}
                 issue["authority"] = mapping.get(cat.lower(), "Municipal Authority")

    # 2. Generate Content (Subject & Body)
    body = email_script(issue)
    
    cat = issue.get("category", "Civic Issue")
    loc = issue.get("location", "General Area")
    desc = issue.get("description", "")
    
    if len(desc) < 60:
         subject = f"Formal Complaint: {desc.title()} - {loc}"
    else:
         subject = f"Formal Complaint: {cat} Issue in {loc}"

    # 3. Resolve Recipient (Logic remains the same, just no fallback to default env var)
    if not recipient:
        print("Resolving recipient...")
        
        # A. Check Payload
        auth_data = issue.get("authority")
        if isinstance(auth_data, dict):
            recipient = auth_data.get("contact", {}).get("email")

        # B. Check DB
        if not recipient or "not available" in str(recipient).lower():
            cat = issue.get("category", "General")
            loc = issue.get("location", "Bangalore")
            cached = get_cached_authority(cat, loc)
            if cached:
                recipient = cached.get("contact", {}).get("email")
                print(f"Using DB Cached Email: {recipient}")
        
        # C. Re-Scrape
        if not recipient or "not available" in str(recipient).lower():
            print("Re-scraping authority...")
            try:
                auth_info = authority(issue.get("category"), issue.get("location"))
                recipient = auth_info.get("contact", {}).get("email")
            except Exception as e:
                print(f"Scrape failed: {e}")

    # 4. Return Android Action
    # The Android app will handle the Intent.ACTION_SENDTO with Intent.EXTRA_STREAM
    
    # Collect attachments (support both keys for flexibility)
    attachments = issue.get("attachments", []) or issue.get("images", [])
    
    return {
        "action": "OPEN_EMAIL",
        "payload": {
            "to": recipient if recipient and "not available" not in str(recipient).lower() else "",
            "subject": subject,
            "body": body,
            "attachments": attachments
        },
        "info": "Action plan generated. Client should execute OPEN_EMAIL."
    }