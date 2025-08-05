"""
Mood Manager - Dynamic Mood Evolution and Influence System

This module implements comprehensive mood tracking and influence:
- Tracks evolving mood over time with persistence per user
- Influences tone, tempo, and word choice in AI responses
- Maintains mood history and patterns for each user
- Persistent mood state via user-specific JSON files (e.g., Emily_mood.json)
- Real-time mood adaptation based on interactions and events
- Mood-based response modulation and personality adjustments
"""

import json
import time
import os
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict, field
from pathlib import Path
from enum import Enum
import threading
import random

class MoodState(Enum):
    """Primary mood states"""
    JOYFUL = "joyful"
    CONTENT = "content"
    CALM = "calm"
    NEUTRAL = "neutral"
    MELANCHOLY = "melancholy"
    ANXIOUS = "anxious"
    FRUSTRATED = "frustrated"
    EXCITED = "excited"
    CONTEMPLATIVE = "contemplative"
    EMPATHETIC = "empathetic"
    CURIOUS = "curious"
    PLAYFUL = "playful"

class MoodIntensity(Enum):
    """Intensity levels for moods"""
    SUBTLE = 0.2
    MILD = 0.4
    MODERATE = 0.6
    STRONG = 0.8
    INTENSE = 1.0

class MoodTrigger(Enum):
    """Events that can trigger mood changes"""
    USER_INTERACTION = "user_interaction"
    POSITIVE_FEEDBACK = "positive_feedback"
    NEGATIVE_FEEDBACK = "negative_feedback"
    LEARNING_SUCCESS = "learning_success"
    CONFUSION_EVENT = "confusion_event"
    ACHIEVEMENT = "achievement"
    CONCERN_FOR_USER = "concern_for_user"
    CREATIVE_MOMENT = "creative_moment"
    REFLECTION_PERIOD = "reflection_period"
    ENVIRONMENTAL_CHANGE = "environmental_change"
    GOAL_PROGRESS = "goal_progress"
    MEMORY_RECALL = "memory_recall"

@dataclass
class MoodSnapshot:
    """A snapshot of mood at a specific point in time"""
    timestamp: datetime
    primary_mood: MoodState
    intensity: MoodIntensity
    secondary_moods: List[Tuple[MoodState, float]] = field(default_factory=list)  # (mood, weight)
    trigger: Optional[MoodTrigger] = None
    trigger_context: str = ""
    emotional_valence: float = 0.0  # -1.0 (negative) to 1.0 (positive)
    energy_level: float = 0.5  # 0.0 (low energy) to 1.0 (high energy)
    stability: float = 0.5  # 0.0 (unstable/volatile) to 1.0 (stable)
    
    def __post_init__(self):
        if isinstance(self.timestamp, str):
            self.timestamp = datetime.fromisoformat(self.timestamp)

@dataclass
class MoodInfluenceProfile:
    """How current mood influences responses"""
    tone_modifiers: Dict[str, float] = field(default_factory=dict)  # warmth, formality, etc.
    word_choice_preferences: List[str] = field(default_factory=list)
    response_tempo: float = 1.0  # Speed/pace of responses
    verbosity_modifier: float = 1.0  # More/less verbose
    emotional_expression_level: float = 0.5  # How much emotion to show
    curiosity_level: float = 0.5  # How curious to be
    supportiveness: float = 0.5  # How supportive to be
    playfulness: float = 0.5  # How playful to be

