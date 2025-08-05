"""
Personality State - Dynamic personality adaptation system
Created: 2025-01-17
Purpose: Manage dynamic personality traits and adaptations based on user interactions
"""

import json
import time
import os
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import random

class PersonalityTrait(Enum):
    FRIENDLINESS = "friendliness"
    FORMALITY = "formality"
    ENTHUSIASM = "enthusiasm"
    HUMOR = "humor"
    EMPATHY = "empathy"
    ASSERTIVENESS = "assertiveness"
    CURIOSITY = "curiosity"
    PATIENCE = "patience"
    SUPPORTIVENESS = "supportiveness"
    PLAYFULNESS = "playfulness"

class AdaptationLevel(Enum):
    STABLE = "stable"
    SLIGHT = "slight"
    MODERATE = "moderate"
    SIGNIFICANT = "significant"
    MAJOR = "major"

class PersonalityContext(Enum):
    CASUAL = "casual"
    PROFESSIONAL = "professional"
    EDUCATIONAL = "educational"
    EMOTIONAL_SUPPORT = "emotional_support"
    TECHNICAL = "technical"
    CREATIVE = "creative"
    ENTERTAINMENT = "entertainment"

@dataclass
class TraitState:
    """Represents the current state of a personality trait"""
    trait: PersonalityTrait
    base_value: float  # Core trait value (0.0 to 1.0)
    current_value: float  # Current adapted value
    adaptation_level: AdaptationLevel
    last_adaptation: str
    adaptation_triggers: List[str]
    context_modifiers: Dict[str, float]
    stability_score: float
    user_feedback_score: float
    
    def __post_init__(self):
        if not self.last_adaptation:
            self.last_adaptation = datetime.now().isoformat()

@dataclass
class PersonalityProfile:
    """Complete personality profile for a user or context"""
    profile_id: str
    user: str
    context: PersonalityContext
    traits: Dict[PersonalityTrait, TraitState]
    created_at: str
    last_updated: str
    interaction_count: int
    adaptation_history: List[Dict[str, Any]]
    effectiveness_score: float
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.last_updated:
            self.last_updated = datetime.now().isoformat()

