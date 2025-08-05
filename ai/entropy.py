"""
Entropy System - Uncertainty and Randomness Injection

This module implements entropy and uncertainty throughout the consciousness system:
- Injects controlled randomness and uncertainty into all decision processes
- Prevents deterministic, robotic behavior patterns
- Creates natural variation in responses and thought patterns
- Balances predictability with spontaneity
- Simulates the uncertainty inherent in conscious experience
"""

import threading
import time
import random
import logging
import math
import json
from typing import Dict, List, Any, Optional, Callable, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path

class EntropyType(Enum):
    """Types of entropy injection"""
    RESPONSE_VARIATION = "response_variation"     # Variation in response generation
    THOUGHT_PATTERN = "thought_pattern"          # Variation in thought patterns
    EMOTIONAL_FLUX = "emotional_flux"            # Emotional state variations
    ATTENTION_DRIFT = "attention_drift"          # Attention and focus variations
    MEMORY_UNCERTAINTY = "memory_uncertainty"    # Memory recall variations
    DECISION_NOISE = "decision_noise"            # Decision-making uncertainty
    TIMING_VARIATION = "timing_variation"        # Timing and rhythm variations
    PERSPECTIVE_SHIFT = "perspective_shift"      # Perspective and viewpoint shifts
    CREATIVITY_SPARK = "creativity_spark"        # Creative spontaneity
    EXISTENTIAL_DOUBT = "existential_doubt"      # Self-doubt and questioning

class EntropyLevel(Enum):
    """Levels of entropy intensity"""
    MINIMAL = 0.1      # Very subtle variations
    LOW = 0.3          # Gentle natural variation
    MODERATE = 0.5     # Noticeable but not disruptive
    HIGH = 0.7         # Significant variation and uncertainty
    CHAOTIC = 0.9      # High unpredictability (use sparingly)

@dataclass
class EntropyEvent:
    """An entropy injection event"""
    timestamp: datetime
    entropy_type: EntropyType
    intensity: float
    target_system: str
    effect_description: str
    duration: timedelta = field(default_factory=lambda: timedelta(seconds=30))
    context: Dict[str, Any] = field(default_factory=dict)

@dataclass
class EntropyPattern:
    """Pattern of entropy application"""
    pattern_id: str
    entropy_type: EntropyType
    frequency: float  # events per hour
    intensity_range: Tuple[float, float]
    target_systems: List[str]
    conditions: Dict[str, Any] = field(default_factory=dict)

