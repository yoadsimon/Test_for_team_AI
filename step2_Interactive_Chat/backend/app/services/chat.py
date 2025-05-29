from typing import List, Optional
import os
import numpy as np
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.highlight import Highlight

class ChatService:
    def __init__(self, db: Session):
        self.db = db
        # Initialize the Gemini embedding model
        self.model = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=settings.GOOGLE_API_KEY,
            task_type="retrieval_document"
        )

    def get_relevant_highlights(self, question: str, limit: int = 5) -> List[dict]:
        """
        Find relevant highlights based on the question using semantic search.
        Returns highlights with their similarity scores.
        """
        try:
            # Generate embedding for the question
            question_embedding = self.model.embed_query(question)
            # Convert to numpy array for manual l2 distance computation
            question_embedding_np = np.array(question_embedding)

            # Query highlights (without using l2_distance on the DB side)
            highlights = (
                self.db.query(Highlight)
                .filter(Highlight.embedding != None)
                .all()
            )

            # Compute l2 distance manually and sort
            highlight_distances = []
            for highlight in highlights:
                # Convert highlight.embedding (assumed to be a list or numpy array) to a numpy array
                highlight_embedding_np = np.array(highlight.embedding)
                # Compute l2 distance using numpy.linalg.norm
                distance = np.linalg.norm(highlight_embedding_np - question_embedding_np)
                highlight_distances.append((highlight, distance))

            # Sort by distance (ascending) and take the top 'limit' highlights
            highlight_distances.sort(key=lambda x: x[1])
            top_highlights = [h for h, _ in highlight_distances[:limit]]

            # Format results with similarity scores
            results = []
            for highlight in top_highlights:
                # (Recompute distance if needed, or use the stored distance from highlight_distances)
                highlight_embedding_np = np.array(highlight.embedding)
                distance = np.linalg.norm(highlight_embedding_np - question_embedding_np)
                similarity_score = 1.0 / (1.0 + distance)  # Convert distance to similarity score

                if similarity_score >= settings.SIMILARITY_THRESHOLD:
                    results.append({
                        "id": highlight.id,
                        "text": highlight.description,  # Using description from step1 schema
                        "timestamp": highlight.timestamp,
                        "similarity_score": similarity_score,
                        "summary": highlight.summary
                    })

            return results
        except Exception as e:
            raise ValueError(f"Error processing question: {str(e)}") 