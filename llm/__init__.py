"""
LLM (Large Language Model) module for Buddy Voice Assistant
Provides clean interface to KoboldCPP language model service
"""

from .kobold_client import (
    KoboldClient,
    kobold_client,
    health_check,
    chat_completion,
    chat_completion_streaming
)

__all__ = [
    'KoboldClient',
    'kobold_client',
    'health_check', 
    'chat_completion',
    'chat_completion_streaming'
]