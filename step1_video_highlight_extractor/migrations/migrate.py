"""Database migration script."""
import os
import sys
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add src directory to Python path
src_dir = str(Path(__file__).parent.parent)
if src_dir not in sys.path:
    sys.path.append(src_dir)

# Import all migrations
from .initial import upgrade as initial_migration

def run_migrations():
    """Run all database migrations."""
    # Get database connection info from environment
    host = os.getenv('POSTGRES_HOST', 'localhost')
    user = os.getenv('POSTGRES_USER', 'postgres')
    password = os.getenv('POSTGRES_PASSWORD', 'postgres')
    db = os.getenv('POSTGRES_DB', 'video_highlights_test')
    
    # Build database URL
    db_url = f"postgresql://{user}:{password}@{host}:5432/{db}"
    
    # Create engine
    engine = create_engine(db_url)
    
    # Run migrations in order
    migrations = [
        initial_migration,
    ]
    
    for migration in migrations:
        print(f"Running migration: {migration.__name__}")
        migration(engine)
        print("Migration completed successfully")

if __name__ == '__main__':
    run_migrations() 