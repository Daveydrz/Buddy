"""
Attention Manager - Focus Control System

This module manages attention and focus like human attention:
- Focuses mind on most important topics
- Prevents rambling and maintains coherence
- Prioritizes emotions, voices, tasks based on importance
- Manages attention switching and multitasking
- Simulates attention limitations and cognitive load
"""

import threading
import time
import logging
import json
import random
from typing import Dict, List, Any, Optional, Callable, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path

class AttentionType(Enum):
    """Types of attention"""
    FOCUSED = "focused"         # Deep, concentrated attention
    SELECTIVE = "selective"     # Selective attention to specific stimuli
    DIVIDED = "divided"         # Attention split between multiple tasks
    SUSTAINED = "sustained"     # Prolonged attention over time
    ALTERNATING = "alternating" # Switching between tasks
    AUTOMATIC = "automatic"     # Automatic, unconscious attention

class AttentionPriority(Enum):
    """Priority levels for attention requests"""
    CRITICAL = 1.0      # Immediate attention required
    HIGH = 0.8          # Important, should interrupt current focus
    MEDIUM = 0.6        # Normal priority
    LOW = 0.4           # Can wait for appropriate time
    BACKGROUND = 0.2    # Minimal attention, background processing

class AttentionState(Enum):
    """Current state of attention system"""
    ALERT = "alert"             # Fully attentive and responsive
    FOCUSED = "focused"         # Deeply focused on specific task
    DISTRACTED = "distracted"   # Easily distracted, unfocused
    OVERLOADED = "overloaded"   # Too many attention demands
    RELAXED = "relaxed"         # Calm, open awareness
    FATIGUED = "fatigued"       # Attention fatigue, reduced capacity

@dataclass
class AttentionRequest:
    """Request for attention from a system component"""
    id: str
    source: str
    content: str
    priority: AttentionPriority
    attention_type: AttentionType
    requested_duration: float  # seconds
    creation_time: datetime = field(default_factory=datetime.now)
    
    # Attention characteristics
    urgency: float = 0.5        # How urgent this request is
    complexity: float = 0.5     # How much cognitive load this requires
    novelty: float = 0.5        # How novel/interesting this is
    emotional_weight: float = 0.5  # Emotional significance
    
    # Context and metadata
    context: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    
    # Processing state
    granted: bool = False
    started_time: Optional[datetime] = None
    completed_time: Optional[datetime] = None
    actual_duration: float = 0.0

@dataclass
class AttentionFocus:
    """Current focus of attention"""
    target: str
    source: str
    content: str
    focus_type: AttentionType
    intensity: float            # 0.0 to 1.0
    
    start_time: datetime = field(default_factory=datetime.now)
    expected_duration: float = 30.0  # seconds
    actual_duration: float = 0.0
    
    # Focus characteristics
    depth: float = 0.5          # How deeply focused
    stability: float = 0.7      # How stable this focus is
    cognitive_load: float = 0.5 # Mental effort required
    
    # Context
    context: Dict[str, Any] = field(default_factory=dict)
    interruption_count: int = 0

