import os
import pytest
from pathlib import Path
from src.processors.video_processor import VideoProcessor, FrameInfo, SceneInfo

# Test video path
TEST_VIDEO_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "videos",
    "Elevator_Pitch_yoad_simon.mov"
)

def test_video_exists():
    """Verify that the test video exists."""
    assert os.path.exists(TEST_VIDEO_PATH), f"Test video not found at {TEST_VIDEO_PATH}"

def test_video_info():
    """Test basic video information extraction."""
    processor = VideoProcessor()
    duration, width, height, fps = processor.get_video_info(TEST_VIDEO_PATH)
    
    # Basic validation of video properties
    assert duration > 0, "Video duration should be positive"
    assert width > 0, "Video width should be positive"
    assert height > 0, "Video height should be positive"
    assert fps > 0, "Video FPS should be positive"
    
    print(f"\nVideo Information:")
    print(f"Duration: {processor.format_timestamp(duration)}")
    print(f"Resolution: {width}x{height}")
    print(f"FPS: {fps}")

def test_frame_extraction():
    """Test frame extraction functionality."""
    processor = VideoProcessor(min_frame_interval=1.0)  # Extract 1 frame per second
    frames = list(processor.extract_frames(TEST_VIDEO_PATH, max_frames=5))
    
    assert len(frames) > 0, "Should extract at least one frame"
    assert all(isinstance(frame, FrameInfo) for frame in frames), "All items should be FrameInfo objects"
    
    print(f"\nExtracted {len(frames)} frames:")
    for frame in frames:
        print(f"Frame {frame.frame_number} at {processor.format_timestamp(frame.timestamp)}")

def test_scene_detection():
    """Test scene detection functionality."""
    processor = VideoProcessor(
        min_frame_interval=0.5,
        scene_threshold=25.0,
        min_scene_duration=1.0
    )
    scenes = processor.detect_scenes(TEST_VIDEO_PATH)
    
    assert len(scenes) > 0, "Should detect at least one scene"
    assert all(isinstance(scene, SceneInfo) for scene in scenes), "All items should be SceneInfo objects"
    
    print(f"\nDetected {len(scenes)} scenes:")
    for i, scene in enumerate(scenes, 1):
        print(f"\nScene {i}:")
        print(processor.get_scene_summary(scene))
        print(f"Confidence: {scene.confidence:.2f}")

def test_frame_preparation():
    """Test frame preparation for LLM analysis."""
    processor = VideoProcessor()
    frames = list(processor.extract_frames(TEST_VIDEO_PATH, max_frames=1))
    
    assert len(frames) > 0, "Should extract at least one frame"
    frame_data = processor.prepare_frame_for_llm(frames[0].frame)
    
    # Verify frame preparation output
    assert 'frame' in frame_data, "Should contain the prepared frame"
    assert 'statistics' in frame_data, "Should contain frame statistics"
    assert 'brightness' in frame_data['statistics'], "Should contain brightness information"
    assert 'contrast' in frame_data['statistics'], "Should contain contrast information"
    assert 'dominant_colors' in frame_data['statistics'], "Should contain dominant colors"
    assert 'edges' in frame_data['statistics'], "Should contain edge information"
    
    print("\nFrame Statistics:")
    stats = frame_data['statistics']
    print(f"Brightness: {stats['brightness']:.2f}")
    print(f"Contrast: {stats['contrast']:.2f}")
    print(f"Edge Density: {stats['edges']['edge_density']:.2f}")
    print(f"Edge Intensity: {stats['edges']['edge_intensity']:.2f}")
    print("Dominant Colors:", stats['dominant_colors'])

def test_audio_extraction():
    """Test audio extraction functionality."""
    processor = VideoProcessor()
    output_path = processor.extract_audio(TEST_VIDEO_PATH)
    
    assert os.path.exists(output_path), "Should create audio file"
    assert output_path.endswith('.wav'), "Should create WAV file"
    
    # Clean up the extracted audio file
    os.remove(output_path)
    
    print(f"\nSuccessfully extracted audio to {output_path}")

if __name__ == "__main__":
    # Run all tests and print results
    print("Running Video Processor Tests...")
    print("=" * 50)
    
    test_video_exists()
    test_video_info()
    test_frame_extraction()
    test_scene_detection()
    test_frame_preparation()
    test_audio_extraction()
    
    print("\nAll tests completed successfully!") 