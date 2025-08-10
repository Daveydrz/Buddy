# audio/full_duplex_manager.py - TURN-BASED CONVERSATION FLOW WITH INTERRUPT HANDLING
# Date: 2025-07-06 19:48:43 (Brisbane Time)
# FIXES: Proper interrupt handling and speech stopping

import threading
import time
import queue
import numpy as np
from collections import deque
from config import *

from audio.smart_aec import smart_aec

try:
    from audio.smart_detection_manager import analyze_speech_detection, get_current_threshold
    SMART_DETECTION_AVAILABLE = True
    print("[FullDuplex] ✅ Smart room-scale detection loaded")
except ImportError:
    SMART_DETECTION_AVAILABLE = False
    print("[FullDuplex] ⚠️ Smart detection not available, using original thresholds")

# ✅ ADD THIS IMPORT BLOCK HERE:
try:
    from config import (USER_SPEECH_QUALITY_THRESHOLD, USER_SPEECH_SPECTRAL_THRESHOLD, 
                        BUDDY_INTERRUPT_QUALITY_THRESHOLD, LOG_REJECTION_REASONS)
    print("[FullDuplex] ✅ Advanced voice thresholds imported from config")
except ImportError:
    # Fallback values if not in config
    USER_SPEECH_QUALITY_THRESHOLD = 0.6
    USER_SPEECH_SPECTRAL_THRESHOLD = 0.5
    BUDDY_INTERRUPT_QUALITY_THRESHOLD = 0.8
    LOG_REJECTION_REASONS = True
    print("[FullDuplex] ⚠️ Using fallback voice thresholds")

