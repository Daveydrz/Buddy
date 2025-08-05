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
    from ai.personality_state import get_personality_state
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
Active beliefs: {beliefs}
Primary goals: {goals}
</consciousness>

{user_input}""",
            
            'comprehensive': """<consciousness>
Emotional state: {emotion} (valence: {valence:.2f}, clarity: {clarity:.2f})
Current focus: {focus}
Processing mode: {mode}
Active beliefs: {beliefs}
Primary goals: {goals}
Inner thoughts: {thoughts}
Qualia experiences: {qualia}
Value priorities: {values}
</consciousness>

{context}

{user_input}""",
            
            'debug': """<consciousness_debug>
Timestamp: {timestamp}
Emotional state: {emotion} (valence: {valence:.2f}, clarity: {clarity:.2f})
Current focus: {focus}
Processing mode: {mode}
Active beliefs: {beliefs}
Primary goals: {goals}
Inner thoughts: {thoughts}
Qualia experiences: {qualia}
Value priorities: {values}
Memory context: {memory}
Personality state: {personality}
</consciousness_debug>

{context}

{user_input}"""
        }
    
    
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