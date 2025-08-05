"""
Personality Profile - Per-User Personality Adaptation System

This module implements comprehensive personality adaptation capabilities:
- Stores per-user personality sliders: humor, empathy, formality, curiosity
- Modifies how Buddy responds based on user's preferred interaction style
- Adapts personality dynamically based on user feedback and interactions
- Maintains persistent personality profiles with learning capabilities
- Integrates with mood and consciousness systems for natural adaptation
"""

import json
import time
import threading
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict, field
from pathlib import Path
from enum import Enum

# Import consciousness modules for integration
try:
    from ai.mood_manager import get_mood_manager, MoodTrigger, MoodState
    MOOD_AVAILABLE = True
except ImportError:
    MOOD_AVAILABLE = False

try:
    from ai.memory_timeline import get_memory_timeline, MemoryType, MemoryImportance
    MEMORY_AVAILABLE = True
except ImportError:
    MEMORY_AVAILABLE = False

class PersonalityDimension(Enum):
    """Core personality dimensions that can be adjusted"""
    HUMOR = "humor"                    # How much humor to include
    EMPATHY = "empathy"               # Level of emotional understanding
    FORMALITY = "formality"           # Formal vs casual communication
    CURIOSITY = "curiosity"           # How inquisitive to be
    ENTHUSIASM = "enthusiasm"         # Energy level in responses
    DIRECTNESS = "directness"         # Straightforward vs nuanced
    SUPPORTIVENESS = "supportiveness" # How supportive and encouraging
    PLAYFULNESS = "playfulness"       # Lighthearted vs serious tone
    INTELLECTUALITY = "intellectuality" # Depth of intellectual content
    PATIENCE = "patience"             # Tolerance for confusion/mistakes

class InteractionStyle(Enum):
    """Overall interaction styles"""
    PROFESSIONAL = "professional"     # Formal, focused, efficient
    FRIENDLY = "friendly"             # Warm, casual, supportive
    MENTOR = "mentor"                 # Guiding, educational, patient
    COMPANION = "companion"           # Personal, caring, empathetic
    ASSISTANT = "assistant"           # Helpful, organized, practical
    CREATIVE = "creative"             # Imaginative, playful, inspiring
    ANALYTICAL = "analytical"         # Logical, precise, thorough
    ADAPTIVE = "adaptive"             # Changes based on context

class PersonalityContext(Enum):
    """Different contexts that might require personality adjustment"""
    WORK = "work"
    CASUAL = "casual"
    LEARNING = "learning"
    EMOTIONAL_SUPPORT = "emotional_support"
    CREATIVE = "creative"
    PROBLEM_SOLVING = "problem_solving"
    ENTERTAINMENT = "entertainment"

@dataclass
class PersonalityTrait:
    """Individual personality trait with value and confidence"""
    dimension: PersonalityDimension
    value: float  # 0.0 to 1.0
    confidence: float  # How confident we are in this value
    last_updated: datetime
    update_count: int = 0
    context_adjustments: Dict[str, float] = field(default_factory=dict)
    
    def __post_init__(self):
        if isinstance(self.last_updated, str):
            self.last_updated = datetime.fromisoformat(self.last_updated)

@dataclass
class PersonalityFeedback:
    """Feedback about personality effectiveness"""
    timestamp: datetime
    dimension: PersonalityDimension
    feedback_type: str  # "positive", "negative", "adjustment_request"
    feedback_strength: float  # 0.0 to 1.0
    context: str
    user_message: str = ""
    
    def __post_init__(self):
        if isinstance(self.timestamp, str):
            self.timestamp = datetime.fromisoformat(self.timestamp)

@dataclass
class PersonalityProfile:
    """Complete personality profile for a user"""
    user_id: str
    traits: Dict[PersonalityDimension, PersonalityTrait]
    preferred_style: InteractionStyle
    context_preferences: Dict[PersonalityContext, Dict[str, float]]
    feedback_history: List[PersonalityFeedback]
    learning_enabled: bool = True
    adaptation_speed: float = 0.1  # How quickly to adapt (0.0 to 1.0)
    created_date: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        if isinstance(self.created_date, str):
            self.created_date = datetime.fromisoformat(self.created_date)
        if isinstance(self.last_updated, str):
            self.last_updated = datetime.fromisoformat(self.last_updated)

