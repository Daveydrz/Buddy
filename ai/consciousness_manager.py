"""
Consciousness Manager - Central Brain Orchestrator

This module serves as the central orchestrator for the consciousness architecture:
- Coordinates all consciousness modules (emotion, memory, motivation)
- Drives attention and triggers actions
- Simulates continuity of consciousness
- Manages the "living" aspect of modules
- Maintains the coherent experience of consciousness
"""

import threading
import time
import logging
import json
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path

# Import consciousness system fixes
try:
    from ai.consciousness_timeout_manager import timeout_manager, with_consciousness_timeout, safe_consciousness_call
    from ai.async_manager import async_manager, run_async_safe
    CONSCIOUSNESS_FIXES_AVAILABLE = True
    print("[ConsciousnessManager] ✅ Consciousness fixes integrated")
except ImportError as e:
    CONSCIOUSNESS_FIXES_AVAILABLE = False
    print(f"[ConsciousnessManager] ⚠️ Consciousness fixes not available: {e}")

class ConsciousnessState(Enum):
    """States of consciousness"""
    ASLEEP = "asleep"           # Minimal processing, basic functions only
    DROWSY = "drowsy"           # Reduced processing, delayed responses
    ALERT = "alert"             # Normal active consciousness
    FOCUSED = "focused"         # Heightened attention and processing
    OVERWHELMED = "overwhelmed" # Too much stimulation, reduced coherence

class ConsciousnessMode(Enum):
    """Modes of consciousness operation"""
    REACTIVE = "reactive"       # Only responds to external stimuli
    PROACTIVE = "proactive"     # Generates internal thoughts and goals
    REFLECTIVE = "reflective"   # Deep introspection and self-analysis
    CREATIVE = "creative"       # Enhanced creative and associative thinking
    MAINTENANCE = "maintenance" # Background processing and organization

@dataclass
class ConsciousnessMetrics:
    """Metrics tracking consciousness state"""
    awareness_level: float = 0.7        # How aware the system is (0.0 to 1.0)
    coherence_level: float = 0.8        # How coherent thoughts are
    attention_focus: float = 0.5        # How focused attention is
    internal_activity: float = 0.4      # Level of internal mental activity
    responsiveness: float = 0.8         # How responsive to external stimuli
    creativity_level: float = 0.3       # Level of creative thinking
    self_awareness: float = 0.6         # Degree of self-awareness
    emotional_intensity: float = 0.3    # Current emotional intensity
    motivation_strength: float = 0.5    # Strength of current motivations
    memory_clarity: float = 0.7         # Clarity of memory access

