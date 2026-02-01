from pydantic import BaseModel
from typing import Optional

class Issue(BaseModel):
    description: str
    category: str
    location: str
    authority: str
    status: str = ""
    referenceId: Optional[str] = None
