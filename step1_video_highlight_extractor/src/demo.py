#!/usr/bin/env python3
from pathlib import Path
import logging
import os
from typing import List

from src.database import DatabaseManager
from src.services.highlight_service import HighlightService
from src.processors.video_processor import VideoProcessor
from src.processors.audio_processor import AudioProcessor
from src.llm.llm_service import LLMService
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_video_files() -> List[Path]:
    """
    Get all video files from the videos directory.
    
    Returns:
        List[Path]: List of video file paths to process
        
    Raises:
        FileNotFoundError: If no videos are found
    """
    video_dir = Path("videos")
    video_files = []
    
    for ext in ['*.mp4', '*.mov', '*.MOV', '*.MP4']:
        video_files.extend(video_dir.glob(ext))
    
    if not video_files:
        raise FileNotFoundError("No videos found in videos directory")
    
    logger.info(f"Found {len(video_files)} videos: {[v.name for v in video_files]}")
    return video_files

def main() -> None:
    """
    Main function to demonstrate video processing and highlight extraction.
    Processes videos, extracts highlights, and displays results.
    """
    logger.info("Initializing services...")
    
    # Initialize services
    logger.info("📊 Initializing database...")
    db_manager = DatabaseManager()
    db_manager.create_tables()
    logger.info("✅ Database ready")
    
    logger.info("🎥 Initializing video processor...")
    video_processor = VideoProcessor()
    logger.info("✅ Video processor ready")
    
    logger.info("🎵 Initializing audio processor...")
    audio_processor = AudioProcessor()
    logger.info("✅ Audio processor ready")
    
    logger.info("🤖 Initializing LLM service (this may take a moment)...")
    llm_service = LLMService()
    logger.info("✅ LLM service ready")
    
    logger.info("🔧 Creating highlight service...")
    highlight_service = HighlightService(
        db_manager=db_manager,
        video_processor=video_processor,
        audio_processor=audio_processor,
        llm_service=llm_service
    )
    logger.info("✅ All services initialized successfully!")
    
    try:
        video_files = get_video_files()
        logger.info(f"Found {len(video_files)} videos to process")
        
        for video_file in video_files:
            logger.info(f"Processing video: {video_file}")
            video = highlight_service.process_video(str(video_file))
            highlights = highlight_service.get_video_highlights(video.id)
            
            logger.info(f"Found {len(highlights)} highlights for video ID {video.id}")
            logger.info("-" * 80)
            
            for highlight in highlights:
                logger.info(f"Timestamp: {highlight.timestamp:.2f}s")
                logger.info(f"Description: {highlight.description}")
                if highlight.summary:
                    logger.info(f"Summary: {highlight.summary}\n")
                logger.info("-" * 80)
                
    except FileNotFoundError as e:
        logger.error(f"Video file error: {e}")
    except Exception as e:
        logger.error(f"Processing error: {e}", exc_info=True)

if __name__ == "__main__":
    main()
