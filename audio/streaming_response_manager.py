# audio/streaming_response_manager.py - Manages streaming TTS responses
"""
Manages streaming TTS responses to ensure proper audio chunk accumulation,
sequencing, and completion tracking for Kokoro audio playback.
"""

import threading
import time
import queue
from typing import Dict, Optional, List
from dataclasses import dataclass
from config import DEBUG

@dataclass
class StreamingResponse:
    """Tracks a streaming response and its chunks"""
    response_id: str
    user: str
    start_time: float
    chunks_expected: Optional[int] = None
    chunks_received: int = 0
    chunks_played: int = 0
    is_complete: bool = False
    is_interrupted: bool = False
    
class StreamingResponseManager:
    """Manages streaming TTS responses and their completion state"""
    
    def __init__(self):
        self.active_responses: Dict[str, StreamingResponse] = {}
        self.response_counter = 0
        self.lock = threading.Lock()
        self.current_response_id: Optional[str] = None
        
    def start_response(self, user: str, expected_chunks: Optional[int] = None) -> str:
        """Start a new streaming response"""
        with self.lock:
            self.response_counter += 1
            response_id = f"response_{self.response_counter}_{int(time.time())}"
            
            # Stop any existing response
            if self.current_response_id:
                self.mark_response_interrupted(self.current_response_id)
            
            response = StreamingResponse(
                response_id=response_id,
                user=user,
                start_time=time.time(),
                chunks_expected=expected_chunks
            )
            
            self.active_responses[response_id] = response
            self.current_response_id = response_id
            
            if DEBUG:
                print(f"[StreamingManager] 🚀 Started response {response_id} for {user}")
                if expected_chunks:
                    print(f"[StreamingManager] 📊 Expecting {expected_chunks} chunks")
            
            return response_id
    
    def add_chunk(self, response_id: str) -> bool:
        """Add a chunk to the response"""
        with self.lock:
            if response_id not in self.active_responses:
                if DEBUG:
                    print(f"[StreamingManager] ⚠️ Response {response_id} not found")
                return False
            
            response = self.active_responses[response_id]
            if response.is_interrupted:
                if DEBUG:
                    print(f"[StreamingManager] 🛑 Response {response_id} is interrupted")
                return False
            
            response.chunks_received += 1
            
            if DEBUG:
                progress = f"{response.chunks_received}"
                if response.chunks_expected:
                    progress += f"/{response.chunks_expected}"
                print(f"[StreamingManager] ➕ Chunk added to {response_id}: {progress}")
            
            return True
    
    def mark_chunk_played(self, response_id: str) -> bool:
        """Mark a chunk as played"""
        with self.lock:
            if response_id not in self.active_responses:
                return False
            
            response = self.active_responses[response_id]
            response.chunks_played += 1
            
            if DEBUG:
                print(f"[StreamingManager] 🎵 Chunk played for {response_id}: {response.chunks_played}/{response.chunks_received}")
            
            # Check if response is complete
            if (response.chunks_expected and 
                response.chunks_played >= response.chunks_expected and
                response.is_complete):
                self._finish_response(response_id)
                return True
            
            return False
    
    def mark_response_complete(self, response_id: str) -> bool:
        """Mark the response as complete (no more chunks coming)"""
        with self.lock:
            if response_id not in self.active_responses:
                return False
            
            response = self.active_responses[response_id]
            response.is_complete = True
            
            if DEBUG:
                print(f"[StreamingManager] ✅ Response {response_id} marked complete")
            
            # Check if all chunks have been played
            if response.chunks_played >= response.chunks_received:
                self._finish_response(response_id)
                return True
            
            return False
    
    def mark_response_interrupted(self, response_id: str) -> bool:
        """Mark the response as interrupted"""
        with self.lock:
            if response_id not in self.active_responses:
                return False
            
            response = self.active_responses[response_id]
            response.is_interrupted = True
            
            if DEBUG:
                print(f"[StreamingManager] 🛑 Response {response_id} interrupted")
            
            self._finish_response(response_id)
            return True
    
    def _finish_response(self, response_id: str):
        """Finish and clean up a response"""
        if response_id in self.active_responses:
            response = self.active_responses[response_id]
            duration = time.time() - response.start_time
            
            if DEBUG:
                status = "INTERRUPTED" if response.is_interrupted else "COMPLETED"
                print(f"[StreamingManager] 🏁 Response {response_id} {status} in {duration:.2f}s")
                print(f"[StreamingManager] 📊 Stats: {response.chunks_played}/{response.chunks_received} chunks played")
            
            # Remove from active responses
            del self.active_responses[response_id]
            
            # Clear current response if this was it
            if self.current_response_id == response_id:
                self.current_response_id = None
    
    def is_response_active(self, response_id: str) -> bool:
        """Check if a response is still active"""
        with self.lock:
            return response_id in self.active_responses and not self.active_responses[response_id].is_interrupted
    
    def should_notify_completion(self) -> bool:
        """Check if we should notify that speaking is complete"""
        with self.lock:
            # Only notify if no active responses or all are complete/interrupted
            for response in self.active_responses.values():
                if not response.is_complete and not response.is_interrupted:
                    return False
            return True
    
    def get_active_response_stats(self) -> Dict:
        """Get statistics about active responses"""
        with self.lock:
            stats = {
                "active_responses": len(self.active_responses),
                "current_response": self.current_response_id,
                "responses": {}
            }
            
            for response_id, response in self.active_responses.items():
                stats["responses"][response_id] = {
                    "user": response.user,
                    "chunks_received": response.chunks_received,
                    "chunks_played": response.chunks_played,
                    "chunks_expected": response.chunks_expected,
                    "is_complete": response.is_complete,
                    "is_interrupted": response.is_interrupted,
                    "duration": time.time() - response.start_time
                }
            
            return stats

# Global streaming response manager
_streaming_manager = None

def get_streaming_manager() -> StreamingResponseManager:
    """Get the global streaming response manager"""
    global _streaming_manager
    if _streaming_manager is None:
        _streaming_manager = StreamingResponseManager()
    return _streaming_manager