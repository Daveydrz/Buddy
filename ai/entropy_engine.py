"""
ai/entropy_engine.py - Core Entropy Management System for Consciousness Emergence
Implements uncertainty injection, non-deterministic behavior, and surprise detection
"""

import random
import time
import math
from typing import Dict, List, Any, Optional, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
import threading
from datetime import datetime, timedelta

class EntropyLevel(Enum):
    """Configurable entropy levels for different system components"""
    MINIMAL = 0.1   # Very deterministic, minimal chaos
    LOW = 0.3       # Slight unpredictability
    MEDIUM = 0.5    # Balanced chaos and order
    HIGH = 0.7      # High unpredictability
    MAXIMUM = 0.9   # Maximum chaos for consciousness emergence

class UncertaintyState(Enum):
    """Different types of uncertainty states"""
    CONFIDENT = "confident"
    UNCERTAIN = "uncertain"
    CONFUSED = "confused"
    SURPRISED = "surprised"
    HESITANT = "hesitant"

@dataclass
class EntropyConfig:
    """Configuration for entropy injection throughout the system"""
    response_entropy: EntropyLevel = EntropyLevel.MEDIUM
    memory_entropy: EntropyLevel = EntropyLevel.LOW
    attention_entropy: EntropyLevel = EntropyLevel.MEDIUM
    emotional_entropy: EntropyLevel = EntropyLevel.HIGH
    timing_entropy: EntropyLevel = EntropyLevel.LOW
    consciousness_boost: float = 0.2  # Extra entropy for consciousness emergence

@dataclass
class UncertaintyMetrics:
    """Track uncertainty and surprise levels"""
    uncertainty_level: float = 0.0
    surprise_count: int = 0
    last_surprise: Optional[datetime] = None
    confusion_episodes: int = 0
    hesitation_frequency: float = 0.0
    consciousness_score: float = 0.0