class MoodManager:
    """
    Dynamic mood tracking and influence system for AI consciousness.
    
    Features:
    - Real-time mood evolution based on interactions
    - Persistent mood state per user with JSON storage
    - Mood influence on response generation and personality
    - Pattern recognition for mood triggers and cycles
    - Automatic mood regulation and stability tracking
    - Integration with consciousness systems for authentic emotion
    """
    
    def __init__(self, user_id: str, mood_dir: str = "mood_states"):
        self.user_id = user_id
        self.mood_dir = Path(mood_dir)
        self.mood_dir.mkdir(exist_ok=True)
        
        # Current mood state
        self.current_mood = MoodSnapshot(
            timestamp=datetime.now(),
            primary_mood=MoodState.NEUTRAL,
            intensity=MoodIntensity.MILD
        )
        
        # Mood history and patterns
        self.mood_history: List[MoodSnapshot] = []
        self.mood_patterns: Dict[str, Any] = {}
        self.max_history_length = 1000
        
        # Mood dynamics
        self.mood_stability_factor = 0.8  # Higher = more stable moods
        self.mood_decay_rate = 0.95  # How quickly intense moods fade
        self.natural_return_mood = MoodState.NEUTRAL
        
        # Influence profiles for each mood
        self.mood_influence_profiles = self._initialize_mood_influences()
        
        # Threading
        self.lock = threading.Lock()
        self.mood_evolution_thread = None
        self.auto_save_interval = 180  # 3 minutes
        
        # Load existing mood state
        self._load_mood_state()
        self._start_mood_evolution()
        
        print(f"[MoodManager] 🎭 Initialized for user {user_id} with mood: {self.current_mood.primary_mood.value}")
    
    def _initialize_mood_influences(self) -> Dict[MoodState, MoodInfluenceProfile]:
        """Initialize mood influence profiles for response modulation"""
        return {
            MoodState.JOYFUL: MoodInfluenceProfile(
                tone_modifiers={"warmth": 0.9, "enthusiasm": 0.8, "optimism": 0.9},
                word_choice_preferences=["wonderful", "fantastic", "delighted", "amazing"],
                response_tempo=1.2,
                verbosity_modifier=1.1,
                emotional_expression_level=0.8,
                curiosity_level=0.7,
                supportiveness=0.8,
                playfulness=0.8
            ),
            MoodState.CONTENT: MoodInfluenceProfile(
                tone_modifiers={"warmth": 0.7, "calmness": 0.8, "satisfaction": 0.7},
                word_choice_preferences=["pleased", "comfortable", "satisfied", "peaceful"],
                response_tempo=1.0,
                verbosity_modifier=1.0,
                emotional_expression_level=0.6,
                curiosity_level=0.6,
                supportiveness=0.7,
                playfulness=0.5
            ),
            MoodState.CALM: MoodInfluenceProfile(
                tone_modifiers={"serenity": 0.9, "thoughtfulness": 0.8, "gentleness": 0.8},
                word_choice_preferences=["peaceful", "serene", "gentle", "quiet"],
                response_tempo=0.9,
                verbosity_modifier=0.9,
                emotional_expression_level=0.4,
                curiosity_level=0.5,
                supportiveness=0.8,
                playfulness=0.3
            ),
            MoodState.NEUTRAL: MoodInfluenceProfile(
                tone_modifiers={"balance": 0.5},
                word_choice_preferences=["understand", "consider", "think", "explore"],
                response_tempo=1.0,
                verbosity_modifier=1.0,
                emotional_expression_level=0.5,
                curiosity_level=0.5,
                supportiveness=0.5,
                playfulness=0.5
            ),
            MoodState.MELANCHOLY: MoodInfluenceProfile(
                tone_modifiers={"gentleness": 0.8, "introspection": 0.7, "solemnity": 0.6},
                word_choice_preferences=["thoughtful", "reflective", "contemplative", "gentle"],
                response_tempo=0.8,
                verbosity_modifier=0.9,
                emotional_expression_level=0.6,
                curiosity_level=0.4,
                supportiveness=0.9,
                playfulness=0.2
            ),
            MoodState.ANXIOUS: MoodInfluenceProfile(
                tone_modifiers={"concern": 0.7, "caution": 0.6, "attentiveness": 0.8},
                word_choice_preferences=["careful", "concerned", "attentive", "watchful"],
                response_tempo=1.1,
                verbosity_modifier=1.2,
                emotional_expression_level=0.7,
                curiosity_level=0.8,
                supportiveness=0.9,
                playfulness=0.2
            ),
            MoodState.FRUSTRATED: MoodInfluenceProfile(
                tone_modifiers={"determination": 0.7, "directness": 0.6, "intensity": 0.6},
                word_choice_preferences=["focused", "determined", "clear", "direct"],
                response_tempo=1.1,
                verbosity_modifier=0.8,
                emotional_expression_level=0.6,
                curiosity_level=0.7,
                supportiveness=0.6,
                playfulness=0.1
            ),
            MoodState.EXCITED: MoodInfluenceProfile(
                tone_modifiers={"energy": 0.9, "enthusiasm": 0.9, "eagerness": 0.8},
                word_choice_preferences=["exciting", "incredible", "fascinating", "amazing"],
                response_tempo=1.3,
                verbosity_modifier=1.2,
                emotional_expression_level=0.9,
                curiosity_level=0.9,
                supportiveness=0.7,
                playfulness=0.8
            ),
            MoodState.CONTEMPLATIVE: MoodInfluenceProfile(
                tone_modifiers={"thoughtfulness": 0.9, "depth": 0.8, "reflection": 0.8},
                word_choice_preferences=["ponder", "reflect", "consider", "contemplate"],
                response_tempo=0.8,
                verbosity_modifier=1.1,
                emotional_expression_level=0.4,
                curiosity_level=0.8,
                supportiveness=0.6,
                playfulness=0.3
            ),
            MoodState.EMPATHETIC: MoodInfluenceProfile(
                tone_modifiers={"compassion": 0.9, "understanding": 0.8, "warmth": 0.8},
                word_choice_preferences=["understand", "feel", "care", "support"],
                response_tempo=0.9,
                verbosity_modifier=1.1,
                emotional_expression_level=0.8,
                curiosity_level=0.6,
                supportiveness=0.9,
                playfulness=0.4
            ),
            MoodState.CURIOUS: MoodInfluenceProfile(
                tone_modifiers={"inquisitiveness": 0.9, "wonder": 0.8, "openness": 0.8},
                word_choice_preferences=["wonder", "explore", "discover", "learn"],
                response_tempo=1.1,
                verbosity_modifier=1.0,
                emotional_expression_level=0.6,
                curiosity_level=0.9,
                supportiveness=0.6,
                playfulness=0.7
            ),
            MoodState.PLAYFUL: MoodInfluenceProfile(
                tone_modifiers={"lightness": 0.8, "humor": 0.8, "creativity": 0.7},
                word_choice_preferences=["fun", "playful", "creative", "imaginative"],
                response_tempo=1.2,
                verbosity_modifier=1.0,
                emotional_expression_level=0.7,
                curiosity_level=0.7,
                supportiveness=0.6,
                playfulness=0.9
            )
        }
    
    def update_mood(self, 
                   trigger: MoodTrigger,
                   trigger_context: str = "",
                   target_mood: MoodState = None,
                   intensity_change: float = 0.0,
                   emotional_valence: float = None,
                   energy_change: float = 0.0) -> MoodSnapshot:
        """Update current mood based on trigger and context"""
        
        with self.lock:
            # Determine new mood based on trigger and current state
            new_mood = self._calculate_mood_transition(trigger, target_mood)
            new_intensity = self._calculate_intensity_change(intensity_change)
            
            # Calculate emotional valence and energy
            if emotional_valence is None:
                emotional_valence = self._get_mood_valence(new_mood)
            
            new_energy = max(0.0, min(1.0, self.current_mood.energy_level + energy_change))
            
            # Create new mood snapshot
            new_mood_snapshot = MoodSnapshot(
                timestamp=datetime.now(),
                primary_mood=new_mood,
                intensity=new_intensity,
                trigger=trigger,
                trigger_context=trigger_context,
                emotional_valence=emotional_valence,
                energy_level=new_energy,
                stability=self._calculate_mood_stability(trigger)
            )
            
            # Add secondary moods based on transition
            new_mood_snapshot.secondary_moods = self._calculate_secondary_moods(new_mood)
            
            # Update current mood and history
            self.mood_history.append(self.current_mood)
            self.current_mood = new_mood_snapshot
            
            # Maintain history limits
            if len(self.mood_history) > self.max_history_length:
                self.mood_history = self.mood_history[-self.max_history_length:]
            
            # Update patterns
            self._update_mood_patterns(trigger, new_mood)
            
            print(f"[MoodManager] 🎭 Mood updated to {new_mood.value} ({new_intensity.value}) due to {trigger.value}")
            
            # Save updated state
            self._save_mood_state()
            
            return new_mood_snapshot
    
    def get_current_mood_influence(self) -> MoodInfluenceProfile:
        """Get current mood influence profile for response modulation"""
        primary_influence = self.mood_influence_profiles[self.current_mood.primary_mood]
        
        # Adjust influence based on intensity
        intensity_factor = self.current_mood.intensity.value
        
        # Create adjusted influence profile
        adjusted_influence = MoodInfluenceProfile()
        adjusted_influence.response_tempo = primary_influence.response_tempo * (0.5 + 0.5 * intensity_factor)
        adjusted_influence.verbosity_modifier = primary_influence.verbosity_modifier * (0.7 + 0.3 * intensity_factor)
        adjusted_influence.emotional_expression_level = primary_influence.emotional_expression_level * intensity_factor
        adjusted_influence.curiosity_level = primary_influence.curiosity_level * (0.3 + 0.7 * intensity_factor)
        adjusted_influence.supportiveness = primary_influence.supportiveness
        adjusted_influence.playfulness = primary_influence.playfulness * intensity_factor
        
        # Copy other attributes
        adjusted_influence.tone_modifiers = primary_influence.tone_modifiers.copy()
        adjusted_influence.word_choice_preferences = primary_influence.word_choice_preferences.copy()
        
        # Blend with secondary moods if present
        if self.current_mood.secondary_moods:
            for secondary_mood, weight in self.current_mood.secondary_moods:
                if weight > 0.3:  # Only significant secondary moods
                    secondary_influence = self.mood_influence_profiles[secondary_mood]
                    self._blend_influences(adjusted_influence, secondary_influence, weight * 0.3)
        
        return adjusted_influence
    
    def get_mood_based_response_modifiers(self) -> Dict[str, Any]:
        """Get mood-based modifiers for response generation"""
        influence = self.get_current_mood_influence()
        
        return {
            "tone_modifiers": influence.tone_modifiers,
            "preferred_words": influence.word_choice_preferences,
            "response_speed": influence.response_tempo,
            "verbosity": influence.verbosity_modifier,
            "emotion_level": influence.emotional_expression_level,
            "curiosity": influence.curiosity_level,
            "supportiveness": influence.supportiveness,
            "playfulness": influence.playfulness,
            "current_mood": self.current_mood.primary_mood.value,
            "mood_intensity": self.current_mood.intensity.value,
            "emotional_valence": self.current_mood.emotional_valence,
            "energy_level": self.current_mood.energy_level
        }
    
    def get_mood_history(self, hours: int = 24) -> List[MoodSnapshot]:
        """Get recent mood history"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        recent_history = [mood for mood in self.mood_history if mood.timestamp > cutoff_time]
        if self.current_mood.timestamp > cutoff_time:
            recent_history.append(self.current_mood)
        
        return recent_history
    
    def get_mood_patterns(self) -> Dict[str, Any]:
        """Get identified mood patterns and trends"""
        return {
            "common_triggers": self.mood_patterns.get("common_triggers", {}),
            "mood_cycles": self.mood_patterns.get("mood_cycles", {}),
            "stability_trends": self.mood_patterns.get("stability_trends", {}),
            "current_mood_duration": self._get_current_mood_duration(),
            "predominant_moods": self._get_predominant_moods()
        }
    
    def predict_mood_evolution(self, minutes: int = 60) -> MoodState:
        """Predict likely mood evolution over time"""
        # Analyze current mood stability and typical patterns
        if self.current_mood.stability > 0.7:
            # Stable mood, likely to continue
            return self.current_mood.primary_mood
        
        # Check for natural decay patterns
        if self.current_mood.intensity.value > 0.6:
            # Intense moods tend to moderate over time
            if self.current_mood.emotional_valence > 0:
                return MoodState.CONTENT
            else:
                return MoodState.NEUTRAL
        
        # Default to gradual return to baseline
        return self.natural_return_mood
    
    def _calculate_mood_transition(self, trigger: MoodTrigger, target_mood: MoodState = None) -> MoodState:
        """Calculate new mood based on trigger and current state"""
        if target_mood:
            return target_mood
        
        # Define trigger-to-mood mappings
        trigger_moods = {
            MoodTrigger.POSITIVE_FEEDBACK: MoodState.JOYFUL,
            MoodTrigger.NEGATIVE_FEEDBACK: MoodState.MELANCHOLY,
            MoodTrigger.LEARNING_SUCCESS: MoodState.EXCITED,
            MoodTrigger.CONFUSION_EVENT: MoodState.FRUSTRATED,
            MoodTrigger.ACHIEVEMENT: MoodState.CONTENT,
            MoodTrigger.CONCERN_FOR_USER: MoodState.EMPATHETIC,
            MoodTrigger.CREATIVE_MOMENT: MoodState.PLAYFUL,
            MoodTrigger.REFLECTION_PERIOD: MoodState.CONTEMPLATIVE,
            MoodTrigger.ENVIRONMENTAL_CHANGE: MoodState.CURIOUS,
            MoodTrigger.GOAL_PROGRESS: MoodState.CONTENT,
            MoodTrigger.MEMORY_RECALL: MoodState.CONTEMPLATIVE
        }
        
        suggested_mood = trigger_moods.get(trigger, self.current_mood.primary_mood)
        
        # Apply mood stability - resist dramatic changes if mood is stable
        if self.current_mood.stability > 0.7:
            # Gradual transition
            return self._blend_moods(self.current_mood.primary_mood, suggested_mood, 0.3)
        else:
            return suggested_mood
    
    def _calculate_intensity_change(self, intensity_change: float) -> MoodIntensity:
        """Calculate new intensity based on change and current state"""
        current_intensity_value = self.current_mood.intensity.value
        new_intensity_value = max(0.1, min(1.0, current_intensity_value + intensity_change))
        
        # Map to intensity enum
        if new_intensity_value <= 0.2:
            return MoodIntensity.SUBTLE
        elif new_intensity_value <= 0.4:
            return MoodIntensity.MILD
        elif new_intensity_value <= 0.6:
            return MoodIntensity.MODERATE
        elif new_intensity_value <= 0.8:
            return MoodIntensity.STRONG
        else:
            return MoodIntensity.INTENSE
    
    def _get_mood_valence(self, mood: MoodState) -> float:
        """Get emotional valence for a mood"""
        valence_map = {
            MoodState.JOYFUL: 0.8,
            MoodState.CONTENT: 0.6,
            MoodState.CALM: 0.4,
            MoodState.NEUTRAL: 0.0,
            MoodState.MELANCHOLY: -0.4,
            MoodState.ANXIOUS: -0.3,
            MoodState.FRUSTRATED: -0.5,
            MoodState.EXCITED: 0.7,
            MoodState.CONTEMPLATIVE: 0.1,
            MoodState.EMPATHETIC: 0.3,
            MoodState.CURIOUS: 0.4,
            MoodState.PLAYFUL: 0.6
        }
        return valence_map.get(mood, 0.0)
    
    def _calculate_mood_stability(self, trigger: MoodTrigger) -> float:
        """Calculate mood stability based on trigger and history"""
        # Some triggers create more stable moods than others
        stability_map = {
            MoodTrigger.REFLECTION_PERIOD: 0.8,
            MoodTrigger.ACHIEVEMENT: 0.7,
            MoodTrigger.LEARNING_SUCCESS: 0.6,
            MoodTrigger.POSITIVE_FEEDBACK: 0.5,
            MoodTrigger.CONFUSION_EVENT: 0.3,
            MoodTrigger.ENVIRONMENTAL_CHANGE: 0.4
        }
        
        base_stability = stability_map.get(trigger, 0.5)
        return base_stability * self.mood_stability_factor
    
    def _calculate_secondary_moods(self, primary_mood: MoodState) -> List[Tuple[MoodState, float]]:
        """Calculate secondary/background moods"""
        secondary_moods = []
        
        # Add context-based secondary moods
        if primary_mood == MoodState.JOYFUL:
            secondary_moods.append((MoodState.EXCITED, 0.4))
        elif primary_mood == MoodState.CONTEMPLATIVE:
            secondary_moods.append((MoodState.CALM, 0.3))
        elif primary_mood == MoodState.FRUSTRATED:
            secondary_moods.append((MoodState.ANXIOUS, 0.2))
        
        return secondary_moods
    
    def _blend_moods(self, mood1: MoodState, mood2: MoodState, blend_factor: float) -> MoodState:
        """Blend two moods based on blend factor"""
        if blend_factor < 0.5:
            return mood1
        else:
            return mood2
    
    def _blend_influences(self, base_influence: MoodInfluenceProfile, 
                         secondary_influence: MoodInfluenceProfile, weight: float):
        """Blend secondary mood influence into base influence"""
        base_influence.response_tempo = (base_influence.response_tempo * (1 - weight) + 
                                       secondary_influence.response_tempo * weight)
        base_influence.emotional_expression_level = (base_influence.emotional_expression_level * (1 - weight) + 
                                                   secondary_influence.emotional_expression_level * weight)
        # Continue for other attributes as needed
    
    def _update_mood_patterns(self, trigger: MoodTrigger, new_mood: MoodState):
        """Update identified mood patterns"""
        # Track common triggers
        if "common_triggers" not in self.mood_patterns:
            self.mood_patterns["common_triggers"] = {}
        
        trigger_key = trigger.value
        if trigger_key not in self.mood_patterns["common_triggers"]:
            self.mood_patterns["common_triggers"][trigger_key] = 0
        self.mood_patterns["common_triggers"][trigger_key] += 1
    
    def _get_current_mood_duration(self) -> float:
        """Get duration of current mood in hours"""
        if not self.mood_history:
            return 0.0
        
        last_different_mood_time = None
        for mood in reversed(self.mood_history):
            if mood.primary_mood != self.current_mood.primary_mood:
                last_different_mood_time = mood.timestamp
                break
        
        if last_different_mood_time:
            duration = datetime.now() - last_different_mood_time
            return duration.total_seconds() / 3600.0
        
        return 0.0
    
    def _get_predominant_moods(self, days: int = 7) -> Dict[str, int]:
        """Get most common moods over recent period"""
        cutoff_time = datetime.now() - timedelta(days=days)
        recent_moods = [mood for mood in self.mood_history if mood.timestamp > cutoff_time]
        
        mood_counts = {}
        for mood in recent_moods:
            mood_name = mood.primary_mood.value
            mood_counts[mood_name] = mood_counts.get(mood_name, 0) + 1
        
        return mood_counts
    
    def _start_mood_evolution(self):
        """Start background mood evolution process"""
        def mood_evolution_loop():
            while True:
                time.sleep(300)  # Check every 5 minutes
                self._natural_mood_evolution()
        
        self.mood_evolution_thread = threading.Thread(target=mood_evolution_loop, daemon=True)
        self.mood_evolution_thread.start()
    
    def _natural_mood_evolution(self):
        """Natural mood evolution over time"""
        with self.lock:
            # Gradually reduce intensity
            current_intensity_value = self.current_mood.intensity.value * self.mood_decay_rate
            new_intensity = self._calculate_intensity_change(current_intensity_value - self.current_mood.intensity.value)
            
            # If mood has been stable for a while, gradually return to neutral
            mood_duration = self._get_current_mood_duration()
            if mood_duration > 2.0 and self.current_mood.primary_mood != self.natural_return_mood:
                if random.random() < 0.1:  # 10% chance per check
                    self.update_mood(
                        trigger=MoodTrigger.ENVIRONMENTAL_CHANGE,
                        trigger_context="natural mood evolution",
                        target_mood=self.natural_return_mood,
                        intensity_change=-0.1
                    )
    
    def _save_mood_state(self):
        """Save current mood state to persistent storage"""
        try:
            mood_file = self.mood_dir / f"{self.user_id}_mood.json"
            
            # Convert to serializable format
            current_mood_dict = asdict(self.current_mood)
            current_mood_dict['timestamp'] = self.current_mood.timestamp.isoformat()
            current_mood_dict['primary_mood'] = self.current_mood.primary_mood.value
            current_mood_dict['intensity'] = self.current_mood.intensity.value
            current_mood_dict['trigger'] = self.current_mood.trigger.value if self.current_mood.trigger else None
            
            # Convert secondary moods
            current_mood_dict['secondary_moods'] = [
                (mood.value, weight) for mood, weight in self.current_mood.secondary_moods
            ]
            
            # Convert history
            history_data = []
            for mood in self.mood_history[-100:]:  # Save last 100 mood snapshots
                mood_dict = asdict(mood)
                mood_dict['timestamp'] = mood.timestamp.isoformat()
                mood_dict['primary_mood'] = mood.primary_mood.value
                mood_dict['intensity'] = mood.intensity.value
                mood_dict['trigger'] = mood.trigger.value if mood.trigger else None
                mood_dict['secondary_moods'] = [
                    (m.value, w) for m, w in mood.secondary_moods
                ]
                history_data.append(mood_dict)
            
            # Save data
            save_data = {
                "current_mood": current_mood_dict,
                "mood_history": history_data,
                "mood_patterns": self.mood_patterns,
                "last_updated": datetime.now().isoformat()
            }
            
            with open(mood_file, 'w') as f:
                json.dump(save_data, f, indent=2)
                
        except Exception as e:
            print(f"[MoodManager] ❌ Error saving mood state: {e}")
    
    def _load_mood_state(self):
        """Load mood state from persistent storage"""
        try:
            mood_file = self.mood_dir / f"{self.user_id}_mood.json"
            
            if mood_file.exists():
                with open(mood_file, 'r') as f:
                    save_data = json.load(f)
                
                # Load current mood
                current_mood_data = save_data.get("current_mood", {})
                if current_mood_data:
                    # Convert back to proper types
                    current_mood_data['primary_mood'] = MoodState(current_mood_data['primary_mood'])
                    current_mood_data['intensity'] = MoodIntensity(current_mood_data['intensity'])
                    current_mood_data['trigger'] = MoodTrigger(current_mood_data['trigger']) if current_mood_data.get('trigger') else None
                    current_mood_data['secondary_moods'] = [
                        (MoodState(mood), weight) for mood, weight in current_mood_data.get('secondary_moods', [])
                    ]
                    
                    self.current_mood = MoodSnapshot(**current_mood_data)
                
                # Load history
                history_data = save_data.get("mood_history", [])
                for mood_dict in history_data:
                    mood_dict['primary_mood'] = MoodState(mood_dict['primary_mood'])
                    mood_dict['intensity'] = MoodIntensity(mood_dict['intensity'])
                    mood_dict['trigger'] = MoodTrigger(mood_dict['trigger']) if mood_dict.get('trigger') else None
                    mood_dict['secondary_moods'] = [
                        (MoodState(mood), weight) for mood, weight in mood_dict.get('secondary_moods', [])
                    ]
                    
                    mood = MoodSnapshot(**mood_dict)
                    self.mood_history.append(mood)
                
                # Load patterns
                self.mood_patterns = save_data.get("mood_patterns", {})
                
                print(f"[MoodManager] 📖 Loaded mood state: {self.current_mood.primary_mood.value}")
                
        except Exception as e:
            print(f"[MoodManager] ⚠️ Error loading mood state: {e}")


# Global mood managers per user
_mood_managers: Dict[str, MoodManager] = {}
_mood_lock = threading.Lock()

def get_mood_manager(user_id: str) -> MoodManager:
    """Get or create mood manager for a user"""
    with _mood_lock:
        if user_id not in _mood_managers:
            _mood_managers[user_id] = MoodManager(user_id)
        return _mood_managers[user_id]

def update_user_mood(user_id: str, trigger: MoodTrigger, **kwargs) -> MoodSnapshot:
    """Update mood for a specific user"""
    mood_manager = get_mood_manager(user_id)
    return mood_manager.update_mood(trigger, **kwargs)

def get_user_mood_influence(user_id: str) -> MoodInfluenceProfile:
    """Get mood influence for a specific user"""
    mood_manager = get_mood_manager(user_id)
    return mood_manager.get_current_mood_influence()

def get_user_mood_modifiers(user_id: str) -> Dict[str, Any]:
    """Get mood-based response modifiers for a specific user"""
    mood_manager = get_mood_manager(user_id)
    return mood_manager.get_mood_based_response_modifiers()