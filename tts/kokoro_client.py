"""
Kokoro TTS Client - Single responsibility adapter for text-to-speech  
Handles HTTP connections to Kokoro-FastAPI with voice selection and streaming
"""
import asyncio
import aiohttp
import requests
from typing import Optional, Dict, Any
from langdetect import detect
from config.models import (
    KOKORO_API_BASE_URL, KOKORO_API_TIMEOUT, KOKORO_DEFAULT_VOICE,
    KOKORO_API_VOICES, KOKORO_VOICE_SPEED, KOKORO_VOICE_STABILITY, 
    KOKORO_VOICE_CLARITY, KOKORO_STREAMING_ENABLED, KOKORO_CHUNK_SIZE,
    get_kokoro_voice_config
)
from config.core import DEBUG, DEFAULT_LANG

class KokoroClient:
    """Client for Kokoro-FastAPI text-to-speech service"""
    
    def __init__(self, base_url: str = KOKORO_API_BASE_URL):
        self.base_url = base_url
        self.timeout = KOKORO_API_TIMEOUT
        self.voice_config = get_kokoro_voice_config()
        self.session = None
        self.is_available = None
        self._setup_session()
    
    def _setup_session(self):
        """Setup requests session for TTS requests"""
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'audio/wav'
        })
    
    async def health_check(self) -> bool:
        """
        Check if Kokoro-FastAPI service is available
        
        Returns:
            True if service is available, False otherwise
        """
        if self.is_available is not None:
            return self.is_available
            
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.session.get(
                    f"{self.base_url}/health",
                    timeout=5
                )
            )
            self.is_available = response.status_code == 200
            if DEBUG and self.is_available:
                print(f"[KokoroClient] ✅ Connected to {self.base_url}")
            return self.is_available
        except Exception as e:
            if DEBUG:
                print(f"[KokoroClient] Health check failed: {e}")
            self.is_available = False
            return False
    
    async def synthesize(self, text: str, voice: Optional[str] = None, language: Optional[str] = None) -> Optional[bytes]:
        """
        Synthesize text to speech audio
        
        Args:
            text: Text to synthesize
            voice: Voice ID to use (defaults to auto-detection based on language)
            language: Language code (defaults to auto-detection)
            
        Returns:
            WAV audio bytes or None on failure
        """
        if not text or len(text.strip()) < 1:
            return None
        
        # Check service availability
        if not await self.health_check():
            if DEBUG:
                print("[KokoroClient] Service not available")
            return None
        
        # Determine voice
        if not voice:
            if not language:
                try:
                    language = detect(text)
                except:
                    language = DEFAULT_LANG
            
            voice = self.voice_config['voices'].get(language, self.voice_config['default_voice'])
        
        # Prepare request payload
        payload = {
            "input": text.strip(),
            "voice": voice,
            "response_format": "wav",
            "speed": self.voice_config['speed'],
            "stability": self.voice_config['stability'],
            "clarity": self.voice_config['clarity']
        }
        
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.session.post(
                    f"{self.base_url}/generate",
                    json=payload,
                    timeout=self.timeout
                )
            )
            
            if response.status_code == 200:
                audio_data = response.content
                if DEBUG:
                    print(f"[KokoroClient] 🎵 Generated {len(audio_data)} bytes for voice '{voice}'")
                return audio_data
            else:
                if DEBUG:
                    print(f"[KokoroClient] HTTP {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            if DEBUG:
                print(f"[KokoroClient] Synthesis error: {e}")
            return None
    
    async def synthesize_streaming(self, text: str, voice: Optional[str] = None, language: Optional[str] = None) -> Optional[bytes]:
        """
        Synthesize text with streaming capabilities (placeholder for future streaming API)
        
        Currently falls back to regular synthesis since Kokoro-FastAPI doesn't support true streaming
        
        Args:
            text: Text to synthesize
            voice: Voice ID to use
            language: Language code
            
        Returns:
            WAV audio bytes or None on failure
        """
        # For now, fall back to regular synthesis
        # In the future, this could be enhanced to support chunked streaming
        return await self.synthesize(text, voice, language)
    
    def get_available_voices(self) -> Dict[str, str]:
        """
        Get available voices
        
        Returns:
            Dictionary mapping language codes to voice IDs
        """
        return self.voice_config['voices'].copy()
    
    def get_voice_for_language(self, language: str) -> str:
        """
        Get appropriate voice for a given language
        
        Args:
            language: Language code
            
        Returns:
            Voice ID
        """
        return self.voice_config['voices'].get(language, self.voice_config['default_voice'])
    
    async def test_voice(self, voice: str, test_text: str = "Hello, this is a voice test.") -> bool:
        """
        Test a specific voice
        
        Args:
            voice: Voice ID to test
            test_text: Text to use for testing
            
        Returns:
            True if voice works, False otherwise
        """
        try:
            audio = await self.synthesize(test_text, voice=voice)
            return audio is not None and len(audio) > 0
        except Exception as e:
            if DEBUG:
                print(f"[KokoroClient] Voice test failed for '{voice}': {e}")
            return False
    
    def close(self):
        """Clean up session resources"""
        if self.session:
            self.session.close()

# Global instance
kokoro_client = KokoroClient()

# Convenience functions for backward compatibility
async def synthesize_speech(text: str, voice: Optional[str] = None) -> Optional[bytes]:
    """Synthesize text to speech - convenience function"""
    return await kokoro_client.synthesize(text, voice)

async def test_tts_service() -> bool:
    """Test if TTS service is available - convenience function"""
    return await kokoro_client.health_check()

def get_voice_for_language(language: str) -> str:
    """Get voice for language - convenience function"""
    return kokoro_client.get_voice_for_language(language)

def get_available_voices() -> Dict[str, str]:
    """Get available voices - convenience function"""
    return kokoro_client.get_available_voices()