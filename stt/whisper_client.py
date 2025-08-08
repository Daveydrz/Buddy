"""
Whisper STT Client - Single responsibility adapter for speech-to-text
Handles WebSocket connection to Faster-Whisper server with timeouts and retries
"""
import asyncio
import json
import numpy as np
import websockets
from typing import AsyncIterator, Optional
from config.models import (
    FASTER_WHISPER_WS, WHISPER_TIMEOUT, WHISPER_MAX_RETRIES, WHISPER_RETRY_DELAY
)
from config.core import DEBUG

class WhisperClient:
    """Client for Faster-Whisper WebSocket transcription service"""
    
    def __init__(self, websocket_url: str = FASTER_WHISPER_WS):
        self.websocket_url = websocket_url
        self.timeout = WHISPER_TIMEOUT
        self.max_retries = WHISPER_MAX_RETRIES
        self.retry_delay = WHISPER_RETRY_DELAY
    
    async def transcribe_stream(self, audio_iter: AsyncIterator[np.ndarray]) -> str:
        """
        Transcribe audio stream using Faster-Whisper WebSocket
        
        Args:
            audio_iter: Async iterator yielding audio numpy arrays
            
        Returns:
            Transcribed text or empty string on failure
        """
        retries = 0
        while retries <= self.max_retries:
            try:
                return await self._transcribe_attempt(audio_iter)
            except Exception as e:
                retries += 1
                if DEBUG:
                    print(f"[WhisperClient] Attempt {retries} failed: {e}")
                
                if retries <= self.max_retries:
                    await asyncio.sleep(self.retry_delay)
                else:
                    if DEBUG:
                        print(f"[WhisperClient] All {self.max_retries + 1} attempts failed")
                    return ""
        return ""
    
    async def transcribe_audio(self, audio: np.ndarray) -> str:
        """
        Transcribe a single audio array
        
        Args:
            audio: Numpy array containing audio data
            
        Returns:
            Transcribed text or empty string on failure
        """
        async def audio_generator():
            yield audio
            
        return await self.transcribe_stream(audio_generator())
    
    async def _transcribe_attempt(self, audio_iter: AsyncIterator[np.ndarray]) -> str:
        """Single transcription attempt"""
        try:
            async with websockets.connect(
                self.websocket_url, 
                ping_interval=None,
                close_timeout=5
            ) as ws:
                
                # Send audio data
                async for audio in audio_iter:
                    # Ensure audio is in correct format
                    if audio.dtype != np.int16:
                        if np.issubdtype(audio.dtype, np.floating):
                            audio = (audio * 32767).clip(-32768, 32767).astype(np.int16)
                        else:
                            audio = audio.astype(np.int16)
                    
                    await ws.send(audio.tobytes())
                
                # Signal end of audio stream
                await ws.send("end")
                
                # Wait for transcription result
                try:
                    message = await asyncio.wait_for(ws.recv(), timeout=self.timeout)
                except asyncio.TimeoutError:
                    if DEBUG:
                        print(f"[WhisperClient] Transcription timeout ({self.timeout}s)")
                    return ""
                
                # Parse response
                return self._parse_response(message)
                
        except Exception as e:
            if DEBUG:
                print(f"[WhisperClient] WebSocket error: {e}")
            raise
    
    def _parse_response(self, message) -> str:
        """Parse transcription response from WebSocket"""
        try:
            # Try JSON format first
            if isinstance(message, (str, bytes)):
                if isinstance(message, bytes):
                    message = message.decode("utf-8")
                    
                try:
                    data = json.loads(message)
                    text = data.get("text", "").strip()
                    if DEBUG and text:
                        print(f"[WhisperClient] 📝 Transcribed: '{text}'")
                    return text
                except json.JSONDecodeError:
                    # Fallback to plain text
                    text = message.strip()
                    if DEBUG and text:
                        print(f"[WhisperClient] 📝 Transcribed: '{text}'")
                    return text
            
            return ""
            
        except Exception as e:
            if DEBUG:
                print(f"[WhisperClient] Response parsing error: {e}")
            return ""
    
    async def health_check(self) -> bool:
        """Check if Whisper service is available"""
        try:
            # Send a small test audio array
            test_audio = np.array([0] * 16000, dtype=np.int16)  # 1 second of silence
            result = await self.transcribe_audio(test_audio)
            return True  # If no exception, service is available
        except Exception as e:
            if DEBUG:
                print(f"[WhisperClient] Health check failed: {e}")
            return False

# Global instance
whisper_client = WhisperClient()

# Convenience function for backward compatibility
async def transcribe_stream(audio_iter: AsyncIterator[np.ndarray]) -> str:
    """Transcribe audio stream - convenience function"""
    return await whisper_client.transcribe_stream(audio_iter)

async def transcribe_audio(audio: np.ndarray) -> str:
    """Transcribe single audio array - convenience function"""
    return await whisper_client.transcribe_audio(audio)