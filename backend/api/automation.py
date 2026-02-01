from fastapi import APIRouter
from agents.orchestrator import run

router = APIRouter(prefix="/automation")

@router.post("/start")
def start(data: dict):
    return run(data["issue"], data["channel"], data.get("recipient_email"))
