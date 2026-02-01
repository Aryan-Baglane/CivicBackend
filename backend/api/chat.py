from fastapi import APIRouter
from agents.llm import llm

router = APIRouter(prefix="/chat")

@router.post("/")
def chat(data: dict):
    return {
        "reply": llm(f"You are a civic assistant. User says: {data['message']}")
    }
