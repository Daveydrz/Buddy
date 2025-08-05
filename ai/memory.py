# ai/memory.py - MEGA-INTELLIGENT Memory System with Advanced Context Awareness + ENTROPY
import time
import json
import datetime
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from config import MAX_HISTORY_LENGTH, DEBUG
from enum import Enum

# ✅ ENTROPY SYSTEM: Import consciousness emergence components for probabilistic memory
try:
    from ai.entropy_engine import get_entropy_engine, probabilistic_select, inject_consciousness_entropy, EntropyLevel
    print("[Memory] 🌀 Entropy system integrated for probabilistic memory retrieval")
    ENTROPY_AVAILABLE = True
except ImportError as e:
    print(f"[Memory] ⚠️ Entropy system not available: {e}")
    ENTROPY_AVAILABLE = False

# 🧠 MULTI-CONTEXT WORKING MEMORY: Track multiple simultaneous contexts
@dataclass
class ContextItem:
    """Individual context/event tracking"""
    context_id: str                           # Unique identifier for this context
    event_type: str                          # "social_event", "medical_appointment", "work_task", etc.
    description: str                         # "niece's birthday", "gp annual check"
    place: Optional[str] = None              # "restaurant", "doctor's office", etc.
    time_reference: Optional[str] = None     # "today", "after birthday", "tomorrow"
    status: str = "planned"                  # "planned", "preparing", "ongoing", "completed"
    priority: int = 1                        # 1=high, 2=medium, 3=low
    timestamp: Optional[str] = None          # When this was added
    related_contexts: List[str] = None       # IDs of related contexts
    completion_status: float = 0.0           # 0.0 to 1.0 progress
    
    def __post_init__(self):
        if self.related_contexts is None:
            self.related_contexts = []

@dataclass
class WorkingMemoryState:
    """Track multiple simultaneous actions/contexts for reference resolution"""
    active_contexts: Dict[str, ContextItem] = None  # Multiple simultaneous contexts
    last_action: Optional[str] = None               # For backward compatibility
    last_place: Optional[str] = None                # For backward compatibility  
    last_topic: Optional[str] = None                # For backward compatibility
    last_goal: Optional[str] = None                 # For backward compatibility
    last_timestamp: Optional[str] = None            # When last updated
    action_status: str = "unknown"                  # For backward compatibility
    context_sequence: List[str] = None              # Order of context creation
    
    def __post_init__(self):
        if self.active_contexts is None:
            self.active_contexts = {}
        if self.context_sequence is None:
            self.context_sequence = []

# 📋 INTERACTION THREAD MEMORY: Track conversation threads
@dataclass
class InteractionThread:
    """Track individual conversation threads for reference resolution"""
    interaction_id: int                        # Turn number in conversation
    timestamp: str                            # When this interaction occurred
    intent: str                               # "internet_search", "help_request", "task_request"
    query: str                                # Original user request/query
    status: str                               # "pending", "completed", "failed"
    user_message: str                         # Full user message
    ai_response: Optional[str] = None         # AI response if completed
    related_threads: List[int] = None         # Connected interaction IDs
    
    def __post_init__(self):
        if self.related_threads is None:
            self.related_threads = []

# 🧠 EPISODIC TURN MEMORY: Track conversation turns with full context
@dataclass
class EpisodicTurn:
    """Track individual conversation turns with full context"""
    turn_number: int                          # Sequential turn number
    timestamp: str                            # When this turn occurred
    user_message: str                         # What user said
    ai_response: str                          # How AI responded
    intent_detected: str                      # Detected intent/purpose
    entities_mentioned: List[str]             # People, places, things mentioned
    emotional_tone: str                       # "neutral", "concerned", "excited"
    context_references: List[str]             # References to previous turns
    
    def __post_init__(self):
        if self.entities_mentioned is None:
            self.entities_mentioned = []
        if self.context_references is None:
            self.context_references = []
    
@dataclass
class IntentSlot:
    """Track multi-turn task intentions"""
    intent: str                                # "go to shop"
    status: str                               # "preparing", "ongoing", "completed"
    prep_steps: List[str]                     # ["check what is needed", "get keys"]
    timestamp: str                            # When intent was detected
    related_actions: List[str]                # Connected actions/statements
    
@dataclass
class ReferenceResolution:
    """Store pronoun/reference resolution context"""
    vague_phrase: str                         # "I finished", "It went well"
    likely_referent: str                      # "making dinner", "shopping trip"
    confidence: float                         # 0.0 - 1.0
    context_source: str                       # "working_memory", "intent_slot"

# Enhanced settings with fallbacks
try:
    from config import (ENHANCED_CONVERSATION_MEMORY, CONVERSATION_MEMORY_LENGTH, 
                       CONVERSATION_CONTEXT_LENGTH, CONVERSATION_SUMMARY_ENABLED,
                       CONVERSATION_SUMMARY_THRESHOLD, TOPIC_TRACKING_ENABLED,
                       MAX_CONVERSATION_TOPICS, CONTEXT_COMPRESSION_ENABLED,
                       MAX_CONTEXT_TOKENS)
except ImportError:
    ENHANCED_CONVERSATION_MEMORY = True
    CONVERSATION_MEMORY_LENGTH = 25
    CONVERSATION_CONTEXT_LENGTH = 10
    CONVERSATION_SUMMARY_ENABLED = True
    CONVERSATION_SUMMARY_THRESHOLD = 18
    TOPIC_TRACKING_ENABLED = True
    MAX_CONVERSATION_TOPICS = 6
    CONTEXT_COMPRESSION_ENABLED = True
    MAX_CONTEXT_TOKENS = 1500

# 🧠 MEGA-INTELLIGENT MEMORY ENHANCEMENTS
class EntityStatus(Enum):
    """Track current status of entities"""
    CURRENT = "current"
    FORMER = "former"
    DECEASED = "deceased"
    SOLD = "sold"
    LOST = "lost"
    ENDED = "ended"
    UNKNOWN = "unknown"

class EmotionalImpact(Enum):
    """Emotional significance levels"""
    CRITICAL = 0.9  # Death, major life events
    HIGH = 0.7      # Job loss, breakups
    MEDIUM = 0.5    # Moving, minor changes
    LOW = 0.3       # Preferences, activities
    MINIMAL = 0.1   # Basic facts

@dataclass
class EntityMemory:
    """🧠 MEGA-INTELLIGENT: Track entities with full context"""
    name: str
    entity_type: str  # "pet", "person", "possession", "relationship"
    status: EntityStatus
    emotional_significance: float
    date_learned: str
    last_updated: str
    context_description: str
    related_memories: List[str]
    emotional_context: List[str]  # ["beloved", "family", "missed"]
    temporal_context: Optional[str] = None  # "last week", "yesterday"
    
@dataclass
class LifeEvent:
    """🧠 MEGA-INTELLIGENT: Track major life events"""
    event_type: str  # "death", "birth", "job_change", "relationship_change"
    description: str
    entities_involved: List[str]
    emotional_impact: float
    date_occurred: str
    date_learned: str
    ongoing_effects: List[str]  # ["grieving", "adjusting", "celebrating"]
    follow_up_contexts: List[str]  # ["avoid_suggesting_activities", "offer_support"]

@dataclass
class PersonalFact:
    """Enhanced personal fact storage"""
    category: str
    key: str
    value: str
    confidence: float
    date_learned: str
    last_mentioned: str
    source_context: str
    emotional_weight: float = 0.3
    current_status: EntityStatus = EntityStatus.CURRENT
    related_entities: List[str] = None
    
    def __post_init__(self):
        if self.related_entities is None:
            self.related_entities = []

@dataclass
class EmotionalState:
    """Enhanced emotional state tracking"""
    emotion: str
    intensity: int
    context: str
    date: str
    follow_up_needed: bool
    related_memories: List[str] = None
    trigger_entities: List[str] = None
    
    def __post_init__(self):
        if self.related_memories is None:
            self.related_memories = []
        if self.trigger_entities is None:
            self.trigger_entities = []

@dataclass
class ScheduledEvent:
    """Enhanced event tracking"""
    event_type: str
    description: str
    date: str
    reminder_dates: List[str]
    completed: bool
    emotional_significance: float = 0.5
    related_entities: List[str] = None
    
    def __post_init__(self):
        if self.related_entities is None:
            self.related_entities = []

@dataclass
class ConversationTopic:
    """Enhanced topic tracking"""
    topic: str
    start_time: str
    last_mentioned: str
    message_count: int
    keywords: List[str]
    emotional_context: str = "neutral"
    related_entities: List[str] = None
    
    def __post_init__(self):
        if self.related_entities is None:
            self.related_entities = []

class MemoryContextValidator:
    """🧠 MEGA-INTELLIGENT: Validate memory context and prevent inappropriate responses"""
    
    def __init__(self):
        self.inappropriate_suggestions = {
            EntityStatus.DECEASED: [
                "walk", "play", "feed", "pet", "visit", "call", "talk to", 
                "bring", "take out", "exercise", "groom", "train"
            ],
            EntityStatus.SOLD: [
                "drive", "use", "fix", "maintain", "clean"
            ],
            EntityStatus.ENDED: [
                "contact", "call", "visit", "meet", "date", "spend time"
            ],
            EntityStatus.LOST: [
                "use", "find", "get", "bring"
            ]
        }
    
    def validate_response_appropriateness(self, proposed_response: str, entities: Dict[str, EntityMemory]) -> Tuple[bool, List[str]]:
        """Check if proposed response conflicts with known entity statuses"""
        warnings = []
        response_lower = proposed_response.lower()
        
        for entity_name, entity in entities.items():
            if entity_name.lower() in response_lower:
                if entity.status in self.inappropriate_suggestions:
                    inappropriate_words = self.inappropriate_suggestions[entity.status]
                    for word in inappropriate_words:
                        if word in response_lower:
                            status_value = entity.status.value if entity.status else "unknown"
                            warnings.append(f"Inappropriate suggestion '{word}' for {status_value} entity '{entity_name}'")
        
        return len(warnings) == 0, warnings
    
    def suggest_appropriate_response_context(self, entity: EntityMemory) -> List[str]:
        """Suggest appropriate response contexts for entities"""
        suggestions = []
        
        if entity.status == EntityStatus.DECEASED:
            if entity.emotional_significance > 0.7:
                suggestions.extend([
                    "offer_condolences", "share_memory", "acknowledge_loss", 
                    "express_empathy", "avoid_present_tense"
                ])
        elif entity.status == EntityStatus.FORMER:
            suggestions.extend([
                "use_past_tense", "acknowledge_change", "offer_support"
            ])
        elif entity.status == EntityStatus.ENDED:
            suggestions.extend([
                "acknowledge_end", "offer_emotional_support", "avoid_couple_activities"
            ])
        
        return suggestions

class MemoryInferenceEngine:
    """🧠 MEGA-INTELLIGENT: Make logical inferences from stored memories"""
    
    def infer_entity_implications(self, entity: EntityMemory) -> List[str]:
        """Infer logical implications of entity status"""
        implications = []
        
        if entity.status == EntityStatus.DECEASED:
            implications.extend([
                "no_physical_activities",
                "use_past_tense",
                "emotional_sensitivity_required",
                "grief_support_appropriate"
            ])
        elif entity.status == EntityStatus.FORMER:
            implications.extend([
                "relationship_ended",
                "use_past_tense",
                "avoid_current_references"
            ])
        elif entity.status == EntityStatus.SOLD:
            implications.extend([
                "no_longer_owned",
                "past_ownership_only"
            ])
        
        return implications
    
    def detect_memory_contradictions(self, new_fact: PersonalFact, existing_entities: Dict[str, EntityMemory]) -> List[str]:
        """Detect contradictions between new information and existing memories"""
        contradictions = []
        
        # Check if new fact contradicts existing entity status
        for entity_name, entity in existing_entities.items():
            if entity_name.lower() in (new_fact.value.lower() if new_fact.value else ""):
                if entity.status == EntityStatus.DECEASED and "alive" in (new_fact.value.lower() if new_fact.value else ""):
                    contradictions.append(f"New fact suggests {entity_name} is alive, but recorded as deceased")
                elif entity.status == EntityStatus.CURRENT and "used to" in new_fact.key:
                    contradictions.append(f"New fact suggests {entity_name} is former, but recorded as current")
        
        return contradictions

