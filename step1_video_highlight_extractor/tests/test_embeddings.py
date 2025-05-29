import os
from dotenv import load_dotenv
from src.llm.llm_service import LLMService
from src.database import DatabaseManager
from src.database.models import Highlight
from src.llm.constants import EMBEDDING_DIM

def test_embedding_dimensions():
    """Test that embeddings are generated with correct dimensions."""
    # Load environment variables
    load_dotenv()
    
    # Initialize services
    llm_service = LLMService()
    db_manager = DatabaseManager()
    
    # Test text
    test_text = "This is a test description for embedding dimension verification."
    
    # Generate embedding
    embedding = llm_service.generate_embedding(test_text)
    
    # Print embedding info
    print("\nStep1 Embedding Test:")
    print("-" * 50)
    print(f"Expected dimension: {EMBEDDING_DIM}")
    print(f"Actual dimension: {len(embedding)}")
    print(f"First few values: {embedding[:5]}")
    print(f"Last few values: {embedding[-5:]}")
    
    # Verify dimension
    assert len(embedding) == EMBEDDING_DIM, f"Expected {EMBEDDING_DIM} dimensions, got {len(embedding)}"
    
    # Test database storage
    with db_manager.get_session() as session:
        # Create a test highlight
        highlight = Highlight(
            video_id=1,  # Assuming video_id 1 exists
            timestamp=0.0,
            description=test_text,
            embedding=embedding
        )
        
        try:
            session.add(highlight)
            session.commit()
            print("\nSuccessfully stored embedding in database")
            
            # Verify stored embedding
            stored_highlight = session.query(Highlight).filter_by(description=test_text).first()
            if stored_highlight is not None and stored_highlight.embedding is not None:
                stored_dim = len(stored_highlight.embedding)
                print(f"Stored embedding dimension: {stored_dim}")
                assert stored_dim == EMBEDDING_DIM, f"Stored embedding has wrong dimension: {stored_dim}"
            
            # Clean up
            session.delete(highlight)
            session.commit()
            
        except Exception as e:
            session.rollback()
            print(f"\nError storing embedding: {str(e)}")
            raise

if __name__ == "__main__":
    test_embedding_dimensions() 