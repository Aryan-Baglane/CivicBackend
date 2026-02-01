from fastapi import APIRouter
from agents.classify import classify
from services.authority import authority

router = APIRouter(prefix="/issue")

@router.post("/")
async def create_issue(data: dict):
    # Start with explicit data
    meta = {
        "description": data.get("description", ""),
        "category": data.get("complaint type"),
        "location": data.get("location"),
        "department": data.get("department")
    }
    
    # If key fields are missing, try to classify from description
    if not meta["category"] or not meta["location"]:
        classified_meta = classify(meta["description"])
        if not meta["category"]:
            meta["category"] = classified_meta.get("category", "General")
        if not meta["location"]:
            meta["location"] = classified_meta.get("location", "Bangalore")
            
    auth = await authority(meta["category"], meta["location"], meta["department"])

    return {
        "description": meta["description"],
        "category": meta["category"],
        "location": meta["location"],
        "authority": auth,
        "status": "REPORTED"
    }
