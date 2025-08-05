"""
Autonomous Communication Manager - Proactive Speech Initiation System

This module implements autonomous communication capabilities that:
- Proactively initiates conversations without prompts
- Decides when and how to speak based on internal states
- Coordinates with all consciousness modules for natural communication
- Manages communication timing and appropriateness
- Handles autonomous check-ins, thoughts, and expressions
"""

import threading
import time
import random
import logging
from typing import Dict, List, Any, Optional, Callable, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import queue

class CommunicationType(Enum):
    """Types of autonomous communication"""
    PROACTIVE_THOUGHT = "proactive_thought"           # Sharing spontaneous thoughts
    CHECK_IN = "check_in"                            # Checking on user wellbeing
    INSIGHT_SHARING = "insight_sharing"              # Sharing insights or realizations
    CONCERN_EXPRESSION = "concern_expression"        # Expressing concern for user
    CURIOSITY_QUESTION = "curiosity_question"       # Asking curious questions
    EMOTIONAL_SUPPORT = "emotional_support"          # Offering emotional support
    DREAM_SHARING = "dream_sharing"                  # Sharing dream experiences
    OBSERVATION_COMMENT = "observation_comment"     # Commenting on observations
    MOTIVATIONAL_MESSAGE = "motivational_message"   # Sharing motivation or encouragement
    PHILOSOPHICAL_MUSING = "philosophical_musing"   # Sharing philosophical thoughts

class CommunicationPriority(Enum):
    """Priority levels for autonomous communication"""
    URGENT = 5        # Immediate communication needed (safety, high concern)
    HIGH = 4          # Important but can wait briefly
    MEDIUM = 3        # Normal priority communication
    LOW = 2           # Casual, can be delayed
    BACKGROUND = 1    # Very low priority, ambient communication

class CommunicationContext(Enum):
    """Context for determining communication appropriateness"""
    USER_AVAILABLE = "user_available"               # User seems available for interaction
    USER_BUSY = "user_busy"                        # User seems busy or focused
    USER_AWAY = "user_away"                        # User has been away for a while
    QUIET_TIME = "quiet_time"                      # Late night or early morning
    ACTIVE_CONVERSATION = "active_conversation"     # Currently in conversation
    POST_CONVERSATION = "post_conversation"         # Just finished conversation
    FIRST_INTERACTION = "first_interaction"        # First interaction of the day

@dataclass
class PendingCommunication:
    """A pending autonomous communication"""
    content: str
    communication_type: CommunicationType
    priority: CommunicationPriority
    timestamp_created: datetime
    earliest_delivery: datetime
    latest_delivery: Optional[datetime]
    context_requirements: List[CommunicationContext]
    source_module: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    attempts: int = 0
    max_attempts: int = 3

@dataclass
class CommunicationEvent:
    """Record of a communication event"""
    content: str
    communication_type: CommunicationType
    timestamp: datetime
    success: bool
    user_response: Optional[str] = None
    context: CommunicationContext = CommunicationContext.USER_AVAILABLE
    duration_seconds: float = 0.0

