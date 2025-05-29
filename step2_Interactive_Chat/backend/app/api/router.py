from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import logging
from app.database.session import get_db
from app.services.chat import ChatService
from app.schemas.chat import QuestionRequest

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/chat/question")
async def ask_question(
    question: QuestionRequest,
    db: Session = Depends(get_db)
):
    """
    Ask a question about the video highlights.
    Returns relevant highlights based on semantic similarity.
    """
    try:
        logger.info(f"Received question: {question.text}")
        chat_service = ChatService(db)
        highlights = chat_service.get_relevant_highlights(question.text)
        logger.info(f"Found {len(highlights)} relevant highlights")
        return highlights
    except Exception as e:
        logger.error(f"Error processing question: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error processing question: {str(e)}"
        ) 