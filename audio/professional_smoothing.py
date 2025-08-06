# audio/professional_smoothing.py - Professional Audio Smoothing for Buddy's Voice
"""
Professional-grade audio smoothing system for seamless voice chunk transitions.
Implements Hann window-based crossfading, zero-gap playback, and professional audio quality.

Features:
- Hann window crossfading for smooth transitions between chunks
- Perfect sample alignment to eliminate clicks/pops
- Short fade-in/fade-out at chunk edges (~11ms at 44.1kHz)
- Zero-gap sequential playback without overlap
- Professional studio-quality output
"""

import math
import array
import threading
import time
import queue
from typing import List, Tuple, Optional, Union
from dataclasses import dataclass
import wave
import struct

# Professional audio configuration
CROSSFADE_SAMPLES = 512  # ~11ms at 44.1kHz, ~32ms at 16kHz
FADE_SAMPLES = 256       # Short fade for click elimination
DEFAULT_SAMPLE_RATE = 44100
DEFAULT_CHANNELS = 1
DEFAULT_SAMPLE_WIDTH = 2  # 16-bit

@dataclass
class AudioChunk:
    """Professional audio chunk with metadata for seamless playback"""
    data: array.array          # Audio samples as array
    sample_rate: int           # Sample rate (Hz)
    channels: int              # Number of channels
    sample_width: int          # Bytes per sample
    chunk_id: str              # Unique identifier
    timestamp: float           # Creation timestamp
    crossfade_enabled: bool = True
    fade_in: bool = False
    fade_out: bool = False

class HannWindow:
    """Pure Python implementation of Hann window for professional crossfading"""
    
    @staticmethod
    def generate(length: int) -> List[float]:
        """Generate Hann window coefficients"""
        if length <= 1:
            return [1.0]
        
        window = []
        for n in range(length):
            # Hann window formula: 0.5 * (1 - cos(2π * n / (N-1)))
            coefficient = 0.5 * (1.0 - math.cos(2.0 * math.pi * n / (length - 1)))
            window.append(coefficient)
        
        return window
    
    @staticmethod
    def apply_fade_in(samples: array.array, fade_length: int) -> array.array:
        """Apply Hann window fade-in to audio samples"""
        if fade_length <= 0 or len(samples) == 0:
            return samples
        
        fade_length = min(fade_length, len(samples))
        window = HannWindow.generate(fade_length * 2)  # Use first half for fade-in
        
        result = array.array(samples.typecode, samples)
        for i in range(fade_length):
            result[i] = int(samples[i] * window[i])
        
        return result
    
    @staticmethod
    def apply_fade_out(samples: array.array, fade_length: int) -> array.array:
        """Apply Hann window fade-out to audio samples"""
        if fade_length <= 0 or len(samples) == 0:
            return samples
        
        fade_length = min(fade_length, len(samples))
        window = HannWindow.generate(fade_length * 2)  # Use second half for fade-out
        
        result = array.array(samples.typecode, samples)
        start_idx = len(samples) - fade_length
        
        for i in range(fade_length):
            window_idx = fade_length + i  # Second half of window (fade-out)
            result[start_idx + i] = int(samples[start_idx + i] * window[window_idx])
        
        return result

