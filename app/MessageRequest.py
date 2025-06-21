from pydantic import BaseModel
from typing import Optional

class MessageRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

