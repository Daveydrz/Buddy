"""
Persistent Cognitive Modules for Buddy's Memory and Self-Awareness

This package implements a comprehensive cognitive architecture for Buddy that includes:
- Persistent memory across sessions
- Self-awareness and adaptive behavior
- Goal management and tracking
- Experience-based learning
- Continuous self-reflection

All modules integrate with the existing consciousness architecture via cognitive_prompt_injection.
"""

from .self_model import PersistentSelfModel
from .goal_bank import GoalBank
from .experience_bank import ExperienceBank
from .memory_prioritization import MemoryPrioritizer
from .thought_loop import ThoughtLoop

__all__ = [
    'PersistentSelfModel',
    'GoalBank', 
    'ExperienceBank',
    'MemoryPrioritizer',
    'ThoughtLoop'
]