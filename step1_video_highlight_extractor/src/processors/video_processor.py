import cv2
import numpy as np
from pathlib import Path
from typing import Generator, List, Tuple, Optional, Dict, Any
from dataclasses import dataclass
from moviepy.editor import VideoFileClip
import tempfile
import os
import logging

logger = logging.getLogger(__name__)


@dataclass
class FrameInfo:
    """Information about a video frame."""
    frame_number: int
    timestamp: float
    frame: np.ndarray
    is_key_frame: bool = False


class VideoProcessor:
    """Video processor focusing on essential functionality."""

    def __init__(self, min_frame_interval: float = 1.0):
        self.min_frame_interval = min_frame_interval
        
        self.output_dir = Path("processed_media")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def get_video_info(self, video_path: str) -> Tuple[float, int, int, float]:
        """Extract basic video information."""
        video = cv2.VideoCapture(video_path)
        if not video.isOpened():
            raise ValueError(f"Could not open video file: {video_path}")
        
        try:
            width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = video.get(cv2.CAP_PROP_FPS)
            frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = frame_count / fps if fps > 0 else 0
            
            return duration, width, height, fps
        finally:
            video.release()

    def extract_frames(
        self, video_path: str, max_frames: Optional[int] = None
    ) -> Generator[FrameInfo, None, None]:
        """Extract frames from a video file at regular intervals."""
        video = cv2.VideoCapture(video_path)
        if not video.isOpened():
            raise ValueError(f"Could not open video file: {video_path}")
        
        try:
            fps = video.get(cv2.CAP_PROP_FPS)
            frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
            
            frame_interval = max(1, int(fps * self.min_frame_interval))
            
            frame_number = 0
            frames_extracted = 0
            
            while True:
                ret, frame = video.read()
                if not ret:
                    break
                
                if frame_number % frame_interval == 0:
                    timestamp = frame_number / fps
                    
                    yield FrameInfo(
                        frame_number=frame_number,
                        timestamp=timestamp,
                        frame=frame.copy(),
                        is_key_frame=False
                    )
                    
                    frames_extracted += 1
                    if max_frames and frames_extracted >= max_frames:
                        break
                
                frame_number += 1
                
        finally:
            video.release()

    def extract_audio(self, video_path: str, output_path: Optional[str] = None) -> str:
        """Extract audio from a video file."""
        if output_path is None:
            temp_fd, output_path = tempfile.mkstemp(suffix='.wav')
            os.close(temp_fd)
        
        try:
            video = VideoFileClip(video_path)
            video.audio.write_audiofile(output_path, verbose=False, logger=None)
            video.close()
            return output_path
        except Exception as e:
            logger.error(f"Error extracting audio: {e}")
            raise

    def get_frame_at_timestamp(self, video_path: str, timestamp: float) -> Optional[np.ndarray]:
        """Extract a single frame at a specific timestamp."""
        video = cv2.VideoCapture(video_path)
        if not video.isOpened():
            return None
        
        try:
            fps = video.get(cv2.CAP_PROP_FPS)
            frame_number = int(timestamp * fps)
            
            video.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            ret, frame = video.read()
            
            return frame if ret else None
        finally:
            video.release()

    def format_timestamp(self, seconds: float) -> str:
        """Format seconds into a human-readable timestamp."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:05.2f}" 