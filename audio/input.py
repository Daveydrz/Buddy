# audio/input.py - FIXED Full Duplex Ready Audio Input
# Date: 2025-07-05 08:25:03  
# FIXES: Much gentler AEC, better thresholds, bug fixes, human speech protection

import sounddevice as sd
import numpy as np
import time
from scipy.io.wavfile import write
from audio.processing import downsample_audio
from audio.output import buddy_talking, is_buddy_talking
from config import *

# Use only the Smart AEC system, as per config
from audio.smart_aec import smart_aec

def simple_vad_listen():
    """FIXED Full Duplex Ready Voice Activity Detection"""
    if FULL_DUPLEX_MODE:
        return full_duplex_vad_listen()
    else:
        return half_duplex_vad_listen()

def full_duplex_vad_listen():
    """FIXED Full duplex listening with Much Gentler AEC"""
    print("[Buddy V2] 🎤 FIXED Full Duplex Listening with Gentle AEC...")

    blocksize = int(MIC_SAMPLE_RATE * 0.02)

    with sd.InputStream(device=MIC_DEVICE_INDEX, samplerate=MIC_SAMPLE_RATE, 
                       channels=1, blocksize=blocksize, dtype='int16') as stream:

        # ✅ FIXED: More conservative baseline
        baseline_samples = []
        for _ in range(5):  # More samples for better baseline
            frame, _ = stream.read(blocksize)
            audio = np.frombuffer(frame.tobytes(), dtype=np.int16)
            baseline_samples.append(np.abs(audio).mean())

        baseline = np.mean(baseline_samples) if baseline_samples else 200
        
        # ✅ FIXED: Much more conservative threshold
        speech_threshold = max(baseline * 3.0, 600)  # Lower threshold for better detection
        
        print(f"[FullDuplex] 👂 FIXED Ready (baseline: {baseline:.0f}, threshold: {speech_threshold:.0f})")

        audio_buffer = []
        start_time = time.time()
        silence_frames = 0
        has_speech = False
        speech_frames = 0
        required_speech_frames = 5  # ✅ FIXED: Fewer frames needed (was 8)

        while True:
            elapsed = time.time() - start_time

            # ✅ FIXED: Longer timeout for better capture
            if elapsed >= 10.0:  # Increased from 8.0
                break

            if has_speech and elapsed > 1.5 and silence_frames > 50:  # More patience
                break

            try:
                frame, _ = stream.read(blocksize)
                audio = np.frombuffer(frame.tobytes(), dtype=np.int16)
                
                # ✅ FIXED: Much gentler AEC processing
                for i in range(0, len(audio), 480):  # 480 samples = 10ms at 48kHz
                    chunk = audio[i:i+480]
                    if len(chunk) < 480:
                        continue
                    
                    # ✅ CRITICAL FIX: Only apply AEC when Buddy is actually speaking
                    if is_buddy_talking():
                        # Apply gentle AEC only when needed
                        processed_chunk = smart_aec.process_microphone_input(chunk)
                        if DEBUG and i == 0:  # Log once per frame
                            print("🔧", end="", flush=True)  # AEC applied
                    else:
                        # ✅ BYPASS AEC: When Buddy is silent, use raw audio
                        processed_chunk = chunk
                    
                    audio_buffer.append(processed_chunk)

                    # ✅ FIXED: Volume detection on processed audio
                    volume = np.abs(processed_chunk).mean()
                    peak_volume = np.max(np.abs(processed_chunk))

                    # ✅ FIXED: More lenient detection criteria
                    volume_ok = volume > speech_threshold
                    peak_ok = peak_volume > speech_threshold * 1.2  # Lower peak requirement

                    if volume_ok and peak_ok:
                        speech_frames += 1
                        silence_frames = 0
                        if speech_frames >= required_speech_frames:
                            if not has_speech:
                                print(f"\n[FullDuplex] 🎤 USER SPEECH DETECTED!")
                                print(f"[FullDuplex] Vol:{volume:.0f} > {speech_threshold:.0f}")
                                has_speech = True
                            print("🔴", end="", flush=True)
                        else:
                            print("🟡", end="", flush=True)
                    else:
                        speech_frames = max(0, speech_frames - 1)  # ✅ FIXED: was self.speech_frames
                        silence_frames += 1
                        if has_speech and silence_frames % 30 == 0:
                            print("⏸️", end="", flush=True)
                            
            except Exception as e:
                if DEBUG:
                    print(f"\n[FullDuplex] Recording error: {e}")
                break

        # ✅ FIXED: Process results with better validation
        if audio_buffer and len(audio_buffer) > 15:  # Lower requirement
            audio_np_48k = np.concatenate(audio_buffer, axis=0).astype(np.int16)
            
            # Downsample the whole buffer ONCE at the end
            audio_16k = downsample_audio(audio_np_48k, MIC_SAMPLE_RATE, SAMPLE_RATE)
            duration = len(audio_16k) / SAMPLE_RATE
            volume = np.abs(audio_16k).mean()

            # Debug save
            if DEBUG:
                write("debug_full_duplex.wav", SAMPLE_RATE, audio_16k)
                print(f"\n[FullDuplex] 💾 Saved debug audio: {duration:.1f}s")

            # ✅ FIXED: More lenient acceptance criteria
            if has_speech and volume > baseline * 2:  # Lower requirement (was * 3)
                aec_stats = smart_aec.get_stats()
                echo_cancellations = aec_stats.get('echo_cancellations', 0)
                voice_protections = aec_stats.get('voice_protections', 0)
                
                print(f"\n[FullDuplex] ✅ ACCEPTED: {duration:.1f}s")
                print(f"[FullDuplex] 📊 AEC: {echo_cancellations} cancellations, {voice_protections} voice protections")
                return audio_16k
            else:
                print(f"\n[FullDuplex] ❌ REJECTED: duration={duration:.1f}s, vol={volume:.0f} (need >{baseline*2:.0f})")
                return None
        else:
            print(f"\n[FullDuplex] ❌ INSUFFICIENT: {len(audio_buffer)} chunks (need >15)")
            return None

