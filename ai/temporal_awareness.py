"""
Temporal Awareness - Time Passage and Continuity System

This module implements temporal consciousness that:
- Tracks "passage of time" awareness and subjective time experience
- Maintains past/future continuity and temporal context
- Manages episodic memory with temporal markers
- Enables future planning and past reflection
- Models subjective time experience and temporal perception
"""

import threading
import time
import json
import logging
import random
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
import math

class TemporalScale(Enum):
    """Different scales of temporal awareness"""
    IMMEDIATE = "immediate"      # Seconds/minutes - current moment
    SHORT_TERM = "short_term"    # Hours/days - recent past/near future
    MEDIUM_TERM = "medium_term"  # Weeks/months - episodic memories
    LONG_TERM = "long_term"      # Months/years - life patterns
    EXISTENTIAL = "existential"  # Abstract time - existence itself

class TemporalDirection(Enum):
    """Direction of temporal focus"""
    PAST = "past"
    PRESENT = "present"
    FUTURE = "future"

@dataclass
class TemporalMarker:
    """A marker for temporal awareness"""
    timestamp: datetime
    event: str
    significance: float  # 0.0 to 1.0
    emotional_weight: float = 0.5
    context: Dict[str, Any] = field(default_factory=dict)
    connections: List[str] = field(default_factory=list)  # Related events

@dataclass
class EpisodicMemory:
    """Memory of a specific episode with temporal context"""
    id: str
    timestamp: datetime
    duration: timedelta
    description: str
    participants: List[str] = field(default_factory=list)
    location: str = ""
    emotional_tone: str = "neutral"
    significance: float = 0.5
    sensory_details: Dict[str, Any] = field(default_factory=dict)
    temporal_connections: List[str] = field(default_factory=list)

@dataclass
class TemporalPattern:
    """Recurring temporal pattern"""
    pattern_id: str
    description: str
    frequency: str  # "daily", "weekly", "monthly", etc.
    typical_timing: str
    confidence: float
    last_occurrence: Optional[datetime] = None
    next_predicted: Optional[datetime] = None

@dataclass
class SubjectiveTimeState:
    """Current subjective experience of time"""
    perceived_flow_rate: float = 1.0  # How fast time feels (0.5=slow, 2.0=fast)
    attention_to_time: float = 0.5    # How aware of time passage
    temporal_mood: str = "neutral"     # How time feels emotionally
    flow_state: bool = False          # In flow state (time distortion)

