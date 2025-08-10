# audio/output.py - ENHANCED with Professional Audio Smoothing
# Date: 2025-01-08 06:23:11 (UTC) - PROFESSIONAL AUDIO SMOOTHING
# FEATURES: Hann window crossfading, zero-gap playback, professional quality

import threading
import time
import queue
import array
import struct

# ✅ Professional audio smoothing system
from audio.professional_smoothing import (
    get_professional_audio_queue, 
    process_audio_chunk_professionally,
    ProfessionalAudioQueue,
    AudioChunk,
    apply_volume_normalization,
    convert_chunk_to_playable
)

# ✅ FIX: Make simpleaudio import optional
try:
    import simpleaudio as sa
    SIMPLEAUDIO_AVAILABLE = True
    print("[AudioOutput] ✅ simpleaudio available with professional smoothing")
except ImportError:
    print("[AudioOutput] ⚠️ simpleaudio not available - audio playback disabled")
    SIMPLEAUDIO_AVAILABLE = False

# ✅ FIX: Make numpy import optional - use professional smoothing instead
try:
    import numpy as np
    NUMPY_AVAILABLE = True
    print("[AudioOutput] ✅ numpy available for enhanced processing")
except ImportError:
    print("[AudioOutput] ℹ️ numpy not available - using pure Python professional smoothing")
    NUMPY_AVAILABLE = False

import requests
import io
import tempfile
import os
from langdetect import detect
from config import *

# Global audio state with professional enhancement
audio_queue = queue.Queue()
professional_audio_queue = get_professional_audio_queue()  # ✅ NEW: Professional queue
current_audio_playback = None
audio_lock = threading.Lock()
buddy_talking = threading.Event()
playback_start_time = None
chunk_sequence_number = 0  # ✅ NEW: Track chunk sequence for seamless playback

# ✅ NEW: Streaming response tracking
from audio.streaming_response_manager import get_streaming_manager
streaming_manager = get_streaming_manager()
current_response_id = None

# ✅ NEW: Kokoro-FastAPI configuration
KOKORO_API_BASE_URL = getattr(globals(), 'KOKORO_API_BASE_URL', "http://127.0.0.1:8880")
KOKORO_API_TIMEOUT = getattr(globals(), 'KOKORO_API_TIMEOUT', 10)
KOKORO_DEFAULT_VOICE = getattr(globals(), 'KOKORO_DEFAULT_VOICE', "af_heart")

# Voice mapping for different languages
KOKORO_API_VOICES = {
    "en": "af_heart",      # Australian female
    "en-us": "am_adam",    # American male  
    "en-gb": "bf_emma",    # British female
    "es": "es_maria",      # Spanish female
    "fr": "fr_pierre",     # French male
    "de": "de_anna",       # German female
    "it": "it_marco",      # Italian male
    "pt": "pt_sofia",      # Portuguese female
    "ja": "ja_yuki",       # Japanese female
    "ko": "ko_minho",      # Korean male
    "zh": "zh_mei",        # Chinese female
}

# Initialize Kokoro-FastAPI connection
kokoro_api_available = False
kokoro_session = None  # ✅ NEW: Persistent HTTP session for connection reuse

def get_kokoro_session():
    """Get or create a persistent HTTP session for Kokoro API"""
    global kokoro_session
    if kokoro_session is None:
        kokoro_session = requests.Session()
        # Set session defaults for better connection management
        kokoro_session.headers.update({
            'Content-Type': 'application/json',
            'Connection': 'keep-alive'
        })
        # Configure connection pooling
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=1,
            pool_maxsize=5,
            max_retries=1
        )
        kokoro_session.mount('http://', adapter)
        kokoro_session.mount('https://', adapter)
    return kokoro_session