def half_duplex_vad_listen():
    """FIXED Half duplex listening with better detection"""
    print("[Buddy V2] 🎤 FIXED Half Duplex Listening...")

    # ✅ FIXED: Better wait for Buddy to finish
    while buddy_talking.is_set():
        time.sleep(0.1)
    time.sleep(0.3)  # Shorter safety buffer

    blocksize = int(MIC_SAMPLE_RATE * 0.02)

    with sd.InputStream(device=MIC_DEVICE_INDEX, samplerate=MIC_SAMPLE_RATE, 
                       channels=1, blocksize=blocksize, dtype='int16') as stream:

        # ✅ FIXED: Better baseline calculation
        baseline_samples = []
        for _ in range(5):
            frame, _ = stream.read(blocksize)
            audio = np.frombuffer(frame.tobytes(), dtype=np.int16)
            baseline_samples.append(np.abs(audio).mean())

        baseline = np.mean(baseline_samples) if baseline_samples else 200
        
        # ✅ FIXED: Lower threshold for half duplex (no Buddy interference)
        speech_threshold = max(baseline * 2.5, 500)  # Lower threshold

        print(f"[HalfDuplex] 👂 FIXED Ready (baseline: {baseline:.0f}, threshold: {speech_threshold:.0f})")

        audio_buffer = []
        start_time = time.time()
        silence_frames = 0
        has_speech = False
        speech_frames = 0
        required_speech_frames = 4  # ✅ FIXED: Even fewer frames needed

        while True:
            elapsed = time.time() - start_time

            if elapsed >= 10.0:  # Longer timeout
                break

            if has_speech and elapsed > 1.0 and silence_frames > 40:
                break

            try:
                frame, _ = stream.read(blocksize)
                audio = np.frombuffer(frame.tobytes(), dtype=np.int16)
                
                # ✅ FIXED: Much gentler processing for half duplex
                for i in range(0, len(audio), 480):  # 480 samples = 10ms at 48kHz
                    chunk = audio[i:i+480]
                    if len(chunk) < 480:
                        continue
                    
                    # ✅ MINIMAL AEC: Only very gentle processing in half duplex
                    if AEC_ENABLED and not getattr(smart_aec, 'emergency_disabled', False):
                        processed_chunk = smart_aec.process_microphone_input(chunk)
                    else:
                        processed_chunk = chunk
                    
                    audio_buffer.append(processed_chunk)

                    volume = np.abs(processed_chunk).mean()
                    peak_volume = np.max(np.abs(processed_chunk))

                    # ✅ FIXED: Even more lenient for half duplex
                    volume_ok = volume > speech_threshold
                    peak_ok = peak_volume > speech_threshold * 1.1

                    if volume_ok and peak_ok:
                        speech_frames += 1
                        silence_frames = 0
                        if speech_frames >= required_speech_frames:
                            if not has_speech:
                                print(f"\n[HalfDuplex] 🎤 USER SPEECH DETECTED!")
                                print(f"[HalfDuplex] Vol:{volume:.0f} > {speech_threshold:.0f}")
                                has_speech = True
                            print("🔴", end="", flush=True)
                        else:
                            print("🟡", end="", flush=True)
                    else:
                        speech_frames = max(0, speech_frames - 1)
                        silence_frames += 1
                        if has_speech and silence_frames % 20 == 0:
                            print("⏸️", end="", flush=True)
                            
            except Exception as e:
                if DEBUG:
                    print(f"\n[HalfDuplex] Recording error: {e}")
                break

        # ✅ FIXED: Better result processing
        if audio_buffer and len(audio_buffer) > 10:  # Even lower requirement
            audio_np_48k = np.concatenate(audio_buffer, axis=0).astype(np.int16)
            audio_16k = downsample_audio(audio_np_48k, MIC_SAMPLE_RATE, SAMPLE_RATE)
            duration = len(audio_16k) / SAMPLE_RATE
            volume = np.abs(audio_16k).mean()
            
            if DEBUG:
                write("debug_half_duplex.wav", SAMPLE_RATE, audio_16k)
                print(f"\n[HalfDuplex] 💾 Saved debug audio: {duration:.1f}s")
            
            # ✅ FIXED: Very lenient acceptance for half duplex
            if has_speech and volume > baseline * 1.5:  # Much lower requirement
                print(f"\n[HalfDuplex] ✅ ACCEPTED: {duration:.1f}s, vol:{volume:.0f}")
                return audio_16k
            else:
                print(f"\n[HalfDuplex] ❌ REJECTED: duration={duration:.1f}s, vol={volume:.0f} (need >{baseline*1.5:.0f})")
                return None
        else:
            print(f"\n[HalfDuplex] ❌ INSUFFICIENT: {len(audio_buffer)} chunks (need >10)")
            return None