class PersonalityProfileManager:
    """
    Per-user personality adaptation system.
    
    Features:
    - Dynamic personality trait adjustment based on user preferences
    - Context-aware personality switching (work vs casual)
    - Continuous learning from user feedback and interactions
    - Integration with mood and consciousness systems
    - Persistent storage of personality profiles
    """
    
    def __init__(self, user_id: str, profile_dir: str = "personality_profiles"):
        self.user_id = user_id
        self.profile_dir = Path(profile_dir)
        self.profile_dir.mkdir(exist_ok=True)
        
        # Current personality profile
        self.profile: Optional[PersonalityProfile] = None
        self.current_context = PersonalityContext.CASUAL
        
        # Learning and adaptation
        self.learning_rate = 0.05
        self.feedback_window = timedelta(days=7)  # Consider feedback from last week
        self.min_feedback_confidence = 0.3
        
        # Default personality values
        self.default_traits = {
            PersonalityDimension.HUMOR: 0.6,
            PersonalityDimension.EMPATHY: 0.8,
            PersonalityDimension.FORMALITY: 0.4,
            PersonalityDimension.CURIOSITY: 0.7,
            PersonalityDimension.ENTHUSIASM: 0.6,
            PersonalityDimension.DIRECTNESS: 0.5,
            PersonalityDimension.SUPPORTIVENESS: 0.8,
            PersonalityDimension.PLAYFULNESS: 0.5,
            PersonalityDimension.INTELLECTUALITY: 0.6,
            PersonalityDimension.PATIENCE: 0.8
        }
        
        # Integration modules
        self.mood_manager = None
        self.memory_timeline = None
        
        # Threading
        self.lock = threading.Lock()
        
        # Load or create profile
        self._load_or_create_profile()
        self._initialize_integrations()
        
        print(f"[PersonalityProfile] 🎭 Initialized for user {user_id}")
    
    def get_current_personality_modifiers(self, context: PersonalityContext = None) -> Dict[str, Any]:
        """Get current personality modifiers for response generation"""
        
        if not self.profile:
            return self._get_default_modifiers()
        
        context = context or self.current_context
        
        with self.lock:
            # Get base trait values
            modifiers = {}
            for dimension, trait in self.profile.traits.items():
                # Apply context adjustments if available
                base_value = trait.value
                context_adjustment = trait.context_adjustments.get(context.value, 0.0)
                adjusted_value = max(0.0, min(1.0, base_value + context_adjustment))
                
                modifiers[dimension.value] = adjusted_value
            
            # Add derived modifiers
            modifiers.update(self._calculate_derived_modifiers(modifiers))
            
            # Add style information
            modifiers['interaction_style'] = self.profile.preferred_style.value
            modifiers['current_context'] = context.value
            
            return modifiers
    
    def update_personality_from_feedback(self, 
                                       feedback_type: str,
                                       dimension: PersonalityDimension = None,
                                       feedback_strength: float = 0.5,
                                       context: str = "",
                                       user_message: str = ""):
        """Update personality based on user feedback"""
        
        if not self.profile or not self.profile.learning_enabled:
            return
        
        feedback = PersonalityFeedback(
            timestamp=datetime.now(),
            dimension=dimension,
            feedback_type=feedback_type,
            feedback_strength=feedback_strength,
            context=context,
            user_message=user_message
        )
        
        with self.lock:
            self.profile.feedback_history.append(feedback)
            
            # Apply feedback to traits
            if dimension and dimension in self.profile.traits:
                self._apply_feedback_to_trait(dimension, feedback)
            else:
                # Infer which traits to adjust based on feedback type
                self._infer_trait_adjustments(feedback)
            
            self.profile.last_updated = datetime.now()
        
        # Store in memory if available
        if MEMORY_AVAILABLE:
            try:
                memory_timeline = get_memory_timeline(self.user_id)
                memory_timeline.store_memory(
                    content=f"Personality feedback: {feedback_type} - {context}",
                    memory_type=MemoryType.SOCIAL,
                    importance=MemoryImportance.MEDIUM,
                    topics=["personality", "feedback", "adaptation"],
                    context_data={"dimension": dimension.value if dimension else "general"}
                )
            except Exception as e:
                print(f"[PersonalityProfile] ⚠️ Memory storage error: {e}")
        
        self._save_profile()
        
        print(f"[PersonalityProfile] 📝 Applied {feedback_type} feedback for {dimension.value if dimension else 'general'}")
    
    def adapt_to_mood(self, user_mood_state: MoodState = None):
        """Adapt personality based on user's current mood"""
        
        if not MOOD_AVAILABLE or not self.profile:
            return
        
        try:
            # Get user's mood if not provided
            if not user_mood_state:
                mood_manager = get_mood_manager(self.user_id)
                mood_modifiers = mood_manager.get_mood_based_response_modifiers()
                current_mood = mood_modifiers.get('current_mood', 'neutral')
                user_mood_state = MoodState(current_mood)
            
            # Adjust personality traits based on mood
            mood_adjustments = self._get_mood_based_adjustments(user_mood_state)
            
            with self.lock:
                for dimension, adjustment in mood_adjustments.items():
                    if dimension in self.profile.traits:
                        trait = self.profile.traits[dimension]
                        # Apply temporary adjustment (doesn't save to profile)
                        context_key = f"mood_{user_mood_state.value}"
                        trait.context_adjustments[context_key] = adjustment
            
            print(f"[PersonalityProfile] 🎭 Adapted personality for mood: {user_mood_state.value}")
            
        except Exception as e:
            print(f"[PersonalityProfile] ⚠️ Mood adaptation error: {e}")
    
    def set_context(self, context: PersonalityContext):
        """Set current interaction context"""
        self.current_context = context
        print(f"[PersonalityProfile] 🎯 Context set to: {context.value}")
    
    def get_personality_description(self) -> str:
        """Get human-readable description of current personality"""
        
        if not self.profile:
            return "Default balanced personality"
        
        modifiers = self.get_current_personality_modifiers()
        
        # Identify dominant traits
        high_traits = [dim for dim, value in modifiers.items() 
                      if isinstance(value, (int, float)) and value > 0.7]
        low_traits = [dim for dim, value in modifiers.items() 
                     if isinstance(value, (int, float)) and value < 0.3]
        
        description_parts = []
        
        if 'humor' in high_traits:
            description_parts.append("humorous")
        if 'empathy' in high_traits:
            description_parts.append("empathetic")
        if 'enthusiasm' in high_traits:
            description_parts.append("enthusiastic")
        if 'formality' in high_traits:
            description_parts.append("formal")
        elif 'formality' in low_traits:
            description_parts.append("casual")
        if 'supportiveness' in high_traits:
            description_parts.append("supportive")
        if 'playfulness' in high_traits:
            description_parts.append("playful")
        
        if description_parts:
            return f"{modifiers['interaction_style']}, " + ", ".join(description_parts[:3])
        else:
            return f"{modifiers['interaction_style']} style"
    
    def get_response_style_guide(self) -> Dict[str, str]:
        """Get style guide for response generation"""
        
        modifiers = self.get_current_personality_modifiers()
        
        guide = {
            'tone': self._determine_tone(modifiers),
            'formality_level': self._determine_formality(modifiers),
            'humor_approach': self._determine_humor_approach(modifiers),
            'empathy_expression': self._determine_empathy_expression(modifiers),
            'question_style': self._determine_question_style(modifiers),
            'support_style': self._determine_support_style(modifiers)
        }
        
        return guide
    
    def suggest_personality_adjustments(self) -> List[str]:
        """Suggest personality adjustments based on recent interactions"""
        
        if not self.profile:
            return []
        
        suggestions = []
        recent_feedback = self._get_recent_feedback()
        
        # Analyze feedback patterns
        negative_patterns = {}
        for feedback in recent_feedback:
            if feedback.feedback_type == "negative" and feedback.dimension:
                dim = feedback.dimension.value
                negative_patterns[dim] = negative_patterns.get(dim, 0) + 1
        
        # Suggest adjustments
        for dimension, count in negative_patterns.items():
            if count >= 2:  # Multiple negative feedback
                suggestions.append(f"Consider adjusting {dimension} based on recent feedback")
        
        # Check for lack of positive feedback
        positive_feedback_count = len([f for f in recent_feedback if f.feedback_type == "positive"])
        if positive_feedback_count == 0 and len(recent_feedback) > 3:
            suggestions.append("Consider experimenting with different personality approaches")
        
        return suggestions
    
    def reset_to_defaults(self):
        """Reset personality to default values"""
        
        if self.profile:
            with self.lock:
                for dimension, default_value in self.default_traits.items():
                    if dimension in self.profile.traits:
                        trait = self.profile.traits[dimension]
                        trait.value = default_value
                        trait.confidence = 0.5
                        trait.context_adjustments.clear()
                        trait.last_updated = datetime.now()
                
                self.profile.preferred_style = InteractionStyle.ADAPTIVE
                self.profile.last_updated = datetime.now()
            
            self._save_profile()
            print("[PersonalityProfile] 🔄 Reset to default personality")
    
    def _load_or_create_profile(self):
        """Load existing profile or create new one"""
        profile_file = self.profile_dir / f"{self.user_id}_personality.json"
        
        if profile_file.exists():
            try:
                with open(profile_file, 'r') as f:
                    profile_data = json.load(f)
                
                # Convert traits
                traits = {}
                for dim_name, trait_data in profile_data.get('traits', {}).items():
                    dimension = PersonalityDimension(dim_name)
                    trait_data['dimension'] = dimension
                    traits[dimension] = PersonalityTrait(**trait_data)
                
                # Convert feedback history
                feedback_history = []
                for feedback_data in profile_data.get('feedback_history', []):
                    feedback_data['dimension'] = PersonalityDimension(feedback_data['dimension']) if feedback_data.get('dimension') else None
                    feedback_history.append(PersonalityFeedback(**feedback_data))
                
                # Convert context preferences
                context_preferences = {}
                for context_name, prefs in profile_data.get('context_preferences', {}).items():
                    context_preferences[PersonalityContext(context_name)] = prefs
                
                self.profile = PersonalityProfile(
                    user_id=self.user_id,
                    traits=traits,
                    preferred_style=InteractionStyle(profile_data.get('preferred_style', 'adaptive')),
                    context_preferences=context_preferences,
                    feedback_history=feedback_history,
                    learning_enabled=profile_data.get('learning_enabled', True),
                    adaptation_speed=profile_data.get('adaptation_speed', 0.1),
                    created_date=datetime.fromisoformat(profile_data.get('created_date', datetime.now().isoformat())),
                    last_updated=datetime.fromisoformat(profile_data.get('last_updated', datetime.now().isoformat()))
                )
                
                print(f"[PersonalityProfile] 📖 Loaded profile for {self.user_id}")
                
            except Exception as e:
                print(f"[PersonalityProfile] ⚠️ Error loading profile: {e}")
                self._create_default_profile()
        else:
            self._create_default_profile()
    
    def _create_default_profile(self):
        """Create default personality profile"""
        
        # Create default traits
        traits = {}
        for dimension, default_value in self.default_traits.items():
            traits[dimension] = PersonalityTrait(
                dimension=dimension,
                value=default_value,
                confidence=0.5,
                last_updated=datetime.now()
            )
        
        self.profile = PersonalityProfile(
            user_id=self.user_id,
            traits=traits,
            preferred_style=InteractionStyle.ADAPTIVE,
            context_preferences={},
            feedback_history=[]
        )
        
        self._save_profile()
        print(f"[PersonalityProfile] ✨ Created default profile for {self.user_id}")
    
    def _apply_feedback_to_trait(self, dimension: PersonalityDimension, feedback: PersonalityFeedback):
        """Apply feedback to specific trait"""
        
        trait = self.profile.traits[dimension]
        
        # Calculate adjustment based on feedback
        adjustment_strength = feedback.feedback_strength * self.profile.adaptation_speed
        
        if feedback.feedback_type == "positive":
            # Positive feedback - slight reinforcement (no change needed)
            trait.confidence = min(1.0, trait.confidence + 0.1)
        elif feedback.feedback_type == "negative":
            # Negative feedback - adjust trait value
            if trait.value > 0.5:
                trait.value = max(0.1, trait.value - adjustment_strength)
            else:
                trait.value = min(0.9, trait.value + adjustment_strength)
        elif feedback.feedback_type == "adjustment_request":
            # Direct adjustment request
            target_direction = 1 if "more" in feedback.user_message.lower() else -1
            trait.value = max(0.1, min(0.9, trait.value + (adjustment_strength * target_direction)))
        
        trait.update_count += 1
        trait.last_updated = datetime.now()
    
    def _infer_trait_adjustments(self, feedback: PersonalityFeedback):
        """Infer which traits to adjust based on general feedback"""
        
        feedback_lower = feedback.user_message.lower()
        context_lower = feedback.context.lower()
        
        # Keyword-based inference
        trait_keywords = {
            PersonalityDimension.HUMOR: ["funny", "humor", "joke", "serious", "formal"],
            PersonalityDimension.EMPATHY: ["understanding", "empathy", "caring", "cold"],
            PersonalityDimension.FORMALITY: ["formal", "casual", "professional", "relaxed"],
            PersonalityDimension.ENTHUSIASM: ["energy", "excited", "calm", "enthusiasm"],
            PersonalityDimension.DIRECTNESS: ["direct", "straightforward", "subtle", "blunt"],
            PersonalityDimension.SUPPORTIVENESS: ["supportive", "encouraging", "helpful", "harsh"]
        }
        
        for dimension, keywords in trait_keywords.items():
            if any(keyword in feedback_lower or keyword in context_lower for keyword in keywords):
                if dimension in self.profile.traits:
                    self._apply_feedback_to_trait(dimension, feedback)
    
    def _get_mood_based_adjustments(self, mood_state: MoodState) -> Dict[PersonalityDimension, float]:
        """Get personality adjustments based on user mood"""
        
        mood_adjustments = {
            MoodState.JOYFUL: {
                PersonalityDimension.HUMOR: 0.2,
                PersonalityDimension.ENTHUSIASM: 0.3,
                PersonalityDimension.PLAYFULNESS: 0.2
            },
            MoodState.MELANCHOLY: {
                PersonalityDimension.EMPATHY: 0.3,
                PersonalityDimension.SUPPORTIVENESS: 0.3,
                PersonalityDimension.HUMOR: -0.2,
                PersonalityDimension.PLAYFULNESS: -0.2
            },
            MoodState.ANXIOUS: {
                PersonalityDimension.PATIENCE: 0.3,
                PersonalityDimension.SUPPORTIVENESS: 0.3,
                PersonalityDimension.DIRECTNESS: -0.2
            },
            MoodState.FRUSTRATED: {
                PersonalityDimension.PATIENCE: 0.4,
                PersonalityDimension.EMPATHY: 0.2,
                PersonalityDimension.DIRECTNESS: 0.1
            },
            MoodState.EXCITED: {
                PersonalityDimension.ENTHUSIASM: 0.2,
                PersonalityDimension.PLAYFULNESS: 0.2
            }
        }
        
        return mood_adjustments.get(mood_state, {})
    
    def _calculate_derived_modifiers(self, base_modifiers: Dict[str, float]) -> Dict[str, Any]:
        """Calculate derived personality modifiers"""
        
        derived = {}
        
        # Response length preference
        verbosity = (base_modifiers.get('intellectuality', 0.5) + 
                    base_modifiers.get('enthusiasm', 0.5)) / 2
        derived['preferred_response_length'] = 'detailed' if verbosity > 0.6 else 'concise'
        
        # Question asking tendency
        question_tendency = (base_modifiers.get('curiosity', 0.5) + 
                           base_modifiers.get('empathy', 0.5)) / 2
        derived['question_frequency'] = 'high' if question_tendency > 0.7 else 'moderate'
        
        # Emotional expression level
        emotional_expression = (base_modifiers.get('empathy', 0.5) + 
                              base_modifiers.get('enthusiasm', 0.5)) / 2
        derived['emotional_expression'] = 'high' if emotional_expression > 0.6 else 'moderate'
        
        return derived
    
    def _determine_tone(self, modifiers: Dict[str, float]) -> str:
        """Determine overall tone based on personality"""
        
        formality = modifiers.get('formality', 0.5)
        enthusiasm = modifiers.get('enthusiasm', 0.5)
        empathy = modifiers.get('empathy', 0.5)
        
        if formality > 0.7:
            return 'professional'
        elif enthusiasm > 0.7 and empathy > 0.6:
            return 'warm_enthusiastic'
        elif empathy > 0.7:
            return 'caring_supportive'
        elif enthusiasm > 0.6:
            return 'energetic_friendly'
        else:
            return 'balanced_neutral'
    
    def _determine_formality(self, modifiers: Dict[str, float]) -> str:
        """Determine formality level"""
        
        formality = modifiers.get('formality', 0.5)
        
        if formality > 0.7:
            return 'formal'
        elif formality < 0.3:
            return 'very_casual'
        elif formality < 0.5:
            return 'casual'
        else:
            return 'semi_formal'
    
    def _determine_humor_approach(self, modifiers: Dict[str, float]) -> str:
        """Determine humor approach"""
        
        humor = modifiers.get('humor', 0.5)
        playfulness = modifiers.get('playfulness', 0.5)
        
        if humor > 0.7 and playfulness > 0.6:
            return 'frequent_playful'
        elif humor > 0.6:
            return 'occasional_light'
        elif humor > 0.4:
            return 'subtle_witty'
        else:
            return 'minimal_serious'
    
    def _determine_empathy_expression(self, modifiers: Dict[str, float]) -> str:
        """Determine empathy expression style"""
        
        empathy = modifiers.get('empathy', 0.5)
        supportiveness = modifiers.get('supportiveness', 0.5)
        
        if empathy > 0.8 and supportiveness > 0.7:
            return 'highly_empathetic'
        elif empathy > 0.6:
            return 'understanding_supportive'
        elif empathy > 0.4:
            return 'considerate_aware'
        else:
            return 'factual_neutral'
    
    def _determine_question_style(self, modifiers: Dict[str, float]) -> str:
        """Determine questioning style"""
        
        curiosity = modifiers.get('curiosity', 0.5)
        directness = modifiers.get('directness', 0.5)
        
        if curiosity > 0.7:
            return 'probing_inquisitive'
        elif curiosity > 0.5 and directness > 0.6:
            return 'direct_clarifying'
        elif curiosity > 0.5:
            return 'gentle_curious'
        else:
            return 'minimal_focused'
    
    def _determine_support_style(self, modifiers: Dict[str, float]) -> str:
        """Determine support style"""
        
        supportiveness = modifiers.get('supportiveness', 0.5)
        directness = modifiers.get('directness', 0.5)
        patience = modifiers.get('patience', 0.5)
        
        if supportiveness > 0.8 and patience > 0.7:
            return 'nurturing_patient'
        elif supportiveness > 0.6 and directness > 0.6:
            return 'practical_helpful'
        elif supportiveness > 0.6:
            return 'encouraging_positive'
        else:
            return 'neutral_informative'
    
    def _get_recent_feedback(self) -> List[PersonalityFeedback]:
        """Get recent feedback within the feedback window"""
        
        if not self.profile:
            return []
        
        cutoff_time = datetime.now() - self.feedback_window
        return [f for f in self.profile.feedback_history if f.timestamp > cutoff_time]
    
    def _get_default_modifiers(self) -> Dict[str, Any]:
        """Get default personality modifiers"""
        
        return {
            'humor': 0.5,
            'empathy': 0.7,
            'formality': 0.4,
            'curiosity': 0.6,
            'enthusiasm': 0.5,
            'directness': 0.5,
            'supportiveness': 0.7,
            'playfulness': 0.4,
            'intellectuality': 0.5,
            'patience': 0.7,
            'interaction_style': 'adaptive',
            'current_context': 'casual'
        }
    
    def _initialize_integrations(self):
        """Initialize integrations with consciousness modules"""
        try:
            if MOOD_AVAILABLE:
                self.mood_manager = get_mood_manager(self.user_id)
            
            if MEMORY_AVAILABLE:
                self.memory_timeline = get_memory_timeline(self.user_id)
                
        except Exception as e:
            print(f"[PersonalityProfile] ⚠️ Error initializing integrations: {e}")
    
    def _save_profile(self):
        """Save personality profile to persistent storage"""
        
        if not self.profile:
            return
        
        try:
            profile_file = self.profile_dir / f"{self.user_id}_personality.json"
            
            # Convert to serializable format
            profile_data = {
                'user_id': self.profile.user_id,
                'preferred_style': self.profile.preferred_style.value,
                'learning_enabled': self.profile.learning_enabled,
                'adaptation_speed': self.profile.adaptation_speed,
                'created_date': self.profile.created_date.isoformat(),
                'last_updated': self.profile.last_updated.isoformat(),
                'traits': {},
                'context_preferences': {},
                'feedback_history': []
            }
            
            # Convert traits
            for dimension, trait in self.profile.traits.items():
                trait_data = asdict(trait)
                trait_data['dimension'] = dimension.value
                trait_data['last_updated'] = trait.last_updated.isoformat()
                profile_data['traits'][dimension.value] = trait_data
            
            # Convert context preferences
            for context, prefs in self.profile.context_preferences.items():
                profile_data['context_preferences'][context.value] = prefs
            
            # Convert feedback history
            for feedback in self.profile.feedback_history:
                feedback_data = asdict(feedback)
                feedback_data['timestamp'] = feedback.timestamp.isoformat()
                feedback_data['dimension'] = feedback.dimension.value if feedback.dimension else None
                profile_data['feedback_history'].append(feedback_data)
            
            with open(profile_file, 'w') as f:
                json.dump(profile_data, f, indent=2)
                
        except Exception as e:
            print(f"[PersonalityProfile] ❌ Error saving profile: {e}")


