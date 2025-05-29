from datetime import datetime, timedelta
from sentence_transformers import SentenceTransformer
from app.database.session import SessionLocal
from app.models.highlight import Highlight
from app.core.config import settings

def init_db():
    db = SessionLocal()
    model = SentenceTransformer(settings.EMBEDDING_MODEL)
    
    # Sample highlights
    highlights = [
        "A person gets out of a car and walks towards the building",
        "The person enters the building through the main entrance",
        "Inside the building, they take the elevator to the 3rd floor",
        "They walk down the hallway and enter an office",
        "The person sits at a desk and starts working on a computer",
        "After an hour, they get up and go to the break room",
        "In the break room, they make coffee and chat with colleagues",
        "They return to their office and continue working",
        "Later, they attend a meeting in the conference room",
        "After the meeting, they pack up and leave the office"
    ]
    
    try:
        # Check if we already have data
        if db.query(Highlight).first() is not None:
            print("Database already has data, skipping initialization")
            return

        # Create highlights with timestamps and embeddings
        base_time = datetime.utcnow() - timedelta(hours=1)
        for i, text in enumerate(highlights):
            timestamp = base_time + timedelta(minutes=i * 10)
            embedding = model.encode(text)
            
            highlight = Highlight(
                video_id=1,  # Assuming video_id 1 exists
                timestamp=timestamp.timestamp(),
                description=text,
                embedding=embedding.tolist(),
                summary=f"Summary of highlight at {timestamp.strftime('%H:%M:%S')}"
            )
            db.add(highlight)
        
        db.commit()
        print("Successfully initialized database with sample highlights")
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_db() 