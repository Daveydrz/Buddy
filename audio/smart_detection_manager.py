#!/usr/bin/env python3
"""
Smart Room-Scale Detection Manager for BuddyAI
Personalized detection system based on room profiling
"""

import numpy as np
from typing import Dict, Tuple, Optional
import time

try:
    from config import (
        DETECTION_TIERS, ROOM_BASELINE_NOISE, BACKGROUND_REJECTION_ENABLED,
        MIN_SPEECH_VOLUME, CASCADING_DETECTION, VOICE_QUALITY_FILTERING,
        USER_SPEECH_THRESHOLD_ORIGINAL, ROOM_SCALE_MODE
    )
except ImportError:
    # Fallback if config not updated yet
    ROOM_SCALE_MODE = False
    USER_SPEECH_THRESHOLD_ORIGINAL = 800

class SmartDetectionManager:
    def __init__(self):
        self.room_scale_enabled = ROOM_SCALE_MODE
        self.baseline_noise = ROOM_BASELINE_NOISE if ROOM_SCALE_MODE else 0
        self.detection_history = []
        self.current_tier = "close"
        
        # Output throttling to reduce spam
        self.last_reject_time = 0
        self.reject_message_interval = 3.0  # Show reject message every 3 seconds max
        self.last_reject_reason = None
        
        print(f"🧠 Smart Detection Manager initialized")
        print(f"   Room-scale: {'✅ ON' if self.room_scale_enabled else '❌ OFF'}, "
              f"Baseline: {self.baseline_noise}, "
              f"Tiers: {len(DETECTION_TIERS) if self.room_scale_enabled else 0}")
    
    def analyze_audio_quality(self, audio_data: np.ndarray) -> float:
        """
        Analyze voice quality/signature in audio
        Returns voice energy ratio (0.0 to 1.0)
        """
        if len(audio_data) == 0:
            return 0.0
        
        # FFT analysis for voice frequency content
        fft_data = np.fft.fft(audio_data)
        freqs = np.fft.fftfreq(len(fft_data), 1/16000)  # Assuming 16kHz sample rate
        magnitude = np.abs(fft_data)
        
        # Voice frequency range (human speech)
        voice_low = 80   # Hz
        voice_high = 8000  # Hz
        
        voice_mask = (freqs >= voice_low) & (freqs <= voice_high)
        voice_energy = np.sum(magnitude[voice_mask])
        total_energy = np.sum(magnitude)
        
        voice_ratio = voice_energy / max(total_energy, 1)
        return float(voice_ratio)
    
    def calculate_snr(self, audio_volume: float) -> float:
        """Calculate signal-to-noise ratio vs room baseline"""
        if not self.room_scale_enabled:
            return audio_volume / 100  # Simple fallback
        
        return audio_volume / max(self.baseline_noise, 1)
    
    def determine_distance_tier(self, volume: float, quality: float, snr: float) -> str:
        """
        Determine which distance tier the audio fits
        Returns: "close", "medium", "far", "room", or "background"
        """
        if not self.room_scale_enabled:
            return "close"  # Fallback to original behavior
        
        # Check if it's just background noise
        if volume < MIN_SPEECH_VOLUME:
            return "background"
        
        # Check each tier from closest to farthest
        for tier_name, tier_config in DETECTION_TIERS.items():
            if (volume >= tier_config["volume_threshold"] and 
                quality >= tier_config["quality_threshold"] and
                snr >= tier_config["snr_minimum"]):
                return tier_name
        
        # If it doesn't meet any tier requirements but is above background
        return "background"
    
    def should_trigger_detection(self, audio_data: np.ndarray, volume: float) -> Tuple[bool, Dict]:
        """
        Main detection logic - determines if audio should trigger voice detection
        Returns: (should_trigger, detection_info)
        """
        detection_info = {
            "volume": volume,
            "tier": "unknown",
            "quality": 0.0,
            "snr": 0.0,
            "reason": "unknown",
            "timestamp": time.time()
        }
        
        # If room-scale mode is disabled, use original threshold
        if not self.room_scale_enabled:
            should_trigger = volume >= USER_SPEECH_THRESHOLD_ORIGINAL
            detection_info.update({
                "tier": "original",
                "reason": f"Original threshold: {volume} >= {USER_SPEECH_THRESHOLD_ORIGINAL}"
            })
            return should_trigger, detection_info
        
        # Analyze audio quality
        if VOICE_QUALITY_FILTERING:
            quality = self.analyze_audio_quality(audio_data)
        else:
            quality = 1.0  # Skip quality analysis
        
        # Calculate signal-to-noise ratio
        snr = self.calculate_snr(volume)
        
        # Update detection info
        detection_info.update({
            "quality": quality,
            "snr": snr
        })
        
        # Background rejection check
        if BACKGROUND_REJECTION_ENABLED and volume < MIN_SPEECH_VOLUME:
            detection_info.update({
                "tier": "background",
                "reason": f"Below minimum speech volume: {volume} < {MIN_SPEECH_VOLUME}"
            })
            
            # Throttled output for rejection messages
            current_time = time.time()
            should_show_reject = (
                (current_time - self.last_reject_time) > self.reject_message_interval or
                self.last_reject_reason != "low_volume"
            )
            
            if should_show_reject:
                print(f"🔇 [SD] Rejected: Vol:{volume:.0f} < {MIN_SPEECH_VOLUME}")
                self.last_reject_time = current_time
                self.last_reject_reason = "low_volume"
            
            return False, detection_info
        
        # Determine distance tier
        tier = self.determine_distance_tier(volume, quality, snr)
        detection_info["tier"] = tier
        
        # Check if tier qualifies for detection
        if tier == "background":
            detection_info["reason"] = f"Classified as background noise"
            
            # Throttled output for background noise
            current_time = time.time()
            should_show_reject = (
                (current_time - self.last_reject_time) > self.reject_message_interval or
                self.last_reject_reason != "background"
            )
            
            if should_show_reject:
                print(f"🔇 [SD] Background noise: V:{volume:.0f}")
                self.last_reject_time = current_time
                self.last_reject_reason = "background"
            
            return False, detection_info
        
        # If we reach here, it's valid speech at some distance
        tier_config = DETECTION_TIERS[tier]
        detection_info["reason"] = f"Detected {tier} speech: vol={volume:.0f}, quality={quality:.3f}, snr={snr:.1f}x"
        
        # Update current tier for adaptive behavior
        self.current_tier = tier
        
        # Store in detection history
        self.detection_history.append(detection_info.copy())
        if len(self.detection_history) > 100:  # Keep last 100 detections
            self.detection_history.pop(0)
        
        return True, detection_info
    
    def get_adaptive_threshold(self) -> int:
        """
        Get current adaptive threshold based on recent detection patterns
        """
        if not self.room_scale_enabled:
            return USER_SPEECH_THRESHOLD_ORIGINAL
        
        # Use current tier's threshold
        if self.current_tier in DETECTION_TIERS:
            return DETECTION_TIERS[self.current_tier]["volume_threshold"]
        
        # Fallback to room tier (most permissive)
        return DETECTION_TIERS["room"]["volume_threshold"]
    
    def get_detection_stats(self) -> Dict:
        """Get recent detection statistics"""
        if not self.detection_history:
            return {"total": 0, "tiers": {}}
        
        stats = {"total": len(self.detection_history), "tiers": {}}
        
        for detection in self.detection_history[-20:]:  # Last 20 detections
            tier = detection["tier"]
            if tier not in stats["tiers"]:
                stats["tiers"][tier] = 0
            stats["tiers"][tier] += 1
        
        return stats
    
    def reset_debug_state(self):
        """Reset debug throttling state"""
        self.last_reject_time = 0
        self.last_reject_reason = None

# Global instance
smart_detector = SmartDetectionManager()

def analyze_speech_detection(audio_data: np.ndarray, volume: float) -> Tuple[bool, Dict]:
    """
    Main entry point for smart speech detection
    """
    return smart_detector.should_trigger_detection(audio_data, volume)

def get_current_threshold() -> int:
    """
    Get current adaptive threshold
    """
    return smart_detector.get_adaptive_threshold()