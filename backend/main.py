from fastapi import FastAPI
from api.issue import router as issue_router
from api.automation import router as automation_router
from api.chat import router as chat_router
from database import init_db

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    init_db()

app.include_router(issue_router)
app.include_router(automation_router)
app.include_router(chat_router)
