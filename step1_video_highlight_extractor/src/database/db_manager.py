import os
from contextlib import contextmanager
from typing import Generator, List, Optional

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker, joinedload

from .models import Base, Highlight, Video


class DatabaseManager:
    """Manager class for database operations."""

    def __init__(self):
        """Initialize the database manager with connection details."""
        self.db_url = self._get_database_url()
        self.engine = create_engine(self.db_url)
        self.SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )

    def _get_database_url(self) -> str:
        """Get the database URL from environment variables."""
        host = os.getenv("POSTGRES_HOST", "localhost")
        port = os.getenv("POSTGRES_PORT", "5432")
        user = os.getenv("POSTGRES_USER", "postgres")
        password = os.getenv("POSTGRES_PASSWORD", "postgres")
        db_name = os.getenv("POSTGRES_DB", "video_highlights")

        return f"postgresql://{user}:{password}@{host}:{port}/{db_name}"

    def create_tables(self) -> None:
        """Create all database tables."""
        with self.get_session() as session:
            # Drop all tables first
            Base.metadata.drop_all(bind=self.engine)
            # Ensure pgvector extension exists
            session.execute(text('CREATE EXTENSION IF NOT EXISTS vector;'))
            session.commit()
            # Create tables with new schema
            Base.metadata.create_all(bind=self.engine)

    def ensure_pgvector_extension(self) -> None:
        """Ensure the pgvector extension is installed in the database."""
        with self.get_session() as session:
            session.execute(text('CREATE EXTENSION IF NOT EXISTS vector;'))
            session.commit()

    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """Get a database session."""
        session = self.SessionLocal()
        try:
            yield session
        finally:
            session.close()

    def add_video(self, filename: str, duration: float) -> Video:
        """Add a new video to the database."""
        with self.get_session() as session:
            video = Video(filename=filename, duration=duration)
            session.add(video)
            session.commit()
            session.refresh(video)
            return video

    def add_highlight(
        self,
        video_id: int,
        timestamp: float,
        description: str,
        embedding: Optional[List[float]] = None,
        summary: Optional[str] = None,
    ) -> Highlight:
        """Add a new highlight to the database."""
        with self.get_session() as session:
            highlight = Highlight(
                video_id=video_id,
                timestamp=timestamp,
                description=description,
                embedding=embedding,
                summary=summary,
            )
            session.add(highlight)
            session.commit()
            session.refresh(highlight)
            return highlight

    def get_video(self, video_id: int) -> Optional[Video]:
        """Get a video by ID."""
        with self.get_session() as session:
            return session.query(Video).options(joinedload(Video.highlights)).filter(Video.id == video_id).first()

    def get_video_highlights(self, video_id: int) -> List[Highlight]:
        """Get all highlights for a video."""
        with self.get_session() as session:
            return (
                session.query(Highlight)
                .filter(Highlight.video_id == video_id)
                .order_by(Highlight.timestamp)
                .all()
            )

    def find_similar_highlights(
        self, embedding: List[float], limit: int = 5
    ) -> List[Highlight]:
        """Find similar highlights using vector similarity search (ORM)."""
        with self.get_session() as session:
            return (
                session.query(Highlight)
                .filter(Highlight.embedding != None)
                .order_by(Highlight.embedding.l2_distance(embedding))
                .options(joinedload(Highlight.video))
                .limit(limit)
                .all()
            )

    def save_video(self, video: Video) -> Video:
        """Save a video object to the database."""
        with self.get_session() as session:
            session.add(video)
            session.commit()
            session.refresh(video)
            return video

    def save_highlight(self, highlight: Highlight) -> Highlight:
        """Save a highlight object to the database."""
        with self.get_session() as session:
            session.add(highlight)
            session.commit()
            session.refresh(highlight)
            return highlight

    def delete_video(self, video_id: int) -> bool:
        """Delete a video and all its highlights."""
        with self.get_session() as session:
            video = session.query(Video).filter(Video.id == video_id).first()
            if video:
                session.delete(video)
                session.commit()
                return True
            return False 