class UserMemorySystem:
    """🧠 MEGA-INTELLIGENT: Enhanced memory system with context awareness"""
    
    def __init__(self, username: str):
        self.username = username
        self.memory_dir = Path(f"memory/{username}")
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        
        # Enhanced memory storage
        self.personal_facts: Dict[str, PersonalFact] = {}
        self.emotional_history: List[EmotionalState] = []
        self.scheduled_events: List[ScheduledEvent] = []
        self.conversation_topics: List[ConversationTopic] = []
        
        # 🧠 NEW: Advanced memory components
        self.entity_memories: Dict[str, EntityMemory] = {}
        self.life_events: List[LifeEvent] = {}
        self.memory_validator = MemoryContextValidator()
        self.inference_engine = MemoryInferenceEngine()
        
        # 🎯 PLAN DETECTION: Store user plans with temporal context
        self.user_today_plan: Optional[str] = None
        self.plan_timestamp: Optional[str] = None
        self.plan_context: Optional[str] = None
        
        # 🧠 WORKING MEMORY TRACKING: Advanced context-aware memory
        self.working_memory: WorkingMemoryState = WorkingMemoryState()
        self.intent_slots: Dict[str, IntentSlot] = {}  # Track multi-turn tasks
        self.reference_history: List[ReferenceResolution] = []  # Track pronoun resolutions
        
        # 📋 INTERACTION THREAD MEMORY: Track conversation threads
        self.interaction_log: List[InteractionThread] = []  # Conversation thread tracking
        self.current_interaction_id: int = 0  # Current turn number
        
        # 🧠 EPISODIC TURN MEMORY: Track full conversation context
        self.episodic_memory: List[EpisodicTurn] = []  # Full conversation history
        self.current_turn_number: int = 0  # Current turn in conversation
        
        self.load_memory()
        print(f"[MegaMemory] 🧠 MEGA-INTELLIGENT memory system loaded for {username}")
    
    def add_entity_memory(self, name: str, entity_type: str, status: EntityStatus, 
                         emotional_significance: float, context: str):
        """🧠 Add or update entity memory with full context"""
        current_time = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        
        entity = EntityMemory(
            name=name,
            entity_type=entity_type,
            status=status,
            emotional_significance=emotional_significance,
            date_learned=current_time,
            last_updated=current_time,
            context_description=context,
            related_memories=[],
            emotional_context=self._extract_emotional_context(context)
        )
        
        self.entity_memories[name.lower()] = entity
        
        # 🧠 MEGA-INTELLIGENT: Auto-generate implications
        implications = self.inference_engine.infer_entity_implications(entity)
        
        status_value = status.value if status else "unknown"
        print(f"[MegaMemory] 🧠 Entity Added: {name} ({entity_type}) - Status: {status_value}")
        print(f"[MegaMemory] 💭 Implications: {', '.join(implications)}")
        
        self.save_memory()
    
    # 🕐 TIME-AWARE GREETINGS: Generate appropriate greeting based on current time
    def get_time_based_greeting(self, user_name: str = None) -> str:
        """Generate time-appropriate greeting (Good morning/afternoon/evening)"""
        current_time = datetime.datetime.now()
        hour = current_time.hour
        
        # Determine time of day
        if 5 <= hour < 12:
            time_greeting = "Good morning"
            time_context = "morning"
        elif 12 <= hour < 17:
            time_greeting = "Good afternoon"
            time_context = "afternoon"
        elif 17 <= hour < 22:
            time_greeting = "Good evening"
            time_context = "evening"
        else:
            time_greeting = "Hello"  # Late night/early morning
            time_context = "late night"
        
        # Personalize if user name available
        if user_name:
            greeting = f"{time_greeting} {user_name}"
        else:
            greeting = time_greeting
        
        # Add contextual follow-up based on time
        if time_context == "morning":
            follow_up = "Did you sleep well?"
        elif time_context == "afternoon":
            follow_up = "How's your day going?"
        elif time_context == "evening":
            follow_up = "How was your day?"
        else:
            follow_up = "You're up late! Everything okay?"
        
        return f"{greeting}. {follow_up}"
    
    # 📋 INTERACTION THREAD MEMORY: Track and resolve conversation threads
    def add_interaction_thread(self, user_message: str, intent: str, query: str = None) -> int:
        """Add new interaction thread for tracking"""
        self.current_interaction_id += 1
        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        thread = InteractionThread(
            interaction_id=self.current_interaction_id,
            timestamp=current_time,
            intent=intent,
            query=query or user_message,
            status="pending",
            user_message=user_message
        )
        
        self.interaction_log.append(thread)
        print(f"[InteractionMemory] 📋 Thread #{self.current_interaction_id}: {intent} - {query}")
        
        self.save_memory()
        return self.current_interaction_id
    
    def complete_interaction_thread(self, interaction_id: int, ai_response: str, status: str = "completed"):
        """Mark interaction thread as completed with AI response"""
        for thread in self.interaction_log:
            if thread.interaction_id == interaction_id:
                thread.ai_response = ai_response
                thread.status = status
                print(f"[InteractionMemory] ✅ Thread #{interaction_id} completed")
                break
        self.save_memory()
    
    def find_recent_interaction(self, intent_type: str, status: str = "pending", max_age_minutes: int = 30) -> Optional[InteractionThread]:
        """Find most recent interaction matching criteria"""
        current_time = datetime.datetime.now()
        
        for thread in reversed(self.interaction_log):  # Search from most recent
            try:
                thread_time = datetime.datetime.strptime(thread.timestamp, '%Y-%m-%d %H:%M:%S')
                age_minutes = (current_time - thread_time).total_seconds() / 60
                
                if (thread.intent == intent_type and 
                    thread.status == status and 
                    age_minutes <= max_age_minutes):
                    return thread
            except ValueError:
                continue  # Skip if timestamp parsing fails
        
        return None
    
    def resolve_thread_reference(self, user_message: str) -> Optional[str]:
        """Resolve vague references to previous interactions"""
        user_lower = user_message.lower()
        
        # Common reference patterns
        reference_patterns = [
            ("did you find", "internet_search"),
            ("what about that", "task_request"),
            ("did you do", "task_request"),
            ("how did it go", "internet_search"),
            ("any update", "pending_task"),
            ("what happened with", "task_request")
        ]
        
        for pattern, intent_type in reference_patterns:
            if pattern in user_lower:
                recent_thread = self.find_recent_interaction(intent_type, "pending")
                if recent_thread:
                    return f"User is referring to their earlier {intent_type}: '{recent_thread.query}' from {self._format_time_ago(recent_thread.timestamp)}"
        
        return None
    
    def _format_time_ago(self, timestamp_str: str) -> str:
        """Format how long ago something happened"""
        try:
            thread_time = datetime.datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
            current_time = datetime.datetime.now()
            diff = current_time - thread_time
            
            minutes = int(diff.total_seconds() / 60)
            if minutes < 1:
                return "just now"
            elif minutes < 60:
                return f"{minutes} minutes ago"
            else:
                hours = int(minutes / 60)
                return f"{hours} hours ago"
        except ValueError:
            return "earlier"
    
    # 🧠 EPISODIC TURN MEMORY: Track full conversation context  
    def add_episodic_turn(self, user_message: str, ai_response: str, intent: str = "general", 
                         entities: List[str] = None, emotional_tone: str = "neutral") -> int:
        """Add complete conversation turn to episodic memory"""
        self.current_turn_number += 1
        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Detect context references to previous turns
        context_refs = self._detect_context_references(user_message)
        
        turn = EpisodicTurn(
            turn_number=self.current_turn_number,
            timestamp=current_time,
            user_message=user_message,
            ai_response=ai_response,
            intent_detected=intent,
            entities_mentioned=entities or [],
            emotional_tone=emotional_tone,
            context_references=context_refs
        )
        
        self.episodic_memory.append(turn)
        print(f"[EpisodicMemory] 🧠 Turn #{self.current_turn_number}: {intent} - {len(entities or [])} entities")
        
        self.save_memory()
        return self.current_turn_number
    
    def _detect_context_references(self, user_message: str) -> List[str]:
        """Detect references to previous conversation turns"""
        refs = []
        user_lower = user_message.lower()
        
        # Temporal references
        temporal_refs = ["earlier", "before", "previously", "just now", "a minute ago"]
        for ref in temporal_refs:
            if ref in user_lower:
                refs.append(f"temporal_reference: {ref}")
        
        # Pronoun references 
        pronoun_refs = ["that", "it", "this", "what we discussed"]
        for ref in pronoun_refs:
            if ref in user_lower:
                refs.append(f"pronoun_reference: {ref}")
        
        return refs
    
    # 💬 NATURAL LANGUAGE CONTEXT INJECTION: Enhanced context for LLM
    def get_conversation_context_for_llm(self, user_message: str) -> str:
        """Generate enhanced conversation context for LLM prompts"""
        context_parts = []
        
        # 🕐 TIME CONTEXT: Current time information
        current_time = datetime.datetime.now()
        time_str = current_time.strftime('%H:%M')
        if 5 <= current_time.hour < 12:
            time_context = f"Current time: {time_str} — morning"
        elif 12 <= current_time.hour < 17:
            time_context = f"Current time: {time_str} — afternoon"
        elif 17 <= current_time.hour < 22:
            time_context = f"Current time: {time_str} — evening"
        else:
            time_context = f"Current time: {time_str} — late night"
        
        context_parts.append(time_context)
        context_parts.append(f"User: {self.username}")
        
        # 📋 THREAD REFERENCE RESOLUTION: Check for references to previous interactions
        thread_reference = self.resolve_thread_reference(user_message)
        if thread_reference:
            context_parts.append(thread_reference)
        
        # 🧠 RECENT EPISODIC CONTEXT: Include recent conversation turns
        if self.episodic_memory:
            recent_turns = self.episodic_memory[-2:]  # Last 2 turns
            for turn in recent_turns:
                turn_context = f"Turn #{turn.turn_number} ({self._format_time_ago(turn.timestamp)}): User said '{turn.user_message}' → Intent: {turn.intent_detected}"
                context_parts.append(turn_context)
        
        # 🧠 WORKING MEMORY: Current action context
        working_memory_context = self.get_working_memory_context_for_llm()
        if working_memory_context:
            context_parts.append(working_memory_context)
        
        return "\n".join(context_parts)
    
    def add_life_event(self, event_type: str, description: str, entities_involved: List[str],
                      emotional_impact: float, ongoing_effects: List[str] = None):
        """🧠 Record major life events with context"""
        current_time = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        
        if ongoing_effects is None:
            ongoing_effects = []
        
        event = LifeEvent(
            event_type=event_type,
            description=description,
            entities_involved=entities_involved,
            emotional_impact=emotional_impact,
            date_occurred=current_time,
            date_learned=current_time,
            ongoing_effects=ongoing_effects,
            follow_up_contexts=self._generate_follow_up_contexts(event_type, emotional_impact)
        )
        
        event_id = f"{event_type}_{int(time.time())}"
        self.life_events[event_id] = event
        
        # Update related entities
        for entity_name in entities_involved:
            if entity_name.lower() in self.entity_memories:
                self.entity_memories[entity_name.lower()].related_memories.append(event_id)
        
        print(f"[MegaMemory] 📅 Life Event: {description} (Impact: {emotional_impact})")
        self.save_memory()
    
    def validate_response_before_output(self, proposed_response: str) -> Tuple[bool, str]:
        """🧠 MEGA-INTELLIGENT: Validate response appropriateness before output"""
        is_appropriate, warnings = self.memory_validator.validate_response_appropriateness(
            proposed_response, self.entity_memories
        )
        
        if not is_appropriate:
            print(f"[MegaMemory] ⚠️ Response validation failed: {warnings}")
            
            # Generate alternative response
            alternative = self._generate_appropriate_alternative(proposed_response, warnings)
            return False, alternative
        
        return True, proposed_response
    
    def _generate_appropriate_alternative(self, original_response: str, warnings: List[str]) -> str:
        """Generate contextually appropriate alternative response"""
        # This is a simplified version - in a full implementation, 
        # this would use more sophisticated NLP to rewrite responses
        
        for warning in warnings:
            if "deceased" in warning and "walk" in warning:
                return "I remember you mentioned your pet. Losing a beloved companion is really difficult. How are you feeling about that?"
            elif "deceased" in warning:
                return "I'm thinking of the loss you mentioned. It's completely normal to still feel emotional about it."
        
        return "I understand. Would you like to talk about how you're feeling today?"
    
    def _extract_emotional_context(self, context: str) -> List[str]:
        """Extract emotional context tags from text"""
        emotional_indicators = {
            "beloved": ["love", "adore", "cherish", "dear", "precious"],
            "missed": ["miss", "gone", "absence", "empty"],
            "sad": ["sad", "grief", "sorrow", "heartbreak"],
            "happy": ["joy", "wonderful", "amazing", "great"],
            "family": ["family", "relative", "close", "important"]
        }
        
        context_lower = context.lower()
        tags = []
        
        for tag, indicators in emotional_indicators.items():
            if any(indicator in context_lower for indicator in indicators):
                tags.append(tag)
        
        return tags
    
    def _generate_follow_up_contexts(self, event_type: str, emotional_impact: float) -> List[str]:
        """Generate appropriate follow-up contexts for events"""
        contexts = []
        
        if event_type == "death" and emotional_impact > 0.7:
            contexts.extend([
                "offer_emotional_support",
                "avoid_suggesting_activities_with_deceased",
                "acknowledge_grief_process",
                "be_sensitive_to_mentions"
            ])
        elif event_type == "relationship_end":
            contexts.extend([
                "avoid_couple_activities",
                "use_past_tense_for_ex",
                "offer_emotional_support"
            ])
        elif event_type == "job_loss":
            contexts.extend([
                "avoid_work_related_assumptions",
                "offer_career_support",
                "be_sensitive_to_stress"
            ])
        
        return contexts
    
    def retrieve_relevant_memories(self, question: str, max_memories: int = 3) -> List[Dict[str, Any]]:
        """🎯 SEMANTIC + TEMPORAL: Retrieve memories relevant to the current question"""
        try:
            question_lower = question.lower()
            relevant_memories = []
            
            # Step 1: ENHANCED temporal keyword detection for edge cases
            time_keywords = [
                # Past events
                'yesterday', 'earlier', 'before', 'last week', 'last month', 'last night',
                'this morning', 'this afternoon', 'this evening', 'recently', 'just now',
                # Future events
                'tomorrow', 'next week', 'next month', 'later', 'tonight', 'upcoming',
                'tomorrow afternoon', 'tomorrow morning', 'next wednesday', 'next friday',
                # Questions about time - ENHANCED for food/location questions
                'where did i go', 'what did i do', 'when did i', 'who did i see',
                'where was i', 'what happened', 'where did we go', 'who did i meet',
                'what do i have', 'when is my', 'where am i going', 'what have i booked',
                'what am i nervous about', 'what am i excited about', 'who am i seeing',
                'where did i eat', 'what did i eat', 'who did i eat with', 'where did we eat',
                'what did we do', 'where did we go', 'who was i with', 'today',
                # Appointment/event questions
                'appointment', 'meeting', 'plans', 'scheduled', 'booked', 'event'
            ]
            
            is_temporal_question = any(keyword in question_lower for keyword in time_keywords)
            
            if not is_temporal_question:
                print(f"[Memory] ❌ Question not temporal: '{question}'")
                return []
            
            print(f"[Memory] 🎯 Temporal question detected: '{question}'")
            
            # Step 2: ENHANCED semantic keywords for edge cases
            place_keywords = [
                'where', 'place', 'restaurant', 'shop', 'store', 'go', 'went', 'going',
                'visit', 'been', 'location', 'mcdonalds', 'mcdonald', 'coffee shop', 'cafe',
                'mall', 'supermarket', 'pharmacy', 'dentist', 'office', 'hospital'
            ]
            
            activity_keywords = [
                'what', 'do', 'did', 'activity', 'eat', 'ate', 'buy', 'bought',
                'grabbed', 'met', 'meeting', 'appointment', 'plans', 'booked', 'scheduled',
                'discuss', 'talking', 'nervous', 'excited', 'worried', 'food', 'grabbed'
            ]
            
            person_keywords = [
                'who', 'person', 'people', 'friend', 'friends', 'family', 'see', 'saw', 
                'meet', 'met', 'with', 'sarah', 'niece', 'nephew', 'cousin', 'colleague'
            ]
            
            # Step 2.5: ENHANCED question type detection
            appointment_keywords = [
                'appointment', 'dentist', 'doctor', 'meeting', 'scheduled', 'booked',
                'plans', 'event', 'birthday', 'wedding', 'nervous', 'excited'
            ]
            
            future_keywords = [
                'tomorrow', 'next week', 'next month', 'later', 'upcoming', 'going to',
                'will', 'planning', 'scheduled for', 'booked for'
            ]
            
            # Step 3: Search through all memory types for semantic matches
            current_time = datetime.datetime.now()
            
            # Search personal facts
            for fact_key, fact in self.personal_facts.items():
                relevance_score = self._calculate_semantic_relevance(
                    question_lower, fact.value.lower(), fact.key.lower()
                )
                
                if relevance_score > 0.3:  # Threshold for relevance
                    # Time decay factor (recent events get higher priority)
                    time_factor = self._calculate_time_relevance(fact.date_learned, current_time)
                    
                    relevant_memories.append({
                        'type': 'personal_fact',
                        'content': f"{fact.key.replace('_', ' ')}: {fact.value}",
                        'relevance': relevance_score * time_factor,
                        'date': fact.date_learned,
                        'original_text': getattr(fact, 'source_context', '')
                    })
            
            # Search working memory (most recent activities)
            if self.working_memory.last_action:
                action_relevance = self._calculate_semantic_relevance(
                    question_lower, self.working_memory.last_action.lower(), 
                    self.working_memory.last_place.lower() if self.working_memory.last_place else ""
                )
                
                if action_relevance > 0.3:
                    relevant_memories.append({
                        'type': 'working_memory',
                        'content': f"Recent activity: {self.working_memory.last_action}" + 
                                  (f" at {self.working_memory.last_place}" if self.working_memory.last_place else ""),
                        'relevance': action_relevance * 1.2,  # Boost recent activities
                        'date': self.working_memory.last_timestamp or datetime.datetime.now().isoformat(),
                        'original_text': self.working_memory.last_action
                    })
            
            # Search episodic memory (conversation turns)
            for turn in self.episodic_memory[-10:]:  # Last 10 turns
                turn_relevance = self._calculate_semantic_relevance(
                    question_lower, turn.user_message.lower(), turn.ai_response.lower()
                )
                
                if turn_relevance > 0.4:  # Higher threshold for conversations
                    turn_time = datetime.datetime.strptime(turn.timestamp, '%Y-%m-%d %H:%M:%S')
                    time_factor = self._calculate_time_relevance(turn.timestamp, current_time)
                    
                    relevant_memories.append({
                        'type': 'conversation',
                        'content': f"Previous conversation: {turn.user_message}",
                        'relevance': turn_relevance * time_factor,
                        'date': turn.timestamp,
                        'original_text': turn.user_message
                    })
            
            # Sort by relevance score and return top results
            relevant_memories.sort(key=lambda x: x['relevance'], reverse=True)
            top_memories = relevant_memories[:max_memories]
            
            print(f"[Memory] ✅ Found {len(top_memories)} relevant memories for: '{question}'")
            for i, memory in enumerate(top_memories):
                print(f"[Memory] {i+1}. {memory['type']}: {memory['content'][:50]}... (score: {memory['relevance']:.2f})")
            
            return top_memories
            
        except Exception as e:
            print(f"[Memory] ❌ Error retrieving relevant memories: {e}")
            return []
    
    def _calculate_semantic_relevance(self, question: str, content: str, extra_content: str = "") -> float:
        """Calculate semantic relevance between question and memory content"""
        try:
            # Simple keyword matching approach (can be enhanced with embeddings later)
            question_words = set(question.split())
            
            # CRITICAL FIX: Split underscores and normalize content
            content_normalized = content.replace('_', ' ').replace('mcdonalds', 'mcdonald mcdonalds')
            extra_normalized = extra_content.replace('_', ' ').replace('mcdonalds', 'mcdonald mcdonalds')
            content_words = set(content_normalized.split() + extra_normalized.split())
            
            # Remove common words
            stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'is', 'was', 'are', 'were', 'have', 'has', 'had', 'do', 'does', 'did'}
            question_words = question_words - stop_words
            content_words = content_words - stop_words
            
            if not question_words or not content_words:
                return 0.0
            
            # Calculate Jaccard similarity
            intersection = len(question_words.intersection(content_words))
            union = len(question_words.union(content_words))
            
            jaccard_score = intersection / union if union > 0 else 0.0
            
            # Boost score for specific high-value matches
            high_value_matches = 0
            for word in question_words:
                if word in content_words:
                    # Boost location names, specific places
                    if word in ['mcdonalds', 'mcdonald', 'restaurant', 'shop', 'store', 'place']:
                        high_value_matches += 2
                    # Boost action words
                    elif word in ['went', 'go', 'visit', 'see', 'eat', 'buy', 'visited']:
                        high_value_matches += 1.5
                    else:
                        high_value_matches += 1
            
            # CRITICAL FIX: Special case for place + location questions
            question_lower = question.lower()
            content_lower = (content + " " + extra_content).lower()
            
            # Direct place name matching
            if 'mcdonald' in content_lower and ('where' in question_lower or 'go' in question_lower):
                high_value_matches += 3  # Strong boost for place + location questions
            
            # Activity matching patterns
            if 'visited' in content_lower and ('where' in question_lower or 'go' in question_lower):
                high_value_matches += 2
                
            # Combine Jaccard with high-value matches
            final_score = jaccard_score + (high_value_matches * 0.1)
            
            print(f"[Memory] 🎯 Relevance calc: jaccard={jaccard_score:.3f}, high_value={high_value_matches}, final={final_score:.3f}")
            
            return min(final_score, 1.0)  # Cap at 1.0
            
        except Exception as e:
            print(f"[Memory] ❌ Error calculating semantic relevance: {e}")
            return 0.0
    
    def _calculate_time_relevance(self, memory_time: str, current_time: datetime.datetime) -> float:
        """Calculate time-based relevance (recent events are more relevant)"""
        try:
            if isinstance(memory_time, str):
                memory_dt = datetime.datetime.strptime(memory_time, '%Y-%m-%d %H:%M:%S')
            else:
                memory_dt = memory_time
            
            # Calculate hours since memory
            hours_diff = (current_time - memory_dt).total_seconds() / 3600
            
            # Time decay function - recent memories get higher scores
            if hours_diff <= 1:        # Last hour
                return 1.0
            elif hours_diff <= 24:     # Last day
                return 0.9
            elif hours_diff <= 168:    # Last week
                return 0.7
            elif hours_diff <= 720:    # Last month
                return 0.5
            else:                      # Older than month
                return 0.3
                
        except Exception as e:
            print(f"[Memory] ❌ Error calculating time relevance: {e}")
            return 0.5  # Default relevance
    
    def get_contextual_memory_for_response(self, current_question: str = "") -> str:
        """🧠 Get memory context optimized for appropriate responses + SEMANTIC RETRIEVAL + TOKEN COMPRESSION + WORKING MEMORY"""
        context_parts = []
        
        # 🎯 SEMANTIC RETRIEVAL: Check if this is a temporal question requiring specific memories
        if current_question:
            relevant_memories = self.retrieve_relevant_memories(current_question)
            if relevant_memories:
                print(f"[Memory] 🎯 Using semantic retrieval for '{current_question}'")
                # Create memory context from relevant memories only
                memory_parts = []
                for memory in relevant_memories:
                    memory_parts.append(f"{memory['content']}")
                
                if memory_parts:
                    context_parts.append("Relevant memories: " + " | ".join(memory_parts))
                    # For semantic retrieval, return early with just relevant memories
                    result = "\n".join(context_parts)
                    print(f"[Memory] ✅ Semantic context: {len(result)} chars")
                    return result
        
        # 🧠 WORKING MEMORY: Include current action/context for reference resolution
        working_memory_context = self.get_working_memory_context_for_llm()
        if working_memory_context:
            context_parts.append(working_memory_context)
        
        # 🎯 PLAN CONTEXT: Include user's current plans if they exist
        user_plan = self.get_user_today_plan()
        if user_plan:
            context_parts.append(f"User's current plan: {user_plan}")
        
        # ✅ ENTROPY SYSTEM: Probabilistic memory retrieval instead of always best match
        if ENTROPY_AVAILABLE:
            entropy_engine = get_entropy_engine()
            uncertainty_state = entropy_engine.get_uncertainty_state()
            uncertainty_value = uncertainty_state.value if uncertainty_state else "normal"
            print(f"[Memory] 🌀 Probabilistic memory retrieval - uncertainty: {uncertainty_value}")
        
        # Recent personal facts with entity awareness + PROBABILISTIC SELECTION (COMPRESSED)
        all_facts = list(self.personal_facts.values())
        if ENTROPY_AVAILABLE and len(all_facts) > 4:
            # Don't always pick the most recent - inject uncertainty
            fact_weights = []
            for i, fact in enumerate(all_facts):
                # More recent facts get higher weight, but with entropy
                recency_weight = (i + 1) / len(all_facts)
                emotional_weight = getattr(fact, 'emotional_significance', 0.5)
                uncertainty_factor = inject_consciousness_entropy("memory", 1.0, EntropyLevel.LOW)
                final_weight = (recency_weight + emotional_weight) * uncertainty_factor
                fact_weights.append(final_weight)
            
            # Probabilistic selection of facts
            selected_facts = []
            for _ in range(min(3, len(all_facts))):  # Reduced from 4 to 3 for compression
                if all_facts:
                    selected_fact = probabilistic_select(all_facts, fact_weights)
                    if selected_fact and selected_fact not in selected_facts:
                        selected_facts.append(selected_fact)
                        # Remove from lists to avoid duplicates
                        fact_index = all_facts.index(selected_fact)
                        all_facts.pop(fact_index)
                        fact_weights.pop(fact_index)
            recent_facts = selected_facts
        else:
            recent_facts = all_facts[-3:]  # Reduced from 4 to 3
        
        for fact in recent_facts:
            # ✅ COMPRESSED: Shorter fact representation
            fact_text = f"{fact.key.replace('_', ' ')}: {fact.value}"
            if len(fact_text) > 50:  # Truncate long facts
                fact_text = fact_text[:47] + "..."
            
            if ENTROPY_AVAILABLE and entropy_engine.random_state.random() < 0.1:  # 10% chance of drift
                # Inject slight uncertainty into memory recall
                uncertainty_markers = ["I think ", "I believe ", ""]
                marker = probabilistic_select(uncertainty_markers)
                if marker:
                    fact_text = marker + fact_text.lower()
            
            if fact.current_status == EntityStatus.CURRENT:
                context_parts.append(fact_text)
            else:
                status_value = fact.current_status.value if fact.current_status else "unknown"
                context_parts.append(f"Former {fact_text} ({status_value})")
        
        # Critical entity statuses with UNCERTAIN RECALL (COMPRESSED)
        all_entities = list(self.entity_memories.values())
        critical_entities = [entity for entity in all_entities if entity.emotional_significance > 0.7]
        
        if ENTROPY_AVAILABLE and critical_entities:
            # Sometimes forget to mention all critical entities (memory imperfection)
            mention_probability = 0.8  # 80% chance to mention each entity
            entities_to_mention = []
            for entity in critical_entities:
                if entropy_engine.random_state.random() < mention_probability:
                    entities_to_mention.append(entity)
            critical_entities = entities_to_mention[:2]  # Limit to 2 for compression
        else:
            critical_entities = critical_entities[:2]  # Limit to 2
        
        for entity in critical_entities:
            status_value = entity.status.value if entity.status else "unknown"
            status_desc = f"{entity.name} ({entity.entity_type}): {status_value}"
            if entity.status == EntityStatus.DECEASED:
                status_desc += " - sensitive"  # Compressed warning
            
            # ✅ ENTROPY SYSTEM: Occasional false memory associations
            if ENTROPY_AVAILABLE and entropy_engine.random_state.random() < 0.05:  # 5% chance
                status_desc += " (uncertain)"
            
            context_parts.append(status_desc)
        
        # Recent emotional states with entity connections + UNCERTAIN RECALL (COMPRESSED)
        if self.emotional_history:
            if ENTROPY_AVAILABLE:
                # Don't always recall the most recent emotion - sometimes confusion
                emotion_weights = []
                for i, emotion in enumerate(self.emotional_history):
                    recency_weight = (i + 1) / len(self.emotional_history)
                    emotional_intensity = getattr(emotion, 'intensity', 0.5)
                    entropy_factor = inject_consciousness_entropy("memory", 1.0, EntropyLevel.LOW)
                    emotion_weights.append((recency_weight + emotional_intensity) * entropy_factor)
                
                recent_emotion = probabilistic_select(self.emotional_history, emotion_weights)
            else:
                recent_emotion = self.emotional_history[-1]
            
            # ✅ COMPRESSED: Shorter emotion context
            emotion_context = f"Recent: {recent_emotion.emotion} - {recent_emotion.context[:30]}..."
            if recent_emotion.trigger_entities:
                emotion_context += f" (re: {', '.join(recent_emotion.trigger_entities[:2])})"  # Limit entities
            
            # ✅ ENTROPY SYSTEM: Uncertainty about emotional memories
            uncertainty_state = entropy_engine.get_uncertainty_state() if ENTROPY_AVAILABLE else None
            if ENTROPY_AVAILABLE and uncertainty_state and uncertainty_state.value == "uncertain":
                emotion_context = "Unsure: " + emotion_context.lower()
            
            context_parts.append(emotion_context)
        
        # Active life events with ongoing effects + MEMORY DRIFT (COMPRESSED)
        all_events = list(self.life_events.values())
        if ENTROPY_AVAILABLE and len(all_events) > 2:  # Reduced from 3 to 2
            # Probabilistic event selection with emphasis on emotional impact
            event_weights = []
            for event in all_events:
                impact_weight = event.emotional_impact
                recency_weight = 0.5  # Less emphasis on recency for major events
                uncertainty_factor = inject_consciousness_entropy("memory", 1.0, EntropyLevel.LOW)
                event_weights.append((impact_weight + recency_weight) * uncertainty_factor)
            
            selected_events = []
            remaining_events = all_events.copy()
            remaining_weights = event_weights.copy()
            
            for _ in range(min(2, len(all_events))):  # Reduced from 3 to 2
                if remaining_events:
                    selected_event = probabilistic_select(remaining_events, remaining_weights)
                    if selected_event:
                        selected_events.append(selected_event)
                        event_index = remaining_events.index(selected_event)
                        remaining_events.pop(event_index)
                        remaining_weights.pop(event_index)
            recent_events = selected_events
        else:
            recent_events = all_events[-2:]  # Reduced from 3 to 2
        
        for event in recent_events:
            if event.ongoing_effects:
                # ✅ COMPRESSED: Shorter event description
                event_desc = f"Event: {event.description[:40]}... - Effects: {', '.join(event.ongoing_effects[:2])}"
                
                # ✅ ENTROPY SYSTEM: Occasional confusion about event timeline
                if ENTROPY_AVAILABLE and entropy_engine.random_state.random() < 0.08:  # 8% chance
                    timeline_confusion = ["recent", "ago", "unsure when"]
                    confusion = probabilistic_select(timeline_confusion)
                    event_desc = event_desc.replace("Event:", f"Event ({confusion}):")
                
                context_parts.append(event_desc)
        
        # ✅ ENTROPY SYSTEM: Random memory association (false memories) - COMPRESSED
        if ENTROPY_AVAILABLE and entropy_engine.random_state.random() < 0.02:  # Reduced from 3% to 2%
            false_memory_fragments = [
                "Music preferences",
                "Travel thoughts", 
                "Food/restaurant talk",
                "Weather discussion",
                "Work routine"
            ]
            false_memory = probabilistic_select(false_memory_fragments)
            context_parts.append(f"(Vague: {false_memory})")
            print(f"[Memory] 🌀 False memory: {false_memory}")
        
        result = "\n".join(context_parts) if context_parts else ""
        
        # ✅ TOKEN COMPRESSION: Limit total memory context size
        from ai.prompt_compressor import prompt_compressor
        if len(result) > 300:  # Keep memory context under 300 chars (~75 tokens)
            result = prompt_compressor.optimize_context_for_budget(result, 75)
        
        # ✅ ENTROPY SYSTEM: Overall memory confidence uncertainty
        if ENTROPY_AVAILABLE and result:
            consciousness_score = entropy_engine.get_consciousness_metrics()['consciousness_score']
            if consciousness_score > 0.6 and entropy_engine.random_state.random() < 0.05:  # Reduced from 10% to 5%
                result = "Note: Memory uncertain.\n" + result
        
        print(f"[Memory] 🗜️ Compressed memory context: {len(result)} chars")
        return result
    
    # Enhanced extraction methods with entity awareness
    def extract_memories_from_text(self, text: str):
        """🧠 MEGA-INTELLIGENT memory extraction with entity tracking + WORKING MEMORY"""
        try:
            text_lower = text.lower().strip()
            
            # 🧠 WORKING MEMORY: Update current action/context tracking
            self.update_working_memory(text_lower, text)
            
            # 🧠 WORKING MEMORY: Track multi-turn intentions
            self.track_intent_across_turns(text_lower, text)
            
            # 🧠 WORKING MEMORY: Detect and resolve vague references
            reference_resolution = self.detect_and_resolve_references(text_lower)
            
            # 🧠 CRITICAL: Death and loss detection
            self._extract_death_and_loss_events(text_lower, text)
            
            # 🧠 Enhanced personal facts with entity awareness
            self._extract_enhanced_personal_facts(text_lower, text)
            
            # 🧠 Enhanced emotional states with entity connections
            self._extract_enhanced_emotional_states(text_lower, text)
            
            # 🧠 Relationship status changes
            self._extract_relationship_changes(text_lower, text)
            
            # 🧠 Enhanced events with entity connections
            self._extract_enhanced_events(text_lower, text)
            
            # 🎯 PLAN DETECTION: Extract user plans for today/future
            self._detect_user_plan_for_today(text_lower, text)
            
        except Exception as e:
            if DEBUG:
                print(f"[MegaMemory] ❌ Enhanced extraction error: {e}")
    
    def _extract_death_and_loss_events(self, text_lower: str, original_text: str):
        """🧠 CRITICAL: Extract death and loss events with high emotional significance"""
        death_patterns = [
            (r"my (\w+) (died|passed away|passed|is dead|has died)", "death", "{0}", EmotionalImpact.CRITICAL.value),
            (r"(\w+) died", "death", "{0}", EmotionalImpact.CRITICAL.value),
            (r"(\w+) passed away", "death", "{0}", EmotionalImpact.CRITICAL.value),
            (r"lost my (\w+)", "loss", "{0}", EmotionalImpact.HIGH.value),
            (r"put (\w+) down", "euthanasia", "{0}", EmotionalImpact.CRITICAL.value),
            (r"had to say goodbye to (\w+)", "death", "{0}", EmotionalImpact.CRITICAL.value),
            (r"(\w+) is no longer with us", "death", "{0}", EmotionalImpact.CRITICAL.value),
        ]
        
        for pattern, event_type, name_template, emotional_impact in death_patterns:
            match = re.search(pattern, text_lower)
            if match:
                entity_name = name_template.format(match.group(1))
                
                # Determine entity type
                entity_type = self._determine_entity_type(entity_name, original_text)
                
                # Add entity memory
                self.add_entity_memory(
                    name=entity_name,
                    entity_type=entity_type,
                    status=EntityStatus.DECEASED,
                    emotional_significance=emotional_impact,
                    context=original_text
                )
                
                # Add life event
                self.add_life_event(
                    event_type=event_type,
                    description=f"{entity_name} {event_type}",
                    entities_involved=[entity_name],
                    emotional_impact=emotional_impact,
                    ongoing_effects=["grieving", "emotional_sensitivity_needed"]
                )
                
                print(f"[MegaMemory] 💔 CRITICAL EVENT: {entity_name} death/loss detected")
    
    def _determine_entity_type(self, name: str, context: str) -> str:
        """Determine entity type from context"""
        context_lower = context.lower()
        
        pet_indicators = ["cat", "dog", "pet", "puppy", "kitten", "bird", "fish", "hamster"]
        person_indicators = ["mom", "dad", "mother", "father", "friend", "sister", "brother", "grandmother", "grandfather"]
        
        if any(indicator in context_lower for indicator in pet_indicators):
            return "pet"
        elif any(indicator in context_lower for indicator in person_indicators):
            return "person"
        else:
            return "unknown"
    
    def _extract_relationship_changes(self, text_lower: str, original_text: str):
        """Extract relationship status changes"""
        relationship_patterns = [
            (r"my (ex|former) (\w+)", "relationship_end", "{1}", EntityStatus.ENDED),
            (r"broke up with (\w+)", "breakup", "{0}", EntityStatus.ENDED),
            (r"divorced (\w+)", "divorce", "{0}", EntityStatus.ENDED),
            (r"separated from (\w+)", "separation", "{0}", EntityStatus.ENDED),
        ]
        
        for pattern, event_type, name_template, status in relationship_patterns:
            match = re.search(pattern, text_lower)
            if match:
                entity_name = name_template.format(*match.groups())
                
                self.add_entity_memory(
                    name=entity_name,
                    entity_type="relationship",
                    status=status,
                    emotional_significance=EmotionalImpact.HIGH.value,
                    context=original_text
                )
                
                print(f"[MegaMemory] 💔 Relationship change: {entity_name} - {status.value}")
    
    def _extract_enhanced_personal_facts(self, text_lower: str, original_text: str):
        """Enhanced personal fact extraction with entity awareness"""
        enhanced_patterns = [
            # Physical attributes
            (r"my shoe size is (\d+)", "physical", "shoe_size", EntityStatus.CURRENT),
            (r"i'm (\d+) years old", "physical", "age", EntityStatus.CURRENT),
            
            # Preferences with entity awareness
            (r"i love my (\w+)", "preferences", "loves_{0}", EntityStatus.CURRENT),
            (r"i hate (\w+)", "preferences", "dislikes_{0}", EntityStatus.CURRENT),
            (r"i used to love (\w+)", "preferences", "formerly_loved_{0}", EntityStatus.FORMER),
            
            # Possessions with status
            (r"i have a (\w+)", "possessions", "owns_{0}", EntityStatus.CURRENT),
            (r"i used to have a (\w+)", "possessions", "formerly_owned_{0}", EntityStatus.FORMER),
            (r"i sold my (\w+)", "possessions", "sold_{0}", EntityStatus.SOLD),
            
            # Medical with ongoing status
            (r"i'm allergic to (\w+)", "medical", "allergy_{0}", EntityStatus.CURRENT),
            (r"i have (\w+) condition", "medical", "condition_{0}", EntityStatus.CURRENT),
            
            # CRITICAL FIX: Place visits and activities - SPECIFIC PATTERNS FIRST WITH COMPANIONS
            # Patterns with companions (who they went with)
            (r"went to mcdonalds? with (\w+)", "activities", "visited_mcdonalds_with_{0}", EntityStatus.CURRENT),
            (r"went to mcdonald'?s? with (\w+)", "activities", "visited_mcdonalds_with_{0}", EntityStatus.CURRENT),
            (r"been to mcdonalds? with (\w+)", "activities", "been_to_mcdonalds_with_{0}", EntityStatus.CURRENT),
            (r"been to mcdonald'?s? with (\w+)", "activities", "been_to_mcdonalds_with_{0}", EntityStatus.CURRENT),
            (r"(\w+ to \w+) with (\w+)", "activities", "{0}_with_{1}", EntityStatus.CURRENT),
            # Special patterns for common places MUST come first to match before generic patterns
            (r"went to mcdonalds", "activities", "visited_mcdonalds", EntityStatus.CURRENT),
            (r"went to mcdonald's", "activities", "visited_mcdonalds", EntityStatus.CURRENT), 
            (r"went to mcdonald", "activities", "visited_mcdonalds", EntityStatus.CURRENT),
            (r"been to mcdonalds", "activities", "visited_mcdonalds", EntityStatus.CURRENT),
            (r"been to mcdonald's", "activities", "visited_mcdonalds", EntityStatus.CURRENT),
            (r"been to mcdonald", "activities", "visited_mcdonalds", EntityStatus.CURRENT),
            # Generic patterns after specific ones
            (r"i went to (\w+)", "activities", "visited_{0}", EntityStatus.CURRENT),
            (r"went to (\w+)", "activities", "visited_{0}", EntityStatus.CURRENT),
            (r"i was at (\w+)", "activities", "was_at_{0}", EntityStatus.CURRENT),
            (r"visited (\w+)", "activities", "visited_{0}", EntityStatus.CURRENT),
            (r"been to (\w+)", "activities", "been_to_{0}", EntityStatus.CURRENT),
            (r"ate at (\w+)", "activities", "ate_at_{0}", EntityStatus.CURRENT),
            (r"had (\w+) at (\w+)", "activities", "had_{0}_at_{1}", EntityStatus.CURRENT),
        ]
        
        for pattern, category, key_template, status in enhanced_patterns:
            match = re.search(pattern, text_lower)
            if match:
                key = key_template.format(*match.groups()) if "{0}" in key_template else key_template
                
                # CRITICAL FIX: Handle specific patterns vs generic patterns for value
                if "mcdonalds" in key_template and not match.groups():
                    value = "mcdonalds"  # Fixed value for McDonald's patterns without capture groups
                elif "mcdonalds_with_" in key_template:
                    value = f"mcdonalds with {match.group(1)}"  # McDonald's with companion
                elif match.groups():
                    if len(match.groups()) == 1:
                        value = match.group(1)  # Single capture group
                    elif len(match.groups()) == 2:
                        value = f"{match.group(1)} with {match.group(2)}"  # Activity with companion
                    else:
                        value = " ".join(match.groups())  # Multiple capture groups
                else:
                    value = "activity"  # Fallback for patterns without capture groups
                
                fact = PersonalFact(
                    category=category,
                    key=key,
                    value=value,
                    confidence=0.8,
                    date_learned=datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
                    last_mentioned=datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
                    source_context=original_text,
                    current_status=status
                )
                
                self.personal_facts[f"{category}_{key}"] = fact
    
    def _extract_enhanced_emotional_states(self, text_lower: str, original_text: str):
        """Enhanced emotional state extraction with entity connections"""
        emotion_patterns = [
            (r"i'm (sad|depressed|down|upset) about (\w+)", "sad", 7, "{1}"),
            (r"i'm (happy|excited|thrilled) about (\w+)", "happy", 8, "{1}"),
            (r"missing (\w+)", "sad", 6, "{0}"),
            (r"grieving (\w+)", "sad", 8, "{0}"),
            (r"i miss (\w+)", "sad", 7, "{0}"),
        ]
        
        for pattern, emotion, intensity, entity_template in emotion_patterns:
            match = re.search(pattern, text_lower)
            if match:
                trigger_entity = entity_template.format(*match.groups()) if entity_template else None
                
                state = EmotionalState(
                    emotion=emotion,
                    intensity=intensity,
                    context=original_text,
                    date=datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
                    follow_up_needed=True,
                    trigger_entities=[trigger_entity] if trigger_entity else []
                )
                
                self.emotional_history.append(state)
                print(f"[MegaMemory] 😢 Emotional state: {emotion} about {trigger_entity}")
    
    def _extract_enhanced_events(self, text_lower: str, original_text: str):
        """Enhanced event extraction with entity connections"""
        event_patterns = [
            (r"(?:it's|its) my (\w+)'s birthday tomorrow", "birthday", "{0}'s birthday", 1, ["{0}"]),
            (r"(\w+)'s funeral is tomorrow", "funeral", "{0}'s funeral", 1, ["{0}"]),
            (r"visiting (\w+) tomorrow", "visit", "visiting {0}", 1, ["{0}"]),
        ]
        
        for pattern, event_type, desc_template, days_ahead, entities_template in event_patterns:
            match = re.search(pattern, text_lower)
            if match:
                description = desc_template.format(*match.groups())
                entities = [template.format(*match.groups()) for template in entities_template]
                
                event_date = (datetime.datetime.utcnow() + 
                            datetime.timedelta(days=days_ahead)).strftime('%Y-%m-%d')
                
                event = ScheduledEvent(
                    event_type=event_type,
                    description=description,
                    date=event_date,
                    reminder_dates=[event_date],
                    completed=False,
                    related_entities=entities
                )
                
                self.scheduled_events.append(event)
    
    def _detect_user_plan_for_today(self, text_lower: str, original_text: str):
        """🎯 PLAN DETECTION: Extract user plans for today/immediate future"""
        try:
            today = datetime.datetime.utcnow().strftime('%Y-%m-%d')
            current_time = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            
            # Plan patterns for today and immediate future
            plan_patterns = [
                # Today specific plans (high priority)
                (r"i'm going to (?:my\s+)?(.+?)\s+(?:birthday party|party)\s+today", "going to {0} birthday party"),
                (r"i'm going to (.+?)\s+today", "going to {0}"),
                (r"today i'm (.+?)(?:\.|$)", "i'm {0}"),
                (r"i have (?:a\s+)?(.+?)\s+today", "have {0}"),
                (r"i'm (?:having|attending) (?:a\s+)?(.+?)\s+today", "attending {0}"),
                (r"my (.+?)\s+(?:birthday|party) is today", "my {0} birthday"),
                
                # General plans without time indicator (considered for today)
                (r"i'm going to (?:my\s+)?(.+?)\s+(?:birthday party|party)(?:\.|$)", "going to {0} birthday party"),
                (r"i'll be at (?:the\s+)?(.+?)(?:\.|$)", "will be at {0}"),
                (r"i have plans? to (.+?)(?:\.|$)", "plan to {0}"),
                (r"planning to (.+?)(?:\.|$)", "planning to {0}"),
            ]
            
            # Tomorrow plans (separate category, not considered "today")
            tomorrow_patterns = [
                (r"tomorrow i'm going to (.+?)(?:\.|$)", "going to {0} tomorrow"),
                (r"i'm going to (.+?)\s+tomorrow", "going to {0} tomorrow"),
            ]
            
            plan_detected = False
            
            # First check for today plans
            for pattern, plan_template in plan_patterns:
                match = re.search(pattern, text_lower)
                if match:
                    plan_description = plan_template.format(match.group(1).strip())
                    
                    # Store the plan (replace any existing plan)
                    self.user_today_plan = plan_description
                    self.plan_timestamp = current_time
                    self.plan_context = original_text
                    
                    print(f"[MegaMemory] 🎯 Plan detected: {plan_description}")
                    plan_detected = True
                    break
            
            # Check for tomorrow plans (do not store as today's plan)
            if not plan_detected:
                for pattern, plan_template in tomorrow_patterns:
                    match = re.search(pattern, text_lower)
                    if match:
                        plan_description = plan_template.format(match.group(1).strip())
                        print(f"[MegaMemory] 📅 Tomorrow plan noted: {plan_description}")
                        # Don't store tomorrow plans as today's plan
                        plan_detected = True
                        break
                    
            # Special handling for family events and celebrations
            if not plan_detected:
                family_event_patterns = [
                    (r"(?:i'm going to|going to) (?:my\s+)?(.+?)\s+(?:birthday|celebration|party)", "{0} celebration"),
                    (r"it's (?:my\s+)?(.+?)'s birthday", "{0}'s birthday"),
                    (r"celebrating (?:my\s+)?(.+?)'s (.+?)(?:\.|$)", "{0}'s {1}"),
                ]
                
                for pattern, plan_template in family_event_patterns:
                    match = re.search(pattern, text_lower)
                    if match:
                        groups = match.groups()
                        if len(groups) == 1:
                            plan_description = plan_template.format(groups[0].strip())
                        else:
                            plan_description = plan_template.format(groups[0].strip(), groups[1].strip())
                        
                        self.user_today_plan = plan_description
                        self.plan_timestamp = current_time
                        self.plan_context = original_text
                        
                        print(f"[MegaMemory] 🎯 Family plan detected: {plan_description}")
                        break
                        
            # Save memory if plan was detected
            if self.user_today_plan:
                self.save_memory()
                
        except Exception as e:
            if DEBUG:
                print(f"[MegaMemory] ❌ Plan detection error: {e}")
    
    def has_user_plan_for_today(self) -> bool:
        """🎯 Check if user has already mentioned plans for today"""
        if not self.user_today_plan:
            return False
            
        # Check if plan is still relevant (within last 24 hours)
        if self.plan_timestamp:
            try:
                plan_time = datetime.datetime.strptime(self.plan_timestamp, '%Y-%m-%d %H:%M:%S')
                now = datetime.datetime.utcnow()
                hours_since_plan = (now - plan_time).total_seconds() / 3600
                
                # Plans are relevant for 24 hours
                return hours_since_plan < 24
            except Exception:
                return True  # If we can't parse timestamp, assume plan is still relevant
                
        return True
    
    def get_user_today_plan(self) -> Optional[str]:
        """🎯 Get user's plan for today if exists"""
        if self.has_user_plan_for_today():
            return self.user_today_plan
        return None
    
    def clear_outdated_plans(self):
        """🎯 Clear plans that are no longer relevant"""
        if not self.has_user_plan_for_today():
            self.user_today_plan = None
            self.plan_timestamp = None
            self.plan_context = None
    
    def should_ask_about_plans(self) -> Tuple[bool, str]:
        """🎯 Check if Buddy should ask about user plans, with context if not"""
        if self.has_user_plan_for_today():
            plan = self.get_user_today_plan()
            return False, f"User already mentioned their plan: {plan}"
        else:
            return True, "No current plan detected - safe to ask about plans"
    
    # 🧠 WORKING MEMORY TRACKING METHODS
    def update_working_memory(self, text: str, original_text: str):
        """🧠 MULTI-CONTEXT: Update working memory with multiple simultaneous contexts"""
        try:
            text_lower = text.lower().strip()
            current_time = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            
            # 🎯 STEP 1: Parse for multiple events in compound statements
            contexts = self._parse_multi_context_statement(text_lower, original_text)
            
            # 🎯 STEP 2: Add detected contexts to working memory
            for context in contexts:
                context_id = f"ctx_{int(time.time())}_{len(self.working_memory.active_contexts)}"
                context.context_id = context_id
                context.timestamp = current_time
                
                self.working_memory.active_contexts[context_id] = context
                self.working_memory.context_sequence.append(context_id)
                
                print(f"[MultiContext] ➕ Added: {context.description} ({context.event_type})")
            
            # 🎯 STEP 3: Update backward compatibility fields with most recent/important context
            if contexts:
                primary_context = contexts[0]  # Use first/primary context
                self.working_memory.last_action = primary_context.description
                self.working_memory.last_place = primary_context.place
                self.working_memory.last_topic = self._extract_topic_from_action(primary_context.description, original_text)
                self.working_memory.last_timestamp = current_time
                self.working_memory.action_status = primary_context.status
            
            # 🎯 STEP 4: Fallback to original single-context parsing if no contexts detected
            if not contexts:
                self._update_single_context_fallback(text_lower, original_text, current_time)
            
            # 🎯 STEP 5: Clean up old/completed contexts (keep max 10 active)
            self._cleanup_old_contexts()
            
            self.save_memory()
            
        except Exception as e:
            if DEBUG:
                print(f"[WorkingMemory] ❌ Update error: {e}")

    def _parse_multi_context_statement(self, text_lower: str, original_text: str) -> List[ContextItem]:
        """🧠 Parse compound statements to extract multiple events/contexts"""
        contexts = []
        
        # 🎯 COMPOUND STATEMENT PATTERNS: Detect multiple events in one statement
        compound_patterns = [
            # "going to X and then Y" - sequential events
            (r"(?:i'm\s+)?going (?:to\s+)?(.+?)\s+and then (?:also\s+)?(?:to\s+)?(.+?)(?:\.|$)", "sequential"),
            (r"(?:i'm\s+)?going (?:for\s+)?(.+?)\s+and then (?:also\s+)?(?:to\s+)?(.+?)(?:\.|$)", "sequential"),
            
            # "doing X and Y" - parallel events
            (r"(?:i'm\s+)?(?:doing|planning|having) (.+?)\s+and (?:also\s+)?(.+?)(?:\.|$)", "parallel"),
            
            # "X then Y" patterns
            (r"(.+?)\s+then (?:i'm\s+)?(?:going\s+)?(?:to\s+)?(.+?)(?:\.|$)", "sequential"),
            
            # "X and Y" - general parallel
            (r"(?:i'm\s+)?(.+?)\s+and (?:then\s+)?(?:also\s+)?(.+?)(?:\.|$)", "parallel"),
        ]
        
        for pattern, relationship_type in compound_patterns:
            match = re.search(pattern, text_lower)
            if match:
                event1_text, event2_text = match.groups()
                
                # Clean up the event descriptions
                event1_text = self._clean_event_description(event1_text)
                event2_text = self._clean_event_description(event2_text)
                
                if event1_text and event2_text:
                    # Create context for first event
                    context1 = self._create_context_from_description(event1_text, original_text, priority=1)
                    
                    # Create context for second event
                    context2 = self._create_context_from_description(event2_text, original_text, priority=2)
                    
                    # Set relationship between contexts
                    if relationship_type == "sequential":
                        context1.status = "planned"
                        context2.status = "planned"
                        context2.time_reference = "after " + event1_text
                    elif relationship_type == "parallel":
                        context1.status = "planned" 
                        context2.status = "planned"
                    
                    contexts.extend([context1, context2])
                    print(f"[MultiContext] 🔗 Parsed {relationship_type}: '{event1_text}' + '{event2_text}'")
                    break
        
        # 🎯 SINGLE EVENT PATTERNS: If no compound found, try single event
        if not contexts:
            single_context = self._parse_single_event(text_lower, original_text)
            if single_context:
                contexts.append(single_context)
        
        return contexts
    
    def _clean_event_description(self, event_text: str) -> str:
        """Clean and normalize event descriptions"""
        event_text = event_text.strip()
        
        # Remove common prefixes/suffixes
        prefixes_to_remove = ["going to", "going for", "i'm", "im", "to", "for"]
        for prefix in prefixes_to_remove:
            if event_text.startswith(prefix + " "):
                event_text = event_text[len(prefix):].strip()
        
        # Remove trailing prepositions
        suffixes_to_remove = [" to", " for", " at"]
        for suffix in suffixes_to_remove:
            if event_text.endswith(suffix):
                event_text = event_text[:-len(suffix)].strip()
        
        return event_text
    
    def _create_context_from_description(self, description: str, original_text: str, priority: int = 1) -> ContextItem:
        """Create a ContextItem from an event description"""
        
        # 🎯 EVENT TYPE CLASSIFICATION
        event_type = self._classify_event_type(description)
        
        # 🎯 PLACE EXTRACTION
        place = self._extract_place_from_description(description)
        
        # 🎯 TIME REFERENCE EXTRACTION
        time_ref = self._extract_time_reference(original_text)
        
        return ContextItem(
            context_id="",  # Will be set later
            event_type=event_type,
            description=description,
            place=place,
            time_reference=time_ref,
            status="planned",
            priority=priority,
            timestamp="",  # Will be set later
            related_contexts=[],
            completion_status=0.0
        )
    
    def _classify_event_type(self, description: str) -> str:
        """Classify the type of event/context"""
        desc_lower = description.lower()
        
        # Medical/health patterns
        if any(word in desc_lower for word in ["doctor", "gp", "appointment", "checkup", "check", "medical", "dentist", "hospital"]):
            return "medical_appointment"
        
        # Social event patterns
        if any(word in desc_lower for word in ["birthday", "party", "wedding", "celebration", "dinner", "lunch", "meeting friends"]):
            return "social_event"
        
        # Work/business patterns
        if any(word in desc_lower for word in ["work", "office", "meeting", "conference", "business", "interview"]):
            return "work_task"
        
        # Shopping patterns
        if any(word in desc_lower for word in ["shop", "shopping", "store", "buy", "purchase", "groceries"]):
            return "shopping_task"
        
        # Travel patterns
        if any(word in desc_lower for word in ["airport", "flight", "train", "travel", "trip", "vacation"]):
            return "travel_event"
        
        # Home/personal patterns
        if any(word in desc_lower for word in ["home", "house", "cleaning", "cooking", "repair", "fix"]):
            return "personal_task"
        
        return "general_event"
    
    def _extract_place_from_description(self, description: str) -> Optional[str]:
        """Extract place/location from event description"""
        desc_lower = description.lower()
        
        # Common place patterns
        place_patterns = [
            (r"at (?:the\s+)?(.+?)(?:\s|$)", "{0}"),
            (r"in (?:the\s+)?(.+?)(?:\s|$)", "{0}"),
            (r"(?:doctor|gp|dentist)", "doctor's office"),
            (r"(?:shop|store|mall)", "shop"),
            (r"(?:office|work)", "office"),
            (r"(?:restaurant|cafe|bar)", "restaurant"),
            (r"(?:home|house)", "home"),
        ]
        
        for pattern, place_template in place_patterns:
            match = re.search(pattern, desc_lower)
            if match:
                if "{" in place_template:
                    return place_template.format(match.group(1))
                else:
                    return place_template
        
        return None
    
    def _extract_time_reference(self, original_text: str) -> Optional[str]:
        """Extract time references from original text"""
        text_lower = original_text.lower()
        
        time_patterns = [
            (r"(today|tomorrow|yesterday)", "{0}"),
            (r"(this morning|this afternoon|this evening|tonight)", "{0}"),
            (r"(next week|next month|next year)", "{0}"),
            (r"(in \d+ hours?|in \d+ days?|in \d+ weeks?)", "{0}"),
            (r"(at \d+(?::\d+)?(?:\s*(?:am|pm))?)", "{0}"),
            (r"(after .+?)(?:\s|$)", "{0}"),
        ]
        
        for pattern, time_template in time_patterns:
            match = re.search(pattern, text_lower)
            if match:
                return time_template.format(match.group(1))
        
        return None
    
    def _parse_single_event(self, text_lower: str, original_text: str) -> Optional[ContextItem]:
        """Parse single event if no compound statement detected"""
        
        # Original single-action patterns (adapted for ContextItem)
        single_patterns = [
            (r"i'm (making|cooking|preparing) (.+?)(?:\.|$)", "personal_task", "{0} {1}", "kitchen"),
            (r"i'm (going to|heading to) (?:the\s+)?(.+?)(?:\.|$)", "general_event", "going to {1}", "{1}"),
            (r"i'm (working on|doing) (.+?)(?:\.|$)", "work_task", "{0} {1}", "office"),
            (r"i'm about to (go to|visit|see) (?:the\s+)?(.+?)(?:\.|$)", "general_event", "going to {1}", "{1}"),
        ]
        
        for pattern, event_type, desc_template, place_hint in single_patterns:
            match = re.search(pattern, text_lower)
            if match:
                groups = match.groups()
                description = desc_template.format(*groups) if "{" in desc_template else desc_template
                
                place = None
                if place_hint and "{" in place_hint:
                    place = place_hint.format(*groups)
                elif place_hint:
                    place = place_hint
                
                return ContextItem(
                    context_id="",
                    event_type=event_type,
                    description=description,
                    place=place,
                    time_reference=self._extract_time_reference(original_text),
                    status="planned",
                    priority=1,
                    timestamp="",
                    related_contexts=[],
                    completion_status=0.0
                )
        
        return None
    
    def _update_single_context_fallback(self, text_lower: str, original_text: str, current_time: str):
        """Fallback to original single-context logic for backward compatibility"""
        
        # Goal detection patterns  
        goal_patterns = [
            (r"to (buy|get|pick up) (.+?)(?:\.|$)", "{0} {1}"),
            (r"to (make|cook|prepare) (.+?)(?:\.|$)", "{0} {1}"),
            (r"to (visit|see|meet) (.+?)(?:\.|$)", "{0} {1}"),
            (r"for (.+?)(?:\.|$)", "for {0}"),
        ]
        
        # Place patterns
        place_patterns = [
            (r"at (?:the\s+)?(.+?)(?:\.|$)", "{0}"),
            (r"in (?:the\s+)?(.+?)(?:\.|$)", "{0}"),
            (r"from (?:the\s+)?(.+?)(?:\.|$)", "{0}"),
        ]
        
        # Check for goal/intent updates
        for pattern, goal_template in goal_patterns:
            match = re.search(pattern, text_lower)
            if match:
                goal = goal_template.format(*match.groups())
                self.working_memory.last_goal = goal
                print(f"[WorkingMemory] 🎯 Goal: {goal}")
                break
        
        # Check for place references
        if not self.working_memory.last_place:
            for pattern, place_template in place_patterns:
                match = re.search(pattern, text_lower)
                if match:
                    place = place_template.format(match.group(1))
                    self.working_memory.last_place = place
                    print(f"[WorkingMemory] 📍 Place: {place}")
                    break
    
    def _cleanup_old_contexts(self):
        """Clean up old/completed contexts to prevent memory bloat"""
        max_active_contexts = 10
        
        if len(self.working_memory.active_contexts) > max_active_contexts:
            # Remove oldest completed contexts first
            contexts_to_remove = []
            for context_id, context in self.working_memory.active_contexts.items():
                if context.status == "completed" and context.completion_status >= 1.0:
                    contexts_to_remove.append(context_id)
            
            # Remove oldest contexts if still too many
            if len(self.working_memory.active_contexts) - len(contexts_to_remove) > max_active_contexts:
                oldest_contexts = sorted(
                    self.working_memory.context_sequence[:-max_active_contexts]
                )
                contexts_to_remove.extend(oldest_contexts)
            
            # Actually remove the contexts
            for context_id in contexts_to_remove:
                if context_id in self.working_memory.active_contexts:
                    del self.working_memory.active_contexts[context_id]
                if context_id in self.working_memory.context_sequence:
                    self.working_memory.context_sequence.remove(context_id)
            
            if contexts_to_remove:
                print(f"[MultiContext] 🧹 Cleaned up {len(contexts_to_remove)} old contexts")
    
    def detect_and_resolve_references(self, text: str) -> Optional[ReferenceResolution]:
        """🧠 MULTI-CONTEXT: Detect vague references and resolve them using all active contexts"""
        try:
            text_lower = text.lower().strip()
            
            # Vague reference patterns
            vague_patterns = [
                # Completion references
                (r"(i just finished|i finished|i'm done|i did it)(?:\.|$)", "completion"),
                (r"(it went well|it was good|it was great|that went well)(?:\.|$)", "outcome"),
                (r"(i just came back|i'm back|i returned)(?:\.|$)", "return"),
                (r"(i'm ready|i'm all set|ready to go)(?:\.|$)", "ready"),
                (r"(that was hard|that was easy|that was fun)(?:\.|$)", "evaluation"),
                (r"(i got it|i found it|i have it)(?:\.|$)", "acquisition"),
                
                # Status references
                (r"(it's done|it's finished|it's ready)(?:\.|$)", "completion"),
                (r"(it worked|it didn't work)(?:\.|$)", "result"),
                (r"(i'm there|i arrived|i made it)(?:\.|$)", "arrival"),
                
                # Multi-context references
                (r"(both are done|both went well|finished both)(?:\.|$)", "multiple_completion"),
                (r"(the first one|the second one|the next one)(?:\.|$)", "sequence_reference"),
            ]
            
            for pattern, reference_type in vague_patterns:
                match = re.search(pattern, text_lower)
                if match:
                    vague_phrase = match.group(1)
                    
                    # Resolve based on multi-context working memory
                    resolution = self._resolve_reference_from_multi_context(vague_phrase, reference_type)
                    if resolution:
                        # Store the resolution
                        self.reference_history.append(resolution)
                        print(f"[MultiReference] 🔗 '{vague_phrase}' → '{resolution.likely_referent}'")
                        return resolution
            
            return None
            
        except Exception as e:
            if DEBUG:
                print(f"[Reference] ❌ Resolution error: {e}")
            return None

    def _resolve_reference_from_multi_context(self, vague_phrase: str, reference_type: str) -> Optional[ReferenceResolution]:
        """🧠 MULTI-CONTEXT: Resolve vague reference using all active contexts"""
        
        # Get most recent/relevant contexts
        active_contexts = list(self.working_memory.active_contexts.values())
        if not active_contexts:
            # Fallback to single-context resolution
            return self._resolve_reference_from_working_memory(vague_phrase, reference_type)
        
        likely_referent = None
        confidence = 0.0
        context_source = "multi_context"
        
        if reference_type == "completion":
            # Find most recently active context
            recent_context = self._get_most_recent_active_context()
            if recent_context:
                likely_referent = f"finished {recent_context.description}"
                confidence = 0.8
                # Update context status
                recent_context.status = "completed"
                recent_context.completion_status = 1.0
            else:
                # Fallback: look for any active context
                for context in active_contexts:
                    if context.status in ["ongoing", "planned"]:
                        likely_referent = f"finished {context.description}"
                        confidence = 0.7
                        context.status = "completed"
                        context.completion_status = 1.0
                        break
        
        elif reference_type == "multiple_completion":
            # Multiple contexts completed
            active_count = len([c for c in active_contexts if c.status in ["ongoing", "planned"]])
            if active_count >= 2:
                context_descriptions = [c.description for c in active_contexts[:2]]
                likely_referent = f"finished {' and '.join(context_descriptions)}"
                confidence = 0.9
                # Update multiple contexts
                for context in active_contexts[:2]:
                    context.status = "completed"
                    context.completion_status = 1.0
        
        elif reference_type == "sequence_reference":
            # Reference to specific item in sequence
            if "first" in vague_phrase and len(active_contexts) >= 1:
                # Get first context by sequence
                first_context = None
                if self.working_memory.context_sequence:
                    first_context_id = self.working_memory.context_sequence[0]
                    first_context = self.working_memory.active_contexts.get(first_context_id)
                
                if first_context:
                    likely_referent = f"the first event: {first_context.description}"
                    confidence = 0.9
                else:
                    likely_referent = f"the first event: {active_contexts[0].description}"
                    confidence = 0.8
            elif "second" in vague_phrase and len(active_contexts) >= 2:
                # Get second context by sequence
                second_context = None
                if len(self.working_memory.context_sequence) >= 2:
                    second_context_id = self.working_memory.context_sequence[1]
                    second_context = self.working_memory.active_contexts.get(second_context_id)
                
                if second_context:
                    likely_referent = f"the second event: {second_context.description}"
                    confidence = 0.9
                else:
                    likely_referent = f"the second event: {active_contexts[1].description}"
                    confidence = 0.8
            elif "next" in vague_phrase:
                next_context = self._get_next_planned_context()
                if next_context:
                    likely_referent = f"the next event: {next_context.description}"
                    confidence = 0.8
        
        elif reference_type == "outcome":
            recent_context = self._get_most_recent_active_context()
            if recent_context:
                likely_referent = f"{recent_context.description} went well"
                confidence = 0.7
        
        elif reference_type == "return":
            # Check for contexts with places
            place_contexts = [c for c in active_contexts if c.place]
            if place_contexts:
                recent_place_context = place_contexts[-1]  # Most recent
                likely_referent = f"came back from {recent_place_context.place} ({recent_place_context.description})"
                confidence = 0.8
                recent_place_context.status = "completed"
        
        elif reference_type == "ready":
            # Check for contexts in preparing status
            preparing_contexts = [c for c in active_contexts if c.status == "planned"]
            if preparing_contexts:
                next_context = preparing_contexts[0]
                likely_referent = f"ready for {next_context.description}"
                confidence = 0.8
                next_context.status = "preparing"
        
        elif reference_type == "arrival":
            # Check for travel/location contexts
            recent_context = self._get_most_recent_active_context()
            if recent_context and recent_context.place:
                likely_referent = f"arrived at {recent_context.place} for {recent_context.description}"
                confidence = 0.9
                recent_context.status = "ongoing"
        
        if likely_referent:
            self.save_memory()  # Save context status updates
            return ReferenceResolution(
                vague_phrase=vague_phrase,
                likely_referent=likely_referent,
                confidence=confidence,
                context_source=context_source
            )
        
        # Fallback to single-context resolution
        return self._resolve_reference_from_working_memory(vague_phrase, reference_type)
    
    def _get_most_recent_active_context(self) -> Optional[ContextItem]:
        """Get the most recently active context"""
        if not self.working_memory.context_sequence:
            return None
        
        # Check contexts in reverse chronological order
        for context_id in reversed(self.working_memory.context_sequence):
            if context_id in self.working_memory.active_contexts:
                context = self.working_memory.active_contexts[context_id]
                if context.status in ["ongoing", "planned", "preparing"]:
                    return context
        
        return None
    
    def _get_next_planned_context(self) -> Optional[ContextItem]:
        """Get the next planned context in sequence"""
        # First try to find planned contexts
        planned_contexts = [
            c for c in self.working_memory.active_contexts.values() 
            if c.status == "planned"
        ]
        
        if planned_contexts:
            # Sort by priority and return highest priority
            planned_contexts.sort(key=lambda x: x.priority)
            return planned_contexts[0]
        
        # If no planned contexts, return any active context
        active_contexts = [
            c for c in self.working_memory.active_contexts.values() 
            if c.status in ["preparing", "ongoing"]
        ]
        
        if active_contexts:
            return active_contexts[0]
        
        return None
    
    def _resolve_reference_from_working_memory(self, vague_phrase: str, reference_type: str) -> Optional[ReferenceResolution]:
        """Resolve vague reference using working memory context"""
        if not self.working_memory.last_action:
            return None
        
        confidence = 0.8
        likely_referent = ""
        context_source = "working_memory"
        
        if reference_type == "completion":
            if self.working_memory.action_status in ["ongoing", "preparing"]:
                likely_referent = f"finished {self.working_memory.last_action}"
                confidence = 0.9
            elif self.working_memory.last_goal:
                likely_referent = f"finished {self.working_memory.last_goal}"
                confidence = 0.8
        
        elif reference_type == "return":
            if self.working_memory.last_place:
                likely_referent = f"came back from {self.working_memory.last_place}"
                confidence = 0.9
            elif "going to" in (self.working_memory.last_action or ""):
                # Extract place from action like "going to shop"
                place_match = re.search(r"going to (.+)", self.working_memory.last_action)
                if place_match:
                    place = place_match.group(1)
                    likely_referent = f"came back from {place}"
                    confidence = 0.8
        
        elif reference_type == "outcome":
            if self.working_memory.last_action:
                likely_referent = f"{self.working_memory.last_action} went well"
                confidence = 0.7
        
        elif reference_type == "ready":
            if self.working_memory.last_goal:
                likely_referent = f"ready for {self.working_memory.last_goal}"
                confidence = 0.8
            elif self.working_memory.last_action and "going to" in self.working_memory.last_action:
                likely_referent = f"ready to {self.working_memory.last_action}"
                confidence = 0.8
        
        elif reference_type == "arrival":
            if self.working_memory.last_place:
                likely_referent = f"arrived at {self.working_memory.last_place}"
                confidence = 0.9
        
        if likely_referent:
            return ReferenceResolution(
                vague_phrase=vague_phrase,
                likely_referent=likely_referent,
                confidence=confidence,
                context_source=context_source
            )
        
        return None
    
    def track_intent_across_turns(self, text: str, original_text: str):
        """🧠 Track multi-turn task intentions"""
        try:
            text_lower = text.lower().strip()
            current_time = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            
            # Intent linking patterns
            prep_patterns = [
                (r"let me (?:first\s+)?(check|get|find|grab) (.+?)(?:\.|$)", "prep", "{0} {1}"),
                (r"i need to (?:first\s+)?(check|get|find|grab) (.+?)(?:\.|$)", "prep", "{0} {1}"),
                (r"before i go, i'll (.+?)(?:\.|$)", "prep", "{0}"),
                (r"first i need to (.+?)(?:\.|$)", "prep", "{0}"),
                (r"let me just (.+?)(?:\.|$)", "prep", "{0}"),
            ]
            
            continuation_patterns = [
                (r"(?:alright|okay|right), (?:i'm\s+)?(ready|set|good to go)(?:\.|$)", "continue"),
                (r"now i can (.+?)(?:\.|$)", "continue"),
                (r"(?:okay|alright), (?:let's\s+)?(go|do this)(?:\.|$)", "continue"),
            ]
            
            # Check for preparation steps
            for pattern, step_type, step_template in prep_patterns:
                match = re.search(pattern, text_lower)
                if match:
                    prep_step = step_template.format(*match.groups()) if "{" in step_template else step_template
                    
                    # Link to existing intent if there's an active one
                    if self.working_memory.last_action and self.working_memory.action_status in ["preparing", "planned"]:
                        intent_id = f"intent_{int(time.time())}"
                        
                        # Create or update intent slot
                        if intent_id not in self.intent_slots:
                            self.intent_slots[intent_id] = IntentSlot(
                                intent=self.working_memory.last_action,
                                status="preparing",
                                prep_steps=[],
                                timestamp=current_time,
                                related_actions=[]
                            )
                        
                        self.intent_slots[intent_id].prep_steps.append(prep_step)
                        self.intent_slots[intent_id].related_actions.append(original_text)
                        
                        print(f"[IntentSlot] 🔧 Prep step: {prep_step} for {self.working_memory.last_action}")
                        break
            
            # Check for continuation signals
            for pattern, signal_type in continuation_patterns:
                match = re.search(pattern, text_lower)
                if match:
                    # Update status of active intents
                    for intent_id, intent in self.intent_slots.items():
                        if intent.status == "preparing":
                            intent.status = "ready"
                            intent.related_actions.append(original_text)
                            print(f"[IntentSlot] ✅ Ready for: {intent.intent}")
                            break
            
            self.save_memory()
            
        except Exception as e:
            if DEBUG:
                print(f"[IntentSlot] ❌ Tracking error: {e}")
    
    def _extract_topic_from_action(self, action: str, context: str) -> str:
        """Extract topic from action description"""
        action_lower = action.lower()
        
        # Topic extraction patterns
        if any(word in action_lower for word in ["cook", "make", "prepar"]):
            if "dinner" in context.lower():
                return "dinner"
            elif "lunch" in context.lower():
                return "lunch"
            elif "breakfast" in context.lower():
                return "breakfast"
            else:
                return "cooking"
        elif any(word in action_lower for word in ["shop", "buy", "grocery"]):
            return "shopping"
        elif any(word in action_lower for word in ["work", "office", "meeting"]):
            return "work"
        elif any(word in action_lower for word in ["clean", "organiz", "tidy"]):
            return "cleaning"
        else:
            # Extract noun from action
            words = action.split()
            if len(words) > 1:
                return words[-1]  # Last word is often the object
            return action
    
    def get_working_memory_context_for_llm(self) -> str:
        """🧠 Generate natural language working memory context for LLM"""
        try:
            context_parts = []
            
            if not any([self.working_memory.last_action, self.working_memory.last_place, 
                       self.working_memory.last_goal, self.reference_history]):
                return ""
            
            # Current action context
            if self.working_memory.last_action:
                status_desc = {
                    "preparing": "getting ready",
                    "ongoing": "currently",
                    "planned": "planning to",
                    "completed": "recently finished"
                }.get(self.working_memory.action_status, "")
                
                if status_desc:
                    action_context = f"User is {status_desc} {self.working_memory.last_action}"
                else:
                    action_context = f"User mentioned {self.working_memory.last_action}"
                
                if self.working_memory.last_place:
                    action_context += f" at {self.working_memory.last_place}"
                
                context_parts.append(action_context)
            
            # Intent context (multi-turn tasks)
            active_intents = [intent for intent in self.intent_slots.values() 
                            if intent.status in ["preparing", "ready"]]
            
            for intent in active_intents[-1:]:  # Only most recent intent
                if intent.prep_steps:
                    prep_desc = f"User preparing for {intent.intent}: {', '.join(intent.prep_steps[-2:])}"
                    context_parts.append(prep_desc)
            
            # Recent reference resolutions
            if self.reference_history:
                recent_resolution = self.reference_history[-1]
                if recent_resolution.confidence > 0.7:
                    resolution_context = f"When user says '{recent_resolution.vague_phrase}', they likely mean '{recent_resolution.likely_referent}'"
                    context_parts.append(resolution_context)
            
            if context_parts:
                result = "Context: " + ". ".join(context_parts)
                return result[:200]  # Keep it concise
            
            return ""
            
        except Exception as e:
            if DEBUG:
                print(f"[WorkingMemory] ❌ Context generation error: {e}")
            return ""
    
    # Enhanced save/load methods
    def save_memory(self):
        """Save enhanced memory with entity awareness + WORKING MEMORY"""
        try:
            # Save all existing memory types
            super_save_methods = [
                self._save_personal_facts,
                self._save_emotional_history,
                self._save_scheduled_events,
                self._save_conversation_topics
            ]
            
            # 🧠 Save new enhanced memory types
            self._save_entity_memories()
            self._save_life_events()
            
            # 🎯 Save plan data
            self._save_plan_data()
            
            # 🧠 WORKING MEMORY: Save working memory data
            self._save_working_memory_data()
            
            # 📋 INTERACTION THREAD MEMORY: Save interaction threads
            self._save_interaction_log()
            
            # 🧠 EPISODIC TURN MEMORY: Save episodic memory
            self._save_episodic_memory()
            
            for save_method in super_save_methods:
                save_method()
                
        except Exception as e:
            if DEBUG:
                print(f"[MegaMemory] ❌ Save error: {e}")
    
    def _save_entity_memories(self):
        """Save entity memories"""
        entities_file = self.memory_dir / "entity_memories.json"
        with open(entities_file, 'w') as f:
            entities_data = {}
            for name, entity in self.entity_memories.items():
                entity_dict = asdict(entity)
                entity_dict['status'] = entity.status.value if entity.status else "unknown"  # Convert enum to string
                entities_data[name] = entity_dict
            json.dump(entities_data, f, indent=2)
    
    def _save_life_events(self):
        """Save life events"""
        events_file = self.memory_dir / "life_events.json"
        with open(events_file, 'w') as f:
            events_data = {k: asdict(v) for k, v in self.life_events.items()}
            json.dump(events_data, f, indent=2)
    
    def load_memory(self):
        """Load enhanced memory with entity awareness + WORKING MEMORY"""
        try:
            # Load existing memory types
            self._load_personal_facts()
            self._load_emotional_history()
            self._load_scheduled_events()
            self._load_conversation_topics()
            
            # 🧠 Load new enhanced memory types
            self._load_entity_memories()
            self._load_life_events()
            
            # 🎯 Load plan data
            self._load_plan_data()
            
            # 🧠 WORKING MEMORY: Load working memory data
            self._load_working_memory_data()
            
            # 📋 INTERACTION THREAD MEMORY: Load interaction threads
            self._load_interaction_log()
            
            # 🧠 EPISODIC TURN MEMORY: Load episodic memory
            self._load_episodic_memory()
            
            if DEBUG:
                print(f"[MegaMemory] 🧠 Loaded MEGA-INTELLIGENT memory for {self.username}")
                print(f"  Entities: {len(self.entity_memories)}")
                print(f"  Life Events: {len(self.life_events)}")
                print(f"  Working Memory: {bool(self.working_memory.last_action)}")
                
        except Exception as e:
            if DEBUG:
                print(f"[MegaMemory] ❌ Load error: {e}")
    
    def _load_entity_memories(self):
        """Load entity memories"""
        entities_file = self.memory_dir / "entity_memories.json"
        if entities_file.exists():
            with open(entities_file, 'r') as f:
                entities_data = json.load(f)
                for name, entity_dict in entities_data.items():
                    entity_dict['status'] = EntityStatus(entity_dict['status'])  # Convert string back to enum
                    self.entity_memories[name] = EntityMemory(**entity_dict)
    
    def _load_life_events(self):
        """Load life events"""
        events_file = self.memory_dir / "life_events.json"
        if events_file.exists():
            with open(events_file, 'r') as f:
                events_data = json.load(f)
                self.life_events = {k: LifeEvent(**v) for k, v in events_data.items()}
    
    def _save_plan_data(self):
        """🎯 Save plan detection data"""
        plan_file = self.memory_dir / "user_plans.json"
        plan_data = {
            "user_today_plan": self.user_today_plan,
            "plan_timestamp": self.plan_timestamp,
            "plan_context": self.plan_context
        }
        with open(plan_file, 'w') as f:
            json.dump(plan_data, f, indent=2)
    
    def _load_plan_data(self):
        """🎯 Load plan detection data"""
        plan_file = self.memory_dir / "user_plans.json"
        if plan_file.exists():
            with open(plan_file, 'r') as f:
                plan_data = json.load(f)
                self.user_today_plan = plan_data.get("user_today_plan")
                self.plan_timestamp = plan_data.get("plan_timestamp")
                self.plan_context = plan_data.get("plan_context")
                
                # Clear outdated plans on load
                self.clear_outdated_plans()
    
    def _save_working_memory_data(self):
        """🧠 MULTI-CONTEXT WORKING MEMORY: Save working memory data with multiple contexts"""
        working_memory_file = self.memory_dir / "working_memory.json"
        
        # Convert active_contexts to serializable format
        active_contexts_data = {}
        if hasattr(self.working_memory, 'active_contexts') and self.working_memory.active_contexts:
            for context_id, context in self.working_memory.active_contexts.items():
                active_contexts_data[context_id] = asdict(context)
        
        working_memory_data = {
            "working_memory": {
                "active_contexts": active_contexts_data,
                "last_action": self.working_memory.last_action,
                "last_place": self.working_memory.last_place,
                "last_topic": self.working_memory.last_topic,
                "last_goal": self.working_memory.last_goal,
                "last_timestamp": self.working_memory.last_timestamp,
                "action_status": self.working_memory.action_status,
                "context_sequence": getattr(self.working_memory, 'context_sequence', [])
            },
            "intent_slots": {k: asdict(v) for k, v in self.intent_slots.items()},
            "reference_history": [asdict(r) for r in self.reference_history[-10:]]  # Keep last 10 resolutions
        }
        with open(working_memory_file, 'w') as f:
            json.dump(working_memory_data, f, indent=2)
    
    def _load_working_memory_data(self):
        """🧠 MULTI-CONTEXT WORKING MEMORY: Load working memory data with multiple contexts"""
        working_memory_file = self.memory_dir / "working_memory.json"
        if working_memory_file.exists():
            try:
                with open(working_memory_file, 'r') as f:
                    data = json.load(f)
                
                # Load working memory state
                if "working_memory" in data:
                    wm_data = data["working_memory"]
                    
                    # Initialize WorkingMemoryState with backward compatibility
                    self.working_memory = WorkingMemoryState(
                        last_action=wm_data.get("last_action"),
                        last_place=wm_data.get("last_place"),
                        last_topic=wm_data.get("last_topic"),
                        last_goal=wm_data.get("last_goal"),
                        last_timestamp=wm_data.get("last_timestamp"),
                        action_status=wm_data.get("action_status", "unknown"),
                        active_contexts={},
                        context_sequence=wm_data.get("context_sequence", [])
                    )
                    
                    # Load active contexts if they exist
                    if "active_contexts" in wm_data and wm_data["active_contexts"]:
                        for context_id, context_data in wm_data["active_contexts"].items():
                            try:
                                self.working_memory.active_contexts[context_id] = ContextItem(**context_data)
                            except Exception as e:
                                print(f"[MultiContext] ⚠️ Error loading context {context_id}: {e}")
                
                # Load intent slots
                if "intent_slots" in data:
                    self.intent_slots = {k: IntentSlot(**v) for k, v in data["intent_slots"].items()}
                
                # Load reference history
                if "reference_history" in data:
                    self.reference_history = [ReferenceResolution(**r) for r in data["reference_history"]]
                    
            except Exception as e:
                print(f"[MultiContext] ⚠️ Error loading working memory: {e}")
                # Initialize with defaults if loading fails
                self.working_memory = WorkingMemoryState()
                self.intent_slots = {}
                self.reference_history = []
    
    def _save_interaction_log(self):
        """📋 INTERACTION THREAD MEMORY: Save interaction threads"""
        interaction_file = self.memory_dir / "interaction_log.json"
        interaction_data = {
            "current_interaction_id": self.current_interaction_id,
            "interaction_log": [asdict(thread) for thread in self.interaction_log[-50:]]  # Keep last 50 interactions
        }
        with open(interaction_file, 'w') as f:
            json.dump(interaction_data, f, indent=2)
    
    def _load_interaction_log(self):
        """📋 INTERACTION THREAD MEMORY: Load interaction threads"""
        interaction_file = self.memory_dir / "interaction_log.json"
        if interaction_file.exists():
            try:
                with open(interaction_file, 'r') as f:
                    data = json.load(f)
                    
                    # Load interaction log
                    if "interaction_log" in data:
                        self.interaction_log = [InteractionThread(**thread) for thread in data["interaction_log"]]
                    
                    # Load current interaction ID
                    if "current_interaction_id" in data:
                        self.current_interaction_id = data["current_interaction_id"]
            except Exception as e:
                print(f"[InteractionMemory] ⚠️ Error loading interaction log: {e}")
                self.interaction_log = []
                self.current_interaction_id = 0
    
    def _save_episodic_memory(self):
        """🧠 EPISODIC TURN MEMORY: Save episodic memory"""
        episodic_file = self.memory_dir / "episodic_memory.json"
        episodic_data = {
            "current_turn_number": self.current_turn_number,
            "episodic_memory": [asdict(turn) for turn in self.episodic_memory[-100:]]  # Keep last 100 turns
        }
        with open(episodic_file, 'w') as f:
            json.dump(episodic_data, f, indent=2)
    
    def _load_episodic_memory(self):
        """🧠 EPISODIC TURN MEMORY: Load episodic memory"""
        episodic_file = self.memory_dir / "episodic_memory.json"
        if episodic_file.exists():
            try:
                with open(episodic_file, 'r') as f:
                    data = json.load(f)
                    
                    # Load episodic memory
                    if "episodic_memory" in data:
                        self.episodic_memory = [EpisodicTurn(**turn) for turn in data["episodic_memory"]]
                    
                    # Load current turn number
                    if "current_turn_number" in data:
                        self.current_turn_number = data["current_turn_number"]
            except Exception as e:
                print(f"[EpisodicMemory] ⚠️ Error loading episodic memory: {e}")
                self.episodic_memory = []
                self.current_turn_number = 0
    
    # Individual save methods for existing data types
    def _save_personal_facts(self):
        facts_file = self.memory_dir / "personal_facts.json"
        with open(facts_file, 'w') as f:
            facts_data = {}
            for k, v in self.personal_facts.items():
                fact_dict = asdict(v)
                if hasattr(v, 'current_status'):
                    fact_dict['current_status'] = v.current_status.value if v.current_status else "unknown"
                facts_data[k] = fact_dict
            json.dump(facts_data, f, indent=2)
    
    def _save_emotional_history(self):
        emotions_file = self.memory_dir / "emotions.json"
        with open(emotions_file, 'w') as f:
            emotions_data = [asdict(e) for e in self.emotional_history]
            json.dump(emotions_data, f, indent=2)
    
    def _save_scheduled_events(self):
        events_file = self.memory_dir / "events.json"
        with open(events_file, 'w') as f:
            events_data = [asdict(e) for e in self.scheduled_events]
            json.dump(events_data, f, indent=2)
    
    def _save_conversation_topics(self):
        topics_file = self.memory_dir / "conversation_topics.json"
        with open(topics_file, 'w') as f:
            topics_data = [asdict(t) for t in self.conversation_topics]
            json.dump(topics_data, f, indent=2)
    
    def _load_personal_facts(self):
        facts_file = self.memory_dir / "personal_facts.json"
        if facts_file.exists():
            with open(facts_file, 'r') as f:
                facts_data = json.load(f)
                for k, v in facts_data.items():
                    if 'current_status' in v:
                        v['current_status'] = EntityStatus(v['current_status'])
                    self.personal_facts[k] = PersonalFact(**v)
    
    def _load_emotional_history(self):
        emotions_file = self.memory_dir / "emotions.json"
        if emotions_file.exists():
            with open(emotions_file, 'r') as f:
                emotions_data = json.load(f)
                self.emotional_history = [EmotionalState(**e) for e in emotions_data]
    
    def _load_scheduled_events(self):
        events_file = self.memory_dir / "events.json"
        if events_file.exists():
            with open(events_file, 'r') as f:
                events_data = json.load(f)
                self.scheduled_events = [ScheduledEvent(**e) for e in events_data]
    
    def _load_conversation_topics(self):
        topics_file = self.memory_dir / "conversation_topics.json"
        if topics_file.exists():
            with open(topics_file, 'r') as f:
                topics_data = json.load(f)
                self.conversation_topics = [ConversationTopic(**t) for t in topics_data]
    
    # Keep existing methods for compatibility
    def add_conversation_topic(self, topic: str, keywords: List[str]):
        """Add or update a conversation topic"""
        current_time = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        
        existing_topic = None
        for t in self.conversation_topics:
            if t.topic.lower() == topic.lower():
                existing_topic = t
                break
        
        if existing_topic:
            existing_topic.last_mentioned = current_time
            existing_topic.message_count += 1
            for keyword in keywords:
                if keyword.lower() not in [k.lower() for k in existing_topic.keywords]:
                    existing_topic.keywords.append(keyword)
        else:
            new_topic = ConversationTopic(
                topic=topic,
                start_time=current_time,
                last_mentioned=current_time,
                message_count=1,
                keywords=keywords
            )
            self.conversation_topics.append(new_topic)
            
            if len(self.conversation_topics) > MAX_CONVERSATION_TOPICS:
                self.conversation_topics = self.conversation_topics[-MAX_CONVERSATION_TOPICS:]
        
        self.save_memory()
    
    def get_recent_topics(self) -> List[str]:
        """Get recently discussed topics"""
        return [topic.topic for topic in self.conversation_topics[-3:]]
    
    def add_personal_fact(self, category: str, key: str, value: str, 
                         confidence: float, context: str):
        """Add or update a personal fact"""
        fact_id = f"{category}_{key}"
        current_time = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        
        fact = PersonalFact(
            category=category,
            key=key,
            value=value,
            confidence=confidence,
            date_learned=current_time,
            last_mentioned=current_time,
            source_context=context
        )
        
        self.personal_facts[fact_id] = fact
        print(f"[MegaMemory] 📝 Learned: {self.username} {key} = {value}")
        self.save_memory()
    
    def add_emotional_state(self, emotion: str, intensity: int, 
                           context: str, follow_up: bool = True):
        """Record user's emotional state"""
        current_time = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        
        state = EmotionalState(
            emotion=emotion,
            intensity=intensity,
            context=context,
            date=current_time,
            follow_up_needed=follow_up
        )
        
        self.emotional_history.append(state)
        print(f"[MegaMemory] 😊 Emotion: {self.username} feeling {emotion} ({intensity}/10)")
        self.save_memory()
    
    def add_scheduled_event(self, event_type: str, description: str, 
                           event_date: str, reminder_days: List[int] = [1, 0]):
        """Add an event to remember"""
        event_dt = datetime.datetime.strptime(event_date, '%Y-%m-%d')
        reminder_dates = []
        
        for days_before in reminder_days:
            reminder_dt = event_dt - datetime.timedelta(days=days_before)
            reminder_dates.append(reminder_dt.strftime('%Y-%m-%d'))
        
        event = ScheduledEvent(
            event_type=event_type,
            description=description,
            date=event_date,
            reminder_dates=reminder_dates,
            completed=False
        )
        
        self.scheduled_events.append(event)
        print(f"[MegaMemory] 📅 Event: {description} on {event_date}")
        self.save_memory()
    
    def get_today_reminders(self) -> List[str]:
        """Get reminders for today"""
        today = datetime.datetime.utcnow().strftime('%Y-%m-%d')
        reminders = []
        
        for event in self.scheduled_events:
            if not event.completed and today in event.reminder_dates:
                if event.date == today:
                    reminders.append(f"Today is {event.description}!")
                else:
                    days_until = (datetime.datetime.strptime(event.date, '%Y-%m-%d') - 
                                datetime.datetime.strptime(today, '%Y-%m-%d')).days
                    reminders.append(f"{event.description} is in {days_until} day(s)")
        
        return reminders
    
    def get_follow_up_questions(self) -> List[str]:
        """Get questions to follow up on previous conversations"""
        questions = []
        today = datetime.datetime.utcnow().strftime('%Y-%m-%d')
        yesterday = (datetime.datetime.utcnow() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
        
        # Check emotional follow-ups from yesterday
        for emotion in self.emotional_history[-5:]:
            emotion_date = emotion.date.split(' ')[0]
            
            if emotion.follow_up_needed and emotion_date == yesterday:
                if emotion.emotion in ["sad", "stressed", "angry", "upset"]:
                    questions.append(f"How are you feeling today? Yesterday you seemed {emotion.emotion} about {emotion.context}")
                elif emotion.emotion in ["happy", "excited", "thrilled"]:
                    questions.append(f"Are you still feeling {emotion.emotion} about {emotion.context}?")
        
        return questions[:2]
    
    def get_memory_context(self) -> str:
        """Get relevant memory context for conversation"""
        return self.get_contextual_memory_for_response()
    
    def get_natural_language_context_for_llm(self, user_message: str) -> str:
        """🧠 Generate natural language context injection for LLM (no data dumps)"""
        try:
            context_parts = []
            
            # Check for vague references and provide resolution context
            resolution = self.detect_and_resolve_references(user_message.lower())
            if resolution and resolution.confidence > 0.7:
                context_parts.append(
                    f"User recently said they were {self.working_memory.last_action}. "
                    f"They now said: '{resolution.vague_phrase}'. "
                    f"Interpret this as: '{resolution.likely_referent}'."
                )
            
            # Provide current action context if relevant
            elif self.working_memory.last_action:
                if self.working_memory.action_status == "ongoing":
                    context_parts.append(f"User is currently {self.working_memory.last_action}.")
                elif self.working_memory.action_status == "preparing":
                    context_parts.append(f"User is preparing to {self.working_memory.last_action}.")
            
            # Provide intent context for multi-turn tasks
            active_intents = [intent for intent in self.intent_slots.values() 
                            if intent.status in ["preparing", "ready"]]
            if active_intents:
                intent = active_intents[-1]  # Most recent
                if intent.prep_steps:
                    context_parts.append(
                        f"User is working on {intent.intent} and has been doing: {', '.join(intent.prep_steps[-2:])}."
                    )
            
            # Provide plan context naturally
            if self.user_today_plan:
                context_parts.append(f"User mentioned their plan: {self.user_today_plan}.")
            
            return " ".join(context_parts) if context_parts else ""
            
        except Exception as e:
            if DEBUG:
                print(f"[WorkingMemory] ❌ Context generation error: {e}")
            return ""
    
    def get_multi_context_summary(self) -> str:
        """🧠 MULTI-CONTEXT: Get summary of all active contexts for LLM injection"""
        if not self.working_memory.active_contexts:
            return ""
        
        context_lines = []
        active_contexts = list(self.working_memory.active_contexts.values())
        
        # Sort by priority and recency
        active_contexts.sort(key=lambda x: (x.priority, x.timestamp), reverse=True)
        
        for i, context in enumerate(active_contexts[:5]):  # Max 5 contexts in summary
            status_emoji = {
                "planned": "📅",
                "preparing": "🔧", 
                "ongoing": "⚡",
                "completed": "✅"
            }.get(context.status, "❓")
            
            context_line = f"{status_emoji} {context.description}"
            
            if context.place:
                context_line += f" (at {context.place})"
            
            if context.time_reference:
                context_line += f" - {context.time_reference}"
            
            if context.completion_status > 0:
                context_line += f" ({int(context.completion_status * 100)}% complete)"
            
            context_lines.append(context_line)
        
        if context_lines:
            return "User's current contexts: " + " | ".join(context_lines)
        
        return ""
    
    def update_context_status(self, context_description: str, new_status: str, completion: float = None):
        """🧠 MULTI-CONTEXT: Update status of specific context"""
        for context in self.working_memory.active_contexts.values():
            if context_description.lower() in context.description.lower():
                context.status = new_status
                if completion is not None:
                    context.completion_status = completion
                print(f"[MultiContext] 🔄 Updated '{context.description}' → {new_status}")
                self.save_memory()
                return True
        return False
    
    def get_active_contexts_count(self) -> int:
        """🧠 MULTI-CONTEXT: Get count of active contexts"""
        return len([c for c in self.working_memory.active_contexts.values() 
                   if c.status in ["planned", "preparing", "ongoing"]])
    
    def get_context_by_type(self, event_type: str) -> List[ContextItem]:
        """🧠 MULTI-CONTEXT: Get contexts by event type"""
        return [c for c in self.working_memory.active_contexts.values() 
                if c.event_type == event_type]

# Global conversation storage (keep existing)
conversation_history = {}

# Global memory manager (keep existing)
user_memories: Dict[str, UserMemorySystem] = {}

def get_user_memory(username: str) -> UserMemorySystem:
    """Get or create user memory system"""
    if username not in user_memories:
        user_memories[username] = UserMemorySystem(username)
    return user_memories[username]

# Enhanced conversation functions
def add_to_conversation_history(username, user_message, ai_response):
    """🧠 Enhanced conversation history with mega-intelligent memory extraction + retrospective memory"""
    try:
        if username not in conversation_history:
            conversation_history[username] = []
        
        conversation_history[username].append({
            "user": user_message,
            "assistant": ai_response,
            "timestamp": time.time()
        })
        
        max_length = CONVERSATION_MEMORY_LENGTH if ENHANCED_CONVERSATION_MEMORY else MAX_HISTORY_LENGTH
        if len(conversation_history[username]) > max_length:
            conversation_history[username] = conversation_history[username][-max_length:]
        
        # 🧠 MEGA-INTELLIGENT: Enhanced memory extraction
        memory = get_user_memory(username)
        
        # Extract memories from both user message and AI response
        memory.extract_memories_from_text(user_message)
        
        # 🧠 NEW: Retrospective Memory - Store Buddy's advice for future recall
        try:
            from ai.retrospective_memory import store_buddy_advice
            store_buddy_advice(username, user_message, ai_response)
        except Exception as retro_error:
            if DEBUG:
                print(f"[RetrospectiveMemory] ⚠️ Error storing advice: {retro_error}")
        
        # Extract topic with entity awareness
        if TOPIC_TRACKING_ENABLED:
            recent_messages = [exc["user"] for exc in conversation_history[username][-2:]]
            topic = extract_topic_from_conversation(recent_messages)
            if topic != "general":
                keywords = re.findall(r'\b\w+\b', user_message.lower())
                memory.add_conversation_topic(topic, keywords[:4])
        
        if DEBUG:
            print(f"[MegaMemory] 💭 Added to MEGA-INTELLIGENT memory for {username}")
            
    except Exception as e:
        if DEBUG:
            print(f"[MegaMemory] ❌ Enhanced memory error: {e}")

def get_conversation_context(username):
    """🧠 Get MEGA-INTELLIGENT conversation context with TOKEN COMPRESSION"""
    try:
        context_parts = []
        
        if username in conversation_history and conversation_history[username]:
            history = conversation_history[username]
            
            # ✅ COMPRESSED: Reduced context length for token optimization
            context_length = min(CONVERSATION_CONTEXT_LENGTH if ENHANCED_CONVERSATION_MEMORY else 2, 6)  # Max 6 exchanges
            recent_exchanges = history[-context_length:]
            
            if (CONVERSATION_SUMMARY_ENABLED and 
                len(history) > CONVERSATION_SUMMARY_THRESHOLD):
                summary = summarize_old_conversation(history)
                if summary:
                    # ✅ COMPRESSED: Shorter summary
                    context_parts.append(f"Earlier: {summary}")
                    context_parts.append("")
            
            for exchange in recent_exchanges:
                # ✅ COMPRESSED: Truncate messages for token optimization
                user_msg = exchange["user"][:80]  # Reduced from 120 to 80
                ai_msg = exchange["assistant"][:80]  # Reduced from 120 to 80
                context_parts.append(f"Human: {user_msg}")
                context_parts.append(f"Assistant: {ai_msg}")
        
        # 🧠 MEGA-INTELLIGENT: Enhanced memory context (COMPRESSED)
        memory = get_user_memory(username)
        memory_context = memory.get_contextual_memory_for_response()
        follow_ups = memory.get_follow_up_questions()
        
        if memory_context:
            context_parts.append(f"\n🧠 Memory for {username}:")
            context_parts.append(memory_context)
        
        if follow_ups and len(follow_ups) > 0:  # Only add if there are follow-ups
            context_parts.append(f"\nSuggested follow-up:")
            context_parts.extend(follow_ups[:1])  # Only include first follow-up for compression
        
        full_context = "\n".join(context_parts)
        
        # ✅ TOKEN COMPRESSION: Strict context optimization
        from ai.prompt_compressor import prompt_compressor
        max_context_tokens = 50  # Significantly reduced from MAX_CONTEXT_TOKENS * 4
        if len(full_context) > max_context_tokens * 4:
            full_context = prompt_compressor.optimize_context_for_budget(full_context, max_context_tokens)
            full_context += "\n[Context optimized for speed]"
        
        if DEBUG and ENHANCED_CONVERSATION_MEMORY:
            print(f"[MegaMemory] 🧠 COMPRESSED context: {len(full_context)} chars")
        
        return full_context
        
    except Exception as e:
        if DEBUG:
            print(f"[MegaMemory] ❌ Context error: {e}")
        return ""

def extract_topic_from_conversation(messages: List[str]) -> str:
    """Extract main topic from recent messages"""
    text = " ".join(messages[-2:]).lower()
    
    topic_patterns = [
        (r"\b(cat|cats|kitten|feline|meow|purr)\b", "cats"),
        (r"\b(dog|dogs|puppy|canine|bark|woof)\b", "dogs"),
        (r"\b(work|job|office|boss|colleague|meeting)\b", "work"),
        (r"\b(vacation|holiday|travel|trip|visit)\b", "vacation"),
        (r"\b(food|cooking|recipe|restaurant|eat|meal)\b", "food"),
        (r"\b(movie|film|cinema|netflix|watch)\b", "movies"),
        (r"\b(music|song|concert|band|listen)\b", "music"),
        (r"\b(family|mom|dad|sister|brother|parent|relative)\b", "family"),
        (r"\b(friend|friends|friendship|buddy)\b", "friends"),
        (r"\b(health|doctor|medical|sick|hospital)\b", "health"),
        (r"\b(shopping|buy|purchase|store|mall)\b", "shopping"),
        (r"\b(weather|rain|sun|snow|cold|hot|temperature)\b", "weather"),
        (r"\b(game|gaming|play|xbox|playstation)\b", "gaming"),
        (r"\b(book|reading|novel|author|chapter)\b", "books"),
        # 🧠 NEW: Death and loss topics
        (r"\b(died|death|passed|loss|grief|funeral)\b", "loss_and_grief"),
        (r"\b(sick|illness|medical|hospital|treatment)\b", "health_concerns"),
    ]
    
    for pattern, topic in topic_patterns:
        if re.search(pattern, text):
            return topic
    
    return "general"

def summarize_old_conversation(history: List[Dict]) -> str:
    """Create a summary of old conversation exchanges"""
    if len(history) <= CONVERSATION_SUMMARY_THRESHOLD:
        return ""
    
    old_exchanges = history[:-CONVERSATION_CONTEXT_LENGTH]
    topics = set()
    
    for exchange in old_exchanges:
        user_msg = exchange["user"].lower()
        if any(word in user_msg for word in ["cat", "cats", "kitten", "feline"]):
            topics.add("cats")
        if any(word in user_msg for word in ["work", "job", "office", "boss"]):
            topics.add("work")
        if any(word in user_msg for word in ["family", "mom", "dad", "parent"]):
            topics.add("family")
        if any(word in user_msg for word in ["vacation", "travel", "trip"]):
            topics.add("vacation")
        if any(word in user_msg for word in ["food", "cooking", "restaurant"]):
            topics.add("food")
        # 🧠 NEW: Loss and grief detection
        if any(word in user_msg for word in ["died", "death", "passed", "loss", "grief"]):
            topics.add("loss_and_grief")
    
    if topics:
        return f"Earlier we discussed: {', '.join(sorted(topics))}"
    
    return f"Earlier conversation ({len(old_exchanges)} exchanges)"

# 🧠 NEW: Response validation function
def validate_ai_response_appropriateness(username: str, proposed_response: str) -> Tuple[bool, str]:
    """🧠 MEGA-INTELLIGENT: Validate AI response before output"""
    memory = get_user_memory(username)
    return memory.validate_response_before_output(proposed_response)

print(f"[MegaMemory] 🧠 MEGA-INTELLIGENT Memory System Loaded!")
print(f"[MegaMemory] ✅ Entity Status Tracking: Active")
print(f"[MegaMemory] ✅ Life Event Detection: Active") 
print(f"[MegaMemory] ✅ Response Validation: Active")
print(f"[MegaMemory] ✅ Memory Inference Engine: Active")
print(f"[MegaMemory] ✅ Working Memory Tracking: Active")
print(f"[MegaMemory] ✅ Reference Resolution: Active")
print(f"[MegaMemory] ✅ Intent Slot Memory: Active")
print(f"[MegaMemory] ✅ Natural Language Context Injection: Active")
print(f"[MegaMemory] ✅ Time-Aware Greetings: Active")
print(f"[MegaMemory] ✅ Interaction Thread Memory: Active")
print(f"[MegaMemory] ✅ Episodic Turn Memory: Active")
print(f"[MegaMemory] ✅ Conversation Context for LLM: Active")
print(f"[MegaMemory] 🚀 MULTI-CONTEXT CONVERSATION HANDLING: Active")
print(f"[MegaMemory] 🎯 Multi-Event Parsing: Active")
print(f"[MegaMemory] 🔗 Advanced Reference Resolution: Active")
print(f"[MegaMemory] 💾 Cross-User Memory Isolation: Active")
print(f"[MegaMemory] 🔄 8K Context Window Preservation: Active")