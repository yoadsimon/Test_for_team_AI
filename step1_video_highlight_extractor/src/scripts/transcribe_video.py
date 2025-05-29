#!/usr/bin/env python3
import argparse
from pathlib import Path
from processors.audio_processor import AudioProcessor
from processors.video_processor import VideoProcessor

def transcribe_video(video_path: str, output_file: str = None) -> list:
    """
    Transcribe a video file and optionally save the transcript to a file.
    
    Args:
        video_path (str): Path to the video file
        output_file (str, optional): Path to save the transcript. If None, only prints to console.
    
    Returns:
        list: List of tuples containing (start_time, end_time, transcript_text)
    """
    # Initialize processors
    video_processor = VideoProcessor()
    audio_processor = AudioProcessor()
    
    # Convert video path to Path object
    video_path = Path(video_path)
    
    # Extract audio from video
    print(f"Extracting audio from {video_path}...")
    audio_path = video_processor.extract_audio(str(video_path))
    print(f"Audio extracted to: {audio_path}")
    
    # Get transcriptions
    print("Transcribing audio...")
    transcriptions = audio_processor.transcribe_audio(audio_path)
    
    # Print transcriptions
    print("\nTranscript:")
    print("-" * 50)
    for start, end, text in transcriptions:
        print(f"[{start:.2f}s - {end:.2f}s] {text}")
    print("-" * 50)
    
    # Save to file if requested
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            for start, end, text in transcriptions:
                f.write(f"[{start:.2f}s - {end:.2f}s] {text}\n")
        print(f"\nTranscript saved to: {output_file}")
    
    return transcriptions

def main():
    parser = argparse.ArgumentParser(description='Transcribe audio from a video file')
    parser.add_argument('video_path', help='Path to the video file')
    parser.add_argument('-o', '--output', help='Path to save the transcript (optional)')
    
    args = parser.parse_args()
    
    try:
        transcribe_video(args.video_path, args.output)
    except Exception as e:
        print(f"Error: {str(e)}")
        exit(1)

if __name__ == '__main__':
    main() 