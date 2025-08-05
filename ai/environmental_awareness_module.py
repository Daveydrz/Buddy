"""
Environmental Awareness Module - Full Prosody & Mood Monitoring

This module implements comprehensive environmental awareness including:
- Voice prosody analysis (tone, pitch, rhythm, emotional indicators)
- Passive mood monitoring and trend detection
- Environmental context awareness (time, patterns, atmosphere)
- Subtle emotional state changes detection
- Proactive mood support and intervention
"""

import threading
import time
import logging
from typing import Dict, List, Any, Optional, Callable, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import math

# Try to import numpy, fallback to basic math if not available
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    print("[EnvironmentalAwareness] ⚠️ NumPy not available, using basic audio analysis")

class MoodState(Enum):
    """Detected mood states"""
    VERY_POSITIVE = "very_positive"
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    SLIGHTLY_NEGATIVE = "slightly_negative"
    NEGATIVE = "negative"
    VERY_NEGATIVE = "very_negative"
    MIXED = "mixed"
    UNCERTAIN = "uncertain"

class ProsodyIndicator(Enum):
    """Voice prosody indicators"""
    PITCH_HIGH = "pitch_high"
    PITCH_LOW = "pitch_low"
    PACE_FAST = "pace_fast"
    PACE_SLOW = "pace_slow"
    VOLUME_LOUD = "volume_loud"
    VOLUME_QUIET = "volume_quiet"
    TONE_BRIGHT = "tone_bright"
    TONE_FLAT = "tone_flat"
    RHYTHM_VARIED = "rhythm_varied"
    RHYTHM_MONOTONE = "rhythm_monotone"
    STRESS_DETECTED = "stress_detected"
    FATIGUE_DETECTED = "fatigue_detected"
    EXCITEMENT_DETECTED = "excitement_detected"
    SADNESS_DETECTED = "sadness_detected"

class EnvironmentalContext(Enum):
    """Environmental context types"""
    MORNING_ENERGY = "morning_energy"
    AFTERNOON_FOCUS = "afternoon_focus"
    EVENING_WIND_DOWN = "evening_wind_down"
    WEEKEND_RELAXED = "weekend_relaxed"
    WEEKDAY_BUSY = "weekday_busy"
    QUIET_CONTEMPLATIVE = "quiet_contemplative"
    ACTIVE_ENGAGED = "active_engaged"
    STRESSED_RUSHED = "stressed_rushed"

@dataclass
class ProsodyAnalysis:
    """Analysis of voice prosody"""
    pitch_mean: float
    pitch_variance: float
    pace_words_per_minute: float
    volume_level: float
    emotional_indicators: List[ProsodyIndicator]
    stress_level: float  # 0.0 to 1.0
    energy_level: float  # 0.0 to 1.0
    confidence_level: float  # 0.0 to 1.0
    timestamp: datetime

@dataclass
class MoodTrend:
    """Tracked mood trend over time"""
    start_time: datetime
    end_time: Optional[datetime]
    mood_progression: List[Tuple[datetime, MoodState]]
    trend_direction: str  # "improving", "declining", "stable", "volatile"
    severity: float  # How significant the trend is
    context_factors: List[str]

@dataclass
class EnvironmentalReading:
    """Environmental awareness reading"""
    timestamp: datetime
    context: EnvironmentalContext
    mood_state: MoodState
    prosody_analysis: Optional[ProsodyAnalysis]
    detected_patterns: List[str]
    intervention_suggested: bool = False
    intervention_type: Optional[str] = None
    confidence: float = 0.5

