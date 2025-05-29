#!/usr/bin/env python3
import logging
from pathlib import Path
import os
import glob

from src.database import DatabaseManager
from src.services.highlight_service import HighlightService
from src.processors.video_processor import VideoProcessor
from src.processors.audio_processor import AudioProcessor
from src.llm.llm_service import LLMService
from dotenv import load_dotenv

# Configure logging with more detailed format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_video_files():
    """Get video files based on environment."""
    video_dir = Path("videos")
    
    # Check if we're running in dev environment (docker-compose.dev.yml)
    is_dev = os.getenv('POSTGRES_DB') == 'video_highlights_test'
    
    if is_dev:
        # In dev environment, use the demo video
        demo_video = video_dir / "demo_v2.MOV"
        if not demo_video.exists():
            raise FileNotFoundError(f"Demo video not found: {demo_video}")
        return [demo_video]
    else:
        # In production, use all non-demo videos
        video_files = []
        for ext in ['*.mp4', '*.mov', '*.MOV', '*.MP4']:
            for video in video_dir.glob(ext):
                if 'demo' not in video.name.lower():
                    video_files.append(video)
        
        if not video_files:
            raise FileNotFoundError("No non-demo videos found in videos directory")
        return video_files

def main():
    """Main function to demonstrate video processing and highlight extraction."""
    logger.info("Initializing services...")
    
    # Initialize services
    db_manager = DatabaseManager()
    
    # Create database tables
    logger.info("Creating database tables...")
    db_manager.create_tables()
    
    video_processor = VideoProcessor()
    audio_processor = AudioProcessor()
    llm_service = LLMService()
    highlight_service = HighlightService(
        db_manager=db_manager,
        video_processor=video_processor,
        audio_processor=audio_processor,
        llm_service=llm_service
    )
    
    # Get video files based on environment
    try:
        video_files = get_video_files()
        logger.info(f"Found {len(video_files)} videos to process.")
        for video_file in video_files:
            logger.info(f"Processing: {video_file}")
    except FileNotFoundError as e:
        logger.error(str(e))
        return
    
    # Process each video
    for video_file in video_files:
        logger.info(f"Starting to process video: {video_file}")
        logger.info("Extracting scenes, transcripts, and generating highlights...")
        
        # Process video and get highlights
        video = highlight_service.process_video(str(video_file))
        
        # Retrieve and display highlights
        logger.info("Retrieving highlights from database...")
        highlights = highlight_service.get_video_highlights(video.id)
        
        logger.info(f"Successfully processed video. Found {len(highlights)} highlights.")
        
        # Display highlights
        logger.info(f"\nHighlights for video ID {video.id}:")
        logger.info("-" * 80)
        
        for highlight in highlights:
            logger.info(f"Timestamp: {highlight.timestamp:.2f}s")
            logger.info(f"Description: {highlight.description}")
            if highlight.summary:
                logger.info(f"Summary: {highlight.summary}\n")
            logger.info("-" * 80)

if __name__ == "__main__":
    main()
