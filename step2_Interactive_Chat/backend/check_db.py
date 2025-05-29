from sqlalchemy import create_engine
import os

db_uri = f'postgresql://{os.environ["POSTGRES_USER"]}:{os.environ["POSTGRES_PASSWORD"]}@{os.environ["POSTGRES_HOST"]}:{os.environ["POSTGRES_PORT"]}/{os.environ["POSTGRES_DB"]}'
engine = create_engine(db_uri)

with engine.connect() as conn:
    result = conn.execute('SELECT id, description, embedding IS NOT NULL as has_embedding FROM highlights').fetchall()
    print(f'Found {len(result)} highlights:')
    for row in result:
        print(row) 