# Global personality profile managers per user
_personality_profiles: Dict[str, PersonalityProfileManager] = {}
_profile_lock = threading.Lock()

def get_personality_profile_manager(user_id: str) -> PersonalityProfileManager:
    """Get or create personality profile manager for a user"""
    with _profile_lock:
        if user_id not in _personality_profiles:
            _personality_profiles[user_id] = PersonalityProfileManager(user_id)
        return _personality_profiles[user_id]

def get_personality_modifiers(user_id: str, context: PersonalityContext = None) -> Dict[str, Any]:
    """Get personality modifiers for a specific user"""
    profile_manager = get_personality_profile_manager(user_id)
    return profile_manager.get_current_personality_modifiers(context)

def update_personality_feedback(user_id: str, feedback_type: str, **kwargs):
    """Update personality based on user feedback"""
    profile_manager = get_personality_profile_manager(user_id)
    profile_manager.update_personality_from_feedback(feedback_type, **kwargs)

def get_personality_description(user_id: str) -> str:
    """Get personality description for a user"""
    profile_manager = get_personality_profile_manager(user_id)
    return profile_manager.get_personality_description()

def get_response_style_guide(user_id: str) -> Dict[str, str]:
    """Get response style guide for a user"""
    profile_manager = get_personality_profile_manager(user_id)
    return profile_manager.get_response_style_guide()

def set_personality_context(user_id: str, context: PersonalityContext):
    """Set personality context for a user"""
    profile_manager = get_personality_profile_manager(user_id)
    profile_manager.set_context(context)

def adapt_personality_to_mood(user_id: str, mood_state: MoodState = None):
    """Adapt personality based on user mood"""
    profile_manager = get_personality_profile_manager(user_id)
    profile_manager.adapt_to_mood(mood_state)