import pytest
from src.processors.audio_processor import AudioProcessor
import os
from pathlib import Path

from src.processors.video_processor import VideoProcessor

@pytest.fixture
def audio_processor():
    return AudioProcessor()

def test_find_speech_segments(audio_processor):
    """Test that speech segments are correctly detected."""
    # Get the test video path
    video_dir = Path("videos")
    test_video = next(video_dir.glob("*.MOV"))  # Get the first MOV file
    test_audio = str(test_video.with_suffix('.wav'))
    
    # First, ensure we have the audio file
    if not os.path.exists(test_audio):
        video_processor = VideoProcessor()
        test_audio = video_processor.extract_audio(str(test_video))
    
    # Find speech segments
    segments = audio_processor.find_speech_segments(test_audio)
    
    # Print all found segments for debugging
    print("\nFound speech segments:")
    for start, end in segments:
        print(f"  {start:.2f}s - {end:.2f}s")
        # Try to transcribe each segment
        text = audio_processor.transcribe_segment(test_audio, start, end)
        print(f"  Text: {text}")
    
    # Basic assertions
    assert len(segments) > 0, "Should detect at least one speech segment"
    
    # Test transcription of each segment
    print("\nTranscribed segments:")
    all_transcriptions = []
    for start, end in segments:
        text = audio_processor.transcribe_segment(test_audio, start, end)
        if text:
            all_transcriptions.append((start, end, text))
            print(f"  {start:.2f}s - {end:.2f}s: {text}")
    
    assert len(all_transcriptions) > 0, "Should have at least one transcribed segment"

def test_transcribe_segment(audio_processor):
    """Test that individual segments are correctly transcribed."""
    # Get the test video path
    video_dir = Path("videos")
    test_video = next(video_dir.glob("*.MOV"))
    test_audio = str(test_video.with_suffix('.wav'))
    
    # First, ensure we have the audio file
    if not os.path.exists(test_audio):
        video_processor = VideoProcessor()
        test_audio = video_processor.extract_audio(str(test_video))
    
    # Test transcription at known speech times (adjust these based on your test video)
    test_segments = [
        (0, 2),    # Test first 2 seconds
        (2, 4),    # Test next 2 seconds
        (4, 6),    # And so on...
        (6, 8),
        (8, 10)
    ]
    
    print("\nTesting fixed time segments:")
    for start, end in test_segments:
        text = audio_processor.transcribe_segment(test_audio, start, end)
        print(f"  {start}s - {end}s: {text}")
        # We don't assert the content, but we want to see what's found

def test_speech_detection_sensitivity(audio_processor):
    """Test different sensitivity thresholds for speech detection."""
    # Get the test video path
    video_dir = Path("videos")
    test_video = next(video_dir.glob("*.MOV"))
    test_audio = str(test_video.with_suffix('.wav'))
    
    # First, ensure we have the audio file
    if not os.path.exists(test_audio):
        video_processor = VideoProcessor()
        test_audio = video_processor.extract_audio(str(test_video))
    
    # Test original threshold
    original_segments = audio_processor.find_speech_segments(test_audio)
    print(f"\nOriginal threshold (0.05) found {len(original_segments)} segments:")
    for start, end in original_segments:
        text = audio_processor.transcribe_segment(test_audio, start, end)
        print(f"  {start:.2f}s - {end:.2f}s: {text}")
    
    # Temporarily modify threshold to be more sensitive
    audio_processor.threshold = 0.03  # More sensitive
    sensitive_segments = audio_processor.find_speech_segments(test_audio)
    print(f"\nMore sensitive threshold (0.03) found {len(sensitive_segments)} segments:")
    for start, end in sensitive_segments:
        text = audio_processor.transcribe_segment(test_audio, start, end)
        print(f"  {start:.2f}s - {end:.2f}s: {text}")
    
    # Compare results
    assert len(sensitive_segments) >= len(original_segments), "More sensitive threshold should find at least as many segments"

def test_extract_audio_from_video():
    """Test extracting audio from a video file."""
    video_dir = Path("videos")
    test_video = next(video_dir.glob("*.MOV"))
    video_processor = VideoProcessor()
    audio_path = video_processor.extract_audio(str(test_video))
    assert os.path.exists(audio_path), f"Audio file was not created: {audio_path}"
    assert os.path.getsize(audio_path) > 0, "Extracted audio file is empty"
    print(f"Extracted audio: {audio_path}, size: {os.path.getsize(audio_path)} bytes")

def test_transcribe_audio_from_file():
    """Test extracting transcript from the audio file."""
    video_dir = Path("videos")
    test_video = next(video_dir.glob("*.MOV"))
    audio_path = str(test_video.with_suffix('.wav'))
    if not os.path.exists(audio_path):
        video_processor = VideoProcessor()
        audio_path = video_processor.extract_audio(str(test_video))
    audio_processor = AudioProcessor()
    transcriptions = audio_processor.transcribe_audio(audio_path)
    print("Transcriptions:", transcriptions)
    assert isinstance(transcriptions, list), "Transcriptions should be a list"
    assert len(transcriptions) > 0, "Should extract at least one transcription segment"
    for start, end, text in transcriptions:
        assert isinstance(text, str)
        assert len(text.strip()) > 0, "Transcript text should not be empty" 