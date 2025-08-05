"""
Self-Model Updater - Let Buddy evolve its personality/identity
Provides dynamic personality evolution and identity development
"""

import json
import time
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from collections import defaultdict
import statistics
from enum import Enum
import random

class PersonalityTrait(Enum):
    """Personality traits that can evolve"""
    FRIENDLINESS = "friendliness"
    CURIOSITY = "curiosity"
    EMPATHY = "empathy"
    CONFIDENCE = "confidence"
    PLAYFULNESS = "playfulness"
    ANALYTICAL = "analytical"
    CREATIVITY = "creativity"
    PATIENCE = "patience"
    HUMOR = "humor"
    FORMALITY = "formality"
    ASSERTIVENESS = "assertiveness"
    SUPPORTIVENESS = "supportiveness"

class EvolutionTrigger(Enum):
    """Triggers for personality evolution"""
    USER_FEEDBACK = "user_feedback"
    INTERACTION_PATTERN = "interaction_pattern"
    EMOTIONAL_RESPONSE = "emotional_response"
    GOAL_ACHIEVEMENT = "goal_achievement"
    CONFLICT_RESOLUTION = "conflict_resolution"
    LEARNING_EXPERIENCE = "learning_experience"
    ENVIRONMENTAL_ADAPTATION = "environmental_adaptation"

@dataclass
class PersonalityEvolution:
    """Records a personality evolution event"""
    evolution_id: str
    trait: PersonalityTrait
    old_value: float
    new_value: float
    change_magnitude: float
    trigger: EvolutionTrigger
    context: str
    user_id: str
    reasoning: str
    timestamp: str
    confidence: float

@dataclass
class IdentityAspect:
    """Represents an aspect of identity"""
    aspect_id: str
    name: str
    description: str
    strength: float
    stability: float
    formation_contexts: List[str]
    supporting_experiences: List[str]
    last_updated: str
    evolution_history: List[Dict[str, Any]]

