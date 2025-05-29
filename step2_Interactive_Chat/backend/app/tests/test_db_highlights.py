import os
from dotenv import load_dotenv
from app.database.session import SessionLocal
from app.models.highlight import Highlight

def test_db_highlights():
    """Test (or print) highlights stored in the DB."""
    load_dotenv()
    db = SessionLocal()
    try:
        highlights = db.query(Highlight).all()
        print("\nDB Highlights Test:")
        print("-" * 50)
        if not highlights:
            print("No highlights found in the DB.")
        else:
            print(f"Found {len(highlights)} highlights:")
            for h in highlights:
                print(f"Highlight (id: {h.id}):\n\tSummary: {h.summary}\n\tDescription: {h.description}\n\tTimestamp: {h.timestamp}\n")
    finally:
        db.close()

if __name__ == "__main__":
    test_db_highlights() 