class ProfessionalAudioSmoother:
    """Professional audio smoothing system for seamless chunk transitions"""
    
    def __init__(self, crossfade_samples: int = CROSSFADE_SAMPLES):
        self.crossfade_samples = crossfade_samples
        self.previous_chunk: Optional[AudioChunk] = None
        self.lock = threading.Lock()
        self.stats = {
            'chunks_processed': 0,
            'crossfades_applied': 0,
            'fade_ins_applied': 0,
            'fade_outs_applied': 0,
            'total_processing_time': 0.0
        }
    
    def smooth_chunk(self, chunk: AudioChunk, is_first: bool = False, is_last: bool = False) -> AudioChunk:
        """Apply professional smoothing to an audio chunk"""
        start_time = time.time()
        
        with self.lock:
            try:
                # Create a copy for processing
                smoothed_chunk = self._copy_chunk(chunk)
                
                # Apply fade-in for first chunk or if requested
                if is_first or chunk.fade_in:
                    smoothed_chunk.data = HannWindow.apply_fade_in(
                        smoothed_chunk.data, FADE_SAMPLES
                    )
                    self.stats['fade_ins_applied'] += 1
                
                # Apply fade-out for last chunk or if requested
                if is_last or chunk.fade_out:
                    smoothed_chunk.data = HannWindow.apply_fade_out(
                        smoothed_chunk.data, FADE_SAMPLES
                    )
                    self.stats['fade_outs_applied'] += 1
                
                # Apply crossfade with previous chunk if available
                if (self.previous_chunk is not None and 
                    chunk.crossfade_enabled and 
                    not is_first):
                    smoothed_chunk = self._apply_crossfade(smoothed_chunk)
                    self.stats['crossfades_applied'] += 1
                
                # Store for next crossfade
                self.previous_chunk = self._copy_chunk(smoothed_chunk)
                
                # Update statistics
                self.stats['chunks_processed'] += 1
                self.stats['total_processing_time'] += time.time() - start_time
                
                return smoothed_chunk
                
            except Exception as e:
                print(f"[AudioSmoother] ❌ Error smoothing chunk {chunk.chunk_id}: {e}")
                return chunk
    
    def _apply_crossfade(self, current_chunk: AudioChunk) -> AudioChunk:
        """Apply professional crossfade between previous and current chunk"""
        if self.previous_chunk is None:
            return current_chunk
        
        try:
            # Ensure compatibility
            if not self._chunks_compatible(self.previous_chunk, current_chunk):
                print(f"[AudioSmoother] ⚠️ Incompatible chunks for crossfade, skipping")
                return current_chunk
            
            # Calculate crossfade region
            prev_data = self.previous_chunk.data
            curr_data = current_chunk.data
            
            crossfade_len = min(
                self.crossfade_samples,
                len(prev_data),
                len(curr_data)
            )
            
            if crossfade_len <= 0:
                return current_chunk
            
            # Generate crossfade windows
            fade_out_window = HannWindow.generate(crossfade_len * 2)[crossfade_len:]  # Second half
            fade_in_window = HannWindow.generate(crossfade_len * 2)[:crossfade_len]   # First half
            
            # Create crossfaded audio
            crossfaded_data = array.array(curr_data.typecode)
            
            # Copy non-crossfade portion of current chunk
            if len(curr_data) > crossfade_len:
                crossfaded_data.extend(curr_data[crossfade_len:])
            
            # Apply crossfade at the beginning
            for i in range(crossfade_len):
                prev_sample = prev_data[-(crossfade_len - i)] if i < len(prev_data) else 0
                curr_sample = curr_data[i] if i < len(curr_data) else 0
                
                # Apply crossfade windows
                faded_prev = int(prev_sample * fade_out_window[i])
                faded_curr = int(curr_sample * fade_in_window[i])
                
                # Mix the samples
                mixed_sample = faded_prev + faded_curr
                
                # Prevent clipping
                mixed_sample = max(-32768, min(32767, mixed_sample))
                
                crossfaded_data.insert(i, mixed_sample)
            
            # Create new chunk with crossfaded data
            result_chunk = self._copy_chunk(current_chunk)
            result_chunk.data = crossfaded_data
            
            return result_chunk
            
        except Exception as e:
            print(f"[AudioSmoother] ❌ Crossfade error: {e}")
            return current_chunk
    
    def _chunks_compatible(self, chunk1: AudioChunk, chunk2: AudioChunk) -> bool:
        """Check if two chunks are compatible for crossfading"""
        return (chunk1.sample_rate == chunk2.sample_rate and
                chunk1.channels == chunk2.channels and
                chunk1.sample_width == chunk2.sample_width)
    
    def _copy_chunk(self, chunk: AudioChunk) -> AudioChunk:
        """Create a deep copy of an audio chunk"""
        return AudioChunk(
            data=array.array(chunk.data.typecode, chunk.data),
            sample_rate=chunk.sample_rate,
            channels=chunk.channels,
            sample_width=chunk.sample_width,
            chunk_id=chunk.chunk_id,
            timestamp=chunk.timestamp,
            crossfade_enabled=chunk.crossfade_enabled,
            fade_in=chunk.fade_in,
            fade_out=chunk.fade_out
        )
    
    def reset(self):
        """Reset the smoother state"""
        with self.lock:
            self.previous_chunk = None
    
    def get_stats(self) -> dict:
        """Get smoothing statistics"""
        with self.lock:
            return self.stats.copy()

