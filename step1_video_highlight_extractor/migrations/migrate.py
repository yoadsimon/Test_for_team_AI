"""Database migration script."""
import os
import sys
import logging
from pathlib import Path

# Add project root to Python path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Import all migrations using absolute imports
from migrations.initial import upgrade as initial_migration

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_migrations():
    """Run all database migrations."""
    # Get database connection info from environment
    host = os.getenv('POSTGRES_HOST', 'localhost')
    user = os.getenv('POSTGRES_USER', 'postgres')
    password = os.getenv('POSTGRES_PASSWORD', 'postgres')
    db = os.getenv('POSTGRES_DB', 'video_highlights')
    
    # Build database URL
    db_url = f"postgresql://{user}:{password}@{host}:5432/{db}"
    
    # Create engine
    engine = create_engine(db_url)
    
    # Run migrations in order
    migrations = [
        initial_migration,
    ]
    
    for migration in migrations:
        logger.info(f"Running migration: {migration.__name__}")
        migration(engine)
        logger.info("Migration completed successfully")

if __name__ == '__main__':
    run_migrations() 