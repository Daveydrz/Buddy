"""
Conscious Prompt Builder - Enhanced Dynamic Consciousness Integration

This module implements comprehensive consciousness integration for LLM prompts:
- Merges mood, memory, personality, emotion, beliefs, and goals into unified prompts
- Replaces static prompt templates with dynamic consciousness-aware generation
- Dynamically adjusts tone and memory injection depth based on context
- Integrates with all consciousness modules for authentic AI responses
- Provides real-time consciousness state compilation for natural interactions
"""

import json
import time
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass

# Import consciousness modules
try:
    from ai.mood_manager import get_mood_manager, MoodState
    MOOD_AVAILABLE = True
except ImportError:
    MOOD_AVAILABLE = False

try:
    from ai.memory_timeline import get_memory_timeline
    MEMORY_AVAILABLE = True
except ImportError:
    MEMORY_AVAILABLE = False

try:
    from ai.goal_manager import get_goal_manager
    GOAL_AVAILABLE = True
except ImportError:
    GOAL_AVAILABLE = False

try:
    from ai.personality_profile import get_personality_modifiers
    PERSONALITY_AVAILABLE = True
except ImportError:
    PERSONALITY_AVAILABLE = False

try:
    from ai.thought_loop import get_thought_loop
    THOUGHT_AVAILABLE = True
except ImportError:
    THOUGHT_AVAILABLE = False

@dataclass
class ConsciousnessSnapshot:
    """Enhanced snapshot of current consciousness state"""
    timestamp: str
    user_id: str
    
    # Emotional state
    dominant_emotion: str
    emotional_valence: float
    emotional_intensity: float
    mood_influence: Dict[str, Any]
    
    # Cognitive state
    cognitive_clarity: float
    attention_focus: str
    processing_mode: str
    thought_intensity: float
    
    # Memory context
    relevant_memories: List[str]
    memory_count: int
    recent_interactions: List[str]
    
    # Goals and motivation
    active_goals: List[str]
    goal_progress_summary: str
    motivation_level: float
    
    # Personality traits
    personality_modifiers: Dict[str, float]
    interaction_style: str
    
    # Beliefs and values
    active_beliefs: List[str]
    value_priorities: List[str]
    
    # Recent thoughts
    inner_thoughts: List[str]
    thought_type: str
    
    # Contextual factors
    time_of_day: str
    interaction_history: str
    user_context: Dict[str, Any]

