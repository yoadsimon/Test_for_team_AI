import os
from pathlib import Path
from src.processors.video_processor import VideoProcessor
from src.processors.audio_processor import AudioProcessor

VIDEO_PATH = Path("videos/demo_v.MOV")
AUDIO_PATH = VIDEO_PATH.with_suffix('.wav')

def main():
    # Extract audio if not already present
    if not AUDIO_PATH.exists():
        print(f"Extracting audio from {VIDEO_PATH}...")
        video_processor = VideoProcessor()
        audio_path = video_processor.extract_audio(str(VIDEO_PATH))
    else:
        audio_path = str(AUDIO_PATH)
        print(f"Audio already exists: {audio_path}")

    # Transcribe audio
    print("Transcribing audio...")
    audio_processor = AudioProcessor()
    transcriptions = audio_processor.transcribe_audio(audio_path)

    print("\nTranscript:")
    for start, end, text in transcriptions:
        print(f"[{start:.2f}s - {end:.2f}s]: {text}")

if __name__ == "__main__":
    main() 