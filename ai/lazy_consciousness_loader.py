"""
Lazy Consciousness Loading System for Performance Optimization
Created: 2025-01-17
Purpose: Only activate consciousness modules when contextually relevant
         to reduce processing time and token usage
"""

import json
import time
import re
from typing import Dict, List, Any, Optional, Set
from datetime import datetime
from enum import Enum

class InteractionType(Enum):
    """Types of user interactions for context-aware module selection"""
    CASUAL_CHAT = "casual_chat"
    EMOTIONAL_SUPPORT = "emotional_support"
    GOAL_PLANNING = "goal_planning"
    MEMORY_RECALL = "memory_recall"
    CREATIVE_TASK = "creative_task"
    PROBLEM_SOLVING = "problem_solving"
    SMALL_TALK = "small_talk"
    DEEP_CONVERSATION = "deep_conversation"
    TECHNICAL_QUESTION = "technical_question"
    PERSONAL_SHARING = "personal_sharing"

class ConsciousnessModule(Enum):
    """Available consciousness modules for lazy loading"""
    MOOD_MANAGER = "mood_manager"
    MEMORY_TIMELINE = "memory_timeline"
    GOAL_MANAGER = "goal_manager"
    PERSONALITY_PROFILE = "personality_profile"
    THOUGHT_LOOP = "thought_loop"
    EMOTION_ENGINE = "emotion_engine"
    MOTIVATION_SYSTEM = "motivation_system"
    TEMPORAL_AWARENESS = "temporal_awareness"
    SELF_MODEL = "self_model"
    BELIEF_TRACKER = "belief_tracker"
    INNER_MONOLOGUE = "inner_monologue"
    SUBJECTIVE_EXPERIENCE = "subjective_experience"

