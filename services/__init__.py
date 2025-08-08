"""
Services module for Buddy Voice Assistant
Provides high-level service facades and coordination
"""

from .consciousness import (
    consciousness,
    idle_tick,
    pre_reply,
    post_user_turn,
    get_consciousness_health
)

__all__ = [
    'consciousness',
    'idle_tick',
    'pre_reply', 
    'post_user_turn',
    'get_consciousness_health'
]