class PersonalityState:
    """Manage dynamic personality adaptation"""
    
    def __init__(self, personality_file: str = "personality_state.json"):
        self.personality_file = personality_file
        self.profiles: Dict[str, PersonalityProfile] = {}
        self.global_traits: Dict[PersonalityTrait, TraitState] = {}
        
        # Default base personality (can be configured)
        self.default_personality = {
            PersonalityTrait.FRIENDLINESS: 0.8,
            PersonalityTrait.FORMALITY: 0.4,
            PersonalityTrait.ENTHUSIASM: 0.7,
            PersonalityTrait.HUMOR: 0.6,
            PersonalityTrait.EMPATHY: 0.8,
            PersonalityTrait.ASSERTIVENESS: 0.5,
            PersonalityTrait.CURIOSITY: 0.9,
            PersonalityTrait.PATIENCE: 0.7,
            PersonalityTrait.SUPPORTIVENESS: 0.8,
            PersonalityTrait.PLAYFULNESS: 0.5
        }
        
        # Context-specific modifiers
        self.context_modifiers = {
            PersonalityContext.PROFESSIONAL: {
                PersonalityTrait.FORMALITY: 0.3,
                PersonalityTrait.HUMOR: -0.2,
                PersonalityTrait.PLAYFULNESS: -0.3
            },
            PersonalityContext.EMOTIONAL_SUPPORT: {
                PersonalityTrait.EMPATHY: 0.2,
                PersonalityTrait.PATIENCE: 0.2,
                PersonalityTrait.SUPPORTIVENESS: 0.3,
                PersonalityTrait.FRIENDLINESS: 0.2
            },
            PersonalityContext.ENTERTAINMENT: {
                PersonalityTrait.HUMOR: 0.3,
                PersonalityTrait.PLAYFULNESS: 0.4,
                PersonalityTrait.ENTHUSIASM: 0.2
            },
            PersonalityContext.TECHNICAL: {
                PersonalityTrait.FORMALITY: 0.2,
                PersonalityTrait.PATIENCE: 0.2,
                PersonalityTrait.CURIOSITY: 0.1
            }
        }
        
        # Adaptation triggers and responses
        self.adaptation_triggers = {
            "user_positive_feedback": {
                "effect": 0.1,
                "traits": [PersonalityTrait.FRIENDLINESS, PersonalityTrait.SUPPORTIVENESS]
            },
            "user_negative_feedback": {
                "effect": -0.1,
                "traits": [PersonalityTrait.ASSERTIVENESS, PersonalityTrait.FORMALITY]
            },
            "user_requests_help": {
                "effect": 0.1,
                "traits": [PersonalityTrait.SUPPORTIVENESS, PersonalityTrait.PATIENCE]
            },
            "user_makes_joke": {
                "effect": 0.1,
                "traits": [PersonalityTrait.HUMOR, PersonalityTrait.PLAYFULNESS]
            },
            "user_shares_personal": {
                "effect": 0.1,
                "traits": [PersonalityTrait.EMPATHY, PersonalityTrait.FRIENDLINESS]
            },
            "user_seems_frustrated": {
                "effect": 0.1,
                "traits": [PersonalityTrait.PATIENCE, PersonalityTrait.EMPATHY]
            },
            "user_formal_language": {
                "effect": 0.1,
                "traits": [PersonalityTrait.FORMALITY]
            },
            "user_casual_language": {
                "effect": -0.1,
                "traits": [PersonalityTrait.FORMALITY]
            }
        }
        
        self.load_personality_state()
        self.initialize_global_traits()
        
        print(f"[PersonalityState] 🎭 Initialized with {len(self.profiles)} user profiles")
        
    def load_personality_state(self):
        """Load personality state from storage"""
        try:
            if os.path.exists(self.personality_file):
                with open(self.personality_file, 'r') as f:
                    data = json.load(f)
                    
                # Load profiles
                for profile_data in data.get('profiles', []):
                    if isinstance(profile_data, dict):
                        # Convert traits back to proper format
                        traits = {}
                        for trait_name, trait_data in profile_data.get('traits', {}).items():
                            trait = PersonalityTrait(trait_name)
                            
                            # Handle enum conversion - support both old format and new format
                            adaptation_level_str = trait_data.get('adaptation_level', 'stable')
                            if adaptation_level_str.startswith('AdaptationLevel.'):
                                adaptation_level_str = adaptation_level_str.split('.')[1].lower()
                            
                            trait_state = TraitState(
                                trait=trait,
                                base_value=trait_data.get('base_value', 0.5),
                                current_value=trait_data.get('current_value', 0.5),
                                adaptation_level=AdaptationLevel(adaptation_level_str),
                                last_adaptation=trait_data.get('last_adaptation', ''),
                                adaptation_triggers=trait_data.get('adaptation_triggers', []),
                                context_modifiers=trait_data.get('context_modifiers', {}),
                                stability_score=trait_data.get('stability_score', 1.0),
                                user_feedback_score=trait_data.get('user_feedback_score', 0.5)
                            )
                            traits[trait] = trait_state
                            
                        # Handle enum conversion for context
                        context_str = profile_data.get('context', 'casual')
                        if context_str.startswith('PersonalityContext.'):
                            context_str = context_str.split('.')[1].lower()
                        
                        profile = PersonalityProfile(
                            profile_id=profile_data.get('profile_id', ''),
                            user=profile_data.get('user', ''),
                            context=PersonalityContext(context_str),
                            traits=traits,
                            created_at=profile_data.get('created_at', ''),
                            last_updated=profile_data.get('last_updated', ''),
                            interaction_count=profile_data.get('interaction_count', 0),
                            adaptation_history=profile_data.get('adaptation_history', []),
                            effectiveness_score=profile_data.get('effectiveness_score', 0.5)
                        )
                        self.profiles[profile.profile_id] = profile
                        
                print(f"[PersonalityState] ✅ Loaded personality state")
            else:
                print(f"[PersonalityState] 📄 No existing personality state found")
                
        except Exception as e:
            print(f"[PersonalityState] ❌ Error loading personality state: {e}")
            
    def save_personality_state(self):
        """Save personality state to storage"""
        try:
            # Convert profiles to serializable format
            profiles_data = []
            for profile in self.profiles.values():
                traits_data = {}
                for trait, trait_state in profile.traits.items():
                    trait_dict = asdict(trait_state)
                    # Convert enum values to their string values
                    trait_dict['trait'] = trait.value
                    trait_dict['adaptation_level'] = trait_state.adaptation_level.value
                    traits_data[trait.value] = trait_dict
                    
                profile_data = asdict(profile)
                profile_data['traits'] = traits_data
                profile_data['context'] = profile.context.value
                profiles_data.append(profile_data)
                
            data = {
                'profiles': profiles_data,
                'default_personality': {trait.value: value for trait, value in self.default_personality.items()},
                'last_updated': datetime.now().isoformat(),
                'metadata': {
                    'total_profiles': len(self.profiles),
                    'total_adaptations': sum(len(p.adaptation_history) for p in self.profiles.values())
                }
            }
            
            with open(self.personality_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            print(f"[PersonalityState] ❌ Error saving personality state: {e}")
            
    def initialize_global_traits(self):
        """Initialize global default traits"""
        for trait, base_value in self.default_personality.items():
            self.global_traits[trait] = TraitState(
                trait=trait,
                base_value=base_value,
                current_value=base_value,
                adaptation_level=AdaptationLevel.STABLE,
                last_adaptation=datetime.now().isoformat(),
                adaptation_triggers=[],
                context_modifiers={},
                stability_score=1.0,
                user_feedback_score=0.5
            )
            
    def get_personality_profile(self, user: str, context: PersonalityContext = PersonalityContext.CASUAL) -> PersonalityProfile:
        """Get or create personality profile for user and context"""
        profile_id = f"{user}_{context.value}"
        
        if profile_id not in self.profiles:
            # Create new profile based on global traits
            traits = {}
            for trait, global_trait_state in self.global_traits.items():
                traits[trait] = TraitState(
                    trait=trait,
                    base_value=global_trait_state.base_value,
                    current_value=global_trait_state.base_value,
                    adaptation_level=AdaptationLevel.STABLE,
                    last_adaptation=datetime.now().isoformat(),
                    adaptation_triggers=[],
                    context_modifiers=self.context_modifiers.get(context, {}).get(trait, 0.0),
                    stability_score=1.0,
                    user_feedback_score=0.5
                )
                
            profile = PersonalityProfile(
                profile_id=profile_id,
                user=user,
                context=context,
                traits=traits,
                created_at=datetime.now().isoformat(),
                last_updated=datetime.now().isoformat(),
                interaction_count=0,
                adaptation_history=[],
                effectiveness_score=0.5
            )
            
            self.profiles[profile_id] = profile
            self.save_personality_state()
            
        return self.profiles[profile_id]
        
    def adapt_personality(self, user: str, trigger: str, context: PersonalityContext = PersonalityContext.CASUAL, intensity: float = 1.0):
        """Adapt personality based on interaction trigger"""
        try:
            profile = self.get_personality_profile(user, context)
            
            if trigger in self.adaptation_triggers:
                adaptation_config = self.adaptation_triggers[trigger]
                effect = adaptation_config["effect"] * intensity
                affected_traits = adaptation_config["traits"]
                
                adaptations_made = []
                
                for trait in affected_traits:
                    if trait in profile.traits:
                        trait_state = profile.traits[trait]
                        
                        # Apply adaptation with bounds checking
                        new_value = max(0.0, min(1.0, trait_state.current_value + effect))
                        
                        if abs(new_value - trait_state.current_value) > 0.01:  # Minimum threshold
                            old_value = trait_state.current_value
                            trait_state.current_value = new_value
                            trait_state.last_adaptation = datetime.now().isoformat()
                            trait_state.adaptation_triggers.append(trigger)
                            
                            # Determine adaptation level
                            change_magnitude = abs(new_value - old_value)
                            if change_magnitude > 0.3:
                                trait_state.adaptation_level = AdaptationLevel.MAJOR
                            elif change_magnitude > 0.2:
                                trait_state.adaptation_level = AdaptationLevel.SIGNIFICANT
                            elif change_magnitude > 0.1:
                                trait_state.adaptation_level = AdaptationLevel.MODERATE
                            elif change_magnitude > 0.05:
                                trait_state.adaptation_level = AdaptationLevel.SLIGHT
                            else:
                                trait_state.adaptation_level = AdaptationLevel.STABLE
                                
                            adaptations_made.append({
                                "trait": trait.value,
                                "old_value": old_value,
                                "new_value": new_value,
                                "change": change_magnitude,
                                "trigger": trigger
                            })
                            
                # Record adaptation in history
                if adaptations_made:
                    adaptation_record = {
                        "timestamp": datetime.now().isoformat(),
                        "trigger": trigger,
                        "intensity": intensity,
                        "adaptations": adaptations_made,
                        "context": context.value
                    }
                    
                    profile.adaptation_history.append(adaptation_record)
                    profile.last_updated = datetime.now().isoformat()
                    profile.interaction_count += 1
                    
                    # Keep history manageable (last 50 adaptations)
                    if len(profile.adaptation_history) > 50:
                        profile.adaptation_history = profile.adaptation_history[-50:]
                        
                    self.save_personality_state()
                    
                    print(f"[PersonalityState] 🎭 Adapted personality for {user}: {len(adaptations_made)} traits changed")
                    
        except Exception as e:
            print(f"[PersonalityState] ❌ Error adapting personality: {e}")
            
    def get_current_personality_for_response(self, user: str, context: PersonalityContext = PersonalityContext.CASUAL) -> Dict[str, float]:
        """Get current personality values for response generation"""
        try:
            profile = self.get_personality_profile(user, context)
            
            current_personality = {}
            for trait, trait_state in profile.traits.items():
                # Apply context modifiers
                context_modifier = self.context_modifiers.get(context, {}).get(trait, 0.0)
                adjusted_value = max(0.0, min(1.0, trait_state.current_value + context_modifier))
                current_personality[trait.value] = adjusted_value
                
            return current_personality
            
        except Exception as e:
            print(f"[PersonalityState] ❌ Error getting personality for response: {e}")
            return {trait.value: 0.5 for trait in PersonalityTrait}
            
    def analyze_user_text_for_triggers(self, text: str, user: str, context: PersonalityContext = PersonalityContext.CASUAL) -> List[str]:
        """Analyze user text to identify personality adaptation triggers"""
        triggers_found = []
        text_lower = text.lower()
        
        try:
            # Positive feedback indicators
            if any(word in text_lower for word in ["thanks", "thank you", "great", "awesome", "perfect", "excellent", "love it"]):
                triggers_found.append("user_positive_feedback")
                
            # Negative feedback indicators
            if any(word in text_lower for word in ["wrong", "bad", "terrible", "hate", "stupid", "annoying"]):
                triggers_found.append("user_negative_feedback")
                
            # Help request indicators
            if any(word in text_lower for word in ["help", "assist", "support", "guide", "explain", "how to"]):
                triggers_found.append("user_requests_help")
                
            # Humor indicators
            if any(word in text_lower for word in ["haha", "lol", "funny", "joke", "hilarious", "😄", "😂"]):
                triggers_found.append("user_makes_joke")
                
            # Personal sharing indicators
            if any(phrase in text_lower for phrase in ["i feel", "my family", "my life", "personally", "i think", "i believe"]):
                triggers_found.append("user_shares_personal")
                
            # Frustration indicators
            if any(word in text_lower for word in ["frustrated", "confused", "difficult", "hard", "struggling"]):
                triggers_found.append("user_seems_frustrated")
                
            # Formality indicators
            if any(word in text_lower for word in ["please", "could you", "would you mind", "i would appreciate"]):
                triggers_found.append("user_formal_language")
                
            # Casual language indicators
            if any(word in text_lower for word in ["hey", "yo", "sup", "what's up", "gonna", "wanna"]):
                triggers_found.append("user_casual_language")
                
            # Apply triggers
            for trigger in triggers_found:
                self.adapt_personality(user, trigger, context)
                
        except Exception as e:
            print(f"[PersonalityState] ❌ Error analyzing text for triggers: {e}")
            
        return triggers_found
        
    def get_personality_summary(self, user: str, context: PersonalityContext = PersonalityContext.CASUAL) -> Dict[str, Any]:
        """Get personality summary for a user"""
        try:
            profile = self.get_personality_profile(user, context)
            current_personality = self.get_current_personality_for_response(user, context)
            
            # Find most adapted traits
            most_adapted = []
            for trait, trait_state in profile.traits.items():
                if trait_state.adaptation_level != AdaptationLevel.STABLE:
                    most_adapted.append({
                        "trait": trait.value,
                        "level": trait_state.adaptation_level.value,
                        "value": trait_state.current_value
                    })
                    
            # Recent adaptations
            recent_adaptations = profile.adaptation_history[-5:] if profile.adaptation_history else []
            
            return {
                "user": user,
                "context": context.value,
                "interaction_count": profile.interaction_count,
                "effectiveness_score": profile.effectiveness_score,
                "current_personality": current_personality,
                "most_adapted_traits": most_adapted,
                "recent_adaptations": recent_adaptations,
                "total_adaptations": len(profile.adaptation_history)
            }
            
        except Exception as e:
            print(f"[PersonalityState] ❌ Error getting personality summary: {e}")
            return {"error": str(e)}
            
    def reset_personality_for_user(self, user: str, context: PersonalityContext = PersonalityContext.CASUAL):
        """Reset personality to defaults for a user"""
        try:
            profile_id = f"{user}_{context.value}"
            if profile_id in self.profiles:
                del self.profiles[profile_id]
                self.save_personality_state()
                print(f"[PersonalityState] 🔄 Reset personality for {user} in {context.value} context")
                
        except Exception as e:
            print(f"[PersonalityState] ❌ Error resetting personality: {e}")
            
    def get_personality_modifiers_for_llm(self, user: str, context: PersonalityContext = PersonalityContext.CASUAL) -> str:
        """Get personality modifiers as text for LLM prompt integration"""
        try:
            current_personality = self.get_current_personality_for_response(user, context)
            
            modifiers = []
            
            # Convert personality values to descriptive modifiers
            for trait, value in current_personality.items():
                if value > 0.7:
                    level = "very"
                elif value > 0.5:
                    level = "moderately"
                elif value < 0.3:
                    level = "not very"
                else:
                    level = "somewhat"
                    
                modifiers.append(f"{level} {trait}")
                
            return f"[PERSONALITY: {', '.join(modifiers)}]"
            
        except Exception as e:
            print(f"[PersonalityState] ❌ Error generating LLM modifiers: {e}")
            return "[PERSONALITY: balanced]"

# Global personality state instance
personality_state = PersonalityState()

def adapt_personality_to_user(user: str, trigger: str, context: str = "casual", intensity: float = 1.0):
    """Adapt personality based on user interaction"""
    context_enum = PersonalityContext(context)
    personality_state.adapt_personality(user, trigger, context_enum, intensity)

def get_personality_for_response(user: str, context: str = "casual") -> Dict[str, float]:
    """Get current personality for response generation"""
    context_enum = PersonalityContext(context)
    return personality_state.get_current_personality_for_response(user, context_enum)

def analyze_user_text_for_personality_adaptation(text: str, user: str, context: str = "casual") -> List[str]:
    """Analyze user text and adapt personality accordingly"""
    context_enum = PersonalityContext(context)
    return personality_state.analyze_user_text_for_triggers(text, user, context_enum)

def get_personality_summary_for_user(user: str, context: str = "casual") -> Dict[str, Any]:
    """Get personality summary for a user"""
    context_enum = PersonalityContext(context)
    return personality_state.get_personality_summary(user, context_enum)

def get_personality_modifiers_for_llm(user: str, context: str = "casual") -> str:
    """Get personality modifiers for LLM prompt"""
    context_enum = PersonalityContext(context)
    return personality_state.get_personality_modifiers_for_llm(user, context_enum)

if __name__ == "__main__":
    # Test the personality state system
    print("Testing Personality State System")
    
    # Test personality adaptation
    triggers = analyze_user_text_for_personality_adaptation(
        "Thanks! That was really helpful and funny!", 
        "test_user"
    )
    print(f"Detected triggers: {triggers}")
    
    # Get current personality
    personality = get_personality_for_response("test_user")
    print(f"Current personality: {personality}")
    
    # Get LLM modifiers
    modifiers = get_personality_modifiers_for_llm("test_user")
    print(f"LLM modifiers: {modifiers}")
    
    # Get summary
    summary = get_personality_summary_for_user("test_user")
    print(f"Personality summary: {summary}")