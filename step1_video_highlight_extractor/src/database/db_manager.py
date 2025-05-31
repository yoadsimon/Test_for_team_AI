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

    def _get_database_url(self) -> str:
        """Get the database URL from environment variables."""
        host = os.getenv("POSTGRES_HOST", "localhost")
        port = os.getenv("POSTGRES_PORT", "5432")
        user = os.getenv("POSTGRES_USER", "postgres")
        password = os.getenv("POSTGRES_PASSWORD", "postgres")
        db_name = os.getenv("POSTGRES_DB", "video_highlights")

        return f"postgresql://{user}:{password}@{host}:{port}/{db_name}"

    def ensure_tables_exist(self) -> None:
        """
        Ensure database tables exist without dropping existing data.
        This is safer than create_tables() as it preserves existing data.
        """
        try:
            # Check if tables exist
            with self.get_session() as session:
                try:
                    # Try to query the highlights table to see if it exists and has data
                    result = session.execute(text("SELECT COUNT(*) FROM highlights"))
                    count = result.scalar()
                    print(f"✅ Database ready with {count} existing highlights")
                    return
                except Exception:
                    # Table doesn't exist or other error, proceed with creation
                    print("ℹ️  Tables don't exist, creating them...")
                    pass
            
            # Create extension in a separate transaction if needed
            print("🔧 Ensuring pgvector extension...")
            try:
                with self.get_session() as session:
                    session.execute(text('CREATE EXTENSION IF NOT EXISTS vector;'))
                    session.commit()
                print("✅ pgvector extension ready")
            except Exception as e:
                print(f"ℹ️  pgvector extension might already exist: {e}")
                
            # Create tables if they don't exist
            print("🏗️ Creating tables if needed...")
            Base.metadata.create_all(bind=self.engine)
            print("✅ Tables ready")
            
        except Exception as e:
            print(f"❌ Database error: {e}")
            raise

    def create_tables(self) -> None:
        """Create database tables with proper transaction handling."""
        try:
            with self.get_session() as session:
                print("🗑️ Dropping existing tables...")
                try:
                    # Try to terminate idle connections first  
                    session.execute(text("""
                        SELECT pg_terminate_backend(pid) 
                        FROM pg_stat_activity 
                        WHERE datname = 'video_highlights' 
                        AND pid <> pg_backend_pid()
                        AND state = 'idle'
                    """))
                    session.commit()
                    print("✅ Terminated idle connections")
                except Exception as e:
                    print(f"ℹ️  Could not terminate connections: {e}")
                    session.rollback()  # Rollback failed transaction
                
                Base.metadata.drop_all(bind=self.engine)
                print("✅ Tables dropped")
                
            # Create extension in a separate transaction
            print("🔧 Creating pgvector extension...")
            try:
                with self.get_session() as session:
                    session.execute(text('CREATE EXTENSION IF NOT EXISTS vector;'))
                    session.commit()
                print("✅ pgvector extension ready")
            except Exception as e:
                print(f"ℹ️  pgvector extension might already exist: {e}")
                
            # Create tables in another separate transaction  
            print("🏗️ Creating new tables...")
            Base.metadata.create_all(bind=self.engine)
            print("✅ Tables created successfully")
            
        except Exception as e:
            print(f"❌ Database error: {e}")
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

    def batch_save_highlights(self, highlights: List[Highlight]) -> List[Highlight]:
        """
        Save multiple highlights to the database in a single transaction for better performance.
        
        Args:
            highlights: List of Highlight objects to save
            
        Returns:
            List of saved highlights with IDs populated
        """
        if not highlights:
            return []
        
        with self.get_session() as session:
            try:
                # Add all highlights to the session
                session.add_all(highlights)
                session.commit()
                
                # Refresh all objects to get their IDs
                for highlight in highlights:
                    session.refresh(highlight)
                
                return highlights
                
            except Exception as e:
                session.rollback()
                raise e

    def get_videos_summary(self) -> List[dict]:
        """
        Get a summary of all videos with highlight counts.
        
        Returns:
            List of dictionaries with video info and highlight counts
        """
        with self.get_session() as session:
            # Use raw SQL for efficient counting
            result = session.execute(text("""
                SELECT 
                    v.id,
                    v.filename,
                    v.duration,
                    v.summary,
                    v.created_at,
                    COUNT(h.id) as highlight_count
                FROM videos v
                LEFT JOIN highlights h ON v.id = h.video_id
                GROUP BY v.id, v.filename, v.duration, v.summary, v.created_at
                ORDER BY v.created_at DESC
            """))
            
            return [
                {
                    "id": row[0],
                    "filename": row[1],
                    "duration": row[2],
                    "summary": row[3],
                    "created_at": row[4],
                    "highlight_count": row[5]
                }
                for row in result
            ]

    def search_highlights_by_text(self, search_text: str, limit: int = 10) -> List[Highlight]:
        """
        Search highlights by text content (simple text search).
        
        Args:
            search_text: Text to search for
            limit: Maximum number of results
            
        Returns:
            List of matching highlights
        """
        with self.get_session() as session:
            return (
                session.query(Highlight)
                .filter(
                    Highlight.description.ilike(f"%{search_text}%") |
                    Highlight.summary.ilike(f"%{search_text}%")
                )
                .options(joinedload(Highlight.video))
                .order_by(Highlight.timestamp)
                .limit(limit)
                .all()
            ) 