import os
from pathlib import Path
from typing import List, Optional, Tuple
from moviepy.editor import AudioFileClip
import numpy as np
import librosa
import soundfile as sf
import tempfile
from faster_whisper import WhisperModel


class AudioProcessor:
    """Handles audio processing including speech detection and transcription."""

    def __init__(self, language: str = "en"):
        """
        Initialize the audio processor.
        
        Args:
            language: Language code for speech recognition
        """
        self.language = language
        self.whisper = WhisperModel("base", device="cpu", compute_type="int8")

    def extract_audio_segment(
        self, audio_path: str, start_time: float, end_time: float
    ) -> str:
        """
        Extract a segment of audio between start_time and end_time.
        
        Args:
            audio_path: Path to the audio file
            start_time: Start time in seconds
            end_time: End time in seconds
            
        Returns:
            Path to the extracted audio segment
        """
        # Load audio
        y, sr = librosa.load(audio_path)
        
        # Convert times to samples
        start_sample = int(start_time * sr)
        end_sample = int(end_time * sr)
        
        # Extract segment
        segment = y[start_sample:end_sample]
        
        # Save to temporary file
        temp_path = tempfile.mktemp(suffix='.wav')
        sf.write(temp_path, segment, sr)
        
        return temp_path

    def transcribe_audio(
        self, audio_path: str, segment_duration: float = 30.0
    ) -> List[Tuple[float, float, str]]:
        """
        Transcribe audio file to text using Whisper.
        
        Args:
            audio_path: Path to the audio file
            segment_duration: Duration of each segment in seconds (not used with Whisper)
            
        Returns:
            List of tuples containing (start_time, end_time, transcription)
        """
        # Transcribe using whisper
        segments, info = self.whisper.transcribe(
            audio_path,
            language=self.language,
            vad_filter=True
        )
        
        # Convert segments to our format
        transcriptions = []
        for segment in segments:
            transcriptions.append((
                segment.start,
                segment.end,
                segment.text.strip()
            ))
        
        return transcriptions

    def find_speech_segments(self, audio_path: str) -> List[Tuple[float, float]]:
        """
        Find segments containing speech in an audio file.
        Uses librosa for more accurate speech detection.
        
        Args:
            audio_path: Path to the audio file
            
        Returns:
            List of (start_time, end_time) tuples for speech segments
        """
        # Load audio file
        y, sr = librosa.load(audio_path)
        
        # Get amplitude envelope
        hop_length = 512
        envelope = np.array([
            sum(abs(y[i:i+hop_length]))
            for i in range(0, len(y), hop_length)
        ])
        
        # Normalize envelope
        envelope = envelope / np.max(envelope)
        
        # Find segments above threshold (speech)
        threshold = 0.05  # Lower threshold to detect quieter speech
        speech_samples = envelope > threshold
        
        # Convert to time segments
        segments = []
        start_sample = None
        min_segment_duration = 0.3  # Shorter minimum duration to catch brief utterances
        
        for i, is_speech in enumerate(speech_samples):
            time = i * hop_length / sr
            
            if is_speech and start_sample is None:
                start_sample = i
            elif not is_speech and start_sample is not None:
                duration = (i - start_sample) * hop_length / sr
                if duration >= min_segment_duration:
                    start_time = start_sample * hop_length / sr
                    end_time = i * hop_length / sr
                    segments.append((start_time, end_time))
                start_sample = None
        
        # Handle the last segment if it ends with speech
        if start_sample is not None:
            duration = (len(speech_samples) - start_sample) * hop_length / sr
            if duration >= min_segment_duration:
                start_time = start_sample * hop_length / sr
                end_time = len(y) / sr
                segments.append((start_time, end_time))
        
        return segments

    def transcribe_segment(self, audio_path: str, start_time: float, end_time: float) -> str:
        """
        Transcribe a segment of audio between start_time and end_time.
        
        Args:
            audio_path: Path to the audio file
            start_time: Start time in seconds
            end_time: End time in seconds
            
        Returns:
            Transcribed text
        """
        # Extract the segment
        segment_path = self.extract_audio_segment(audio_path, start_time, end_time)
        
        try:
            # Transcribe using whisper
            segments, info = self.whisper.transcribe(
                segment_path,
                language=self.language,
                vad_filter=True
            )
            
            # Combine all segments
            text = " ".join(segment.text for segment in segments)
            return text.strip()
            
        finally:
            # Clean up temporary file
            if os.path.exists(segment_path):
                os.remove(segment_path)

    def get_audio_energy(self, audio_path: str, start_time: float, end_time: float) -> float:
        """
        Calculate the average energy/volume in an audio segment.
        
        Args:
            audio_path: Path to the audio file
            start_time: Start time in seconds
            end_time: End time in seconds
            
        Returns:
            Average energy as a float
        """
        # Load audio segment
        y, sr = librosa.load(audio_path)
        
        # Convert times to samples
        start_sample = int(start_time * sr)
        end_sample = int(end_time * sr)
        
        # Extract segment
        segment = y[start_sample:end_sample]
        
        # Calculate RMS energy
        energy = np.sqrt(np.mean(segment**2))
        
        return float(energy) 