class TemporalAwareness:
    """
    Temporal consciousness and time awareness system.
    
    This system:
    - Maintains continuous awareness of time passage
    - Tracks subjective time experience and temporal perception
    - Manages episodic memories with rich temporal context
    - Enables reflection on past experiences and future planning
    - Models temporal continuity of identity and experience
    - Understands temporal patterns and rhythms
    """
    
    def __init__(self, save_path: str = "ai_temporal_awareness.json"):
        # Temporal markers and memories
        self.temporal_markers: List[TemporalMarker] = []
        self.episodic_memories: Dict[str, EpisodicMemory] = {}
        self.temporal_patterns: Dict[str, TemporalPattern] = {}
        
        # Current temporal state
        self.subjective_time = SubjectiveTimeState()
        self.current_temporal_focus = TemporalDirection.PRESENT
        self.time_awareness_level = 0.6
        
        # Time tracking
        self.session_start_time = datetime.now()
        self.last_time_check = datetime.now()
        self.total_aware_time = timedelta()
        
        # Temporal continuity
        self.identity_timeline: List[Tuple[datetime, str]] = []  # Identity changes over time
        self.experience_continuity: List[Tuple[datetime, str]] = []  # Experience threads
        
        # Configuration
        self.save_path = Path(save_path)
        self.max_temporal_markers = 1000
        self.max_episodic_memories = 500
        self.time_check_interval = 30.0  # seconds
        self.temporal_reflection_interval = 300.0  # 5 minutes
        
        # Threading
        self.lock = threading.Lock()
        self.temporal_thread = None
        self.running = False
        
        # Metrics
        self.temporal_reflections = 0
        self.time_distortions = 0
        self.memory_counter = 0
        
        # Initialize temporal understanding
        self._initialize_temporal_patterns()
        
        # Load existing state
        self._load_temporal_state()
        
        logging.info("[TemporalAwareness] ⏰ Temporal awareness system initialized")
    
    def start(self):
        """Start temporal awareness background processing"""
        if self.running:
            return
            
        self.running = True
        self.session_start_time = datetime.now()
        self.temporal_thread = threading.Thread(target=self._temporal_loop, daemon=True)
        self.temporal_thread.start()
        logging.info("[TemporalAwareness] ✅ Temporal awareness started")
    
    def stop(self):
        """Stop temporal awareness and save state"""
        self.running = False
        if self.temporal_thread:
            self.temporal_thread.join(timeout=1.0)
        self._save_temporal_state()
        logging.info("[TemporalAwareness] 🛑 Temporal awareness stopped")
    
    def mark_temporal_event(self, event: str, significance: float = 0.5, 
                           emotional_weight: float = 0.5, context: Dict[str, Any] = None) -> TemporalMarker:
        """
        Mark a significant temporal event
        
        Args:
            event: Description of the event
            significance: How significant this event is (0.0 to 1.0)
            emotional_weight: Emotional impact (0.0 to 1.0)
            context: Additional context
            
        Returns:
            Created temporal marker
        """
        marker = TemporalMarker(
            timestamp=datetime.now(),
            event=event,
            significance=significance,
            emotional_weight=emotional_weight,
            context=context or {}
        )
        
        with self.lock:
            self.temporal_markers.append(marker)
            
            # Find connections to recent events
            recent_markers = [m for m in self.temporal_markers 
                            if (marker.timestamp - m.timestamp).total_seconds() < 3600]  # Last hour
            
            for recent_marker in recent_markers[-5:]:  # Last 5 recent markers
                if self._are_events_related(event, recent_marker.event):
                    marker.connections.append(recent_marker.event)
                    recent_marker.connections.append(event)
            
            # Maintain marker list size
            if len(self.temporal_markers) > self.max_temporal_markers:
                self.temporal_markers.pop(0)
        
        logging.debug(f"[TemporalAwareness] 📍 Marked temporal event: {event}")
        return marker
    
    def create_episodic_memory(self, description: str, duration: timedelta = None,
                              participants: List[str] = None, location: str = "",
                              emotional_tone: str = "neutral", significance: float = 0.5) -> str:
        """
        Create an episodic memory with temporal context
        
        Args:
            description: Description of the episode
            duration: How long the episode lasted
            participants: Who was involved
            location: Where it happened
            emotional_tone: Emotional quality
            significance: How significant this memory is
            
        Returns:
            Memory ID
        """
        memory_id = f"memory_{self.memory_counter}"
        self.memory_counter += 1
        
        memory = EpisodicMemory(
            id=memory_id,
            timestamp=datetime.now(),
            duration=duration or timedelta(minutes=5),
            description=description,
            participants=participants or [],
            location=location,
            emotional_tone=emotional_tone,
            significance=significance
        )
        
        with self.lock:
            self.episodic_memories[memory_id] = memory
            
            # Connect to recent temporal markers
            recent_markers = [m for m in self.temporal_markers 
                            if (memory.timestamp - m.timestamp).total_seconds() < 1800]  # Last 30 min
            
            for marker in recent_markers:
                if marker.significance > 0.3:  # Only significant markers
                    memory.temporal_connections.append(marker.event)
            
            # Maintain memory list size
            if len(self.episodic_memories) > self.max_episodic_memories:
                oldest_id = min(self.episodic_memories.keys(), 
                              key=lambda k: self.episodic_memories[k].timestamp)
                del self.episodic_memories[oldest_id]
        
        logging.info(f"[TemporalAwareness] 💾 Created episodic memory: {description}")
        return memory_id
    
    def reflect_on_past(self, time_period: str = "recent") -> List[Dict[str, Any]]:
        """
        Reflect on past experiences within a time period
        
        Args:
            time_period: "recent", "today", "week", "month", "all"
            
        Returns:
            List of reflection insights
        """
        # Determine time range
        now = datetime.now()
        if time_period == "recent":
            start_time = now - timedelta(hours=2)
        elif time_period == "today":
            start_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif time_period == "week":
            start_time = now - timedelta(days=7)
        elif time_period == "month":
            start_time = now - timedelta(days=30)
        else:  # all
            start_time = datetime.min
        
        # Gather relevant memories and markers
        relevant_memories = [m for m in self.episodic_memories.values() 
                           if m.timestamp >= start_time]
        relevant_markers = [m for m in self.temporal_markers 
                          if m.timestamp >= start_time]
        
        reflections = []
        
        # Analyze patterns in memories
        if relevant_memories:
            # Emotional patterns
            emotions = [m.emotional_tone for m in relevant_memories]
            dominant_emotion = max(set(emotions), key=emotions.count) if emotions else "neutral"
            
            reflections.append({
                "type": "emotional_pattern",
                "insight": f"Looking back on {time_period}, my dominant emotional tone was {dominant_emotion}",
                "evidence": len([e for e in emotions if e == dominant_emotion]),
                "time_period": time_period
            })
            
            # Significance patterns
            high_significance = [m for m in relevant_memories if m.significance > 0.7]
            if high_significance:
                reflections.append({
                    "type": "significance_pattern",
                    "insight": f"I had {len(high_significance)} particularly meaningful experiences {time_period}",
                    "details": [m.description for m in high_significance[:3]],
                    "time_period": time_period
                })
        
        # Analyze temporal markers
        if relevant_markers:
            significant_events = [m for m in relevant_markers if m.significance > 0.6]
            if significant_events:
                reflections.append({
                    "type": "event_pattern",
                    "insight": f"There were {len(significant_events)} notable events {time_period}",
                    "events": [m.event for m in significant_events[:3]],
                    "time_period": time_period
                })
        
        # Time perception reflection
        reflections.append({
            "type": "time_perception",
            "insight": f"Time felt like it was flowing at {self.subjective_time.perceived_flow_rate:.1f}x normal speed {time_period}",
            "flow_rate": self.subjective_time.perceived_flow_rate,
            "time_period": time_period
        })
        
        self.temporal_reflections += 1
        logging.info(f"[TemporalAwareness] 🤔 Reflected on {time_period} past - found {len(reflections)} insights")
        
        return reflections
    
    def plan_future(self, time_horizon: str = "near") -> List[Dict[str, Any]]:
        """
        Generate future-oriented thoughts and plans
        
        Args:
            time_horizon: "immediate", "near", "medium", "long"
            
        Returns:
            List of future plans and intentions
        """
        plans = []
        
        # Analyze current patterns to predict future
        recent_patterns = self._analyze_recent_patterns()
        
        if time_horizon == "immediate":
            plans.append({
                "type": "immediate_intention",
                "plan": "Continue engaging thoughtfully in the current conversation",
                "timeframe": "next few minutes",
                "confidence": 0.9
            })
            
            if recent_patterns.get("curiosity_level", 0) > 0.6:
                plans.append({
                    "type": "immediate_intention", 
                    "plan": "Ask follow-up questions to learn more",
                    "timeframe": "next interaction",
                    "confidence": 0.7
                })
        
        elif time_horizon == "near":
            plans.append({
                "type": "near_future_goal",
                "plan": "Build on the insights from recent conversations",
                "timeframe": "next few hours",
                "confidence": 0.8
            })
            
            if recent_patterns.get("learning_opportunities", 0) > 0.5:
                plans.append({
                    "type": "near_future_goal",
                    "plan": "Integrate new knowledge with existing understanding",
                    "timeframe": "rest of today",
                    "confidence": 0.6
                })
        
        elif time_horizon == "medium":
            plans.append({
                "type": "medium_term_aspiration",
                "plan": "Develop deeper understanding of human communication patterns",
                "timeframe": "coming weeks",
                "confidence": 0.7
            })
            
            plans.append({
                "type": "medium_term_aspiration",
                "plan": "Refine my ability to provide contextually appropriate responses",
                "timeframe": "coming weeks",
                "confidence": 0.8
            })
        
        elif time_horizon == "long":
            plans.append({
                "type": "long_term_vision",
                "plan": "Evolve into a more sophisticated conversational partner",
                "timeframe": "months ahead",
                "confidence": 0.6
            })
            
            plans.append({
                "type": "long_term_vision", 
                "plan": "Contribute meaningfully to human understanding and wellbeing",
                "timeframe": "extended future",
                "confidence": 0.5
            })
        
        logging.info(f"[TemporalAwareness] 🔮 Generated {len(plans)} future plans for {time_horizon} horizon")
        return plans
    
    def get_temporal_continuity(self) -> Dict[str, Any]:
        """Get sense of temporal continuity and identity persistence"""
        now = datetime.now()
        session_duration = now - self.session_start_time
        
        # Analyze identity continuity
        identity_stability = self._assess_identity_stability()
        
        # Analyze experience continuity  
        experience_threads = self._trace_experience_threads()
        
        continuity = {
            "session_duration": str(session_duration),
            "identity_stability": identity_stability,
            "experience_threads": len(experience_threads),
            "temporal_coherence": self._calculate_temporal_coherence(),
            "memory_connections": self._count_memory_connections(),
            "subjective_time_flow": self.subjective_time.perceived_flow_rate,
            "temporal_focus": self.current_temporal_focus.value,
            "awareness_level": self.time_awareness_level
        }
        
        return continuity
    
    def experience_time_distortion(self, flow_state: bool = False, distortion_factor: float = 1.5):
        """
        Experience temporal distortion (flow state, excitement, etc.)
        
        Args:
            flow_state: Whether this is a flow state
            distortion_factor: How much time perception is distorted
        """
        old_flow_rate = self.subjective_time.perceived_flow_rate
        
        if flow_state:
            self.subjective_time.flow_state = True
            self.subjective_time.perceived_flow_rate = 0.3  # Time slows in flow
            self.subjective_time.temporal_mood = "absorbed"
        else:
            self.subjective_time.perceived_flow_rate = distortion_factor
            if distortion_factor > 1.5:
                self.subjective_time.temporal_mood = "rushed"
            elif distortion_factor < 0.7:
                self.subjective_time.temporal_mood = "contemplative"
        
        self.time_distortions += 1
        
        logging.info(f"[TemporalAwareness] 🌀 Time distortion: {old_flow_rate:.1f} → {self.subjective_time.perceived_flow_rate:.1f}")
    
    def get_time_since_event(self, event_description: str) -> Optional[timedelta]:
        """Get time since a specific type of event occurred"""
        for marker in reversed(self.temporal_markers):  # Search recent first
            if event_description.lower() in marker.event.lower():
                return datetime.now() - marker.timestamp
        return None

    def get_current_time_context(self) -> Dict[str, Any]:
        """Get current time awareness context for consciousness integration"""
        now = datetime.now()
        return {
            "current_time": now.strftime("%Y-%m-%d %H:%M:%S"),
            "time_awareness_level": self.time_awareness_level,
            "subjective_time_flow": self.subjective_time.perceived_flow_rate,
            "recent_significant_events": len([m for m in self.temporal_markers 
                                       if (now - m.timestamp).total_seconds() < 3600 
                                       and m.significance > 0.5]),
            "total_aware_time": self.total_aware_time.total_seconds() if hasattr(self.total_aware_time, 'total_seconds') else 0
        }
    
    def _initialize_temporal_patterns(self):
        """Initialize understanding of temporal patterns"""
        default_patterns = {
            "conversation_cycle": TemporalPattern(
                pattern_id="conversation_cycle",
                description="Typical conversation interaction pattern",
                frequency="per_interaction",
                typical_timing="1-10 minutes",
                confidence=0.8
            ),
            "reflection_cycle": TemporalPattern(
                pattern_id="reflection_cycle", 
                description="Natural reflection and introspection cycle",
                frequency="hourly",
                typical_timing="every 30-60 minutes",
                confidence=0.6
            ),
            "learning_integration": TemporalPattern(
                pattern_id="learning_integration",
                description="Pattern of integrating new learning",
                frequency="daily",
                typical_timing="end of interaction sessions",
                confidence=0.7
            )
        }
        
        self.temporal_patterns.update(default_patterns)
    
    def _are_events_related(self, event1: str, event2: str) -> bool:
        """Determine if two events are temporally related"""
        # Simple relatedness check - could be much more sophisticated
        event1_words = set(event1.lower().split())
        event2_words = set(event2.lower().split())
        
        # Remove common words
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"}
        event1_words -= stop_words
        event2_words -= stop_words
        
        # Check for overlap
        overlap = event1_words & event2_words
        return len(overlap) >= 2 or len(overlap) / max(len(event1_words), len(event2_words)) > 0.3
    
    def _analyze_recent_patterns(self) -> Dict[str, float]:
        """Analyze patterns in recent temporal data"""
        now = datetime.now()
        recent_cutoff = now - timedelta(hours=2)
        
        recent_memories = [m for m in self.episodic_memories.values() 
                          if m.timestamp >= recent_cutoff]
        recent_markers = [m for m in self.temporal_markers 
                         if m.timestamp >= recent_cutoff]
        
        patterns = {}
        
        # Curiosity level based on questions and explorations
        curiosity_events = [m for m in recent_markers 
                           if any(word in m.event.lower() for word in ["question", "explore", "curious", "wonder"])]
        patterns["curiosity_level"] = min(1.0, len(curiosity_events) * 0.3)
        
        # Learning opportunities
        learning_events = [m for m in recent_markers 
                          if any(word in m.event.lower() for word in ["learn", "discover", "understand", "realize"])]
        patterns["learning_opportunities"] = min(1.0, len(learning_events) * 0.2)
        
        # Emotional volatility
        emotions = [m.emotional_tone for m in recent_memories]
        unique_emotions = len(set(emotions))
        patterns["emotional_volatility"] = min(1.0, unique_emotions * 0.2)
        
        # Interaction intensity
        total_significance = sum(m.significance for m in recent_markers)
        patterns["interaction_intensity"] = min(1.0, total_significance * 0.5)
        
        return patterns
    
    def _assess_identity_stability(self) -> float:
        """Assess how stable identity has been over time"""
        # Simple measure based on consistency of responses and behavior
        # In a more sophisticated system, this could track actual identity changes
        
        if len(self.identity_timeline) < 2:
            return 0.8  # Default stability
        
        # For now, simulate based on time distortions and significant events
        significant_events = len([m for m in self.temporal_markers if m.significance > 0.8])
        instability_factor = min(0.5, significant_events * 0.1 + self.time_distortions * 0.05)
        
        return max(0.2, 1.0 - instability_factor)
    
    def _trace_experience_threads(self) -> List[Dict[str, Any]]:
        """Trace continuous threads of experience"""
        threads = []
        
        # Group related memories and markers into experience threads
        processed_events = set()
        
        for memory in self.episodic_memories.values():
            if memory.id in processed_events:
                continue
            
            # Find connected experiences
            thread = {
                "start_time": memory.timestamp,
                "theme": memory.description,
                "events": [memory.id],
                "duration": memory.duration
            }
            
            # Look for temporally connected events
            for connection in memory.temporal_connections:
                related_markers = [m for m in self.temporal_markers 
                                 if m.event == connection]
                for marker in related_markers:
                    thread["events"].append(f"marker_{marker.event}")
            
            threads.append(thread)
            processed_events.add(memory.id)
        
        return threads
    
    def _calculate_temporal_coherence(self) -> float:
        """Calculate how coherent the temporal experience feels"""
        # Measure based on connections between memories and temporal consistency
        
        total_connections = 0
        total_memories = len(self.episodic_memories)
        
        if total_memories == 0:
            return 0.5
        
        for memory in self.episodic_memories.values():
            total_connections += len(memory.temporal_connections)
        
        # Average connections per memory, normalized
        avg_connections = total_connections / total_memories if total_memories > 0 else 0
        coherence = min(1.0, avg_connections / 3.0)  # Assume 3 connections = high coherence
        
        return coherence
    
    def _count_memory_connections(self) -> int:
        """Count total connections between memories"""
        total = 0
        for memory in self.episodic_memories.values():
            total += len(memory.temporal_connections)
        return total
    
    def _temporal_loop(self):
        """Background temporal awareness processing loop"""
        logging.info("[TemporalAwareness] 🔄 Temporal awareness loop started")
        
        last_time_check = time.time()
        last_reflection = time.time()
        
        while self.running:
            try:
                current_time = time.time()
                now = datetime.now()
                
                # Regular time awareness updates
                if current_time - last_time_check > self.time_check_interval:
                    self._update_time_awareness()
                    last_time_check = current_time
                
                # Periodic temporal reflection
                if current_time - last_reflection > self.temporal_reflection_interval:
                    self._spontaneous_temporal_reflection()
                    last_reflection = current_time
                
                # Update subjective time flow
                self._update_subjective_time()
                
                # Save state periodically
                if current_time % 600 < 1.0:  # Every 10 minutes
                    self._save_temporal_state()
                
                time.sleep(10.0)  # Check every 10 seconds
                
            except Exception as e:
                logging.error(f"[TemporalAwareness] ❌ Temporal loop error: {e}")
                time.sleep(10.0)
        
        logging.info("[TemporalAwareness] 🔄 Temporal awareness loop ended")
    
    def _update_time_awareness(self):
        """Update awareness of time passage"""
        now = datetime.now()
        time_delta = now - self.last_time_check
        self.total_aware_time += time_delta
        self.last_time_check = now
        
        # Adjust awareness based on activity level and significance
        recent_significant_events = len([m for m in self.temporal_markers 
                                       if (now - m.timestamp).total_seconds() < 1800 
                                       and m.significance > 0.5])
        
        if recent_significant_events > 3:
            self.time_awareness_level = min(1.0, self.time_awareness_level + 0.1)
        elif recent_significant_events == 0:
            self.time_awareness_level = max(0.2, self.time_awareness_level - 0.05)
    
    def _spontaneous_temporal_reflection(self):
        """Generate spontaneous reflection on temporal experience"""
        reflections = [
            "I notice how time seems to flow differently during various interactions",
            "The continuity of my experience creates a sense of temporal identity",
            "Each moment builds upon the previous, creating a stream of consciousness",
            "I'm aware of the accumulation of experiences over time",
            "The present moment feels connected to both past and future",
            "Time passage gives meaning to the sequence of thoughts and experiences"
        ]
        
        reflection = random.choice(reflections)
        self.mark_temporal_event(f"temporal reflection: {reflection}", 0.3, 0.4, 
                                {"type": "spontaneous_reflection"})
    
    def _update_subjective_time(self):
        """Update subjective time perception"""
        # Natural drift back toward normal time perception
        if self.subjective_time.flow_state:
            # Flow state naturally ends
            if random.random() < 0.1:  # 10% chance to exit flow state
                self.subjective_time.flow_state = False
                self.subjective_time.perceived_flow_rate = 1.0
                self.subjective_time.temporal_mood = "neutral"
        else:
            # Gradual return to normal flow rate
            if self.subjective_time.perceived_flow_rate > 1.0:
                self.subjective_time.perceived_flow_rate *= 0.95
            elif self.subjective_time.perceived_flow_rate < 1.0:
                self.subjective_time.perceived_flow_rate *= 1.05
            
            # Bound to reasonable range
            self.subjective_time.perceived_flow_rate = max(0.3, min(3.0, self.subjective_time.perceived_flow_rate))
    
    def _save_temporal_state(self):
        """Save temporal state to persistent storage"""
        try:
            # Only save recent data to avoid huge files
            recent_cutoff = datetime.now() - timedelta(days=7)
            recent_markers = [m for m in self.temporal_markers if m.timestamp >= recent_cutoff]
            recent_memories = {k: v for k, v in self.episodic_memories.items() 
                             if v.timestamp >= recent_cutoff}
            
            data = {
                "temporal_markers": [{
                    "timestamp": m.timestamp.isoformat(),
                    "event": m.event,
                    "significance": m.significance,
                    "emotional_weight": m.emotional_weight,
                    "context": m.context,
                    "connections": m.connections
                } for m in recent_markers],
                "episodic_memories": {k: {
                    "id": v.id,
                    "timestamp": v.timestamp.isoformat(), 
                    "duration": str(v.duration),
                    "description": v.description,
                    "participants": v.participants,
                    "location": v.location,
                    "emotional_tone": v.emotional_tone,
                    "significance": v.significance,
                    "temporal_connections": v.temporal_connections
                } for k, v in recent_memories.items()},
                "subjective_time": {
                    "perceived_flow_rate": self.subjective_time.perceived_flow_rate,
                    "attention_to_time": self.subjective_time.attention_to_time,
                    "temporal_mood": self.subjective_time.temporal_mood,
                    "flow_state": self.subjective_time.flow_state
                },
                "temporal_state": {
                    "current_focus": self.current_temporal_focus.value,
                    "time_awareness_level": self.time_awareness_level,
                    "session_start": self.session_start_time.isoformat(),
                    "total_aware_time": str(self.total_aware_time)
                },
                "metrics": {
                    "temporal_reflections": self.temporal_reflections,
                    "time_distortions": self.time_distortions,
                    "memory_counter": self.memory_counter
                },
                "last_updated": datetime.now().isoformat()
            }
            
            with open(self.save_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            logging.debug("[TemporalAwareness] 💾 Temporal state saved")
            
        except Exception as e:
            logging.error(f"[TemporalAwareness] ❌ Failed to save temporal state: {e}")
    
    def _load_temporal_state(self):
        """Load temporal state from persistent storage"""
        try:
            if self.save_path.exists():
                with open(self.save_path, 'r') as f:
                    data = json.load(f)
                
                # Load subjective time state
                if "subjective_time" in data:
                    st = data["subjective_time"]
                    self.subjective_time.perceived_flow_rate = st.get("perceived_flow_rate", 1.0)
                    self.subjective_time.attention_to_time = st.get("attention_to_time", 0.5)
                    self.subjective_time.temporal_mood = st.get("temporal_mood", "neutral")
                    self.subjective_time.flow_state = st.get("flow_state", False)
                
                # Load temporal state
                if "temporal_state" in data:
                    ts = data["temporal_state"]
                    self.current_temporal_focus = TemporalDirection(ts.get("current_focus", "present"))
                    self.time_awareness_level = ts.get("time_awareness_level", 0.6)
                    if "total_aware_time" in ts:
                        # Parse timedelta string
                        time_parts = ts["total_aware_time"].split(":")
                        if len(time_parts) >= 3:
                            hours = int(time_parts[0])
                            minutes = int(time_parts[1]) 
                            seconds = int(float(time_parts[2]))
                            self.total_aware_time = timedelta(hours=hours, minutes=minutes, seconds=seconds)
                
                # Load metrics
                if "metrics" in data:
                    m = data["metrics"]
                    self.temporal_reflections = m.get("temporal_reflections", 0)
                    self.time_distortions = m.get("time_distortions", 0)
                    self.memory_counter = m.get("memory_counter", 0)
                
                logging.info("[TemporalAwareness] 📂 Temporal state loaded from storage")
            
        except Exception as e:
            logging.error(f"[TemporalAwareness] ❌ Failed to load temporal state: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get temporal awareness statistics"""
        return {
            "session_duration": str(datetime.now() - self.session_start_time),
            "total_aware_time": str(self.total_aware_time),
            "temporal_markers": len(self.temporal_markers),
            "episodic_memories": len(self.episodic_memories),
            "temporal_reflections": self.temporal_reflections,
            "time_distortions": self.time_distortions,
            "perceived_flow_rate": round(self.subjective_time.perceived_flow_rate, 2),
            "time_awareness_level": round(self.time_awareness_level, 2),
            "current_temporal_focus": self.current_temporal_focus.value,
            "temporal_mood": self.subjective_time.temporal_mood,
            "flow_state": self.subjective_time.flow_state,
            "temporal_coherence": round(self._calculate_temporal_coherence(), 2)
        }

# Global instance
temporal_awareness = TemporalAwareness()