# audio/kyutai_coordinator.py - Text chunking coordinator for streaming TTS
"""
Kyutai coordinator for optimizing text chunks for Kokoro TTS streaming.
Handles intelligent text segmentation and prosody optimization.
"""

import re
import time
from dataclasses import dataclass
from typing import List, Optional
from config import DEBUG

@dataclass
class StreamingChunk:
    """Represents a chunk of text optimized for streaming TTS"""
    text: str
    chunk_id: str
    priority: int = 1
    prosody_pause: float = 0.1
    is_sentence_end: bool = False
    is_paragraph_end: bool = False

class KyutaiCoordinator:
    """Coordinates text chunking for optimal streaming TTS"""
    
    def __init__(self):
        self.chunk_counter = 0
        
    def smart_chunk_text(self, text: str, max_chunk_size: int = 100) -> List[StreamingChunk]:
        """Split text into smart chunks optimized for TTS streaming"""
        if not text or not text.strip():
            return []
        
        chunks = []
        self.chunk_counter = 0
        
        # Clean and normalize text
        text = text.strip()
        
        # Split by sentences first
        sentences = re.split(r'[.!?]+', text)
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            # If sentence is short enough, create a single chunk
            if len(sentence) <= max_chunk_size:
                chunk = self._create_chunk(sentence, is_sentence_end=True)
                chunks.append(chunk)
            else:
                # Split long sentences by commas and clauses
                sub_chunks = self._split_long_sentence(sentence, max_chunk_size)
                chunks.extend(sub_chunks)
        
        if DEBUG:
            print(f"[KyutaiCoordinator] Created {len(chunks)} text chunks")
            
        return chunks
    
    def _create_chunk(self, text: str, is_sentence_end: bool = False, is_paragraph_end: bool = False) -> StreamingChunk:
        """Create a streaming chunk with metadata"""
        self.chunk_counter += 1
        
        return StreamingChunk(
            text=text.strip(),
            chunk_id=f"chunk_{self.chunk_counter}",
            priority=1,
            prosody_pause=0.2 if is_sentence_end else 0.1,
            is_sentence_end=is_sentence_end,
            is_paragraph_end=is_paragraph_end
        )
    
    def _split_long_sentence(self, sentence: str, max_chunk_size: int) -> List[StreamingChunk]:
        """Split a long sentence into smaller chunks at natural break points"""
        chunks = []
        
        # Try to split by commas and conjunctions
        break_patterns = [
            r',\s+',          # Commas
            r'\s+and\s+',     # And conjunctions
            r'\s+but\s+',     # But conjunctions  
            r'\s+or\s+',      # Or conjunctions
            r'\s+so\s+',      # So conjunctions
            r'\s+because\s+', # Because clauses
            r'\s+when\s+',    # When clauses
            r'\s+where\s+',   # Where clauses
            r'\s+which\s+',   # Which clauses
            r'\s+that\s+',    # That clauses
        ]
        
        current_text = sentence
        
        for pattern in break_patterns:
            if len(current_text) <= max_chunk_size:
                break
                
            parts = re.split(pattern, current_text, maxsplit=1)
            if len(parts) > 1:
                first_part = parts[0].strip()
                remaining = parts[1].strip()
                
                if first_part and len(first_part) <= max_chunk_size:
                    chunk = self._create_chunk(first_part)
                    chunks.append(chunk)
                    current_text = remaining
                    break
        
        # If still too long, split by words
        if len(current_text) > max_chunk_size:
            words = current_text.split()
            current_chunk_words = []
            
            for word in words:
                current_chunk_words.append(word)
                current_length = len(' '.join(current_chunk_words))
                
                if current_length >= max_chunk_size and len(current_chunk_words) > 1:
                    # Remove the last word and create chunk
                    current_chunk_words.pop()
                    chunk_text = ' '.join(current_chunk_words)
                    chunk = self._create_chunk(chunk_text)
                    chunks.append(chunk)
                    current_chunk_words = [word]
            
            # Add remaining words
            if current_chunk_words:
                chunk_text = ' '.join(current_chunk_words)
                chunk = self._create_chunk(chunk_text, is_sentence_end=True)
                chunks.append(chunk)
        else:
            # Add the remaining text as final chunk
            if current_text:
                chunk = self._create_chunk(current_text, is_sentence_end=True)
                chunks.append(chunk)
        
        return chunks
    
    def optimize_for_kokoro(self, chunks: List[StreamingChunk]) -> List[StreamingChunk]:
        """Optimize chunks specifically for Kokoro TTS"""
        if not chunks:
            return chunks
            
        optimized = []
        
        for chunk in chunks:
            # Clean up text for better TTS
            text = chunk.text
            
            # Remove excessive punctuation
            text = re.sub(r'[.]{2,}', '.', text)
            text = re.sub(r'[!]{2,}', '!', text)
            text = re.sub(r'[?]{2,}', '?', text)
            
            # Normalize spacing
            text = re.sub(r'\s+', ' ', text)
            text = text.strip()
            
            if text:
                optimized_chunk = StreamingChunk(
                    text=text,
                    chunk_id=chunk.chunk_id,
                    priority=chunk.priority,
                    prosody_pause=chunk.prosody_pause,
                    is_sentence_end=chunk.is_sentence_end,
                    is_paragraph_end=chunk.is_paragraph_end
                )
                optimized.append(optimized_chunk)
        
        if DEBUG:
            print(f"[KyutaiCoordinator] Optimized {len(optimized)} chunks for Kokoro")
            
        return optimized

# Global coordinator instance
_kyutai_coordinator = None

def get_kyutai_coordinator() -> KyutaiCoordinator:
    """Get the global Kyutai coordinator instance"""
    global _kyutai_coordinator
    if _kyutai_coordinator is None:
        _kyutai_coordinator = KyutaiCoordinator()
    return _kyutai_coordinator