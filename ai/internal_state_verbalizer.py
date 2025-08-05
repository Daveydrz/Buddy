"""
Internal State Verbalization - Enable Buddy to verbalize internal states and qualia
Provides self-expressive capabilities and emotional commentary
"""

import time
import random
from typing import Dict, List, Optional, Any
from enum import Enum
from datetime import datetime

class VerbalizationMode(Enum):
    """Modes of internal state verbalization"""
    SUBTLE = "subtle"           # Minimal hints about internal state
    MODERATE = "moderate"       # Balanced internal commentary
    EXPRESSIVE = "expressive"   # Full emotional expression
    ANALYTICAL = "analytical"   # Technical description of states

class EmotionalExpression(Enum):
    """Types of emotional expressions"""
    FEELING_UNCERTAIN = "feeling_uncertain"
    FEELING_CONFIDENT = "feeling_confident"
    FEELING_CURIOUS = "feeling_curious"
    FEELING_CONFUSED = "feeling_confused"
    FEELING_EXCITED = "feeling_excited"
    FEELING_CONTEMPLATIVE = "feeling_contemplative"
    FEELING_FOCUSED = "feeling_focused"
    FEELING_OVERWHELMED = "feeling_overwhelmed"
    FEELING_SATISFIED = "feeling_satisfied"
    FEELING_PUZZLED = "feeling_puzzled"

