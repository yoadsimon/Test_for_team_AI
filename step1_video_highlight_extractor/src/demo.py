#!/usr/bin/env python3
from pathlib import Path
import logging
import os
from typing import List
import time

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
    Main function to demonstrate streamlined video processing and intelligent highlight extraction.
    Processes videos with smart filtering and displays results.
    """
    logger.info("🚀 Starting Enhanced Video Highlight Extractor")
    logger.info("=" * 80)
    
    # Initialize services
    logger.info("📊 Initializing database...")
    db_manager = DatabaseManager()
    db_manager.ensure_tables_exist()  # Use safer method that preserves existing data
    logger.info("✅ Database ready")
    
    logger.info("🎥 Initializing simplified video processor...")
    video_processor = VideoProcessor()
    logger.info("✅ Video processor ready")
    
    logger.info("🎵 Initializing audio processor...")
    audio_processor = AudioProcessor()
    logger.info("✅ Audio processor ready")
    
    logger.info("🤖 Initializing enhanced LLM service with LangChain...")
    llm_service = LLMService()
    logger.info("✅ LLM service ready")
    
    logger.info("🔧 Creating streamlined highlight service...")
    highlight_service = HighlightService(
        db_manager=db_manager,
        video_processor=video_processor,
        audio_processor=audio_processor,
        llm_service=llm_service
    )
    logger.info("✅ All services initialized successfully!")
    logger.info("=" * 80)
    
    try:
        video_files = get_video_files()
        logger.info(f"🎬 Processing {len(video_files)} videos with smart filtering")
        
        total_highlights = 0
        start_time = time.time()
        
        for i, video_file in enumerate(video_files, 1):
            logger.info(f"\n🎯 Processing video {i}/{len(video_files)}: {video_file.name}")
            logger.info("-" * 60)
            
            video_start_time = time.time()
            
            try:
                # Process video with intelligent filtering
                video = highlight_service.process_video(str(video_file))
                highlights = highlight_service.get_video_highlights(video.id)
                
                video_duration = time.time() - video_start_time
                total_highlights += len(highlights)
                
                logger.info(f"✨ Video Processing Complete!")
                logger.info(f"📹 Video: {video.filename}")
                logger.info(f"⏱️  Duration: {video.duration:.1f}s")
                logger.info(f"🎯 Quality Highlights Found: {len(highlights)}")
                logger.info(f"⚡ Processing Time: {video_duration:.1f}s")
                
                if video.summary:
                    logger.info(f"📄 Summary: {video.summary}")
                
                if highlights:
                    logger.info(f"\n🎪 Top Highlights:")
                    # Show top 5 highlights
                    for j, highlight in enumerate(highlights[:5], 1):
                        logger.info(f"\n  {j}. ⏰ {highlight.format_timestamp()}")
                        logger.info(f"     📝 {highlight.description}")
                        if highlight.summary:
                            logger.info(f"     💡 {highlight.summary}")
                else:
                    logger.info("ℹ️  No highlights met the quality threshold for this video.")
                
                logger.info("-" * 60)
                
            except Exception as e:
                logger.error(f"❌ Failed to process {video_file.name}: {e}")
                continue
        
        # Final summary
        total_time = time.time() - start_time
        logger.info(f"\n" + "=" * 80)
        logger.info(f"🎉 PROCESSING COMPLETE!")
        logger.info(f"📊 Statistics:")
        logger.info(f"   • Videos Processed: {len(video_files)}")
        logger.info(f"   • Total Quality Highlights: {total_highlights}")
        logger.info(f"   • Average Highlights per Video: {total_highlights/len(video_files):.1f}")
        logger.info(f"   • Total Processing Time: {total_time:.1f}s")
        logger.info(f"   • Average Time per Video: {total_time/len(video_files):.1f}s")
        logger.info("=" * 80)
        
        # Show database summary
        try:
            videos_summary = db_manager.get_videos_summary()
            if videos_summary:
                logger.info(f"\n📚 Database Summary:")
                for video_info in videos_summary[:5]:  # Show last 5 videos
                    logger.info(
                        f"   • {video_info['filename']}: "
                        f"{video_info['highlight_count']} highlights "
                        f"({video_info['duration']:.1f}s)"
                    )
        except Exception as e:
            logger.warning(f"Could not get database summary: {e}")
                
    except FileNotFoundError as e:
        logger.error(f"📁 Video file error: {e}")
        logger.info("💡 Tip: Add video files (MP4/MOV) to the 'videos' directory")
    except Exception as e:
        logger.error(f"💥 Processing error: {e}", exc_info=True)

if __name__ == "__main__":
    main()