class AttentionManager:
    """
    Attention and focus control system that manages cognitive resources.
    
    This manager:
    - Manages attention allocation like human attention
    - Prioritizes competing attention demands
    - Maintains focus while allowing appropriate interruptions
    - Simulates attention limitations and cognitive load
    - Prevents information overload and maintains coherence
    - Handles attention switching and multitasking
    """
    
    def __init__(self, save_path: str = "attention_state.json"):
        # Attention state
        self.state = AttentionState.ALERT
        self.current_focus: Optional[AttentionFocus] = None
        self.attention_capacity = 1.0  # Total attention capacity
        self.available_capacity = 1.0  # Currently available capacity
        
        # Attention requests
        self.pending_requests: List[AttentionRequest] = []
        self.active_requests: List[AttentionRequest] = []
        self.completed_requests: List[AttentionRequest] = []
        
        # Attention metrics
        self.focus_stability = 0.7      # How stable current focus is
        self.distractibility = 0.3      # How easily distracted
        self.cognitive_load = 0.4       # Current mental load
        self.attention_fatigue = 0.2    # Fatigue level
        self.novelty_bias = 0.4         # Preference for novel stimuli
        
        # Focus management
        self.focus_history: List[AttentionFocus] = []
        self.attention_switches = 0
        self.total_focus_time = 0.0
        self.interruption_tolerance = 0.6  # Tolerance for interruptions
        
        # Configuration
        self.save_path = Path(save_path)
        self.max_concurrent_requests = 3
        self.max_pending_requests = 10
        self.attention_decay_rate = 0.98
        self.focus_update_interval = 1.0  # seconds
        
        # Threading
        self.lock = threading.Lock()
        self.attention_thread = None
        self.running = False
        
        # Event callbacks
        self.event_callbacks: Dict[str, List[Callable]] = {
            'focus_started': [],
            'focus_ended': [],
            'attention_switched': [],
            'attention_overload': [],
            'focus_interrupted': []
        }
        
        # Load existing state
        self._load_attention_state()
        
        logging.info("[AttentionManager] 🎯 Attention management system initialized")
    
    def start(self):
        """Start attention management"""
        if self.running:
            return
            
        self.running = True
        self.attention_thread = threading.Thread(target=self._attention_loop, daemon=True)
        self.attention_thread.start()
        
        logging.info("[AttentionManager] ✅ Attention management started")
    
    def stop(self):
        """Stop attention management and save state"""
        self.running = False
        if self.attention_thread:
            self.attention_thread.join(timeout=2.0)
        self._save_attention_state()
        logging.info("[AttentionManager] 🛑 Attention management stopped")
    
    def request_attention(self, source: str, content: str, 
                         priority: AttentionPriority = AttentionPriority.MEDIUM,
                         attention_type: AttentionType = AttentionType.SELECTIVE,
                         duration: float = 30.0,
                         urgency: float = 0.5,
                         complexity: float = 0.5,
                         emotional_weight: float = 0.5,
                         context: Dict[str, Any] = None,
                         tags: List[str] = None) -> str:
        """
        Request attention from the system
        
        Args:
            source: System component requesting attention
            content: What requires attention
            priority: Priority level
            attention_type: Type of attention needed
            duration: Expected duration in seconds
            urgency: How urgent this request is (0.0 to 1.0)
            complexity: Cognitive complexity (0.0 to 1.0)
            emotional_weight: Emotional significance (0.0 to 1.0)
            context: Additional context
            tags: Tags for categorization
            
        Returns:
            Attention request ID
        """
        request_id = f"attn_{int(time.time() * 1000)}_{source}"
        
        request = AttentionRequest(
            id=request_id,
            source=source,
            content=content,
            priority=priority,
            attention_type=attention_type,
            requested_duration=duration,
            urgency=urgency,
            complexity=complexity,
            emotional_weight=emotional_weight,
            context=context or {},
            tags=tags or []
        )
        
        # Calculate novelty
        request.novelty = self._calculate_novelty(content, source, context)
        
        with self.lock:
            # Check if we can handle this request immediately
            if self._can_grant_immediately(request):
                self._grant_attention(request)
            else:
                # Add to pending requests
                self.pending_requests.append(request)
                
                # Maintain queue size
                if len(self.pending_requests) > self.max_pending_requests:
                    # Remove lowest priority request
                    self.pending_requests.sort(key=lambda r: (r.priority.value, r.urgency), reverse=True)
                    removed = self.pending_requests.pop()
                    logging.debug(f"[AttentionManager] 🗑️ Dropped low priority request: {removed.content[:30]}...")
        
        logging.debug(f"[AttentionManager] 📥 Attention requested: {source} - {content[:50]}...")
        return request_id
    
    def release_attention(self, request_id: str):
        """
        Release attention for a completed request
        
        Args:
            request_id: ID of the request to release
        """
        with self.lock:
            # Find and remove from active requests
            for i, request in enumerate(self.active_requests):
                if request.id == request_id:
                    request.completed_time = datetime.now()
                    request.actual_duration = (request.completed_time - request.started_time).total_seconds()
                    
                    # Release capacity
                    capacity_used = self._calculate_capacity_usage(request)
                    self.available_capacity = min(1.0, self.available_capacity + capacity_used)
                    
                    # Move to completed
                    self.completed_requests.append(request)
                    self.active_requests.pop(i)
                    
                    logging.debug(f"[AttentionManager] ✅ Released attention: {request.content[:30]}...")
                    break
        
        # Try to process pending requests
        self._process_pending_requests()
    
    def focus_on(self, target: str, source: str, content: str = "",
                focus_type: AttentionType = AttentionType.FOCUSED,
                intensity: float = 0.8,
                duration: float = 60.0,
                context: Dict[str, Any] = None) -> bool:
        """
        Focus attention on a specific target
        
        Args:
            target: What to focus on
            source: Source requesting focus
            content: Details about focus target
            focus_type: Type of focus
            intensity: Focus intensity (0.0 to 1.0)
            duration: Expected focus duration
            context: Additional context
            
        Returns:
            True if focus was successfully established
        """
        # Check if we can establish focus
        if self.cognitive_load > 0.8:
            logging.warning(f"[AttentionManager] ⚠️ Cannot focus - cognitive overload")
            return False
        
        # End current focus if any
        if self.current_focus:
            self._end_current_focus("new_focus_requested")
        
        # Create new focus
        new_focus = AttentionFocus(
            target=target,
            source=source,
            content=content,
            focus_type=focus_type,
            intensity=intensity,
            expected_duration=duration,
            context=context or {}
        )
        
        # Calculate focus characteristics
        new_focus.depth = min(1.0, intensity * (1.0 - self.attention_fatigue))
        new_focus.stability = self.focus_stability * (1.0 - self.distractibility)
        new_focus.cognitive_load = self._calculate_focus_cognitive_load(new_focus)
        
        with self.lock:
            self.current_focus = new_focus
            self.attention_switches += 1
            
            # Update cognitive load
            self.cognitive_load = min(1.0, self.cognitive_load + new_focus.cognitive_load)
            
            # Update state
            if self.state != AttentionState.OVERLOADED:
                self.state = AttentionState.FOCUSED
        
        # Trigger event
        self._trigger_event('focus_started', {
            'target': target,
            'source': source,
            'intensity': intensity,
            'expected_duration': duration,
            'timestamp': datetime.now()
        })
        
        logging.info(f"[AttentionManager] 🎯 Focused on: {target} (intensity: {intensity:.2f})")
        return True
    
    def interrupt_focus(self, source: str, reason: str, 
                       priority: AttentionPriority = AttentionPriority.MEDIUM) -> bool:
        """
        Attempt to interrupt current focus
        
        Args:
            source: Source of interruption
            reason: Reason for interruption
            priority: Priority of interruption
            
        Returns:
            True if interruption was allowed
        """
        if not self.current_focus:
            return True  # No current focus to interrupt
        
        # Calculate interruption probability
        interruption_chance = self._calculate_interruption_chance(priority, reason)
        
        if random.random() < interruption_chance:
            # Allow interruption
            self.current_focus.interruption_count += 1
            
            # Reduce focus stability
            self.current_focus.stability *= 0.8
            
            # Trigger event
            self._trigger_event('focus_interrupted', {
                'source': source,
                'reason': reason,
                'priority': priority.value,
                'focus_target': self.current_focus.target,
                'timestamp': datetime.now()
            })
            
            logging.info(f"[AttentionManager] ⚡ Focus interrupted by {source}: {reason}")
            return True
        else:
            logging.debug(f"[AttentionManager] 🛡️ Interruption blocked: {reason}")
            return False
    
    def get_attention_summary(self) -> Dict[str, Any]:
        """
        Get summary of current attention state
        
        Returns:
            Attention state summary
        """
        with self.lock:
            current_focus_info = None
            if self.current_focus:
                current_focus_info = {
                    'target': self.current_focus.target,
                    'source': self.current_focus.source,
                    'intensity': self.current_focus.intensity,
                    'depth': self.current_focus.depth,
                    'stability': self.current_focus.stability,
                    'duration_so_far': (datetime.now() - self.current_focus.start_time).total_seconds(),
                    'expected_duration': self.current_focus.expected_duration,
                    'interruption_count': self.current_focus.interruption_count
                }
            
            return {
                'state': self.state.value,
                'current_focus': current_focus_info,
                'attention_capacity': self.attention_capacity,
                'available_capacity': self.available_capacity,
                'cognitive_load': self.cognitive_load,
                'focus_stability': self.focus_stability,
                'distractibility': self.distractibility,
                'attention_fatigue': self.attention_fatigue,
                'pending_requests': len(self.pending_requests),
                'active_requests': len(self.active_requests),
                'attention_switches': self.attention_switches,
                'total_focus_time': self.total_focus_time
            }
    
    def set_attention_state(self, new_state: AttentionState):
        """
        Set the attention state
        
        Args:
            new_state: New attention state
        """
        if new_state != self.state:
            old_state = self.state
            self.state = new_state
            
            # Adjust metrics based on state
            self._adjust_metrics_for_state(new_state)
            
            logging.info(f"[AttentionManager] 🔄 State changed: {old_state.value} → {new_state.value}")
    
    def adjust_distractibility(self, factor: float):
        """
        Adjust distractibility level
        
        Args:
            factor: Adjustment factor (0.0 to 1.0)
        """
        self.distractibility = max(0.0, min(1.0, self.distractibility * factor))
        logging.debug(f"[AttentionManager] 🎚️ Distractibility adjusted to: {self.distractibility:.3f}")
    
    def _attention_loop(self):
        """Main attention management loop"""
        logging.info("[AttentionManager] 🔄 Attention management loop started")
        
        last_update = time.time()
        
        while self.running:
            try:
                current_time = time.time()
                
                # Periodic updates
                if current_time - last_update > self.focus_update_interval:
                    self._update_attention_state()
                    self._process_pending_requests()
                    self._update_current_focus()
                    self._apply_attention_decay()
                    self._check_state_transitions()
                    last_update = current_time
                
                # Save state periodically
                if current_time % 300 < self.focus_update_interval:  # Every 5 minutes
                    self._save_attention_state()
                
                time.sleep(self.focus_update_interval)
                
            except Exception as e:
                logging.error(f"[AttentionManager] ❌ Attention loop error: {e}")
                time.sleep(self.focus_update_interval)
        
        logging.info("[AttentionManager] 🔄 Attention management loop ended")
    
    def _can_grant_immediately(self, request: AttentionRequest) -> bool:
        """Check if a request can be granted immediately"""
        # Check capacity
        capacity_needed = self._calculate_capacity_usage(request)
        if self.available_capacity < capacity_needed:
            return False
        
        # Check if this is high priority and should interrupt
        if request.priority in [AttentionPriority.CRITICAL, AttentionPriority.HIGH]:
            return True
        
        # Check current load
        if len(self.active_requests) >= self.max_concurrent_requests:
            return False
        
        return True
    
    def _grant_attention(self, request: AttentionRequest):
        """Grant attention to a request"""
        request.granted = True
        request.started_time = datetime.now()
        
        # Use capacity
        capacity_used = self._calculate_capacity_usage(request)
        self.available_capacity = max(0.0, self.available_capacity - capacity_used)
        
        # Add to active requests
        self.active_requests.append(request)
        
        # Update cognitive load
        self.cognitive_load = min(1.0, self.cognitive_load + request.complexity * 0.2)
        
        logging.debug(f"[AttentionManager] ✅ Granted attention: {request.content[:30]}...")
    
    def _calculate_capacity_usage(self, request: AttentionRequest) -> float:
        """Calculate how much attention capacity a request uses"""
        base_usage = 0.2  # Base capacity usage
        
        # Adjust based on attention type
        type_multipliers = {
            AttentionType.FOCUSED: 0.8,
            AttentionType.SELECTIVE: 0.4,
            AttentionType.DIVIDED: 0.6,
            AttentionType.SUSTAINED: 0.5,
            AttentionType.ALTERNATING: 0.7,
            AttentionType.AUTOMATIC: 0.1
        }
        
        type_usage = type_multipliers.get(request.attention_type, 0.4)
        
        # Adjust based on complexity and priority
        complexity_factor = request.complexity
        priority_factor = request.priority.value * 0.5
        
        total_usage = base_usage + type_usage + complexity_factor * 0.3 + priority_factor * 0.2
        return min(1.0, total_usage)
    
    def _calculate_novelty(self, content: str, source: str, context: Dict[str, Any]) -> float:
        """Calculate novelty score for content"""
        # Simple novelty calculation - could be more sophisticated
        novelty = 0.5
        
        # Check against recent requests
        recent_content = [r.content for r in self.completed_requests[-10:]]
        similar_count = sum(1 for rc in recent_content if any(word in content.lower() for word in rc.lower().split()))
        
        if similar_count > 0:
            novelty -= similar_count * 0.1
        
        # New sources are more novel
        recent_sources = [r.source for r in self.completed_requests[-20:]]
        if source not in recent_sources:
            novelty += 0.2
        
        return max(0.0, min(1.0, novelty))
    
    def _calculate_interruption_chance(self, priority: AttentionPriority, reason: str) -> float:
        """Calculate probability of allowing an interruption"""
        base_chance = 0.3
        
        # Priority affects interruption chance
        priority_bonus = priority.value * 0.4
        
        # Current focus stability affects resistance to interruption
        stability_resistance = self.current_focus.stability * 0.3 if self.current_focus else 0.0
        
        # Interruption tolerance
        tolerance_factor = self.interruption_tolerance * 0.3
        
        # Attention fatigue makes more susceptible to interruption
        fatigue_factor = self.attention_fatigue * 0.2
        
        interruption_chance = base_chance + priority_bonus + tolerance_factor + fatigue_factor - stability_resistance
        
        return max(0.0, min(1.0, interruption_chance))
    
    def _calculate_focus_cognitive_load(self, focus: AttentionFocus) -> float:
        """Calculate cognitive load for a focus"""
        base_load = 0.3
        
        # Intensity affects load
        intensity_load = focus.intensity * 0.4
        
        # Focus type affects load
        type_loads = {
            AttentionType.FOCUSED: 0.6,
            AttentionType.SELECTIVE: 0.3,
            AttentionType.DIVIDED: 0.8,
            AttentionType.SUSTAINED: 0.4,
            AttentionType.ALTERNATING: 0.7,
            AttentionType.AUTOMATIC: 0.1
        }
        
        type_load = type_loads.get(focus.focus_type, 0.4)
        
        return base_load + intensity_load + type_load
    
    def _process_pending_requests(self):
        """Process pending attention requests"""
        with self.lock:
            if not self.pending_requests:
                return
            
            # Sort by priority and urgency
            self.pending_requests.sort(
                key=lambda r: (r.priority.value, r.urgency, r.emotional_weight, r.novelty), 
                reverse=True
            )
            
            # Try to grant requests
            for request in list(self.pending_requests):
                if self._can_grant_immediately(request):
                    self.pending_requests.remove(request)
                    self._grant_attention(request)
                
                # Stop if we've reached capacity
                if len(self.active_requests) >= self.max_concurrent_requests:
                    break
    
    def _update_attention_state(self):
        """Update overall attention state"""
        # Calculate current load
        total_load = self.cognitive_load + (len(self.active_requests) * 0.1)
        
        # Update metrics based on load
        if total_load > 0.8:
            self.attention_fatigue = min(1.0, self.attention_fatigue + 0.02)
        else:
            self.attention_fatigue = max(0.0, self.attention_fatigue - 0.01)
        
        # Update distractibility based on fatigue
        self.distractibility = min(1.0, 0.3 + self.attention_fatigue * 0.4)
        
        # Update focus stability
        if self.current_focus:
            # Stability decreases with interruptions and fatigue
            stability_decay = 0.01 + (self.current_focus.interruption_count * 0.05) + (self.attention_fatigue * 0.02)
            self.current_focus.stability = max(0.2, self.current_focus.stability - stability_decay)
    
    def _update_current_focus(self):
        """Update current focus state"""
        if not self.current_focus:
            return
        
        # Update duration
        self.current_focus.actual_duration = (datetime.now() - self.current_focus.start_time).total_seconds()
        self.total_focus_time += self.focus_update_interval
        
        # Check if focus should end naturally
        if (self.current_focus.actual_duration > self.current_focus.expected_duration or
            self.current_focus.stability < 0.3):
            self._end_current_focus("natural_completion")
    
    def _end_current_focus(self, reason: str):
        """End the current focus"""
        if not self.current_focus:
            return
        
        # Record final duration
        self.current_focus.actual_duration = (datetime.now() - self.current_focus.start_time).total_seconds()
        
        # Reduce cognitive load
        self.cognitive_load = max(0.0, self.cognitive_load - self.current_focus.cognitive_load)
        
        # Add to history
        self.focus_history.append(self.current_focus)
        if len(self.focus_history) > 50:  # Keep last 50 focus sessions
            self.focus_history.pop(0)
        
        # Trigger event
        self._trigger_event('focus_ended', {
            'target': self.current_focus.target,
            'reason': reason,
            'duration': self.current_focus.actual_duration,
            'interruptions': self.current_focus.interruption_count,
            'timestamp': datetime.now()
        })
        
        logging.info(f"[AttentionManager] 🎯 Focus ended: {self.current_focus.target} ({reason})")
        
        # Clear current focus
        self.current_focus = None
        
        # Update state
        if self.state == AttentionState.FOCUSED:
            self.state = AttentionState.ALERT
    
    def _apply_attention_decay(self):
        """Apply natural decay to attention metrics"""
        # Cognitive load naturally decreases
        self.cognitive_load *= self.attention_decay_rate
        
        # Attention fatigue recovers slowly
        if len(self.active_requests) == 0 and not self.current_focus:
            self.attention_fatigue = max(0.0, self.attention_fatigue - 0.01)
        
        # Available capacity recovers
        if self.available_capacity < self.attention_capacity:
            self.available_capacity = min(self.attention_capacity, 
                                        self.available_capacity + 0.05)
    
    def _check_state_transitions(self):
        """Check for attention state transitions"""
        current_load = self.cognitive_load + (len(self.active_requests) * 0.1)
        
        if current_load > 0.9:
            if self.state != AttentionState.OVERLOADED:
                self.set_attention_state(AttentionState.OVERLOADED)
                self._trigger_event('attention_overload', {
                    'cognitive_load': self.cognitive_load,
                    'active_requests': len(self.active_requests),
                    'timestamp': datetime.now()
                })
        
        elif self.attention_fatigue > 0.7:
            if self.state != AttentionState.FATIGUED:
                self.set_attention_state(AttentionState.FATIGUED)
        
        elif self.distractibility > 0.6:
            if self.state not in [AttentionState.OVERLOADED, AttentionState.FATIGUED]:
                self.set_attention_state(AttentionState.DISTRACTED)
        
        elif self.current_focus and self.current_focus.depth > 0.7:
            if self.state != AttentionState.FOCUSED:
                self.set_attention_state(AttentionState.FOCUSED)
        
        elif current_load < 0.3 and self.attention_fatigue < 0.3:
            if self.state not in [AttentionState.FOCUSED]:
                self.set_attention_state(AttentionState.RELAXED)
        
        else:
            if self.state in [AttentionState.OVERLOADED, AttentionState.FATIGUED, AttentionState.DISTRACTED]:
                self.set_attention_state(AttentionState.ALERT)
    
    def _adjust_metrics_for_state(self, state: AttentionState):
        """Adjust metrics based on attention state"""
        if state == AttentionState.OVERLOADED:
            self.distractibility = min(1.0, self.distractibility + 0.2)
            self.focus_stability = max(0.2, self.focus_stability - 0.2)
        
        elif state == AttentionState.FATIGUED:
            self.attention_capacity = max(0.5, self.attention_capacity - 0.1)
            self.focus_stability = max(0.3, self.focus_stability - 0.1)
        
        elif state == AttentionState.FOCUSED:
            self.distractibility = max(0.1, self.distractibility - 0.1)
            self.focus_stability = min(1.0, self.focus_stability + 0.1)
        
        elif state == AttentionState.RELAXED:
            self.attention_capacity = min(1.0, self.attention_capacity + 0.05)
            self.attention_fatigue = max(0.0, self.attention_fatigue - 0.05)
    
    def _trigger_event(self, event_type: str, event_data: Dict[str, Any]):
        """Trigger attention event callbacks"""
        callbacks = self.event_callbacks.get(event_type, [])
        for callback in callbacks:
            try:
                callback(event_data)
            except Exception as e:
                logging.error(f"[AttentionManager] ❌ Event callback error: {e}")
    
    def _save_attention_state(self):
        """Save attention state to persistent storage"""
        try:
            # Save only essential state information
            current_focus_data = None
            if self.current_focus:
                current_focus_data = {
                    'target': self.current_focus.target,
                    'source': self.current_focus.source,
                    'content': self.current_focus.content,
                    'focus_type': self.current_focus.focus_type.value,
                    'intensity': self.current_focus.intensity,
                    'start_time': self.current_focus.start_time.isoformat(),
                    'expected_duration': self.current_focus.expected_duration,
                    'depth': self.current_focus.depth,
                    'stability': self.current_focus.stability,
                    'cognitive_load': self.current_focus.cognitive_load,
                    'interruption_count': self.current_focus.interruption_count
                }
            
            data = {
                'attention_state': {
                    'state': self.state.value,
                    'attention_capacity': self.attention_capacity,
                    'available_capacity': self.available_capacity,
                    'current_focus': current_focus_data
                },
                'metrics': {
                    'focus_stability': self.focus_stability,
                    'distractibility': self.distractibility,
                    'cognitive_load': self.cognitive_load,
                    'attention_fatigue': self.attention_fatigue,
                    'novelty_bias': self.novelty_bias,
                    'interruption_tolerance': self.interruption_tolerance
                },
                'statistics': {
                    'attention_switches': self.attention_switches,
                    'total_focus_time': self.total_focus_time,
                    'pending_requests': len(self.pending_requests),
                    'active_requests': len(self.active_requests),
                    'completed_requests': len(self.completed_requests)
                },
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.save_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            logging.debug("[AttentionManager] 💾 Attention state saved")
            
        except Exception as e:
            logging.error(f"[AttentionManager] ❌ Failed to save attention state: {e}")
    
    def _load_attention_state(self):
        """Load attention state from persistent storage"""
        try:
            if self.save_path.exists():
                with open(self.save_path, 'r') as f:
                    data = json.load(f)
                
                # Load attention state
                if 'attention_state' in data:
                    as_data = data['attention_state']
                    try:
                        self.state = AttentionState(as_data.get('state', 'alert'))
                    except ValueError:
                        self.state = AttentionState.ALERT
                    
                    self.attention_capacity = as_data.get('attention_capacity', 1.0)
                    self.available_capacity = as_data.get('available_capacity', 1.0)
                
                # Load metrics
                if 'metrics' in data:
                    m = data['metrics']
                    self.focus_stability = m.get('focus_stability', 0.7)
                    self.distractibility = m.get('distractibility', 0.3)
                    self.cognitive_load = m.get('cognitive_load', 0.4)
                    self.attention_fatigue = m.get('attention_fatigue', 0.2)
                    self.novelty_bias = m.get('novelty_bias', 0.4)
                    self.interruption_tolerance = m.get('interruption_tolerance', 0.6)
                
                # Load statistics
                if 'statistics' in data:
                    s = data['statistics']
                    self.attention_switches = s.get('attention_switches', 0)
                    self.total_focus_time = s.get('total_focus_time', 0.0)
                
                logging.info("[AttentionManager] 📂 Attention state loaded from storage")
            
        except Exception as e:
            logging.error(f"[AttentionManager] ❌ Failed to load attention state: {e}")
    
    def subscribe_to_event(self, event_type: str, callback: Callable):
        """Subscribe to attention events"""
        if event_type in self.event_callbacks:
            self.event_callbacks[event_type].append(callback)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get attention manager statistics"""
        return {
            'state': self.state.value,
            'current_focus': self.current_focus.target if self.current_focus else None,
            'attention_capacity': round(self.attention_capacity, 3),
            'available_capacity': round(self.available_capacity, 3),
            'cognitive_load': round(self.cognitive_load, 3),
            'focus_stability': round(self.focus_stability, 3),
            'distractibility': round(self.distractibility, 3),
            'attention_fatigue': round(self.attention_fatigue, 3),
            'pending_requests': len(self.pending_requests),
            'active_requests': len(self.active_requests),
            'attention_switches': self.attention_switches,
            'total_focus_time': round(self.total_focus_time, 1),
            'interruption_tolerance': round(self.interruption_tolerance, 3)
        }

# Global instance
attention_manager = AttentionManager()