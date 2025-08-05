# audio/smart_aec.py - FIXED Smart AEC - Buddy Voice Detection Fixed
# Date: 2025-07-05 08:42:15
# FIXES: Proper Buddy voice detection, AEC now works when Buddy speaks

import numpy as np
from collections import deque
import time
from config import *

class SmartAEC:
    def __init__(self):
        self.reference_buffer = deque(maxlen=8000)  # 500ms reference
        self.adaptation_buffer = deque(maxlen=16000)  # 1 second adaptation
        self.echo_profile = None
        self.adaptation_rate = min(AEC_ADAPTATION_RATE, 0.03)
        self.suppression_factor = min(AEC_SUPPRESSION_FACTOR, 0.1)
        self.voice_detector = VoiceProtector()
        
        # ✅ NEW: Buddy speaking state tracking
        self.buddy_is_speaking = False
        self.buddy_reference_active = False
        
        self.gentle_mode = True
        self.human_priority_mode = True
        
        self.stats = {
            "echo_cancellations": 0,
            "voice_protections": 0,
            "adaptations": 0,
            "bypassed_for_human": 0,
            "gentle_processings": 0,
            "buddy_voice_processed": 0,
            "aec_applied": 0
        }
        print("[SmartAEC] ✅ FIXED Smart AEC with proper Buddy voice detection")

    def update_reference(self, reference_audio):
        """Update reference audio and mark Buddy as speaking"""
        try:
            # ✅ CRITICAL: Mark that Buddy is speaking and we have reference
            self.buddy_is_speaking = True
            self.buddy_reference_active = True
            
            if len(reference_audio) > 0:
                if len(reference_audio) > 4000:
                    reference_audio = reference_audio[::2][:4000]
                
                self.reference_buffer.extend(reference_audio)
                self.adaptation_buffer.extend(reference_audio)
                self._gentle_adapt_echo_profile()
                
                if DEBUG:
                    print(f"[SmartAEC] 🤖 Reference updated: Buddy speaking, {len(reference_audio)} samples")
                
        except Exception as e:
            if DEBUG:
                print(f"[SmartAEC] Reference update error: {e}")

    def clear_reference(self):
        """Clear reference when Buddy stops speaking"""
        self.buddy_is_speaking = False
        self.buddy_reference_active = False
        if DEBUG:
            print("[SmartAEC] 🤖 Reference cleared: Buddy stopped")

    def process_microphone_input(self, mic_audio):
        """✅ FIXED: Proper AEC that works when Buddy speaks"""
        try:
            if not AEC_ENABLED or getattr(self, 'emergency_disabled', False):
                return mic_audio

            # ✅ CRITICAL FIX: When Buddy is speaking, ALWAYS apply AEC
            if self.buddy_is_speaking and self.buddy_reference_active:
                # Buddy is speaking - apply AEC to remove his voice from mic
                if DEBUG:
                    print(f"[SmartAEC] 🤖 Buddy speaking - applying AEC to remove echo")
                
                processed = self._apply_echo_cancellation(mic_audio)
                if processed is not None:
                    self.stats["echo_cancellations"] += 1
                    self.stats["aec_applied"] += 1
                    self.stats["buddy_voice_processed"] += 1
                    return processed
                else:
                    return mic_audio
            
            # ✅ When Buddy is NOT speaking, check for human speech
            elif self.voice_detector.is_human_speech(mic_audio):
                self.stats["voice_protections"] += 1
                self.stats["bypassed_for_human"] += 1
                
                if DEBUG:
                    print(f"[SmartAEC] 👤 Human speech detected - bypassing AEC")
                
                return mic_audio
            
            # ✅ Default: light processing
            else:
                processed = self._light_processing(mic_audio)
                self.stats["gentle_processings"] += 1
                return processed
                
        except Exception as e:
            if DEBUG:
                print(f"[SmartAEC] Processing error: {e}")
            return mic_audio

    def _apply_echo_cancellation(self, mic_audio):
        """Apply echo cancellation when Buddy is speaking"""
        try:
            if len(self.reference_buffer) < len(mic_audio):
                return None
            
            reference = np.array(list(self.reference_buffer)[-len(mic_audio):])
            
            # Calculate correlation
            correlation = np.corrcoef(mic_audio, reference)[0, 1]
            
            if DEBUG:
                mic_volume = np.abs(mic_audio).mean()
                ref_volume = np.abs(reference).mean()
                print(f"[SmartAEC] 🔄 AEC: mic={mic_volume:.0f}, ref={ref_volume:.0f}, corr={correlation:.3f}")
            
            if correlation > 0.3:  # Lower threshold - more aggressive when Buddy speaks
                # Apply echo cancellation
                suppression = min(self.suppression_factor * 2, 0.2)  # Slightly more aggressive
                echo_estimate = reference * suppression
                
                # Remove echo
                result = mic_audio.astype(np.float32) - echo_estimate.astype(np.float32)
                
                # Prevent over-suppression
                result = np.clip(result, -32768, 32767)
                
                if DEBUG:
                    result_volume = np.abs(result).mean()
                    print(f"[SmartAEC] ✅ Echo removed: {mic_volume:.0f} -> {result_volume:.0f}")
                
                return result.astype(np.int16)
            
            return mic_audio
            
        except Exception as e:
            if DEBUG:
                print(f"[SmartAEC] Echo cancellation error: {e}")
            return mic_audio

    def _light_processing(self, audio):
        """Light processing for when neither Buddy nor human is clearly speaking"""
        try:
            # Very gentle noise reduction
            if len(audio) > 160:
                sorted_audio = np.sort(np.abs(audio))
                noise_floor = np.mean(sorted_audio[:len(sorted_audio)//4])
                noise_gate = noise_floor * 0.2
                mask = np.abs(audio) > noise_gate
                return np.where(mask, audio, audio * 0.9)
            return audio
        except Exception as e:
            return audio

    def _gentle_adapt_echo_profile(self):
        """Much gentler adaptation"""
        try:
            if len(self.adaptation_buffer) >= 8000:
                recent_audio = np.array(list(self.adaptation_buffer)[-8000:])
                
                new_profile = {
                    "volume": np.abs(recent_audio).mean(),
                    "peak": np.max(np.abs(recent_audio)),
                    "spectral_centroid": self._calculate_spectral_centroid(recent_audio)
                }
                
                if self.echo_profile:
                    blend_rate = 0.1
                    for key in new_profile:
                        if key in self.echo_profile:
                            self.echo_profile[key] = (
                                self.echo_profile[key] * (1 - blend_rate) + 
                                new_profile[key] * blend_rate
                            )
                else:
                    self.echo_profile = new_profile
                
                self.stats["adaptations"] += 1
                
        except Exception as e:
            if DEBUG:
                print(f"[SmartAEC] Gentle adaptation error: {e}")

    def _calculate_spectral_centroid(self, audio):
        """Calculate spectral centroid"""
        try:
            audio_chunk = audio[:1024] if len(audio) > 1024 else audio
            fft = np.fft.rfft(audio_chunk)
            magnitude = np.abs(fft)
            freqs = np.fft.rfftfreq(len(audio_chunk), 1/SAMPLE_RATE)
            centroid = np.sum(freqs * magnitude) / (np.sum(magnitude) + 1e-10)
            return centroid
        except Exception as e:
            return 1000

    def emergency_disable(self):
        """Emergency disable AEC completely"""
        self.emergency_disabled = True
        print("[SmartAEC] 🚨 EMERGENCY DISABLED")

    def emergency_enable(self):
        """Re-enable AEC after emergency disable"""
        self.emergency_disabled = False
        print("[SmartAEC] ✅ EMERGENCY RE-ENABLED")

    def set_gentle_mode(self, enabled=True):
        """Enable/disable gentle mode"""
        self.gentle_mode = enabled
        print(f"[SmartAEC] {'🌟 GENTLE MODE' if enabled else '🔧 NORMAL MODE'}")

    def get_stats(self):
        """Get AEC statistics"""
        stats = self.stats.copy()
        stats.update({
            "gentle_mode": self.gentle_mode,
            "human_priority_mode": self.human_priority_mode,
            "emergency_disabled": getattr(self, 'emergency_disabled', False),
            "buddy_is_speaking": self.buddy_is_speaking,
            "buddy_reference_active": self.buddy_reference_active,
            "suppression_factor": self.suppression_factor,
            "adaptation_rate": self.adaptation_rate,
            "reference_buffer_size": len(self.reference_buffer)
        })
        return stats

class VoiceProtector:
    """✅ FIXED: More accurate human vs TTS detection"""
    
    def __init__(self):
        self.human_voice_freq_range = (80, 300)
        self.speech_harmonics_range = (300, 3000)
        self.speech_pattern_buffer = deque(maxlen=4)
        self.volume_history = deque(maxlen=10)
        self.detection_confidence = 0.0

    def is_human_speech(self, audio):
        """✅ FIXED: Better detection that doesn't confuse TTS with human speech"""
        try:
            if len(audio) < 160:
                self.speech_pattern_buffer.append(False)
                return False

            volume = np.abs(audio).mean()
            
            # ✅ FIXED: Higher volume threshold to avoid TTS detection
            if volume < 400:  # Higher threshold
                self.speech_pattern_buffer.append(False)
                return False

            self.volume_history.append(volume)

            # ✅ TEST 1: Human frequency content (more restrictive)
            has_human_freqs = self._has_human_frequencies(audio, min_ratio=0.25)  # Higher ratio needed
            
            # ✅ TEST 2: Speech-like patterns (more restrictive)
            has_speech_pattern = self._has_speech_pattern(audio)
            
            # ✅ TEST 3: Dynamic range appropriate for natural speech
            peak = np.max(np.abs(audio))
            dynamic_range = peak / (volume + 1e-10)
            good_dynamic_range = 2.0 < dynamic_range < 20.0  # Natural speech range
            
            # ✅ TEST 4: Temporal consistency
            has_consistency = self._has_temporal_consistency()
            
            # ✅ TEST 5: Not obviously synthetic/TTS
            not_synthetic = self._is_not_synthetic(audio)
            
            # ✅ NEW TEST 6: Not too regular (TTS is often too regular)
            not_too_regular = self._not_too_regular(audio)

            # ✅ SCORING: Much more restrictive
            score = 0
            if has_human_freqs:
                score += 2
            if has_speech_pattern:
                score += 2  
            if good_dynamic_range:
                score += 1
            if has_consistency:
                score += 1
            if not_synthetic:
                score += 1
            if not_too_regular:
                score += 1
            if volume > 800:  # Bonus for very close speech
                score += 1

            is_speech = score >= 6  # ✅ FIXED: Need 6+ points out of 8 (much more restrictive)
            
            self.speech_pattern_buffer.append(is_speech)
            
            # ✅ DECISION: Require strong consistency
            if len(self.speech_pattern_buffer) >= 3:
                recent_detections = sum(list(self.speech_pattern_buffer)[-3:])
                final_decision = recent_detections >= 3  # ✅ FIXED: Need ALL 3 to agree
            else:
                final_decision = False  # Default to False
            
            if DEBUG and final_decision:
                print(f"[VoiceProtector] 👤 CONFIDENT HUMAN SPEECH: vol={volume:.0f}, score={score}/8")
            elif DEBUG and score >= 4:
                print(f"[VoiceProtector] 🤖 Likely TTS/synthetic: vol={volume:.0f}, score={score}/8")
            
            return final_decision
            
        except Exception as e:
            if DEBUG:
                print(f"[VoiceProtector] Detection error: {e}")
            self.speech_pattern_buffer.append(False)
            return False

    def _not_too_regular(self, audio):
        """Check that audio is not too regular (TTS often has very regular patterns)"""
        try:
            # Check for overly regular amplitude patterns
            window_size = 40
            windows = [audio[i:i+window_size] for i in range(0, len(audio)-window_size, window_size//4)]
            
            if len(windows) < 4:
                return True
            
            volumes = [np.abs(w).mean() for w in windows]
            
            # Check for too much regularity in volume
            volume_std = np.std(volumes)
            volume_mean = np.mean(volumes)
            
            if volume_mean > 0:
                regularity_ratio = volume_std / volume_mean
                # TTS often has regularity ratio < 0.3, human speech > 0.3
                return regularity_ratio > 0.3
            
            return True
            
        except Exception:
            return True

    def _has_human_frequencies(self, audio, min_ratio=0.25):
        """Check for human voice frequency content - more restrictive"""
        try:
            audio_chunk = audio[:512] if len(audio) > 512 else audio
            fft = np.fft.rfft(audio_chunk)
            magnitude = np.abs(fft)
            freqs = np.fft.rfftfreq(len(audio_chunk), 1/SAMPLE_RATE)
            
            fundamental_mask = (freqs >= self.human_voice_freq_range[0]) & (freqs <= self.human_voice_freq_range[1])
            harmonic_mask = (freqs >= self.speech_harmonics_range[0]) & (freqs <= self.speech_harmonics_range[1])
            
            fundamental_energy = np.sum(magnitude[fundamental_mask])
            harmonic_energy = np.sum(magnitude[harmonic_mask])
            total_energy = np.sum(magnitude) + 1e-10
            
            fund_ratio = fundamental_energy / total_energy
            harm_ratio = harmonic_energy / total_energy
            
            # ✅ FIXED: More restrictive - need both fundamental AND harmonic content
            return (fund_ratio > min_ratio) and (harm_ratio > 0.4)
            
        except Exception:
            return False

    def _has_speech_pattern(self, audio):
        """Check for natural speech-like amplitude modulation"""
        try:
            window_size = 40
            windows = [audio[i:i+window_size] for i in range(0, len(audio)-window_size, window_size//2)]
            
            if len(windows) < 3:
                return False
            
            volumes = [np.abs(w).mean() for w in windows]
            
            if len(volumes) < 3:
                return False
            
            volume_std = np.std(volumes)
            volume_mean = np.mean(volumes)
            modulation_ratio = volume_std / (volume_mean + 1e-10)
            
            # ✅ FIXED: Natural speech modulation range
            return 0.3 < modulation_ratio < 2.5
            
        except Exception:
            return False

    def _has_temporal_consistency(self):
        """Check for consistent volume levels"""
        try:
            if len(self.volume_history) < 3:
                return True
            
            volumes = list(self.volume_history)
            volume_std = np.std(volumes)
            volume_mean = np.mean(volumes)
            
            consistency_ratio = volume_std / (volume_mean + 1e-10)
            return 0.2 < consistency_ratio < 1.5
            
        except Exception:
            return True

    def _is_not_synthetic(self, audio):
        """Check that audio doesn't sound synthetic"""
        try:
            fft = np.fft.rfft(audio[:256] if len(audio) > 256 else audio)
            magnitude = np.abs(fft)
            
            peak_idx = np.argmax(magnitude)
            peak_mag = magnitude[peak_idx]
            total_mag = np.sum(magnitude)
            
            peak_ratio = peak_mag / (total_mag + 1e-10)
            
            # ✅ FIXED: TTS often has dominant frequencies
            return peak_ratio < 0.6
            
        except Exception:
            return True

# Global instance
smart_aec = SmartAEC()
print("[SmartAEC] 🌟 FIXED Smart AEC with proper Buddy/Human detection")