class EnvironmentalAwarenessModule:
    """
    Comprehensive environmental awareness system for voice prosody and mood monitoring.
    
    This module:
    - Continuously analyzes voice prosody for emotional indicators
    - Tracks mood trends and patterns over time
    - Detects subtle environmental and emotional changes
    - Provides proactive support based on detected states
    - Integrates with consciousness for natural responses
    """
    
    def __init__(self, save_path: str = "ai_environmental_awareness.json"):
        # Core monitoring data
        self.prosody_readings: List[ProsodyAnalysis] = []
        self.mood_trends: List[MoodTrend] = []
        self.environmental_readings: List[EnvironmentalReading] = []
        self.save_path = save_path
        
        # Analysis parameters
        self.prosody_analysis_interval = 5.0  # Analyze every 5 seconds during conversation
        self.mood_trend_window = 3600  # 1 hour window for trend analysis
        self.intervention_threshold = 0.7  # Threshold for suggesting intervention
        
        # Current state tracking
        self.current_mood_state = MoodState.NEUTRAL
        self.current_prosody = None
        self.current_environmental_context = EnvironmentalContext.QUIET_CONTEMPLATIVE
        self.last_voice_analysis = datetime.now()
        
        # Pattern detection
        self.conversation_patterns = {}
        self.emotional_baselines = {}
        self.prosody_baselines = {}
        self.user_voice_signature = {}
        
        # Consciousness integration
        self.consciousness_modules = {}
        self.voice_system = None
        self.llm_handler = None
        self.audio_system = None
        
        # Threading
        self.lock = threading.Lock()
        self.monitoring_thread = None
        self.running = False
        
        # Buffered audio for analysis
        self.audio_buffer = []
        self.audio_buffer_size = 1000  # Keep last 1000 audio samples
        
        self._load_awareness_data()
        self._initialize_baselines()
        
        logging.info("[EnvironmentalAwareness] 🌍 Environmental awareness module initialized")
    
    def start(self):
        """Start environmental awareness monitoring"""
        if self.running:
            return
        
        self.running = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        logging.info("[EnvironmentalAwareness] ✅ Environmental monitoring started")
    
    def stop(self):
        """Stop environmental monitoring"""
        self.running = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=2.0)
        self._save_awareness_data()
        logging.info("[EnvironmentalAwareness] 🛑 Environmental monitoring stopped")
    
    def register_consciousness_module(self, name: str, module: Any):
        """Register consciousness module for integration"""
        with self.lock:
            self.consciousness_modules[name] = module
    
    def register_voice_system(self, voice_system: Any):
        """Register voice system for prosody analysis"""
        self.voice_system = voice_system
    
    def register_llm_handler(self, llm_handler: Any):
        """Register LLM handler for enhanced analysis"""
        self.llm_handler = llm_handler
    
    def register_audio_system(self, audio_system: Any):
        """Register audio system for voice analysis"""
        self.audio_system = audio_system
    
    def process_voice_input(self, audio_data: Any, text: str) -> ProsodyAnalysis:
        """Process voice input for prosody analysis"""
        try:
            # Analyze prosody
            prosody = self._analyze_voice_prosody(audio_data, text)
            
            # Update current state
            with self.lock:
                self.prosody_readings.append(prosody)
                self.current_prosody = prosody
                self.last_voice_analysis = datetime.now()
                
                # Limit stored readings
                if len(self.prosody_readings) > 1000:
                    self.prosody_readings = self.prosody_readings[-1000:]
            
            # Update mood state based on prosody
            self._update_mood_state(prosody)
            
            # Check for intervention needs
            self._check_intervention_needs(prosody)
            
            return prosody
            
        except Exception as e:
            logging.error(f"[EnvironmentalAwareness] ❌ Voice processing error: {e}")
            return None
    
    def update_environmental_context(self, context_data: Dict[str, Any]):
        """Update environmental context information"""
        try:
            # Determine context from data
            new_context = self._determine_environmental_context(context_data)
            
            with self.lock:
                if new_context != self.current_environmental_context:
                    logging.info(f"[EnvironmentalAwareness] 🔄 Context changed: {self.current_environmental_context.value} → {new_context.value}")
                    self.current_environmental_context = new_context
            
            # Create environmental reading
            reading = EnvironmentalReading(
                timestamp=datetime.now(),
                context=new_context,
                mood_state=self.current_mood_state,
                prosody_analysis=self.current_prosody,
                detected_patterns=self._detect_current_patterns(),
                confidence=0.8
            )
            
            with self.lock:
                self.environmental_readings.append(reading)
                if len(self.environmental_readings) > 500:
                    self.environmental_readings = self.environmental_readings[-500:]
            
        except Exception as e:
            logging.error(f"[EnvironmentalAwareness] ❌ Context update error: {e}")
    
    def get_current_mood_assessment(self) -> Dict[str, Any]:
        """Get current comprehensive mood assessment"""
        with self.lock:
            recent_prosody = [
                p for p in self.prosody_readings 
                if (datetime.now() - p.timestamp).total_seconds() < 300  # Last 5 minutes
            ]
            
            assessment = {
                'current_mood': self.current_mood_state.value,
                'environmental_context': self.current_environmental_context.value,
                'confidence': 0.5,
                'trend': 'stable',
                'intervention_recommended': False,
                'prosody_indicators': [],
                'time_analysis': self._get_time_based_analysis()
            }
            
            if recent_prosody:
                # Calculate average stress and energy
                avg_stress = sum(p.stress_level for p in recent_prosody) / len(recent_prosody)
                avg_energy = sum(p.energy_level for p in recent_prosody) / len(recent_prosody)
                
                assessment.update({
                    'average_stress': avg_stress,
                    'average_energy': avg_energy,
                    'prosody_indicators': list(set(
                        indicator.value 
                        for p in recent_prosody 
                        for indicator in p.emotional_indicators
                    ))
                })
                
                # Determine trend
                if len(recent_prosody) >= 3:
                    stress_trend = [p.stress_level for p in recent_prosody[-3:]]
                    if stress_trend[-1] > stress_trend[0] + 0.2:
                        assessment['trend'] = 'stress_increasing'
                    elif stress_trend[-1] < stress_trend[0] - 0.2:
                        assessment['trend'] = 'stress_decreasing'
                
                # Check intervention needs
                if avg_stress > 0.7 or any(
                    ProsodyIndicator.STRESS_DETECTED in p.emotional_indicators 
                    for p in recent_prosody[-2:]
                ):
                    assessment['intervention_recommended'] = True
                    assessment['intervention_type'] = 'stress_support'
            
            return assessment
    
    def _monitoring_loop(self):
        """Main environmental monitoring loop"""
        while self.running:
            try:
                current_time = datetime.now()
                
                # Update environmental context based on time
                time_context = self._get_time_based_context(current_time)
                self.update_environmental_context({'time_context': time_context})
                
                # Analyze mood trends
                self._analyze_mood_trends()
                
                # Check for pattern changes
                self._detect_pattern_changes()
                
                # Process environmental awareness
                self._process_environmental_awareness()
                
                # Clean up old data
                self._cleanup_old_data()
                
                time.sleep(30.0)  # Check every 30 seconds
                
            except Exception as e:
                logging.error(f"[EnvironmentalAwareness] ❌ Monitoring loop error: {e}")
                time.sleep(60.0)  # Error recovery
    
    def _analyze_voice_prosody(self, audio_data: Any, text: str) -> ProsodyAnalysis:
        """Analyze voice prosody from audio data"""
        try:
            if not NUMPY_AVAILABLE or audio_data is None:
                # Fallback analysis without numpy
                return self._analyze_prosody_fallback(text)
            
            # Basic audio analysis with numpy
            if hasattr(audio_data, '__len__') and len(audio_data) > 0:
                pitch_data = self._extract_pitch(audio_data)
                if NUMPY_AVAILABLE:
                    # Ensure we have a numpy array and it's not empty
                    if not isinstance(audio_data, np.ndarray):
                        audio_data = np.array(audio_data)
                    if len(audio_data) > 0:
                        volume_level = float(np.mean(np.abs(audio_data)))
                    else:
                        volume_level = 0.5
                else:
                    # Simple volume calculation without numpy
                    volume_level = sum(abs(x) for x in audio_data) / len(audio_data) if (audio_data is not None and len(audio_data) > 0) else 0.5
            else:
                pitch_data = []
                volume_level = 0.5
            
            # Calculate prosody features
            if NUMPY_AVAILABLE and len(pitch_data) > 0:
                pitch_mean = float(np.mean(pitch_data))
                pitch_variance = float(np.var(pitch_data))
            else:
                pitch_mean = 200.0  # Default
                pitch_variance = 50.0
            
            # Estimate speaking pace (words per minute)
            word_count = len(text.split())
            audio_duration = len(audio_data) / 16000 if (audio_data is not None and hasattr(audio_data, '__len__') and len(audio_data) > 0) else 1.0
            pace_wpm = (word_count / max(audio_duration, 0.1)) * 60 if audio_duration > 0 else 150.0
            
            # Detect emotional indicators
            emotional_indicators = self._detect_emotional_indicators(
                pitch_mean, pitch_variance, pace_wpm, volume_level, text
            )
            
            # Calculate composite metrics
            stress_level = self._calculate_stress_level(pitch_variance, pace_wpm, emotional_indicators)
            energy_level = self._calculate_energy_level(volume_level, pace_wpm, pitch_mean)
            confidence_level = self._calculate_confidence_level(volume_level, pitch_variance, pace_wpm)
            
            return ProsodyAnalysis(
                pitch_mean=pitch_mean,
                pitch_variance=pitch_variance,
                pace_words_per_minute=pace_wpm,
                volume_level=volume_level,
                emotional_indicators=emotional_indicators,
                stress_level=stress_level,
                energy_level=energy_level,
                confidence_level=confidence_level,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logging.error(f"[EnvironmentalAwareness] ❌ Prosody analysis error: {e}")
            # Return neutral analysis
            return self._analyze_prosody_fallback(text)
    
    def _analyze_prosody_fallback(self, text: str) -> ProsodyAnalysis:
        """Fallback prosody analysis without audio data"""
        word_count = len(text.split())
        estimated_pace = word_count * 4  # Rough estimate: 4 words per second average
        
        # Text-based emotional analysis
        emotional_indicators = []
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['excited', 'amazing', 'fantastic']):
            emotional_indicators.append(ProsodyIndicator.EXCITEMENT_DETECTED)
        if any(word in text_lower for word in ['tired', 'exhausted']):
            emotional_indicators.append(ProsodyIndicator.FATIGUE_DETECTED)
        if any(word in text_lower for word in ['stressed', 'worried', 'anxious']):
            emotional_indicators.append(ProsodyIndicator.STRESS_DETECTED)
        
        return ProsodyAnalysis(
            pitch_mean=200.0,
            pitch_variance=50.0,
            pace_words_per_minute=max(estimated_pace, 120.0),
            volume_level=0.5,
            emotional_indicators=emotional_indicators,
            stress_level=0.3,
            energy_level=0.5,
            confidence_level=0.5,
            timestamp=datetime.now()
        )
    
    def _extract_pitch(self, audio_data: Any) -> List[float]:
        """Extract pitch information from audio data"""
        try:
            if not NUMPY_AVAILABLE or audio_data is None:
                return [200.0]  # Default pitch
            
            # Simple autocorrelation-based pitch detection
            if hasattr(audio_data, '__len__') and len(audio_data) < 1024:
                return [200.0]  # Default for short audio
            
            # Convert to numpy array if needed
            if NUMPY_AVAILABLE:
                if not isinstance(audio_data, np.ndarray):
                    audio_data = np.array(audio_data)
                
                # Apply window to avoid edge effects
                windowed = audio_data * np.hanning(len(audio_data))
                
                # Autocorrelation
                autocorr = np.correlate(windowed, windowed, mode='full')
                autocorr = autocorr[len(autocorr)//2:]
                
                # Find peaks (basic pitch detection)
                if len(autocorr) > 100:
                    # Look for peaks in reasonable pitch range
                    min_period = 20  # ~800Hz at 16kHz
                    max_period = 200  # ~80Hz at 16kHz
                    
                    search_range = autocorr[min_period:max_period]
                    if len(search_range) > 0 and np.any(search_range):
                        peak_idx = np.argmax(search_range) + min_period
                        pitch = 16000 / peak_idx  # Convert to Hz
                        return [float(pitch)]
            
            return [200.0]  # Default pitch
            
        except Exception as e:
            logging.error(f"[EnvironmentalAwareness] ❌ Pitch extraction error: {e}")
            return [200.0]
    
    def _detect_emotional_indicators(self, pitch_mean: float, pitch_variance: float, 
                                   pace_wpm: float, volume_level: float, text: str) -> List[ProsodyIndicator]:
        """Detect emotional indicators from prosody features"""
        indicators = []
        
        try:
            # Pitch-based indicators
            if pitch_mean > 250:  # High pitch (relative)
                indicators.append(ProsodyIndicator.PITCH_HIGH)
                if pitch_variance > 100:  # High variance with high pitch
                    indicators.append(ProsodyIndicator.EXCITEMENT_DETECTED)
            elif pitch_mean < 150:  # Low pitch
                indicators.append(ProsodyIndicator.PITCH_LOW)
                if pitch_variance < 20:  # Low variance with low pitch
                    indicators.append(ProsodyIndicator.SADNESS_DETECTED)
            
            # Pace-based indicators
            if pace_wpm > 180:  # Fast speaking
                indicators.append(ProsodyIndicator.PACE_FAST)
                if pitch_variance > 80:
                    indicators.append(ProsodyIndicator.STRESS_DETECTED)
            elif pace_wpm < 120:  # Slow speaking
                indicators.append(ProsodyIndicator.PACE_SLOW)
                if pitch_variance < 30:
                    indicators.append(ProsodyIndicator.FATIGUE_DETECTED)
            
            # Volume-based indicators
            if volume_level > 0.7:
                indicators.append(ProsodyIndicator.VOLUME_LOUD)
            elif volume_level < 0.3:
                indicators.append(ProsodyIndicator.VOLUME_QUIET)
            
            # Variance-based indicators (emotional range)
            if pitch_variance > 100:
                indicators.append(ProsodyIndicator.RHYTHM_VARIED)
                indicators.append(ProsodyIndicator.TONE_BRIGHT)
            elif pitch_variance < 20:
                indicators.append(ProsodyIndicator.RHYTHM_MONOTONE)
                indicators.append(ProsodyIndicator.TONE_FLAT)
            
            # Text-based emotional cues
            text_lower = text.lower()
            stress_words = ['stressed', 'tired', 'exhausted', 'overwhelmed', 'frustrated']
            excitement_words = ['excited', 'amazing', 'fantastic', 'awesome', 'incredible']
            sadness_words = ['sad', 'depressed', 'down', 'upset', 'disappointed']
            
            if any(word in text_lower for word in stress_words):
                indicators.append(ProsodyIndicator.STRESS_DETECTED)
            if any(word in text_lower for word in excitement_words):
                indicators.append(ProsodyIndicator.EXCITEMENT_DETECTED)
            if any(word in text_lower for word in sadness_words):
                indicators.append(ProsodyIndicator.SADNESS_DETECTED)
            
            return indicators
            
        except Exception as e:
            logging.error(f"[EnvironmentalAwareness] ❌ Emotional indicator detection error: {e}")
            return []
    
    def _calculate_stress_level(self, pitch_variance: float, pace_wpm: float, 
                              indicators: List[ProsodyIndicator]) -> float:
        """Calculate stress level from prosody features"""
        stress = 0.0
        
        # High variance + fast pace indicates stress
        if pitch_variance > 80 and pace_wpm > 170:
            stress += 0.4
        
        # Specific stress indicators
        if ProsodyIndicator.STRESS_DETECTED in indicators:
            stress += 0.5
        
        # Fast pace alone
        if pace_wpm > 200:
            stress += 0.3
        
        # High pitch variance
        if pitch_variance > 120:
            stress += 0.2
        
        return min(1.0, stress)
    
    def _calculate_energy_level(self, volume_level: float, pace_wpm: float, pitch_mean: float) -> float:
        """Calculate energy level from prosody features"""
        energy = 0.5  # Base energy level
        
        # Volume contribution
        energy += (volume_level - 0.5) * 0.4
        
        # Pace contribution
        if pace_wpm > 150:
            energy += (pace_wpm - 150) / 200 * 0.3
        elif pace_wpm < 120:
            energy -= (120 - pace_wpm) / 120 * 0.3
        
        # Pitch contribution
        if pitch_mean > 200:
            energy += (pitch_mean - 200) / 200 * 0.2
        
        return max(0.0, min(1.0, energy))
    
    def _calculate_confidence_level(self, volume_level: float, pitch_variance: float, pace_wpm: float) -> float:
        """Calculate confidence level from prosody features"""
        confidence = 0.5  # Base confidence
        
        # Steady, clear speech indicates confidence
        if 0.4 <= volume_level <= 0.8 and 120 <= pace_wpm <= 180:
            confidence += 0.3
        
        # Appropriate pitch variation
        if 30 <= pitch_variance <= 80:
            confidence += 0.2
        
        # Very quiet or very loud can indicate low confidence
        if volume_level < 0.3 or volume_level > 0.9:
            confidence -= 0.2
        
        # Very fast or very slow pace can indicate nervousness
        if pace_wpm < 100 or pace_wpm > 220:
            confidence -= 0.2
        
        return max(0.0, min(1.0, confidence))
    
    def _update_mood_state(self, prosody: ProsodyAnalysis):
        """Update mood state based on prosody analysis"""
        # Calculate mood score based on prosody
        mood_score = 0.0  # -1.0 (very negative) to +1.0 (very positive)
        
        # Energy and stress balance
        if prosody.energy_level > 0.6 and prosody.stress_level < 0.4:
            mood_score += 0.4  # Good energy, low stress = positive
        elif prosody.energy_level < 0.3:
            mood_score -= 0.3  # Low energy = less positive
        
        if prosody.stress_level > 0.6:
            mood_score -= 0.5  # High stress = negative
        
        # Specific emotional indicators
        positive_indicators = [
            ProsodyIndicator.EXCITEMENT_DETECTED,
            ProsodyIndicator.TONE_BRIGHT,
            ProsodyIndicator.RHYTHM_VARIED
        ]
        negative_indicators = [
            ProsodyIndicator.STRESS_DETECTED,
            ProsodyIndicator.SADNESS_DETECTED,
            ProsodyIndicator.FATIGUE_DETECTED,
            ProsodyIndicator.TONE_FLAT
        ]
        
        for indicator in prosody.emotional_indicators:
            if indicator in positive_indicators:
                mood_score += 0.2
            elif indicator in negative_indicators:
                mood_score -= 0.2
        
        # Convert score to mood state
        if mood_score >= 0.6:
            new_mood = MoodState.VERY_POSITIVE
        elif mood_score >= 0.2:
            new_mood = MoodState.POSITIVE
        elif mood_score >= -0.2:
            new_mood = MoodState.NEUTRAL
        elif mood_score >= -0.4:
            new_mood = MoodState.SLIGHTLY_NEGATIVE
        elif mood_score >= -0.6:
            new_mood = MoodState.NEGATIVE
        else:
            new_mood = MoodState.VERY_NEGATIVE
        
        # Update mood with smoothing
        with self.lock:
            if new_mood != self.current_mood_state:
                logging.info(f"[EnvironmentalAwareness] 😊 Mood change detected: {self.current_mood_state.value} → {new_mood.value}")
                self.current_mood_state = new_mood
                
                # Notify consciousness systems
                self._notify_mood_change(new_mood, prosody)
    
    def _determine_environmental_context(self, context_data: Dict[str, Any]) -> EnvironmentalContext:
        """Determine environmental context from available data"""
        current_time = datetime.now()
        hour = current_time.hour
        weekday = current_time.weekday()
        
        # Time-based context
        if 6 <= hour <= 10:
            base_context = EnvironmentalContext.MORNING_ENERGY
        elif 11 <= hour <= 16:
            base_context = EnvironmentalContext.AFTERNOON_FOCUS
        elif 17 <= hour <= 22:
            base_context = EnvironmentalContext.EVENING_WIND_DOWN
        else:
            base_context = EnvironmentalContext.QUIET_CONTEMPLATIVE
        
        # Weekend adjustment
        if weekday >= 5:  # Saturday, Sunday
            if base_context == EnvironmentalContext.AFTERNOON_FOCUS:
                base_context = EnvironmentalContext.WEEKEND_RELAXED
        else:  # Weekday
            if base_context in [EnvironmentalContext.MORNING_ENERGY, EnvironmentalContext.AFTERNOON_FOCUS]:
                base_context = EnvironmentalContext.WEEKDAY_BUSY
        
        # Adjust based on current mood and stress
        if self.current_prosody:
            if self.current_prosody.stress_level > 0.6:
                base_context = EnvironmentalContext.STRESSED_RUSHED
            elif self.current_prosody.energy_level > 0.7:
                base_context = EnvironmentalContext.ACTIVE_ENGAGED
        
        return base_context
    
    def _get_time_based_context(self, current_time: datetime) -> str:
        """Get time-based environmental context"""
        hour = current_time.hour
        weekday = current_time.weekday()
        
        if weekday >= 5:  # Weekend
            if 6 <= hour <= 10:
                return "weekend_morning"
            elif 11 <= hour <= 16:
                return "weekend_afternoon"
            elif 17 <= hour <= 22:
                return "weekend_evening"
            else:
                return "weekend_night"
        else:  # Weekday
            if 6 <= hour <= 9:
                return "weekday_morning"
            elif 10 <= hour <= 12:
                return "weekday_late_morning"
            elif 13 <= hour <= 17:
                return "weekday_afternoon"
            elif 18 <= hour <= 22:
                return "weekday_evening"
            else:
                return "weekday_night"
    
    def _get_time_based_analysis(self) -> Dict[str, Any]:
        """Get analysis based on current time patterns"""
        current_time = datetime.now()
        
        return {
            'time_of_day': current_time.strftime("%H:%M"),
            'day_of_week': current_time.strftime("%A"),
            'is_weekend': current_time.weekday() >= 5,
            'is_business_hours': 9 <= current_time.hour <= 17 and current_time.weekday() < 5,
            'is_evening': 17 <= current_time.hour <= 22,
            'is_late_night': current_time.hour >= 23 or current_time.hour <= 5
        }
    
    def _analyze_mood_trends(self):
        """Analyze mood trends over time"""
        current_time = datetime.now()
        cutoff_time = current_time - timedelta(seconds=self.mood_trend_window)
        
        # Get recent prosody readings
        recent_readings = [
            p for p in self.prosody_readings 
            if p.timestamp > cutoff_time
        ]
        
        if len(recent_readings) < 3:
            return
        
        # Analyze stress trend
        stress_values = [p.stress_level for p in recent_readings]
        stress_trend = self._calculate_trend(stress_values)
        
        # Analyze energy trend
        energy_values = [p.energy_level for p in recent_readings]
        energy_trend = self._calculate_trend(energy_values)
        
        # Create mood trend if significant
        if abs(stress_trend) > 0.3 or abs(energy_trend) > 0.3:
            trend_direction = "improving" if (energy_trend > 0.2 and stress_trend < -0.2) else \
                            "declining" if (energy_trend < -0.2 or stress_trend > 0.2) else \
                            "volatile" if (abs(stress_trend) > 0.4 or abs(energy_trend) > 0.4) else \
                            "stable"
            
            mood_trend = MoodTrend(
                start_time=recent_readings[0].timestamp,
                end_time=None,
                mood_progression=[(p.timestamp, self.current_mood_state) for p in recent_readings[-5:]],
                trend_direction=trend_direction,
                severity=max(abs(stress_trend), abs(energy_trend)),
                context_factors=[self.current_environmental_context.value]
            )
            
            with self.lock:
                self.mood_trends.append(mood_trend)
                if len(self.mood_trends) > 50:
                    self.mood_trends = self.mood_trends[-50:]
    
    def _calculate_trend(self, values: List[float]) -> float:
        """Calculate trend direction from series of values"""
        if len(values) < 2:
            return 0.0
        
        # Simple linear trend calculation
        x = list(range(len(values)))
        n = len(values)
        
        sum_x = sum(x)
        sum_y = sum(values)
        sum_xy = sum(x[i] * values[i] for i in range(n))
        sum_x2 = sum(x_val ** 2 for x_val in x)
        
        # Calculate slope
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
        return slope
    
    def _detect_current_patterns(self) -> List[str]:
        """Detect current behavioral and environmental patterns"""
        patterns = []
        
        # Time-based patterns
        current_time = datetime.now()
        hour = current_time.hour
        weekday = current_time.weekday()
        
        if weekday < 5 and 9 <= hour <= 17:
            patterns.append("work_hours")
        elif weekday >= 5:
            patterns.append("weekend")
        
        if hour <= 6 or hour >= 22:
            patterns.append("quiet_hours")
        
        # Mood-based patterns
        if self.current_mood_state in [MoodState.POSITIVE, MoodState.VERY_POSITIVE]:
            patterns.append("positive_mood")
        elif self.current_mood_state in [MoodState.NEGATIVE, MoodState.VERY_NEGATIVE]:
            patterns.append("concerning_mood")
        
        # Prosody-based patterns
        if self.current_prosody:
            if self.current_prosody.stress_level > 0.6:
                patterns.append("high_stress")
            if self.current_prosody.energy_level > 0.7:
                patterns.append("high_energy")
            if self.current_prosody.energy_level < 0.3:
                patterns.append("low_energy")
        
        return patterns
    
    def _detect_pattern_changes(self):
        """Detect changes in patterns that might need attention"""
        # This would implement pattern change detection logic
        # For now, we'll keep it simple
        pass
    
    def _check_intervention_needs(self, prosody: ProsodyAnalysis):
        """Check if intervention or support is needed based on prosody"""
        intervention_needed = False
        intervention_type = None
        
        # High stress intervention
        if prosody.stress_level > 0.8:
            intervention_needed = True
            intervention_type = "high_stress_support"
        
        # Fatigue intervention
        elif (prosody.energy_level < 0.2 and 
              ProsodyIndicator.FATIGUE_DETECTED in prosody.emotional_indicators):
            intervention_needed = True
            intervention_type = "fatigue_support"
        
        # Sadness intervention
        elif ProsodyIndicator.SADNESS_DETECTED in prosody.emotional_indicators:
            intervention_needed = True
            intervention_type = "emotional_support"
        
        if intervention_needed:
            self._trigger_intervention(intervention_type, prosody)
    
    def _trigger_intervention(self, intervention_type: str, prosody: ProsodyAnalysis):
        """Trigger appropriate intervention based on detected needs"""
        try:
            # Notify consciousness systems about intervention need
            if 'self_motivation' in self.consciousness_modules:
                sm = self.consciousness_modules['self_motivation']
                if hasattr(sm, 'add_concern_indicator'):
                    severity = prosody.stress_level if intervention_type == "high_stress_support" else 0.6
                    sm.add_concern_indicator(f"Detected {intervention_type}", severity)
            
            # Request attention from global workspace
            if 'global_workspace' in self.consciousness_modules:
                gw = self.consciousness_modules['global_workspace']
                if hasattr(gw, 'request_attention'):
                    from ai.global_workspace import AttentionPriority, ProcessingMode
                    
                    gw.request_attention(
                        "environmental_awareness",
                        f"Intervention needed: {intervention_type}",
                        AttentionPriority.HIGH,
                        ProcessingMode.CONSCIOUS,
                        tags=['intervention', intervention_type, 'user_support']
                    )
            
            logging.info(f"[EnvironmentalAwareness] 🚨 Intervention triggered: {intervention_type}")
            
        except Exception as e:
            logging.error(f"[EnvironmentalAwareness] ❌ Intervention trigger error: {e}")
    
    def _notify_mood_change(self, new_mood: MoodState, prosody: ProsodyAnalysis):
        """Notify consciousness systems about mood change"""
        try:
            # Update emotion engine
            if 'emotion_engine' in self.consciousness_modules:
                ee = self.consciousness_modules['emotion_engine']
                if hasattr(ee, 'process_emotional_trigger'):
                    ee.process_emotional_trigger(
                        f"mood_change_to_{new_mood.value}",
                        {
                            'prosody_stress': prosody.stress_level,
                            'prosody_energy': prosody.energy_level,
                            'source': 'environmental_awareness'
                        }
                    )
            
            # Add to temporal awareness
            if 'temporal_awareness' in self.consciousness_modules:
                ta = self.consciousness_modules['temporal_awareness']
                if hasattr(ta, 'mark_temporal_event'):
                    ta.mark_temporal_event(
                        f"Mood change detected: {new_mood.value}",
                        significance=0.6,
                        context={'prosody_indicators': [i.value for i in prosody.emotional_indicators]}
                    )
            
        except Exception as e:
            logging.error(f"[EnvironmentalAwareness] ❌ Mood change notification error: {e}")
    
    def _process_environmental_awareness(self):
        """Process overall environmental awareness"""
        # Integrate all awareness data for holistic understanding
        current_time = datetime.now()
        
        # Get recent data
        recent_readings = [
            r for r in self.environmental_readings 
            if (current_time - r.timestamp).total_seconds() < 1800  # Last 30 minutes
        ]
        
        if len(recent_readings) >= 3:
            # Analyze environmental stability
            contexts = [r.context for r in recent_readings]
            mood_states = [r.mood_state for r in recent_readings]
            
            # Check for concerning patterns
            if len(set(mood_states)) == 1 and mood_states[0] in [MoodState.NEGATIVE, MoodState.VERY_NEGATIVE]:
                # Persistent negative mood
                self._handle_persistent_negative_mood()
    
    def _handle_persistent_negative_mood(self):
        """Handle detection of persistent negative mood"""
        try:
            # Trigger concern in self-motivation system
            if 'self_motivation' in self.consciousness_modules:
                sm = self.consciousness_modules['self_motivation']
                if hasattr(sm, 'add_concern_indicator'):
                    sm.add_concern_indicator("Persistent negative mood detected", 0.8)
            
            logging.info("[EnvironmentalAwareness] 😟 Persistent negative mood detected")
            
        except Exception as e:
            logging.error(f"[EnvironmentalAwareness] ❌ Persistent mood handling error: {e}")
    
    def _cleanup_old_data(self):
        """Clean up old monitoring data"""
        current_time = datetime.now()
        cutoff_time = current_time - timedelta(hours=24)
        
        with self.lock:
            # Clean prosody readings
            self.prosody_readings = [
                p for p in self.prosody_readings 
                if p.timestamp > cutoff_time
            ]
            
            # Clean environmental readings
            self.environmental_readings = [
                r for r in self.environmental_readings 
                if r.timestamp > cutoff_time
            ]
            
            # Clean mood trends
            trend_cutoff = current_time - timedelta(hours=6)
            self.mood_trends = [
                t for t in self.mood_trends 
                if t.start_time > trend_cutoff
            ]
    
    def _initialize_baselines(self):
        """Initialize baseline measurements for comparison"""
        self.emotional_baselines = {
            'stress_baseline': 0.3,
            'energy_baseline': 0.5,
            'confidence_baseline': 0.6
        }
        
        self.prosody_baselines = {
            'pitch_mean_baseline': 200.0,
            'pitch_variance_baseline': 50.0,
            'pace_baseline': 150.0,
            'volume_baseline': 0.5
        }
    
    def _save_awareness_data(self):
        """Save environmental awareness data"""
        try:
            data = {
                'current_mood_state': self.current_mood_state.value,
                'current_environmental_context': self.current_environmental_context.value,
                'prosody_readings': [],
                'mood_trends': [],
                'environmental_readings': [],
                'emotional_baselines': self.emotional_baselines,
                'prosody_baselines': self.prosody_baselines,
                'last_save': datetime.now().isoformat()
            }
            
            # Save recent prosody readings
            cutoff = datetime.now() - timedelta(hours=6)
            recent_prosody = [p for p in self.prosody_readings if p.timestamp > cutoff]
            
            for prosody in recent_prosody:
                data['prosody_readings'].append({
                    'pitch_mean': prosody.pitch_mean,
                    'pitch_variance': prosody.pitch_variance,
                    'pace_words_per_minute': prosody.pace_words_per_minute,
                    'volume_level': prosody.volume_level,
                    'emotional_indicators': [i.value for i in prosody.emotional_indicators],
                    'stress_level': prosody.stress_level,
                    'energy_level': prosody.energy_level,
                    'confidence_level': prosody.confidence_level,
                    'timestamp': prosody.timestamp.isoformat()
                })
            
            # Save recent environmental readings
            recent_readings = [r for r in self.environmental_readings if r.timestamp > cutoff]
            for reading in recent_readings:
                data['environmental_readings'].append({
                    'timestamp': reading.timestamp.isoformat(),
                    'context': reading.context.value,
                    'mood_state': reading.mood_state.value,
                    'detected_patterns': reading.detected_patterns,
                    'intervention_suggested': reading.intervention_suggested,
                    'intervention_type': reading.intervention_type,
                    'confidence': reading.confidence
                })
            
            with open(self.save_path, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            logging.error(f"[EnvironmentalAwareness] ❌ Save error: {e}")
    
    def _load_awareness_data(self):
        """Load environmental awareness data"""
        try:
            with open(self.save_path, 'r') as f:
                data = json.load(f)
            
            # Load current states
            self.current_mood_state = MoodState(data.get('current_mood_state', 'neutral'))
            self.current_environmental_context = EnvironmentalContext(
                data.get('current_environmental_context', 'quiet_contemplative')
            )
            
            # Load baselines
            self.emotional_baselines = data.get('emotional_baselines', {})
            self.prosody_baselines = data.get('prosody_baselines', {})
            
            # Load recent data (if needed for continuity)
            # For now, we start fresh with each session
            
            logging.info("[EnvironmentalAwareness] 📚 Loaded environmental awareness data")
            
        except FileNotFoundError:
            logging.info("[EnvironmentalAwareness] 📝 No previous awareness data found, starting fresh")
        except Exception as e:
            logging.error(f"[EnvironmentalAwareness] ❌ Load error: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get environmental awareness statistics"""
        with self.lock:
            recent_prosody = [
                p for p in self.prosody_readings 
                if (datetime.now() - p.timestamp).total_seconds() < 3600
            ]
            
            return {
                'current_mood': self.current_mood_state.value,
                'environmental_context': self.current_environmental_context.value,
                'prosody_readings_count': len(self.prosody_readings),
                'recent_prosody_count': len(recent_prosody),
                'mood_trends_tracked': len(self.mood_trends),
                'environmental_readings_count': len(self.environmental_readings),
                'current_stress_level': self.current_prosody.stress_level if self.current_prosody else 0.0,
                'current_energy_level': self.current_prosody.energy_level if self.current_prosody else 0.5,
                'last_voice_analysis': self.last_voice_analysis.isoformat(),
                'running': self.running,
                'consciousness_modules': list(self.consciousness_modules.keys())
            }


# Global instance
environmental_awareness_module = EnvironmentalAwarenessModule()