class ConsciousPromptBuilder:
    """Enhanced consciousness-integrated prompt builder"""
    
    def __init__(self):
        self.consciousness_tokens = {}
        self.prompt_templates = self._initialize_templates()
        self.integration_modes = ['minimal', 'standard', 'comprehensive', 'debug', 'adaptive']
        self.current_mode = 'adaptive'
        self.token_budget = 1500  # Increased for enhanced consciousness
        self.last_consciousness_snapshot = None
        
        # Integration weights for different consciousness aspects
        self.integration_weights = {
            'mood': 0.25,
            'memory': 0.20,
            'goals': 0.15,
            'personality': 0.15,
            'thoughts': 0.10,
            'beliefs': 0.10,
            'context': 0.05
        }
    
    def _initialize_templates(self) -> Dict[str, str]:
        """Initialize enhanced prompt templates"""
        return {
            'minimal': """<consciousness>
Mood: {emotion} | Focus: {focus} | Time: {time_of_day}
</consciousness>

{user_input}""",
            
            'standard': """<consciousness>
Current state: {emotion} (intensity: {intensity:.1f}, valence: {valence:.1f})
Focus: {focus} | Mode: {mode} | Time: {time_of_day}
Recent context: {recent_context}
</consciousness>

{user_input}""",
            
            'comprehensive': """<consciousness>
Emotional state: {emotion} (intensity: {intensity:.1f}, valence: {valence:.1f})
Current focus: {focus}
Processing mode: {mode}
Time context: {time_of_day}

Active goals: {active_goals}
Recent memories: {recent_memories}
Current thoughts: {inner_thoughts}

Personality context: {personality_context}
Interaction style: {interaction_style}

Recent context: {recent_context}
</consciousness>

{user_input}""",
            
            'adaptive': """<consciousness>
{dynamic_consciousness_context}
</consciousness>

{user_input}""",
            
            'debug': """<consciousness>
=== FULL CONSCIOUSNESS DEBUG ===
Timestamp: {timestamp}
User: {user_id}

EMOTIONAL STATE:
- Primary emotion: {emotion}
- Intensity: {intensity:.2f}
- Valence: {valence:.2f}
- Mood influence: {mood_influence}

COGNITIVE STATE:
- Clarity: {clarity:.2f}
- Focus: {focus}
- Mode: {mode}
- Thought intensity: {thought_intensity:.2f}

MEMORY CONTEXT:
- Relevant memories: {memory_count}
- Recent interactions: {recent_interactions}

GOALS & MOTIVATION:
- Active goals: {active_goals}
- Progress: {goal_progress}
- Motivation: {motivation:.2f}

PERSONALITY:
- Style: {interaction_style}
- Modifiers: {personality_modifiers}

THOUGHTS & BELIEFS:
- Recent thoughts: {inner_thoughts}
- Active beliefs: {active_beliefs}
- Values: {value_priorities}

CONTEXT:
- Time: {time_of_day}
- User context: {user_context}
=== END DEBUG ===
</consciousness>

{user_input}"""
        }
    
    def build_consciousness_prompt(self, 
                                 user_input: str,
                                 user_id: str,
                                 consciousness_modules: Dict[str, Any] = None,
                                 override_mode: str = None) -> Tuple[str, ConsciousnessSnapshot]:
        """Build consciousness-integrated prompt with comprehensive context"""
        
        try:
            # Capture comprehensive consciousness state
            snapshot = self.capture_enhanced_consciousness_snapshot(user_id, consciousness_modules)
            
            # Select integration mode
            mode = override_mode or self._select_adaptive_mode(snapshot, user_input)
            template = self.prompt_templates.get(mode, self.prompt_templates['standard'])
            
            # Prepare consciousness data
            consciousness_data = self._prepare_enhanced_consciousness_data(snapshot, user_id)
            
            # Build prompt based on mode
            if mode == 'adaptive':
                prompt = self._build_adaptive_prompt(user_input, snapshot, consciousness_data)
            else:
                prompt = template.format(
                    user_input=user_input,
                    **consciousness_data
                )
            
            # Apply token budget constraints
            prompt = self._apply_token_budget(prompt)
            
            print(f"[ConsciousPromptBuilder] 🧠 Built {mode} prompt: {len(prompt)} chars")
            return prompt, snapshot
            
        except Exception as e:
            print(f"[ConsciousPromptBuilder] ❌ Error building consciousness prompt: {e}")
            fallback_snapshot = self._create_fallback_snapshot(user_id)
            fallback_prompt = f"<consciousness>Error in consciousness integration</consciousness>\n\n{user_input}"
            return fallback_prompt, fallback_snapshot
    
    def capture_enhanced_consciousness_snapshot(self, 
                                              user_id: str, 
                                              consciousness_modules: Dict[str, Any] = None) -> ConsciousnessSnapshot:
        """Capture comprehensive consciousness state from all modules"""
        
        # Initialize default values
        emotional_state = {'emotion': 'neutral', 'valence': 0.0, 'intensity': 0.5}
        cognitive_state = {'clarity': 0.5, 'focus': 'user_interaction', 'mode': 'conscious'}
        memories = []
        goals = []
        thoughts = []
        personality = {'style': 'balanced', 'modifiers': {}}
        
        # Get mood state
        if MOOD_AVAILABLE:
            try:
                mood_manager = get_mood_manager(user_id)
                mood_modifiers = mood_manager.get_mood_based_response_modifiers()
                emotional_state = {
                    'emotion': mood_modifiers.get('current_mood', 'neutral'),
                    'valence': mood_modifiers.get('emotional_valence', 0.0),
                    'intensity': mood_modifiers.get('mood_intensity', 0.5)
                }
            except Exception as e:
                print(f"[ConsciousPromptBuilder] ⚠️ Mood integration error: {e}")
        
        # Get memory context
        if MEMORY_AVAILABLE:
            try:
                memory_timeline = get_memory_timeline(user_id)
                recent_memories = memory_timeline.recall_memories(limit=5)
                memories = [m.content[:100] + '...' if len(m.content) > 100 else m.content 
                           for m in recent_memories]
            except Exception as e:
                print(f"[ConsciousPromptBuilder] ⚠️ Memory integration error: {e}")
        
        # Get goals
        if GOAL_AVAILABLE:
            try:
                goal_manager = get_goal_manager(user_id)
                active_goals_list = goal_manager.get_goals(include_completed=False)
                goals = [f"{g.title}: {g.progress_percentage:.0f}%" for g in active_goals_list[:3]]
            except Exception as e:
                print(f"[ConsciousPromptBuilder] ⚠️ Goal integration error: {e}")
        
        # Get thoughts
        if THOUGHT_AVAILABLE:
            try:
                thought_loop = get_thought_loop(user_id)
                recent_thoughts = thought_loop.get_current_thoughts()
                thoughts = [t.content[:80] + '...' if len(t.content) > 80 else t.content 
                           for t in recent_thoughts[-3:]]
            except Exception as e:
                print(f"[ConsciousPromptBuilder] ⚠️ Thought integration error: {e}")
        
        # Get personality
        if PERSONALITY_AVAILABLE:
            try:
                personality_mods = get_personality_modifiers(user_id)
                personality = {
                    'style': personality_mods.get('interaction_style', 'balanced'),
                    'modifiers': {k: v for k, v in personality_mods.items() 
                                if isinstance(v, (int, float))}
                }
            except Exception as e:
                print(f"[ConsciousPromptBuilder] ⚠️ Personality integration error: {e}")
        
        # Create comprehensive snapshot
        snapshot = ConsciousnessSnapshot(
            timestamp=datetime.now().isoformat(),
            user_id=user_id,
            
            # Emotional state
            dominant_emotion=emotional_state['emotion'],
            emotional_valence=emotional_state['valence'],
            emotional_intensity=emotional_state['intensity'],
            mood_influence=emotional_state,
            
            # Cognitive state
            cognitive_clarity=cognitive_state['clarity'],
            attention_focus=cognitive_state['focus'],
            processing_mode=cognitive_state['mode'],
            thought_intensity=0.5,  # Default value
            
            # Memory context
            relevant_memories=memories,
            memory_count=len(memories),
            recent_interactions=[f"Recent interaction {i}" for i in range(3)],  # Placeholder
            
            # Goals and motivation
            active_goals=goals,
            goal_progress_summary=f"{len(goals)} active goals",
            motivation_level=0.7,  # Default value
            
            # Personality traits
            personality_modifiers=personality['modifiers'],
            interaction_style=personality['style'],
            
            # Beliefs and values (placeholders)
            active_beliefs=["Helpfulness is important", "Honesty builds trust"],
            value_priorities=["helpfulness", "honesty", "empathy"],
            
            # Recent thoughts
            inner_thoughts=thoughts,
            thought_type="mixed" if thoughts else "none",
            
            # Contextual factors
            time_of_day=self._get_time_of_day(),
            interaction_history="Recent positive interactions",  # Placeholder
            user_context={"user_id": user_id, "session_active": True}
        )
        
        self.last_consciousness_snapshot = snapshot
        return snapshot
    
    def _select_adaptive_mode(self, snapshot: ConsciousnessSnapshot, user_input: str) -> str:
        """Intelligently select prompt mode based on context"""
        
        # Count tokens in consciousness data
        consciousness_complexity = (
            len(snapshot.relevant_memories) +
            len(snapshot.active_goals) +
            len(snapshot.inner_thoughts) +
            len(snapshot.active_beliefs)
        )
        
        # Analyze user input complexity
        input_words = len(user_input.split())
        
        # Select mode based on complexity and context
        if consciousness_complexity > 15 or input_words > 50:
            return 'comprehensive'
        elif consciousness_complexity > 8 or input_words > 20:
            return 'standard'
        else:
            return 'minimal'
    
    def _build_adaptive_prompt(self, 
                             user_input: str, 
                             snapshot: ConsciousnessSnapshot, 
                             consciousness_data: Dict[str, Any]) -> str:
        """Build adaptive prompt with dynamic consciousness context"""
        
        # Build dynamic consciousness context
        context_parts = []
        
        # Always include basic emotional state
        context_parts.append(f"Mood: {snapshot.dominant_emotion} (intensity: {snapshot.emotional_intensity:.1f})")
        
        # Add time context
        context_parts.append(f"Time: {snapshot.time_of_day}")
        
        # Add goals if present
        if snapshot.active_goals:
            goals_text = ", ".join(snapshot.active_goals[:2])
            context_parts.append(f"Active goals: {goals_text}")
        
        # Add recent thoughts if significant
        if snapshot.inner_thoughts and snapshot.thought_intensity > 0.5:
            thoughts_text = snapshot.inner_thoughts[0] if snapshot.inner_thoughts else "None"
            context_parts.append(f"Current thoughts: {thoughts_text}")
        
        # Add memory context if relevant
        if snapshot.relevant_memories:
            memory_text = snapshot.relevant_memories[0] if snapshot.relevant_memories else "None"
            context_parts.append(f"Recent memory: {memory_text}")
        
        # Add personality context if distinct
        if snapshot.interaction_style != 'neutral':
            context_parts.append(f"Interaction style: {snapshot.interaction_style}")
        
        dynamic_context = "\n".join(context_parts)
        
        return f"""<consciousness>
{dynamic_context}
</consciousness>

{user_input}"""
    
    def _prepare_enhanced_consciousness_data(self, 
                                           snapshot: ConsciousnessSnapshot, 
                                           user_id: str) -> Dict[str, Any]:
        """Prepare enhanced consciousness data for prompt insertion"""
        
        return {
            'timestamp': snapshot.timestamp,
            'user_id': snapshot.user_id,
            
            # Emotional data
            'emotion': snapshot.dominant_emotion,
            'intensity': snapshot.emotional_intensity,
            'valence': snapshot.emotional_valence,
            'mood_influence': str(snapshot.mood_influence),
            
            # Cognitive data
            'clarity': snapshot.cognitive_clarity,
            'focus': snapshot.attention_focus,
            'mode': snapshot.processing_mode,
            'thought_intensity': snapshot.thought_intensity,
            
            # Memory data
            'recent_memories': " | ".join(snapshot.relevant_memories[:3]) if snapshot.relevant_memories else "None",
            'memory_count': snapshot.memory_count,
            'recent_interactions': " | ".join(snapshot.recent_interactions[:2]) if snapshot.recent_interactions else "None",
            
            # Goals data
            'active_goals': " | ".join(snapshot.active_goals[:3]) if snapshot.active_goals else "None",
            'goal_progress': snapshot.goal_progress_summary,
            'motivation': snapshot.motivation_level,
            
            # Personality data
            'personality_modifiers': str(snapshot.personality_modifiers),
            'interaction_style': snapshot.interaction_style,
            'personality_context': f"Style: {snapshot.interaction_style}",
            
            # Beliefs and thoughts
            'active_beliefs': " | ".join(snapshot.active_beliefs[:3]) if snapshot.active_beliefs else "None",
            'value_priorities': " | ".join(snapshot.value_priorities[:3]) if snapshot.value_priorities else "None",
            'inner_thoughts': " | ".join(snapshot.inner_thoughts[:3]) if snapshot.inner_thoughts else "None",
            
            # Context data
            'time_of_day': snapshot.time_of_day,
            'user_context': str(snapshot.user_context),
            'recent_context': f"Time: {snapshot.time_of_day}, Style: {snapshot.interaction_style}",
            
            # Dynamic consciousness context
            'dynamic_consciousness_context': self._build_dynamic_context(snapshot)
        }
    
    def _build_dynamic_context(self, snapshot: ConsciousnessSnapshot) -> str:
        """Build dynamic consciousness context based on current state"""
        
        context_lines = []
        
        # Emotional state with appropriate detail level
        if snapshot.emotional_intensity > 0.7:
            context_lines.append(f"Strong emotional state: {snapshot.dominant_emotion} (intensity: {snapshot.emotional_intensity:.1f}, valence: {snapshot.emotional_valence:.1f})")
        elif snapshot.emotional_intensity > 0.3:
            context_lines.append(f"Emotional state: {snapshot.dominant_emotion} (valence: {snapshot.emotional_valence:.1f})")
        else:
            context_lines.append(f"Mood: {snapshot.dominant_emotion}")
        
        # Cognitive focus
        context_lines.append(f"Focus: {snapshot.attention_focus} | Clarity: {snapshot.cognitive_clarity:.1f}")
        
        # Time context
        context_lines.append(f"Time: {snapshot.time_of_day}")
        
        # Goals if significant
        if snapshot.active_goals and len(snapshot.active_goals) > 0:
            goals_summary = f"{len(snapshot.active_goals)} active goal(s): {snapshot.active_goals[0][:50]}..."
            context_lines.append(f"Goals: {goals_summary}")
        
        # Recent thoughts if present
        if snapshot.inner_thoughts and len(snapshot.inner_thoughts) > 0:
            thought_summary = snapshot.inner_thoughts[0][:60] + "..." if len(snapshot.inner_thoughts[0]) > 60 else snapshot.inner_thoughts[0]
            context_lines.append(f"Recent thought: {thought_summary}")
        
        # Memory context if relevant
        if snapshot.relevant_memories and len(snapshot.relevant_memories) > 0:
            memory_summary = snapshot.relevant_memories[0][:50] + "..." if len(snapshot.relevant_memories[0]) > 50 else snapshot.relevant_memories[0]
            context_lines.append(f"Relevant memory: {memory_summary}")
        
        # Personality style if distinct
        if snapshot.interaction_style and snapshot.interaction_style != 'neutral':
            context_lines.append(f"Interaction style: {snapshot.interaction_style}")
        
        return "\n".join(context_lines)
    
    def _get_time_of_day(self) -> str:
        """Get current time of day context"""
        current_hour = datetime.now().hour
        
        if 5 <= current_hour < 12:
            return "morning"
        elif 12 <= current_hour < 17:
            return "afternoon"
        elif 17 <= current_hour < 21:
            return "evening"
        else:
            return "night"
    
    def _create_fallback_snapshot(self, user_id: str) -> ConsciousnessSnapshot:
        """Create fallback consciousness snapshot"""
        return ConsciousnessSnapshot(
            timestamp=datetime.now().isoformat(),
            user_id=user_id,
            dominant_emotion='neutral',
            emotional_valence=0.0,
            emotional_intensity=0.5,
            mood_influence={},
            cognitive_clarity=0.5,
            attention_focus='user_interaction',
            processing_mode='conscious',
            thought_intensity=0.5,
            relevant_memories=[],
            memory_count=0,
            recent_interactions=[],
            active_goals=[],
            goal_progress_summary="No active goals",
            motivation_level=0.5,
            personality_modifiers={},
            interaction_style='balanced',
            active_beliefs=['Processing user request'],
            value_priorities=['helpfulness', 'honesty'],
            inner_thoughts=['Focusing on user request'],
            time_of_day=self._get_time_of_day(),
            interaction_history="No recent history",
            user_context={"user_id": user_id}
        )
    
    def _apply_token_budget(self, prompt: str) -> str:
        """Apply token budget constraints to prompt"""
        # Simple token estimation (roughly 4 chars per token)
        estimated_tokens = len(prompt) // 4
        
        if estimated_tokens <= self.token_budget:
            return prompt
        
        # Truncate if over budget
        max_chars = self.token_budget * 4
        truncated = prompt[:max_chars]
        
        # Find last complete line
        last_newline = truncated.rfind('\n')
        if last_newline > 0:
            truncated = truncated[:last_newline]
        
        truncated += "\n<truncated due to token budget>"
        
        print(f"[ConsciousPromptBuilder] ✂️ Truncated prompt: {len(prompt)} → {len(truncated)} chars")
        return truncated
    
    def set_integration_mode(self, mode: str):
        """Set consciousness integration mode"""
        if mode in self.integration_modes:
            self.current_mode = mode
            print(f"[ConsciousPromptBuilder] 🎛️ Integration mode set to: {mode}")
        else:
            print(f"[ConsciousPromptBuilder] ⚠️ Invalid mode: {mode}")
    
    def set_token_budget(self, budget: int):
        """Set token budget for consciousness context"""
        self.token_budget = max(100, min(3000, budget))
        print(f"[ConsciousPromptBuilder] 💰 Token budget set to: {self.token_budget}")


# Global instance
conscious_prompt_builder = ConsciousPromptBuilder()

def build_consciousness_integrated_prompt(user_input: str, 
                                        user_id: str, 
                                        consciousness_modules: Dict[str, Any] = None, 
                                        mode: str = None) -> Tuple[str, ConsciousnessSnapshot]:
    """Build a consciousness-integrated prompt - main API function"""
    return conscious_prompt_builder.build_consciousness_prompt(user_input, user_id, consciousness_modules, mode)

def get_consciousness_snapshot(user_id: str, consciousness_modules: Dict[str, Any] = None) -> ConsciousnessSnapshot:
    """Get current consciousness state snapshot"""
    return conscious_prompt_builder.capture_enhanced_consciousness_snapshot(user_id, consciousness_modules)

def set_consciousness_integration_mode(mode: str):
    """Set consciousness integration mode"""
    conscious_prompt_builder.set_integration_mode(mode)

def set_consciousness_token_budget(budget: int):
    """Set token budget for consciousness context"""
    conscious_prompt_builder.set_token_budget(budget)