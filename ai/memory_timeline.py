"""
Memory Timeline - Persistent Long-term Episodic and Thematic Memory System

This module implements comprehensive memory persistence with:
- Long-term episodic memories per user with structured storage
- Thematic memory linking across time periods
- Automatic memory consolidation and organization
- Cross-user memory isolation with per-user storage
- Auto-load on system reboot for seamless continuity
- Memory relationship tracking and recall optimization
"""

import json
import time
import os
from typing import Dict, List, Any, Optional, Tuple, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict, field
from pathlib import Path
from enum import Enum
import threading
import hashlib

class MemoryType(Enum):
    """Types of memories stored in the timeline"""
    EPISODIC = "episodic"           # Specific events and experiences
    SEMANTIC = "semantic"           # Facts and knowledge
    EMOTIONAL = "emotional"         # Emotional experiences and associations
    PROCEDURAL = "procedural"       # How to do things, skills
    AUTOBIOGRAPHICAL = "autobiographical"  # Personal history and identity
    SOCIAL = "social"              # Interpersonal interactions and relationships
    GOAL_RELATED = "goal_related"  # Memories related to goals and achievements
    TEMPORAL = "temporal"          # Time-based and temporal memories

class MemoryImportance(Enum):
    """Memory importance levels for retention and recall"""
    CRITICAL = 1.0      # Never forget, highest recall priority
    HIGH = 0.8          # Very important, frequent recall
    MEDIUM = 0.6        # Normal importance
    LOW = 0.4          # Less important, may fade
    MINIMAL = 0.2      # Background information

class MemoryEmotionalValence(Enum):
    """Emotional associations with memories"""
    VERY_POSITIVE = 1.0
    POSITIVE = 0.5
    NEUTRAL = 0.0
    NEGATIVE = -0.5
    VERY_NEGATIVE = -1.0

@dataclass
class MemoryObject:
    """A structured memory object with rich metadata"""
    memory_id: str
    user_id: str
    content: str
    memory_type: MemoryType
    importance: MemoryImportance
    timestamp: datetime
    emotional_valence: MemoryEmotionalValence = MemoryEmotionalValence.NEUTRAL
    topics: List[str] = field(default_factory=list)
    entities: List[str] = field(default_factory=list)  # People, places, things
    beliefs_affected: List[str] = field(default_factory=list)
    goals_related: List[str] = field(default_factory=list)
    linked_memories: List[str] = field(default_factory=list)  # Related memory IDs
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    consolidation_level: float = 0.0  # 0.0 = fresh, 1.0 = fully consolidated
    context_data: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if isinstance(self.timestamp, str):
            self.timestamp = datetime.fromisoformat(self.timestamp)
        if isinstance(self.last_accessed, str) and self.last_accessed:
            self.last_accessed = datetime.fromisoformat(self.last_accessed)

@dataclass
class ThematicLink:
    """Links between memories based on themes and concepts"""
    theme: str
    memory_ids: List[str]
    strength: float  # 0.0 to 1.0
    creation_time: datetime
    last_reinforced: datetime
    
    def __post_init__(self):
        if isinstance(self.creation_time, str):
            self.creation_time = datetime.fromisoformat(self.creation_time)
        if isinstance(self.last_reinforced, str):
            self.last_reinforced = datetime.fromisoformat(self.last_reinforced)

