import pytest
from datetime import datetime
import numpy as np

from src.database import Video, Highlight


def test_add_and_get_video(test_db):
    """Test adding and retrieving a video."""
    # Add a video
    video = test_db.add_video(filename="test.mp4", duration=60.5)
    
    # Verify video was added correctly
    assert video.id is not None
    assert video.filename == "test.mp4"
    assert video.duration == 60.5
    assert isinstance(video.created_at, datetime)
    
    # Retrieve the video
    retrieved_video = test_db.get_video(video.id)
    assert retrieved_video is not None
    assert retrieved_video.id == video.id
    assert retrieved_video.filename == video.filename
    assert retrieved_video.duration == video.duration


def test_add_and_get_highlight(test_db):
    """Test adding and retrieving a highlight."""
    # First add a video
    video = test_db.add_video(filename="test.mp4", duration=60.5)
    
    # Add a highlight
    embedding = [0.1] * 768  # Create a test embedding
    highlight = test_db.add_highlight(
        video_id=video.id,
        timestamp=15.5,
        description="Test highlight",
        embedding=embedding,
        summary="Test summary"
    )
    
    # Verify highlight was added correctly
    assert highlight.id is not None
    assert highlight.video_id == video.id
    assert highlight.timestamp == 15.5
    assert highlight.description == "Test highlight"
    assert np.allclose(highlight.embedding, embedding)
    assert highlight.summary == "Test summary"
    assert isinstance(highlight.created_at, datetime)
    
    # Get highlights for the video
    highlights = test_db.get_video_highlights(video.id)
    assert len(highlights) == 1
    assert highlights[0].id == highlight.id
    assert highlights[0].description == highlight.description


def test_find_similar_highlights(test_db):
    """Test finding similar highlights using vector similarity."""
    # Add a video
    video = test_db.add_video(filename="test.mp4", duration=60.5)
    
    # Add multiple highlights with different embeddings
    embeddings = [
        [0.1] * 768,  # Base embedding
        [0.2] * 768,  # Different embedding
        [0.11] * 768,  # Similar to base embedding
    ]
    
    for i, embedding in enumerate(embeddings):
        test_db.add_highlight(
            video_id=video.id,
            timestamp=float(i * 10),
            description=f"Highlight {i}",
            embedding=embedding
        )
    
    # Search for similar highlights using the base embedding
    similar_highlights = test_db.find_similar_highlights(
        embedding=embeddings[0],
        limit=2
    )
    
    # Should find the base embedding and the similar one
    assert len(similar_highlights) == 2
    # The first result should be the exact match
    assert np.allclose(similar_highlights[0].embedding, embeddings[0])
    # The second result should be the similar embedding
    assert np.allclose(similar_highlights[1].embedding, embeddings[2])


def test_delete_video(test_db):
    """Test deleting a video and its highlights."""
    # Add a video
    video = test_db.add_video(filename="test.mp4", duration=60.5)
    
    # Add some highlights
    for i in range(3):
        test_db.add_highlight(
            video_id=video.id,
            timestamp=float(i * 10),
            description=f"Highlight {i}"
        )
    
    # Verify video and highlights exist
    assert test_db.get_video(video.id) is not None
    assert len(test_db.get_video_highlights(video.id)) == 3
    
    # Delete the video
    assert test_db.delete_video(video.id) is True
    
    # Verify video and highlights are deleted
    assert test_db.get_video(video.id) is None
    assert len(test_db.get_video_highlights(video.id)) == 0
    
    # Try to delete non-existent video
    assert test_db.delete_video(999) is False


def test_video_highlight_relationship(test_db):
    """Test the relationship between Video and Highlight models."""
    # Add a video using the correct method signature
    video = test_db.add_video(filename="test_video.mp4", duration=120.0)
    video_id = video.id
    
    # Create a highlight for the video using the correct method signature
    highlight = test_db.add_highlight(
        video_id=video_id,
        timestamp=10.0,  # Using timestamp instead of start_time/end_time
        description="Test highlight",
        embedding=np.random.rand(768).tolist()  # Using list instead of numpy array
    )
    highlight_id = highlight.id
    
    # Retrieve the video and verify the relationship
    retrieved_video = test_db.get_video(video_id)
    assert retrieved_video is not None
    assert len(retrieved_video.highlights) == 1
    
    # Re-query the highlight through the session to ensure it's attached
    with test_db.get_session() as session:
        attached_highlight = session.query(Highlight).filter(Highlight.id == highlight_id).first()
        assert attached_highlight is not None
        assert attached_highlight.video is not None
        assert attached_highlight.video.id == video_id
        assert attached_highlight.video.filename == "test_video.mp4"


def test_null_embedding_handling(test_db):
    """Test handling of highlights without embeddings."""
    # Add a video
    video = test_db.add_video(filename="test.mp4", duration=60.5)
    
    # Add a highlight without embedding
    highlight = test_db.add_highlight(
        video_id=video.id,
        timestamp=15.5,
        description="No embedding highlight"
    )
    
    # Verify highlight was added correctly
    assert highlight.embedding is None
    
    # Add a highlight with embedding
    highlight_with_embedding = test_db.add_highlight(
        video_id=video.id,
        timestamp=25.5,
        description="With embedding highlight",
        embedding=[0.1] * 768
    )
    
    # Verify highlight was added correctly
    assert highlight_with_embedding.embedding is not None
    assert len(highlight_with_embedding.embedding) == 768


def test_embedding_and_storage(test_db):
    """Test generating embeddings and storing them in the database."""
    from src.llm.llm_service import LLMService
    from src.database.models import Video, Highlight
    from datetime import datetime

    # Initialize services
    llm_service = LLMService()
    
    # Create a test video
    video = Video(
        filename="test_video.mp4",
        duration=10.0,
        width=1280,
        height=720,
        fps=30.0,
        summary="Test video",
        created_at=datetime.now()
    )
    
    # Save video to get an ID
    with test_db.get_session() as session:
        session.add(video)
        session.commit()
        session.refresh(video)
    
    # Test descriptions
    descriptions = [
        "A person walking down a street",
        "A car driving past the camera",
        "Birds flying in the sky"
    ]
    
    stored_highlights = []
    
    # Generate embeddings and store highlights
    for i, desc in enumerate(descriptions):
        # Generate embedding
        embedding = llm_service.generate_embedding(desc)
        
        # Verify embedding dimension
        assert len(embedding) == 768, f"Expected embedding dimension 768, got {len(embedding)}"
        
        # Create and store highlight
        highlight = Highlight(
            video_id=video.id,
            timestamp=float(i),
            description=desc,
            embedding=embedding,
            summary=f"Summary of {desc}",
            created_at=datetime.now()
        )
        
        with test_db.get_session() as session:
            session.add(highlight)
            session.commit()
            session.refresh(highlight)
            stored_highlights.append(highlight)
    
    # Verify storage and retrieval
    with test_db.get_session() as session:
        # Check all highlights were stored
        highlights = session.query(Highlight).filter(Highlight.video_id == video.id).all()
        assert len(highlights) == len(descriptions), "Not all highlights were stored"
        
        # Check embeddings were stored correctly
        for h in highlights:
            assert h.embedding is not None, "Embedding was not stored"
            assert len(h.embedding) == 768, f"Stored embedding has wrong dimension: {len(h.embedding)}"
            
        # Test similarity search
        first_highlight = highlights[0]
        similar = test_db.find_similar_highlights(first_highlight.embedding, limit=2)
        assert len(similar) > 0, "No similar highlights found" 