class FullDuplexManager:
    def __init__(self):
        self.input_queue = queue.Queue(maxsize=100)
        self.output_queue = queue.Queue(maxsize=50)
        self.processed_queue = queue.Queue(maxsize=50)

        self.listening = False
        self.processing = False
        self.buddy_interrupted = False
        
        # ✅ NEW: Add interrupt flag for main.py integration
        self.speech_interrupted = False
        self.interrupt_lock = threading.Lock()
        
        # ✅ TURN-BASED: Conversation state management
        self.conversation_state = "WAITING_FOR_INPUT"  # Start waiting for user
        self.buddy_is_speaking = False
        self.user_is_speaking = False
        self.conversation_state_lock = threading.Lock()

        # ✅ TURN-BASED: Separate detection systems
        self.vad_active = False  # VAD only active during Buddy speech
        self.user_speech_detection_active = True  # Always detect user speech start
        self.interrupt_detection_active = False  # Only during Buddy speech

        # Buffers
        self.mic_buffer = deque(maxlen=8000)
        self.speech_buffer = deque(maxlen=240000)
        self.pre_speech_buffer = deque(maxlen=32000)

        # ✅ TURN-BASED: Different thresholds for different modes
        self.user_speech_threshold = USER_SPEECH_THRESHOLD
        self.user_min_speech_frames = USER_MIN_SPEECH_FRAMES
        self.user_max_silence_frames = USER_MAX_SILENCE_FRAMES
        
        self.buddy_interrupt_threshold = BUDDY_INTERRUPT_THRESHOLD
        self.buddy_interrupt_min_frames = BUDDY_INTERRUPT_MIN_FRAMES
        self.buddy_interrupt_grace_period = BUDDY_INTERRUPT_GRACE_PERIOD

        # Counters
        self.speech_frames = 0
        self.silence_frames = 0
        self.interrupt_frames = 0

        self.noise_baseline = 150
        self.noise_samples = deque(maxlen=200)
        self.noise_calibrated = False

        # Stats
        self.interrupts_detected = 0
        self.speeches_processed = 0
        self.user_turns = 0
        self.buddy_turns = 0

        self.running = False
        self.threads = []

        print(f"[FullDuplex] 🔄 TURN-BASED Full Duplex Manager with Interrupt Handling")
        print(f"[FullDuplex] 🎯 User Speech Threshold: {self.user_speech_threshold}")
        print(f"[FullDuplex] 🎯 Buddy Interrupt Threshold: {self.buddy_interrupt_threshold}")
        print(f"[FullDuplex] 🔄 Initial State: {self.conversation_state}")

        # ✅ ADVANCED: Add advanced voice detection thresholds
        self.user_speech_quality_threshold = getattr(globals().get('config', {}), 'USER_SPEECH_QUALITY_THRESHOLD', 0.6)
        self.user_speech_spectral_threshold = getattr(globals().get('config', {}), 'USER_SPEECH_SPECTRAL_THRESHOLD', 0.5)
        self.buddy_interrupt_quality_threshold = getattr(globals().get('config', {}), 'BUDDY_INTERRUPT_QUALITY_THRESHOLD', 0.8)
        self.log_rejection_reasons = getattr(globals().get('config', {}), 'LOG_REJECTION_REASONS', True)

        print(f"[FullDuplex] 🧠 Advanced Voice Detection:")
        print(f"[FullDuplex]   - User Quality Threshold: {self.user_speech_quality_threshold}")
        print(f"[FullDuplex]   - User Spectral Threshold: {self.user_speech_spectral_threshold}")
        print(f"[FullDuplex]   - Interrupt Quality Threshold: {self.buddy_interrupt_quality_threshold}")

    # ✅ NEW: Interrupt flag management
    def reset_interrupt_flag(self):
        """Reset the interrupt flag"""
        with self.interrupt_lock:
            self.speech_interrupted = False
            print("[FullDuplex] 🔄 Interrupt flag reset")

    def set_interrupt_flag(self):
        """Set the interrupt flag"""
        with self.interrupt_lock:
            self.speech_interrupted = True
            print("[FullDuplex] ⚠️ Interrupt flag set")

    def is_speech_interrupted(self):
        """Check if speech was interrupted"""
        with self.interrupt_lock:
            return self.speech_interrupted

    def clear_interrupt(self):
        """Clear any pending interrupt"""
        with self.interrupt_lock:
            self.speech_interrupted = False

    def start(self):
        """Start the turn-based manager"""
        if self.running:
            return
        self.running = True
        self.listening = True
        
        # Reset interrupt flag on start
        self.reset_interrupt_flag()
        
        self.threads = [
            threading.Thread(target=self._audio_input_worker, daemon=True),
            threading.Thread(target=self._turn_based_processor, daemon=True),
            threading.Thread(target=self._speech_processor, daemon=True),
            threading.Thread(target=self._conversation_state_manager, daemon=True),
            threading.Thread(target=self._noise_tracker, daemon=True),
        ]
        
        for thread in self.threads:
            thread.start()
        print("[FullDuplex] ✅ TURN-BASED Full duplex started with interrupt handling")

    def stop(self):
        """Stop the turn-based manager"""
        self.running = False
        self.listening = False
        print("[FullDuplex] 🛑 TURN-BASED Full duplex stopped")

    def add_audio_input(self, audio_chunk):
        """Add audio input with turn-based processing"""
        if not self.listening:
            return
        try:
            self.pre_speech_buffer.extend(audio_chunk)
            
            # ✅ TURN-BASED AEC: Only when Buddy speaking
            with self.conversation_state_lock:
                if self.buddy_is_speaking and AEC_ONLY_DURING_BUDDY_SPEECH:
                    processed_chunk = smart_aec.process_microphone_input(audio_chunk)
                else:
                    processed_chunk = audio_chunk  # Raw audio during user turn
            
            if not self.input_queue.full():
                self.input_queue.put(processed_chunk)
            self.mic_buffer.extend(processed_chunk)
            
        except Exception as e:
            if DEBUG:
                print(f"[FullDuplex] Audio input error: {e}")

    def notify_buddy_speaking(self, audio_data):
        """Buddy started speaking - switch to Buddy turn"""
        try:
            print("🔥 DEBUG: notify_buddy_speaking() called!")
            print(f"🔥 DEBUG: Setting conversation_state to BUDDY_RESPONDING")
            print(f"🔥 DEBUG: Current time: {time.time()}")
            
            # Reset interrupt flag when Buddy starts speaking
            self.reset_interrupt_flag()
            
            with self.conversation_state_lock:
                self.conversation_state = "BUDDY_RESPONDING"
                self.buddy_is_speaking = True
                self.user_is_speaking = False
                
                # ✅ TURN SWITCH: Enable VAD for interrupts, disable user speech detection
                self.vad_active = True
                self.user_speech_detection_active = False
                self.interrupt_detection_active = True
                
                self.buddy_turns += 1
                
                # ✅ FIXED: Set buddy speech start time for grace period
                self._buddy_speech_start_time = time.time()
                print(f"🔥 DEBUG: _buddy_speech_start_time set to: {self._buddy_speech_start_time}")
                
            if AEC_ENABLED:
                smart_aec.update_reference(audio_data)
                
            print(f"[FullDuplex] 🔄 TURN SWITCH: Buddy speaking (Turn #{self.buddy_turns})")
            print(f"[FullDuplex] 📊 VAD: ON, User Detection: OFF, Interrupts: ON")
            print(f"[FullDuplex] ⏰ Grace period: {self.buddy_interrupt_grace_period}s")
            
        except Exception as e:
            if DEBUG:
                print(f"[FullDuplex] Notify buddy speaking error: {e}")

    def notify_buddy_stopped_speaking(self):
        """Buddy stopped speaking - switch to user turn"""
        try:
            with self.conversation_state_lock:
                self.conversation_state = "WAITING_FOR_INPUT"
                self.buddy_is_speaking = False
                self.user_is_speaking = False
                
                # ✅ TURN SWITCH: Disable VAD, enable user speech detection
                self.vad_active = False
                self.user_speech_detection_active = True
                self.interrupt_detection_active = False
                
            # ✅ CRITICAL: Reset interrupt flag when Buddy stops speaking
            self.reset_interrupt_flag()
                
            print(f"[FullDuplex] 🔄 TURN SWITCH: Waiting for user input")
            print(f"[FullDuplex] 📊 VAD: OFF, User Detection: ON, Interrupts: OFF")
            
        except Exception as e:
            if DEBUG:
                print(f"[FullDuplex] Notify buddy stopped error: {e}")

    def start_user_turn(self):
        """User started speaking - user turn active"""
        try:
            with self.conversation_state_lock:
                self.conversation_state = "USER_SPEAKING"
                self.user_is_speaking = True
                self.buddy_is_speaking = False
                
                # ✅ USER TURN: No VAD, no interrupts, just capture
                self.vad_active = False
                self.user_speech_detection_active = False
                self.interrupt_detection_active = False
                
                self.user_turns += 1
                
            print(f"[FullDuplex] 🔄 USER TURN: Started (Turn #{self.user_turns})")
            print(f"[FullDuplex] 📊 VAD: OFF, User Detection: OFF, Interrupts: OFF")
            
        except Exception as e:
            if DEBUG:
                print(f"[FullDuplex] Start user turn error: {e}")

    def end_user_turn(self):
        """User finished speaking - process and wait for Buddy"""
        try:
            with self.conversation_state_lock:
                self.conversation_state = "PROCESSING_RESPONSE"
                self.user_is_speaking = False
                
                # ✅ PROCESSING: All detection off while processing
                self.vad_active = False
                self.user_speech_detection_active = False
                self.interrupt_detection_active = False
                
            print(f"[FullDuplex] 🔄 USER TURN: Ended, processing response")
            print(f"[FullDuplex] 📊 VAD: OFF, User Detection: OFF, Interrupts: OFF")
            
        except Exception as e:
            if DEBUG:
                print(f"[FullDuplex] End user turn error: {e}")

    def _audio_input_worker(self):
        """Process audio input"""
        while self.running:
            try:
                audio_chunk = self.input_queue.get(timeout=0.1)
                self.speech_buffer.extend(audio_chunk)
                
                if self.processing:
                    if not hasattr(self, '_captured_speech'):
                        self._captured_speech = []
                    self._captured_speech.extend(audio_chunk)
            except queue.Empty:
                continue
            except Exception as e:
                if DEBUG:
                    print(f"[FullDuplex] Input worker error: {e}")

    def _turn_based_processor(self):
        """✅ SMART DETECTION: Turn-based processor with room-scale detection for Daveydrz"""
        consecutive_silence_frames = 0
        last_debug_time = 0

        print("[FullDuplex] 🧠 SMART PROCESSOR: Room-scale detection enabled")

        while self.running:
            try:
                if len(self.speech_buffer) < 160:
                    time.sleep(0.01)
                    continue
                
                chunk = np.array(list(self.speech_buffer)[-160:])
                current_time = time.time()
                
                with self.conversation_state_lock:
                    state = self.conversation_state
                    vad_active = self.vad_active
                    user_detection_active = self.user_speech_detection_active
                    interrupt_active = self.interrupt_detection_active

                # ✅ VOICE ANALYSIS WITH SMART DETECTION
                try:
                    from audio.voice_analyzer import voice_analyzer
                    if voice_analyzer:
                        is_voice, voice_score, details = voice_analyzer.analyze_audio(
                            chunk, is_buddy_speaking=(state == "BUDDY_RESPONDING")
                        )
                    else:
                        # Fallback with smart detection if available
                        volume = np.abs(chunk).mean()
                        peak = np.max(np.abs(chunk))
                        
                        if SMART_DETECTION_AVAILABLE and state != "BUDDY_RESPONDING":
                            # Use smart detection for user speech
                            should_trigger, detection_info = analyze_speech_detection(chunk, volume)
                            is_voice = should_trigger
                            voice_score = detection_info.get('quality', volume / self.user_speech_threshold)
                            details = {
                                'volume': volume, 
                                'peak': peak, 
                                'combined': voice_score,
                                'smart_detection': True,
                                'smart_tier': detection_info['tier'],
                                'smart_reason': detection_info['reason']
                            }
                        else:
                            # Original detection for interrupts or fallback
                            is_voice = volume > self.user_speech_threshold
                            voice_score = min(1.0, volume / self.user_speech_threshold)
                            details = {'volume': volume, 'peak': peak, 'combined': voice_score}
                            
                except Exception as e:
                    if DEBUG:
                        print(f"[FullDuplex] Voice analysis error: {e}")
                    # Fallback to simple detection
                    volume = np.abs(chunk).mean()
                    peak = np.max(np.abs(chunk))
                    is_voice = volume > self.user_speech_threshold
                    voice_score = min(1.0, volume / self.user_speech_threshold)
                    details = {'volume': volume, 'peak': peak, 'combined': voice_score}

                # Extract volume for legacy compatibility
                volume = details.get('volume', np.abs(chunk).mean())
                peak = details.get('peak', np.max(np.abs(chunk)))

                # ✅ STATE 1: WAITING_FOR_INPUT - SMART DETECTION INTEGRATED
                if state == "WAITING_FOR_INPUT" and user_detection_active:
                    if SMART_DETECTION_AVAILABLE and 'smart_detection' in details:
                        # Use smart detection result
                        speech_detected = is_voice
                        if speech_detected:
                            detection_method = f"SMART-{details['smart_tier'].upper()}"
                        else:
                            detection_method = "SMART-REJECTED"
                    else:
                        # Fallback to calibrated detection for YOUR voice profile
                        # 🎯 CALIBRATED: Background ~500, Others ~1100, YOU ~5000+, score ~0.62+
                        background_level = 1200        # Above others talking
                        your_voice_level = 3500        # Well below your typical 5000
                        combined_threshold = 0.55      # Just below your typical 0.62+
                        instant_level = 4500           # Your typical speaking volume
                        
                        # Multiple detection methods calibrated to YOUR voice
                        instant_trigger = volume > instant_level  # Your strong voice
                        volume_trigger = volume > your_voice_level  # Clear voice detection
                        quality_trigger = voice_score > combined_threshold and volume > background_level  # Quality + volume
                        
                        speech_detected = instant_trigger or volume_trigger or quality_trigger
                        detection_method = "INSTANT" if instant_trigger else ("VOLUME" if volume_trigger else "QUALITY")
                    
                    if speech_detected:
                        self.speech_frames += 1
                        
                        if DEBUG and current_time - last_debug_time > 0.5:
                            print(f"🎯 [TURN] YOUR speech building ({detection_method}): {self.speech_frames}/{self.user_min_speech_frames} "
                                  f"(score:{voice_score:.2f}, vol:{volume:.0f})")
                            last_debug_time = current_time
                        
                        if self.speech_frames >= self.user_min_speech_frames:
                            print(f"\n🎯 [FullDuplex] 🎤 YOUR SPEECH DETECTED! ({detection_method}, score:{voice_score:.2f}, vol:{volume:.0f})")
                            if hasattr(self, 'start_user_turn'):
                                self.start_user_turn()
                            self._start_user_speech_capture()
                            self.speech_frames = 0
                    else:
                        self.speech_frames = max(0, self.speech_frames - 1)
                        
                        # Log rejection reasons
                        if (DEBUG and volume > 1000 and current_time - last_debug_time > 2.0):
                            if SMART_DETECTION_AVAILABLE and 'smart_reason' in details:
                                print(f"🎯 [TURN] ❌ Smart Rejected: {details['smart_reason']}")
                            else:
                                print(f"🎯 [TURN] ❌ Rejected: vol={volume:.0f} (need >3500), score={voice_score:.2f} (need >0.55)")
                            last_debug_time = current_time

                # ✅ STATE 2: USER_SPEAKING - CALIBRATED for when YOU stop talking
                elif state == "USER_SPEAKING":
                    # 🎯 CALIBRATED: YOUR voice is 5000+, others are 1100, background is 500
                    dropped_significantly = volume < 2000    # Well below your voice level
                    back_to_background = volume < 800        # Back to background/others
                    quality_dropped = voice_score < 0.45     # Well below your 0.62+ level
                    very_quiet = volume < 300                # Very quiet
                    
                    # Speech ends when you drop from your strong voice pattern
                    speech_ended = dropped_significantly or very_quiet or (back_to_background and quality_dropped)
                    
                    if speech_ended:
                        consecutive_silence_frames += 1
                        
                        if DEBUG and current_time - last_debug_time > 0.5:
                            print(f"🎯 [TURN] YOU stopping: {consecutive_silence_frames}/{self.user_max_silence_frames} "
                                  f"(score:{voice_score:.2f}, vol:{volume:.0f})")
                            last_debug_time = current_time
                            
                        if consecutive_silence_frames >= self.user_max_silence_frames:
                            print(f"\n🎯 [FullDuplex] 🎤 YOU FINISHED SPEAKING! (vol:{volume:.0f})")
                            self._end_user_speech_capture()
                            if hasattr(self, 'end_user_turn'):
                                self.end_user_turn()
                            consecutive_silence_frames = 0
                    else:
                        consecutive_silence_frames = 0
                        
                        # Debug: Show why speech continues
                        if DEBUG and current_time - last_debug_time > 1.0:
                            print(f"🎯 [TURN] Still speaking: vol={volume:.0f} (>2000), score={voice_score:.2f}")
                            last_debug_time = current_time

                # ✅ STATE 3: BUDDY_RESPONDING - CALIBRATED interrupt detection with flag setting
                elif state == "BUDDY_RESPONDING" and interrupt_active:
                    buddy_speech_time = time.time() - getattr(self, '_buddy_speech_start_time', time.time())
                    
                    # 🔥 SHORTER GRACE PERIOD for faster interrupts
                    grace_period = 0.5  # Reduced from 1.0 to 0.5 seconds
                    
                    if buddy_speech_time > grace_period:
                        # 🎯 CALIBRATED: YOUR interrupt levels (need to be higher than 5000)
                        instant_interrupt_level = 6000        # Higher than your normal speech
                        sustained_interrupt_level = 4000      # Your normal speech level
                        quality_interrupt_threshold = 0.60    # Your typical quality level
                        
                        # Multiple interrupt detection methods
                        instant_interrupt = volume > instant_interrupt_level
                        sustained_interrupt = volume > sustained_interrupt_level
                        quality_interrupt = voice_score > quality_interrupt_threshold and volume > sustained_interrupt_level * 0.8
                        
                        interrupt_detected = instant_interrupt or sustained_interrupt or quality_interrupt
                        
                        if interrupt_detected:
                            self.interrupt_frames += 1
                            
                            if DEBUG:
                                method = "INSTANT" if instant_interrupt else ("SUSTAINED" if sustained_interrupt else "QUALITY")
                                print(f"🎯 [INTERRUPT] {method}: {self.interrupt_frames}/3 "
                                      f"(vol:{volume:.0f}, score:{voice_score:.2f})")
                            
                            # 🔥 LOWER FRAME REQUIREMENT for faster response
                            required_frames = 3  # Only need 3 frames
                            if self.interrupt_frames >= required_frames:
                                method = "INSTANT" if instant_interrupt else ("SUSTAINED" if sustained_interrupt else "QUALITY")
                                print(f"\n🎯 [FullDuplex] ⚡ YOU INTERRUPTING BUDDY! ({method}, vol:{volume:.0f})")
                                
                                # ✅ SET INTERRUPT FLAG for main.py
                                self.set_interrupt_flag()
                                
                                self._handle_interrupt()
                                self.interrupt_frames = 0
                        else:
                            self.interrupt_frames = max(0, self.interrupt_frames - 1)
                            
                            # Show rejections for debugging
                            if DEBUG and volume > 2000 and current_time - last_debug_time > 1.0:
                                print(f"🎯 [INTERRUPT] Rejected: vol={volume:.0f} (need >{sustained_interrupt_level:.0f}), "
                                      f"score={voice_score:.2f}")
                                last_debug_time = current_time
                                
                    else:
                        # During grace period
                        if DEBUG and current_time - last_debug_time > 1.0:
                            remaining = grace_period - buddy_speech_time
                            print(f"🎯 [GRACE] {remaining:.1f}s remaining (vol:{volume:.0f})")
                            last_debug_time = current_time

                # ✅ STATE 4: PROCESSING_RESPONSE - Ignore all input
                elif state == "PROCESSING_RESPONSE":
                    pass

                time.sleep(0.01)
                
            except Exception as e:
                if DEBUG:
                    print(f"[FullDuplex] Turn-based processor error: {e}")

    def _conversation_state_manager(self):
        """Manage conversation state transitions"""
        while self.running:
            try:
                with self.conversation_state_lock:
                    state = self.conversation_state
                
                # State transition logic
                if state == "PROCESSING_RESPONSE":
                    # Check if we should transition back to waiting
                    # This would be triggered by the main conversation loop
                    pass
                
                time.sleep(0.1)
                
            except Exception as e:
                if DEBUG:
                    print(f"[FullDuplex] State manager error: {e}")

    def _start_user_speech_capture(self):
        """Start capturing user speech"""
        self.processing = True
        
        # Add pre-context for better capture
        pre_context_frames = int(SPEECH_PADDING_START * SAMPLE_RATE)
        if len(self.pre_speech_buffer) >= pre_context_frames:
            pre_context = list(self.pre_speech_buffer)[-pre_context_frames:]
        else:
            pre_context = list(self.pre_speech_buffer)
        
        self.speech_buffer.clear()
        if pre_context:
            self.speech_buffer.extend(pre_context)
        
        self._captured_speech = []
        print("🔴 CAPTURING USER SPEECH", end="", flush=True)

    def _end_user_speech_capture(self):
        """End user speech capture and process"""
        if not self.processing:
            return
        
        self.processing = False
        time.sleep(SPEECH_PADDING_END)
        
        # Get captured audio
        audio_data = np.array(getattr(self, '_captured_speech', []), dtype=np.int16)
        
        # Quality checks
        duration = len(audio_data) / SAMPLE_RATE
        volume = np.abs(audio_data).mean()
        
        if duration >= 0.3 and volume > 300:  # Lenient requirements for user speech
            print(f"\n[FullDuplex] ✅ USER SPEECH CAPTURED: {duration:.1f}s (vol:{volume:.0f})")
            self.processed_queue.put(audio_data)
            self.speeches_processed += 1
        else:
            print(f"\n[FullDuplex] ❌ USER SPEECH TOO SHORT: {duration:.1f}s (vol:{volume:.0f})")
        
        self._captured_speech = []

    def _handle_interrupt(self):
        """✅ FIXED: Handle interrupt and reset flag properly"""
        self.interrupts_detected += 1
        self.buddy_interrupted = True
        
        print(f"[FullDuplex] ⚡ INTERRUPT #{self.interrupts_detected} - STOPPING AUDIO")
        
        try:
            # ✅ STOP AUDIO IMMEDIATELY
            try:
                from audio.output import emergency_stop_all_audio
                emergency_stop_all_audio()
                print("[FullDuplex] 🚨 Emergency stop called")
            except ImportError:
                from audio.output import stop_audio_playback, clear_audio_queue
                print("[FullDuplex] 🛑 Stopping audio immediately")
                stop_audio_playback()
                clear_audio_queue()
            
            # ✅ RESET CONVERSATION STATE
            with self.conversation_state_lock:
                print("[FullDuplex] 🔄 Resetting state after interrupt")
                self.conversation_state = "WAITING_FOR_INPUT"
                self.buddy_is_speaking = False
                self.user_is_speaking = False
                
                # Reset all detection systems
                self.vad_active = False
                self.user_speech_detection_active = True
                self.interrupt_detection_active = False
            
            # ✅ CRITICAL: Reset counters
            self.speech_frames = 0
            self.silence_frames = 0
            self.interrupt_frames = 0
            
            print("[FullDuplex] ✅ State reset complete")
            print(f"[FullDuplex] 📊 VAD: OFF, User Detection: ON, Interrupts: OFF")
            
            # ✅ CRITICAL FIX: Reset interrupt flag AFTER handling interrupt
            # Give audio worker a moment to see the interrupt flag and stop
            time.sleep(0.1)  # 100ms delay to ensure audio stops
            self.reset_interrupt_flag()
            print("[FullDuplex] ⚡ Interrupt handling complete - ready for new input")
            
        except Exception as e:
            if DEBUG:
                print(f"[FullDuplex] Interrupt handling error: {e}")

    def force_reset_to_waiting(self):
        """✅ NEW: Force reset to waiting state (for debugging stuck states)"""
        try:
            with self.conversation_state_lock:
                print("[FullDuplex] 🚨 FORCE RESET: Conversation state to WAITING_FOR_INPUT")
                self.conversation_state = "WAITING_FOR_INPUT"
                self.buddy_is_speaking = False
                self.user_is_speaking = False
                
                # Reset all detection
                self.vad_active = False
                self.user_speech_detection_active = True
                self.interrupt_detection_active = False
                
                # Reset counters
                self.speech_frames = 0
                self.silence_frames = 0
                self.interrupt_frames = 0
                
                # Reset flags
                self.speech_interrupted = False
                self.buddy_interrupted = False
                
            print("[FullDuplex] ✅ FORCE RESET complete - should detect user speech now")
            
        except Exception as e:
            print(f"[FullDuplex] Force reset error: {e}")
    
    def reset_conversation_session(self):
        """Reset voice detection system between conversations to prevent stuck states"""
        try:
            # Reset conversation state
            self.force_reset_to_waiting()
            
            # Reset voice analyzer state if available
            try:
                from audio.voice_analyzer import voice_analyzer
                voice_analyzer.reset_conversation_state()
                print("[FullDuplex] ✅ Voice analyzer state reset")
            except Exception as e:
                print(f"[FullDuplex] ⚠️ Could not reset voice analyzer: {e}")
                
            # Reset smart detection if available
            try:
                from audio.smart_detection_manager import smart_detector
                if hasattr(smart_detector, 'reset_session'):
                    smart_detector.reset_session()
                    print("[FullDuplex] ✅ Smart detection state reset")
            except Exception as e:
                print(f"[FullDuplex] ⚠️ Could not reset smart detection: {e}")
                
            print("[FullDuplex] 🔄 Full conversation session reset complete")
            
        except Exception as e:
            print(f"[FullDuplex] ❌ Session reset error: {e}")

    def _noise_tracker(self):
        """Track noise levels"""
        calibration_samples = 0
        while self.running:
            try:
                if len(self.mic_buffer) >= 160:
                    chunk = np.array(list(self.mic_buffer)[-160:])
                    volume = np.abs(chunk).mean()
                    
                    # Only calibrate during quiet periods
                    if self.conversation_state == "WAITING_FOR_INPUT" and not self.processing:
                        self.noise_samples.append(volume)
                        calibration_samples += 1
                        
                        if not self.noise_calibrated and calibration_samples >= 30:
                            self.noise_baseline = np.percentile(self.noise_samples, 70)
                            self.noise_calibrated = True
                            print(f"[FullDuplex] 🎯 Noise calibrated: {self.noise_baseline:.1f}")
                
                time.sleep(0.1)
            except Exception as e:
                if DEBUG:
                    print(f"[FullDuplex] Noise tracker error: {e}")

    def _speech_processor(self):
        """Process captured speech"""
        while self.running:
            try:
                audio_data = self.processed_queue.get(timeout=0.5)
                
                def transcribe_and_handle():
                    import asyncio
                    
                    # ✅ FIX: Create event loop for this thread to handle async transcription
                    try:
                        # Check if there's already an event loop in this thread
                        try:
                            loop = asyncio.get_event_loop()
                            if loop.is_closed():
                                raise RuntimeError("Event loop is closed")
                        except RuntimeError:
                            # No event loop exists, create a new one for this thread
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                            print("[Speech] 🔧 Created new event loop for transcription thread")
                        
                        # Import and run transcription
                        from ai.speech import transcribe_audio
                        
                        if DEBUG:
                            duration = len(audio_data) / SAMPLE_RATE
                            volume = np.abs(audio_data).mean()
                            print(f"[Speech] 🎙️ Transcribing user speech: {duration:.1f}s, vol:{volume:.1f}")
                        
                        text = transcribe_audio(audio_data)
                        
                        if text and len(text.strip()) > 0:
                            print(f"[Speech] 📝 User said: '{text}'")
                            self._handle_transcribed_text(text, audio_data)
                        else:
                            print(f"[Speech] ❌ Empty transcription")
                            # Go back to waiting for input
                            with self.conversation_state_lock:
                                self.conversation_state = "WAITING_FOR_INPUT"
                                self.user_speech_detection_active = True
                                
                    except Exception as e:
                        print(f"[Speech] ❌ Async event loop error: {e}")
                        print("[Speech] ⚠️ Using fallback transcription method")
                        
                        # Fallback: Try to transcribe without async if possible
                        try:
                            from ai.speech import _transcribe_audio_fallback
                            text = _transcribe_audio_fallback(audio_data)
                            if text and len(text.strip()) > 0 and text != "Audio transcription unavailable":
                                print(f"[Speech] 📝 Fallback transcription: '{text}'")
                                self._handle_transcribed_text(text, audio_data)
                            else:
                                print(f"[Speech] ❌ Fallback transcription failed")
                                with self.conversation_state_lock:
                                    self.conversation_state = "WAITING_FOR_INPUT"
                                    self.user_speech_detection_active = True
                        except Exception as fallback_error:
                            print(f"[Speech] ❌ Fallback transcription error: {fallback_error}")
                            with self.conversation_state_lock:
                                self.conversation_state = "WAITING_FOR_INPUT"
                                self.user_speech_detection_active = True
                    
                    finally:
                        # Clean up event loop if we created it
                        try:
                            current_loop = asyncio.get_event_loop()
                            if current_loop and not current_loop.is_running():
                                current_loop.close()
                        except:
                            pass
                
                threading.Thread(target=transcribe_and_handle, daemon=True).start()
                
            except queue.Empty:
                continue
            except Exception as e:
                if DEBUG:
                    print(f"[FullDuplex] Speech processor error: {e}")

    def _handle_transcribed_text(self, text, audio_data):
        """Handle transcribed text"""
        self.last_transcription = (text, audio_data)

    def get_next_speech(self, timeout=0.1):
        """Get next transcribed speech"""
        try:
            if hasattr(self, 'last_transcription'):
                result = self.last_transcription
                delattr(self, 'last_transcription')
                return result
        except:
            pass
        return None

    def get_stats(self):
        """Get statistics"""
        return {
            "running": self.running,
            "conversation_state": getattr(self, 'conversation_state', 'UNKNOWN'),
            "buddy_is_speaking": getattr(self, 'buddy_is_speaking', False),
            "user_is_speaking": getattr(self, 'user_is_speaking', False),
            "vad_active": getattr(self, 'vad_active', False),
            "user_detection_active": getattr(self, 'user_speech_detection_active', False),
            "interrupt_detection_active": getattr(self, 'interrupt_detection_active', False),
            "speech_interrupted": getattr(self, 'speech_interrupted', False),  # ✅ NEW
            "user_turns": getattr(self, 'user_turns', 0),
            "buddy_turns": getattr(self, 'buddy_turns', 0),
            "interrupts_detected": self.interrupts_detected,
            "speeches_processed": self.speeches_processed,
            "noise_calibrated": self.noise_calibrated,
            "noise_baseline": self.noise_baseline,
        }

# Create global instance
try:
    full_duplex_manager = FullDuplexManager()
    print("[FullDuplex] ✅ TURN-BASED Global manager created with interrupt handling - Proper conversation flow")
except Exception as e:
    print(f"[FullDuplex] ❌ Error creating turn-based manager: {e}")
    full_duplex_manager = None