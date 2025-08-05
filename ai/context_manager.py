# ai/context_manager.py - Natural context checking with session management
from .human_memory import HumanLikeMemory
from typing import Optional

class NaturalContextManager:
    """🎭 Manages natural context and memory integration"""
    
    def __init__(self, username: str):
        self.username = username
        self.memory = HumanLikeMemory(username)
        self.has_checked_context_this_session = False
        
    def process_user_input(self, text: str) -> tuple[Optional[str], str]:
        """
        Process user input and return (context_response, processed_text)
        
        Returns:
            context_response: Natural memory response if appropriate
            processed_text: Original text (for normal processing)
        """
        
        # Extract and store new memories from user input
        self.memory.extract_and_store_human_memories(text)
        
        # Check if we should bring up any memories (only once per session)
        context_response = None
        if not self.has_checked_context_this_session:
            context_response = self.memory.check_for_natural_context_response()
            self.has_checked_context_this_session = True
        
        return context_response, text
    
    def reset_session(self):
        """Reset session state (call when conversation starts)"""
        self.has_checked_context_this_session = False
        self.memory.reset_session_context()
        print(f"[NaturalContext] 🔄 Session reset for {self.username}")
    
    def force_context_check(self) -> Optional[str]:
        """Force a context check (for testing)"""
        return self.memory.check_for_natural_context_response()