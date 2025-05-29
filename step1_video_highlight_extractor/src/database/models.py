from datetime import datetime
from typing import List, Optional

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from pgvector.sqlalchemy import Vector
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for all database models."""
    pass


class Video(Base):
    """Model representing a processed video file."""
    __tablename__ = "videos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    duration: Mapped[float] = mapped_column(Float, nullable=False)
    width: Mapped[int] = mapped_column(Integer, nullable=False)
    height: Mapped[int] = mapped_column(Integer, nullable=False)
    fps: Mapped[float] = mapped_column(Float, nullable=False)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )

    # Relationship with highlights
    highlights: Mapped[List["Highlight"]] = relationship(
        "Highlight", back_populates="video", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Video(id={self.id}, filename='{self.filename}', duration={self.duration})>"


class Highlight(Base):
    """Model representing a highlight moment from a video."""
    __tablename__ = "highlights"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    video_id: Mapped[int] = mapped_column(Integer, ForeignKey("videos.id"), nullable=False)
    timestamp: Mapped[float] = mapped_column(Float, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[Optional[List[float]]] = mapped_column(Vector(768), nullable=True)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )

    # Relationship with video
    video: Mapped["Video"] = relationship("Video", back_populates="highlights")

    def __repr__(self) -> str:
        return f"<Highlight(id={self.id}, video_id={self.video_id}, timestamp={self.timestamp})>" 