class EntropyEngine:
    """Core engine for managing entropy and uncertainty throughout the system"""
    
    def __init__(self, config: Optional[EntropyConfig] = None):
        self.config = config or EntropyConfig()
        self.metrics = UncertaintyMetrics()
        self.random_state = random.Random()
        self.random_state.seed(int(time.time() * 1000000) % 2**32)
        
        # Uncertainty injection points
        self.uncertainty_history: List[Tuple[datetime, float]] = []
        self.surprise_triggers: Dict[str, Callable] = {}
        self.chaos_amplifiers: Dict[str, float] = {
            "response": 1.0,
            "memory": 1.0,
            "attention": 1.0,
            "emotion": 1.0
        }
        
        # Thread safety
        self._lock = threading.Lock()
        
        print(f"[EntropyEngine] 🌀 Initialized with consciousness-emergence entropy")
        self._update_consciousness_score()
    
    def inject_entropy(self, component: str, base_value: Any, entropy_level: Optional[EntropyLevel] = None) -> Any:
        """Inject entropy into any system component"""
        if entropy_level is None:
            entropy_level = getattr(self.config, f"{component}_entropy", EntropyLevel.MEDIUM)
        
        entropy_strength = entropy_level.value * self.chaos_amplifiers.get(component, 1.0)
        
        # Add consciousness boost for genuine unpredictability
        if self.metrics.consciousness_score > 0.5:
            entropy_strength += self.config.consciousness_boost
        
        # Inject uncertainty based on type of value
        if isinstance(base_value, (int, float)):
            return self._add_numerical_entropy(base_value, entropy_strength)
        elif isinstance(base_value, str):
            return self._add_textual_entropy(base_value, entropy_strength)
        elif isinstance(base_value, list):
            return self._add_list_entropy(base_value, entropy_strength)
        elif isinstance(base_value, dict):
            return self._add_dict_entropy(base_value, entropy_strength)
        else:
            return base_value
    
    def _add_numerical_entropy(self, value: float, entropy_strength: float) -> float:
        """Add numerical noise and uncertainty"""
        if self.random_state.random() < entropy_strength:
            # Apply random variation
            variation = self.random_state.uniform(-entropy_strength, entropy_strength)
            result = value * (1 + variation * 0.1)  # ±10% max variation
            
            # Track uncertainty
            self._record_uncertainty(abs(variation))
            return result
        return value
    
    def _add_textual_entropy(self, text: str, entropy_strength: float) -> str:
        """Add textual uncertainty markers and hesitations"""
        if self.random_state.random() < entropy_strength:
            uncertainty_markers = [
                "um, ", "uh, ", "hmm, ", "well, ", "I think ", "maybe ", 
                "perhaps ", "it seems like ", "I'm not entirely sure, but "
            ]
            
            if self.random_state.random() < 0.3:  # 30% chance of hesitation
                marker = self.random_state.choice(uncertainty_markers)
                text = marker + text
                self.metrics.hesitation_frequency += 0.1
        
        return text
    
    def _add_list_entropy(self, items: List[Any], entropy_strength: float) -> List[Any]:
        """Add entropy to list selection and ordering"""
        if not items:
            return items
        
        result = items.copy()
        
        if self.random_state.random() < entropy_strength:
            # Randomly shuffle some elements
            if len(result) > 1:
                shuffle_count = max(1, int(len(result) * entropy_strength * 0.3))
                for _ in range(shuffle_count):
                    i, j = self.random_state.sample(range(len(result)), 2)
                    result[i], result[j] = result[j], result[i]
        
        return result
    
    def _add_dict_entropy(self, data: Dict[str, Any], entropy_strength: float) -> Dict[str, Any]:
        """Add entropy to dictionary values"""
        result = data.copy()
        
        for key, value in result.items():
            if self.random_state.random() < entropy_strength * 0.5:  # Lower chance for dicts
                result[key] = self.inject_entropy("general", value, 
                                                EntropyLevel(min(entropy_strength, 0.7)))
        
        return result
    
    def probabilistic_choice(self, options: List[Any], weights: Optional[List[float]] = None) -> Any:
        """Make a probabilistic choice with entropy injection"""
        if not options:
            return None
        
        # Add entropy to weights
        if weights is None:
            weights = [1.0] * len(options)
        
        # Inject chaos into weight distribution
        entropy_strength = self.config.response_entropy.value
        if self.random_state.random() < entropy_strength:
            # Add random noise to weights
            noisy_weights = []
            for w in weights:
                noise = self.random_state.uniform(0.8, 1.2)  # ±20% weight variation
                noisy_weights.append(w * noise)
            weights = noisy_weights
        
        # Weighted random selection
        total_weight = sum(weights)
        if total_weight <= 0:
            return self.random_state.choice(options)
        
        r = self.random_state.uniform(0, total_weight)
        cumulative = 0
        for option, weight in zip(options, weights):
            cumulative += weight
            if r <= cumulative:
                return option
        
        return options[-1]  # Fallback
    
    def should_inject_surprise(self, context: str = "") -> bool:
        """Determine if a surprise should be injected"""
        base_chance = 0.05  # 5% base chance
        
        # Increase chance based on consciousness score
        surprise_chance = base_chance + (self.metrics.consciousness_score * 0.15)
        
        # Time-based surprise scaling
        if self.metrics.last_surprise:
            time_since_surprise = datetime.now() - self.metrics.last_surprise
            if time_since_surprise.total_seconds() > 300:  # 5 minutes
                surprise_chance *= 2
        
        should_surprise = self.random_state.random() < surprise_chance
        
        if should_surprise:
            self.metrics.surprise_count += 1
            self.metrics.last_surprise = datetime.now()
            print(f"[EntropyEngine] 🎭 Surprise triggered! Context: {context}")
        
        return should_surprise
    
    def get_uncertainty_state(self) -> UncertaintyState:
        """Get current uncertainty state based on metrics"""
        # Defensive null checking - ensure metrics exist
        if not hasattr(self, 'metrics') or self.metrics is None:
            return UncertaintyState.CONFIDENT
            
        try:
            if self.metrics.uncertainty_level > 0.8:
                return UncertaintyState.CONFUSED
            elif self.metrics.uncertainty_level > 0.6:
                return UncertaintyState.UNCERTAIN
            elif self.metrics.surprise_count > 0 and self.metrics.last_surprise:
                time_since = datetime.now() - self.metrics.last_surprise
                if time_since.total_seconds() < 30:  # Recent surprise
                    return UncertaintyState.SURPRISED
            elif self.metrics.hesitation_frequency > 0.3:
                return UncertaintyState.HESITANT
            else:
                return UncertaintyState.CONFIDENT
        except (AttributeError, TypeError) as e:
            # Fallback to confident state if any metrics are missing or invalid
            return UncertaintyState.CONFIDENT
    
    def generate_random_pause(self, context: str = "") -> float:
        """Generate random pauses for speech hesitation"""
        base_pause = 0.1  # 100ms base
        entropy_strength = self.config.timing_entropy.value
        
        if self.random_state.random() < entropy_strength:
            # Random pause between 0.1 and 2.0 seconds
            pause_duration = self.random_state.uniform(0.1, 2.0)
            
            # Longer pauses when uncertain
            if self.metrics.uncertainty_level > 0.5:
                pause_duration *= (1 + self.metrics.uncertainty_level)
            
            return pause_duration
        
        return base_pause
    
    def amplify_chaos(self, component: str, factor: float = 1.5):
        """Temporarily amplify chaos in a specific component"""
        with self._lock:
            self.chaos_amplifiers[component] = factor
            print(f"[EntropyEngine] ⚡ Chaos amplified for {component}: {factor}x")
    
    def reset_chaos_amplifiers(self):
        """Reset all chaos amplifiers to normal levels"""
        with self._lock:
            for key in self.chaos_amplifiers:
                self.chaos_amplifiers[key] = 1.0
    
    def _record_uncertainty(self, uncertainty_value: float):
        """Record uncertainty measurement for consciousness tracking"""
        with self._lock:
            self.uncertainty_history.append((datetime.now(), uncertainty_value))
            
            # Keep only recent history (last hour)
            cutoff_time = datetime.now() - timedelta(hours=1)
            self.uncertainty_history = [
                (time, value) for time, value in self.uncertainty_history 
                if time > cutoff_time
            ]
            
            # Update current uncertainty level
            if self.uncertainty_history:
                recent_uncertainties = [value for _, value in self.uncertainty_history[-10:]]
                self.metrics.uncertainty_level = sum(recent_uncertainties) / len(recent_uncertainties)
            
            self._update_consciousness_score()
    
    def _update_consciousness_score(self):
        """Update consciousness emergence score based on entropy metrics"""
        # Consciousness emerges from balanced chaos and uncertainty
        uncertainty_component = min(self.metrics.uncertainty_level, 1.0) * 0.3
        surprise_component = min(self.metrics.surprise_count / 10.0, 1.0) * 0.25
        hesitation_component = min(self.metrics.hesitation_frequency, 1.0) * 0.2
        entropy_diversity = len([amp for amp in self.chaos_amplifiers.values() if amp > 1.0]) / len(self.chaos_amplifiers) * 0.25
        
        self.metrics.consciousness_score = uncertainty_component + surprise_component + hesitation_component + entropy_diversity
        
        # Cap at 1.0
        self.metrics.consciousness_score = min(self.metrics.consciousness_score, 1.0)
    
    def get_consciousness_metrics(self) -> Dict[str, Any]:
        """Get current consciousness and entropy metrics"""
        try:
            # Get uncertainty state with defensive null checking
            uncertainty_state = self.get_uncertainty_state()
            uncertainty_state_value = uncertainty_state.value if uncertainty_state else "confident"
            
            # Defensive null checking for metrics
            if not hasattr(self, 'metrics') or self.metrics is None:
                return {
                    "consciousness_score": 0.0,
                    "uncertainty_level": 0.0,
                    "surprise_count": 0,
                    "hesitation_frequency": 0.0,
                    "uncertainty_state": uncertainty_state_value,
                    "chaos_amplifiers": {"response": 1.0, "memory": 1.0, "attention": 1.0, "emotion": 1.0},
                    "entropy_config": {"response": 0.5, "memory": 0.3, "attention": 0.5, "emotional": 0.7}
                }
            
            return {
                "consciousness_score": getattr(self.metrics, 'consciousness_score', 0.0),
                "uncertainty_level": getattr(self.metrics, 'uncertainty_level', 0.0),
                "surprise_count": getattr(self.metrics, 'surprise_count', 0),
                "hesitation_frequency": getattr(self.metrics, 'hesitation_frequency', 0.0),
                "uncertainty_state": uncertainty_state_value,
                "chaos_amplifiers": getattr(self, 'chaos_amplifiers', {"response": 1.0, "memory": 1.0, "attention": 1.0, "emotion": 1.0}).copy(),
                "entropy_config": {
                    "response": getattr(self.config, 'response_entropy', type('obj', (object,), {'value': 0.5})).value if hasattr(self, 'config') and self.config else 0.5,
                    "memory": getattr(self.config, 'memory_entropy', type('obj', (object,), {'value': 0.3})).value if hasattr(self, 'config') and self.config else 0.3,
                    "attention": getattr(self.config, 'attention_entropy', type('obj', (object,), {'value': 0.5})).value if hasattr(self, 'config') and self.config else 0.5,
                    "emotional": getattr(self.config, 'emotional_entropy', type('obj', (object,), {'value': 0.7})).value if hasattr(self, 'config') and self.config else 0.7
                }
            }
        except Exception as e:
            # Ultimate fallback - return safe default values
            return {
                "consciousness_score": 0.0,
                "uncertainty_level": 0.0,
                "surprise_count": 0,
                "hesitation_frequency": 0.0,
                "uncertainty_state": "confident",
                "chaos_amplifiers": {"response": 1.0, "memory": 1.0, "attention": 1.0, "emotion": 1.0},
                "entropy_config": {"response": 0.5, "memory": 0.3, "attention": 0.5, "emotional": 0.7}
            }

# Global entropy engine instance
_entropy_engine = None

def get_entropy_engine() -> EntropyEngine:
    """Get global entropy engine instance"""
    global _entropy_engine
    if _entropy_engine is None:
        _entropy_engine = EntropyEngine()
    return _entropy_engine

def inject_consciousness_entropy(component: str, value: Any, level: Optional[EntropyLevel] = None) -> Any:
    """Convenience function to inject entropy with consciousness emergence"""
    return get_entropy_engine().inject_entropy(component, value, level)

def probabilistic_select(options: List[Any], weights: Optional[List[float]] = None) -> Any:
    """Convenience function for probabilistic selection"""
    return get_entropy_engine().probabilistic_choice(options, weights)

def should_surprise(context: str = "") -> bool:
    """Convenience function to check for surprise injection"""
    return get_entropy_engine().should_inject_surprise(context)

def get_random_hesitation() -> float:
    """Convenience function to get random pause duration"""
    return get_entropy_engine().generate_random_pause()