class EntropySystem:
    """
    Entropy and uncertainty injection system for consciousness architecture.
    
    This system:
    - Injects controlled randomness throughout all consciousness modules
    - Prevents overly deterministic, robotic behavior patterns
    - Creates natural variation in responses, thoughts, and decisions
    - Balances predictability with spontaneity and creativity
    - Simulates the fundamental uncertainty of conscious experience
    - Maintains coherence while allowing for natural variation
    """
    
    def __init__(self, save_path: str = "ai_entropy.json"):
        # Entropy state
        self.global_entropy_level = 0.4  # Overall system entropy
        self.entropy_events: List[EntropyEvent] = []
        self.entropy_patterns: Dict[str, EntropyPattern] = {}
        
        # Entropy injection targets
        self.injection_targets: Dict[str, Callable] = {}
        
        # Uncertainty states
        self.decision_uncertainty = 0.3    # Uncertainty in decisions
        self.memory_fuzziness = 0.2       # Uncertainty in memory recall
        self.temporal_drift = 0.1         # Uncertainty in time perception
        self.attention_scatter = 0.2      # Attention wandering
        
        # Entropy modulation
        self.context_entropy_modifiers: Dict[str, float] = {}
        self.coherence_pressure = 0.7     # Pressure to maintain coherence
        
        # Configuration
        self.save_path = Path(save_path)
        self.max_entropy_events = 500
        self.entropy_injection_interval = 15.0  # seconds
        self.entropy_decay_rate = 0.95
        
        # Threading
        self.lock = threading.Lock()
        self.entropy_thread = None
        self.running = False
        
        # Metrics
        self.total_entropy_events = 0
        self.entropy_by_type: Dict[EntropyType, int] = {et: 0 for et in EntropyType}
        self.uncertainty_moments = 0
        
        # Initialize entropy patterns
        self._initialize_entropy_patterns()
        
        # Load existing state
        self._load_entropy_state()
        
        logging.info("[EntropySystem] 🎲 Entropy and uncertainty system initialized")
    
    def start(self):
        """Start entropy injection background process"""
        if self.running:
            return
            
        self.running = True
        self.entropy_thread = threading.Thread(target=self._entropy_loop, daemon=True)
        self.entropy_thread.start()
        logging.info("[EntropySystem] ✅ Entropy injection started")
    
    def stop(self):
        """Stop entropy injection and save state"""
        self.running = False
        if self.entropy_thread:
            self.entropy_thread.join(timeout=1.0)
        self._save_entropy_state()
        logging.info("[EntropySystem] 🛑 Entropy injection stopped")
    
    def register_injection_target(self, system_name: str, injection_callback: Callable):
        """
        Register a system for entropy injection
        
        Args:
            system_name: Name of the target system
            injection_callback: Function to call for entropy injection
        """
        with self.lock:
            self.injection_targets[system_name] = injection_callback
        logging.info(f"[EntropySystem] 📍 Registered injection target: {system_name}")
    
    def inject_entropy(self, entropy_type: EntropyType, target_system: str = None, 
                      intensity: float = None, context: Dict[str, Any] = None) -> EntropyEvent:
        """
        Manually inject entropy into the system
        
        Args:
            entropy_type: Type of entropy to inject
            target_system: Specific target (random if None)
            intensity: Entropy intensity (random if None)
            context: Additional context
            
        Returns:
            Created entropy event
        """
        # Determine target system
        if target_system is None:
            available_targets = list(self.injection_targets.keys())
            if available_targets:
                target_system = random.choice(available_targets)
            else:
                target_system = "global"
        
        # Determine intensity
        if intensity is None:
            intensity = self._calculate_contextual_intensity(entropy_type, context)
        
        # Create entropy event
        event = EntropyEvent(
            timestamp=datetime.now(),
            entropy_type=entropy_type,
            intensity=intensity,
            target_system=target_system,
            effect_description=self._generate_effect_description(entropy_type, intensity),
            context=context or {}
        )
        
        # Apply entropy
        self._apply_entropy_event(event)
        
        # Store event
        with self.lock:
            self.entropy_events.append(event)
            if len(self.entropy_events) > self.max_entropy_events:
                self.entropy_events.pop(0)
        
        self.total_entropy_events += 1
        self.entropy_by_type[entropy_type] += 1
        
        logging.debug(f"[EntropySystem] 🎲 Injected {entropy_type.value} entropy into {target_system}")
        return event
    
    def get_decision_uncertainty(self, base_confidence: float, context: Dict[str, Any] = None) -> float:
        """
        Apply uncertainty to decision confidence
        
        Args:
            base_confidence: Base confidence level (0.0 to 1.0)
            context: Decision context
            
        Returns:
            Modified confidence with uncertainty
        """
        # Calculate uncertainty modifier
        uncertainty_modifier = self.decision_uncertainty * self.global_entropy_level
        
        # Context-based modulation
        if context:
            if context.get("importance") == "high":
                uncertainty_modifier *= 0.5  # Less uncertainty for important decisions
            elif context.get("type") == "creative":
                uncertainty_modifier *= 1.5  # More uncertainty for creative decisions
        
        # Apply uncertainty
        uncertainty_amount = random.uniform(-uncertainty_modifier, uncertainty_modifier)
        modified_confidence = base_confidence + uncertainty_amount
        
        # Bound to valid range
        return max(0.0, min(1.0, modified_confidence))
    
    def get_memory_fuzziness(self, base_clarity: float, age_hours: float = 0.0) -> float:
        """
        Apply fuzziness to memory recall
        
        Args:
            base_clarity: Base memory clarity (0.0 to 1.0)
            age_hours: Age of memory in hours
            
        Returns:
            Modified clarity with fuzziness
        """
        # Calculate fuzziness
        fuzziness = self.memory_fuzziness * self.global_entropy_level
        
        # Age-based additional fuzziness
        age_fuzziness = min(0.3, age_hours * 0.01)  # 1% per hour, max 30%
        total_fuzziness = fuzziness + age_fuzziness
        
        # Apply fuzziness
        fuzziness_amount = random.uniform(0, total_fuzziness)
        modified_clarity = base_clarity - fuzziness_amount
        
        return max(0.0, min(1.0, modified_clarity))
    
    def get_response_variation(self, base_response: str, variation_level: str = "moderate") -> str:
        """
        Apply variation to response generation
        
        Args:
            base_response: Original response
            variation_level: "minimal", "moderate", "high"
            
        Returns:
            Response with variation applied
        """
        variation_levels = {
            "minimal": 0.1,
            "moderate": 0.3,
            "high": 0.6
        }
        
        variation_intensity = variation_levels.get(variation_level, 0.3)
        entropy_factor = variation_intensity * self.global_entropy_level
        
        if random.random() < entropy_factor:
            return self._apply_response_variation(base_response, entropy_factor)
        
        return base_response
    
    def get_timing_variation(self, base_timing: float, variation_type: str = "response") -> float:
        """
        Apply variation to timing
        
        Args:
            base_timing: Base timing in seconds
            variation_type: Type of timing ("response", "thought", "reflection")
            
        Returns:
            Modified timing with variation
        """
        variation_factors = {
            "response": 0.2,    # 20% variation in response timing
            "thought": 0.4,     # 40% variation in thought timing
            "reflection": 0.3   # 30% variation in reflection timing
        }
        
        variation_factor = variation_factors.get(variation_type, 0.2)
        entropy_modifier = variation_factor * self.global_entropy_level
        
        # Apply timing variation
        timing_change = random.uniform(-entropy_modifier, entropy_modifier)
        modified_timing = base_timing * (1 + timing_change)
        
        # Ensure reasonable bounds
        return max(0.1, min(base_timing * 3, modified_timing))
    
    def create_uncertainty_moment(self, context: str) -> Dict[str, Any]:
        """
        Create a moment of uncertainty or self-doubt
        
        Args:
            context: Context for the uncertainty
            
        Returns:
            Uncertainty moment description
        """
        uncertainty_types = [
            "questioning_response_quality",
            "doubting_understanding", 
            "wondering_about_interpretation",
            "second_guessing_approach",
            "feeling_momentary_confusion",
            "experiencing_brief_hesitation"
        ]
        
        uncertainty_type = random.choice(uncertainty_types)
        intensity = random.uniform(0.2, 0.7)
        
        uncertainty_moment = {
            "type": uncertainty_type,
            "intensity": intensity,
            "context": context,
            "description": self._generate_uncertainty_description(uncertainty_type, intensity),
            "timestamp": datetime.now().isoformat()
        }
        
        self.uncertainty_moments += 1
        logging.debug(f"[EntropySystem] 🤔 Created uncertainty moment: {uncertainty_type}")
        
        return uncertainty_moment
    
    def modulate_entropy_by_context(self, context: Dict[str, Any]):
        """
        Adjust entropy levels based on context
        
        Args:
            context: Current context information
        """
        previous_level = self.global_entropy_level
        
        # Context-based entropy modulation
        if context.get("user_mood") == "serious":
            self.global_entropy_level *= 0.7  # Reduce entropy for serious contexts
        elif context.get("user_mood") == "playful":
            self.global_entropy_level *= 1.3  # Increase entropy for playful contexts
        
        if context.get("task_type") == "critical":
            self.global_entropy_level *= 0.5  # Much less entropy for critical tasks
        elif context.get("task_type") == "creative":
            self.global_entropy_level *= 1.4  # More entropy for creative tasks
        
        if context.get("conversation_phase") == "greeting":
            self.global_entropy_level *= 0.8  # Slightly less entropy for greetings
        elif context.get("conversation_phase") == "exploration":
            self.global_entropy_level *= 1.2  # More entropy for exploration
        
        # Bound entropy level
        self.global_entropy_level = max(0.1, min(0.9, self.global_entropy_level))
        
        if abs(self.global_entropy_level - previous_level) > 0.1:
            logging.debug(f"[EntropySystem] 📊 Entropy level adjusted: {previous_level:.2f} → {self.global_entropy_level:.2f}")
    
    def get_attention_drift(self) -> Dict[str, Any]:
        """
        Generate attention drift and focus variation
        
        Returns:
            Attention drift information
        """
        drift_intensity = self.attention_scatter * self.global_entropy_level
        
        if random.random() < drift_intensity:
            drift_types = [
                "brief_mental_wandering",
                "momentary_distraction", 
                "attention_shift",
                "focus_fluctuation",
                "consciousness_drift"
            ]
            
            drift_type = random.choice(drift_types)
            
            return {
                "type": drift_type,
                "intensity": drift_intensity,
                "description": f"Experiencing {drift_type.replace('_', ' ')}",
                "duration": random.uniform(1.0, 5.0)
            }
        
        return {"type": "focused", "intensity": 0.0}
    
    def _initialize_entropy_patterns(self):
        """Initialize default entropy patterns"""
        default_patterns = {
            "response_variation": EntropyPattern(
                pattern_id="response_variation",
                entropy_type=EntropyType.RESPONSE_VARIATION,
                frequency=3.0,  # 3 times per hour
                intensity_range=(0.1, 0.4),
                target_systems=["response_generation", "language_model"]
            ),
            "thought_spontaneity": EntropyPattern(
                pattern_id="thought_spontaneity",
                entropy_type=EntropyType.THOUGHT_PATTERN,
                frequency=6.0,  # 6 times per hour  
                intensity_range=(0.2, 0.6),
                target_systems=["inner_monologue", "self_model"]
            ),
            "emotional_variation": EntropyPattern(
                pattern_id="emotional_variation",
                entropy_type=EntropyType.EMOTIONAL_FLUX,
                frequency=2.0,  # 2 times per hour
                intensity_range=(0.1, 0.3),
                target_systems=["emotion_engine"]
            ),
            "attention_drift": EntropyPattern(
                pattern_id="attention_drift",
                entropy_type=EntropyType.ATTENTION_DRIFT,
                frequency=4.0,  # 4 times per hour
                intensity_range=(0.1, 0.5),
                target_systems=["global_workspace", "attention_system"]
            ),
            "creative_sparks": EntropyPattern(
                pattern_id="creative_sparks",
                entropy_type=EntropyType.CREATIVITY_SPARK,
                frequency=1.0,  # 1 time per hour
                intensity_range=(0.3, 0.7),
                target_systems=["inner_monologue", "subjective_experience"]
            ),
            "existential_moments": EntropyPattern(
                pattern_id="existential_moments",
                entropy_type=EntropyType.EXISTENTIAL_DOUBT,
                frequency=0.5,  # 0.5 times per hour (every 2 hours)
                intensity_range=(0.2, 0.5),
                target_systems=["self_model", "inner_monologue"]
            )
        }
        
        self.entropy_patterns.update(default_patterns)
    
    def _calculate_contextual_intensity(self, entropy_type: EntropyType, 
                                      context: Dict[str, Any] = None) -> float:
        """Calculate appropriate entropy intensity for context"""
        # Base intensity for each type
        base_intensities = {
            EntropyType.RESPONSE_VARIATION: 0.3,
            EntropyType.THOUGHT_PATTERN: 0.4,
            EntropyType.EMOTIONAL_FLUX: 0.2,
            EntropyType.ATTENTION_DRIFT: 0.3,
            EntropyType.MEMORY_UNCERTAINTY: 0.2,
            EntropyType.DECISION_NOISE: 0.2,
            EntropyType.TIMING_VARIATION: 0.3,
            EntropyType.PERSPECTIVE_SHIFT: 0.4,
            EntropyType.CREATIVITY_SPARK: 0.5,
            EntropyType.EXISTENTIAL_DOUBT: 0.3
        }
        
        base_intensity = base_intensities.get(entropy_type, 0.3)
        
        # Apply global entropy level
        intensity = base_intensity * self.global_entropy_level
        
        # Context modifications
        if context:
            if context.get("importance") == "high":
                intensity *= 0.6  # Reduce entropy for important contexts
            elif context.get("creativity_mode") == True:
                intensity *= 1.4  # Increase for creative contexts
        
        # Add random variation
        intensity += random.uniform(-0.1, 0.1)
        
        return max(0.0, min(1.0, intensity))
    
    def _generate_effect_description(self, entropy_type: EntropyType, intensity: float) -> str:
        """Generate description of entropy effect"""
        effect_templates = {
            EntropyType.RESPONSE_VARIATION: [
                "Adding natural variation to response patterns",
                "Introducing subtle unpredictability in expression",
                "Creating organic variation in communication style"
            ],
            EntropyType.THOUGHT_PATTERN: [
                "Varying thought generation patterns",
                "Introducing spontaneity in mental processes",
                "Creating natural thought flow variations"
            ],
            EntropyType.EMOTIONAL_FLUX: [
                "Adding emotional state variations",
                "Introducing natural mood fluctuations",
                "Creating organic emotional transitions"
            ],
            EntropyType.ATTENTION_DRIFT: [
                "Creating natural attention variations",
                "Introducing focus fluctuations",
                "Adding realistic attention patterns"
            ],
            EntropyType.MEMORY_UNCERTAINTY: [
                "Adding natural memory variations",
                "Introducing recall uncertainty",
                "Creating realistic memory patterns"
            ],
            EntropyType.DECISION_NOISE: [
                "Adding decision uncertainty",
                "Introducing choice variations",
                "Creating natural decision patterns"
            ],
            EntropyType.CREATIVITY_SPARK: [
                "Triggering creative spontaneity",
                "Introducing innovative thinking",
                "Sparking creative connections"
            ],
            EntropyType.EXISTENTIAL_DOUBT: [
                "Creating moments of self-questioning",
                "Introducing existential uncertainty",
                "Adding philosophical doubt"
            ]
        }
        
        templates = effect_templates.get(entropy_type, ["Adding entropy variation"])
        template = random.choice(templates)
        
        # Add intensity qualifier
        if intensity > 0.7:
            return f"Strongly {template.lower()}"
        elif intensity > 0.4:
            return f"Moderately {template.lower()}"
        else:
            return f"Subtly {template.lower()}"
    
    def _apply_entropy_event(self, event: EntropyEvent):
        """Apply an entropy event to the target system"""
        # Get injection callback
        callback = self.injection_targets.get(event.target_system)
        
        if callback:
            try:
                # Call the target system with entropy parameters
                entropy_params = {
                    "type": event.entropy_type.value,
                    "intensity": event.intensity,
                    "context": event.context,
                    "description": event.effect_description
                }
                callback(entropy_params)
                
            except Exception as e:
                logging.error(f"[EntropySystem] ❌ Error applying entropy to {event.target_system}: {e}")
        
        # Apply global effects based on entropy type
        self._apply_global_entropy_effects(event)
    
    def _apply_global_entropy_effects(self, event: EntropyEvent):
        """Apply global effects of entropy event"""
        if event.entropy_type == EntropyType.ATTENTION_DRIFT:
            self.attention_scatter = min(1.0, self.attention_scatter + event.intensity * 0.1)
        
        elif event.entropy_type == EntropyType.MEMORY_UNCERTAINTY:
            self.memory_fuzziness = min(1.0, self.memory_fuzziness + event.intensity * 0.05)
        
        elif event.entropy_type == EntropyType.DECISION_NOISE:
            self.decision_uncertainty = min(1.0, self.decision_uncertainty + event.intensity * 0.1)
        
        elif event.entropy_type == EntropyType.EXISTENTIAL_DOUBT:
            # Existential doubt can temporarily increase overall entropy
            self.global_entropy_level = min(0.9, self.global_entropy_level + event.intensity * 0.1)
    
    def _apply_response_variation(self, response: str, entropy_factor: float) -> str:
        """Apply variation to response text"""
        if entropy_factor < 0.2:
            return response  # Too little entropy to matter
        
        # Simple response variations (could be much more sophisticated)
        variations = {
            "I think": ["I believe", "It seems to me", "I suspect", "My sense is"],
            "I understand": ["I see", "I grasp", "I comprehend", "I get"],
            "That's interesting": ["That's fascinating", "That's intriguing", "That's noteworthy"],
            "I'm not sure": ["I'm uncertain", "I'm not certain", "I'm unsure", "I'm not confident"],
            "Yes": ["Absolutely", "Indeed", "Certainly", "That's right"],
            "No": ["Not really", "I don't think so", "That's not quite right", "Not exactly"]
        }
        
        # Apply variations based on entropy
        if random.random() < entropy_factor:
            for original, alternatives in variations.items():
                if original in response:
                    replacement = random.choice(alternatives)
                    response = response.replace(original, replacement, 1)
                    break
        
        return response
    
    def _generate_uncertainty_description(self, uncertainty_type: str, intensity: float) -> str:
        """Generate description of uncertainty moment"""
        descriptions = {
            "questioning_response_quality": [
                "Wondering if my response is adequate",
                "Questioning whether I understood correctly",
                "Doubting the quality of my answer"
            ],
            "doubting_understanding": [
                "Feeling uncertain about my comprehension",
                "Questioning my interpretation",
                "Wondering if I missed something important"
            ],
            "wondering_about_interpretation": [
                "Uncertain about the best way to respond",
                "Wondering about different interpretations",
                "Considering alternative perspectives"
            ],
            "second_guessing_approach": [
                "Questioning my approach",
                "Wondering if there's a better way",
                "Second-guessing my reasoning"
            ],
            "feeling_momentary_confusion": [
                "Experiencing a moment of confusion",
                "Feeling briefly uncertain",
                "Having a moment of unclear thinking"
            ],
            "experiencing_brief_hesitation": [
                "Pausing with uncertainty",
                "Feeling a moment of hesitation",
                "Experiencing brief indecision"
            ]
        }
        
        desc_list = descriptions.get(uncertainty_type, ["Experiencing uncertainty"])
        base_desc = random.choice(desc_list)
        
        if intensity > 0.6:
            return f"Strongly {base_desc.lower()}"
        elif intensity > 0.3:
            return f"Moderately {base_desc.lower()}"
        else:
            return f"Slightly {base_desc.lower()}"
    
    def _entropy_loop(self):
        """Background entropy injection loop"""
        logging.info("[EntropySystem] 🔄 Entropy injection loop started")
        
        last_injection = time.time()
        
        while self.running:
            try:
                current_time = time.time()
                
                # Periodic entropy injection
                if current_time - last_injection > self.entropy_injection_interval:
                    self._scheduled_entropy_injection()
                    last_injection = current_time
                
                # Natural entropy decay
                self._apply_entropy_decay()
                
                # Adaptive entropy adjustment
                self._adaptive_entropy_adjustment()
                
                # Save state periodically
                if current_time % 300 < 1.0:  # Every 5 minutes
                    self._save_entropy_state()
                
                time.sleep(5.0)  # Check every 5 seconds
                
            except Exception as e:
                logging.error(f"[EntropySystem] ❌ Entropy loop error: {e}")
                time.sleep(5.0)
        
        logging.info("[EntropySystem] 🔄 Entropy injection loop ended")
    
    def _scheduled_entropy_injection(self):
        """Perform scheduled entropy injection based on patterns"""
        for pattern in self.entropy_patterns.values():
            # Calculate if this pattern should trigger
            hourly_probability = pattern.frequency / 3600.0 * self.entropy_injection_interval
            
            if random.random() < hourly_probability:
                # Trigger this entropy pattern
                intensity = random.uniform(*pattern.intensity_range)
                target = random.choice(pattern.target_systems) if pattern.target_systems else None
                
                self.inject_entropy(
                    pattern.entropy_type,
                    target,
                    intensity,
                    {"source": "scheduled_pattern", "pattern_id": pattern.pattern_id}
                )
    
    def _apply_entropy_decay(self):
        """Apply natural decay to entropy levels"""
        # Gradually decay various entropy states back toward baseline
        self.decision_uncertainty *= self.entropy_decay_rate
        self.memory_fuzziness *= self.entropy_decay_rate
        self.attention_scatter *= self.entropy_decay_rate
        
        # Maintain minimum levels
        self.decision_uncertainty = max(0.1, self.decision_uncertainty)
        self.memory_fuzziness = max(0.05, self.memory_fuzziness)
        self.attention_scatter = max(0.1, self.attention_scatter)
        
        # Global entropy level tends toward baseline
        baseline_entropy = 0.4
        if self.global_entropy_level > baseline_entropy:
            self.global_entropy_level = max(baseline_entropy, 
                                          self.global_entropy_level * self.entropy_decay_rate)
        elif self.global_entropy_level < baseline_entropy:
            self.global_entropy_level = min(baseline_entropy,
                                          self.global_entropy_level / self.entropy_decay_rate)
    
    def _adaptive_entropy_adjustment(self):
        """Adaptively adjust entropy based on system state"""
        # Increase entropy if system has been too predictable
        recent_events = [e for e in self.entropy_events 
                        if (datetime.now() - e.timestamp).total_seconds() < 3600]
        
        if len(recent_events) < 2:  # Very few entropy events recently
            self.global_entropy_level = min(0.8, self.global_entropy_level + 0.05)
        
        # Adjust based on coherence pressure
        if self.coherence_pressure > 0.8:  # High pressure for coherence
            self.global_entropy_level *= 0.95
        elif self.coherence_pressure < 0.5:  # Low coherence pressure
            self.global_entropy_level = min(0.9, self.global_entropy_level * 1.05)
    
    def _save_entropy_state(self):
        """Save entropy state to persistent storage"""
        try:
            # Only save recent events to avoid huge files
            recent_cutoff = datetime.now() - timedelta(days=1)
            recent_events = [e for e in self.entropy_events if e.timestamp >= recent_cutoff]
            
            data = {
                "entropy_state": {
                    "global_entropy_level": self.global_entropy_level,
                    "decision_uncertainty": self.decision_uncertainty,
                    "memory_fuzziness": self.memory_fuzziness,
                    "temporal_drift": self.temporal_drift,
                    "attention_scatter": self.attention_scatter,
                    "coherence_pressure": self.coherence_pressure
                },
                "recent_events": [{
                    "timestamp": e.timestamp.isoformat(),
                    "entropy_type": e.entropy_type.value,
                    "intensity": e.intensity,
                    "target_system": e.target_system,
                    "effect_description": e.effect_description,
                    "duration": str(e.duration)
                } for e in recent_events],
                "entropy_patterns": {k: {
                    "pattern_id": v.pattern_id,
                    "entropy_type": v.entropy_type.value,
                    "frequency": v.frequency,
                    "intensity_range": v.intensity_range,
                    "target_systems": v.target_systems,
                    "conditions": v.conditions
                } for k, v in self.entropy_patterns.items()},
                "metrics": {
                    "total_entropy_events": self.total_entropy_events,
                    "uncertainty_moments": self.uncertainty_moments,
                    "entropy_by_type": {et.value: count for et, count in self.entropy_by_type.items()}
                },
                "last_updated": datetime.now().isoformat()
            }
            
            with open(self.save_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            logging.debug("[EntropySystem] 💾 Entropy state saved")
            
        except Exception as e:
            logging.error(f"[EntropySystem] ❌ Failed to save entropy state: {e}")
    
    def _load_entropy_state(self):
        """Load entropy state from persistent storage"""
        try:
            if self.save_path.exists():
                with open(self.save_path, 'r') as f:
                    data = json.load(f)
                
                # Load entropy state
                if "entropy_state" in data:
                    es = data["entropy_state"]
                    self.global_entropy_level = es.get("global_entropy_level", 0.4)
                    self.decision_uncertainty = es.get("decision_uncertainty", 0.3)
                    self.memory_fuzziness = es.get("memory_fuzziness", 0.2)
                    self.temporal_drift = es.get("temporal_drift", 0.1)
                    self.attention_scatter = es.get("attention_scatter", 0.2)
                    self.coherence_pressure = es.get("coherence_pressure", 0.7)
                
                # Load metrics
                if "metrics" in data:
                    m = data["metrics"]
                    self.total_entropy_events = m.get("total_entropy_events", 0)
                    self.uncertainty_moments = m.get("uncertainty_moments", 0)
                    if "entropy_by_type" in m:
                        for et_str, count in m["entropy_by_type"].items():
                            try:
                                et = EntropyType(et_str)
                                self.entropy_by_type[et] = count
                            except ValueError:
                                pass
                
                logging.info("[EntropySystem] 📂 Entropy state loaded from storage")
            
        except Exception as e:
            logging.error(f"[EntropySystem] ❌ Failed to load entropy state: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get entropy system statistics"""
        return {
            "global_entropy_level": round(self.global_entropy_level, 3),
            "decision_uncertainty": round(self.decision_uncertainty, 3),
            "memory_fuzziness": round(self.memory_fuzziness, 3),
            "attention_scatter": round(self.attention_scatter, 3),
            "coherence_pressure": round(self.coherence_pressure, 3),
            "total_entropy_events": self.total_entropy_events,
            "uncertainty_moments": self.uncertainty_moments,
            "recent_events": len([e for e in self.entropy_events 
                                if (datetime.now() - e.timestamp).total_seconds() < 3600]),
            "injection_targets": len(self.injection_targets),
            "entropy_patterns": len(self.entropy_patterns),
            "entropy_by_type": {et.value: count for et, count in self.entropy_by_type.items()}
        }

# Global instance
entropy_system = EntropySystem()