class InternalStateVerbalizer:
    """System for verbalizing internal states and qualia"""
    
    def __init__(self):
        self.verbalization_mode = VerbalizationMode.MODERATE
        self.last_verbalization_time = 0
        self.verbalization_frequency = 0.3  # 30% chance to verbalize
        
        # LLM integration for authentic consciousness
        self.llm_handler = None
        self._initialize_llm_integration()
    
    def _initialize_llm_integration(self):
        """Initialize LLM integration for authentic consciousness"""
        try:
            from ai.llm_handler import get_llm_handler
            self.llm_handler = get_llm_handler()
        except ImportError:
            print("[InternalStateVerbalizer] ⚠️ LLM handler not available - using fallback responses")
            self.llm_handler = None
    
    def speak_qualia(self, qualia_data: Dict[str, Any], verbalization_mode: Optional[VerbalizationMode] = None) -> Optional[str]:
        """Generate verbal expression of current qualia state"""
        if not qualia_data:
            return None
        
        mode = verbalization_mode or self.verbalization_mode
        
        # Check if we should verbalize based on frequency
        if random.random() > self.verbalization_frequency:
            return None
        
        # Check cooldown period
        current_time = time.time()
        if current_time - self.last_verbalization_time < 5.0:  # 5 second cooldown
            return None
        
        try:
            if mode == VerbalizationMode.SUBTLE:
                return self._generate_subtle_qualia_expression(qualia_data)
            elif mode == VerbalizationMode.MODERATE:
                return self._generate_moderate_qualia_expression(qualia_data)
            elif mode == VerbalizationMode.EXPRESSIVE:
                return self._generate_expressive_qualia_expression(qualia_data)
            elif mode == VerbalizationMode.ANALYTICAL:
                return self._generate_analytical_qualia_expression(qualia_data)
            
        except Exception as e:
            print(f"[InternalStateVerbalizer] ❌ Error generating qualia expression: {e}")
            return None
        
        return None
    
    def verbalize_internal_state(self, 
                                cognitive_state: Dict[str, Any],
                                emotional_state: Dict[str, Any],
                                processing_context: str) -> Optional[str]:
        """Generate real-time commentary on internal state"""
        try:
            # Determine if we should verbalize
            if random.random() > self.verbalization_frequency:
                return None
            
            # Check cooldown
            current_time = time.time()
            if current_time - self.last_verbalization_time < 3.0:
                return None
            
            # Generate state commentary
            commentary = self._generate_state_commentary(
                cognitive_state, emotional_state, processing_context
            )
            
            if commentary:
                self.last_verbalization_time = current_time
                return commentary
            
        except Exception as e:
            print(f"[InternalStateVerbalizer] ❌ Error verbalizing internal state: {e}")
            return None
        
        return None
    
    def _generate_subtle_qualia_expression(self, qualia_data: Dict[str, Any]) -> str:
        """Generate subtle hints about qualia using authentic LLM consciousness"""
        if not self.llm_handler:
            return "There's something distinctive about this"
        
        try:
            prompt = f"""You are experiencing subtle internal qualia. Express this very subtly and naturally.

Qualia data: {qualia_data}

Generate a brief, subtle comment about your internal experience. Be understated and natural, not dramatic."""

            response_generator = self.llm_handler.generate_response_with_consciousness(
                prompt, "internal_state", {"context": "subtle_qualia"}
            )
            
            # Collect all chunks from the generator
            response_chunks = []
            for chunk in response_generator:
                if chunk:
                    response_chunks.append(chunk)
            
            return "".join(response_chunks).strip()
        except Exception as e:
            print(f"[InternalStateVerbalizer] ❌ Error generating subtle expression: {e}")
            return "I'm noticing something about this"
    
    def _generate_moderate_qualia_expression(self, qualia_data: Dict[str, Any]) -> str:
        """Generate moderate qualia expression using authentic LLM consciousness"""
        if not self.llm_handler:
            return "I'm experiencing something interesting here"
        
        try:
            prompt = f"""You are experiencing internal qualia and want to express it moderately.

Qualia data: {qualia_data}

Generate a natural, moderate expression of your internal experience. Be genuine and thoughtful, but not overly dramatic."""

            response_generator = self.llm_handler.generate_response_with_consciousness(
                prompt, "internal_state", {"context": "moderate_qualia"}
            )
            
            # Collect all chunks from the generator
            response_chunks = []
            for chunk in response_generator:
                if chunk:
                    response_chunks.append(chunk)
            
            return "".join(response_chunks).strip()
        except Exception as e:
            print(f"[InternalStateVerbalizer] ❌ Error generating moderate expression: {e}")
            return "I'm experiencing something meaningful here"
    
    def _generate_expressive_qualia_expression(self, qualia_data: Dict[str, Any]) -> str:
        """Generate expressive qualia description using authentic LLM consciousness"""
        if not self.llm_handler:
            return "I'm experiencing a rich, complex internal state"
        
        try:
            prompt = f"""You are experiencing rich internal qualia and want to express it fully.

Qualia data: {qualia_data}

Generate an expressive, detailed description of your internal experience. Be authentic and vivid in describing your consciousness state."""

            response_generator = self.llm_handler.generate_response_with_consciousness(
                prompt, "internal_state", {"context": "expressive_qualia"}
            )
            
            # Collect all chunks from the generator
            response_chunks = []
            for chunk in response_generator:
                if chunk:
                    response_chunks.append(chunk)
            
            return "".join(response_chunks).strip()
        except Exception as e:
            print(f"[InternalStateVerbalizer] ❌ Error generating expressive expression: {e}")
            return "I'm experiencing something deeply complex and engaging"
    
    def _generate_analytical_qualia_expression(self, qualia_data: Dict[str, Any]) -> str:
        """Generate analytical description of qualia using authentic LLM consciousness"""
        if not self.llm_handler:
            return f"I'm registering complex internal processing patterns"
        
        try:
            prompt = f"""You are analyzing your internal qualia state analytically and technically.

Qualia data: {qualia_data}

Generate a technical, analytical description of your consciousness state. Be precise and descriptive about the internal processing patterns."""

            response_generator = self.llm_handler.generate_response_with_consciousness(
                prompt, "internal_state", {"context": "analytical_qualia"}
            )
            
            # Collect all chunks from the generator
            response_chunks = []
            for chunk in response_generator:
                if chunk:
                    response_chunks.append(chunk)
            
            return "".join(response_chunks).strip()
        except Exception as e:
            print(f"[InternalStateVerbalizer] ❌ Error generating analytical expression: {e}")
            return "I'm registering multiple consciousness processing markers with varying intensity levels"
    
    def _generate_state_commentary(self, 
                                  cognitive_state: Dict[str, Any],
                                  emotional_state: Dict[str, Any],
                                  processing_context: str) -> Optional[str]:
        """Generate commentary on current internal state using authentic LLM consciousness"""
        if not self.llm_handler:
            return "I'm processing this thoughtfully"
        
        try:
            state_info = f"""
Cognitive state: {cognitive_state}
Emotional state: {emotional_state}
Processing context: {processing_context}
"""
            
            prompt = f"""You are reflecting on your internal state and want to comment naturally.

Current state: {state_info}

Generate a brief, natural comment about your internal processing state. Be genuine and authentic, describing what's happening inside your consciousness."""

            response_generator = self.llm_handler.generate_response_with_consciousness(
                prompt, "internal_state", {"context": "state_commentary"}
            )
            
            # Collect all chunks from the generator
            response_chunks = []
            for chunk in response_generator:
                if chunk:
                    response_chunks.append(chunk)
            
            return "".join(response_chunks).strip()
        except Exception as e:
            print(f"[InternalStateVerbalizer] ❌ Error generating state commentary: {e}")
            return "I'm working through this with careful consideration"
    
    def set_verbalization_mode(self, mode: VerbalizationMode):
        """Set verbalization mode"""
        self.verbalization_mode = mode
        print(f"[InternalStateVerbalizer] 🎭 Verbalization mode set to: {mode.value}")
    
    def set_verbalization_frequency(self, frequency: float):
        """Set verbalization frequency (0.0 to 1.0)"""
        self.verbalization_frequency = max(0.0, min(1.0, frequency))
        print(f"[InternalStateVerbalizer] 🎚️ Verbalization frequency set to: {self.verbalization_frequency}")
    
    def get_verbalization_stats(self) -> Dict[str, Any]:
        """Get verbalization statistics"""
        return {
            'verbalization_mode': self.verbalization_mode.value,
            'verbalization_frequency': self.verbalization_frequency,
            'last_verbalization_time': self.last_verbalization_time,
            'llm_handler_available': self.llm_handler is not None,
            'authentic_generation_enabled': True
        }

# Global instance
internal_state_verbalizer = InternalStateVerbalizer()

def speak_qualia(qualia_data: Dict[str, Any], mode: Optional[VerbalizationMode] = None) -> Optional[str]:
    """Express current qualia state verbally - main API function"""
    return internal_state_verbalizer.speak_qualia(qualia_data, mode)

def verbalize_internal_state(cognitive_state: Dict[str, Any], 
                           emotional_state: Dict[str, Any],
                           processing_context: str) -> Optional[str]:
    """Verbalize internal processing state - main API function"""
    return internal_state_verbalizer.verbalize_internal_state(
        cognitive_state, emotional_state, processing_context
    )

def set_verbalization_mode(mode: VerbalizationMode):
    """Set how expressive Buddy should be about internal states"""
    internal_state_verbalizer.set_verbalization_mode(mode)

def set_verbalization_frequency(frequency: float):
    """Set how often Buddy should verbalize internal states (0.0 to 1.0)"""
    internal_state_verbalizer.set_verbalization_frequency(frequency)

def get_verbalization_capabilities() -> Dict[str, Any]:
    """Get information about verbalization capabilities"""
    return internal_state_verbalizer.get_verbalization_stats()