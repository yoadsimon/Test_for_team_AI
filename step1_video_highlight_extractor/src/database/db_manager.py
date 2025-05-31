import os
from contextlib import contextmanager
from typing import Generator, List, Optional
import logging

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker, joinedload

from .models import Base, Highlight, Video


class DatabaseManager:
    """Manager class for database operations."""

    def __init__(self):
        """Initialize the database manager with connection details."""
        self.db_url = self._get_database_url()
        self.engine = create_engine(
            self.db_url, 
            pool_pre_ping=True,
            pool_timeout=30,
            pool_recycle=3600,
            connect_args={"connect_timeout": 10}
        )
        self.SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )
        self.logger = logging.getLogger(__name__)

    def _get_database_url(self) -> str:
        """Get the database URL from environment variables."""
        host = os.getenv("POSTGRES_HOST", "localhost")
        port = os.getenv("POSTGRES_PORT", "5432")
        user = os.getenv("POSTGRES_USER", "postgres")
        password = os.getenv("POSTGRES_PASSWORD", "postgres")
        db_name = os.getenv("POSTGRES_DB", "video_highlights")

        return f"postgresql://{user}:{password}@{host}:{port}/{db_name}"

    def ensure_tables_exist(self) -> None:
        """Ensure database tables exist without dropping existing data."""
        try:
            with self.get_session() as session:
                try:
                    result = session.execute(text("SELECT COUNT(*) FROM highlights"))
                    count = result.scalar()
                    self.logger.info(f"Database ready with {count} existing highlights")
                    return
                except Exception:
                    self.logger.info("Tables don't exist, creating them...")
                    pass
            
            self.logger.info("Ensuring pgvector extension...")
            try:
                with self.get_session() as session:
                    session.execute(text('CREATE EXTENSION IF NOT EXISTS vector;'))
                    session.commit()
                self.logger.info("pgvector extension ready")
            except Exception as e:
                self.logger.info(f"pgvector extension might already exist: {e}")
                
            self.logger.info("Creating tables if needed...")
            Base.metadata.create_all(bind=self.engine)
            self.logger.info("Tables ready")
            
        except Exception as e:
            self.logger.error(f"Database error: {e}")
            raise

    def create_tables(self) -> None:
        """Create database tables with proper transaction handling."""
        try:
            with self.get_session() as session:
                self.logger.info("Dropping existing tables...")
                try:
                    session.execute(text("""
                        SELECT pg_terminate_backend(pid) 
                        FROM pg_stat_activity 
                        WHERE datname = 'video_highlights' 
                        AND pid <> pg_backend_pid()
                        AND state = 'idle'
                    """))
                    session.commit()
                    self.logger.info("Terminated idle connections")
                except Exception as e:
                    self.logger.warning(f"Could not terminate connections: {e}")
                    session.rollback()
                
                Base.metadata.drop_all(bind=self.engine)
                self.logger.info("Tables dropped")
                
            self.logger.info("Creating pgvector extension...")
            try:
                with self.get_session() as session:
                    session.execute(text('CREATE EXTENSION IF NOT EXISTS vector;'))
                    session.commit()
                self.logger.info("pgvector extension ready")
            except Exception as e:
                self.logger.info(f"pgvector extension might already exist: {e}")
                
            self.logger.info("Creating new tables...")
            Base.metadata.create_all(bind=self.engine)
            self.logger.info("Tables created successfully")
            
        except Exception as e:
            self.logger.error(f"Database error: {e}")
            raise

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
        """Find similar highlights using vector similarity search."""
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

    def batch_save_highlights(self, highlights: List[Highlight]) -> List[Highlight]:
        """Save multiple highlights efficiently."""
        if not highlights:
            return []
        
        with self.get_session() as session:
            try:
                session.add_all(highlights)
                session.commit()
                
                for highlight in highlights:
                    session.refresh(highlight)
                
                return highlights
                
            except Exception as e:
                session.rollback()
                self.logger.error(f"Batch save failed: {e}")
                
                saved_highlights = []
                for highlight in highlights:
                    try:
                        session.add(highlight)
                        session.commit()
                        session.refresh(highlight)
                        saved_highlights.append(highlight)
                    except Exception as e:
                        session.rollback()
                        self.logger.error(f"Failed to save individual highlight: {e}")
                        continue
                
                return saved_highlights

    def get_videos_summary(self) -> List[dict]:
        """Get a summary of all videos and their highlight counts."""
        with self.get_session() as session:
            result = session.execute(text("""
                SELECT 
                    v.id,
                    v.filename,
                    v.duration,
                    v.created_at,
                    v.summary,
                    COUNT(h.id) as highlight_count
                FROM videos v
                LEFT JOIN highlights h ON v.id = h.video_id
                GROUP BY v.id, v.filename, v.duration, v.created_at, v.summary
                ORDER BY v.created_at DESC
            """))
            
            return [
                {
                    'id': row[0],
                    'filename': row[1],
                    'duration': row[2],
                    'created_at': row[3],
                    'summary': row[4],
                    'highlight_count': row[5]
                }
                for row in result
            ]

    def search_highlights_by_text(self, search_text: str, limit: int = 10) -> List[Highlight]:
        """Search highlights by text content."""
        with self.get_session() as session:
            return (
                session.query(Highlight)
                .filter(Highlight.description.ilike(f"%{search_text}%"))
                .options(joinedload(Highlight.video))
                .order_by(Highlight.timestamp)
                .limit(limit)
                .all()
            ) 