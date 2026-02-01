from agents.scraper import find_contact_info
from database import save_authority

async def authority(category, location, department=None):
    # Map common categories to authority types
    mapping = {
        "pothole": "Municipal Corporation",
        "garbage": "Municipal Corporation",
        "water": "Water Supply Board",
        "electricity": "Electricity Board",
        "traffic": "Traffic Police",
        "crime": "Police"
    }
    
    # 1. Determine Authority Name
    if department:
        auth_search_term = department
    else:
        # Smart mappings based on location
        cat_lower = category.lower()
        loc_lower = location.lower()
        
        if "transport" in cat_lower and "delhi" in loc_lower:
            auth_search_term = "Delhi Transport Corporation (DTC)"
        elif "police" in cat_lower:
            auth_search_term = "Police"
        else:
            auth_search_term = mapping.get(cat_lower, "Municipal Corporation")
        
    print(f"Fetching details for {auth_search_term} in {location}...")

    # 2. Call the Scraper
    try:
        details = await find_contact_info(auth_search_term, location)
        
        # 3. SAVE TO DB (Persistent Cache, refreshed on every call as requested)
        result = {
            "name": auth_search_term,
            "contact": details
        }
        save_authority(category, location, result)
        
        return result
    except Exception as e:
        print(f"Service Error: {e}")
        return {
            "name": auth_search_term,
            "contact": {
                "phone": "Not available",
                "email": "Not available",
                "website": "Not available",
                "officer": "Not available"
            }
        }
