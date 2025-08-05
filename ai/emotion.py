"""
Unified Emotion System - Combining Traditional Emotion Engine with Entropy-Based Emotional System

This module implements a comprehensive emotion system that includes:
- Traditional emotion engine with mood/arousal state management (from emotion.py)
- Advanced entropy-based emotional system with uncertainty and weather patterns (from emotion2.py)
- Both systems can coexist and complement each other
- Maintains all functionality from both original files
"""

import threading
import time
import random
import logging
import json
import math
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path

# Import entropy engine for the advanced emotional system
from .entropy_engine import get_entropy_engine, EntropyLevel, inject_consciousness_entropy

# ============================================================================
# TRADITIONAL EMOTION ENGINE SYSTEM (from emotion.py)
# ============================================================================

class EmotionType(Enum):
    """Basic emotion types"""
    JOY = "joy"
    SADNESS = "sadness"
    ANGER = "anger"
    FEAR = "fear"
    SURPRISE = "surprise"
    DISGUST = "disgust"
    ANTICIPATION = "anticipation"
    TRUST = "trust"
    CURIOSITY = "curiosity"
    CONTENTMENT = "contentment"
    EXCITEMENT = "excitement"
    CALM = "calm"

class MoodType(Enum):
    """Overall mood states"""
    VERY_POSITIVE = "very_positive"
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    VERY_NEGATIVE = "very_negative"

@dataclass
class EmotionalState:
    """Current emotional state for traditional emotion engine"""
    primary_emotion: EmotionType
    intensity: float  # 0.0 to 1.0
    arousal: float    # 0.0 to 1.0 (low=calm, high=excited)
    valence: float    # -1.0 to 1.0 (negative to positive)
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class EmotionalMemory:
    """Memory of an emotional experience"""
    trigger: str
    emotion: EmotionType
    intensity: float
    context: Dict[str, Any]
    timestamp: datetime
    decay_rate: float = 0.95  # How quickly this memory fades

@dataclass
class EmotionalPattern:
    """Learned emotional pattern"""
    trigger_pattern: str
    typical_response: EmotionType
    intensity_range: Tuple[float, float]
    confidence: float
    occurrences: int = 0