class MemoryTimeline:
    """
    Persistent long-term memory system with episodic and thematic organization.
    
    Features:
    - Per-user memory isolation and persistence
    - Automatic memory consolidation over time
    - Thematic linking and pattern recognition
    - Importance-based retention and recall
    - Cross-memory relationship tracking
    - Temporal organization and retrieval
    """
    
    def __init__(self, user_id: str, memory_dir: str = "memory"):
        self.user_id = user_id
        self.memory_dir = Path(memory_dir)
        self.memory_dir.mkdir(exist_ok=True)
        
        # Memory storage
        self.memories: Dict[str, MemoryObject] = {}
        self.thematic_links: Dict[str, ThematicLink] = {}
        self.memory_index: Dict[str, Set[str]] = {}  # Topic -> memory_ids
        
        # Configuration
        self.max_memories_per_user = 10000
        self.consolidation_period = timedelta(days=7)  # When to consolidate memories
        self.importance_decay_rate = 0.95  # Daily importance decay for LOW memories
        
        # Threading
        self.lock = threading.Lock()
        self.consolidation_thread = None
        self.auto_save_interval = 300  # 5 minutes
        
        # Load existing memories
        self._load_memories()
        self._build_memory_index()
        self._start_background_processes()
        
        print(f"[MemoryTimeline] 📚 Initialized for user {user_id} with {len(self.memories)} memories")
    
    def _generate_memory_id(self, content: str, timestamp: datetime) -> str:
        """Generate unique memory ID"""
        content_hash = hashlib.md5(f"{content}{timestamp.isoformat()}".encode()).hexdigest()[:12]
        return f"mem_{self.user_id}_{content_hash}"
    
    def store_memory(self, 
                    content: str,
                    memory_type: MemoryType,
                    importance: MemoryImportance,
                    emotional_valence: MemoryEmotionalValence = MemoryEmotionalValence.NEUTRAL,
                    topics: List[str] = None,
                    entities: List[str] = None,
                    beliefs_affected: List[str] = None,
                    goals_related: List[str] = None,
                    context_data: Dict[str, Any] = None) -> str:
        """Store a new memory with rich metadata"""
        
        timestamp = datetime.now()
        memory_id = self._generate_memory_id(content, timestamp)
        
        memory = MemoryObject(
            memory_id=memory_id,
            user_id=self.user_id,
            content=content,
            memory_type=memory_type,
            importance=importance,
            timestamp=timestamp,
            emotional_valence=emotional_valence,
            topics=topics or [],
            entities=entities or [],
            beliefs_affected=beliefs_affected or [],
            goals_related=goals_related or [],
            context_data=context_data or {}
        )
        
        with self.lock:
            self.memories[memory_id] = memory
            self._update_memory_index(memory)
            self._create_thematic_links(memory)
            self._enforce_memory_limits()
        
        self._save_memories()
        print(f"[MemoryTimeline] 💾 Stored {memory_type.value} memory: {content[:50]}...")
        return memory_id
    
    def recall_memories(self, 
                       query: str = None,
                       memory_type: MemoryType = None,
                       importance_threshold: MemoryImportance = MemoryImportance.LOW,
                       time_range: Tuple[datetime, datetime] = None,
                       topics: List[str] = None,
                       limit: int = 10) -> List[MemoryObject]:
        """Recall memories based on various criteria"""
        
        with self.lock:
            candidate_memories = list(self.memories.values())
        
        # Filter by criteria
        if memory_type:
            candidate_memories = [m for m in candidate_memories if m.memory_type == memory_type]
        
        if importance_threshold:
            candidate_memories = [m for m in candidate_memories 
                                if m.importance.value >= importance_threshold.value]
        
        if time_range:
            start_time, end_time = time_range
            candidate_memories = [m for m in candidate_memories 
                                if start_time <= m.timestamp <= end_time]
        
        if topics:
            candidate_memories = [m for m in candidate_memories 
                                if any(topic in m.topics for topic in topics)]
        
        if query:
            # Simple content matching - could be enhanced with semantic search
            query_lower = query.lower()
            candidate_memories = [m for m in candidate_memories 
                                if query_lower in m.content.lower() or 
                                   any(query_lower in topic.lower() for topic in m.topics)]
        
        # Sort by relevance (importance * recency * access frequency)
        def relevance_score(memory: MemoryObject) -> float:
            importance_score = memory.importance.value
            recency_score = 1.0 / (1.0 + (datetime.now() - memory.timestamp).days * 0.1)
            access_score = min(memory.access_count * 0.1, 1.0)
            return importance_score * 0.5 + recency_score * 0.3 + access_score * 0.2
        
        candidate_memories.sort(key=relevance_score, reverse=True)
        
        # Update access count for returned memories
        result_memories = candidate_memories[:limit]
        with self.lock:
            for memory in result_memories:
                memory.access_count += 1
                memory.last_accessed = datetime.now()
        
        return result_memories
    
    def get_memory_by_id(self, memory_id: str) -> Optional[MemoryObject]:
        """Get specific memory by ID"""
        with self.lock:
            memory = self.memories.get(memory_id)
            if memory:
                memory.access_count += 1
                memory.last_accessed = datetime.now()
        return memory
    
    def link_memories(self, memory_id1: str, memory_id2: str, relationship: str = None):
        """Create explicit link between two memories"""
        with self.lock:
            if memory_id1 in self.memories and memory_id2 in self.memories:
                if memory_id2 not in self.memories[memory_id1].linked_memories:
                    self.memories[memory_id1].linked_memories.append(memory_id2)
                if memory_id1 not in self.memories[memory_id2].linked_memories:
                    self.memories[memory_id2].linked_memories.append(memory_id1)
                print(f"[MemoryTimeline] 🔗 Linked memories {memory_id1[:12]} ↔ {memory_id2[:12]}")
    
    def get_related_memories(self, memory_id: str, max_depth: int = 2) -> List[MemoryObject]:
        """Get memories related to a specific memory through various connections"""
        if memory_id not in self.memories:
            return []
        
        related_ids = set()
        to_explore = [(memory_id, 0)]
        explored = set()
        
        while to_explore:
            current_id, depth = to_explore.pop(0)
            if current_id in explored or depth >= max_depth:
                continue
            
            explored.add(current_id)
            current_memory = self.memories[current_id]
            
            # Add explicitly linked memories
            for linked_id in current_memory.linked_memories:
                if linked_id not in explored:
                    related_ids.add(linked_id)
                    if depth + 1 < max_depth:
                        to_explore.append((linked_id, depth + 1))
            
            # Add thematically linked memories
            for topic in current_memory.topics:
                if topic in self.memory_index:
                    for topic_memory_id in self.memory_index[topic]:
                        if topic_memory_id not in explored and topic_memory_id != memory_id:
                            related_ids.add(topic_memory_id)
        
        return [self.memories[mid] for mid in related_ids if mid in self.memories]
    
    def get_memory_statistics(self) -> Dict[str, Any]:
        """Get comprehensive memory statistics"""
        with self.lock:
            stats = {
                "total_memories": len(self.memories),
                "memory_types": {},
                "importance_distribution": {},
                "emotional_distribution": {},
                "average_access_count": 0,
                "recent_memories": 0,
                "consolidated_memories": 0,
                "thematic_links": len(self.thematic_links)
            }
            
            if self.memories:
                # Type distribution
                for memory in self.memories.values():
                    mem_type = memory.memory_type.value
                    stats["memory_types"][mem_type] = stats["memory_types"].get(mem_type, 0) + 1
                    
                    importance = memory.importance.value
                    stats["importance_distribution"][importance] = stats["importance_distribution"].get(importance, 0) + 1
                    
                    valence = memory.emotional_valence.value
                    stats["emotional_distribution"][valence] = stats["emotional_distribution"].get(valence, 0) + 1
                
                # Access patterns
                stats["average_access_count"] = sum(m.access_count for m in self.memories.values()) / len(self.memories)
                
                # Recent vs consolidated
                recent_threshold = datetime.now() - timedelta(days=7)
                stats["recent_memories"] = sum(1 for m in self.memories.values() if m.timestamp > recent_threshold)
                stats["consolidated_memories"] = sum(1 for m in self.memories.values() if m.consolidation_level > 0.5)
        
        return stats
    
    def _update_memory_index(self, memory: MemoryObject):
        """Update memory index for fast topic-based retrieval"""
        for topic in memory.topics:
            if topic not in self.memory_index:
                self.memory_index[topic] = set()
            self.memory_index[topic].add(memory.memory_id)
        
        # Also index entities
        for entity in memory.entities:
            entity_topic = f"entity:{entity}"
            if entity_topic not in self.memory_index:
                self.memory_index[entity_topic] = set()
            self.memory_index[entity_topic].add(memory.memory_id)
    
    def _create_thematic_links(self, memory: MemoryObject):
        """Create thematic links based on shared topics and concepts"""
        for topic in memory.topics:
            if topic in self.thematic_links:
                # Reinforce existing thematic link
                link = self.thematic_links[topic]
                if memory.memory_id not in link.memory_ids:
                    link.memory_ids.append(memory.memory_id)
                    link.strength = min(link.strength + 0.1, 1.0)
                    link.last_reinforced = datetime.now()
            else:
                # Create new thematic link
                self.thematic_links[topic] = ThematicLink(
                    theme=topic,
                    memory_ids=[memory.memory_id],
                    strength=0.1,
                    creation_time=datetime.now(),
                    last_reinforced=datetime.now()
                )
    
    def _enforce_memory_limits(self):
        """Enforce memory limits by removing least important old memories"""
        if len(self.memories) <= self.max_memories_per_user:
            return
        
        # Sort memories by importance and recency
        memories_list = list(self.memories.values())
        memories_list.sort(key=lambda m: (m.importance.value, m.timestamp), reverse=True)
        
        # Keep only the most important/recent memories
        memories_to_keep = memories_list[:self.max_memories_per_user]
        memories_to_remove = memories_list[self.max_memories_per_user:]
        
        for memory in memories_to_remove:
            del self.memories[memory.memory_id]
            print(f"[MemoryTimeline] 🗑️ Removed old memory: {memory.content[:30]}...")
    
    def _build_memory_index(self):
        """Build memory index from existing memories"""
        self.memory_index.clear()
        for memory in self.memories.values():
            self._update_memory_index(memory)
    
    def _save_memories(self):
        """Save memories to persistent storage"""
        try:
            memories_file = self.memory_dir / f"{self.user_id}_memories.json"
            thematic_file = self.memory_dir / f"{self.user_id}_thematic_links.json"
            
            # Convert memories to serializable format
            memories_data = {}
            for memory_id, memory in self.memories.items():
                memory_dict = asdict(memory)
                memory_dict['timestamp'] = memory.timestamp.isoformat()
                memory_dict['last_accessed'] = memory.last_accessed.isoformat() if memory.last_accessed else None
                memory_dict['memory_type'] = memory.memory_type.value
                memory_dict['importance'] = memory.importance.value
                memory_dict['emotional_valence'] = memory.emotional_valence.value
                memories_data[memory_id] = memory_dict
            
            # Convert thematic links to serializable format
            thematic_data = {}
            for theme, link in self.thematic_links.items():
                link_dict = asdict(link)
                link_dict['creation_time'] = link.creation_time.isoformat()
                link_dict['last_reinforced'] = link.last_reinforced.isoformat()
                thematic_data[theme] = link_dict
            
            with open(memories_file, 'w') as f:
                json.dump(memories_data, f, indent=2)
            
            with open(thematic_file, 'w') as f:
                json.dump(thematic_data, f, indent=2)
                
        except Exception as e:
            print(f"[MemoryTimeline] ❌ Error saving memories: {e}")
    
    def _load_memories(self):
        """Load memories from persistent storage"""
        try:
            memories_file = self.memory_dir / f"{self.user_id}_memories.json"
            thematic_file = self.memory_dir / f"{self.user_id}_thematic_links.json"
            
            # Load memories
            if memories_file.exists():
                with open(memories_file, 'r') as f:
                    memories_data = json.load(f)
                
                for memory_id, memory_dict in memories_data.items():
                    # Convert back to proper types
                    memory_dict['memory_type'] = MemoryType(memory_dict['memory_type'])
                    memory_dict['importance'] = MemoryImportance(memory_dict['importance'])
                    memory_dict['emotional_valence'] = MemoryEmotionalValence(memory_dict['emotional_valence'])
                    
                    memory = MemoryObject(**memory_dict)
                    self.memories[memory_id] = memory
            
            # Load thematic links
            if thematic_file.exists():
                with open(thematic_file, 'r') as f:
                    thematic_data = json.load(f)
                
                for theme, link_dict in thematic_data.items():
                    link = ThematicLink(**link_dict)
                    self.thematic_links[theme] = link
                    
        except Exception as e:
            print(f"[MemoryTimeline] ⚠️ Error loading memories: {e}")
    
    def _start_background_processes(self):
        """Start background consolidation and auto-save processes"""
        def background_maintenance():
            while True:
                time.sleep(self.auto_save_interval)
                self._save_memories()
                self._consolidate_memories()
        
        maintenance_thread = threading.Thread(target=background_maintenance, daemon=True)
        maintenance_thread.start()
    
    def _consolidate_memories(self):
        """Consolidate memories over time"""
        cutoff_time = datetime.now() - self.consolidation_period
        
        with self.lock:
            for memory in self.memories.values():
                if memory.timestamp < cutoff_time and memory.consolidation_level < 1.0:
                    # Gradually consolidate memories
                    memory.consolidation_level = min(memory.consolidation_level + 0.1, 1.0)
                    
                    # Decay importance for low-importance memories
                    if memory.importance == MemoryImportance.LOW:
                        new_importance_value = memory.importance.value * self.importance_decay_rate
                        if new_importance_value < MemoryImportance.MINIMAL.value:
                            memory.importance = MemoryImportance.MINIMAL


# Global memory timeline instances per user
_memory_timelines: Dict[str, MemoryTimeline] = {}
_timeline_lock = threading.Lock()

def get_memory_timeline(user_id: str) -> MemoryTimeline:
    """Get or create memory timeline for a user"""
    with _timeline_lock:
        if user_id not in _memory_timelines:
            _memory_timelines[user_id] = MemoryTimeline(user_id)
        return _memory_timelines[user_id]

def store_user_memory(user_id: str, content: str, memory_type: MemoryType, 
                     importance: MemoryImportance, **kwargs) -> str:
    """Store a memory for a specific user"""
    timeline = get_memory_timeline(user_id)
    return timeline.store_memory(content, memory_type, importance, **kwargs)

def recall_user_memories(user_id: str, **kwargs) -> List[MemoryObject]:
    """Recall memories for a specific user"""
    timeline = get_memory_timeline(user_id)
    return timeline.recall_memories(**kwargs)