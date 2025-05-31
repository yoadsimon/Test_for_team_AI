import os
from pathlib import Path
from typing import List, Optional, Tuple, Dict, Any
import logging
from datetime import datetime
import concurrent.futures

from src.database import DatabaseManager, Video, Highlight
from src.processors.video_processor import VideoProcessor, FrameInfo
from src.processors.audio_processor import AudioProcessor
from src.llm.llm_service import LLMService, HighlightDescription


class HighlightService:
    """Streamlined service for extracting and managing video highlights with smart filtering."""

    def __init__(
        self,
        db_manager: DatabaseManager,
        video_processor: Optional[VideoProcessor] = None,
        audio_processor: Optional[AudioProcessor] = None,
        llm_service: Optional[LLMService] = None
    ):
        """
        Initialize the highlight service.
        
        Args:
            db_manager: Database manager instance
            video_processor: Optional video processor instance
            audio_processor: Optional audio processor instance
            llm_service: Optional LLM service instance
        """
        self.db = db_manager
        self.video_processor = video_processor or VideoProcessor()
        self.audio_processor = audio_processor or AudioProcessor()
        self.llm_service = llm_service or LLMService()
        
        # Configure logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def process_video(self, video_path: str) -> Video:
        """
        Process a video file to extract and store highlights using smart filtering.
        
        Args:
            video_path: Path to the video file
            
        Returns:
            Video object representing the processed video
        """
        self.logger.info(f"🎬 Processing video: {video_path}")
        
        try:
            # Get video info
            duration, width, height, fps = self.video_processor.get_video_info(video_path)
            
            # Create and save the video entry
            video = Video(
                filename=os.path.basename(video_path),
                duration=duration,
                width=width,
                height=height,
                fps=fps,
                created_at=datetime.now()
            )
            video = self.db.save_video(video)
            self.logger.info(f"📝 Created video record with ID {video.id}")
            
            # Add context to LLM for better understanding
            video_context = f"Video: {video.filename}, Duration: {duration:.1f}s"
            
            # Extract and transcribe audio
            self.logger.info("🎵 Extracting and transcribing audio...")
            audio_path = self.video_processor.extract_audio(video_path)
            transcriptions = self.audio_processor.transcribe_audio(audio_path)
            
            # Filter for meaningful speech segments
            meaningful_segments = self._filter_meaningful_segments(transcriptions)
            self.logger.info(f"🔍 Found {len(meaningful_segments)} meaningful segments from {len(transcriptions)} total")
            
            if not meaningful_segments:
                self.logger.warning("No meaningful segments found. Creating minimal summary.")
                video.summary = "No significant dialogue or content detected in this video."
                return self.db.save_video(video)
            
            # Process segments with smart filtering
            highlights = self._process_segments_with_smart_filtering(
                meaningful_segments, 
                video_context
            )
            
            if not highlights:
                self.logger.warning("No highlights generated after smart filtering.")
                video.summary = "Video processed but no significant highlights identified."
                return self.db.save_video(video)
            
            # Generate overall summary
            overall_summary = self.llm_service.generate_highlight_summary(highlights)
            video.summary = overall_summary
            video = self.db.save_video(video)
            self.logger.info(f"📊 Generated video summary: {overall_summary[:100]}...")
            
            # Batch save highlights to database
            self._batch_save_highlights(highlights, video.id)
            
            # Clean up
            if os.path.exists(audio_path):
                os.remove(audio_path)
            
            self.logger.info(f"✅ Successfully processed video with {len(highlights)} highlights")
            return video
            
        except Exception as e:
            self.logger.error(f"❌ Error processing video {video_path}: {e}", exc_info=True)
            # Try to save partial progress
            if 'video' in locals():
                video.summary = f"Processing failed: {str(e)}"
                self.db.save_video(video)
            raise

    def _filter_meaningful_segments(
        self, transcriptions: List[Tuple[float, float, str]]
    ) -> List[Dict[str, Any]]:
        """
        Filter transcription segments to keep only meaningful content.
        
        Args:
            transcriptions: List of (start_time, end_time, text) tuples
            
        Returns:
            List of meaningful segments with metadata
        """
        meaningful_segments = []
        
        for start, end, text in transcriptions:
            text = text.strip()
            
            # Skip very short or empty segments
            if not text or len(text) < 10:
                continue
            
            # Skip segments that are too short (less than 2 seconds)
            if (end - start) < 2.0:
                continue
            
            # Basic filtering for filler words and noise
            text_lower = text.lower()
            filler_words = ['uh', 'um', 'hmm', 'ah', 'eh', 'like', 'you know']
            
            # If the segment is mostly filler words, skip it
            words = text_lower.split()
            if len(words) > 0:
                filler_ratio = sum(1 for word in words if word in filler_words) / len(words)
                if filler_ratio > 0.7:  # More than 70% filler words
                    continue
            
            meaningful_segments.append({
                'start_time': start,
                'end_time': end,
                'text': text,
                'duration': end - start,
                'word_count': len(words)
            })
        
        return meaningful_segments

    def _process_segments_with_smart_filtering(
        self, 
        segments: List[Dict[str, Any]], 
        video_context: str
    ) -> List[HighlightDescription]:
        """
        Process segments using LLM smart filtering to generate only quality highlights.
        
        Args:
            segments: List of meaningful segments
            video_context: Context for the video
            
        Returns:
            List of quality highlights
        """
        self.logger.info(f"🤖 Processing {len(segments)} segments with AI filtering...")
        
        def process_segment(segment: Dict[str, Any]) -> Optional[HighlightDescription]:
            """Process a single segment and return highlight if significant."""
            try:
                # Calculate target timestamp (middle of segment)
                target_time = segment['start_time'] + (segment['duration'] / 2)
                
                # Use LLM to determine if this should be a highlight
                highlight = self.llm_service.generate_highlight_description(
                    audio_context=segment['text'],
                    timestamp=target_time,
                    video_context=video_context
                )
                
                return highlight  # Will be None if not significant enough
                
            except Exception as e:
                self.logger.error(f"Error processing segment at {segment['start_time']:.2f}s: {e}")
                return None

        # Process segments in parallel with progress tracking
        highlights = []
        total_segments = len(segments)
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            # Submit all tasks
            futures = {
                executor.submit(process_segment, segment): i 
                for i, segment in enumerate(segments)
            }
            
            completed_count = 0
            for future in concurrent.futures.as_completed(futures):
                completed_count += 1
                try:
                    result = future.result()
                    if result is not None:
                        highlights.append(result)
                    
                    if completed_count % 10 == 0 or completed_count == total_segments:
                        self.logger.info(
                            f"📈 Progress: {completed_count}/{total_segments} segments processed "
                            f"({completed_count/total_segments*100:.1f}%) - "
                            f"{len(highlights)} highlights found"
                        )
                except Exception as e:
                    self.logger.error(f"Segment processing failed: {e}")
        
        # Sort highlights by timestamp
        highlights.sort(key=lambda h: h.timestamp)
        
        self.logger.info(f"✨ Generated {len(highlights)} quality highlights from {total_segments} segments")
        return highlights

    def _batch_save_highlights(self, highlights: List[HighlightDescription], video_id: int):
        """
        Save highlights to database in batches for better performance.
        
        Args:
            highlights: List of highlights to save
            video_id: ID of the video
        """
        if not highlights:
            return
        
        self.logger.info(f"💾 Batch saving {len(highlights)} highlights...")
        
        try:
            # Generate embeddings in batch for better performance
            descriptions = [h.description for h in highlights]
            embeddings = self.llm_service.batch_generate_embeddings(descriptions)
            
            # Create highlight objects
            db_highlights = []
            for i, (highlight, embedding) in enumerate(zip(highlights, embeddings)):
                db_highlight = Highlight(
                    video_id=video_id,
                    timestamp=highlight.timestamp,
                    description=highlight.description,
                    embedding=embedding,
                    summary=highlight.summary,
                    created_at=datetime.now()
                )
                db_highlights.append(db_highlight)
            
            # Batch save to database
            saved_highlights = self.db.batch_save_highlights(db_highlights)
            self.logger.info(f"✅ Successfully saved {len(saved_highlights)} highlights to database")
            
        except Exception as e:
            self.logger.error(f"❌ Error batch saving highlights: {e}", exc_info=True)
            # Fallback to individual saves
            self.logger.info("🔄 Falling back to individual saves...")
            self._individual_save_highlights(highlights, video_id)

    def _individual_save_highlights(self, highlights: List[HighlightDescription], video_id: int):
        """
        Fallback method to save highlights individually.
        
        Args:
            highlights: List of highlights to save
            video_id: ID of the video
        """
        saved_count = 0
        for i, highlight in enumerate(highlights):
            try:
                # Generate embedding
                embedding = self.llm_service.generate_embedding(highlight.description)
                
                # Create and save highlight
                db_highlight = Highlight(
                    video_id=video_id,
                    timestamp=highlight.timestamp,
                    description=highlight.description,
                    embedding=embedding,
                    summary=highlight.summary,
                    created_at=datetime.now()
                )
                self.db.save_highlight(db_highlight)
                saved_count += 1
                
            except Exception as e:
                self.logger.error(f"Failed to save highlight {i+1}: {e}")
                continue
        
        self.logger.info(f"✅ Individually saved {saved_count}/{len(highlights)} highlights")

    def get_video_highlights(
        self, video_id: int, limit: Optional[int] = None
    ) -> List[Highlight]:
        """
        Get highlights for a video.
        
        Args:
            video_id: ID of the video
            limit: Optional limit on number of highlights
            
        Returns:
            List of highlights
        """
        highlights = self.db.get_video_highlights(video_id)
        if limit:
            highlights = highlights[:limit]
        return highlights

    def find_similar_highlights(
        self, video_id: int, highlight_id: int, limit: int = 5
    ) -> List[Highlight]:
        """
        Find highlights similar to a given highlight.
        
        Args:
            video_id: ID of the video
            highlight_id: ID of the highlight to compare against
            limit: Maximum number of similar highlights to return
            
        Returns:
            List of similar highlights
        """
        # Get the reference highlight
        highlights = self.db.get_video_highlights(video_id)
        reference = next((h for h in highlights if h.id == highlight_id), None)
        
        if not reference or not reference.embedding:
            return []
        
        # Find similar highlights
        return self.db.find_similar_highlights(
            embedding=reference.embedding,
            limit=limit
        ) 