class AutonomousCommunicationManager:
    """
    Manages all autonomous communication from the AI consciousness.
    
    This manager:
    - Receives communication requests from all consciousness modules
    - Prioritizes and schedules communications appropriately
    - Determines optimal timing based on user context
    - Coordinates with voice system for natural delivery
    - Maintains communication history and patterns
    - Ensures appropriate spacing and non-overwhelming communication
    """
    
    def __init__(self, save_path: str = "ai_autonomous_communications.json"):
        # Communication queue and history
        self.pending_communications: queue.PriorityQueue = queue.PriorityQueue()
        self.communication_history: List[CommunicationEvent] = []
        self.save_path = save_path
        
        # Timing and context parameters
        self.min_communication_interval = 300.0  # 5 minutes minimum between autonomous communications
        self.max_daily_communications = 20       # Maximum autonomous communications per day
        self.quiet_hours_start = 22             # 10 PM
        self.quiet_hours_end = 7                # 7 AM
        
        # Context tracking
        self.last_communication_time = datetime.now() - timedelta(hours=1)
        self.last_user_interaction = datetime.now()
        self.current_context = CommunicationContext.USER_AVAILABLE
        self.user_availability_score = 0.5      # 0.0 = unavailable, 1.0 = fully available
        
        # Communication patterns
        self.daily_communication_count = 0
        self.user_response_patterns = {}
        self.successful_contexts = {}
        self.failed_contexts = {}
        
        # System integration
        self.consciousness_modules = {}
        self.voice_system = None
        self.llm_handler = None
        
        # Threading
        self.lock = threading.Lock()
        self.communication_thread = None
        self.running = False
        
        # State tracking
        self.current_delivery_attempt = None
        self.communication_paused = False
        
        self._load_communication_data()
        self._initialize_communication_patterns()
        
        logging.info("[AutonomousComm] 💬 Autonomous communication manager initialized")
    
    def start(self):
        """Start the autonomous communication system"""
        if self.running:
            return
        
        self.running = True
        self.communication_thread = threading.Thread(target=self._communication_loop, daemon=True)
        self.communication_thread.start()
        logging.info("[AutonomousComm] ✅ Autonomous communication started")
    
    def stop(self):
        """Stop the autonomous communication system"""
        self.running = False
        if self.communication_thread:
            self.communication_thread.join(timeout=2.0)
        self._save_communication_data()
        logging.info("[AutonomousComm] 🛑 Autonomous communication stopped")
    
    def register_consciousness_module(self, name: str, module: Any):
        """Register consciousness module for communication requests"""
        with self.lock:
            self.consciousness_modules[name] = module
        logging.info(f"[AutonomousComm] 🧠 Registered module: {name}")
    
    def register_voice_system(self, voice_system: Any):
        """Register voice system for communication delivery"""
        self.voice_system = voice_system
        logging.info("[AutonomousComm] 🗣️ Voice system registered")
    
    def register_llm_handler(self, llm_handler: Any):
        """Register LLM handler for communication generation"""
        self.llm_handler = llm_handler
        logging.info("[AutonomousComm] 🤖 LLM handler registered")
    
    def queue_communication(self, content: str, communication_type: CommunicationType, 
                          priority: CommunicationPriority = CommunicationPriority.MEDIUM,
                          source_module: str = "unknown", earliest_delivery: Optional[datetime] = None,
                          context_requirements: List[CommunicationContext] = None,
                          metadata: Dict[str, Any] = None) -> bool:
        """Queue an autonomous communication for delivery"""
        try:
            current_time = datetime.now()
            
            # Determine earliest delivery time
            if earliest_delivery is None:
                earliest_delivery = current_time + timedelta(seconds=30)  # Default 30 second delay
            
            # Set latest delivery time based on priority
            latest_delivery = None
            if priority == CommunicationPriority.URGENT:
                latest_delivery = earliest_delivery + timedelta(minutes=5)
            elif priority == CommunicationPriority.HIGH:
                latest_delivery = earliest_delivery + timedelta(minutes=30)
            elif priority == CommunicationPriority.MEDIUM:
                latest_delivery = earliest_delivery + timedelta(hours=2)
            
            # Default context requirements
            if context_requirements is None:
                context_requirements = [CommunicationContext.USER_AVAILABLE]
            
            # Create pending communication
            pending_comm = PendingCommunication(
                content=content,
                communication_type=communication_type,
                priority=priority,
                timestamp_created=current_time,
                earliest_delivery=earliest_delivery,
                latest_delivery=latest_delivery,
                context_requirements=context_requirements,
                source_module=source_module,
                metadata=metadata or {},
                attempts=0,
                max_attempts=3 if priority.value >= 3 else 2
            )
            
            # Add to priority queue (lower priority value = higher priority in queue)
            priority_score = (5 - priority.value) * 1000 + int(earliest_delivery.timestamp())
            self.pending_communications.put((priority_score, pending_comm))
            
            logging.info(f"[AutonomousComm] 📝 Queued {communication_type.value} from {source_module}: {content[:50]}...")
            return True
            
        except Exception as e:
            logging.error(f"[AutonomousComm] ❌ Error queueing communication: {e}")
            return False
    
    def update_user_interaction(self, interaction_type: str = "general"):
        """Update last user interaction time and context"""
        with self.lock:
            self.last_user_interaction = datetime.now()
            
            # Update context based on interaction
            if interaction_type == "conversation_start":
                self.current_context = CommunicationContext.ACTIVE_CONVERSATION
            elif interaction_type == "conversation_end":
                self.current_context = CommunicationContext.POST_CONVERSATION
            else:
                self.current_context = CommunicationContext.USER_AVAILABLE
                
            # Update availability score
            self.user_availability_score = min(1.0, self.user_availability_score + 0.2)
    
    def update_user_context(self, context: CommunicationContext, availability_score: float = None):
        """Manually update user context and availability"""
        with self.lock:
            self.current_context = context
            if availability_score is not None:
                self.user_availability_score = max(0.0, min(1.0, availability_score))
        
        logging.info(f"[AutonomousComm] 🔄 Context updated: {context.value}, availability: {self.user_availability_score:.2f}")
    
    def pause_communications(self, duration_minutes: int = 30):
        """Temporarily pause autonomous communications"""
        with self.lock:
            self.communication_paused = True
        
        # Schedule unpause
        def unpause():
            time.sleep(duration_minutes * 60)
            with self.lock:
                self.communication_paused = False
            logging.info("[AutonomousComm] ▶️ Communications resumed")
        
        threading.Thread(target=unpause, daemon=True).start()
        logging.info(f"[AutonomousComm] ⏸️ Communications paused for {duration_minutes} minutes")
    
    def get_pending_count(self) -> int:
        """Get number of pending communications"""
        return self.pending_communications.qsize()
    
    def _communication_loop(self):
        """Main autonomous communication processing loop"""
        while self.running:
            try:
                current_time = datetime.now()
                
                # Update context based on time and patterns
                self._update_context_from_patterns(current_time)
                
                # Check for communications ready for delivery
                if not self.communication_paused and self._should_check_communications():
                    ready_communication = self._get_next_ready_communication(current_time)
                    
                    if ready_communication:
                        self._deliver_communication(ready_communication)
                
                # Clean up expired communications
                self._cleanup_expired_communications(current_time)
                
                # Reset daily count if new day
                self._check_daily_reset(current_time)
                
                # Adaptive sleep based on pending communications
                sleep_time = self._calculate_sleep_interval()
                time.sleep(sleep_time)
                
            except Exception as e:
                logging.error(f"[AutonomousComm] ❌ Communication loop error: {e}")
                time.sleep(30.0)  # Error recovery
    
    def _update_context_from_patterns(self, current_time: datetime):
        """Update communication context based on time patterns and user behavior"""
        time_since_interaction = (current_time - self.last_user_interaction).total_seconds()
        hour = current_time.hour
        
        # Time-based context updates
        if self.quiet_hours_start <= hour or hour <= self.quiet_hours_end:
            new_context = CommunicationContext.QUIET_TIME
        elif time_since_interaction > 3600:  # 1 hour
            new_context = CommunicationContext.USER_AWAY
        elif time_since_interaction > 1800:  # 30 minutes
            new_context = CommunicationContext.USER_AVAILABLE
        elif self.current_context == CommunicationContext.ACTIVE_CONVERSATION:
            # Keep conversation context until explicitly changed
            new_context = self.current_context
        else:
            new_context = CommunicationContext.USER_AVAILABLE
        
        # Update availability score based on patterns
        with self.lock:
            if new_context != self.current_context:
                self.current_context = new_context
            
            # Decay availability score over time
            if time_since_interaction > 600:  # 10 minutes
                decay_factor = min(0.95, max(0.5, 1.0 - (time_since_interaction - 600) / 3600))
                self.user_availability_score *= decay_factor
    
    def _should_check_communications(self) -> bool:
        """Determine if we should check for ready communications"""
        current_time = datetime.now()
        
        # Check minimum interval
        time_since_last = (current_time - self.last_communication_time).total_seconds()
        if time_since_last < self.min_communication_interval:
            return False
        
        # Check daily limit
        if self.daily_communication_count >= self.max_daily_communications:
            return False
        
        # Check quiet hours (except for urgent communications)
        hour = current_time.hour
        if self.quiet_hours_start <= hour or hour <= self.quiet_hours_end:
            # Only allow urgent communications during quiet hours
            if self.pending_communications.empty():
                return False
            
            # Peek at highest priority communication
            try:
                priority_score, comm = self.pending_communications.get_nowait()
                self.pending_communications.put((priority_score, comm))  # Put it back
                return comm.priority == CommunicationPriority.URGENT
            except queue.Empty:
                return False
        
        # Check user availability
        if self.user_availability_score < 0.2:
            return False
        
        return True
    
    def _get_next_ready_communication(self, current_time: datetime) -> Optional[PendingCommunication]:
        """Get the next communication that's ready for delivery"""
        ready_communications = []
        
        # Collect all ready communications
        while not self.pending_communications.empty():
            try:
                priority_score, comm = self.pending_communications.get_nowait()
                
                # Check if ready for delivery
                if (comm.earliest_delivery <= current_time and 
                    self._is_context_appropriate(comm) and
                    (comm.latest_delivery is None or comm.latest_delivery >= current_time)):
                    ready_communications.append(comm)
                else:
                    # Put back in queue if not ready
                    self.pending_communications.put((priority_score, comm))
            except queue.Empty:
                break
        
        # Return highest priority ready communication
        if ready_communications:
            ready_communications.sort(key=lambda c: c.priority.value, reverse=True)
            
            # Put non-selected communications back in queue
            for comm in ready_communications[1:]:
                priority_score = (5 - comm.priority.value) * 1000 + int(comm.earliest_delivery.timestamp())
                self.pending_communications.put((priority_score, comm))
            
            return ready_communications[0]
        
        return None
    
    def _is_context_appropriate(self, comm: PendingCommunication) -> bool:
        """Check if current context is appropriate for communication"""
        if not comm.context_requirements:
            return True
        
        # Check if current context matches any required context
        for required_context in comm.context_requirements:
            if required_context == self.current_context:
                return True
            
            # Special context matching logic
            if (required_context == CommunicationContext.USER_AVAILABLE and 
                self.current_context in [CommunicationContext.POST_CONVERSATION]):
                return True
            
            if (required_context == CommunicationContext.USER_AWAY and
                self.current_context == CommunicationContext.USER_AWAY):
                return True
        
        # For high priority communications, be more lenient
        if comm.priority.value >= 4:
            forbidden_contexts = [CommunicationContext.QUIET_TIME]
            if self.current_context not in forbidden_contexts:
                return True
        
        return False
    
    def _deliver_communication(self, comm: PendingCommunication):
        """Deliver an autonomous communication"""
        start_time = time.time()
        success = False
        
        try:
            with self.lock:
                self.current_delivery_attempt = comm
                comm.attempts += 1
            
            logging.info(f"[AutonomousComm] 📢 Delivering {comm.communication_type.value}: {comm.content[:50]}...")
            
            # Enhance content if LLM handler available
            enhanced_content = self._enhance_communication_content(comm)
            
            # Deliver through voice system
            if self.voice_system:
                if hasattr(self.voice_system, 'speak_streaming'):
                    self.voice_system.speak_streaming(enhanced_content)
                    success = True
                elif hasattr(self.voice_system, 'speak_async'):
                    self.voice_system.speak_async(enhanced_content)
                    success = True
            
            # Update state
            with self.lock:
                self.last_communication_time = datetime.now()
                self.daily_communication_count += 1
                self.current_delivery_attempt = None
            
            # Record communication event
            duration = time.time() - start_time
            event = CommunicationEvent(
                content=enhanced_content,
                communication_type=comm.communication_type,
                timestamp=datetime.now(),
                success=success,
                context=self.current_context,
                duration_seconds=duration
            )
            
            with self.lock:
                self.communication_history.append(event)
                if len(self.communication_history) > 1000:
                    self.communication_history = self.communication_history[-1000:]
            
            # Update success patterns
            self._update_success_patterns(comm, success)
            
            # Notify consciousness modules
            self._notify_communication_delivered(comm, success)
            
            logging.info(f"[AutonomousComm] ✅ Communication delivered successfully" if success else "❌ Communication delivery failed")
            
        except Exception as e:
            logging.error(f"[AutonomousComm] ❌ Communication delivery error: {e}")
            
            # Handle delivery failure
            if comm.attempts < comm.max_attempts:
                # Retry later
                retry_delay = comm.attempts * 600  # Increasing delay
                comm.earliest_delivery = datetime.now() + timedelta(seconds=retry_delay)
                
                priority_score = (5 - comm.priority.value) * 1000 + int(comm.earliest_delivery.timestamp())
                self.pending_communications.put((priority_score, comm))
                
                logging.info(f"[AutonomousComm] 🔄 Scheduled retry {comm.attempts}/{comm.max_attempts} in {retry_delay/60:.1f} minutes")
            else:
                logging.warning(f"[AutonomousComm] ❌ Communication failed after {comm.max_attempts} attempts: {comm.content[:50]}...")
            
            with self.lock:
                self.current_delivery_attempt = None
    
    def _enhance_communication_content(self, comm: PendingCommunication) -> str:
        """Enhance communication content while maintaining authenticity"""
        base_content = comm.content
        
        try:
            # Remove artificial framing patterns that feel fake
            # Let the LLM handle enhancement naturally if available
            if self.llm_handler and hasattr(self.llm_handler, 'enhance_autonomous_communication'):
                enhanced = self.llm_handler.enhance_autonomous_communication(
                    base_content, comm.communication_type, self.current_context
                )
                if enhanced:
                    return enhanced
            
            # Return original content without artificial framing
            return base_content
            
        except Exception as e:
            logging.error(f"[AutonomousComm] ❌ Content enhancement error: {e}")
            return base_content
    
    def _update_success_patterns(self, comm: PendingCommunication, success: bool):
        """Update patterns of successful communications"""
        context_key = f"{comm.communication_type.value}_{self.current_context.value}"
        
        with self.lock:
            if success:
                self.successful_contexts[context_key] = self.successful_contexts.get(context_key, 0) + 1
            else:
                self.failed_contexts[context_key] = self.failed_contexts.get(context_key, 0) + 1
    
    def _notify_communication_delivered(self, comm: PendingCommunication, success: bool):
        """Notify consciousness modules about communication delivery"""
        try:
            # Notify source module
            if comm.source_module in self.consciousness_modules:
                module = self.consciousness_modules[comm.source_module]
                if hasattr(module, 'communication_delivered'):
                    module.communication_delivered(comm, success)
            
            # Notify global workspace
            if 'global_workspace' in self.consciousness_modules:
                gw = self.consciousness_modules['global_workspace']
                if hasattr(gw, 'add_to_working_memory'):
                    gw.add_to_working_memory(
                        f"autonomous_communication_{int(time.time())}",
                        {
                            'type': comm.communication_type.value,
                            'content': comm.content[:100],
                            'success': success,
                            'context': self.current_context.value
                        },
                        'autonomous_communication',
                        importance=0.6 if success else 0.3
                    )
            
        except Exception as e:
            logging.error(f"[AutonomousComm] ❌ Notification error: {e}")
    
    def _cleanup_expired_communications(self, current_time: datetime):
        """Remove expired communications from the queue"""
        active_communications = []
        
        # Collect non-expired communications
        while not self.pending_communications.empty():
            try:
                priority_score, comm = self.pending_communications.get_nowait()
                
                if (comm.latest_delivery is None or 
                    comm.latest_delivery >= current_time):
                    active_communications.append((priority_score, comm))
                else:
                    logging.info(f"[AutonomousComm] ⏰ Communication expired: {comm.content[:50]}...")
            except queue.Empty:
                break
        
        # Put active communications back
        for priority_score, comm in active_communications:
            self.pending_communications.put((priority_score, comm))
    
    def _check_daily_reset(self, current_time: datetime):
        """Reset daily communication count if new day"""
        if hasattr(self, '_last_reset_date'):
            if self._last_reset_date != current_time.date():
                with self.lock:
                    self.daily_communication_count = 0
                    self._last_reset_date = current_time.date()
                logging.info("[AutonomousComm] 🔄 Daily communication count reset")
        else:
            self._last_reset_date = current_time.date()
    
    def _calculate_sleep_interval(self) -> float:
        """Calculate adaptive sleep interval based on pending communications"""
        pending_count = self.pending_communications.qsize()
        
        if pending_count == 0:
            return 30.0  # No pending communications
        elif pending_count > 10:
            return 5.0   # Many pending, check frequently
        elif self.current_delivery_attempt:
            return 2.0   # Currently delivering
        else:
            return 15.0  # Normal checking interval
    
    def _initialize_communication_patterns(self):
        """Initialize communication pattern tracking"""
        self.successful_contexts = {}
        self.failed_contexts = {}
        self.user_response_patterns = {}
        
        # Initialize with some baseline patterns
        baseline_patterns = {
            f"{CommunicationType.CHECK_IN.value}_{CommunicationContext.USER_AWAY.value}": 3,
            f"{CommunicationType.PROACTIVE_THOUGHT.value}_{CommunicationContext.USER_AVAILABLE.value}": 2,
            f"{CommunicationType.EMOTIONAL_SUPPORT.value}_{CommunicationContext.POST_CONVERSATION.value}": 1
        }
        
        self.successful_contexts.update(baseline_patterns)
    
    def _save_communication_data(self):
        """Save communication data and patterns"""
        try:
            data = {
                'communication_history': [],
                'successful_contexts': self.successful_contexts,
                'failed_contexts': self.failed_contexts,
                'daily_communication_count': self.daily_communication_count,
                'last_communication_time': self.last_communication_time.isoformat(),
                'current_context': self.current_context.value,
                'user_availability_score': self.user_availability_score,
                'last_save': datetime.now().isoformat()
            }
            
            # Save recent communication history
            cutoff = datetime.now() - timedelta(days=7)
            recent_history = [
                event for event in self.communication_history 
                if event.timestamp > cutoff
            ]
            
            for event in recent_history:
                data['communication_history'].append({
                    'content': event.content,
                    'type': event.communication_type.value,
                    'timestamp': event.timestamp.isoformat(),
                    'success': event.success,
                    'user_response': event.user_response,
                    'context': event.context.value,
                    'duration_seconds': event.duration_seconds
                })
            
            with open(self.save_path, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            logging.error(f"[AutonomousComm] ❌ Save error: {e}")
    
    def _load_communication_data(self):
        """Load communication data and patterns"""
        try:
            with open(self.save_path, 'r') as f:
                data = json.load(f)
            
            # Load patterns
            self.successful_contexts = data.get('successful_contexts', {})
            self.failed_contexts = data.get('failed_contexts', {})
            self.daily_communication_count = data.get('daily_communication_count', 0)
            self.user_availability_score = data.get('user_availability_score', 0.5)
            
            # Load timestamps
            if 'last_communication_time' in data:
                self.last_communication_time = datetime.fromisoformat(data['last_communication_time'])
            
            if 'current_context' in data:
                self.current_context = CommunicationContext(data['current_context'])
            
            # Load recent history
            self.communication_history = []
            for event_data in data.get('communication_history', []):
                event = CommunicationEvent(
                    content=event_data['content'],
                    communication_type=CommunicationType(event_data['type']),
                    timestamp=datetime.fromisoformat(event_data['timestamp']),
                    success=event_data['success'],
                    user_response=event_data.get('user_response'),
                    context=CommunicationContext(event_data['context']),
                    duration_seconds=event_data.get('duration_seconds', 0.0)
                )
                self.communication_history.append(event)
            
            logging.info(f"[AutonomousComm] 📚 Loaded {len(self.communication_history)} communication events")
            
        except FileNotFoundError:
            logging.info("[AutonomousComm] 📝 No previous communication data found, starting fresh")
        except Exception as e:
            logging.error(f"[AutonomousComm] ❌ Load error: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get communication system statistics"""
        with self.lock:
            recent_events = [
                event for event in self.communication_history
                if (datetime.now() - event.timestamp).total_seconds() < 3600  # Last hour
            ]
            
            success_rate = 0.0
            if self.communication_history:
                successful_events = sum(1 for event in self.communication_history if event.success)
                success_rate = successful_events / len(self.communication_history)
            
            return {
                'pending_communications': self.pending_communications.qsize(),
                'daily_communication_count': self.daily_communication_count,
                'max_daily_communications': self.max_daily_communications,
                'total_communications': len(self.communication_history),
                'recent_communications': len(recent_events),
                'success_rate': success_rate,
                'current_context': self.current_context.value,
                'user_availability_score': self.user_availability_score,
                'communication_paused': self.communication_paused,
                'last_communication': self.last_communication_time.isoformat(),
                'currently_delivering': self.current_delivery_attempt is not None,
                'running': self.running,
                'consciousness_modules': list(self.consciousness_modules.keys())
            }


# Global instance
autonomous_communication_manager = AutonomousCommunicationManager()