class ProfessionalAudioQueue:
    """Enhanced thread-safe audio queue with professional error handling"""
    
    def __init__(self, maxsize: int = 50):
        self.queue = queue.Queue(maxsize=maxsize)
        self.smoother = ProfessionalAudioSmoother()
        self.lock = threading.Lock()
        self.total_chunks = 0
        self.dropped_chunks = 0
        self.processing_errors = 0
        
    def put_raw_audio(self, audio_data: Union[bytes, array.array], 
                     sample_rate: int = DEFAULT_SAMPLE_RATE,
                     channels: int = DEFAULT_CHANNELS,
                     sample_width: int = DEFAULT_SAMPLE_WIDTH,
                     chunk_id: str = None,
                     crossfade_enabled: bool = True,
                     is_first: bool = False,
                     is_last: bool = False) -> bool:
        """Add raw audio data to queue with professional smoothing"""
        try:
            # Convert audio data to array if needed
            if isinstance(audio_data, bytes):
                if sample_width == 2:
                    audio_array = array.array('h')  # signed short
                    for i in range(0, len(audio_data), 2):
                        if i + 1 < len(audio_data):
                            sample = struct.unpack('<h', audio_data[i:i+2])[0]
                            audio_array.append(sample)
                else:
                    print(f"[AudioQueue] ⚠️ Unsupported sample width: {sample_width}")
                    return False
            elif isinstance(audio_data, array.array):
                # Already an array, use directly
                audio_array = audio_data
            elif hasattr(audio_data, 'tobytes'):  # numpy array
                audio_array = array.array('h', audio_data.astype('int16'))
            elif isinstance(audio_data, (list, tuple)):
                audio_array = array.array('h', audio_data)
            else:
                print(f"[AudioQueue] ⚠️ Unsupported audio data type: {type(audio_data)}")
                return False
            
            # Create chunk
            chunk = AudioChunk(
                data=audio_array,
                sample_rate=sample_rate,
                channels=channels,
                sample_width=sample_width,
                chunk_id=chunk_id or f"chunk_{self.total_chunks}",
                timestamp=time.time(),
                crossfade_enabled=crossfade_enabled,
                fade_in=is_first,
                fade_out=is_last
            )
            
            # Apply professional smoothing
            smoothed_chunk = self.smoother.smooth_chunk(chunk, is_first, is_last)
            
            # Add to queue
            try:
                self.queue.put(smoothed_chunk, block=False)
                self.total_chunks += 1
                return True
            except queue.Full:
                print(f"[AudioQueue] ⚠️ Queue full, dropping chunk {chunk.chunk_id}")
                self.dropped_chunks += 1
                return False
                
        except Exception as e:
            print(f"[AudioQueue] ❌ Error adding audio: {e}")
            self.processing_errors += 1
            return False
    
    def get(self, timeout: float = None) -> Optional[AudioChunk]:
        """Get next smoothed audio chunk"""
        try:
            return self.queue.get(timeout=timeout)
        except queue.Empty:
            return None
    
    def task_done(self):
        """Mark a queue task as done"""
        self.queue.task_done()
    
    def qsize(self) -> int:
        """Get current queue size"""
        return self.queue.qsize()
    
    def empty(self) -> bool:
        """Check if queue is empty"""
        return self.queue.empty()
    
    def clear(self) -> int:
        """Clear all pending items and return count cleared"""
        cleared = 0
        while not self.queue.empty():
            try:
                self.queue.get_nowait()
                self.queue.task_done()
                cleared += 1
            except queue.Empty:
                break
        
        # Reset smoother state
        self.smoother.reset()
        return cleared
    
    def get_stats(self) -> dict:
        """Get comprehensive queue statistics"""
        smoother_stats = self.smoother.get_stats()
        return {
            'queue_size': self.qsize(),
            'total_chunks': self.total_chunks,
            'dropped_chunks': self.dropped_chunks,
            'processing_errors': self.processing_errors,
            'smoother_stats': smoother_stats
        }

# Global professional audio queue
_professional_audio_queue = None

def get_professional_audio_queue() -> ProfessionalAudioQueue:
    """Get the global professional audio queue"""
    global _professional_audio_queue
    if _professional_audio_queue is None:
        _professional_audio_queue = ProfessionalAudioQueue()
    return _professional_audio_queue

