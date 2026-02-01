def report_via_web(issue):
    """
    Android-Compatible Web Agent.
    Returns a JSON Action Plan for adding a complaint via a web portal.
    """
    
    # 1. Determine URL (Mock logic for now, could be dynamic based on location)
    # Ideally, we scrape this validation too, but for now we fallback to generic portals
    location = issue.get("location", "").lower()
    
    if "delhi" in location:
        url = "https://mcdonline.nic.in/portal/grievance"
    elif "bangalore" in location:
        url = "https://bengaluru.citizenmatters.in/" # Example placeholder
    else:
        url = "https://services.india.gov.in/"

    # 2. Return Android Action
    return {
        "action": "OPEN_WEB",
        "payload": {
            "url": url,
            "autoFill": {
                "description": issue.get("description", ""),
                "category": issue.get("category", ""),
                "location": issue.get("location", "")
            }
        },
        "info": "Web portal identified. Client should execute OPEN_WEB."
    }
