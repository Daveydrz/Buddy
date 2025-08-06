# audio/streaming_kokoro.py - FIXED: Actually connect to your Kokoro TTS
"""
Streaming wrapper for Kokoro TTS that works with your existing setup
"""
import threading
import queue
import time
import numpy as np
from typing import Optional, Generator, List
from concurrent.futures import ThreadPoolExecutor, Future
from dataclasses import dataclass
from audio.kyutai_coordinator import StreamingChunk, get_kyutai_coordinator
from config import *

@dataclass
class AudioChunk:
    """Audio chunk with metadata"""
    audio_data: np.ndarray
    sample_rate: int
    chunk_id: str
    text: str
    start_time: float
    generation_time: float

class StreamingKokoroWrapper:
    """FIXED: Streaming wrapper that uses your existing Kokoro setup"""
    
    def __init__(self):
        self.thread_pool = ThreadPoolExecutor(max_workers=STREAMING_THREAD_POOL_SIZE)
        self.audio_queue = queue.Queue(maxsize=STREAMING_BUFFER_SIZE)
        self.generation_futures = {}
        self.is_streaming = False
        self.current_voice = "af_heart"  # Default voice
        self.current_lang = "en-us"
        
    def set_voice_settings(self, lang: str):
        """Set voice and language for Kokoro"""
        if lang in KOKORO_VOICES:
            self.current_voice = KOKORO_VOICES[lang]
            self.current_lang = KOKORO_LANGS[lang]
            if DEBUG:
                print(f"[StreamingKokoro] 🎭 Voice set to {self.current_voice} ({self.current_lang})")
    
    def generate_audio_chunk_sync(self, text: str, chunk_id: str, response_id: str = None) -> Optional[AudioChunk]:
        """Generate audio for a single chunk using improved audio output system"""
        try:
            start_time = time.time()
            
            if DEBUG:
                print(f"[StreamingKokoro] 🎵 Generating chunk {chunk_id}: '{text[:30]}...'")
            
            # ✅ FIXED: Use improved speak_streaming with response tracking
            from audio.output import speak_streaming
            success = speak_streaming(text, self.current_lang.split('-')[0], response_id=response_id)
            
            generation_time = time.time() - start_time
            
            if success:
                # Create audio chunk metadata (actual audio is handled by speak_streaming)
                audio_chunk = AudioChunk(
                    audio_data=np.array([]),  # Placeholder - actual audio is queued by speak_streaming
                    sample_rate=16000,
                    chunk_id=chunk_id,
                    text=text,
                    start_time=start_time,
                    generation_time=generation_time
                )
                
                if DEBUG:
                    print(f"[StreamingKokoro] ✅ Queued chunk {chunk_id} in {generation_time:.2f}s")
                
                return audio_chunk
            else:
                print(f"[StreamingKokoro] ❌ Failed to queue chunk {chunk_id}")
                return None
            
        except Exception as e:
            print(f"[StreamingKokoro] ❌ Error generating audio for chunk {chunk_id}: {e}")
            return None
    
    def stream_text_chunks(self, text_chunks: List[str], lang: str = "en", response_id: str = None) -> Generator[AudioChunk, None, None]:
        """Stream audio generation for text chunks with proper response tracking"""
        self.set_voice_settings(lang)
        self.is_streaming = True
        
        try:
            # Create Kyutai coordinator chunks
            coordinator = get_kyutai_coordinator()
            all_chunks = []
            
            for text in text_chunks:
                chunks = coordinator.smart_chunk_text(text)
                optimized_chunks = coordinator.optimize_for_kokoro(chunks)
                all_chunks.extend(optimized_chunks)
            
            if DEBUG:
                print(f"[StreamingKokoro] 🎵 Streaming {len(all_chunks)} chunks")
                if response_id:
                    print(f"[StreamingKokoro] 📊 Response ID: {response_id}")
            
            # Process chunks with timing
            for i, chunk in enumerate(all_chunks):
                chunk_id = f"chunk_{i}"
                
                # Generate and queue audio with response tracking
                audio_chunk = self.generate_audio_chunk_sync(chunk.text, chunk_id, response_id)
                
                if audio_chunk:
                    yield audio_chunk
                
                # Apply Kyutai prosody timing
                if KYUTAI_PROSODY_OVERLAP > 0 and i < len(all_chunks) - 1:
                    time.sleep(KYUTAI_PROSODY_OVERLAP)
        
        finally:
            self.is_streaming = False
    
    def get_streaming_stats(self) -> dict:
        """Get streaming performance statistics"""
        return {
            "is_streaming": self.is_streaming,
            "current_voice": self.current_voice,
            "current_lang": self.current_lang,
            "buffer_size": STREAMING_BUFFER_SIZE,
            "thread_pool_size": STREAMING_THREAD_POOL_SIZE
        }

# Global streaming Kokoro instance
streaming_kokoro = StreamingKokoroWrapper()

def stream_speak_chunks(text_chunks: List[str], lang: str = "en", response_id: str = None):
    """✅ FIXED: High-level function to stream speak text chunks with response tracking"""
    from audio.output import complete_streaming_response
    
    kokoro = streaming_kokoro
    
    if DEBUG:
        print(f"[StreamSpeak] 🌊 Starting to stream {len(text_chunks)} text chunks")
        if response_id:
            print(f"[StreamSpeak] 📊 Response ID: {response_id}")
    
    chunk_count = 0
    try:
        for audio_chunk in kokoro.stream_text_chunks(text_chunks, lang, response_id):
            chunk_count += 1
            if DEBUG:
                print(f"[StreamSpeak] 🎵 Completed chunk {chunk_count}: '{audio_chunk.text[:30]}...'")
    finally:
        # Mark the response as complete when all chunks are processed
        if response_id:
            complete_streaming_response(response_id)
        
        if DEBUG:
            print(f"[StreamSpeak] ✅ Completed streaming {chunk_count} chunks")
            if response_id:
                print(f"[StreamSpeak] 🏁 Response {response_id} marked complete")