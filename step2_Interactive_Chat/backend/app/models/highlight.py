from datetime import datetime
from typing import List, Optional
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship, Mapped, mapped_column
from pgvector.sqlalchemy import Vector
from app.database.base_class import Base
from app.core.constants import EMBEDDING_DIM

class Video(Base):
    """Model representing a processed video file."""
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True)
    filename = Column(String(255), nullable=False)
    duration = Column(Float, nullable=False)
    width = Column(Integer, nullable=False)
    height = Column(Integer, nullable=False)
    fps = Column(Float, nullable=False)
    summary = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationship with highlights
    highlights = relationship("Highlight", back_populates="video", cascade="all, delete-orphan")

class Highlight(Base):
    """Model representing a highlight moment from a video."""
    __tablename__ = "highlights"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    video_id: Mapped[int] = mapped_column(Integer, ForeignKey("videos.id"), nullable=False)
    timestamp: Mapped[float] = mapped_column(Float, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[Optional[List[float]]] = mapped_column(Vector(EMBEDDING_DIM), nullable=True)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )

    # Relationship with video
    video: Mapped["Video"] = relationship("Video", back_populates="highlights")

    def __repr__(self) -> str:
        return f"<Highlight(id={self.id}, video_id={self.video_id}, timestamp={self.timestamp})>" 