"""
TTS (Text-to-Speech) module for Buddy Voice Assistant  
Provides clean interface to Kokoro-FastAPI speech synthesis service
"""

from .kokoro_client import (
    KokoroClient,
    kokoro_client,
    synthesize_speech,
    test_tts_service,
    get_voice_for_language,
    get_available_voices
)

__all__ = [
    'KokoroClient',
    'kokoro_client',
    'synthesize_speech',
    'test_tts_service',
    'get_voice_for_language', 
    'get_available_voices'
]