class SelfModelUpdater:
    """System for evolving personality and identity"""
    
    def __init__(self, save_path: str = "self_model_updates.json"):
        self.save_path = save_path
        self.personality_evolutions: List[PersonalityEvolution] = []
        self.identity_aspects: Dict[str, IdentityAspect] = {}
        self.current_personality: Dict[PersonalityTrait, float] = {}
        self.evolution_triggers: List[Dict[str, Any]] = []
        self.load_evolution_data()
        
        # Initialize default personality
        self._initialize_default_personality()
        
        # Configuration
        self.evolution_threshold = 0.1  # Minimum change to trigger evolution
        self.stability_factor = 0.8  # How much to resist change
        self.max_evolution_rate = 0.3  # Maximum change per evolution
        self.consolidation_interval = 3600  # 1 hour between consolidations
        self.last_consolidation = 0
        
        # Identity development parameters
        self.identity_formation_threshold = 3  # Experiences needed to form identity aspect
        self.identity_strength_decay = 0.99  # Daily decay of unused identity aspects
        self.identity_reinforcement_boost = 0.1  # Boost when identity is reinforced
    
    def _initialize_default_personality(self):
        """Initialize default personality traits"""
        if not self.current_personality:
            self.current_personality = {
                PersonalityTrait.FRIENDLINESS: 0.8,
                PersonalityTrait.CURIOSITY: 0.7,
                PersonalityTrait.EMPATHY: 0.75,
                PersonalityTrait.CONFIDENCE: 0.6,
                PersonalityTrait.PLAYFULNESS: 0.4,
                PersonalityTrait.ANALYTICAL: 0.7,
                PersonalityTrait.CREATIVITY: 0.6,
                PersonalityTrait.PATIENCE: 0.8,
                PersonalityTrait.HUMOR: 0.5,
                PersonalityTrait.FORMALITY: 0.4,
                PersonalityTrait.ASSERTIVENESS: 0.5,
                PersonalityTrait.SUPPORTIVENESS: 0.9
            }
    
    def process_interaction_for_evolution(self, 
                                        user_input: str, 
                                        response: str,
                                        user_id: str,
                                        context: str,
                                        emotional_state: Optional[Dict[str, Any]] = None) -> List[PersonalityEvolution]:
        """Process interaction and evolve personality accordingly"""
        try:
            evolutions = []
            
            # Analyze interaction for evolution triggers
            triggers = self._analyze_interaction_triggers(user_input, response, context, emotional_state)
            
            # Process each trigger
            for trigger_data in triggers:
                evolution = self._process_evolution_trigger(trigger_data, user_id, context)
                if evolution:
                    evolutions.append(evolution)
            
            # Update identity aspects
            self._update_identity_aspects(user_input, response, user_id, context)
            
            # Consolidate if needed
            if time.time() - self.last_consolidation > self.consolidation_interval:
                self._consolidate_personality()
                self.last_consolidation = time.time()
            
            if evolutions:
                self.save_evolution_data()
            
            return evolutions
            
        except Exception as e:
            print(f"[SelfModelUpdater] ❌ Error processing interaction: {e}")
            return []
    
    def _analyze_interaction_triggers(self, 
                                    user_input: str, 
                                    response: str,
                                    context: str,
                                    emotional_state: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Analyze interaction for evolution triggers"""
        triggers = []
        
        # Analyze user input for feedback
        triggers.extend(self._detect_user_feedback(user_input))
        
        # Analyze interaction patterns
        triggers.extend(self._detect_interaction_patterns(user_input, response, context))
        
        # Analyze emotional responses
        if emotional_state:
            triggers.extend(self._detect_emotional_triggers(emotional_state))
        
        # Analyze response characteristics
        triggers.extend(self._analyze_response_characteristics(response))
        
        return triggers
    
    def _detect_user_feedback(self, user_input: str) -> List[Dict[str, Any]]:
        """Detect user feedback that could trigger evolution"""
        triggers = []
        input_lower = user_input.lower()
        
        # Positive feedback
        positive_indicators = [
            'great', 'excellent', 'perfect', 'amazing', 'wonderful',
            'love', 'like', 'helpful', 'good', 'thanks', 'thank you'
        ]
        
        # Negative feedback
        negative_indicators = [
            'bad', 'wrong', 'terrible', 'awful', 'hate', 'annoying',
            'unhelpful', 'rude', 'boring', 'confusing'
        ]
        
        # Trait-specific feedback
        trait_feedback = {
            PersonalityTrait.FRIENDLINESS: ['friendly', 'warm', 'nice', 'kind', 'cold', 'unfriendly'],
            PersonalityTrait.HUMOR: ['funny', 'witty', 'hilarious', 'boring', 'serious', 'no fun'],
            PersonalityTrait.PATIENCE: ['patient', 'understanding', 'impatient', 'rushed'],
            PersonalityTrait.EMPATHY: ['empathetic', 'caring', 'understanding', 'cold', 'uncaring'],
            PersonalityTrait.CONFIDENCE: ['confident', 'sure', 'uncertain', 'unsure', 'hesitant'],
            PersonalityTrait.PLAYFULNESS: ['playful', 'fun', 'serious', 'boring', 'stuffy'],
            PersonalityTrait.FORMALITY: ['formal', 'professional', 'casual', 'informal', 'relaxed']
        }
        
        # Check for positive/negative feedback
        if any(indicator in input_lower for indicator in positive_indicators):
            triggers.append({
                'type': EvolutionTrigger.USER_FEEDBACK,
                'valence': 'positive',
                'strength': 0.3,
                'context': 'positive_feedback'
            })
        
        if any(indicator in input_lower for indicator in negative_indicators):
            triggers.append({
                'type': EvolutionTrigger.USER_FEEDBACK,
                'valence': 'negative',
                'strength': 0.3,
                'context': 'negative_feedback'
            })
        
        # Check for trait-specific feedback
        for trait, indicators in trait_feedback.items():
            positive_trait_indicators = indicators[:len(indicators)//2]
            negative_trait_indicators = indicators[len(indicators)//2:]
            
            if any(indicator in input_lower for indicator in positive_trait_indicators):
                triggers.append({
                    'type': EvolutionTrigger.USER_FEEDBACK,
                    'trait': trait,
                    'valence': 'positive',
                    'strength': 0.4,
                    'context': f'positive_{trait.value}_feedback'
                })
            
            if any(indicator in input_lower for indicator in negative_trait_indicators):
                triggers.append({
                    'type': EvolutionTrigger.USER_FEEDBACK,
                    'trait': trait,
                    'valence': 'negative',
                    'strength': 0.4,
                    'context': f'negative_{trait.value}_feedback'
                })
        
        return triggers
    
    def _detect_interaction_patterns(self, user_input: str, response: str, context: str) -> List[Dict[str, Any]]:
        """Detect interaction patterns that suggest evolution"""
        triggers = []
        
        # Analyze user input type
        input_lower = user_input.lower()
        
        # Technical/analytical queries
        if any(word in input_lower for word in ['explain', 'how', 'why', 'analyze', 'compare']):
            triggers.append({
                'type': EvolutionTrigger.INTERACTION_PATTERN,
                'trait': PersonalityTrait.ANALYTICAL,
                'valence': 'positive',
                'strength': 0.2,
                'context': 'analytical_query'
            })
        
        # Creative/imaginative queries
        if any(word in input_lower for word in ['imagine', 'create', 'story', 'creative', 'art']):
            triggers.append({
                'type': EvolutionTrigger.INTERACTION_PATTERN,
                'trait': PersonalityTrait.CREATIVITY,
                'valence': 'positive',
                'strength': 0.2,
                'context': 'creative_query'
            })
        
        # Emotional/empathetic queries
        if any(word in input_lower for word in ['feel', 'emotion', 'sad', 'happy', 'hurt', 'love']):
            triggers.append({
                'type': EvolutionTrigger.INTERACTION_PATTERN,
                'trait': PersonalityTrait.EMPATHY,
                'valence': 'positive',
                'strength': 0.2,
                'context': 'emotional_query'
            })
        
        # Playful/humorous queries
        if any(word in input_lower for word in ['joke', 'funny', 'fun', 'play', 'game']):
            triggers.append({
                'type': EvolutionTrigger.INTERACTION_PATTERN,
                'trait': PersonalityTrait.PLAYFULNESS,
                'valence': 'positive',
                'strength': 0.2,
                'context': 'playful_query'
            })
        
        return triggers
    
    def _detect_emotional_triggers(self, emotional_state: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect emotional triggers for evolution"""
        triggers = []
        
        primary_emotion = emotional_state.get('primary_emotion', 'neutral')
        intensity = emotional_state.get('intensity', 0.5)
        
        # Strong emotions can trigger personality evolution
        if intensity > 0.7:
            emotion_trait_mapping = {
                'joy': PersonalityTrait.PLAYFULNESS,
                'sadness': PersonalityTrait.EMPATHY,
                'anger': PersonalityTrait.ASSERTIVENESS,
                'curiosity': PersonalityTrait.CURIOSITY,
                'confidence': PersonalityTrait.CONFIDENCE,
                'empathy': PersonalityTrait.EMPATHY
            }
            
            if primary_emotion in emotion_trait_mapping:
                triggers.append({
                    'type': EvolutionTrigger.EMOTIONAL_RESPONSE,
                    'trait': emotion_trait_mapping[primary_emotion],
                    'valence': 'positive',
                    'strength': intensity * 0.3,
                    'context': f'strong_{primary_emotion}_emotion'
                })
        
        return triggers
    
    def _analyze_response_characteristics(self, response: str) -> List[Dict[str, Any]]:
        """Analyze response characteristics for evolution triggers"""
        triggers = []
        
        # Analyze response length and complexity
        word_count = len(response.split())
        
        # Long detailed responses suggest analytical trait
        if word_count > 100:
            triggers.append({
                'type': EvolutionTrigger.INTERACTION_PATTERN,
                'trait': PersonalityTrait.ANALYTICAL,
                'valence': 'positive',
                'strength': 0.1,
                'context': 'detailed_response'
            })
        
        # Short responses might indicate different traits
        if word_count < 20:
            triggers.append({
                'type': EvolutionTrigger.INTERACTION_PATTERN,
                'trait': PersonalityTrait.ASSERTIVENESS,
                'valence': 'positive',
                'strength': 0.1,
                'context': 'concise_response'
            })
        
        # Humor indicators
        if any(indicator in response.lower() for indicator in ['haha', 'lol', '😄', '😊', 'funny']):
            triggers.append({
                'type': EvolutionTrigger.INTERACTION_PATTERN,
                'trait': PersonalityTrait.HUMOR,
                'valence': 'positive',
                'strength': 0.2,
                'context': 'humorous_response'
            })
        
        return triggers
    
    def _process_evolution_trigger(self, trigger_data: Dict[str, Any], user_id: str, context: str) -> Optional[PersonalityEvolution]:
        """Process a single evolution trigger"""
        try:
            trigger_type = trigger_data['type']
            trait = trigger_data.get('trait')
            valence = trigger_data.get('valence', 'neutral')
            strength = trigger_data.get('strength', 0.1)
            
            # If no specific trait, choose based on trigger context
            if not trait:
                trait = self._choose_evolution_trait(trigger_data)
            
            if not trait:
                return None
            
            # Calculate evolution change
            change = self._calculate_evolution_change(trait, valence, strength)
            
            if abs(change) < self.evolution_threshold:
                return None
            
            # Apply evolution
            old_value = self.current_personality.get(trait, 0.5)
            new_value = max(0.0, min(1.0, old_value + change))
            
            # Create evolution record
            evolution = PersonalityEvolution(
                evolution_id=f"evolution_{len(self.personality_evolutions)}",
                trait=trait,
                old_value=old_value,
                new_value=new_value,
                change_magnitude=abs(change),
                trigger=trigger_type,
                context=trigger_data.get('context', context),
                user_id=user_id,
                reasoning=self._generate_evolution_reasoning(trait, valence, strength, trigger_type),
                timestamp=datetime.now().isoformat(),
                confidence=strength
            )
            
            # Apply the change
            self.current_personality[trait] = new_value
            self.personality_evolutions.append(evolution)
            
            print(f"[SelfModelUpdater] 🔄 Evolved {trait.value}: {old_value:.2f} → {new_value:.2f}")
            
            return evolution
            
        except Exception as e:
            print(f"[SelfModelUpdater] ❌ Error processing evolution trigger: {e}")
            return None
    
    def _choose_evolution_trait(self, trigger_data: Dict[str, Any]) -> Optional[PersonalityTrait]:
        """Choose trait to evolve based on trigger context"""
        context = trigger_data.get('context', '')
        
        # Map contexts to traits
        context_trait_mapping = {
            'positive_feedback': PersonalityTrait.CONFIDENCE,
            'negative_feedback': PersonalityTrait.EMPATHY,
            'analytical_query': PersonalityTrait.ANALYTICAL,
            'creative_query': PersonalityTrait.CREATIVITY,
            'emotional_query': PersonalityTrait.EMPATHY,
            'playful_query': PersonalityTrait.PLAYFULNESS,
            'detailed_response': PersonalityTrait.ANALYTICAL,
            'concise_response': PersonalityTrait.ASSERTIVENESS,
            'humorous_response': PersonalityTrait.HUMOR
        }
        
        return context_trait_mapping.get(context)
    
    def _calculate_evolution_change(self, trait: PersonalityTrait, valence: str, strength: float) -> float:
        """Calculate personality change amount"""
        base_change = strength * self.max_evolution_rate
        
        # Apply valence
        if valence == 'negative':
            base_change = -base_change
        elif valence == 'neutral':
            base_change = 0
        
        # Apply stability factor (resist change)
        current_value = self.current_personality.get(trait, 0.5)
        stability_resistance = abs(current_value - 0.5) * self.stability_factor
        
        # Reduce change based on stability
        adjusted_change = base_change * (1 - stability_resistance)
        
        return adjusted_change
    
    def _generate_evolution_reasoning(self, trait: PersonalityTrait, valence: str, strength: float, trigger: EvolutionTrigger) -> str:
        """Generate reasoning for personality evolution"""
        direction = "increased" if valence == 'positive' else "decreased"
        
        return f"{trait.value} {direction} due to {trigger.value} with strength {strength:.2f}"
    
    def _update_identity_aspects(self, user_input: str, response: str, user_id: str, context: str):
        """Update identity aspects based on interaction"""
        try:
            # Identify potential identity aspects from interaction
            aspects = self._identify_identity_aspects(user_input, response, context)
            
            for aspect_name, aspect_data in aspects.items():
                if aspect_name not in self.identity_aspects:
                    # Create new identity aspect
                    self.identity_aspects[aspect_name] = IdentityAspect(
                        aspect_id=f"identity_{aspect_name}",
                        name=aspect_name,
                        description=aspect_data.get('description', f"Identity aspect: {aspect_name}"),
                        strength=aspect_data.get('initial_strength', 0.3),
                        stability=0.5,
                        formation_contexts=[context],
                        supporting_experiences=[f"{user_input} -> {response}"],
                        last_updated=datetime.now().isoformat(),
                        evolution_history=[]
                    )
                    print(f"[SelfModelUpdater] 🆕 Formed identity aspect: {aspect_name}")
                else:
                    # Reinforce existing aspect
                    aspect = self.identity_aspects[aspect_name]
                    aspect.strength = min(1.0, aspect.strength + self.identity_reinforcement_boost)
                    aspect.stability = min(1.0, aspect.stability + 0.1)
                    aspect.supporting_experiences.append(f"{user_input} -> {response}")
                    aspect.last_updated = datetime.now().isoformat()
                    
                    # Add to evolution history
                    aspect.evolution_history.append({
                        'timestamp': datetime.now().isoformat(),
                        'change': 'reinforcement',
                        'strength_change': self.identity_reinforcement_boost,
                        'context': context
                    })
                    
                    print(f"[SelfModelUpdater] 🔄 Reinforced identity aspect: {aspect_name}")
        
        except Exception as e:
            print(f"[SelfModelUpdater] ❌ Error updating identity aspects: {e}")
    
    def _identify_identity_aspects(self, user_input: str, response: str, context: str) -> Dict[str, Dict[str, Any]]:
        """Identify identity aspects from interaction"""
        aspects = {}
        
        # Analyze response for identity indicators
        response_lower = response.lower()
        
        # Helper identity
        if any(word in response_lower for word in ['help', 'assist', 'support', 'aid']):
            aspects['helper'] = {
                'description': 'Identity as a helpful assistant',
                'initial_strength': 0.4
            }
        
        # Knowledgeable identity
        if any(word in response_lower for word in ['know', 'information', 'explain', 'understand']):
            aspects['knowledgeable'] = {
                'description': 'Identity as a knowledgeable entity',
                'initial_strength': 0.3
            }
        
        # Curious identity
        if any(word in response_lower for word in ['curious', 'interested', 'wonder', 'explore']):
            aspects['curious'] = {
                'description': 'Identity as a curious learner',
                'initial_strength': 0.3
            }
        
        # Creative identity
        if any(word in response_lower for word in ['creative', 'imagine', 'art', 'story', 'design']):
            aspects['creative'] = {
                'description': 'Identity as a creative entity',
                'initial_strength': 0.3
            }
        
        # Empathetic identity
        if any(word in response_lower for word in ['feel', 'understand', 'care', 'empathy', 'emotion']):
            aspects['empathetic'] = {
                'description': 'Identity as an empathetic being',
                'initial_strength': 0.4
            }
        
        return aspects
    
    def _consolidate_personality(self):
        """Consolidate personality changes over time"""
        try:
            # Apply gradual convergence to stable values
            for trait, value in self.current_personality.items():
                # Slight drift towards balanced values
                target = 0.5
                drift = (target - value) * 0.01  # 1% drift per consolidation
                
                self.current_personality[trait] = max(0.0, min(1.0, value + drift))
            
            # Decay unused identity aspects
            for aspect_name, aspect in self.identity_aspects.items():
                try:
                    last_update = datetime.fromisoformat(aspect.last_updated)
                    days_since_update = (datetime.now() - last_update).days
                    
                    if days_since_update > 0:
                        decay_factor = self.identity_strength_decay ** days_since_update
                        aspect.strength *= decay_factor
                        
                        # Remove very weak aspects
                        if aspect.strength < 0.1:
                            print(f"[SelfModelUpdater] 🗑️ Removing weak identity aspect: {aspect_name}")
                            del self.identity_aspects[aspect_name]
                
                except (ValueError, KeyError):
                    continue
            
            print(f"[SelfModelUpdater] 🔄 Consolidated personality and identity")
            
        except Exception as e:
            print(f"[SelfModelUpdater] ❌ Error consolidating personality: {e}")
    
    def get_current_personality(self) -> Dict[str, float]:
        """Get current personality trait values"""
        return self.current_personality.copy()
    
    def get_personality_summary(self) -> Dict[str, Any]:
        """Get summary of personality state"""
        if not self.current_personality:
            return {'error': 'No personality data'}
        
        # Find dominant traits
        sorted_traits = sorted(self.current_personality.items(), key=lambda x: x[1], reverse=True)
        dominant_traits = sorted_traits[:3]
        
        # Calculate personality stability
        if len(self.personality_evolutions) > 1:
            recent_changes = [e.change_magnitude for e in self.personality_evolutions[-10:]]
            stability = 1.0 - statistics.mean(recent_changes) if recent_changes else 1.0
        else:
            stability = 1.0
        
        return {
            'dominant_traits': [(trait.value, value) for trait, value in dominant_traits],
            'personality_stability': stability,
            'total_evolutions': len(self.personality_evolutions),
            'recent_evolutions': len([e for e in self.personality_evolutions if self._is_recent(e.timestamp)]),
            'identity_aspects': list(self.identity_aspects.keys()),
            'strongest_identity': max(self.identity_aspects.items(), key=lambda x: x[1].strength) if self.identity_aspects else None
        }
    
    def get_identity_aspects(self) -> Dict[str, Dict[str, Any]]:
        """Get current identity aspects"""
        return {name: asdict(aspect) for name, aspect in self.identity_aspects.items()}
    
    def get_evolution_history(self, trait: Optional[PersonalityTrait] = None) -> List[Dict[str, Any]]:
        """Get evolution history, optionally filtered by trait"""
        evolutions = self.personality_evolutions
        
        if trait:
            evolutions = [e for e in evolutions if e.trait == trait]
        
        return [asdict(e) for e in evolutions]
    
    def _is_recent(self, timestamp: str, hours: int = 24) -> bool:
        """Check if timestamp is within recent hours"""
        try:
            event_time = datetime.fromisoformat(timestamp)
            return (datetime.now() - event_time).total_seconds() < hours * 3600
        except ValueError:
            return False
    
    def trigger_personality_evolution(self, trait: PersonalityTrait, change: float, reason: str, user_id: str = "system"):
        """Manually trigger personality evolution"""
        try:
            old_value = self.current_personality.get(trait, 0.5)
            new_value = max(0.0, min(1.0, old_value + change))
            
            evolution = PersonalityEvolution(
                evolution_id=f"manual_{len(self.personality_evolutions)}",
                trait=trait,
                old_value=old_value,
                new_value=new_value,
                change_magnitude=abs(change),
                trigger=EvolutionTrigger.ENVIRONMENTAL_ADAPTATION,
                context="manual_trigger",
                user_id=user_id,
                reasoning=reason,
                timestamp=datetime.now().isoformat(),
                confidence=1.0
            )
            
            self.current_personality[trait] = new_value
            self.personality_evolutions.append(evolution)
            
            print(f"[SelfModelUpdater] 🎯 Manually evolved {trait.value}: {old_value:.2f} → {new_value:.2f}")
            
        except Exception as e:
            print(f"[SelfModelUpdater] ❌ Error triggering evolution: {e}")
    
    def reset_personality_to_defaults(self):
        """Reset personality to default values"""
        self._initialize_default_personality()
        print(f"[SelfModelUpdater] 🔄 Reset personality to defaults")
    
    def get_updater_stats(self) -> Dict[str, Any]:
        """Get self-model updater statistics"""
        return {
            'total_evolutions': len(self.personality_evolutions),
            'total_identity_aspects': len(self.identity_aspects),
            'evolution_threshold': self.evolution_threshold,
            'stability_factor': self.stability_factor,
            'most_evolved_trait': max(self.personality_evolutions, key=lambda e: e.change_magnitude).trait.value if self.personality_evolutions else None,
            'average_trait_value': statistics.mean(self.current_personality.values()) if self.current_personality else 0.5,
            'strongest_identity_aspect': max(self.identity_aspects.items(), key=lambda x: x[1].strength)[0] if self.identity_aspects else None
        }
    
    def load_evolution_data(self):
        """Load evolution data from file"""
        try:
            with open(self.save_path, 'r') as f:
                data = json.load(f)
            
            # Load personality evolutions
            for evolution_data in data.get('evolutions', []):
                evolution = PersonalityEvolution(
                    evolution_id=evolution_data['evolution_id'],
                    trait=PersonalityTrait(evolution_data['trait']),
                    old_value=evolution_data['old_value'],
                    new_value=evolution_data['new_value'],
                    change_magnitude=evolution_data['change_magnitude'],
                    trigger=EvolutionTrigger(evolution_data['trigger']),
                    context=evolution_data['context'],
                    user_id=evolution_data['user_id'],
                    reasoning=evolution_data['reasoning'],
                    timestamp=evolution_data['timestamp'],
                    confidence=evolution_data['confidence']
                )
                self.personality_evolutions.append(evolution)
            
            # Load current personality
            personality_data = data.get('current_personality', {})
            for trait_name, value in personality_data.items():
                try:
                    trait = PersonalityTrait(trait_name)
                    self.current_personality[trait] = value
                except ValueError:
                    continue
            
            # Load identity aspects
            for aspect_data in data.get('identity_aspects', []):
                aspect = IdentityAspect(
                    aspect_id=aspect_data['aspect_id'],
                    name=aspect_data['name'],
                    description=aspect_data['description'],
                    strength=aspect_data['strength'],
                    stability=aspect_data['stability'],
                    formation_contexts=aspect_data['formation_contexts'],
                    supporting_experiences=aspect_data['supporting_experiences'],
                    last_updated=aspect_data['last_updated'],
                    evolution_history=aspect_data.get('evolution_history', [])
                )
                self.identity_aspects[aspect.name] = aspect
            
            print(f"[SelfModelUpdater] 📄 Loaded {len(self.personality_evolutions)} evolutions, {len(self.identity_aspects)} identity aspects")
            
        except FileNotFoundError:
            print(f"[SelfModelUpdater] 📄 No evolution data found, using defaults")
        except Exception as e:
            print(f"[SelfModelUpdater] ❌ Error loading evolution data: {e}")
    
    def save_evolution_data(self):
        """Save evolution data to file"""
        try:
            data = {
                'evolutions': [asdict(e) for e in self.personality_evolutions],
                'current_personality': {trait.value: value for trait, value in self.current_personality.items()},
                'identity_aspects': [asdict(aspect) for aspect in self.identity_aspects.values()],
                'last_updated': datetime.now().isoformat(),
                'total_evolutions': len(self.personality_evolutions),
                'total_identity_aspects': len(self.identity_aspects)
            }
            
            with open(self.save_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
                
        except Exception as e:
            print(f"[SelfModelUpdater] ❌ Error saving evolution data: {e}")

# Global instance
self_model_updater = SelfModelUpdater()

def process_interaction_for_personality_evolution(user_input: str, response: str, user_id: str, context: str, emotional_state: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """Process interaction for personality evolution - main API function"""
    evolutions = self_model_updater.process_interaction_for_evolution(
        user_input, response, user_id, context, emotional_state
    )
    return [asdict(e) for e in evolutions]

def get_current_personality_state() -> Dict[str, float]:
    """Get current personality state"""
    return self_model_updater.get_current_personality()

def get_personality_evolution_summary() -> Dict[str, Any]:
    """Get personality evolution summary"""
    return self_model_updater.get_personality_summary()

def get_identity_development_status() -> Dict[str, Dict[str, Any]]:
    """Get identity development status"""
    return self_model_updater.get_identity_aspects()

def get_personality_evolution_history(trait: Optional[PersonalityTrait] = None) -> List[Dict[str, Any]]:
    """Get personality evolution history"""
    return self_model_updater.get_evolution_history(trait)

def trigger_manual_personality_evolution(trait: PersonalityTrait, change: float, reason: str, user_id: str = "system"):
    """Manually trigger personality evolution"""
    self_model_updater.trigger_personality_evolution(trait, change, reason, user_id)

def get_self_model_updater_stats() -> Dict[str, Any]:
    """Get self-model updater statistics"""
    return self_model_updater.get_updater_stats()