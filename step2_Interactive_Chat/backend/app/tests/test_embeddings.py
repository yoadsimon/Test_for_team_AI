import os
from dotenv import load_dotenv
from app.services.chat import ChatService
from app.database.session import SessionLocal
from app.models.highlight import Highlight
from app.core.constants import EMBEDDING_DIM

def test_embedding_dimensions():
    """Test that embeddings are generated with correct dimensions."""
    # Load environment variables
    load_dotenv()
    
    # Initialize services
    db = SessionLocal()
    chat_service = ChatService(db)
    
    # Test text
    test_text = "This is a test description for embedding dimension verification."
    
    try:
        # Generate embedding
        question_embedding = chat_service.model.embed_query(test_text)
        
        # Print embedding info
        print("\nStep2 Embedding Test:")
        print("-" * 50)
        print(f"Expected dimension: {EMBEDDING_DIM}")
        print(f"Actual dimension: {len(question_embedding)}")
        print(f"First few values: {question_embedding[:5]}")
        print(f"Last few values: {question_embedding[-5:]}")
        
        # Verify dimension
        assert len(question_embedding) == EMBEDDING_DIM, f"Expected {EMBEDDING_DIM} dimensions, got {len(question_embedding)}"
        
        # Test database storage
        highlight = Highlight(
            video_id=1,  # Assuming video_id 1 exists
            timestamp=0.0,
            description=test_text,
            embedding=question_embedding
        )
        
        try:
            db.add(highlight)
            db.commit()
            print("\nSuccessfully stored embedding in database")
            
            # Verify stored embedding
            stored_highlight = db.query(Highlight).filter_by(description=test_text).first()
            if stored_highlight is not None and stored_highlight.embedding is not None:
                stored_dim = len(stored_highlight.embedding)
                print(f"Stored embedding dimension: {stored_dim}")
                assert stored_dim == EMBEDDING_DIM, f"Stored embedding has wrong dimension: {stored_dim}"
            
            # Clean up
            db.delete(highlight)
            db.commit()
            
        except Exception as e:
            db.rollback()
            print(f"\nError storing embedding: {str(e)}")
            raise
            
    finally:
        db.close()

if __name__ == "__main__":
    test_embedding_dimensions() 