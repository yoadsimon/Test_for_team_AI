"""Initial database schema."""
from datetime import datetime
from typing import List, Optional

from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from pgvector.sqlalchemy import Vector

# Import our models
from src.database.models import Base, Video, Highlight

def upgrade(migrate_engine):
    """Upgrade the database schema."""
    # Create all tables from our models
    Base.metadata.create_all(migrate_engine)

def downgrade(migrate_engine):
    """Downgrade the database schema."""
    Base.metadata.drop_all(migrate_engine) 