def apply_volume_normalization(chunk: AudioChunk, target_rms: float = 0.1) -> AudioChunk:
    """Apply professional volume normalization to maintain consistent levels"""
    try:
        if len(chunk.data) == 0:
            return chunk
        
        # Calculate RMS (Root Mean Square) for current volume level
        sum_squares = sum(sample * sample for sample in chunk.data)
        rms = math.sqrt(sum_squares / len(chunk.data))
        
        if rms < 1e-6:  # Avoid division by zero for silent audio
            return chunk
        
        # Calculate normalization factor
        normalization_factor = (target_rms * 32767) / rms
        
        # Limit factor to prevent extreme amplification
        normalization_factor = min(normalization_factor, 4.0)
        normalization_factor = max(normalization_factor, 0.1)
        
        # Apply normalization
        normalized_data = array.array(chunk.data.typecode)
        for sample in chunk.data:
            normalized_sample = int(sample * normalization_factor)
            # Prevent clipping
            normalized_sample = max(-32768, min(32767, normalized_sample))
            normalized_data.append(normalized_sample)
        
        # Create new chunk with normalized data
        result_chunk = AudioChunk(
            data=normalized_data,
            sample_rate=chunk.sample_rate,
            channels=chunk.channels,
            sample_width=chunk.sample_width,
            chunk_id=chunk.chunk_id,
            timestamp=chunk.timestamp,
            crossfade_enabled=chunk.crossfade_enabled,
            fade_in=chunk.fade_in,
            fade_out=chunk.fade_out
        )
        
        return result_chunk
        
    except Exception as e:
        print(f"[AudioNormalizer] ❌ Error normalizing chunk {chunk.chunk_id}: {e}")
        return chunk

def convert_chunk_to_playable(chunk: AudioChunk) -> bytes:
    """Convert professional audio chunk to playable bytes for simpleaudio"""
    try:
        # Convert array to bytes for playback
        return chunk.data.tobytes()
    except Exception as e:
        print(f"[AudioConverter] ❌ Error converting chunk {chunk.chunk_id}: {e}")
        return b''

# Professional audio processing pipeline
def process_audio_chunk_professionally(audio_data: Union[bytes, array.array], 
                                     sample_rate: int = DEFAULT_SAMPLE_RATE,
                                     chunk_id: str = None,
                                     apply_normalization: bool = True,
                                     crossfade_enabled: bool = True,
                                     is_first: bool = False,
                                     is_last: bool = False) -> bytes:
    """Complete professional audio processing pipeline"""
    try:
        # Get professional queue
        prof_queue = get_professional_audio_queue()
        
        # Add to professional queue with smoothing
        success = prof_queue.put_raw_audio(
            audio_data=audio_data,
            sample_rate=sample_rate,
            chunk_id=chunk_id,
            crossfade_enabled=crossfade_enabled,
            is_first=is_first,
            is_last=is_last
        )
        
        if not success:
            print(f"[AudioProcessor] ❌ Failed to queue chunk {chunk_id}")
            # Return original data as fallback
            if isinstance(audio_data, bytes):
                return audio_data
            elif hasattr(audio_data, 'tobytes'):
                return audio_data.tobytes()
            elif isinstance(audio_data, array.array):
                return audio_data.tobytes()
            else:
                return bytes()
        
        # Get processed chunk
        processed_chunk = prof_queue.get(timeout=1.0)
        if processed_chunk is None:
            print(f"[AudioProcessor] ❌ Failed to get processed chunk {chunk_id}")
            # Return original data as fallback
            if isinstance(audio_data, bytes):
                return audio_data
            elif hasattr(audio_data, 'tobytes'):
                return audio_data.tobytes()
            elif isinstance(audio_data, array.array):
                return audio_data.tobytes()
            else:
                return bytes()
        
        # Apply volume normalization if requested
        if apply_normalization:
            processed_chunk = apply_volume_normalization(processed_chunk)
        
        # Convert to playable format
        playable_audio = convert_chunk_to_playable(processed_chunk)
        
        # Mark task as done
        prof_queue.task_done()
        
        return playable_audio
        
    except Exception as e:
        print(f"[AudioProcessor] ❌ Error in professional processing: {e}")
        # Return original data as fallback
        if isinstance(audio_data, bytes):
            return audio_data
        elif hasattr(audio_data, 'tobytes'):
            return audio_data.tobytes()
        elif isinstance(audio_data, array.array):
            return audio_data.tobytes()
        else:
            return bytes()