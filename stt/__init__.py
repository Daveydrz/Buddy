"""
STT (Speech-to-Text) module for Buddy Voice Assistant
Provides clean interface to Faster-Whisper transcription service
"""

from .whisper_client import (
    WhisperClient,
    whisper_client,
    transcribe_stream,
    transcribe_audio
)

__all__ = [
    'WhisperClient',
    'whisper_client', 
    'transcribe_stream',
    'transcribe_audio'
]