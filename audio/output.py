# audio/output.py - UPDATED for Kokoro-FastAPI with FIXED Interrupt Handling
# Date: 2025-07-06 20:15:28 (Brisbane Time)
# FIXES: Proper interrupt handling, notification system, and streaming TTS coordination

import threading
import time
import queue
import numpy as np

# ✅ FIX: Make simpleaudio import optional
try:
    import simpleaudio as sa
    SIMPLEAUDIO_AVAILABLE = True
    print("[AudioOutput] ✅ simpleaudio available")
except ImportError:
    print("[AudioOutput] ⚠️ simpleaudio not available - audio playback disabled")
    SIMPLEAUDIO_AVAILABLE = False

import requests
import io
import tempfile
import os
from langdetect import detect
from config import *

# Global audio state
audio_queue = queue.Queue()
current_audio_playback = None
audio_lock = threading.Lock()
buddy_talking = threading.Event()
playback_start_time = None

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

def test_kokoro_api():
    """Test if Kokoro-FastAPI is available"""
    global kokoro_api_available
    try:
        response = requests.get(f"{KOKORO_API_BASE_URL}/health", timeout=5)
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
    """Generate TTS audio using Kokoro-FastAPI"""
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
        
        # Call Kokoro-FastAPI
        response = requests.post(
            f"{KOKORO_API_BASE_URL}/v1/audio/speech",
            json=payload,
            timeout=KOKORO_API_TIMEOUT
        )
        
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
            
            # Convert to numpy array
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
                from scipy.signal import resample_poly
                audio_data = resample_poly(audio_data, SAMPLE_RATE, sample_rate)
                audio_data = audio_data.astype(np.int16)
            
            # Clean up temp file
            try:
                os.unlink(temp_path)
            except:
                pass
            
            if DEBUG:
                print(f"[Buddy V2] 🗣️ Generated TTS via FastAPI: {len(audio_data)} samples, voice: {voice}")
            
            return audio_data, SAMPLE_RATE
            
        else:
            print(f"[Buddy V2] ❌ Kokoro-FastAPI error: {response.status_code}")
            if response.text:
                print(f"[Buddy V2] Error details: {response.text}")
            return None, None
            
    except Exception as e:
        print(f"[Buddy V2] TTS error: {e}")
        return None, None

def speak_async(text, lang=DEFAULT_LANG):
    """Queue text for speech synthesis"""
    if not text or len(text.strip()) < 2:
        return
        
    def tts_worker():
        pcm, sr = generate_tts(text.strip(), lang)
        if pcm is not None:
            audio_queue.put((pcm, sr))
    
    threading.Thread(target=tts_worker, daemon=True).start()

