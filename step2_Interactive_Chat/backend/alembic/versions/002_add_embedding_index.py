"""add embedding index

Revision ID: 002
Revises: 001
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Create an IVF-Flat index for cosine similarity search
    op.execute('CREATE INDEX IF NOT EXISTS highlights_embedding_idx ON highlights USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100)')

def downgrade() -> None:
    # Drop the index
    op.execute('DROP INDEX IF EXISTS highlights_embedding_idx') 