def test_kokoro_api():
    """Test if Kokoro-FastAPI is available"""
    global kokoro_api_available
    try:
        session = get_kokoro_session()
        response = session.get(f"{KOKORO_API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            kokoro_api_available = True
            print(f"[Buddy V2] ✅ Kokoro-FastAPI connected at {KOKORO_API_BASE_URL}")
            return True
    except Exception as e:
        print(f"[Buddy V2] ❌ Kokoro-FastAPI not available: {e}")
        print(f"[Buddy V2] 💡 Make sure Kokoro-FastAPI is running on {KOKORO_API_BASE_URL}")
    
    kokoro_api_available = False
    return False

def generate_tts(text, lang=DEFAULT_LANG):
    """Generate TTS audio using Kokoro-FastAPI with professional smoothing"""
    try:
        if not kokoro_api_available:
            if not test_kokoro_api():
                return None, None
            
        # Detect language and select voice
        detected_lang = lang or detect(text)
        voice = KOKORO_API_VOICES.get(detected_lang, KOKORO_DEFAULT_VOICE)
        
        # Prepare API request
        payload = {
            "input": text.strip(),
            "voice": voice,
            "response_format": "wav"
        }
        
        result = {}

        def _request():
            session = get_kokoro_session()
            try:
                result['response'] = session.post(
                    f"{KOKORO_API_BASE_URL}/v1/audio/speech",
                    json=payload,
                    timeout=(3.0, 8.0)
                )
            except requests.RequestException as e:
                result['error'] = e

        thread = threading.Thread(target=_request, daemon=True)
        thread.start()
        thread.join()

        if 'error' in result:
            print("[TTS] timeout: falling back to text-only")
            return None, None

        response = result.get('response')
        
        if response.status_code == 200:
            # Save audio to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
                temp_file.write(response.content)
                temp_path = temp_file.name
            
            # Load audio data for processing
            import wave
            with wave.open(temp_path, 'rb') as wav_file:
                frames = wav_file.readframes(wav_file.getnframes())
                sample_rate = wav_file.getframerate()
                channels = wav_file.getnchannels()
                sample_width = wav_file.getsampwidth()
            
            # ✅ ENHANCED: Professional audio processing
            if NUMPY_AVAILABLE:
                # Convert to numpy array if available
                if sample_width == 2:
                    audio_data = np.frombuffer(frames, dtype=np.int16)
                else:
                    audio_data = np.frombuffer(frames, dtype=np.uint8)
                    audio_data = ((audio_data.astype(np.int16) - 128) * 256)
                
                # Handle stereo to mono conversion
                if channels == 2:
                    audio_data = audio_data.reshape(-1, 2)
                    audio_data = audio_data[:, 0]  # Take left channel
                
                # Resample if needed
                if sample_rate != SAMPLE_RATE:
                    try:
                        from scipy.signal import resample_poly
                        audio_data = resample_poly(audio_data, SAMPLE_RATE, sample_rate)
                        audio_data = audio_data.astype(np.int16)
                    except ImportError:
                        print("[AudioOutput] ⚠️ scipy not available, using original sample rate")
                        pass
                
                # Convert to array for professional processing
                audio_array = array.array('h', audio_data)
            else:
                # ✅ NEW: Pure Python audio processing for professional smoothing
                if sample_width == 2:
                    audio_array = array.array('h')
                    for i in range(0, len(frames), 2):
                        if i + 1 < len(frames):
                            sample = struct.unpack('<h', frames[i:i+2])[0]
                            audio_array.append(sample)
                else:
                    # Convert 8-bit to 16-bit
                    audio_array = array.array('h')
                    for byte in frames:
                        sample = (byte - 128) * 256  # Convert to 16-bit
                        audio_array.append(sample)
                
                # Handle stereo to mono for pure Python
                if channels == 2:
                    mono_array = array.array('h')
                    for i in range(0, len(audio_array), 2):
                        if i + 1 < len(audio_array):
                            mono_array.append(audio_array[i])  # Take left channel
                    audio_array = mono_array
            
            # Clean up temp file
            try:
                os.unlink(temp_path)
            except:
                pass
            
            if DEBUG:
                print(f"[Buddy V2] 🗣️ Generated TTS via FastAPI: {len(audio_array)} samples, voice: {voice}")
                print(f"[Buddy V2] 🎵 Professional smoothing ready for seamless playback")
            
            return audio_array, sample_rate
            
        else:
            print(f"[Buddy V2] ❌ Kokoro-FastAPI error: {response.status_code}")
            if response.text:
                print(f"[Buddy V2] Error details: {response.text}")
            return None, None
            
    except Exception as e:
        print(f"[Buddy V2] TTS error: {e}")
        return None, None

def speak_async(text, lang=DEFAULT_LANG, use_professional_smoothing=True):
    """Queue text for speech synthesis with optional professional smoothing"""
    if not text or len(text.strip()) < 2:
        return
        
    def tts_worker():
        audio_data, sr = generate_tts(text.strip(), lang)
        if audio_data is not None:
            if use_professional_smoothing:
                # ✅ NEW: Use professional smoothing for seamless playback
                global chunk_sequence_number
                chunk_sequence_number += 1
                
                # Apply professional processing
                processed_audio = process_audio_chunk_professionally(
                    audio_data=audio_data,
                    sample_rate=sr,
                    chunk_id=f"async_{chunk_sequence_number}",
                    apply_normalization=True,
                    crossfade_enabled=True,
                    is_first=(chunk_sequence_number == 1),
                    is_last=True  # Single chunk, so it's also last
                )
                
                # Queue the professionally processed audio
                audio_queue.put((processed_audio, sr, None))
            else:
                # Legacy behavior
                audio_data_bytes = audio_data.tobytes() if hasattr(audio_data, 'tobytes') else bytes(audio_data)
                audio_queue.put((audio_data_bytes, sr))
    
    threading.Thread(target=tts_worker, daemon=True).start()

def speak_streaming(text, voice=None, lang=DEFAULT_LANG, response_id=None, use_professional_smoothing=True):
    """✅ ENHANCED: Queue text chunk for professional streaming TTS with seamless transitions"""
    global current_response_id, chunk_sequence_number
    
    if not text or len(text.strip()) < 2:
        return False
        
    def streaming_tts_worker():
        try:
            if not kokoro_api_available:
                if not test_kokoro_api():
                    return False
            
            # ✅ FIX: Track this chunk in the streaming manager
            if response_id and streaming_manager.is_response_active(response_id):
                streaming_manager.add_chunk(response_id)
            
            # ✅ FIX: Properly handle voice parameter
            selected_voice = voice  # Use provided voice
            if selected_voice is None:
                # Detect voice from language if none provided
                detected_lang = lang or detect(text)
                selected_voice = KOKORO_API_VOICES.get(detected_lang, KOKORO_DEFAULT_VOICE)
            
            # ✅ NEW: Use persistent session for connection reuse
            payload = {
                "input": text.strip(),
                "voice": selected_voice,
                "response_format": "wav"
            }
            
            session = get_kokoro_session()
            response = session.post(
                f"{KOKORO_API_BASE_URL}/v1/audio/speech",
                json=payload,
                timeout=5  # Shorter timeout for streaming
            )
            
            if response.status_code == 200:
                # Process audio quickly for streaming
                with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
                    temp_file.write(response.content)
                    temp_path = temp_file.name
                
                import wave
                with wave.open(temp_path, 'rb') as wav_file:
                    frames = wav_file.readframes(wav_file.getnframes())
                    sample_rate = wav_file.getframerate()
                    channels = wav_file.getnchannels()
                    sample_width = wav_file.getsampwidth()
                
                # ✅ ENHANCED: Professional audio processing for streaming
                if use_professional_smoothing:
                    # Increment chunk sequence for seamless tracking
                    chunk_sequence_number += 1
                    
                    # Convert frames to audio array for professional processing
                    if NUMPY_AVAILABLE:
                        if sample_width == 2:
                            audio_data = np.frombuffer(frames, dtype=np.int16)
                        else:
                            audio_data = np.frombuffer(frames, dtype=np.uint8)
                            audio_data = ((audio_data.astype(np.int16) - 128) * 256)
                        
                        if channels == 2:
                            audio_data = audio_data.reshape(-1, 2)[:, 0]
                        
                        audio_array = array.array('h', audio_data)
                    else:
                        # Pure Python conversion
                        if sample_width == 2:
                            audio_array = array.array('h')
                            for i in range(0, len(frames), 2):
                                if i + 1 < len(frames):
                                    sample = struct.unpack('<h', frames[i:i+2])[0]
                                    audio_array.append(sample)
                        else:
                            audio_array = array.array('h')
                            for byte in frames:
                                sample = (byte - 128) * 256
                                audio_array.append(sample)
                        
                        # Handle stereo to mono
                        if channels == 2:
                            mono_array = array.array('h')
                            for i in range(0, len(audio_array), 2):
                                if i + 1 < len(audio_array):
                                    mono_array.append(audio_array[i])
                            audio_array = mono_array
                    
                    # ✅ NEW: Professional processing with seamless transitions
                    # Determine if this is first or last chunk in sequence
                    is_first_chunk = (chunk_sequence_number == 1)
                    # Note: We can't easily determine if it's the last chunk in streaming,
                    # so we'll let the completion handler manage that
                    
                    processed_audio = process_audio_chunk_professionally(
                        audio_data=audio_array,
                        sample_rate=sample_rate,
                        chunk_id=f"stream_{response_id}_{chunk_sequence_number}",
                        apply_normalization=True,
                        crossfade_enabled=True,
                        is_first=is_first_chunk,
                        is_last=False  # Will be handled by completion
                    )
                    
                    # ✅ FIX: Queue professionally processed audio with response tracking
                    audio_queue.put((processed_audio, sample_rate, response_id))
                else:
                    # Legacy processing for compatibility
                    if sample_width == 2:
                        audio_data = array.array('h')
                        for i in range(0, len(frames), 2):
                            if i + 1 < len(frames):
                                sample = struct.unpack('<h', frames[i:i+2])[0]
                                audio_data.append(sample)
                    else:
                        audio_data = array.array('h')
                        for byte in frames:
                            sample = (byte - 128) * 256
                            audio_data.append(sample)
                    
                    if channels == 2:
                        mono_array = array.array('h')
                        for i in range(0, len(audio_data), 2):
                            if i + 1 < len(audio_data):
                                mono_array.append(audio_data[i])
                        audio_data = mono_array
                    
                    audio_queue.put((audio_data.tobytes(), sample_rate, response_id))
                
                # Cleanup
                try:
                    os.unlink(temp_path)
                except:
                    pass
                
                if DEBUG:
                    chunk_info = f"'{text[:50]}...'" if len(text) > 50 else f"'{text}'"
                    smoothing_status = "with professional smoothing" if use_professional_smoothing else "legacy mode"
                    print(f"[StreamingTTS] ✅ Queued chunk: {chunk_info} {smoothing_status}")
                    print(f"[StreamingTTS] 🎵 Voice: {selected_voice}, Chunk #{chunk_sequence_number}")
                    if response_id:
                        print(f"[StreamingTTS] 📊 Response: {response_id}")
                
                return True
            else:
                print(f"[StreamingTTS] ❌ API Error {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"[StreamingTTS] ❌ Error: {e}")
        
        return False
    
    threading.Thread(target=streaming_tts_worker, daemon=True).start()
    return True

def play_chime():
    """Play notification chime with fallback for missing chime.wav"""
    try:
        # Check if chime file exists first
        if not os.path.exists(CHIME_PATH):
            # Create a simple synthetic chime if file is missing
            _create_fallback_chime()
        
        from pydub import AudioSegment
        from audio.processing import downsample_audio
        
        audio = AudioSegment.from_wav(CHIME_PATH)
        samples = np.array(audio.get_array_of_samples(), dtype=np.int16)
        
        if audio.channels == 2:
            samples = samples.reshape((-1, 2))
            samples = samples[:, 0]
        
        if audio.frame_rate != SAMPLE_RATE:
            samples = downsample_audio(samples, audio.frame_rate, SAMPLE_RATE)
        
        audio_queue.put((samples, SAMPLE_RATE))
    except Exception as e:
        if DEBUG:
            print(f"[Buddy V2] Chime error: {e}")
        # Fallback: Generate simple beep programmatically
        _generate_simple_beep()

def _create_fallback_chime():
    """Create a simple fallback chime.wav file if missing"""
    try:
        import numpy as np
        from scipy.io.wavfile import write
        
        # Generate a simple 800Hz tone for 0.3 seconds
        sample_rate = 44100
        duration = 0.3
        frequency = 800
        
        t = np.linspace(0, duration, int(sample_rate * duration))
        # Create a simple chime with fade in/out
        tone = np.sin(2 * np.pi * frequency * t) * np.exp(-t * 3)  # Exponential decay
        tone = (tone * 32767 * 0.3).astype(np.int16)  # Convert to 16-bit, reduce volume
        
        write(CHIME_PATH, sample_rate, tone)
        print(f"[Audio] ✅ Created fallback chime.wav at {CHIME_PATH}")
        
    except Exception as e:
        print(f"[Audio] ⚠️ Could not create fallback chime: {e}")

def _generate_simple_beep():
    """Generate a simple beep directly to audio queue as final fallback"""
    try:
        # Generate a simple 600Hz beep for 0.2 seconds
        duration = 0.2
        frequency = 600
        
        t = np.linspace(0, duration, int(SAMPLE_RATE * duration))
        beep = np.sin(2 * np.pi * frequency * t) * 0.2  # Low volume
        beep = (beep * 32767).astype(np.int16)
        
        audio_queue.put((beep, SAMPLE_RATE))
        if DEBUG:
            print("[Audio] 🔔 Generated fallback beep")
            
    except Exception as e:
        if DEBUG:
            print(f"[Audio] ⚠️ Could not generate fallback beep: {e}")

def notify_full_duplex_manager_speaking(audio_data):
    """✅ SIMPLE: Notify for audio chunk"""
    try:
        if FULL_DUPLEX_MODE:
            from audio.full_duplex_manager import full_duplex_manager
            if full_duplex_manager and hasattr(full_duplex_manager, 'notify_buddy_speaking'):
                full_duplex_manager.notify_buddy_speaking(audio_data)
                print("[Audio] 🤖 ✅ NOTIFIED: Buddy speaking")
    except Exception as e:
        print(f"[Audio] ❌ Error notifying speaking start: {e}")

def notify_full_duplex_manager_stopped():
    """✅ SIMPLE: Notify when audio stops"""
    try:
        if FULL_DUPLEX_MODE:
            from audio.full_duplex_manager import full_duplex_manager
            if full_duplex_manager and hasattr(full_duplex_manager, 'notify_buddy_stopped_speaking'):
                full_duplex_manager.notify_buddy_stopped_speaking()
                print("[Audio] 🤖 ✅ NOTIFIED: Buddy stopped")
                
                # Clear AEC reference
                from audio.smart_aec import smart_aec
                smart_aec.clear_reference()
                print("[Audio] 🧹 Cleared AEC reference")
    except Exception as e:
        print(f"[Audio] ❌ Error notifying speaking stop: {e}")

def audio_worker():
    """✅ ENHANCED: Audio worker with professional smoothing and seamless transitions"""
    global current_audio_playback, playback_start_time
    
    print(f"[Buddy V2] 🎵 Enhanced Audio Worker started with professional smoothing")
    
    while True:
        try:
            item = audio_queue.get(timeout=0.1)
            if item is None:
                break
            
            # ✅ ENHANCED: Handle both new professional format and legacy format
            if len(item) == 3:
                audio_data, sr, response_id = item
            else:
                # Legacy format for backward compatibility
                audio_data, sr = item
                response_id = None
            
            # ✅ ENHANCED: Convert audio data to proper format for playback
            if isinstance(audio_data, (array.array, list)):
                # Convert array to bytes for simpleaudio
                if hasattr(audio_data, 'tobytes'):
                    pcm_bytes = audio_data.tobytes()
                else:
                    # Convert list to bytes
                    pcm_bytes = struct.pack(f'<{len(audio_data)}h', *audio_data)
            elif hasattr(audio_data, 'tobytes'):  # numpy array
                pcm_bytes = audio_data.tobytes()
            else:
                # Already bytes
                pcm_bytes = audio_data
                
            # ✅ SIMPLE: Check interrupt before playing
            if FULL_DUPLEX_MODE:
                from audio.full_duplex_manager import full_duplex_manager
                if full_duplex_manager and getattr(full_duplex_manager, 'speech_interrupted', False):
                    print("[Audio] 🛑 INTERRUPT - Skipping chunk")
                    # Mark as interrupted if we have a response ID
                    if response_id:
                        streaming_manager.mark_response_interrupted(response_id)
                    audio_queue.task_done()
                    continue
            
            with audio_lock:
                # Notify once when starting
                if FULL_DUPLEX_MODE:
                    notify_full_duplex_manager_speaking(pcm_bytes)
                
                if not FULL_DUPLEX_MODE:
                    buddy_talking.set()
                
                playback_start_time = time.time()
                
                try:
                    print(f"[Audio] 🎵 Playing professionally smoothed chunk: {len(pcm_bytes)} bytes")
                    if response_id:
                        print(f"[Audio] 📊 Response ID: {response_id}")
                    
                    if SIMPLEAUDIO_AVAILABLE:
                        current_audio_playback = sa.play_buffer(pcm_bytes, 1, 2, sr)
                        
                        # ✅ CRITICAL: Check for interrupt every 1ms during playback
                        while current_audio_playback and current_audio_playback.is_playing():
                            if FULL_DUPLEX_MODE:
                                try:
                                    from audio.full_duplex_manager import full_duplex_manager
                                    if full_duplex_manager and getattr(full_duplex_manager, 'speech_interrupted', False):
                                        print("[Audio] ⚡ IMMEDIATE STOP - Interrupt detected!")
                                        current_audio_playback.stop()
                                        
                                        # Mark current response as interrupted
                                        if response_id:
                                            streaming_manager.mark_response_interrupted(response_id)
                                        
                                        # Clear ALL remaining chunks
                                        cleared = 0
                                        while not audio_queue.empty():
                                            try:
                                                item = audio_queue.get_nowait()
                                                # Mark any other response chunks as interrupted
                                                if len(item) == 3 and item[2]:
                                                    streaming_manager.mark_response_interrupted(item[2])
                                                audio_queue.task_done()
                                                cleared += 1
                                            except queue.Empty:
                                                break
                                        
                                        print(f"[Audio] 🗑️ Cleared {cleared} remaining chunks")
                                        
                                        # Reset professional queue state
                                        professional_audio_queue.clear()
                                        
                                        break
                                except Exception:
                                    pass
                            
                            time.sleep(0.001)  # Check every 1 millisecond
                        
                        if current_audio_playback and not current_audio_playback.is_playing():
                            print(f"[Audio] ✅ Professional chunk completed seamlessly")
                            # ✅ FIX: Mark chunk as played in streaming manager
                            if response_id:
                                chunk_completed_response = streaming_manager.mark_chunk_played(response_id)
                                if chunk_completed_response:
                                    print(f"[Audio] 🏁 Response {response_id} fully completed")
                    else:
                        print("[Audio] ⚠️ simpleaudio not available - skipping audio playback")
                        # Still track completion for testing
                        if response_id:
                            streaming_manager.mark_chunk_played(response_id)
                    
                except Exception as playback_err:
                    print(f"[Audio] ❌ Playback error: {playback_err}")
                
                finally:
                    # Clean up
                    try:
                        if current_audio_playback:
                            if current_audio_playback.is_playing():
                                current_audio_playback.stop()
                            current_audio_playback = None
                    except:
                        pass
                    
                    # Check if interrupted after chunk
                    if FULL_DUPLEX_MODE:
                        from audio.full_duplex_manager import full_duplex_manager
                        if full_duplex_manager and getattr(full_duplex_manager, 'speech_interrupted', False):
                            print("[Audio] 🛑 Post-chunk interrupt detected")
                            
                            # Mark response as interrupted
                            if response_id:
                                streaming_manager.mark_response_interrupted(response_id)
                            
                            # Clear remaining queue and reset professional state
                            while not audio_queue.empty():
                                try:
                                    item = audio_queue.get_nowait()
                                    # Mark any response chunks as interrupted
                                    if len(item) == 3 and item[2]:
                                        streaming_manager.mark_response_interrupted(item[2])
                                    audio_queue.task_done()
                                except queue.Empty:
                                    break
                            
                            professional_audio_queue.clear()
                            
                            # ✅ FIX: Only notify stopped if all responses are complete
                            if streaming_manager.should_notify_completion():
                                notify_full_duplex_manager_stopped()
                            audio_queue.task_done()
                            continue
                    
                    # ✅ FIX: Only notify completion when all streaming responses are done
                    if FULL_DUPLEX_MODE and audio_queue.empty():
                        from audio.full_duplex_manager import full_duplex_manager
                        is_interrupted = full_duplex_manager and getattr(full_duplex_manager, 'speech_interrupted', False)
                        
                        if not is_interrupted and streaming_manager.should_notify_completion():
                            print("[Audio] 🏁 All professionally smoothed responses completed")
                            notify_full_duplex_manager_stopped()
                    
                    if not FULL_DUPLEX_MODE and audio_queue.empty() and streaming_manager.should_notify_completion():
                        buddy_talking.clear()
                    
                    playback_start_time = None
                
            audio_queue.task_done()
            
        except queue.Empty:
            continue
            
        except Exception as e:
            print(f"[Audio] ❌ Worker error: {e}")
            try:
                if current_audio_playback:
                    current_audio_playback.stop()
                    current_audio_playback = None
                if FULL_DUPLEX_MODE and streaming_manager.should_notify_completion():
                    notify_full_duplex_manager_stopped()
                elif not FULL_DUPLEX_MODE:
                    buddy_talking.clear()
                
                # Reset professional audio state on error
                professional_audio_queue.clear()
                
            except:
                pass

def emergency_stop_all_audio():
    """✅ EMERGENCY: Stop ALL audio immediately"""
    global current_audio_playback
    
    try:
        print("[Audio] 🚨 EMERGENCY STOP")
        
        with audio_lock:
            if current_audio_playback:
                if current_audio_playback.is_playing():
                    current_audio_playback.stop()
                    print("[Audio] ⚡ Current chunk STOPPED")
                current_audio_playback = None
        
        cleared = clear_audio_queue()
        
        if not FULL_DUPLEX_MODE:
            buddy_talking.clear()
        
        print(f"[Audio] ⚡ EMERGENCY COMPLETE - Cleared {cleared} chunks")
        
    except Exception as e:
        print(f"[Audio] Emergency stop error: {e}")

def start_audio_worker():
    """Start the audio worker thread"""
    test_kokoro_api()
    threading.Thread(target=audio_worker, daemon=True).start()
    if DEBUG:
        print("[Audio] 🚀 Audio worker thread started")

def is_buddy_talking():
    """Check if Buddy is currently talking"""
    if FULL_DUPLEX_MODE:
        return current_audio_playback is not None and current_audio_playback.is_playing()
    else:
        return buddy_talking.is_set()

def stop_audio_playback():
    """✅ Emergency stop"""
    global current_audio_playback
    
    try:
        with audio_lock:
            if current_audio_playback and current_audio_playback.is_playing():
                current_audio_playback.stop()
                print("[Audio] 🛑 Emergency stop")
                
            current_audio_playback = None
            playback_start_time = None
            
            if FULL_DUPLEX_MODE:
                notify_full_duplex_manager_stopped()
            else:
                buddy_talking.clear()
                
    except Exception as e:
        if DEBUG:
            print(f"[Audio] Emergency stop error: {e}")

def clear_audio_queue():
    """Clear pending audio queue and reset professional smoothing state"""
    cleared = 0
    while not audio_queue.empty():
        try:
            audio_queue.get_nowait()
            audio_queue.task_done()
            cleared += 1
        except queue.Empty:
            break
    
    # ✅ NEW: Clear professional audio queue and reset smoothing state
    professional_cleared = professional_audio_queue.clear()
    
    # Reset chunk sequence for new session
    global chunk_sequence_number
    chunk_sequence_number = 0
    
    if cleared > 0 and DEBUG:
        print(f"[Audio] 🗑️ Cleared {cleared} pending audio items")
        print(f"[Audio] 🎭 Cleared {professional_cleared} professional queue items")
        print(f"[Audio] 🔄 Reset professional smoothing state")
    
    return cleared + professional_cleared

def force_buddy_stop_notification():
    """Force notify that Buddy stopped"""
    print("[Audio] 🚨 FORCE notifying Buddy stopped")
    notify_full_duplex_manager_stopped()

def get_audio_stats():
    """Get comprehensive audio system statistics with professional smoothing info"""
    stats = {
        "queue_size": audio_queue.qsize(),
        "is_playing": current_audio_playback is not None and current_audio_playback.is_playing() if current_audio_playback else False,
        "buddy_talking": buddy_talking.is_set(),
        "playback_start_time": playback_start_time,
        "current_time": time.time(),
        "mode": "FULL_DUPLEX" if FULL_DUPLEX_MODE else "HALF_DUPLEX",
        "kokoro_api_available": kokoro_api_available,
        "api_url": KOKORO_API_BASE_URL,
        "current_response_id": current_response_id,
        "streaming_stats": streaming_manager.get_active_response_stats(),
        "chunk_sequence_number": chunk_sequence_number,
        "professional_smoothing": {
            "enabled": True,
            "numpy_available": NUMPY_AVAILABLE,
            "professional_queue_stats": professional_audio_queue.get_stats()
        }
    }
    return stats

def log_audio_playback_verification():
    """Log comprehensive audio playback verification with professional smoothing details"""
    if DEBUG:
        stats = get_audio_stats()
        prof_stats = stats['professional_smoothing']
        smoother_stats = prof_stats['professional_queue_stats']['smoother_stats']
        
        print("=" * 80)
        print("🔊 PROFESSIONAL AUDIO PLAYBACK VERIFICATION")
        print("=" * 80)
        print(f"📊 Queue Size: {stats['queue_size']}")
        print(f"🎵 Currently Playing: {stats['is_playing']}")
        print(f"🤖 Buddy Talking: {stats['buddy_talking']}")
        print(f"🌐 Kokoro API Available: {stats['kokoro_api_available']}")
        print(f"📡 API URL: {stats['api_url']}")
        print(f"🆔 Current Response ID: {stats['current_response_id']}")
        print(f"🔢 Chunk Sequence: {stats['chunk_sequence_number']}")
        
        # Professional smoothing details
        print(f"\n🎭 PROFESSIONAL SMOOTHING:")
        print(f"  ✅ Enabled: {prof_stats['enabled']}")
        print(f"  📊 NumPy Available: {prof_stats['numpy_available']}")
        print(f"  🎵 Chunks Processed: {smoother_stats['chunks_processed']}")
        print(f"  🌊 Crossfades Applied: {smoother_stats['crossfades_applied']}")
        print(f"  📈 Fade-ins Applied: {smoother_stats['fade_ins_applied']}")
        print(f"  📉 Fade-outs Applied: {smoother_stats['fade_outs_applied']}")
        print(f"  ⏱️ Total Processing Time: {smoother_stats['total_processing_time']:.3f}s")
        
        # Professional queue stats
        prof_queue_stats = prof_stats['professional_queue_stats']
        print(f"\n📦 PROFESSIONAL QUEUE:")
        print(f"  📊 Total Chunks: {prof_queue_stats['total_chunks']}")
        print(f"  ❌ Dropped Chunks: {prof_queue_stats['dropped_chunks']}")
        print(f"  🐛 Processing Errors: {prof_queue_stats['processing_errors']}")
        print(f"  📈 Queue Size: {prof_queue_stats['queue_size']}")
        
        # Streaming response details
        streaming_stats = stats['streaming_stats']
        print(f"\n📈 STREAMING RESPONSES:")
        print(f"  🎯 Active Responses: {streaming_stats['active_responses']}")
        
        if streaming_stats['responses']:
            print("  📋 Response Details:")
            for resp_id, resp_data in streaming_stats['responses'].items():
                print(f"    - {resp_id}:")
                print(f"      User: {resp_data['user']}")
                print(f"      Chunks: {resp_data['chunks_played']}/{resp_data['chunks_received']}")
                print(f"      Complete: {resp_data['is_complete']}")
                print(f"      Duration: {resp_data['duration']:.2f}s")
        
        print("=" * 80)
        print("🎉 PROFESSIONAL AUDIO SYSTEM: Ready for seamless, studio-quality playback!")
        print("=" * 80)

def generate_and_play_kokoro(text, voice=None, lang=DEFAULT_LANG):
    """✅ FIX: Generate and play TTS using Kokoro - called after LLM generation is complete"""
    if not text or len(text.strip()) < 2:
        print("[Kokoro] ⚠️ No text provided for TTS")
        return False
    
    try:
        print(f"[Kokoro] 🎵 Generating TTS for: '{text[:50]}...'")
        success = speak_streaming(text.strip(), voice, lang)
        if success:
            print(f"[Kokoro] ✅ TTS queued successfully")
            return True
        else:
            print(f"[Kokoro] ❌ TTS queueing failed")
            return False
    except Exception as e:
        print(f"[Kokoro] ❌ TTS generation error: {e}")
        return False

def start_streaming_response(user_input, current_user, language):
    """Start a streaming response with proper tracking"""
    global current_response_id
    current_response_id = streaming_manager.start_response(current_user)
    if DEBUG:
        print(f"[Audio] 🚀 Started streaming response {current_response_id} for {current_user}")
    return current_response_id

def queue_text_chunk(text_chunk, voice=None, response_id=None):
    """Queue a text chunk for immediate TTS processing with response tracking"""
    global current_response_id
    if response_id is None:
        response_id = current_response_id
    return speak_streaming(text_chunk, voice, response_id=response_id)

def complete_streaming_response(response_id=None):
    """Mark a streaming response as complete (no more chunks)"""
    global current_response_id
    if response_id is None:
        response_id = current_response_id
    
    if response_id:
        completed = streaming_manager.mark_response_complete(response_id)
        if DEBUG:
            print(f"[Audio] ✅ Marked response {response_id} as complete")
        
        # Clear current response if this was it
        if response_id == current_response_id:
            current_response_id = None
        
        return completed
    return False

# Initialize API connection on module load
test_kokoro_api()