def speak_streaming(text, voice=None, lang=DEFAULT_LANG):
    """✅ FIXED: Queue text chunk for immediate streaming TTS"""
    if not text or len(text.strip()) < 2:
        return False
        
    def streaming_tts_worker():
        try:
            if not kokoro_api_available:
                if not test_kokoro_api():
                    return False
            
            # ✅ FIX: Properly handle voice parameter
            selected_voice = voice  # Use provided voice
            if selected_voice is None:
                # Detect voice from language if none provided
                detected_lang = lang or detect(text)
                selected_voice = KOKORO_API_VOICES.get(detected_lang, KOKORO_DEFAULT_VOICE)
            
            # Quick API call for streaming
            payload = {
                "input": text.strip(),
                "voice": selected_voice,  # ✅ Use selected_voice instead of voice
                "response_format": "wav"
            }
            
            response = requests.post(
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
                
                # Quick conversion
                if sample_width == 2:
                    audio_data = np.frombuffer(frames, dtype=np.int16)
                else:
                    audio_data = np.frombuffer(frames, dtype=np.uint8)
                    audio_data = ((audio_data.astype(np.int16) - 128) * 256)
                
                if channels == 2:
                    audio_data = audio_data.reshape(-1, 2)[:, 0]
                
                # Queue immediately
                audio_queue.put((audio_data, sample_rate))
                
                # Cleanup
                try:
                    os.unlink(temp_path)
                except:
                    pass
                
                if DEBUG:
                    print(f"[StreamingTTS] ✅ Queued chunk: '{text[:50]}...' with voice: {selected_voice}")
                
                return True
            else:
                print(f"[StreamingTTS] ❌ API Error {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"[StreamingTTS] ❌ Error: {e}")
        
        return False
    
    threading.Thread(target=streaming_tts_worker, daemon=True).start()
    return True

def play_chime():
    """Play notification chime"""
    try:
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
    """✅ SIMPLE FIX: Audio worker that STOPS IMMEDIATELY on interrupt"""
    global current_audio_playback, playback_start_time
    
    print(f"[Buddy V2] 🎵 Simple Audio Worker started")
    
    while True:
        try:
            item = audio_queue.get(timeout=0.1)
            if item is None:
                break
                
            pcm, sr = item
            
            # ✅ SIMPLE: Check interrupt before playing
            if FULL_DUPLEX_MODE:
                from audio.full_duplex_manager import full_duplex_manager
                if full_duplex_manager and getattr(full_duplex_manager, 'speech_interrupted', False):
                    print("[Audio] 🛑 INTERRUPT - Skipping chunk")
                    audio_queue.task_done()
                    continue
            
            with audio_lock:
                # Notify once when starting
                if FULL_DUPLEX_MODE:
                    notify_full_duplex_manager_speaking(pcm)
                
                if not FULL_DUPLEX_MODE:
                    buddy_talking.set()
                
                playback_start_time = time.time()
                
                try:
                    print(f"[Audio] 🎵 Playing chunk: {len(pcm)} samples")
                    
                    if SIMPLEAUDIO_AVAILABLE:
                        current_audio_playback = sa.play_buffer(pcm.tobytes(), 1, 2, sr)
                        
                        # ✅ CRITICAL: Check for interrupt every 1ms during playback
                        while current_audio_playback and current_audio_playback.is_playing():
                            if FULL_DUPLEX_MODE:
                                try:
                                    from audio.full_duplex_manager import full_duplex_manager
                                    if full_duplex_manager and getattr(full_duplex_manager, 'speech_interrupted', False):
                                        print("[Audio] ⚡ IMMEDIATE STOP - Interrupt detected!")
                                        current_audio_playback.stop()
                                        
                                        # Clear ALL remaining chunks
                                        cleared = 0
                                        while not audio_queue.empty():
                                            try:
                                                audio_queue.get_nowait()
                                                audio_queue.task_done()
                                                cleared += 1
                                            except queue.Empty:
                                                break
                                        
                                        print(f"[Audio] 🗑️ Cleared {cleared} remaining chunks")
                                        break
                                except Exception:
                                    pass
                            
                            time.sleep(0.001)  # Check every 1 millisecond
                        
                        if current_audio_playback and not current_audio_playback.is_playing():
                            print(f"[Audio] ✅ Chunk completed")
                    else:
                        print("[Audio] ⚠️ simpleaudio not available - skipping audio playback")
                    
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
                            
                            # Clear remaining queue
                            while not audio_queue.empty():
                                try:
                                    audio_queue.get_nowait()
                                    audio_queue.task_done()
                                except queue.Empty:
                                    break
                            
                            notify_full_duplex_manager_stopped()
                            audio_queue.task_done()
                            continue
                    
                    # Normal completion - notify stopped only if queue empty
                    if FULL_DUPLEX_MODE and audio_queue.empty():
                        from audio.full_duplex_manager import full_duplex_manager
                        is_interrupted = full_duplex_manager and getattr(full_duplex_manager, 'speech_interrupted', False)
                        
                        if not is_interrupted:
                            print("[Audio] 🏁 All chunks completed normally")
                            notify_full_duplex_manager_stopped()
                    
                    if not FULL_DUPLEX_MODE and audio_queue.empty():
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
                if FULL_DUPLEX_MODE:
                    notify_full_duplex_manager_stopped()
                else:
                    buddy_talking.clear()
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
    """Clear pending audio queue"""
    cleared = 0
    while not audio_queue.empty():
        try:
            audio_queue.get_nowait()
            audio_queue.task_done()
            cleared += 1
        except queue.Empty:
            break
    
    if cleared > 0 and DEBUG:
        print(f"[Audio] 🗑️ Cleared {cleared} pending audio items")
    
    return cleared

def force_buddy_stop_notification():
    """Force notify that Buddy stopped"""
    print("[Audio] 🚨 FORCE notifying Buddy stopped")
    notify_full_duplex_manager_stopped()

def get_audio_stats():
    """Get audio system statistics"""
    return {
        "queue_size": audio_queue.qsize(),
        "is_playing": current_audio_playback is not None and current_audio_playback.is_playing() if current_audio_playback else False,
        "buddy_talking": buddy_talking.is_set(),
        "playback_start_time": playback_start_time,
        "current_time": time.time(),
        "mode": "FULL_DUPLEX" if FULL_DUPLEX_MODE else "HALF_DUPLEX",
        "kokoro_api_available": kokoro_api_available,
        "api_url": KOKORO_API_BASE_URL
    }

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
    """Start a streaming response with immediate TTS"""
    pass

def queue_text_chunk(text_chunk, voice=None):
    """Queue a text chunk for immediate TTS processing"""
    return speak_streaming(text_chunk, voice)

# Initialize API connection on module load
test_kokoro_api()