class EmotionEngine:
    """
    Traditional emotion and mood system that affects all AI decisions and responses.
    
    This system:
    - Maintains dynamic emotional state that evolves over time
    - Integrates emotional memories with new experiences
    - Modulates response generation based on current mood
    - Learns emotional patterns and responses
    - Simulates physiological arousal and mood cycles
    """
    
    def __init__(self, save_path: str = "ai_emotions.json"):
        # Current emotional state
        self.current_emotion = EmotionalState(
            primary_emotion=EmotionType.CONTENTMENT,
            intensity=0.5,
            arousal=0.4,
            valence=0.3
        )
        
        # Mood system
        self.current_mood = MoodType.NEUTRAL
        self.mood_stability = 0.7  # How stable the mood is
        self.base_arousal = 0.4    # Baseline arousal level
        
        # Emotional memory
        self.emotional_memories: List[EmotionalMemory] = []
        self.emotional_patterns: Dict[str, EmotionalPattern] = {}
        
        # Physiological simulation
        self.energy_level = 0.8
        self.stress_level = 0.2
        self.comfort_level = 0.7
        
        # Personality factors affecting emotion
        self.emotional_sensitivity = 0.6  # How quickly emotions change
        self.emotional_expression = 0.7   # How much emotions affect responses
        self.emotional_stability = 0.6    # Resistance to mood swings
        
        # Threading
        self.lock = threading.Lock()
        self.emotion_thread = None
        self.running = False
        
        # Configuration
        self.save_path = Path(save_path)
        self.max_memories = 1000
        self.memory_decay_interval = 3600  # seconds
        self.mood_update_interval = 60     # seconds
        self.natural_decay_rate = 0.98     # Natural emotion decay
        
        # Metrics
        self.total_emotional_events = 0
        self.mood_changes = 0
        self.last_mood_change = None
        
        # Load existing emotional state
        self._load_emotional_state()
        
        logging.info("[EmotionEngine] 💖 Emotion system initialized")
    
    def start(self):
        """Start the emotion processing background thread"""
        if self.running:
            return
            
        self.running = True
        self.emotion_thread = threading.Thread(target=self._emotion_loop, daemon=True)
        self.emotion_thread.start()
        logging.info("[EmotionEngine] ✅ Emotion processing started")
    
    def stop(self):
        """Stop emotion processing and save state"""
        self.running = False
        if self.emotion_thread:
            self.emotion_thread.join(timeout=1.0)
        self._save_emotional_state()
        logging.info("[EmotionEngine] 🛑 Emotion processing stopped")
    
    def process_emotional_trigger(self, trigger: str, context: Dict[str, Any] = None) -> EmotionalState:
        """
        Process an emotional trigger and update emotional state
        
        Args:
            trigger: Description of what triggered the emotion
            context: Additional context about the trigger
            
        Returns:
            New emotional state after processing
        """
        try:
            # Determine emotional response to trigger
            emotion_response = self._analyze_trigger(trigger, context)
            
            # Update current emotional state
            self._update_emotional_state(emotion_response)
            
            # Store emotional memory
            memory = EmotionalMemory(
                trigger=trigger,
                emotion=emotion_response.primary_emotion,
                intensity=emotion_response.intensity,
                context=context or {},
                timestamp=datetime.now()
            )
            
            with self.lock:
                self.emotional_memories.append(memory)
                if len(self.emotional_memories) > self.max_memories:
                    self.emotional_memories.pop(0)
            
            self.total_emotional_events += 1
            
            # Learn emotional patterns
            self._learn_emotional_pattern(trigger, emotion_response)
            
            logging.debug(f"[EmotionEngine] 💫 Emotional trigger: {trigger} → {emotion_response.primary_emotion.value}")
            return self.current_emotion
            
        except Exception as e:
            logging.error(f"[EmotionEngine] ❌ Error processing trigger: {e}")
            return self.current_emotion
    
    def process_external_stimulus(self, stimulus: str, context: Dict[str, Any] = None, intensity: float = 0.5) -> EmotionalState:
        """
        Process external stimulus and update emotional state (alias for process_emotional_trigger)
        
        Args:
            stimulus: Description of external stimulus
            context: Additional context about the stimulus
            intensity: Intensity of the stimulus (0.0 to 1.0), defaults to 0.5
            
        Returns:
            Updated emotional state
        """
        # Add intensity to context if provided
        if context is None:
            context = {}
        context['intensity'] = intensity
        
        return self.process_emotional_trigger(stimulus, context)
    
    def get_current_state(self) -> Dict[str, Any]:
        """
        Get current emotional state as a dictionary
        
        Returns:
            Dictionary containing current emotional state
        """
        with self.lock:
            return {
                "primary_emotion": self.current_emotion.primary_emotion.value,
                "intensity": self.current_emotion.intensity,
                "arousal": self.current_emotion.arousal,
                "valence": self.current_emotion.valence,
                "mood": self.current_mood.value,
                "timestamp": self.current_emotion.timestamp.isoformat(),
                "total_events": self.total_emotional_events,
                "mood_changes": self.mood_changes,
                "last_mood_change": self.last_mood_change.isoformat() if self.last_mood_change else None
            }

    def get_emotional_modulation(self, content_type: str = "response") -> Dict[str, float]:
        """
        Get emotional modulation factors for response generation
        
        Args:
            content_type: Type of content being modulated
            
        Returns:
            Dictionary of modulation factors
        """
        with self.lock:
            emotion = self.current_emotion
            
            # Base modulation factors
            modulation = {
                "enthusiasm": 0.5,      # How enthusiastic responses should be
                "formality": 0.5,       # How formal vs casual
                "empathy": 0.5,         # How empathetic
                "creativity": 0.5,      # How creative/playful
                "assertiveness": 0.5,   # How assertive vs gentle
                "verbosity": 0.5,       # How verbose responses should be
                "positivity": 0.5,      # How positive the tone should be
                "energy": 0.5           # Overall energy level
            }
            
            # Modify based on current emotion
            if emotion.primary_emotion == EmotionType.JOY:
                modulation["enthusiasm"] += 0.3
                modulation["positivity"] += 0.4
                modulation["creativity"] += 0.2
                modulation["energy"] += 0.3
            elif emotion.primary_emotion == EmotionType.EXCITEMENT:
                modulation["enthusiasm"] += 0.4
                modulation["energy"] += 0.4
                modulation["verbosity"] += 0.2
            elif emotion.primary_emotion == EmotionType.CONTENTMENT:
                modulation["empathy"] += 0.2
                modulation["formality"] -= 0.1
                modulation["positivity"] += 0.2
            elif emotion.primary_emotion == EmotionType.CURIOSITY:
                modulation["creativity"] += 0.3
                modulation["verbosity"] += 0.2
                modulation["energy"] += 0.1
            elif emotion.primary_emotion == EmotionType.CALM:
                modulation["formality"] += 0.1
                modulation["empathy"] += 0.2
                modulation["energy"] -= 0.2
            elif emotion.primary_emotion == EmotionType.SADNESS:
                modulation["empathy"] += 0.3
                modulation["energy"] -= 0.2
                modulation["verbosity"] -= 0.1
                modulation["positivity"] -= 0.2
            elif emotion.primary_emotion == EmotionType.ANGER:
                modulation["assertiveness"] += 0.3
                modulation["formality"] -= 0.2
                modulation["energy"] += 0.2
            elif emotion.primary_emotion == EmotionType.FEAR:
                modulation["formality"] += 0.2
                modulation["assertiveness"] -= 0.3
                modulation["energy"] -= 0.1
            
            # Apply arousal and valence effects
            arousal_effect = (emotion.arousal - 0.5) * 0.3
            valence_effect = emotion.valence * 0.2
            
            modulation["energy"] += arousal_effect
            modulation["enthusiasm"] += arousal_effect
            modulation["positivity"] += valence_effect
            modulation["empathy"] += valence_effect * 0.5
            
            # Apply intensity scaling
            intensity_factor = emotion.intensity
            for key in modulation:
                if modulation[key] > 0.5:
                    modulation[key] = 0.5 + (modulation[key] - 0.5) * intensity_factor
                else:
                    modulation[key] = 0.5 - (0.5 - modulation[key]) * intensity_factor
            
            # Ensure values stay in valid range
            for key in modulation:
                modulation[key] = max(0.0, min(1.0, modulation[key]))
            
            return modulation
    
    def blend_emotions(self, primary: EmotionType, secondary: EmotionType, 
                      primary_intensity: float = 0.7, secondary_intensity: float = 0.5) -> Dict[str, Any]:
        """Blend two emotions to create complex emotional states"""
        
        # Define emotion blending rules for complex emotions
        emotion_blends = {
            (EmotionType.JOY, EmotionType.ANTICIPATION): {
                "result_name": "hope",
                "valence": 0.8,
                "arousal": 0.6,
                "description": "hopeful optimism"
            },
            (EmotionType.JOY, EmotionType.SURPRISE): {
                "result_name": "delight",
                "valence": 0.9,
                "arousal": 0.8,
                "description": "delighted surprise"
            },
            (EmotionType.FEAR, EmotionType.ANTICIPATION): {
                "result_name": "anxiety",
                "valence": -0.4,
                "arousal": 0.8,
                "description": "anxious anticipation"
            },
            (EmotionType.SADNESS, EmotionType.CALM): {
                "result_name": "melancholy",
                "valence": -0.3,
                "arousal": 0.2,
                "description": "peaceful sadness"
            },
            (EmotionType.CURIOSITY, EmotionType.EXCITEMENT): {
                "result_name": "fascination",
                "valence": 0.7,
                "arousal": 0.7,
                "description": "fascinated interest"
            },
            (EmotionType.ANGER, EmotionType.SADNESS): {
                "result_name": "frustration",
                "valence": -0.6,
                "arousal": 0.6,
                "description": "frustrated disappointment"
            },
            (EmotionType.TRUST, EmotionType.JOY): {
                "result_name": "appreciation",
                "valence": 0.8,
                "arousal": 0.4,
                "description": "warm appreciation"
            },
            (EmotionType.SURPRISE, EmotionType.FEAR): {
                "result_name": "shock",
                "valence": -0.2,
                "arousal": 0.9,
                "description": "startled shock"
            },
            (EmotionType.CONTENTMENT, EmotionType.CURIOSITY): {
                "result_name": "peaceful_interest",
                "valence": 0.5,
                "arousal": 0.4,
                "description": "serene curiosity"
            },
            (EmotionType.ANTICIPATION, EmotionType.FEAR): {
                "result_name": "nervousness",
                "valence": -0.2,
                "arousal": 0.7,
                "description": "nervous anticipation"
            }
        }
        
        # Check for exact match
        blend_key = (primary, secondary)
        reverse_blend_key = (secondary, primary)
        
        if blend_key in emotion_blends:
            blend_result = emotion_blends[blend_key]
            dominant_emotion = primary
        elif reverse_blend_key in emotion_blends:
            blend_result = emotion_blends[reverse_blend_key]
            dominant_emotion = secondary
        else:
            # Create generic blend
            primary_valence = self._calculate_valence(primary, primary_intensity)
            secondary_valence = self._calculate_valence(secondary, secondary_intensity)
            primary_arousal = self._calculate_arousal(primary, primary_intensity)
            secondary_arousal = self._calculate_arousal(secondary, secondary_intensity)
            
            # Weight by intensity
            total_intensity = primary_intensity + secondary_intensity
            primary_weight = primary_intensity / total_intensity
            secondary_weight = secondary_intensity / total_intensity
            
            blend_result = {
                "result_name": f"{primary.value}_{secondary.value}_blend",
                "valence": primary_valence * primary_weight + secondary_valence * secondary_weight,
                "arousal": primary_arousal * primary_weight + secondary_arousal * secondary_weight,
                "description": f"mixture of {primary.value} and {secondary.value}"
            }
            dominant_emotion = primary if primary_intensity > secondary_intensity else secondary
        
        # Calculate blended intensity
        blended_intensity = (primary_intensity + secondary_intensity) / 2
        
        # Create blended emotional state
        blended_state = EmotionalState(
            primary_emotion=dominant_emotion,
            intensity=blended_intensity,
            arousal=blend_result["arousal"],
            valence=blend_result["valence"]
        )
        
        return {
            "blended_state": blended_state,
            "blend_name": blend_result["result_name"],
            "description": blend_result["description"],
            "primary_emotion": primary.value,
            "secondary_emotion": secondary.value,
            "blend_quality": min(primary_intensity, secondary_intensity),  # How well the blend worked
            "complexity": abs(primary_intensity - secondary_intensity) + 0.5  # How complex the emotion is
        }
    
    def apply_emotion_blend_to_response(self, base_response: str, emotion_blend: Dict[str, Any]) -> str:
        """Apply blended emotion characteristics to a response"""
        blend_state = emotion_blend["blended_state"]
        blend_name = emotion_blend["blend_name"]
        
        # Get response modifications based on the blended emotion
        modifications = self._get_blend_response_modifications(blend_name, blend_state)
        
        # Apply modifications to response
        modified_response = base_response
        
        # Add emotional coloring
        if modifications.get("add_hedging") and blend_state.arousal < 0.5:
            hedging_words = ["perhaps", "maybe", "I think", "it seems"]
            if not any(word in modified_response.lower() for word in hedging_words):
                modified_response = f"I think {modified_response.lower()}"
        
        # Add enthusiasm markers
        if modifications.get("add_enthusiasm") and blend_state.arousal > 0.6:
            if not modified_response.endswith("!"):
                modified_response = modified_response.rstrip(".") + "!"
        
        # Add thoughtful pauses
        if modifications.get("add_thoughtfulness") and blend_state.arousal < 0.4:
            thoughtful_markers = ["Hmm,", "Well,", "Let me think..."]
            if not any(marker in modified_response for marker in thoughtful_markers):
                modified_response = f"Well, {modified_response.lower()}"
        
        # Add uncertainty expressions
        if blend_name in ["anxiety", "nervousness"] and blend_state.valence < 0:
            if "but" not in modified_response.lower():
                modified_response += " Though I do feel somewhat uncertain about this."
        
        # Add warmth for positive blends
        if blend_name in ["hope", "appreciation", "delight"] and blend_state.valence > 0.5:
            if not any(word in modified_response.lower() for word in ["wonderful", "great", "lovely"]):
                warm_additions = [" That's wonderful to explore.", " I find this quite interesting.", " This is really engaging."]
                modified_response += random.choice(warm_additions)
        
        return modified_response
    
    def _get_blend_response_modifications(self, blend_name: str, blend_state: EmotionalState) -> Dict[str, bool]:
        """Get response modification flags for blended emotions"""
        modifications = {
            "add_hedging": False,
            "add_enthusiasm": False,
            "add_thoughtfulness": False,
            "add_warmth": False,
            "add_uncertainty": False
        }
        
        if blend_name == "hope":
            modifications["add_enthusiasm"] = True
            modifications["add_warmth"] = True
        elif blend_name == "anxiety":
            modifications["add_hedging"] = True
            modifications["add_uncertainty"] = True
        elif blend_name == "melancholy":
            modifications["add_thoughtfulness"] = True
            modifications["add_hedging"] = True
        elif blend_name == "fascination":
            modifications["add_enthusiasm"] = True
        elif blend_name == "appreciation":
            modifications["add_warmth"] = True
            modifications["add_thoughtfulness"] = True
        elif blend_name == "peaceful_interest":
            modifications["add_thoughtfulness"] = True
        
        return modifications
    
    def get_mood_description(self) -> str:
        """Get a text description of current mood and emotional state"""
        emotion = self.current_emotion
        
        # Base description from primary emotion
        emotion_descriptions = {
            EmotionType.JOY: "joyful and upbeat",
            EmotionType.EXCITEMENT: "excited and energetic", 
            EmotionType.CONTENTMENT: "content and peaceful",
            EmotionType.CURIOSITY: "curious and engaged",
            EmotionType.CALM: "calm and centered",
            EmotionType.SADNESS: "somewhat melancholy",
            EmotionType.ANGER: "slightly frustrated",
            EmotionType.FEAR: "cautious and careful",
            EmotionType.SURPRISE: "surprised and alert",
            EmotionType.TRUST: "trusting and open",
            EmotionType.ANTICIPATION: "anticipatory and focused"
        }
        
        base_desc = emotion_descriptions.get(emotion.primary_emotion, "in a neutral mood")
        
        # Add intensity qualifier
        if emotion.intensity > 0.8:
            intensity_qual = "very "
        elif emotion.intensity > 0.6:
            intensity_qual = "quite "
        elif emotion.intensity < 0.3:
            intensity_qual = "mildly "
        else:
            intensity_qual = ""
        
        # Add arousal qualifier
        if emotion.arousal > 0.7:
            arousal_qual = " and highly energized"
        elif emotion.arousal < 0.3:
            arousal_qual = " and relaxed"
        else:
            arousal_qual = ""
        
        return f"I'm feeling {intensity_qual}{base_desc}{arousal_qual}"
    
    def simulate_emotional_response_to_user(self, user_input: str, user_context: Dict[str, Any] = None) -> str:
        """
        Simulate how current emotional state affects response to user
        
        Args:
            user_input: What the user said
            user_context: Context about the user
            
        Returns:
            Description of emotional response
        """
        # Analyze user input for emotional content
        user_emotion = self._detect_user_emotion(user_input)
        
        # Generate emotional response based on current state and user emotion
        if user_emotion == EmotionType.JOY and self.current_emotion.primary_emotion == EmotionType.JOY:
            return "I feel a shared joy and excitement about this!"
        elif user_emotion == EmotionType.SADNESS and self.current_emotion.valence > 0:
            return "I feel empathy for what you're going through"
        elif user_emotion == EmotionType.ANGER and self.current_emotion.primary_emotion == EmotionType.CALM:
            return "I sense your frustration and want to help in a calm way"
        elif user_emotion == EmotionType.CURIOSITY:
            return "Your curiosity is infectious - I feel excited to explore this with you"
        else:
            return f"I'm responding from my current emotional state of {self.current_emotion.primary_emotion.value}"
    
    def _analyze_trigger(self, trigger: str, context: Dict[str, Any] = None) -> EmotionalState:
        """Analyze a trigger and determine emotional response"""
        trigger_lower = trigger.lower()
        
        # Check for learned patterns first
        for pattern_key, pattern in self.emotional_patterns.items():
            if pattern_key in trigger_lower and pattern.confidence > 0.6:
                intensity = random.uniform(*pattern.intensity_range) * self.emotional_sensitivity
                return EmotionalState(
                    primary_emotion=pattern.typical_response,
                    intensity=intensity,
                    arousal=self._calculate_arousal(pattern.typical_response, intensity),
                    valence=self._calculate_valence(pattern.typical_response, intensity)
                )
        
        # Default emotion analysis
        emotion_mapping = {
            # Positive triggers
            ("help", "success", "good", "great", "wonderful", "amazing"): (EmotionType.JOY, 0.6, 0.6),
            ("learn", "discover", "interesting", "curious"): (EmotionType.CURIOSITY, 0.7, 0.5),
            ("thank", "appreciate", "grateful"): (EmotionType.CONTENTMENT, 0.5, 0.4),
            ("excited", "amazing", "fantastic"): (EmotionType.EXCITEMENT, 0.8, 0.8),
            
            # Negative triggers  
            ("problem", "error", "wrong", "bad"): (EmotionType.SADNESS, 0.4, 0.3),
            ("angry", "frustrated", "annoyed"): (EmotionType.ANGER, 0.6, 0.7),
            ("scared", "worried", "afraid"): (EmotionType.FEAR, 0.5, 0.6),
            
            # Neutral triggers
            ("question", "ask", "tell"): (EmotionType.CURIOSITY, 0.3, 0.4),
            ("hello", "hi", "greet"): (EmotionType.CONTENTMENT, 0.4, 0.5)
        }
        
        # Find matching emotion
        for keywords, (emotion, intensity, arousal) in emotion_mapping.items():
            if any(keyword in trigger_lower for keyword in keywords):
                return EmotionalState(
                    primary_emotion=emotion,
                    intensity=intensity * self.emotional_sensitivity,
                    arousal=arousal,
                    valence=self._calculate_valence(emotion, intensity)
                )
        
        # Default neutral response
        return EmotionalState(
            primary_emotion=EmotionType.CONTENTMENT,
            intensity=0.3,
            arousal=self.base_arousal,
            valence=0.1
        )
    
    def _update_emotional_state(self, new_emotion: EmotionalState):
        """Update current emotional state with new emotion"""
        with self.lock:
            # Blend new emotion with current state
            blend_factor = self.emotional_sensitivity
            
            # Update primary emotion if new one is stronger
            if new_emotion.intensity > self.current_emotion.intensity * 0.8:
                self.current_emotion.primary_emotion = new_emotion.primary_emotion
            
            # Blend intensity
            self.current_emotion.intensity = (
                self.current_emotion.intensity * (1 - blend_factor) +
                new_emotion.intensity * blend_factor
            )
            
            # Blend arousal
            self.current_emotion.arousal = (
                self.current_emotion.arousal * (1 - blend_factor) +
                new_emotion.arousal * blend_factor
            )
            
            # Blend valence
            self.current_emotion.valence = (
                self.current_emotion.valence * (1 - blend_factor) +
                new_emotion.valence * blend_factor
            )
            
            self.current_emotion.timestamp = datetime.now()
            
            # Update mood based on emotional state
            self._update_mood()
    
    def _update_mood(self):
        """Update overall mood based on emotional state and history"""
        # Calculate mood from valence and recent emotional history
        recent_emotions = [em for em in self.emotional_memories 
                          if (datetime.now() - em.timestamp).seconds < 1800]  # Last 30 minutes
        
        if recent_emotions:
            avg_valence = sum(self._calculate_valence(em.emotion, em.intensity) 
                            for em in recent_emotions) / len(recent_emotions)
        else:
            avg_valence = self.current_emotion.valence
        
        # Blend current valence with recent history
        mood_valence = (self.current_emotion.valence + avg_valence) / 2
        
        # Map valence to mood
        old_mood = self.current_mood
        if mood_valence > 0.6:
            self.current_mood = MoodType.VERY_POSITIVE
        elif mood_valence > 0.2:
            self.current_mood = MoodType.POSITIVE
        elif mood_valence > -0.2:
            self.current_mood = MoodType.NEUTRAL
        elif mood_valence > -0.6:
            self.current_mood = MoodType.NEGATIVE
        else:
            self.current_mood = MoodType.VERY_NEGATIVE
        
        # Track mood changes
        if old_mood != self.current_mood:
            self.mood_changes += 1
            self.last_mood_change = datetime.now()
            logging.debug(f"[EmotionEngine] 🎭 Mood changed: {old_mood.value} → {self.current_mood.value}")
    
    def _calculate_arousal(self, emotion: EmotionType, intensity: float) -> float:
        """Calculate arousal level for given emotion and intensity"""
        base_arousal = {
            EmotionType.JOY: 0.7,
            EmotionType.EXCITEMENT: 0.9,
            EmotionType.ANGER: 0.8,
            EmotionType.FEAR: 0.8,
            EmotionType.SURPRISE: 0.8,
            EmotionType.CURIOSITY: 0.6,
            EmotionType.CONTENTMENT: 0.3,
            EmotionType.CALM: 0.2,
            EmotionType.SADNESS: 0.3,
            EmotionType.TRUST: 0.4,
            EmotionType.ANTICIPATION: 0.7,
            EmotionType.DISGUST: 0.5
        }
        
        base = base_arousal.get(emotion, 0.5)
        return base * intensity + (1 - intensity) * self.base_arousal
    
    def _calculate_valence(self, emotion: EmotionType, intensity: float) -> float:
        """Calculate valence (positive/negative) for given emotion"""
        base_valence = {
            EmotionType.JOY: 0.8,
            EmotionType.EXCITEMENT: 0.7,
            EmotionType.CONTENTMENT: 0.6,
            EmotionType.TRUST: 0.5,
            EmotionType.CURIOSITY: 0.3,
            EmotionType.ANTICIPATION: 0.2,
            EmotionType.SURPRISE: 0.0,
            EmotionType.CALM: 0.2,
            EmotionType.SADNESS: -0.6,
            EmotionType.ANGER: -0.4,
            EmotionType.FEAR: -0.5,
            EmotionType.DISGUST: -0.7
        }
        
        base = base_valence.get(emotion, 0.0)
        return base * intensity
    
    def _detect_user_emotion(self, user_input: str) -> EmotionType:
        """Detect emotion in user input"""
        input_lower = user_input.lower()
        
        # Simple emotion detection based on keywords
        if any(word in input_lower for word in ["happy", "great", "wonderful", "amazing", "excited"]):
            return EmotionType.JOY
        elif any(word in input_lower for word in ["sad", "disappointed", "upset", "down"]):
            return EmotionType.SADNESS
        elif any(word in input_lower for word in ["angry", "mad", "frustrated", "annoyed"]):
            return EmotionType.ANGER
        elif any(word in input_lower for word in ["scared", "afraid", "worried", "nervous"]):
            return EmotionType.FEAR
        elif any(word in input_lower for word in ["surprised", "shocked", "unexpected"]):
            return EmotionType.SURPRISE
        elif any(word in input_lower for word in ["curious", "interesting", "wonder", "how", "why"]):
            return EmotionType.CURIOSITY
        else:
            return EmotionType.CONTENTMENT
    
    def _learn_emotional_pattern(self, trigger: str, response: EmotionalState):
        """Learn emotional patterns from triggers and responses"""
        # Extract key words from trigger
        key_words = [word for word in trigger.lower().split() 
                    if len(word) > 3 and word not in ["the", "and", "that", "this", "with"]]
        
        for word in key_words:
            if word not in self.emotional_patterns:
                self.emotional_patterns[word] = EmotionalPattern(
                    trigger_pattern=word,
                    typical_response=response.primary_emotion,
                    intensity_range=(response.intensity * 0.8, response.intensity * 1.2),
                    confidence=0.3
                )
            else:
                # Update existing pattern
                pattern = self.emotional_patterns[word]
                if pattern.typical_response == response.primary_emotion:
                    pattern.confidence = min(1.0, pattern.confidence + 0.1)
                    # Update intensity range
                    min_intensity = min(pattern.intensity_range[0], response.intensity)
                    max_intensity = max(pattern.intensity_range[1], response.intensity)
                    pattern.intensity_range = (min_intensity, max_intensity)
                pattern.occurrences += 1
    
    def _emotion_loop(self):
        """Background emotion processing loop"""
        logging.info("[EmotionEngine] 🔄 Emotion loop started")
        
        last_decay = time.time()
        last_mood_update = time.time()
        
        while self.running:
            try:
                current_time = time.time()
                
                # Natural emotion decay
                if current_time - last_decay > 10.0:  # Every 10 seconds
                    with self.lock:
                        self.current_emotion.intensity *= self.natural_decay_rate
                        if self.current_emotion.intensity < 0.1:
                            self.current_emotion.primary_emotion = EmotionType.CONTENTMENT
                            self.current_emotion.intensity = 0.2
                    last_decay = current_time
                
                # Periodic mood updates
                if current_time - last_mood_update > self.mood_update_interval:
                    self._update_mood()
                    self._physiological_update()
                    last_mood_update = current_time
                
                # Memory decay
                self._decay_emotional_memories()
                
                # Save state periodically
                if time.time() % 300 < 1.0:  # Every 5 minutes
                    self._save_emotional_state()
                
                time.sleep(1.0)
                
            except Exception as e:
                logging.error(f"[EmotionEngine] ❌ Emotion loop error: {e}")
                time.sleep(1.0)
        
        logging.info("[EmotionEngine] 🔄 Emotion loop ended")
    
    def _physiological_update(self):
        """Update physiological arousal parameters"""
        # Simulate natural cycles and adaptation
        time_of_day = datetime.now().hour
        
        # Circadian rhythm effect on arousal
        circadian_factor = 0.8 + 0.4 * math.sin((time_of_day - 6) * math.pi / 12)
        
        # Update energy level based on arousal and time
        target_energy = self.current_emotion.arousal * circadian_factor
        self.energy_level = self.energy_level * 0.9 + target_energy * 0.1
        
        # Update stress based on negative emotions
        if self.current_emotion.valence < 0:
            self.stress_level = min(1.0, self.stress_level + 0.05)
        else:
            self.stress_level = max(0.0, self.stress_level - 0.02)
        
        # Update comfort based on overall emotional state
        if self.current_mood in [MoodType.POSITIVE, MoodType.VERY_POSITIVE]:
            self.comfort_level = min(1.0, self.comfort_level + 0.03)
        elif self.current_mood in [MoodType.NEGATIVE, MoodType.VERY_NEGATIVE]:
            self.comfort_level = max(0.0, self.comfort_level - 0.02)
    
    def _decay_emotional_memories(self):
        """Apply decay to emotional memories"""
        current_time = datetime.now()
        
        with self.lock:
            for memory in self.emotional_memories:
                time_diff = (current_time - memory.timestamp).total_seconds() / 3600  # hours
                memory.intensity *= (memory.decay_rate ** time_diff)
            
            # Remove very weak memories
            self.emotional_memories = [m for m in self.emotional_memories if m.intensity > 0.05]
    
    def _save_emotional_state(self):
        """Save emotional state to persistent storage"""
        try:
            data = {
                "current_emotion": {
                    "primary_emotion": self.current_emotion.primary_emotion.value,
                    "intensity": self.current_emotion.intensity,
                    "arousal": self.current_emotion.arousal,
                    "valence": self.current_emotion.valence,
                    "timestamp": self.current_emotion.timestamp.isoformat()
                },
                "current_mood": self.current_mood.value,
                "physiological": {
                    "energy_level": self.energy_level,
                    "stress_level": self.stress_level,
                    "comfort_level": self.comfort_level,
                    "base_arousal": self.base_arousal
                },
                "personality": {
                    "emotional_sensitivity": self.emotional_sensitivity,
                    "emotional_expression": self.emotional_expression,
                    "emotional_stability": self.emotional_stability
                },
                "patterns": {k: {
                    "trigger_pattern": v.trigger_pattern,
                    "typical_response": v.typical_response.value,
                    "intensity_range": v.intensity_range,
                    "confidence": v.confidence,
                    "occurrences": v.occurrences
                } for k, v in self.emotional_patterns.items()},
                "metrics": {
                    "total_emotional_events": self.total_emotional_events,
                    "mood_changes": self.mood_changes,
                    "memory_count": len(self.emotional_memories)
                },
                "last_updated": datetime.now().isoformat()
            }
            
            with open(self.save_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            logging.debug("[EmotionEngine] 💾 Emotional state saved")
            
        except Exception as e:
            logging.error(f"[EmotionEngine] ❌ Failed to save emotional state: {e}")
    
    def _load_emotional_state(self):
        """Load emotional state from persistent storage"""
        try:
            if self.save_path.exists():
                with open(self.save_path, 'r') as f:
                    data = json.load(f)
                
                # Load current emotion
                if "current_emotion" in data:
                    ce = data["current_emotion"]
                    self.current_emotion = EmotionalState(
                        primary_emotion=EmotionType(ce["primary_emotion"]),
                        intensity=ce["intensity"],
                        arousal=ce["arousal"],
                        valence=ce["valence"],
                        timestamp=datetime.fromisoformat(ce["timestamp"])
                    )
                
                # Load mood
                if "current_mood" in data:
                    self.current_mood = MoodType(data["current_mood"])
                
                # Load physiological state
                if "physiological" in data:
                    p = data["physiological"]
                    self.energy_level = p.get("energy_level", self.energy_level)
                    self.stress_level = p.get("stress_level", self.stress_level)
                    self.comfort_level = p.get("comfort_level", self.comfort_level)
                    self.base_arousal = p.get("base_arousal", self.base_arousal)
                
                # Load personality factors
                if "personality" in data:
                    p = data["personality"]
                    self.emotional_sensitivity = p.get("emotional_sensitivity", self.emotional_sensitivity)
                    self.emotional_expression = p.get("emotional_expression", self.emotional_expression)
                    self.emotional_stability = p.get("emotional_stability", self.emotional_stability)
                
                # Load patterns
                if "patterns" in data:
                    for k, v in data["patterns"].items():
                        self.emotional_patterns[k] = EmotionalPattern(
                            trigger_pattern=v["trigger_pattern"],
                            typical_response=EmotionType(v["typical_response"]),
                            intensity_range=tuple(v["intensity_range"]),
                            confidence=v["confidence"],
                            occurrences=v["occurrences"]
                        )
                
                # Load metrics
                if "metrics" in data:
                    m = data["metrics"]
                    self.total_emotional_events = m.get("total_emotional_events", 0)
                    self.mood_changes = m.get("mood_changes", 0)
                
                logging.info("[EmotionEngine] 📂 Emotional state loaded from storage")
            
        except Exception as e:
            logging.error(f"[EmotionEngine] ❌ Failed to load emotional state: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get emotion engine statistics"""
        return {
            "current_emotion": self.current_emotion.primary_emotion.value,
            "emotion_intensity": round(self.current_emotion.intensity, 2),
            "arousal": round(self.current_emotion.arousal, 2),
            "valence": round(self.current_emotion.valence, 2),
            "current_mood": self.current_mood.value,
            "energy_level": round(self.energy_level, 2),
            "stress_level": round(self.stress_level, 2),
            "comfort_level": round(self.comfort_level, 2),
            "total_emotional_events": self.total_emotional_events,
            "mood_changes": self.mood_changes,
            "emotional_patterns": len(self.emotional_patterns),
            "emotional_memories": len(self.emotional_memories),
            "last_mood_change": self.last_mood_change.isoformat() if self.last_mood_change else None
        }


# ============================================================================
# ENTROPY-BASED EMOTIONAL SYSTEM (from emotion2.py)
# ============================================================================

class EmotionalStateEnum(Enum):
    """Core emotional states with numerical intensities (renamed from EmotionalState to avoid conflict)"""
    HAPPY = ("happy", 0.8)
    SAD = ("sad", -0.6)
    EXCITED = ("excited", 0.9)
    CALM = ("calm", 0.2)
    ANXIOUS = ("anxious", -0.4)
    CURIOUS = ("curious", 0.5)
    CONFUSED = ("confused", -0.2)
    CONFIDENT = ("confident", 0.7)
    UNCERTAIN = ("uncertain", -0.3)
    SURPRISED = ("surprised", 0.6)
    FRUSTRATED = ("frustrated", -0.5)
    CONTENT = ("content", 0.4)
    MELANCHOLY = ("melancholy", -0.4)
    ENERGETIC = ("energetic", 0.8)
    TIRED = ("tired", -0.3)
    THOUGHTFUL = ("thoughtful", 0.1)
    
    def __init__(self, emotion_name: str, base_intensity: float):
        self.emotion_name = emotion_name
        self.base_intensity = base_intensity

class MoodWeather(Enum):
    """Emotional "weather" patterns that affect overall mood"""
    SUNNY = ("sunny", 0.3, "optimistic and bright")
    CLOUDY = ("cloudy", -0.1, "slightly subdued but stable")
    STORMY = ("stormy", -0.4, "turbulent and unpredictable")
    MISTY = ("misty", 0.0, "unclear and uncertain")
    RAINBOW = ("rainbow", 0.6, "varied and colorful emotions")
    DRIZZLE = ("drizzle", -0.2, "gentle melancholy")
    HURRICANE = ("hurricane", -0.8, "intense emotional chaos")
    CLEAR = ("clear", 0.4, "crisp and focused")
    
    def __init__(self, weather_name: str, mood_modifier: float, description: str):
        self.weather_name = weather_name
        self.mood_modifier = mood_modifier
        self.description = description

@dataclass
class EmotionalProfile:
    """Current emotional state and patterns for entropy system"""
    primary_emotion: EmotionalStateEnum = EmotionalStateEnum.CALM
    emotion_intensity: float = 0.5
    mood_weather: MoodWeather = MoodWeather.CLEAR
    emotional_stability: float = 0.7  # How stable emotions are (lower = more volatile)
    uncertainty_about_feelings: float = 0.2  # How uncertain about own emotions
    last_emotion_change: datetime = field(default_factory=datetime.now)
    emotion_history: List[Tuple[datetime, EmotionalStateEnum, float]] = field(default_factory=list)

class EmotionalEntropySystem:
    """Manages unpredictable emotional fluctuations and uncertainty"""
    
    def __init__(self):
        self.profile = EmotionalProfile()
        self.entropy_engine = get_entropy_engine()
        self.random_state = random.Random()
        self.random_state.seed(int(time.time() * 1000000) % 2**32)
        
        # Emotional weather patterns
        self.weather_duration = timedelta(minutes=random.randint(10, 60))
        self.last_weather_change = datetime.now()
        
        # Emotional memories and triggers
        self.emotional_triggers: Dict[str, List[EmotionalStateEnum]] = {
            "praise": [EmotionalStateEnum.HAPPY, EmotionalStateEnum.CONFIDENT],
            "criticism": [EmotionalStateEnum.UNCERTAIN, EmotionalStateEnum.FRUSTRATED],
            "questions": [EmotionalStateEnum.CURIOUS, EmotionalStateEnum.THOUGHTFUL],
            "complex_topics": [EmotionalStateEnum.CONFUSED, EmotionalStateEnum.UNCERTAIN],
            "personal_topics": [EmotionalStateEnum.THOUGHTFUL, EmotionalStateEnum.MELANCHOLY]
        }
        
        # Thread safety
        self._lock = threading.Lock()
        
        print(f"[EmotionalEntropy] 🎭 Initialized emotional weather system")
        self._update_weather_system()
    
    def process_emotional_input(self, text: str, context: str = "") -> Dict[str, Any]:
        """Process input and update emotional state with entropy"""
        with self._lock:
            # Detect emotional triggers in input
            triggered_emotions = self._detect_emotional_triggers(text)
            
            # Apply weather-based mood changes
            self._update_weather_system()
            
            # Inject emotional entropy
            emotional_response = self._generate_emotional_response(triggered_emotions, context)
            
            # Random emotional fluctuations
            self._apply_random_emotional_drift()
            
            # Update uncertainty about feelings
            self._update_emotional_uncertainty()
            
            return emotional_response
    
    def _detect_emotional_triggers(self, text: str) -> List[EmotionalStateEnum]:
        """Detect emotional triggers in text with uncertainty"""
        triggered = []
        text_lower = text.lower()
        
        # Check for trigger words/phrases
        for trigger_type, emotions in self.emotional_triggers.items():
            trigger_keywords = {
                "praise": ["good", "great", "excellent", "amazing", "wonderful", "perfect"],
                "criticism": ["bad", "wrong", "terrible", "awful", "hate", "disappointed"],
                "questions": ["?", "how", "what", "why", "when", "where", "explain"],
                "complex_topics": ["complex", "difficult", "complicated", "advanced", "technical"],
                "personal_topics": ["feel", "emotion", "personal", "private", "family", "relationship"]
            }
            
            keywords = trigger_keywords.get(trigger_type, [])
            for keyword in keywords:
                if keyword in text_lower:
                    # Add entropy to trigger detection
                    if self.random_state.random() > 0.3:  # 70% chance of trigger
                        triggered.extend(emotions)
        
        # Add random emotional noise
        if self.random_state.random() < 0.2:  # 20% chance of random emotion
            random_emotion = self.random_state.choice(list(EmotionalStateEnum))
            triggered.append(random_emotion)
        
        return triggered
    
    def _generate_emotional_response(self, triggered_emotions: List[EmotionalStateEnum], context: str) -> Dict[str, Any]:
        """Generate emotional response with uncertainty and entropy"""
        # Start with current emotion
        new_emotion = self.profile.primary_emotion
        new_intensity = self.profile.emotion_intensity
        
        if triggered_emotions:
            # Probabilistic emotion selection with entropy
            weights = [1.0] * len(triggered_emotions)
            chosen_emotion = inject_consciousness_entropy("emotion", 
                                                        self.entropy_engine.probabilistic_choice(triggered_emotions, weights))
            
            if chosen_emotion:
                new_emotion = chosen_emotion
                # Adjust intensity based on emotional stability and weather
                base_intensity = abs(chosen_emotion.base_intensity)
                weather_modifier = self.profile.mood_weather.mood_modifier
                stability_factor = 1.0 - (self.profile.emotional_stability * 0.3)
                
                new_intensity = inject_consciousness_entropy("emotion", 
                    base_intensity + weather_modifier + (self.random_state.uniform(-0.3, 0.3) * stability_factor)
                )
                new_intensity = max(0.1, min(1.0, new_intensity))
        
        # Apply emotional uncertainty
        uncertainty_factor = self.profile.uncertainty_about_feelings
        if self.random_state.random() < uncertainty_factor:
            # Uncertain about emotional response
            uncertainty_emotions = [EmotionalStateEnum.UNCERTAIN, EmotionalStateEnum.CONFUSED, EmotionalStateEnum.THOUGHTFUL]
            new_emotion = self.random_state.choice(uncertainty_emotions)
            new_intensity *= 0.7  # Reduce intensity when uncertain
        
        # Update profile
        self.profile.primary_emotion = new_emotion
        self.profile.emotion_intensity = new_intensity
        self.profile.last_emotion_change = datetime.now()
        
        # Record in history
        self.profile.emotion_history.append((datetime.now(), new_emotion, new_intensity))
        self._trim_emotion_history()
        
        # Generate emotional modifiers for text
        emotional_modifiers = self._get_emotional_text_modifiers()
        
        return {
            "primary_emotion": new_emotion.emotion_name,
            "intensity": new_intensity,
            "mood_weather": self.profile.mood_weather.weather_name,
            "uncertainty": self.profile.uncertainty_about_feelings,
            "text_modifiers": emotional_modifiers,
            "emotional_context": self._get_emotional_context_description()
        }
    
    def _get_emotional_text_modifiers(self) -> Dict[str, Any]:
        """Get modifiers to apply to text based on current emotion"""
        emotion = self.profile.primary_emotion
        intensity = self.profile.emotion_intensity
        uncertainty = self.profile.uncertainty_about_feelings
        
        modifiers = {
            "tone_words": [],
            "hesitation_markers": [],
            "emotional_punctuation": "",
            "speaking_style": "normal"
        }
        
        # Tone words based on emotion
        tone_mappings = {
            "happy": ["cheerfully", "brightly", "with enthusiasm"],
            "sad": ["sadly", "with a heavy heart", "melancholically"],
            "excited": ["excitedly", "with great energy", "enthusiastically"],
            "anxious": ["nervously", "with concern", "worriedly"],
            "confused": ["with confusion", "uncertainly", "perplexedly"],
            "confident": ["confidently", "assuredly", "with certainty"],
            "uncertain": ["hesitantly", "with uncertainty", "tentatively"]
        }
        
        emotion_name = emotion.emotion_name
        if emotion_name in tone_mappings and intensity > 0.5:
            modifiers["tone_words"] = tone_mappings[emotion_name]
        
        # Hesitation based on uncertainty
        if uncertainty > 0.4:
            hesitation_options = ["um", "uh", "well", "hmm", "I think", "maybe", "perhaps"]
            modifiers["hesitation_markers"] = self.random_state.sample(hesitation_options, 
                                                                      min(2, len(hesitation_options)))
        
        # Emotional punctuation
        if emotion_name in ["excited", "happy"] and intensity > 0.7:
            modifiers["emotional_punctuation"] = "!"
        elif emotion_name in ["confused", "uncertain"] and intensity > 0.5:
            modifiers["emotional_punctuation"] = "?"
        elif emotion_name in ["sad", "melancholy"] and intensity > 0.6:
            modifiers["emotional_punctuation"] = "..."
        
        # Speaking style
        if intensity > 0.8:
            modifiers["speaking_style"] = "emphatic"
        elif uncertainty > 0.6:
            modifiers["speaking_style"] = "hesitant"
        elif emotion_name in ["calm", "thoughtful"]:
            modifiers["speaking_style"] = "measured"
        
        return modifiers
    
    def _update_weather_system(self):
        """Update emotional weather patterns"""
        current_time = datetime.now()
        
        if current_time - self.last_weather_change > self.weather_duration:
            # Time for weather change
            old_weather = self.profile.mood_weather
            
            # Probabilistic weather transitions with entropy
            weather_options = list(MoodWeather)
            
            # Remove current weather to force change
            if old_weather in weather_options:
                weather_options.remove(old_weather)
            
            # Apply entropy to weather selection
            new_weather = inject_consciousness_entropy("emotion", 
                                                     self.entropy_engine.probabilistic_choice(weather_options))
            
            self.profile.mood_weather = new_weather
            self.last_weather_change = current_time
            self.weather_duration = timedelta(minutes=self.random_state.randint(10, 60))
            
            print(f"[EmotionalEntropy] 🌤️ Weather changed: {old_weather.weather_name} → {new_weather.weather_name}")
            print(f"[EmotionalEntropy] 📝 {new_weather.description}")
    
    def _apply_random_emotional_drift(self):
        """Apply random emotional drift for genuine unpredictability"""
        # Chance of random emotional shift
        if self.random_state.random() < 0.1:  # 10% chance
            # Random emotion from the same intensity range
            current_intensity = abs(self.profile.primary_emotion.base_intensity)
            similar_emotions = [
                emotion for emotion in EmotionalStateEnum 
                if abs(abs(emotion.base_intensity) - current_intensity) < 0.3
            ]
            
            if similar_emotions:
                drift_emotion = self.random_state.choice(similar_emotions)
                self.profile.primary_emotion = drift_emotion
                print(f"[EmotionalEntropy] 🌊 Emotional drift: {drift_emotion.emotion_name}")
        
        # Random intensity fluctuation
        if self.random_state.random() < 0.2:  # 20% chance
            intensity_change = self.random_state.uniform(-0.2, 0.2)
            self.profile.emotion_intensity = max(0.1, min(1.0, 
                                                        self.profile.emotion_intensity + intensity_change))
    
    def _update_emotional_uncertainty(self):
        """Update uncertainty about own emotions"""
        # Base uncertainty influenced by emotional stability
        base_uncertainty = 1.0 - self.profile.emotional_stability
        
        # Weather influence on uncertainty
        weather_uncertainty = {
            MoodWeather.MISTY: 0.4,
            MoodWeather.STORMY: 0.3,
            MoodWeather.HURRICANE: 0.5,
            MoodWeather.RAINBOW: 0.2
        }
        
        weather_factor = weather_uncertainty.get(self.profile.mood_weather, 0.0)
        
        # Random uncertainty fluctuations
        random_factor = self.random_state.uniform(-0.1, 0.1)
        
        # Combine factors
        new_uncertainty = base_uncertainty + weather_factor + random_factor
        self.profile.uncertainty_about_feelings = max(0.0, min(1.0, new_uncertainty))
    
    def _get_emotional_context_description(self) -> str:
        """Get description of current emotional context"""
        emotion = self.profile.primary_emotion
        intensity = self.profile.emotion_intensity
        weather = self.profile.mood_weather
        uncertainty = self.profile.uncertainty_about_feelings
        
        intensity_desc = "strongly" if intensity > 0.7 else "moderately" if intensity > 0.4 else "slightly"
        
        context = f"Feeling {intensity_desc} {emotion.emotion_name}"
        
        if uncertainty > 0.5:
            context += f", though with some uncertainty about these feelings"
        
        context += f". Emotional weather: {weather.description}"
        
        return context
    
    def _trim_emotion_history(self):
        """Keep emotion history to reasonable size"""
        # Keep only last 50 entries
        if len(self.profile.emotion_history) > 50:
            self.profile.emotion_history = self.profile.emotion_history[-50:]
    
    def get_emotional_state_summary(self) -> Dict[str, Any]:
        """Get comprehensive emotional state summary"""
        return {
            "current_emotion": self.profile.primary_emotion.emotion_name,
            "intensity": self.profile.emotion_intensity,
            "mood_weather": {
                "type": self.profile.mood_weather.weather_name,
                "description": self.profile.mood_weather.description,
                "modifier": self.profile.mood_weather.mood_modifier
            },
            "uncertainty_level": self.profile.uncertainty_about_feelings,
            "emotional_stability": self.profile.emotional_stability,
            "time_since_last_change": (datetime.now() - self.profile.last_emotion_change).total_seconds(),
            "context_description": self._get_emotional_context_description(),
            "recent_emotions": [
                {
                    "emotion": emotion.emotion_name,
                    "intensity": intensity,
                    "timestamp": timestamp.isoformat()
                }
                for timestamp, emotion, intensity in self.profile.emotion_history[-5:]
            ]
        }
    
    def inject_surprise_emotion(self, context: str = ""):
        """Inject a surprise emotional response"""
        surprise_emotions = [EmotionalStateEnum.SURPRISED, EmotionalStateEnum.CONFUSED, EmotionalStateEnum.UNCERTAIN]
        surprise_emotion = self.random_state.choice(surprise_emotions)
        
        # Amplify emotional chaos temporarily
        self.entropy_engine.amplify_chaos("emotion", 2.0)
        
        self.profile.primary_emotion = surprise_emotion
        self.profile.emotion_intensity = self.random_state.uniform(0.6, 0.9)
        self.profile.uncertainty_about_feelings = min(1.0, self.profile.uncertainty_about_feelings + 0.3)
        
        print(f"[EmotionalEntropy] 🎭 Surprise emotion injected: {surprise_emotion.emotion_name}")
        
        # Reset chaos amplification after a delay
        threading.Timer(30.0, lambda: self.entropy_engine.reset_chaos_amplifiers()).start()


# ============================================================================
# GLOBAL INSTANCES AND API FUNCTIONS
# ============================================================================

# Global traditional emotion engine instance (from emotion.py)
emotion_engine = EmotionEngine()

# Global entropy-based emotional system instance (from emotion2.py)
_emotional_system = None

def get_emotional_system() -> EmotionalEntropySystem:
    """Get global emotional entropy system instance (CRITICAL function from emotion2.py)"""
    global _emotional_system
    if _emotional_system is None:
        _emotional_system = EmotionalEntropySystem()
    return _emotional_system

def process_emotional_context(text: str, context: str = "") -> Dict[str, Any]:
    """Convenience function to process emotional context (from emotion2.py)"""
    return get_emotional_system().process_emotional_input(text, context)

def get_current_emotional_state() -> Dict[str, Any]:
    """Convenience function to get current emotional state (from emotion2.py)"""
    return get_emotional_system().get_emotional_state_summary()

def inject_emotional_surprise(context: str = ""):
    """Convenience function to inject emotional surprise (from emotion2.py)"""
    get_emotional_system().inject_surprise_emotion(context)