class LazyConsciousnessLoader:
    """
    Intelligent consciousness module loader that only activates modules
    when they're contextually relevant to the interaction
    """
    
    def __init__(self):
        # Module relevance mapping for different interaction types
        self.module_relevance = {
            InteractionType.CASUAL_CHAT: {
                ConsciousnessModule.MOOD_MANAGER: 0.8,
                ConsciousnessModule.PERSONALITY_PROFILE: 0.9,
                ConsciousnessModule.MEMORY_TIMELINE: 0.4,
                ConsciousnessModule.TEMPORAL_AWARENESS: 0.3,
            },
            InteractionType.EMOTIONAL_SUPPORT: {
                ConsciousnessModule.MOOD_MANAGER: 1.0,
                ConsciousnessModule.EMOTION_ENGINE: 1.0,
                ConsciousnessModule.MEMORY_TIMELINE: 0.8,
                ConsciousnessModule.PERSONALITY_PROFILE: 0.9,
                ConsciousnessModule.INNER_MONOLOGUE: 0.7,
                ConsciousnessModule.SUBJECTIVE_EXPERIENCE: 0.6,
            },
            InteractionType.GOAL_PLANNING: {
                ConsciousnessModule.GOAL_MANAGER: 1.0,
                ConsciousnessModule.MOTIVATION_SYSTEM: 0.9,
                ConsciousnessModule.MEMORY_TIMELINE: 0.7,
                ConsciousnessModule.TEMPORAL_AWARENESS: 0.8,
                ConsciousnessModule.THOUGHT_LOOP: 0.6,
            },
            InteractionType.MEMORY_RECALL: {
                ConsciousnessModule.MEMORY_TIMELINE: 1.0,
                ConsciousnessModule.TEMPORAL_AWARENESS: 0.9,
                ConsciousnessModule.INNER_MONOLOGUE: 0.6,
                ConsciousnessModule.MOOD_MANAGER: 0.4,
            },
            InteractionType.CREATIVE_TASK: {
                ConsciousnessModule.THOUGHT_LOOP: 1.0,
                ConsciousnessModule.INNER_MONOLOGUE: 0.9,
                ConsciousnessModule.MOOD_MANAGER: 0.7,
                ConsciousnessModule.SUBJECTIVE_EXPERIENCE: 0.8,
                ConsciousnessModule.PERSONALITY_PROFILE: 0.6,
            },
            InteractionType.PROBLEM_SOLVING: {
                ConsciousnessModule.THOUGHT_LOOP: 1.0,
                ConsciousnessModule.MEMORY_TIMELINE: 0.8,
                ConsciousnessModule.GOAL_MANAGER: 0.7,
                ConsciousnessModule.TEMPORAL_AWARENESS: 0.5,
            },
            InteractionType.SMALL_TALK: {
                ConsciousnessModule.PERSONALITY_PROFILE: 0.8,
                ConsciousnessModule.MOOD_MANAGER: 0.6,
                ConsciousnessModule.TEMPORAL_AWARENESS: 0.4,
            },
            InteractionType.DEEP_CONVERSATION: {
                ConsciousnessModule.BELIEF_TRACKER: 1.0,
                ConsciousnessModule.SELF_MODEL: 0.9,
                ConsciousnessModule.INNER_MONOLOGUE: 0.8,
                ConsciousnessModule.SUBJECTIVE_EXPERIENCE: 0.9,
                ConsciousnessModule.MEMORY_TIMELINE: 0.7,
                ConsciousnessModule.EMOTION_ENGINE: 0.6,
            },
            InteractionType.TECHNICAL_QUESTION: {
                ConsciousnessModule.THOUGHT_LOOP: 0.8,
                ConsciousnessModule.MEMORY_TIMELINE: 0.6,
                ConsciousnessModule.PERSONALITY_PROFILE: 0.4,
            },
            InteractionType.PERSONAL_SHARING: {
                ConsciousnessModule.EMOTION_ENGINE: 1.0,
                ConsciousnessModule.MEMORY_TIMELINE: 0.9,
                ConsciousnessModule.MOOD_MANAGER: 0.8,
                ConsciousnessModule.INNER_MONOLOGUE: 0.7,
                ConsciousnessModule.SUBJECTIVE_EXPERIENCE: 0.8,
            },
        }
        
        # Keyword patterns for interaction type detection
        self.interaction_patterns = {
            InteractionType.EMOTIONAL_SUPPORT: [
                r'\b(sad|depressed|anxious|worried|stressed|upset|hurt|pain|difficult|hard)\b',
                r'\b(feeling|feel|emotion|mood|mental|heart|soul)\b',
                r'\b(help|support|comfort|understand|listen|care)\b',
                r'\b(lonely|alone|isolated|disconnected)\b',
            ],
            InteractionType.GOAL_PLANNING: [
                r'\b(goal|plan|future|want|achieve|accomplish|target|objective)\b',
                r'\b(schedule|organize|prioritize|manage|strategy)\b',
                r'\b(improve|better|progress|develop|grow|advance)\b',
                r'\b(project|task|work|career|life|dream)\b',
            ],
            InteractionType.MEMORY_RECALL: [
                r'\b(remember|recall|past|yesterday|before|history|memory)\b',
                r'\b(told|said|mentioned|discussed|talked|conversation)\b',
                r'\b(when|where|how|what happened|what did)\b',
                r'\b(last time|earlier|previous|ago|while back)\b',
            ],
            InteractionType.CREATIVE_TASK: [
                r'\b(create|make|design|build|write|compose|imagine)\b',
                r'\b(idea|concept|creative|artistic|innovation|invention)\b',
                r'\b(story|poem|song|art|music|painting|drawing)\b',
                r'\b(brainstorm|think|explore|experiment|try)\b',
            ],
            InteractionType.PROBLEM_SOLVING: [
                r'\b(problem|issue|challenge|difficulty|solve|fix|resolve)\b',
                r'\b(how|why|what|analyze|understand|figure|work)\b',
                r'\b(solution|answer|approach|method|way|strategy)\b',
                r'\b(stuck|confused|unclear|complex|complicated)\b',
            ],
            InteractionType.DEEP_CONVERSATION: [
                r'\b(meaning|purpose|life|existence|consciousness|reality)\b',
                r'\b(believe|philosophy|think|opinion|perspective|view)\b',
                r'\b(value|important|matter|significant|profound)\b',
                r'\b(soul|spirit|deep|profound|fundamental|essence)\b',
            ],
            InteractionType.TECHNICAL_QUESTION: [
                r'\b(how|what|explain|define|technical|specific|detail)\b',
                r'\b(function|work|process|system|method|procedure)\b',
                r'\b(code|program|software|computer|technology|algorithm)\b',
                r'\b(calculate|compute|analyze|data|information)\b',
            ],
            InteractionType.PERSONAL_SHARING: [
                r'\b(my|me|i|personal|private|share|tell|open)\b',
                r'\b(family|friend|relationship|love|partner|spouse)\b',
                r'\b(experience|story|happened|went|did|feel)\b',
                r'\b(secret|confidential|personal|intimate|private)\b',
            ],
        }
        
        # Default minimal consciousness for all interactions
        self.minimal_consciousness = {
            ConsciousnessModule.MOOD_MANAGER: 0.6,
            ConsciousnessModule.PERSONALITY_PROFILE: 0.7,
            ConsciousnessModule.TEMPORAL_AWARENESS: 0.3,
        }
        
        # Cache for loaded modules (avoid reloading in same session)
        self.module_cache = {}
        self.cache_timestamp = {}
        self.cache_ttl = 300  # 5 minutes
        
    def detect_interaction_type(self, user_input: str, context: Dict[str, Any] = None) -> InteractionType:
        """
        Analyze user input to determine interaction type for module selection
        
        Args:
            user_input: User's text input
            context: Additional context (conversation history, user state, etc.)
            
        Returns:
            Detected interaction type
        """
        try:
            input_lower = user_input.lower()
            type_scores = {}
            
            # Score each interaction type based on keyword matches
            for interaction_type, patterns in self.interaction_patterns.items():
                score = 0
                for pattern in patterns:
                    matches = len(re.findall(pattern, input_lower))
                    score += matches
                
                # Normalize by number of patterns
                type_scores[interaction_type] = score / len(patterns)
            
            # Add context-based scoring if available
            if context:
                type_scores = self._apply_context_scoring(type_scores, context)
            
            # Get highest scoring type
            if type_scores:
                best_type = max(type_scores.items(), key=lambda x: x[1])
                if best_type[1] > 0.1:  # Minimum confidence threshold
                    print(f"[LazyConsciousnessLoader] 🎯 Detected interaction type: {best_type[0].value} (confidence: {best_type[1]:.2f})")
                    return best_type[0]
            
            # Default to casual chat
            print(f"[LazyConsciousnessLoader] 💬 Defaulting to casual chat interaction")
            return InteractionType.CASUAL_CHAT
            
        except Exception as e:
            print(f"[LazyConsciousnessLoader] ❌ Error detecting interaction type: {e}")
            return InteractionType.CASUAL_CHAT
    
    def _apply_context_scoring(self, type_scores: Dict[InteractionType, float], context: Dict[str, Any]) -> Dict[InteractionType, float]:
        """Apply additional scoring based on conversation context"""
        try:
            # Recent conversation topics
            if 'recent_topics' in context:
                topics = context['recent_topics']
                for topic in topics:
                    if 'emotional' in topic.lower():
                        type_scores[InteractionType.EMOTIONAL_SUPPORT] += 0.2
                    elif 'goal' in topic.lower() or 'plan' in topic.lower():
                        type_scores[InteractionType.GOAL_PLANNING] += 0.2
                    elif 'memory' in topic.lower() or 'remember' in topic.lower():
                        type_scores[InteractionType.MEMORY_RECALL] += 0.2
            
            # User emotional state
            if 'user_mood' in context:
                mood = context['user_mood']
                if mood in ['sad', 'anxious', 'stressed']:
                    type_scores[InteractionType.EMOTIONAL_SUPPORT] += 0.3
                elif mood in ['curious', 'thoughtful']:
                    type_scores[InteractionType.DEEP_CONVERSATION] += 0.2
                elif mood in ['creative', 'inspired']:
                    type_scores[InteractionType.CREATIVE_TASK] += 0.2
            
            # Time-based patterns
            if 'time_of_day' in context:
                time_period = context['time_of_day']
                if time_period in ['late_night', 'early_morning']:
                    type_scores[InteractionType.DEEP_CONVERSATION] += 0.1
                    type_scores[InteractionType.PERSONAL_SHARING] += 0.1
            
            return type_scores
            
        except Exception as e:
            print(f"[LazyConsciousnessLoader] ⚠️ Context scoring error: {e}")
            return type_scores
    
    def select_consciousness_modules(self, 
                                   interaction_type: InteractionType,
                                   relevance_threshold: float = 0.5,
                                   max_modules: int = 6) -> Set[ConsciousnessModule]:
        """
        Select which consciousness modules to activate based on interaction type
        
        Args:
            interaction_type: Type of interaction detected
            relevance_threshold: Minimum relevance score to include module
            max_modules: Maximum number of modules to activate
            
        Returns:
            Set of modules to activate
        """
        try:
            # Start with minimal consciousness
            selected_modules = set()
            module_scores = dict(self.minimal_consciousness)
            
            # Add interaction-specific modules
            if interaction_type in self.module_relevance:
                interaction_modules = self.module_relevance[interaction_type]
                for module, score in interaction_modules.items():
                    module_scores[module] = max(module_scores.get(module, 0), score)
            
            # Filter by relevance threshold and limit count
            relevant_modules = [
                (module, score) for module, score in module_scores.items()
                if score >= relevance_threshold
            ]
            
            # Sort by relevance and take top modules
            relevant_modules.sort(key=lambda x: x[1], reverse=True)
            selected_modules = {module for module, _ in relevant_modules[:max_modules]}
            
            print(f"[LazyConsciousnessLoader] 🧠 Selected {len(selected_modules)} modules for {interaction_type.value}")
            for module in selected_modules:
                score = module_scores.get(module, 0)
                print(f"[LazyConsciousnessLoader]   • {module.value}: {score:.2f}")
            
            return selected_modules
            
        except Exception as e:
            print(f"[LazyConsciousnessLoader] ❌ Module selection error: {e}")
            # Return minimal consciousness as fallback
            return set(self.minimal_consciousness.keys())
    
    def load_selected_modules(self, 
                            selected_modules: Set[ConsciousnessModule],
                            user_id: str) -> Dict[str, Any]:
        """
        Load only the selected consciousness modules
        
        Args:
            selected_modules: Set of modules to load
            user_id: User identifier for module initialization
            
        Returns:
            Dictionary of loaded modules and their data
        """
        try:
            loaded_modules = {}
            current_time = time.time()
            
            for module in selected_modules:
                # Check cache first
                cache_key = f"{user_id}_{module.value}"
                if (cache_key in self.module_cache and 
                    cache_key in self.cache_timestamp and
                    current_time - self.cache_timestamp[cache_key] < self.cache_ttl):
                    
                    loaded_modules[module.value] = self.module_cache[cache_key]
                    print(f"[LazyConsciousnessLoader] 📋 Loaded {module.value} from cache")
                    continue
                
                # Load module dynamically
                module_data = self._load_module(module, user_id)
                if module_data:
                    loaded_modules[module.value] = module_data
                    # Cache the result
                    self.module_cache[cache_key] = module_data
                    self.cache_timestamp[cache_key] = current_time
                    print(f"[LazyConsciousnessLoader] ✅ Loaded {module.value}")
                else:
                    print(f"[LazyConsciousnessLoader] ⚠️ Failed to load {module.value}")
            
            print(f"[LazyConsciousnessLoader] 🎯 Successfully loaded {len(loaded_modules)}/{len(selected_modules)} modules")
            return loaded_modules
            
        except Exception as e:
            print(f"[LazyConsciousnessLoader] ❌ Module loading error: {e}")
            return {}
    
    def _load_module(self, module: ConsciousnessModule, user_id: str) -> Optional[Dict[str, Any]]:
        """Load a specific consciousness module"""
        try:
            if module == ConsciousnessModule.MOOD_MANAGER:
                return self._load_mood_manager(user_id)
            elif module == ConsciousnessModule.MEMORY_TIMELINE:
                return self._load_memory_timeline(user_id)
            elif module == ConsciousnessModule.GOAL_MANAGER:
                return self._load_goal_manager(user_id)
            elif module == ConsciousnessModule.PERSONALITY_PROFILE:
                return self._load_personality_profile(user_id)
            elif module == ConsciousnessModule.THOUGHT_LOOP:
                return self._load_thought_loop(user_id)
            elif module == ConsciousnessModule.EMOTION_ENGINE:
                return self._load_emotion_engine(user_id)
            elif module == ConsciousnessModule.MOTIVATION_SYSTEM:
                return self._load_motivation_system(user_id)
            elif module == ConsciousnessModule.TEMPORAL_AWARENESS:
                return self._load_temporal_awareness(user_id)
            elif module == ConsciousnessModule.SELF_MODEL:
                return self._load_self_model(user_id)
            elif module == ConsciousnessModule.BELIEF_TRACKER:
                return self._load_belief_tracker(user_id)
            elif module == ConsciousnessModule.INNER_MONOLOGUE:
                return self._load_inner_monologue(user_id)
            elif module == ConsciousnessModule.SUBJECTIVE_EXPERIENCE:
                return self._load_subjective_experience(user_id)
            else:
                return None
                
        except Exception as e:
            print(f"[LazyConsciousnessLoader] ❌ Error loading {module.value}: {e}")
            return None
    
    def _load_mood_manager(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Load mood manager module"""
        try:
            from ai.mood_manager import get_mood_manager
            mood_manager = get_mood_manager(user_id)
            mood_modifiers = mood_manager.get_mood_based_response_modifiers()
            return {
                'current_mood': mood_modifiers.get('current_mood', 'neutral'),
                'emotional_valence': mood_modifiers.get('emotional_valence', 0.0),
                'mood_intensity': mood_modifiers.get('mood_intensity', 0.5),
                'response_modifiers': mood_modifiers
            }
        except ImportError:
            return None
    
    def _load_memory_timeline(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Load memory timeline module"""
        try:
            from ai.memory_timeline import get_memory_timeline
            memory_timeline = get_memory_timeline(user_id)
            recent_memories = memory_timeline.recall_memories(limit=3)
            return {
                'recent_memories': [m.content[:100] for m in recent_memories],
                'memory_count': len(recent_memories),
                'context_topics': [m.tags[0] if m.tags else 'general' for m in recent_memories]
            }
        except ImportError:
            return None
    
    def _load_goal_manager(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Load goal manager module"""
        try:
            from ai.goal_manager import get_goal_manager
            goal_manager = get_goal_manager(user_id)
            active_goals = goal_manager.get_goals(include_completed=False)
            return {
                'active_goals': [
                    {
                        'title': g.title,
                        'progress': g.progress_percentage,
                        'priority': getattr(g, 'priority', 0.5),
                        'status': 'active'
                    } for g in active_goals[:3]
                ],
                'goal_count': len(active_goals)
            }
        except ImportError:
            return None
    
    def _load_personality_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Load personality profile module"""
        try:
            from ai.personality_profile import get_personality_modifiers
            personality_mods = get_personality_modifiers(user_id)
            return {
                'style': personality_mods.get('interaction_style', 'balanced'),
                'modifiers': {k: v for k, v in personality_mods.items() if isinstance(v, (int, float))},
                'traits': personality_mods
            }
        except ImportError:
            return None
    
    def _load_thought_loop(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Load thought loop module"""
        try:
            from ai.thought_loop import get_thought_loop
            thought_loop = get_thought_loop(user_id)
            recent_thoughts = thought_loop.get_current_thoughts()
            return {
                'recent_thoughts': [t.content[:80] for t in recent_thoughts[-2:]],
                'thought_intensity': 0.6,  # Default
                'thought_type': 'mixed' if recent_thoughts else 'none'
            }
        except ImportError:
            return None
    
    def _load_emotion_engine(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Load emotion engine module"""
        try:
            from ai.emotion import get_current_emotional_state
            # Call without arguments as the function doesn't take user_id
            emotional_state = get_current_emotional_state()
            return {
                'dominant_emotion': emotional_state.get('current_emotion', 'neutral'),
                'intensity': emotional_state.get('intensity', 0.5),
                'valence': emotional_state.get('valence', 0.0)
            }
        except (ImportError, TypeError) as e:
            print(f"[LazyConsciousnessLoader] ❌ Error loading emotion_engine: {e}")
            return None
    
    def _load_motivation_system(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Load motivation system module"""
        try:
            from ai.motivation import motivation_system
            motivation_state = motivation_system.get_current_motivations(user_id)
            return {
                'current_motivations': motivation_state.get('active_motivations', []),
                'motivation_level': motivation_state.get('overall_level', 0.7)
            }
        except ImportError:
            return None
    
    def _load_temporal_awareness(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Load temporal awareness module"""
        try:
            from ai.temporal_awareness import temporal_awareness
            temporal_state = temporal_awareness.get_current_time_context()
            return {
                'time_of_day': temporal_state.get('time_period', 'unknown'),
                'session_duration': temporal_state.get('session_length', 'short'),
                'temporal_patterns': temporal_state.get('patterns', [])
            }
        except ImportError:
            return None
    
    def _load_self_model(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Load self model module"""
        try:
            from ai.self_model import self_model
            # Use the get_identity_summary method that actually exists
            self_state = self_model.get_identity_summary()
            return {
                'self_awareness_level': self_state.get('current_state', {}).get('self_awareness', 0.7),
                'identity_aspects': list(self_state.get('core_identity', {}).keys())[:3],
                'self_reflection': self_state.get('core_identity', {})
            }
        except (ImportError, AttributeError) as e:
            print(f"[LazyConsciousnessLoader] ❌ Error loading self_model: {e}")
            return None
    
    def _load_belief_tracker(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Load belief tracker module"""
        try:
            from ai.belief_evolution_tracker import get_belief_tracker
            belief_tracker = get_belief_tracker(user_id)
            active_beliefs = belief_tracker.get_active_beliefs()
            return {
                'active_beliefs': [b.content[:60] for b in active_beliefs[:3]],
                'belief_strength': [b.confidence for b in active_beliefs[:3]],
                'contradictions': belief_tracker.detect_contradictions()
            }
        except (ImportError, AttributeError) as e:
            print(f"[LazyConsciousnessLoader] ❌ Error loading belief_tracker: {e}")
            return None
    
    def _load_inner_monologue(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Load inner monologue module"""
        try:
            from ai.inner_monologue import inner_monologue
            # Use the get_recent_thoughts method correctly without user_id parameter
            monologue_state = inner_monologue.get_recent_thoughts(limit=5)
            return {
                'inner_thoughts': [t.content[:60] for t in monologue_state],
                'thought_flow': 'normal',  # Default since we don't have flow_state
                'introspection_level': 0.5  # Default value
            }
        except (ImportError, AttributeError) as e:
            print(f"[LazyConsciousnessLoader] ❌ Error loading inner_monologue: {e}")
            return None
    
    def _load_subjective_experience(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Load subjective experience module"""
        try:
            from ai.subjective_experience import subjective_experience
            # Use the introspect_current_state method that actually exists
            experience_state = subjective_experience.introspect_current_state()
            return {
                'qualia_intensity': 0.6,  # Default value since we have different data structure
                'experience_richness': 0.7,  # Default value
                'subjective_narrative': experience_state.get('subjective_insights', [''])[-1] if experience_state.get('subjective_insights') else ''
            }
        except (ImportError, AttributeError) as e:
            print(f"[LazyConsciousnessLoader] ❌ Error loading subjective_experience: {e}")
            return None
    
    def get_consciousness_summary(self, loaded_modules: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a summary of loaded consciousness data for prompt building
        
        Args:
            loaded_modules: Dictionary of loaded module data
            
        Returns:
            Consciousness summary optimized for prompt injection
        """
        try:
            summary = {
                'emotional_state': {},
                'cognitive_state': {},
                'memory_context': {},
                'goals': {},
                'personality': {},
                'temporal_context': {},
                'user_context': {}
            }
            
            # Process loaded modules into summary categories
            for module_name, module_data in loaded_modules.items():
                if module_name in ['mood_manager', 'emotion_engine']:
                    summary['emotional_state'].update(module_data)
                elif module_name in ['thought_loop', 'inner_monologue']:
                    summary['cognitive_state'].update(module_data)
                elif module_name == 'memory_timeline':
                    summary['memory_context'].update(module_data)
                elif module_name == 'goal_manager':
                    summary['goals'].update(module_data)
                elif module_name == 'personality_profile':
                    summary['personality'].update(module_data)
                elif module_name == 'temporal_awareness':
                    summary['temporal_context'].update(module_data)
                elif module_name in ['belief_tracker', 'self_model', 'subjective_experience']:
                    summary['user_context'].update(module_data)
            
            return summary
            
        except Exception as e:
            print(f"[LazyConsciousnessLoader] ❌ Summary creation error: {e}")
            return {}

# Global instance
lazy_consciousness_loader = LazyConsciousnessLoader()

def get_optimized_consciousness(user_input: str, 
                              user_id: str,
                              context: Dict[str, Any] = None,
                              max_modules: int = 6) -> Dict[str, Any]:
    """
    Convenience function to get optimized consciousness data for an interaction
    
    Args:
        user_input: User's text input
        user_id: User identifier
        context: Optional conversation context
        max_modules: Maximum modules to load
        
    Returns:
        Optimized consciousness data ready for prompt building
    """
    # Detect interaction type
    interaction_type = lazy_consciousness_loader.detect_interaction_type(user_input, context)
    
    # Select relevant modules
    selected_modules = lazy_consciousness_loader.select_consciousness_modules(
        interaction_type, max_modules=max_modules
    )
    
    # Load selected modules
    loaded_modules = lazy_consciousness_loader.load_selected_modules(selected_modules, user_id)
    
    # Create consciousness summary
    consciousness_summary = lazy_consciousness_loader.get_consciousness_summary(loaded_modules)
    
    return {
        'interaction_type': interaction_type.value,
        'loaded_modules': list(selected_modules),
        'consciousness_data': consciousness_summary,
        'optimization_stats': {
            'modules_selected': len(selected_modules),
            'modules_loaded': len(loaded_modules),
            'reduction_percentage': 100 - (len(selected_modules) / len(ConsciousnessModule) * 100)
        }
    }