from pydantic import BaseModel
from typing import Optional

class QuestionRequest(BaseModel):
    text: str

class HighlightResponse(BaseModel):
    id: int
    text: str
    timestamp: float
    similarity_score: float
    summary: Optional[str] = None 