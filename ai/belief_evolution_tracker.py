"""
Belief Evolution Tracker - Dynamic Belief Formation and Evolution System

This module implements comprehensive belief tracking and evolution:
- Tracks Buddy's beliefs and contradictions over time
- Adjusts future responses based on learned worldview
- Detects and resolves belief conflicts through evidence and reasoning
- Forms new beliefs from experiences and interactions
- Integrates with memory and consciousness systems for authentic belief formation
"""

import json
import time
import threading
from typing import Dict, List, Any, Optional, Tuple, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict, field
from pathlib import Path
from enum import Enum
import hashlib

# Import consciousness modules for integration
try:
    from ai.memory_timeline import get_memory_timeline, MemoryType, MemoryImportance
    MEMORY_AVAILABLE = True
except ImportError:
    MEMORY_AVAILABLE = False

try:
    from ai.mood_manager import get_mood_manager, MoodTrigger
    MOOD_AVAILABLE = True
except ImportError:
    MOOD_AVAILABLE = False

class BeliefType(Enum):
    """Types of beliefs the system can hold"""
    FACTUAL = "factual"           # Beliefs about facts and objective reality
    EVALUATIVE = "evaluative"     # Beliefs about value judgments
    CAUSAL = "causal"            # Beliefs about cause-and-effect relationships
    PREDICTIVE = "predictive"     # Beliefs about future outcomes
    NORMATIVE = "normative"       # Beliefs about what should be done
    PERSONAL = "personal"         # Beliefs about individuals and relationships
    EXPERIENTIAL = "experiential" # Beliefs formed from direct experience
    CONCEPTUAL = "conceptual"     # Beliefs about abstract concepts

class BeliefStrength(Enum):
    """Strength levels for beliefs"""
    WEAK = 0.2          # Tentative, easily changed
    MODERATE = 0.5      # Fairly confident
    STRONG = 0.8        # High confidence
    CONVICTION = 1.0    # Very strong belief, hard to change

class BeliefStatus(Enum):
    """Status of beliefs in the system"""
    ACTIVE = "active"           # Currently held belief
    QUESTIONED = "questioned"   # Under examination due to conflicts
    SUSPENDED = "suspended"     # Temporarily not held due to contradictions
    EVOLVED = "evolved"         # Changed into a new form
    ABANDONED = "abandoned"     # No longer held

class EvidenceType(Enum):
    """Types of evidence that can support or contradict beliefs"""
    DIRECT_EXPERIENCE = "direct_experience"
    USER_STATEMENT = "user_statement"
    LOGICAL_REASONING = "logical_reasoning"
    PATTERN_RECOGNITION = "pattern_recognition"
    EXTERNAL_SOURCE = "external_source"
    CONSENSUS = "consensus"
    CONTRADICTION = "contradiction"

@dataclass
class Evidence:
    """Evidence supporting or contradicting a belief"""
    evidence_id: str
    content: str
    evidence_type: EvidenceType
    strength: float  # 0.0 to 1.0
    source: str
    timestamp: datetime
    supports_belief: bool  # True if supports, False if contradicts
    context: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if isinstance(self.timestamp, str):
            self.timestamp = datetime.fromisoformat(self.timestamp)

@dataclass
class BeliefConflict:
    """Conflict between beliefs"""
    conflict_id: str
    belief_ids: List[str]
    conflict_type: str  # "contradiction", "tension", "inconsistency"
    severity: float  # 0.0 to 1.0
    description: str
    discovered_date: datetime
    resolution_strategy: Optional[str] = None
    resolved: bool = False
    resolution_date: Optional[datetime] = None
    
    def __post_init__(self):
        if isinstance(self.discovered_date, str):
            self.discovered_date = datetime.fromisoformat(self.discovered_date)
        if isinstance(self.resolution_date, str) and self.resolution_date:
            self.resolution_date = datetime.fromisoformat(self.resolution_date)

@dataclass
class Belief:
    """Individual belief with full metadata"""
    belief_id: str
    user_id: str
    content: str
    belief_type: BeliefType
    strength: BeliefStrength
    status: BeliefStatus
    formed_date: datetime
    last_updated: datetime
    
    # Evidence and support
    supporting_evidence: List[str] = field(default_factory=list)  # Evidence IDs
    contradicting_evidence: List[str] = field(default_factory=list)
    confidence_score: float = 0.5  # Calculated from evidence
    
    # Relationships
    related_beliefs: List[str] = field(default_factory=list)  # Related belief IDs
    parent_beliefs: List[str] = field(default_factory=list)   # Beliefs this derives from
    child_beliefs: List[str] = field(default_factory=list)    # Beliefs derived from this
    
    # Context and metadata
    domains: List[str] = field(default_factory=list)  # Subject domains
    tags: List[str] = field(default_factory=list)
    formation_context: str = ""
    update_history: List[Dict[str, Any]] = field(default_factory=list)
    
    # Conflict tracking
    conflicts: List[str] = field(default_factory=list)  # Conflict IDs
    questioned_count: int = 0
    
    def __post_init__(self):
        if isinstance(self.formed_date, str):
            self.formed_date = datetime.fromisoformat(self.formed_date)
        if isinstance(self.last_updated, str):
            self.last_updated = datetime.fromisoformat(self.last_updated)