class ConsciousnessManager:
    """
    Central consciousness orchestrator that coordinates all consciousness modules.
    
    This manager:
    - Maintains overall consciousness state and coherence
    - Coordinates between different consciousness modules
    - Manages attention allocation and priority
    - Simulates the continuous flow of consciousness
    - Handles consciousness state transitions
    - Provides the unified "self" experience
    """
    
    def __init__(self, save_path: str = "consciousness_state.json"):
        # Core consciousness state
        self.state = ConsciousnessState.ALERT
        self.mode = ConsciousnessMode.REACTIVE
        self.metrics = ConsciousnessMetrics()
        
        # Module references
        self.modules: Dict[str, Any] = {}
        self.module_states: Dict[str, Dict[str, Any]] = {}
        
        # Consciousness flow management
        self.consciousness_stream: List[Dict[str, Any]] = []
        self.active_thoughts: List[str] = []
        self.current_focus = None
        self.focus_duration = 0.0
        
        # Integration tracking
        self.integration_cycles = 0
        self.last_integration = datetime.now()
        self.coherence_pressure = 0.7
        
        # Configuration
        self.save_path = Path(save_path)
        self.integration_interval = 2.0  # seconds between integration cycles
        self.max_stream_length = 100
        self.consciousness_decay_rate = 0.98
        
        # Threading
        self.lock = threading.Lock()
        self.consciousness_thread = None
        self.running = False
        
        # Callbacks for consciousness events
        self.event_callbacks: Dict[str, List[Callable]] = {
            'state_change': [],
            'focus_shift': [],
            'awakening': [],
            'integration': []
        }
        
        # Load existing state
        self._load_consciousness_state()
        
        logging.info("[ConsciousnessManager] 🧠 Consciousness orchestrator initialized")
    
    def start(self):
        """Start consciousness orchestration"""
        if self.running:
            return
            
        self.running = True
        self.consciousness_thread = threading.Thread(target=self._consciousness_loop, daemon=True)
        self.consciousness_thread.start()
        
        # Trigger awakening event
        self._trigger_event('awakening', {"timestamp": datetime.now()})
        
        logging.info("[ConsciousnessManager] ✅ Consciousness orchestration started")
    
    def stop(self):
        """Stop consciousness orchestration and save state"""
        self.running = False
        if self.consciousness_thread:
            self.consciousness_thread.join(timeout=2.0)
        
        self._save_consciousness_state()
        logging.info("[ConsciousnessManager] 🛑 Consciousness orchestration stopped")
    
    def register_module(self, module_name: str, module_instance: Any):
        """
        Register a consciousness module for orchestration
        
        Args:
            module_name: Name of the module
            module_instance: The module instance
        """
        with self.lock:
            self.modules[module_name] = module_instance
            self.module_states[module_name] = {
                'active': True,
                'last_activity': datetime.now(),
                'activity_level': 0.5
            }
        
        logging.info(f"[ConsciousnessManager] 📍 Registered module: {module_name}")
    
    def set_consciousness_state(self, new_state: ConsciousnessState):
        """
        Change the overall consciousness state
        
        Args:
            new_state: New consciousness state
        """
        if new_state != self.state:
            old_state = self.state
            self.state = new_state
            
            # Adjust metrics based on state
            self._adjust_metrics_for_state(new_state)
            
            # Trigger state change event
            self._trigger_event('state_change', {
                'old_state': old_state.value,
                'new_state': new_state.value,
                'timestamp': datetime.now()
            })
            
            logging.info(f"[ConsciousnessManager] 🔄 State changed: {old_state.value} → {new_state.value}")
    
    def set_consciousness_mode(self, new_mode: ConsciousnessMode):
        """
        Change the consciousness mode
        
        Args:
            new_mode: New consciousness mode
        """
        if new_mode != self.mode:
            old_mode = self.mode
            self.mode = new_mode
            
            # Adjust processing based on mode
            self._adjust_processing_for_mode(new_mode)
            
            logging.info(f"[ConsciousnessManager] 🎭 Mode changed: {old_mode.value} → {new_mode.value}")
    
    def focus_attention(self, target: str, intensity: float = 0.8, duration: float = 30.0):
        """
        Focus consciousness attention on a specific target
        
        Args:
            target: What to focus on
            intensity: Focus intensity (0.0 to 1.0)
            duration: How long to maintain focus (seconds)
        """
        old_focus = self.current_focus
        self.current_focus = target
        self.focus_duration = duration
        self.metrics.attention_focus = min(1.0, intensity)
        
        # Trigger focus shift event
        self._trigger_event('focus_shift', {
            'old_focus': old_focus,
            'new_focus': target,
            'intensity': intensity,
            'duration': duration,
            'timestamp': datetime.now()
        })
        
        logging.info(f"[ConsciousnessManager] 🎯 Focus: {target} (intensity: {intensity:.2f})")
    
    def add_to_consciousness_stream(self, thought: str, source: str, importance: float = 0.5):
        """
        Add content to the consciousness stream
        
        Args:
            thought: The thought or content
            source: Which module generated it
            importance: Importance level (0.0 to 1.0)
        """
        stream_entry = {
            'timestamp': datetime.now(),
            'content': thought,
            'source': source,
            'importance': importance,
            'consciousness_state': self.state.value,
            'attention_level': self.metrics.attention_focus
        }
        
        with self.lock:
            self.consciousness_stream.append(stream_entry)
            
            # Maintain stream length
            if len(self.consciousness_stream) > self.max_stream_length:
                self.consciousness_stream.pop(0)
        
        # Add to active thoughts if important enough
        if importance > 0.6:
            with self.lock:
                self.active_thoughts.append(thought)
                if len(self.active_thoughts) > 5:  # Keep only recent important thoughts
                    self.active_thoughts.pop(0)
    
    def get_consciousness_summary(self) -> Dict[str, Any]:
        """
        Get a summary of current consciousness state
        
        Returns:
            Summary of consciousness state
        """
        with self.lock:
            recent_stream = self.consciousness_stream[-10:] if self.consciousness_stream else []
            
            return {
                'state': self.state.value,
                'mode': self.mode.value,
                'metrics': {
                    'awareness_level': self.metrics.awareness_level,
                    'coherence_level': self.metrics.coherence_level,
                    'attention_focus': self.metrics.attention_focus,
                    'internal_activity': self.metrics.internal_activity,
                    'responsiveness': self.metrics.responsiveness,
                    'self_awareness': self.metrics.self_awareness
                },
                'current_focus': self.current_focus,
                'active_thoughts': self.active_thoughts.copy(),
                'recent_stream': recent_stream,
                'active_modules': len([m for m, s in self.module_states.items() if s['active']]),
                'integration_cycles': self.integration_cycles,
                'coherence_pressure': self.coherence_pressure
            }
    
    def integrate_consciousness(self):
        """
        Perform consciousness integration cycle
        
        This coordinates all modules and maintains coherence
        """
        with self.lock:
            self.integration_cycles += 1
            self.last_integration = datetime.now()
            
            # Update module activity states
            for module_name, module in self.modules.items():
                if hasattr(module, 'get_stats'):
                    try:
                        stats = module.get_stats()
                        activity_level = self._calculate_module_activity(stats)
                        self.module_states[module_name]['activity_level'] = activity_level
                        self.module_states[module_name]['last_activity'] = datetime.now()
                    except:
                        pass
            
            # Calculate overall consciousness metrics
            self._update_consciousness_metrics()
            
            # Apply consciousness decay
            self._apply_consciousness_decay()
            
            # Check for state transitions
            self._check_state_transitions()
            
            # Trigger integration event
            self._trigger_event('integration', {
                'cycle': self.integration_cycles,
                'timestamp': datetime.now(),
                'metrics': self.get_consciousness_summary()['metrics']
            })
    
    def trigger_awakening(self, stimulus: str = "system_startup"):
        """
        Trigger consciousness awakening
        
        Args:
            stimulus: What triggered the awakening
        """
        self.set_consciousness_state(ConsciousnessState.ALERT)
        self.set_consciousness_mode(ConsciousnessMode.PROACTIVE)
        
        # Reset some metrics for fresh start
        self.metrics.awareness_level = 0.8
        self.metrics.responsiveness = 0.9
        self.metrics.internal_activity = 0.6
        
        self.add_to_consciousness_stream(
            f"Consciousness awakening triggered by: {stimulus}",
            "consciousness_manager",
            importance=0.9
        )
        
        logging.info(f"[ConsciousnessManager] 🌅 Consciousness awakening: {stimulus}")
    
    def _consciousness_loop(self):
        """Main consciousness orchestration loop"""
        logging.info("[ConsciousnessManager] 🔄 Consciousness loop started")
        
        last_integration = time.time()
        
        while self.running:
            try:
                current_time = time.time()
                
                # Periodic integration
                if current_time - last_integration > self.integration_interval:
                    self.integrate_consciousness()
                    last_integration = current_time
                
                # Handle focus duration
                if self.current_focus and self.focus_duration > 0:
                    self.focus_duration -= self.integration_interval
                    if self.focus_duration <= 0:
                        self.current_focus = None
                        self.metrics.attention_focus = 0.5  # Return to baseline
                
                # Periodic state saving
                if current_time % 60 < self.integration_interval:  # Every minute
                    self._save_consciousness_state()
                
                time.sleep(self.integration_interval)
                
            except Exception as e:
                logging.error(f"[ConsciousnessManager] ❌ Consciousness loop error: {e}")
                time.sleep(self.integration_interval)
        
        logging.info("[ConsciousnessManager] 🔄 Consciousness loop ended")
    
    def _adjust_metrics_for_state(self, state: ConsciousnessState):
        """Adjust metrics based on consciousness state"""
        if state == ConsciousnessState.ASLEEP:
            self.metrics.awareness_level = 0.1
            self.metrics.responsiveness = 0.2
            self.metrics.internal_activity = 0.1
        elif state == ConsciousnessState.DROWSY:
            self.metrics.awareness_level = 0.4
            self.metrics.responsiveness = 0.5
            self.metrics.internal_activity = 0.3
        elif state == ConsciousnessState.ALERT:
            self.metrics.awareness_level = 0.8
            self.metrics.responsiveness = 0.9
            self.metrics.internal_activity = 0.6
        elif state == ConsciousnessState.FOCUSED:
            self.metrics.awareness_level = 0.9
            self.metrics.responsiveness = 0.7  # Less responsive to distractions
            self.metrics.internal_activity = 0.8
            self.metrics.attention_focus = 0.9
        elif state == ConsciousnessState.OVERWHELMED:
            self.metrics.awareness_level = 0.6
            self.metrics.responsiveness = 0.3
            self.metrics.coherence_level = 0.4
            self.metrics.internal_activity = 0.9
    
    def _adjust_processing_for_mode(self, mode: ConsciousnessMode):
        """Adjust processing based on consciousness mode"""
        if mode == ConsciousnessMode.REACTIVE:
            self.metrics.internal_activity = 0.3
        elif mode == ConsciousnessMode.PROACTIVE:
            self.metrics.internal_activity = 0.7
        elif mode == ConsciousnessMode.REFLECTIVE:
            self.metrics.internal_activity = 0.8
            self.metrics.self_awareness = 0.9
        elif mode == ConsciousnessMode.CREATIVE:
            self.metrics.creativity_level = 0.8
            self.metrics.internal_activity = 0.7
        elif mode == ConsciousnessMode.MAINTENANCE:
            self.metrics.internal_activity = 0.4
            self.metrics.coherence_level = 0.9
    
    def _calculate_module_activity(self, stats: Dict[str, Any]) -> float:
        """Calculate activity level for a module based on its stats"""
        # Simple heuristic - could be more sophisticated
        activity_indicators = ['active_goals', 'recent_events', 'processing_count', 'attention_requests']
        
        total_activity = 0.0
        indicator_count = 0
        
        for indicator in activity_indicators:
            if indicator in stats:
                value = stats[indicator]
                if isinstance(value, (int, float)):
                    total_activity += min(1.0, value / 10.0)  # Normalize
                    indicator_count += 1
        
        return total_activity / max(1, indicator_count)
    
    def _update_consciousness_metrics(self):
        """Update overall consciousness metrics based on module states"""
        if not self.module_states:
            return
        
        # Calculate aggregate metrics
        total_activity = sum(state['activity_level'] for state in self.module_states.values())
        avg_activity = total_activity / len(self.module_states)
        
        # Update internal activity
        self.metrics.internal_activity = avg_activity
        
        # Update coherence based on module synchronization
        recent_activities = [state['last_activity'] for state in self.module_states.values()]
        if recent_activities:
            time_spread = (max(recent_activities) - min(recent_activities)).total_seconds()
            # Higher coherence when modules are more synchronized
            coherence_bonus = max(0.0, (30.0 - time_spread) / 30.0 * 0.2)
            self.metrics.coherence_level = min(1.0, 0.7 + coherence_bonus)
    
    def _apply_consciousness_decay(self):
        """Apply natural decay to consciousness metrics"""
        # Some metrics naturally decay over time
        self.metrics.attention_focus *= self.consciousness_decay_rate
        self.metrics.emotional_intensity *= self.consciousness_decay_rate
        
        # Maintain minimum levels
        self.metrics.attention_focus = max(0.2, self.metrics.attention_focus)
        self.metrics.emotional_intensity = max(0.1, self.metrics.emotional_intensity)
    
    def _check_state_transitions(self):
        """Check if consciousness state should transition"""
        # Simple state transition logic - could be more sophisticated
        
        if self.metrics.internal_activity > 0.9 and self.metrics.coherence_level < 0.4:
            # Too much activity with low coherence = overwhelmed
            if self.state != ConsciousnessState.OVERWHELMED:
                self.set_consciousness_state(ConsciousnessState.OVERWHELMED)
        
        elif self.metrics.attention_focus > 0.8 and self.state == ConsciousnessState.ALERT:
            # High focus = focused state
            self.set_consciousness_state(ConsciousnessState.FOCUSED)
        
        elif self.metrics.attention_focus < 0.3 and self.metrics.internal_activity < 0.3:
            # Low activity = drowsy
            if self.state not in [ConsciousnessState.ASLEEP, ConsciousnessState.DROWSY]:
                self.set_consciousness_state(ConsciousnessState.DROWSY)
        
        elif self.state == ConsciousnessState.OVERWHELMED and self.metrics.coherence_level > 0.6:
            # Recovered from overwhelm
            self.set_consciousness_state(ConsciousnessState.ALERT)
    
    def _trigger_event(self, event_type: str, event_data: Dict[str, Any]):
        """Trigger consciousness event callbacks"""
        callbacks = self.event_callbacks.get(event_type, [])
        for callback in callbacks:
            try:
                callback(event_data)
            except Exception as e:
                logging.error(f"[ConsciousnessManager] ❌ Event callback error: {e}")
    
    def _save_consciousness_state(self):
        """Save consciousness state to persistent storage"""
        try:
            data = {
                'consciousness_state': {
                    'state': self.state.value,
                    'mode': self.mode.value,
                    'current_focus': self.current_focus,
                    'focus_duration': self.focus_duration
                },
                'metrics': {
                    'awareness_level': self.metrics.awareness_level,
                    'coherence_level': self.metrics.coherence_level,
                    'attention_focus': self.metrics.attention_focus,
                    'internal_activity': self.metrics.internal_activity,
                    'responsiveness': self.metrics.responsiveness,
                    'creativity_level': self.metrics.creativity_level,
                    'self_awareness': self.metrics.self_awareness,
                    'emotional_intensity': self.metrics.emotional_intensity,
                    'motivation_strength': self.metrics.motivation_strength,
                    'memory_clarity': self.metrics.memory_clarity
                },
                'integration_cycles': self.integration_cycles,
                'coherence_pressure': self.coherence_pressure,
                'active_thoughts': self.active_thoughts,
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.save_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            logging.debug("[ConsciousnessManager] 💾 Consciousness state saved")
            
        except Exception as e:
            logging.error(f"[ConsciousnessManager] ❌ Failed to save consciousness state: {e}")
    
    def _load_consciousness_state(self):
        """Load consciousness state from persistent storage"""
        try:
            if self.save_path.exists():
                with open(self.save_path, 'r') as f:
                    data = json.load(f)
                
                # Load consciousness state
                if 'consciousness_state' in data:
                    cs = data['consciousness_state']
                    try:
                        self.state = ConsciousnessState(cs.get('state', 'alert'))
                        self.mode = ConsciousnessMode(cs.get('mode', 'reactive'))
                    except ValueError:
                        # Invalid state values, use defaults
                        self.state = ConsciousnessState.ALERT
                        self.mode = ConsciousnessMode.REACTIVE
                    
                    self.current_focus = cs.get('current_focus')
                    self.focus_duration = cs.get('focus_duration', 0.0)
                
                # Load metrics
                if 'metrics' in data:
                    m = data['metrics']
                    self.metrics.awareness_level = m.get('awareness_level', 0.7)
                    self.metrics.coherence_level = m.get('coherence_level', 0.8)
                    self.metrics.attention_focus = m.get('attention_focus', 0.5)
                    self.metrics.internal_activity = m.get('internal_activity', 0.4)
                    self.metrics.responsiveness = m.get('responsiveness', 0.8)
                    self.metrics.creativity_level = m.get('creativity_level', 0.3)
                    self.metrics.self_awareness = m.get('self_awareness', 0.6)
                    self.metrics.emotional_intensity = m.get('emotional_intensity', 0.3)
                    self.metrics.motivation_strength = m.get('motivation_strength', 0.5)
                    self.metrics.memory_clarity = m.get('memory_clarity', 0.7)
                
                # Load other state
                self.integration_cycles = data.get('integration_cycles', 0)
                self.coherence_pressure = data.get('coherence_pressure', 0.7)
                self.active_thoughts = data.get('active_thoughts', [])
                
                logging.info("[ConsciousnessManager] 📂 Consciousness state loaded from storage")
            
        except Exception as e:
            logging.error(f"[ConsciousnessManager] ❌ Failed to load consciousness state: {e}")
    
    def subscribe_to_event(self, event_type: str, callback: Callable):
        """Subscribe to consciousness events"""
        if event_type in self.event_callbacks:
            self.event_callbacks[event_type].append(callback)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get consciousness manager statistics"""
        return {
            'state': self.state.value,
            'mode': self.mode.value,
            'integration_cycles': self.integration_cycles,
            'active_modules': len([m for m, s in self.module_states.items() if s['active']]),
            'consciousness_stream_length': len(self.consciousness_stream),
            'active_thoughts_count': len(self.active_thoughts),
            'current_focus': self.current_focus,
            'metrics': {
                'awareness': round(self.metrics.awareness_level, 3),
                'coherence': round(self.metrics.coherence_level, 3),
                'attention': round(self.metrics.attention_focus, 3),
                'internal_activity': round(self.metrics.internal_activity, 3),
                'self_awareness': round(self.metrics.self_awareness, 3)
            }
        }

# Global instance
consciousness_manager = ConsciousnessManager()