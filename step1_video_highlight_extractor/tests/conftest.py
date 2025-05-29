import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.database import Base, DatabaseManager


@pytest.fixture(scope="session")
def test_db_url():
    """Create a test database URL."""
    # Use a test database name to avoid interfering with production data
    os.environ["POSTGRES_DB"] = "video_highlights_test"
    return DatabaseManager()._get_database_url()


@pytest.fixture(scope="session")
def test_engine(test_db_url):
    """Create a test database engine."""
    engine = create_engine(test_db_url)
    return engine


@pytest.fixture(scope="function")
def test_db(test_engine):
    """Create a fresh database for each test."""
    # Create all tables
    Base.metadata.create_all(test_engine)
    
    # Create a new database manager for testing
    db = DatabaseManager()
    db.engine = test_engine
    db.SessionLocal = sessionmaker(bind=test_engine)
    
    # Ensure pgvector extension is installed
    db.ensure_pgvector_extension()
    
    yield db
    
    # Clean up after each test
    Base.metadata.drop_all(test_engine) 