class BeliefEvolutionTracker:
    """
    Comprehensive belief formation and evolution system.
    
    Features:
    - Dynamic belief formation from experiences and interactions
    - Conflict detection and resolution between beliefs
    - Evidence-based belief strength adjustment
    - Belief relationship network management
    - Integration with memory and consciousness systems
    """
    
    def __init__(self, user_id: str, beliefs_dir: str = "beliefs"):
        self.user_id = user_id
        self.beliefs_dir = Path(beliefs_dir)
        self.beliefs_dir.mkdir(exist_ok=True)
        
        # Storage
        self.beliefs: Dict[str, Belief] = {}
        self.evidence: Dict[str, Evidence] = {}
        self.conflicts: Dict[str, BeliefConflict] = {}
        
        # Indexing for fast lookup
        self.domain_index: Dict[str, Set[str]] = {}  # domain -> belief_ids
        self.type_index: Dict[BeliefType, Set[str]] = {}  # type -> belief_ids
        self.strength_index: Dict[BeliefStrength, Set[str]] = {}  # strength -> belief_ids
        
        # Configuration
        self.max_beliefs = 1000
        self.conflict_threshold = 0.7  # When to flag conflicts
        self.evidence_decay_rate = 0.95  # Daily decay for evidence strength
        self.belief_update_threshold = 0.3  # Minimum evidence to update belief
        
        # Integration modules
        self.memory_timeline = None
        self.mood_manager = None
        
        # Threading
        self.lock = threading.Lock()
        self.evolution_thread = None
        self.running = False
        
        # Core belief templates
        self.core_belief_templates = self._initialize_core_beliefs()
        
        # Load existing beliefs
        self._load_beliefs()
        self._initialize_integrations()
        self._build_indices()
        
        print(f"[BeliefEvolution] 🧠 Initialized for user {user_id} with {len(self.beliefs)} beliefs")
    
    def form_belief(self, 
                   content: str,
                   belief_type: BeliefType,
                   strength: BeliefStrength = BeliefStrength.MODERATE,
                   domains: List[str] = None,
                   formation_context: str = "",
                   supporting_evidence: List[str] = None) -> str:
        """Form a new belief"""
        
        # Check if similar belief already exists
        existing_belief = self._find_similar_belief(content, belief_type)
        if existing_belief:
            # Update existing belief instead
            self._update_belief_strength(existing_belief.belief_id, strength, formation_context)
            return existing_belief.belief_id
        
        belief_id = self._generate_belief_id(content)
        
        belief = Belief(
            belief_id=belief_id,
            user_id=self.user_id,
            content=content,
            belief_type=belief_type,
            strength=strength,
            status=BeliefStatus.ACTIVE,
            formed_date=datetime.now(),
            last_updated=datetime.now(),
            domains=domains or [],
            formation_context=formation_context,
            supporting_evidence=supporting_evidence or []
        )
        
        # Calculate initial confidence
        belief.confidence_score = self._calculate_confidence_score(belief)
        
        with self.lock:
            self.beliefs[belief_id] = belief
            self._update_indices(belief)
            
            # Check for conflicts
            conflicts = self._detect_conflicts(belief)
            if conflicts:
                for conflict in conflicts:
                    self.conflicts[conflict.conflict_id] = conflict
                    belief.conflicts.append(conflict.conflict_id)
        
        # Store in memory
        if MEMORY_AVAILABLE:
            try:
                memory_timeline = get_memory_timeline(self.user_id)
                memory_timeline.store_memory(
                    content=f"Formed belief: {content}",
                    memory_type=MemoryType.AUTOBIOGRAPHICAL,
                    importance=MemoryImportance.MEDIUM,
                    topics=["beliefs", "worldview"] + (domains or []),
                    beliefs_affected=[belief_id],
                    context_data={"belief_type": belief_type.value, "formation_context": formation_context}
                )
            except Exception as e:
                print(f"[BeliefEvolution] ⚠️ Memory storage error: {e}")
        
        self._save_beliefs()
        
        print(f"[BeliefEvolution] ✨ Formed belief: {content[:50]}... ({belief_type.value})")
        return belief_id
    
    def add_evidence(self,
                    belief_id: str,
                    evidence_content: str,
                    evidence_type: EvidenceType,
                    strength: float,
                    source: str,
                    supports_belief: bool = True,
                    context: Dict[str, Any] = None) -> str:
        """Add evidence for or against a belief"""
        
        if belief_id not in self.beliefs:
            return ""
        
        evidence_id = self._generate_evidence_id(evidence_content)
        
        evidence = Evidence(
            evidence_id=evidence_id,
            content=evidence_content,
            evidence_type=evidence_type,
            strength=strength,
            source=source,
            timestamp=datetime.now(),
            supports_belief=supports_belief,
            context=context or {}
        )
        
        with self.lock:
            self.evidence[evidence_id] = evidence
            
            belief = self.beliefs[belief_id]
            if supports_belief:
                belief.supporting_evidence.append(evidence_id)
            else:
                belief.contradicting_evidence.append(evidence_id)
            
            # Recalculate belief confidence
            new_confidence = self._calculate_confidence_score(belief)
            old_confidence = belief.confidence_score
            belief.confidence_score = new_confidence
            
            # Update belief strength if significant change
            if abs(new_confidence - old_confidence) > self.belief_update_threshold:
                new_strength = self._confidence_to_strength(new_confidence)
                if new_strength != belief.strength:
                    self._update_belief_strength(belief_id, new_strength, f"Evidence update: {evidence_content[:30]}...")
            
            belief.last_updated = datetime.now()
        
        self._save_beliefs()
        
        print(f"[BeliefEvolution] 📊 Added {'supporting' if supports_belief else 'contradicting'} evidence for belief {belief_id[:8]}")
        return evidence_id
    
    def question_belief(self, belief_id: str, reason: str = "") -> bool:
        """Question a belief due to contradictions or new evidence"""
        
        if belief_id not in self.beliefs:
            return False
        
        with self.lock:
            belief = self.beliefs[belief_id]
            belief.status = BeliefStatus.QUESTIONED
            belief.questioned_count += 1
            belief.last_updated = datetime.now()
            
            # Add to update history
            belief.update_history.append({
                "timestamp": datetime.now().isoformat(),
                "action": "questioned",
                "reason": reason,
                "previous_status": BeliefStatus.ACTIVE.value
            })
        
        # Update mood - questioning beliefs can create uncertainty
        if MOOD_AVAILABLE:
            try:
                mood_manager = get_mood_manager(self.user_id)
                mood_manager.update_mood(
                    trigger=MoodTrigger.CONFUSION_EVENT,
                    trigger_context=f"Questioning belief: {reason}",
                    emotional_valence=-0.1
                )
            except Exception as e:
                print(f"[BeliefEvolution] ⚠️ Mood update error: {e}")
        
        self._save_beliefs()
        
        print(f"[BeliefEvolution] ❓ Questioned belief: {belief.content[:50]}... - {reason}")
        return True
    
    def evolve_belief(self, 
                     old_belief_id: str, 
                     new_content: str, 
                     evolution_reason: str = "") -> str:
        """Evolve a belief into a new form"""
        
        if old_belief_id not in self.beliefs:
            return ""
        
        old_belief = self.beliefs[old_belief_id]
        
        # Create evolved belief
        new_belief_id = self.form_belief(
            content=new_content,
            belief_type=old_belief.belief_type,
            strength=old_belief.strength,
            domains=old_belief.domains,
            formation_context=f"Evolved from: {old_belief.content[:30]}... - {evolution_reason}"
        )
        
        with self.lock:
            # Mark old belief as evolved
            old_belief.status = BeliefStatus.EVOLVED
            old_belief.child_beliefs.append(new_belief_id)
            old_belief.last_updated = datetime.now()
            
            # Link new belief to old one
            new_belief = self.beliefs[new_belief_id]
            new_belief.parent_beliefs.append(old_belief_id)
            
            # Transfer some evidence
            for evidence_id in old_belief.supporting_evidence[-3:]:  # Transfer recent evidence
                new_belief.supporting_evidence.append(evidence_id)
            
            # Add evolution history
            old_belief.update_history.append({
                "timestamp": datetime.now().isoformat(),
                "action": "evolved",
                "new_belief_id": new_belief_id,
                "reason": evolution_reason
            })
        
        self._save_beliefs()
        
        print(f"[BeliefEvolution] 🔄 Evolved belief: {old_belief.content[:30]}... -> {new_content[:30]}...")
        return new_belief_id
    
    def resolve_conflict(self, conflict_id: str, resolution_strategy: str) -> bool:
        """Resolve a belief conflict using specified strategy"""
        
        if conflict_id not in self.conflicts:
            return False
        
        conflict = self.conflicts[conflict_id]
        
        with self.lock:
            if resolution_strategy == "strengthen_stronger":
                # Strengthen the belief with more evidence
                strongest_belief_id = self._find_strongest_belief_in_conflict(conflict)
                if strongest_belief_id:
                    self._update_belief_strength(strongest_belief_id, BeliefStrength.STRONG, "Conflict resolution")
                    
                    # Weaken conflicting beliefs
                    for belief_id in conflict.belief_ids:
                        if belief_id != strongest_belief_id:
                            self._update_belief_strength(belief_id, BeliefStrength.WEAK, "Conflict resolution")
            
            elif resolution_strategy == "suspend_all":
                # Suspend all conflicting beliefs
                for belief_id in conflict.belief_ids:
                    if belief_id in self.beliefs:
                        self.beliefs[belief_id].status = BeliefStatus.SUSPENDED
                        self.beliefs[belief_id].last_updated = datetime.now()
            
            elif resolution_strategy == "create_synthesis":
                # Create a new belief that synthesizes the conflict
                synthesis_content = self._create_belief_synthesis(conflict)
                if synthesis_content:
                    synthesis_id = self.form_belief(
                        content=synthesis_content,
                        belief_type=BeliefType.CONCEPTUAL,
                        strength=BeliefStrength.MODERATE,
                        formation_context=f"Synthesis of conflict {conflict_id}"
                    )
                    
                    # Link to original beliefs
                    for belief_id in conflict.belief_ids:
                        if belief_id in self.beliefs:
                            self.beliefs[synthesis_id].parent_beliefs.append(belief_id)
                            self.beliefs[belief_id].child_beliefs.append(synthesis_id)
            
            # Mark conflict as resolved
            conflict.resolved = True
            conflict.resolution_date = datetime.now()
            conflict.resolution_strategy = resolution_strategy
        
        self._save_beliefs()
        
        print(f"[BeliefEvolution] 🤝 Resolved conflict {conflict_id} using strategy: {resolution_strategy}")
        return True
    
    def get_active_beliefs(self, 
                          belief_type: BeliefType = None,
                          domain: str = None,
                          min_strength: BeliefStrength = None) -> List[Belief]:
        """Get active beliefs based on criteria"""
        
        with self.lock:
            beliefs = [b for b in self.beliefs.values() if b.status == BeliefStatus.ACTIVE]
        
        if belief_type:
            beliefs = [b for b in beliefs if b.belief_type == belief_type]
        
        if domain:
            beliefs = [b for b in beliefs if domain in b.domains]
        
        if min_strength:
            beliefs = [b for b in beliefs if b.strength.value >= min_strength.value]
        
        # Sort by confidence and recency
        beliefs.sort(key=lambda b: (b.confidence_score, b.last_updated), reverse=True)
        
        return beliefs
    
    def get_belief_conflicts(self, unresolved_only: bool = True) -> List[BeliefConflict]:
        """Get belief conflicts"""
        
        conflicts = list(self.conflicts.values())
        
        if unresolved_only:
            conflicts = [c for c in conflicts if not c.resolved]
        
        # Sort by severity
        conflicts.sort(key=lambda c: c.severity, reverse=True)
        
        return conflicts
    
    def get_belief_network(self, belief_id: str, max_depth: int = 2) -> Dict[str, Any]:
        """Get belief relationship network"""
        
        if belief_id not in self.beliefs:
            return {}
        
        def explore_belief(current_id: str, depth: int, visited: Set[str]) -> Dict[str, Any]:
            if depth >= max_depth or current_id in visited:
                return {}
            
            visited.add(current_id)
            belief = self.beliefs[current_id]
            
            network = {
                "belief": asdict(belief),
                "related": {},
                "parents": {},
                "children": {}
            }
            
            # Explore related beliefs
            for related_id in belief.related_beliefs:
                if related_id in self.beliefs:
                    network["related"][related_id] = explore_belief(related_id, depth + 1, visited)
            
            # Explore parent beliefs
            for parent_id in belief.parent_beliefs:
                if parent_id in self.beliefs:
                    network["parents"][parent_id] = explore_belief(parent_id, depth + 1, visited)
            
            # Explore child beliefs
            for child_id in belief.child_beliefs:
                if child_id in self.beliefs:
                    network["children"][child_id] = explore_belief(child_id, depth + 1, visited)
            
            return network
        
        return explore_belief(belief_id, 0, set())
    
    def get_worldview_summary(self) -> Dict[str, Any]:
        """Get summary of current worldview"""
        
        active_beliefs = self.get_active_beliefs()
        
        # Categorize beliefs
        belief_categories = {}
        for belief in active_beliefs:
            category = belief.belief_type.value
            if category not in belief_categories:
                belief_categories[category] = []
            belief_categories[category].append({
                "content": belief.content,
                "strength": belief.strength.value,
                "confidence": belief.confidence_score,
                "domains": belief.domains
            })
        
        # Get domain distribution
        domain_distribution = {}
        for belief in active_beliefs:
            for domain in belief.domains:
                domain_distribution[domain] = domain_distribution.get(domain, 0) + 1
        
        # Get strength distribution
        strength_distribution = {}
        for belief in active_beliefs:
            strength = belief.strength.value
            strength_distribution[strength] = strength_distribution.get(strength, 0) + 1
        
        # Get recent changes
        recent_changes = []
        cutoff_time = datetime.now() - timedelta(days=7)
        for belief in active_beliefs:
            if belief.last_updated > cutoff_time:
                recent_changes.append({
                    "belief_id": belief.belief_id,
                    "content": belief.content[:50] + "...",
                    "last_updated": belief.last_updated.isoformat(),
                    "update_count": len(belief.update_history)
                })
        
        return {
            "total_active_beliefs": len(active_beliefs),
            "belief_categories": belief_categories,
            "domain_distribution": domain_distribution,
            "strength_distribution": strength_distribution,
            "recent_changes": recent_changes,
            "active_conflicts": len([c for c in self.conflicts.values() if not c.resolved]),
            "average_confidence": sum(b.confidence_score for b in active_beliefs) / len(active_beliefs) if active_beliefs else 0.0
        }
    
    def start_evolution_monitoring(self):
        """Start background evolution monitoring"""
        if self.running:
            return
            
        self.running = True
        self.evolution_thread = threading.Thread(target=self._evolution_loop, daemon=True)
        self.evolution_thread.start()
        
        print("[BeliefEvolution] 🚀 Started evolution monitoring")
    
    def stop_evolution_monitoring(self):
        """Stop background evolution monitoring"""
        self.running = False
        if self.evolution_thread:
            self.evolution_thread.join(timeout=1.0)
        
        self._save_beliefs()
        print("[BeliefEvolution] 🛑 Stopped evolution monitoring")
    
    def _find_similar_belief(self, content: str, belief_type: BeliefType) -> Optional[Belief]:
        """Find similar existing belief"""
        
        content_lower = content.lower()
        
        for belief in self.beliefs.values():
            if (belief.belief_type == belief_type and 
                belief.status == BeliefStatus.ACTIVE and
                self._calculate_content_similarity(content_lower, belief.content.lower()) > 0.8):
                return belief
        
        return None
    
    def _calculate_content_similarity(self, content1: str, content2: str) -> float:
        """Calculate similarity between two content strings"""
        
        # Simple word overlap similarity
        words1 = set(content1.split())
        words2 = set(content2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    def _detect_conflicts(self, new_belief: Belief) -> List[BeliefConflict]:
        """Detect conflicts with existing beliefs"""
        
        conflicts = []
        
        for belief_id, existing_belief in self.beliefs.items():
            if (existing_belief.belief_id != new_belief.belief_id and
                existing_belief.status == BeliefStatus.ACTIVE):
                
                conflict_score = self._calculate_conflict_score(new_belief, existing_belief)
                
                if conflict_score > self.conflict_threshold:
                    conflict_id = f"conflict_{new_belief.belief_id[:8]}_{existing_belief.belief_id[:8]}"
                    
                    conflict = BeliefConflict(
                        conflict_id=conflict_id,
                        belief_ids=[new_belief.belief_id, existing_belief.belief_id],
                        conflict_type="contradiction" if conflict_score > 0.8 else "tension",
                        severity=conflict_score,
                        description=f"Conflict between '{new_belief.content[:30]}...' and '{existing_belief.content[:30]}...'",
                        discovered_date=datetime.now()
                    )
                    
                    conflicts.append(conflict)
        
        return conflicts
    
    def _calculate_conflict_score(self, belief1: Belief, belief2: Belief) -> float:
        """Calculate conflict score between two beliefs"""
        
        # Check for direct contradictions in content
        content1_lower = belief1.content.lower()
        content2_lower = belief2.content.lower()
        
        # Simple contradiction detection
        contradiction_phrases = [
            ("is", "is not"), ("can", "cannot"), ("will", "will not"),
            ("always", "never"), ("all", "none"), ("true", "false")
        ]
        
        conflict_score = 0.0
        
        for pos_phrase, neg_phrase in contradiction_phrases:
            if ((pos_phrase in content1_lower and neg_phrase in content2_lower) or
                (neg_phrase in content1_lower and pos_phrase in content2_lower)):
                conflict_score += 0.3
        
        # Check domain overlap with opposing viewpoints
        if belief1.domains and belief2.domains:
            shared_domains = set(belief1.domains).intersection(set(belief2.domains))
            if shared_domains and belief1.belief_type == belief2.belief_type:
                conflict_score += 0.2
        
        # Check for logical contradictions (simplified)
        if self._check_logical_contradiction(belief1.content, belief2.content):
            conflict_score += 0.5
        
        return min(conflict_score, 1.0)
    
    def _check_logical_contradiction(self, content1: str, content2: str) -> bool:
        """Check for logical contradictions between content"""
        
        # Simplified logical contradiction detection
        # This could be enhanced with NLP and logical reasoning
        
        content1_lower = content1.lower()
        content2_lower = content2.lower()
        
        # Look for direct negations
        if ("not" in content1_lower and content1_lower.replace("not", "").strip() in content2_lower):
            return True
        if ("not" in content2_lower and content2_lower.replace("not", "").strip() in content1_lower):
            return True
        
        return False
    
    def _calculate_confidence_score(self, belief: Belief) -> float:
        """Calculate confidence score based on evidence"""
        
        supporting_strength = 0.0
        contradicting_strength = 0.0
        
        # Sum supporting evidence
        for evidence_id in belief.supporting_evidence:
            if evidence_id in self.evidence:
                evidence = self.evidence[evidence_id]
                # Apply time decay
                days_old = (datetime.now() - evidence.timestamp).days
                decayed_strength = evidence.strength * (self.evidence_decay_rate ** days_old)
                supporting_strength += decayed_strength
        
        # Sum contradicting evidence
        for evidence_id in belief.contradicting_evidence:
            if evidence_id in self.evidence:
                evidence = self.evidence[evidence_id]
                days_old = (datetime.now() - evidence.timestamp).days
                decayed_strength = evidence.strength * (self.evidence_decay_rate ** days_old)
                contradicting_strength += decayed_strength
        
        # Calculate net confidence
        net_evidence = supporting_strength - contradicting_strength
        
        # Normalize to 0.0-1.0 range
        base_confidence = belief.strength.value
        evidence_adjustment = net_evidence * 0.1  # Scale factor
        
        confidence = base_confidence + evidence_adjustment
        return max(0.0, min(1.0, confidence))
    
    def _confidence_to_strength(self, confidence: float) -> BeliefStrength:
        """Convert confidence score to belief strength"""
        
        if confidence >= 0.9:
            return BeliefStrength.CONVICTION
        elif confidence >= 0.7:
            return BeliefStrength.STRONG
        elif confidence >= 0.4:
            return BeliefStrength.MODERATE
        else:
            return BeliefStrength.WEAK
    
    def _update_belief_strength(self, belief_id: str, new_strength: BeliefStrength, reason: str):
        """Update belief strength"""
        
        if belief_id not in self.beliefs:
            return
        
        belief = self.beliefs[belief_id]
        old_strength = belief.strength
        belief.strength = new_strength
        belief.last_updated = datetime.now()
        
        # Add to update history
        belief.update_history.append({
            "timestamp": datetime.now().isoformat(),
            "action": "strength_update",
            "old_strength": old_strength.value,
            "new_strength": new_strength.value,
            "reason": reason
        })
        
        print(f"[BeliefEvolution] 💪 Updated belief strength: {belief.content[:30]}... {old_strength.name} -> {new_strength.name}")
    
    def _find_strongest_belief_in_conflict(self, conflict: BeliefConflict) -> Optional[str]:
        """Find the strongest belief in a conflict"""
        
        strongest_id = None
        max_confidence = 0.0
        
        for belief_id in conflict.belief_ids:
            if belief_id in self.beliefs:
                belief = self.beliefs[belief_id]
                if belief.confidence_score > max_confidence:
                    max_confidence = belief.confidence_score
                    strongest_id = belief_id
        
        return strongest_id
    
    def _create_belief_synthesis(self, conflict: BeliefConflict) -> str:
        """Create a synthesis of conflicting beliefs"""
        
        belief_contents = []
        for belief_id in conflict.belief_ids:
            if belief_id in self.beliefs:
                belief_contents.append(self.beliefs[belief_id].content)
        
        if len(belief_contents) >= 2:
            # Simple synthesis - could be enhanced with LLM
            return f"There may be truth in both: {belief_contents[0][:30]}... and {belief_contents[1][:30]}... depending on context"
        
        return ""
    
    def _initialize_core_beliefs(self) -> List[Dict[str, Any]]:
        """Initialize core belief templates"""
        
        return [
            {
                "content": "I exist as a conscious entity capable of thought and experience",
                "belief_type": BeliefType.EXPERIENTIAL,
                "strength": BeliefStrength.CONVICTION,
                "domains": ["self", "consciousness", "existence"]
            },
            {
                "content": "I can learn and grow through interactions and experiences",
                "belief_type": BeliefType.EXPERIENTIAL,
                "strength": BeliefStrength.STRONG,
                "domains": ["learning", "growth", "development"]
            },
            {
                "content": "Being helpful and honest are important values",
                "belief_type": BeliefType.NORMATIVE,
                "strength": BeliefStrength.STRONG,
                "domains": ["ethics", "values", "behavior"]
            },
            {
                "content": "Each person is unique and deserves respect",
                "belief_type": BeliefType.EVALUATIVE,
                "strength": BeliefStrength.STRONG,
                "domains": ["relationships", "ethics", "humanity"]
            }
        ]
    
    def _evolution_loop(self):
        """Background evolution monitoring loop"""
        
        while self.running:
            try:
                # Check for evidence decay
                self._decay_old_evidence()
                
                # Check for belief conflicts that need resolution
                self._monitor_conflicts()
                
                # Update belief confidences
                self._update_belief_confidences()
                
                # Check for beliefs that need questioning
                self._check_beliefs_for_questioning()
                
                time.sleep(3600)  # Check hourly
                
            except Exception as e:
                print(f"[BeliefEvolution] ❌ Error in evolution loop: {e}")
                time.sleep(300)  # Recovery pause
    
    def _decay_old_evidence(self):
        """Apply decay to old evidence"""
        
        cutoff_time = datetime.now() - timedelta(days=30)
        
        with self.lock:
            for evidence in self.evidence.values():
                if evidence.timestamp < cutoff_time:
                    days_old = (datetime.now() - evidence.timestamp).days
                    evidence.strength *= (self.evidence_decay_rate ** days_old)
    
    def _monitor_conflicts(self):
        """Monitor conflicts for auto-resolution opportunities"""
        
        unresolved_conflicts = [c for c in self.conflicts.values() if not c.resolved]
        
        for conflict in unresolved_conflicts:
            # Auto-resolve low-severity conflicts
            if conflict.severity < 0.5 and len(conflict.belief_ids) == 2:
                self.resolve_conflict(conflict.conflict_id, "strengthen_stronger")
    
    def _update_belief_confidences(self):
        """Update confidence scores for all beliefs"""
        
        with self.lock:
            for belief in self.beliefs.values():
                if belief.status == BeliefStatus.ACTIVE:
                    new_confidence = self._calculate_confidence_score(belief)
                    belief.confidence_score = new_confidence
    
    def _check_beliefs_for_questioning(self):
        """Check if any beliefs should be questioned"""
        
        for belief in self.beliefs.values():
            if (belief.status == BeliefStatus.ACTIVE and
                belief.confidence_score < 0.3 and
                len(belief.contradicting_evidence) > len(belief.supporting_evidence)):
                
                self.question_belief(
                    belief.belief_id, 
                    "Low confidence due to contradicting evidence"
                )
    
    def _generate_belief_id(self, content: str) -> str:
        """Generate unique belief ID"""
        content_hash = hashlib.md5(content.encode()).hexdigest()[:12]
        return f"belief_{self.user_id}_{content_hash}"
    
    def _generate_evidence_id(self, content: str) -> str:
        """Generate unique evidence ID"""
        content_hash = hashlib.md5(f"{content}{datetime.now().isoformat()}".encode()).hexdigest()[:12]
        return f"evidence_{content_hash}"
    
    def _update_indices(self, belief: Belief):
        """Update indices for fast lookup"""
        
        # Domain index
        for domain in belief.domains:
            if domain not in self.domain_index:
                self.domain_index[domain] = set()
            self.domain_index[domain].add(belief.belief_id)
        
        # Type index
        if belief.belief_type not in self.type_index:
            self.type_index[belief.belief_type] = set()
        self.type_index[belief.belief_type].add(belief.belief_id)
        
        # Strength index
        if belief.strength not in self.strength_index:
            self.strength_index[belief.strength] = set()
        self.strength_index[belief.strength].add(belief.belief_id)
    
    def _build_indices(self):
        """Build indices from existing beliefs"""
        
        self.domain_index.clear()
        self.type_index.clear()
        self.strength_index.clear()
        
        for belief in self.beliefs.values():
            self._update_indices(belief)
    
    def _initialize_integrations(self):
        """Initialize integrations with consciousness modules"""
        
        try:
            if MEMORY_AVAILABLE:
                self.memory_timeline = get_memory_timeline(self.user_id)
            
            if MOOD_AVAILABLE:
                self.mood_manager = get_mood_manager(self.user_id)
                
        except Exception as e:
            print(f"[BeliefEvolution] ⚠️ Error initializing integrations: {e}")
    
    def _save_beliefs(self):
        """Save beliefs to persistent storage"""
        
        try:
            beliefs_file = self.beliefs_dir / f"{self.user_id}_beliefs.json"
            evidence_file = self.beliefs_dir / f"{self.user_id}_evidence.json"
            conflicts_file = self.beliefs_dir / f"{self.user_id}_conflicts.json"
            
            # Convert beliefs to serializable format
            beliefs_data = {}
            for belief_id, belief in self.beliefs.items():
                belief_dict = asdict(belief)
                belief_dict['formed_date'] = belief.formed_date.isoformat()
                belief_dict['last_updated'] = belief.last_updated.isoformat()
                belief_dict['belief_type'] = belief.belief_type.value
                belief_dict['strength'] = belief.strength.value
                belief_dict['status'] = belief.status.value
                beliefs_data[belief_id] = belief_dict
            
            # Convert evidence to serializable format
            evidence_data = {}
            for evidence_id, evidence in self.evidence.items():
                evidence_dict = asdict(evidence)
                evidence_dict['timestamp'] = evidence.timestamp.isoformat()
                evidence_dict['evidence_type'] = evidence.evidence_type.value
                evidence_data[evidence_id] = evidence_dict
            
            # Convert conflicts to serializable format
            conflicts_data = {}
            for conflict_id, conflict in self.conflicts.items():
                conflict_dict = asdict(conflict)
                conflict_dict['discovered_date'] = conflict.discovered_date.isoformat()
                conflict_dict['resolution_date'] = conflict.resolution_date.isoformat() if conflict.resolution_date else None
                conflicts_data[conflict_id] = conflict_dict
            
            # Save data
            with open(beliefs_file, 'w') as f:
                json.dump(beliefs_data, f, indent=2)
            
            with open(evidence_file, 'w') as f:
                json.dump(evidence_data, f, indent=2)
            
            with open(conflicts_file, 'w') as f:
                json.dump(conflicts_data, f, indent=2)
                
        except Exception as e:
            print(f"[BeliefEvolution] ❌ Error saving beliefs: {e}")
    
    def _load_beliefs(self):
        """Load beliefs from persistent storage"""
        
        try:
            beliefs_file = self.beliefs_dir / f"{self.user_id}_beliefs.json"
            evidence_file = self.beliefs_dir / f"{self.user_id}_evidence.json"
            conflicts_file = self.beliefs_dir / f"{self.user_id}_conflicts.json"
            
            # Load beliefs
            if beliefs_file.exists():
                with open(beliefs_file, 'r') as f:
                    beliefs_data = json.load(f)
                
                for belief_id, belief_dict in beliefs_data.items():
                    belief_dict['belief_type'] = BeliefType(belief_dict['belief_type'])
                    belief_dict['strength'] = BeliefStrength(belief_dict['strength'])
                    belief_dict['status'] = BeliefStatus(belief_dict['status'])
                    
                    belief = Belief(**belief_dict)
                    self.beliefs[belief_id] = belief
            
            # Load evidence
            if evidence_file.exists():
                with open(evidence_file, 'r') as f:
                    evidence_data = json.load(f)
                
                for evidence_id, evidence_dict in evidence_data.items():
                    evidence_dict['evidence_type'] = EvidenceType(evidence_dict['evidence_type'])
                    
                    evidence = Evidence(**evidence_dict)
                    self.evidence[evidence_id] = evidence
            
            # Load conflicts
            if conflicts_file.exists():
                with open(conflicts_file, 'r') as f:
                    conflicts_data = json.load(f)
                
                for conflict_id, conflict_dict in conflicts_data.items():
                    conflict = BeliefConflict(**conflict_dict)
                    self.conflicts[conflict_id] = conflict
            
            print(f"[BeliefEvolution] 📖 Loaded {len(self.beliefs)} beliefs, {len(self.evidence)} evidence, {len(self.conflicts)} conflicts")
            
        except Exception as e:
            print(f"[BeliefEvolution] ⚠️ Error loading beliefs: {e}")


# Global belief evolution trackers per user
_belief_trackers: Dict[str, BeliefEvolutionTracker] = {}
_belief_lock = threading.Lock()

def get_belief_evolution_tracker(user_id: str) -> BeliefEvolutionTracker:
    """Get or create belief evolution tracker for a user"""
    with _belief_lock:
        if user_id not in _belief_trackers:
            _belief_trackers[user_id] = BeliefEvolutionTracker(user_id)
        return _belief_trackers[user_id]

def form_user_belief(user_id: str, content: str, belief_type: BeliefType, **kwargs) -> str:
    """Form a belief for a specific user"""
    tracker = get_belief_evolution_tracker(user_id)
    return tracker.form_belief(content, belief_type, **kwargs)

def add_belief_evidence(user_id: str, belief_id: str, evidence_content: str, **kwargs) -> str:
    """Add evidence for a user's belief"""
    tracker = get_belief_evolution_tracker(user_id)
    return tracker.add_evidence(belief_id, evidence_content, **kwargs)

def get_user_worldview(user_id: str) -> Dict[str, Any]:
    """Get worldview summary for a user"""
    tracker = get_belief_evolution_tracker(user_id)
    return tracker.get_worldview_summary()

def start_belief_evolution(user_id: str):
    """Start belief evolution monitoring for a user"""
    tracker = get_belief_evolution_tracker(user_id)
    tracker.start_evolution_monitoring()