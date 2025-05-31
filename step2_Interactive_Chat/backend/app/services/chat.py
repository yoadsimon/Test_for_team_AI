from typing import List, Dict, Any, Optional
import os
import numpy as np
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.config import settings
from app.models.highlight import Highlight, Video
import logging

logger = logging.getLogger(__name__)

class ChatService:
    """Service for handling chat interactions with video highlights using semantic search."""
    
    def __init__(self, db: Session) -> None:
        self.db = db
        try:
            self.model = GoogleGenerativeAIEmbeddings(
                model="models/embedding-001",
                google_api_key=settings.GOOGLE_API_KEY,
                task_type="retrieval_document"
            )
        except Exception as e:
            logger.error(f"Failed to initialize embedding model: {e}")
            raise

    def get_relevant_highlights(self, question: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Find relevant highlights based on semantic similarity to the question using pgvector."""
        try:
            question_embedding = self.model.embed_query(question)
            
            highlights = (
                self.db.query(
                    Highlight,
                    Video.filename,
                    (1 - Highlight.embedding.cosine_distance(question_embedding)).label('similarity_score')
                )
                .join(Video, Highlight.video_id == Video.id)
                .filter(Highlight.embedding.isnot(None))
                .filter(1 - Highlight.embedding.cosine_distance(question_embedding) >= settings.SIMILARITY_THRESHOLD)
                .order_by(Highlight.embedding.cosine_distance(question_embedding))
                .limit(limit)
                .all()
            )
            
            if not highlights:
                logger.warning("No highlights found in database")
                return []
            
            results = [
                {
                    "id": highlight.id,
                    "description": highlight.description,
                    "timestamp": highlight.timestamp,
                    "similarity_score": similarity_score,
                    "video_name": filename
                }
                for highlight, filename, similarity_score in highlights
            ]
            
            logger.info(f"Found {len(results)} relevant highlights for question")
            return results
            
        except Exception as e:
            logger.error(f"Error processing question: {e}", exc_info=True)
            raise ValueError(f"Failed to process question: {str(e)}") 