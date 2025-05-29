import os
from pathlib import Path
from typing import List, Optional, Tuple, Dict, Any
import logging
from datetime import datetime

from src.database import DatabaseManager, Video, Highlight
from src.processors.video_processor import VideoProcessor, FrameInfo
from src.processors.audio_processor import AudioProcessor
from src.llm.llm_service import LLMService, HighlightDescription


class HighlightService:
    """Service for extracting and managing video highlights."""

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
        Process a video file to extract and store highlights.
        
        Args:
            video_path: Path to the video file
            
        Returns:
            Video object representing the processed video
        """
        self.logger.info(f"Processing video: {video_path}")
        
        # Get video info
        duration, width, height, fps = self.video_processor.get_video_info(video_path)
        
        # Extract audio
        self.logger.info("Extracting audio...")
        audio_path = self.video_processor.extract_audio(video_path)
        
        # Transcribe the whole audio using Whisper
        self.logger.info("Transcribing entire audio with Whisper...")
        transcriptions = self.audio_processor.transcribe_audio(audio_path)
        
        # Prepare segments for highlights
        all_segments = []
        for start, end, text in transcriptions:
            if text.strip():
                all_segments.append({
                    'start_time': start,
                    'end_time': end,
                    'text': text.strip(),
                    'has_speech': True
                })
        
        # Detect scenes
        self.logger.info("Detecting scenes...")
        scenes = self.video_processor.detect_scenes(video_path)
        self.logger.info(f"Detected {len(scenes)} scenes.")
        
        # Process each segment to generate highlights
        highlights = []
        for segment in all_segments:
            self.logger.info(f"Processing segment from {segment['start_time']:.2f}s to {segment['end_time']:.2f}s")
            
            # Extract frames for this segment
            frames = [
                frame for frame in self.video_processor.extract_frames(video_path, max_frames=None)
                if segment['start_time'] <= frame.timestamp <= segment['end_time']
            ]
            
            if not frames:
                self.logger.warning(f"No frames extracted for segment {segment['start_time']:.2f}s – {segment['end_time']:.2f}s. Skipping.")
                continue
            
            # Find the most representative frame (middle of segment)
            segment_duration = segment['end_time'] - segment['start_time']
            target_time = segment['start_time'] + (segment_duration / 2)
            closest_frame = min(frames, key=lambda f: abs(f.timestamp - target_time))
            
            # Generate visual description
            frame_info = self.video_processor.prepare_frame_for_llm(closest_frame.frame)
            stats = frame_info['statistics']
            visual_desc = (
                f"Frame analysis shows brightness: {stats['brightness']:.1f}, "
                f"contrast: {stats['contrast']:.1f}, "
                f"edge density: {stats['edges']['edge_density']:.2f}. "
                f"The dominant colors are: " + 
                " and ".join([f"RGB({c['rgb'][0]},{c['rgb'][1]},{c['rgb'][2]}) at {c['percent']*100:.1f}%" 
                            for c in stats['dominant_colors'][:2]])
            )
            
            # Prepare audio context
            audio_context = f"Contains speech: \"{segment['text']}\""
            
            # Generate highlight description
            description_obj = self.llm_service.generate_highlight_description(
                visual_desc,
                audio_context,
                target_time
            )
            
            highlights.append(description_obj)
            self.logger.info(f"Added highlight at {target_time:.2f}s")
        
        # Generate overall summary
        overall_summary = self._generate_video_summary(highlights)
        
        # Store video in database
        video = Video(
            filename=os.path.basename(video_path),
            duration=duration,
            width=width,
            height=height,
            fps=fps,
            summary=overall_summary,
            created_at=datetime.now()
        )
        video = self.db.save_video(video)
        
        # Store highlights in database
        for highlight in highlights:
            # Generate embedding for the highlight description
            embedding = self.llm_service.generate_embedding(highlight.description)
            
            # Create and save the highlight
            db_highlight = Highlight(
                video_id=video.id,
                timestamp=highlight.timestamp,
                description=highlight.description,
                embedding=embedding,
                summary=highlight.summary,
                created_at=datetime.now()
            )
            self.db.save_highlight(db_highlight)
        
        return video

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

    def _generate_highlight_description(
        self,
        frame_info: Dict[str, Any],
        audio_text: str,
        timestamp: float
    ) -> str:
        """
        Generate a description for a highlight using the LLM.
        
        Args:
            frame_info: Visual analysis of the frame
            audio_text: Transcribed audio for this moment
            timestamp: Timestamp in seconds
            
        Returns:
            Generated description
        """
        # Prepare context for LLM
        stats = frame_info['statistics']
        visual_desc = (
            f"Frame analysis shows brightness: {stats['brightness']:.1f}, "
            f"contrast: {stats['contrast']:.1f}, "
            f"edge density: {stats['edges']['edge_density']:.2f}. "
            f"The dominant colors are: "
        )
        
        # Add color information
        colors = []
        for color in stats['dominant_colors'][:2]:  # Only use top 2 colors
            r, g, b = color['rgb']
            percent = color['percent'] * 100
            colors.append(f"RGB({r},{g},{b}) at {percent:.1f}%")
        visual_desc += " and ".join(colors)
        
        # Build full context
        context = f"At timestamp {timestamp:.1f}s, {visual_desc}"
        if audio_text:
            context += f". The audio contains: \"{audio_text}\""
        
        # Generate description
        description = self.llm_service.generate_text(
            f"Please describe this moment in the video: {context}"
        )
        
        return description

    def _generate_video_summary(self, highlights: List[Highlight]) -> str:
        """
        Generate an overall summary of the video based on its highlights.
        
        Args:
            highlights: List of highlights to summarize
            
        Returns:
            Generated summary
        """
        if not highlights:
            return "No significant highlights found in the video."
        
        # Prepare context
        context = "The video contains the following highlights:\n\n"
        for highlight in highlights:
            context += f"- At {highlight.timestamp:.1f}s: {highlight.description}\n"
        
        # Generate summary
        summary = self.llm_service.generate_text(
            f"Please provide a concise summary of this video based on its highlights: {context}"
        )
        
        return summary

    def _generate_embedding(self, text: str) -> List[float]:
        """
        Generate an embedding for text using the LLM.
        
        Args:
            text: Text to generate embedding for
            
        Returns:
            List of floats representing the embedding
        """
        return self.llm_service.generate_embedding(text) 