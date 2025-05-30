import cv2
import numpy as np
from pathlib import Path
from typing import Generator, List, Tuple, Optional, Dict, Any
from dataclasses import dataclass
from moviepy.editor import VideoFileClip
from datetime import timedelta
import scenedetect
from scenedetect import detect, ContentDetector, split_video_ffmpeg
from faster_whisper import WhisperModel
from ultralytics import YOLO
import json
import os
import logging
from sklearn.cluster import KMeans

logger = logging.getLogger(__name__)


@dataclass
class SceneInfo:
    """Information about a detected scene in the video."""
    start_frame: int
    end_frame: int
    start_time: float
    end_time: float
    description: Optional[str] = None
    objects_detected: List[str] = None
    confidence: float = 0.0
    transcript: Optional[str] = None
    key_frame_path: Optional[str] = None


@dataclass
class FrameInfo:
    """Information about a video frame."""
    frame_number: int
    timestamp: float
    frame: np.ndarray
    is_key_frame: bool = False
    scene_id: Optional[int] = None
    objects_detected: List[str] = None


class VideoProcessor:
    """Handles video processing including frame extraction and analysis."""

    def __init__(
        self,
        min_frame_interval: float = 1.0,
        scene_threshold: float = 30.0,
        min_scene_duration: float = 1.0,
        model_size: str = "base"
    ):
        """
        Initialize the video processor.
        
        Args:
            min_frame_interval: Minimum time interval between frames in seconds
            scene_threshold: Threshold for scene detection
            min_scene_duration: Minimum duration of a scene in seconds
            model_size: Size of the Whisper model to use (tiny, base, small, medium, large)
        """
        self.min_frame_interval = min_frame_interval
        self.scene_threshold = scene_threshold
        self.min_scene_duration = min_scene_duration
        
        # Initialize models
        self.whisper_model = WhisperModel(model_size, device="cpu", compute_type="int8")
        self.yolo_model = YOLO("yolov8n.pt")  # Use nano model for speed
        
        # Create output directories
        self.output_dir = Path("processed_media")
        self.frames_dir = self.output_dir / "frames"
        self.scenes_dir = self.output_dir / "scenes"
        for dir_path in [self.output_dir, self.frames_dir, self.scenes_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)

        self._prev_frame = None  # Initialize previous frame for motion detection

    def process_video(self, video_path: str) -> List[Dict[str, Any]]:
        """
        Process a video file to extract scenes, transcripts, and visual information.
        Returns a list of scene dictionaries.
        """
        # Reset previous frame
        self._prev_frame = None
        
        scenes = self.detect_scenes(video_path)
        if not scenes:
            # Fallback: treat the whole video as one scene
            video = cv2.VideoCapture(video_path)
            fps = video.get(cv2.CAP_PROP_FPS)
            total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = total_frames / fps if fps else 0
            video.release()
            scenes = [
                SceneInfo(
                    start_frame=0,
                    end_frame=total_frames-1,
                    start_time=0.0,
                    end_time=duration,
                    objects_detected=[],
                    confidence=1.0
                )
            ]
        
        # Extract audio and transcribe
        audio_path = self.extract_audio(video_path)
        transcript_segments = self.transcribe_audio(audio_path)
        
        # Process each scene
        scene_data = []
        for i, scene in enumerate(scenes):
            # Extract key frame
            key_frame_path = self._extract_key_frame(video_path, scene)
            
            # Get transcript for this scene
            scene_transcript = self._get_scene_transcript(
                transcript_segments,
                scene.start_time,
                scene.end_time
            )
            
            # Only include scenes with either significant visual content or speech
            if scene_transcript.strip() or self._is_significant_frame(key_frame_path):
                # Detect objects in key frame
                objects = self._detect_objects(key_frame_path)
                
                # Create scene data
                scene_info = {
                    "timestamp": f"{self.format_timestamp(scene.start_time)} - {self.format_timestamp(scene.end_time)}",
                    "transcript": scene_transcript,
                    "visual_info": objects,
                    "key_frame": str(key_frame_path),
                    "duration": scene.end_time - scene.start_time
                }
                scene_data.append(scene_info)
            
        # Save scene info to JSON
        for i, scene in enumerate(scene_data):
            scene_file = self.scenes_dir / f"scene_{i:03d}.json"
            with open(scene_file, "w") as f:
                json.dump(scene, f, indent=2)
        
        # Clean up
        if os.path.exists(audio_path):
            os.remove(audio_path)
        
        return scene_data

    def detect_scenes(self, video_path: str) -> List[SceneInfo]:
        """
        Detect scenes in the video using PySceneDetect.
        
        Args:
            video_path: Path to the video file
            
        Returns:
            List of SceneInfo objects describing detected scenes
        """
        try:
            # Detect scenes with more sensitive threshold for better segmentation
            scene_list = detect(
                video_path,
                ContentDetector(
                    threshold=27.0,  # More sensitive threshold
                    min_scene_len=30  # Minimum scene length in frames (1 second at 30fps)
                )
            )
            
            # If no scenes detected, create a single scene for the whole video
            if not scene_list:
                video = cv2.VideoCapture(video_path)
                fps = video.get(cv2.CAP_PROP_FPS)
                total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
                duration = total_frames / fps if fps else 0
                video.release()
                
                return [
                    SceneInfo(
                        start_frame=0,
                        end_frame=total_frames-1,
                        start_time=0.0,
                        end_time=duration,
                        objects_detected=[],
                        confidence=1.0
                    )
                ]
            
            # Convert to SceneInfo objects
            scenes = []
            for i, scene in enumerate(scene_list):
                start_frame = scene[0].frame_num
                end_frame = scene[1].frame_num - 1
                
                # Get frame rate
                video = cv2.VideoCapture(video_path)
                fps = video.get(cv2.CAP_PROP_FPS)
                video.release()
                
                start_time = start_frame / fps
                end_time = end_frame / fps
                
                # Only include scenes that are long enough to be meaningful
                if end_time - start_time >= self.min_scene_duration:
                    scenes.append(SceneInfo(
                        start_frame=start_frame,
                        end_frame=end_frame,
                        start_time=start_time,
                        end_time=end_time,
                        objects_detected=[],
                        confidence=1.0
                    ))
            
            return scenes
            
        except Exception as e:
            logger.error(f"Error detecting scenes: {e}")
            # Fallback: treat the whole video as one scene
            video = cv2.VideoCapture(video_path)
            fps = video.get(cv2.CAP_PROP_FPS)
            total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = total_frames / fps if fps else 0
            video.release()
            
            return [
                SceneInfo(
                    start_frame=0,
                    end_frame=total_frames-1,
                    start_time=0.0,
                    end_time=duration,
                    objects_detected=[],
                    confidence=1.0
                )
            ]

    def transcribe_audio(self, audio_path: str) -> List[Dict[str, Any]]:
        """
        Transcribe audio using Whisper.
        
        Args:
            audio_path: Path to the audio file
            
        Returns:
            List of transcript segments with timestamps
        """
        segments, _ = self.whisper_model.transcribe(
            audio_path,
            word_timestamps=True
        )
        
        return [
            {
                "start": segment.start,
                "end": segment.end,
                "text": segment.text
            }
            for segment in segments
        ]

    def _extract_key_frame(self, video_path: str, scene: SceneInfo) -> Path:
        """Extract a key frame from the middle of the scene."""
        video = cv2.VideoCapture(video_path)
        fps = video.get(cv2.CAP_PROP_FPS)
        
        # Calculate middle frame
        middle_frame = (scene.start_frame + scene.end_frame) // 2
        video.set(cv2.CAP_PROP_POS_FRAMES, middle_frame)
        
        ret, frame = video.read()
        video.release()
        
        if not ret:
            raise ValueError(f"Could not extract frame at position {middle_frame}")
        
        # Save frame
        frame_path = self.frames_dir / f"scene_{scene.start_frame:06d}.jpg"
        cv2.imwrite(str(frame_path), frame)
        
        return frame_path

    def _detect_objects(self, frame_path: str) -> List[str]:
        """Detect objects in a frame using YOLOv8."""
        results = self.yolo_model(frame_path)
        
        # Get unique object classes
        objects = set()
        for result in results:
            for box in result.boxes:
                class_id = int(box.cls[0])
                objects.add(result.names[class_id])
        
        return sorted(list(objects))

    def _get_scene_transcript(
        self,
        transcript_segments: List[Dict[str, Any]],
        start_time: float,
        end_time: float
    ) -> str:
        """Get transcript text for a specific scene."""
        relevant_segments = [
            seg["text"]
            for seg in transcript_segments
            if start_time <= seg["start"] <= end_time or
               start_time <= seg["end"] <= end_time
        ]
        return " ".join(relevant_segments)

    def get_video_info(self, video_path: str) -> Tuple[float, int, int, float]:
        """
        Get basic information about a video file.
        
        Args:
            video_path: Path to the video file
            
        Returns:
            Tuple of (duration, width, height, fps)
        """
        video = cv2.VideoCapture(video_path)
        if not video.isOpened():
            raise ValueError(f"Could not open video file: {video_path}")
        
        try:
            fps = video.get(cv2.CAP_PROP_FPS)
            frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
            duration = frame_count / fps if fps > 0 else 0
            
            return duration, width, height, fps
        finally:
            video.release()

    def extract_frames(
        self, video_path: str, max_frames: Optional[int] = None
    ) -> Generator[FrameInfo, None, None]:
        """
        Extract frames from a video file at regular intervals.
        
        Args:
            video_path: Path to the video file
            max_frames: Maximum number of frames to extract (None for all)
            
        Yields:
            FrameInfo objects containing frame data and metadata
        """
        video = cv2.VideoCapture(video_path)
        if not video.isOpened():
            raise ValueError(f"Could not open video file: {video_path}")
        
        try:
            fps = video.get(cv2.CAP_PROP_FPS)
            frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = frame_count / fps if fps > 0 else 0
            
            # Calculate frame interval based on min_frame_interval
            frame_interval = max(1, int(fps * self.min_frame_interval))
            
            frame_number = 0
            frames_extracted = 0
            
            while True:
                ret, frame = video.read()
                if not ret:
                    break
                
                if frame_number % frame_interval == 0:
                    timestamp = frame_number / fps
                    is_key_frame = self._is_key_frame(frame)
                    
                    yield FrameInfo(
                        frame_number=frame_number,
                        timestamp=timestamp,
                        frame=frame.copy(),
                        is_key_frame=is_key_frame
                    )
                    
                    frames_extracted += 1
                    if max_frames and frames_extracted >= max_frames:
                        break
                
                frame_number += 1
                
        finally:
            video.release()

    def _is_key_frame(self, frame: np.ndarray) -> bool:
        """
        Determine if a frame is a key frame based on visual content.
        This is a simple implementation that can be enhanced with more sophisticated
        scene detection algorithms.
        
        Args:
            frame: The frame to analyze
            
        Returns:
            True if the frame is considered a key frame
        """
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Calculate frame statistics
        mean = np.mean(gray)
        std = np.std(gray)
        
        # Simple heuristic: frames with high standard deviation
        # are more likely to be key frames
        return std > 50  # This threshold can be adjusted

    def extract_audio(self, video_path: str, output_path: Optional[str] = None) -> str:
        """
        Extract audio from a video file.
        
        Args:
            video_path: Path to the video file
            output_path: Path to save the audio file (if None, uses video filename with .wav extension)
            
        Returns:
            Path to the extracted audio file
        """
        if output_path is None:
            output_path = str(Path(video_path).with_suffix('.wav'))
        
        video = VideoFileClip(video_path)
        try:
            video.audio.write_audiofile(output_path)
            return output_path
        finally:
            video.close()

    def get_frame_differences(
        self, frames: List[FrameInfo], threshold: float = 30.0
    ) -> List[int]:
        """
        Calculate frame differences to detect significant changes.
        
        Args:
            frames: List of FrameInfo objects
            threshold: Threshold for considering frames different
            
        Returns:
            List of frame numbers where significant changes occur
        """
        if len(frames) < 2:
            return []
        
        significant_changes = []
        prev_frame = cv2.cvtColor(frames[0].frame, cv2.COLOR_BGR2GRAY)
        
        for i in range(1, len(frames)):
            curr_frame = cv2.cvtColor(frames[i].frame, cv2.COLOR_BGR2GRAY)
            
            # Calculate mean absolute difference
            diff = cv2.absdiff(prev_frame, curr_frame)
            mean_diff = np.mean(diff)
            
            if mean_diff > threshold:
                significant_changes.append(frames[i].frame_number)
            
            prev_frame = curr_frame
        
        return significant_changes

    def prepare_frame_for_llm(self, frame):
        """
        Prepare a frame for LLM analysis by extracting meaningful visual features.
        
        Args:
            frame: The video frame to analyze
            
        Returns:
            Dictionary containing frame data and semantic visual description
        """
        # Convert frame to RGB if needed
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Basic image statistics
        brightness = np.mean(frame_rgb)
        contrast = np.std(frame_rgb)
        
        # Edge detection for scene complexity
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 100, 200)
        edge_density = np.count_nonzero(edges) / (edges.shape[0] * edges.shape[1])
        
        # Simple color analysis using histograms
        # Split into RGB channels
        r, g, b = cv2.split(frame_rgb)
        
        # Calculate mean values for each channel
        r_mean = np.mean(r)
        g_mean = np.mean(g)
        b_mean = np.mean(b)
        
        # Determine dominant color
        max_channel = max(r_mean, g_mean, b_mean)
        if max_channel == r_mean:
            dominant_color = "red"
        elif max_channel == g_mean:
            dominant_color = "green"
        else:
            dominant_color = "blue"
            
        # Calculate color temperature (warm vs cool)
        # Warm colors have higher red component, cool colors have higher blue
        color_temp = "warm" if r_mean > b_mean * 1.1 else "cool" if b_mean > r_mean * 1.1 else "neutral"
        
        # Calculate color intensity
        if max(r_mean, g_mean, b_mean) < 85:
            intensity = "dark"
        elif max(r_mean, g_mean, b_mean) < 170:
            intensity = "muted"
        else:
            intensity = "bright"
        
        # Generate semantic description
        scene_type = self._analyze_scene_type(frame_rgb, edge_density, r_mean, g_mean, b_mean)
        lighting = self._analyze_lighting(brightness, contrast)
        color_mood = f"with {intensity} {color_temp} tones"
        activity_level = self._analyze_activity_level(edge_density)
        
        semantic_description = f"{scene_type} {lighting} {color_mood} {activity_level}"
        
        return {
            "frame": frame_rgb,
            "statistics": {
                "brightness": float(brightness),
                "contrast": float(contrast),
                "edges": {
                    "edge_density": float(edge_density)
                },
                "colors": {
                    "r_mean": float(r_mean),
                    "g_mean": float(g_mean),
                    "b_mean": float(b_mean),
                    "dominant": dominant_color,
                    "temperature": color_temp,
                    "intensity": intensity
                }
            },
            "semantic_description": semantic_description
        }
    
    def _analyze_scene_type(self, frame, edge_density, r_mean, g_mean, b_mean):
        """Analyze the type of scene based on visual features."""
        # Determine if it's indoor/outdoor based on color distribution
        # Outdoor scenes tend to have more blue (sky) or green (nature)
        is_outdoor = (b_mean > max(r_mean, g_mean) * 1.2 or 
                     g_mean > max(r_mean, b_mean) * 1.2)
        
        # Determine scene complexity
        if edge_density < 0.05:
            complexity = "simple"
        elif edge_density < 0.15:
            complexity = "moderate"
        else:
            complexity = "complex"
            
        return f"A {complexity} {'outdoor' if is_outdoor else 'indoor'} scene"
    
    def _analyze_lighting(self, brightness, contrast):
        """Analyze the lighting conditions."""
        if brightness < 85:
            return "in dim lighting"
        elif brightness < 170:
            return "in moderate lighting"
        else:
            return "in bright lighting"
    
    def _analyze_activity_level(self, edge_density):
        """Analyze the level of activity or movement in the scene."""
        if edge_density < 0.05:
            return "showing minimal movement"
        elif edge_density < 0.15:
            return "with moderate activity"
        else:
            return "with high activity or movement"

    def _describe_frame_content(self, motion_level, edge_density, dominant_colors):
        """
        Generate a description of the frame content based on visual features.
        
        Args:
            motion_level: Level of motion detected
            edge_density: Density of edges in the frame
            dominant_colors: List of dominant colors with percentages
            
        Returns:
            String description of the frame content
        """
        # Describe motion
        motion_desc = ""
        if motion_level < 5:
            motion_desc = "very low motion"
        elif motion_level < 10:
            motion_desc = "low motion"
        elif motion_level < 20:
            motion_desc = "moderate motion"
        else:
            motion_desc = "high motion"
            
        # Describe edges
        edge_desc = ""
        if edge_density < 0.1:
            edge_desc = "low edge density"
        elif edge_density < 0.2:
            edge_desc = "moderate edge density"
        else:
            edge_desc = "high edge density"
            
        # Describe colors
        color_desc = []
        for color in dominant_colors[:2]:  # Only describe top 2 colors
            r, g, b = color["rgb"]
            percent = color["percent"] * 100
            
            # Basic color naming
            if max(r, g, b) < 64:
                color_name = "dark"
            elif max(r, g, b) < 128:
                color_name = "muted"
            else:
                color_name = "bright"
                
            if b > max(r, g):
                color_name += " blue"
            elif g > max(r, b):
                color_name += " green"
            elif r > max(g, b):
                color_name += " red"
            else:
                color_name += " gray"
                
            color_desc.append(f"{color_name} ({percent:.1f}%)")
            
        colors_text = " and ".join(color_desc)
        
        # Combine descriptions
        description = f"The frame shows a scene with {motion_desc} and {edge_desc}. "
        description += f"The dominant colors suggest a {colors_text} color palette."
        
        return description

    def format_timestamp(self, seconds: float) -> str:
        """Format seconds into a human-readable timestamp."""
        return str(timedelta(seconds=seconds))

    def get_scene_summary(self, scene: SceneInfo) -> str:
        """Generate a summary string for a scene."""
        return (
            f"Scene from {self.format_timestamp(scene.start_time)} to "
            f"{self.format_timestamp(scene.end_time)} "
            f"(duration: {self.format_timestamp(scene.end_time - scene.start_time)})"
        )

    def _is_significant_frame(self, frame_path: str) -> bool:
        """
        Determine if a frame contains significant visual content.
        
        Args:
            frame_path: Path to the frame image
            
        Returns:
            True if the frame contains significant content
        """
        # Load the frame
        frame = cv2.imread(str(frame_path))
        if frame is None:
            return False
        
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Calculate frame statistics
        mean = np.mean(gray)
        std = np.std(gray)
        
        # Detect edges
        edges = cv2.Canny(gray, 100, 200)
        edge_density = np.sum(edges > 0) / (edges.shape[0] * edges.shape[1])
        
        # Frame is significant if it has:
        # 1. Good contrast (std dev > 30)
        # 2. Reasonable brightness (mean between 30 and 225)
        # 3. Some edge content (density > 0.01)
        return (std > 30 and 30 < mean < 225 and edge_density > 0.01) 