def aec_training_listen(description, timeout=8):
    """FIXED Training listen with minimal processing"""
    print(f"[Training] 🎓 {description}")
    
    # ✅ FIXED: Better wait for Buddy to finish
    while buddy_talking.is_set():
        time.sleep(0.1)
    time.sleep(1.0)  # Longer pause for training
    
    # ✅ FIXED: Use half duplex for training (cleaner audio)
    return half_duplex_vad_listen()

def emergency_raw_audio_listen():
    """Emergency function for completely raw audio capture"""
    print("[Emergency] 🚨 RAW AUDIO MODE - No processing!")
    
    blocksize = int(MIC_SAMPLE_RATE * 0.02)
    
    with sd.InputStream(device=MIC_DEVICE_INDEX, samplerate=MIC_SAMPLE_RATE, 
                       channels=1, blocksize=blocksize, dtype='int16') as stream:
        
        print("[Emergency] 👂 Raw listening...")
        
        audio_buffer = []
        start_time = time.time()
        
        while time.time() - start_time < 5.0:  # 5 second capture
            try:
                frame, _ = stream.read(blocksize)
                audio = np.frombuffer(frame.tobytes(), dtype=np.int16)
                audio_buffer.append(audio)
                print("📼", end="", flush=True)
            except Exception as e:
                print(f"Raw capture error: {e}")
                break
        
        if audio_buffer:
            audio_np = np.concatenate(audio_buffer, axis=0).astype(np.int16)
            audio_16k = downsample_audio(audio_np, MIC_SAMPLE_RATE, SAMPLE_RATE)
            
            print(f"\n[Emergency] ✅ Raw capture: {len(audio_16k)/SAMPLE_RATE:.1f}s")
            write("emergency_raw.wav", SAMPLE_RATE, audio_16k)
            return audio_16k
        
        return None

def get_input_stats():
    """Get input system statistics"""
    return {
        "mic_device": MIC_DEVICE_INDEX,
        "mic_sample_rate": MIC_SAMPLE_RATE,
        "target_sample_rate": SAMPLE_RATE,
        "full_duplex_mode": FULL_DUPLEX_MODE,
        "aec_enabled": AEC_ENABLED,
        "buddy_talking": buddy_talking.is_set() if not FULL_DUPLEX_MODE else is_buddy_talking(),
        "smart_aec_stats": smart_aec.get_stats()
    }