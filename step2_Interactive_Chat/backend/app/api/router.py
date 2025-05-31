from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import logging
from typing import List

from app.database.session import get_db
from app.services.chat import ChatService
from app.schemas.chat import QuestionRequest, HighlightResponse

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/chat",
    tags=["chat"],
    responses={
        404: {"description": "Not found"},
        500: {"description": "Internal server error"}
    }
)

@router.post("/question", response_model=List[HighlightResponse])
async def ask_question(
    question: QuestionRequest,
    db: Session = Depends(get_db)
) -> List[HighlightResponse]:
    """Ask a question about video highlights and get relevant responses."""
    try:
        logger.info(f"Processing question: {question.text[:100]}...")
        chat_service = ChatService(db)
        highlights = chat_service.get_relevant_highlights(question.text)
        
        if not highlights:
            logger.info("No relevant highlights found")
            return []
            
        logger.info(f"Found {len(highlights)} relevant highlights")
        return highlights
        
    except ValueError as e:
        logger.error(f"Invalid question: {e}")
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error processing question: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error while processing question"
        ) 