"""
Belief Memory Refiner - Enhance belief confidence from repetition
Provides dynamic belief strength adjustment and memory consolidation
"""

import json
import time
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from collections import defaultdict
import statistics
from enum import Enum
import hashlib

class BeliefStrength(Enum):
    """Belief strength levels"""
    VERY_WEAK = "very_weak"
    WEAK = "weak"
    MODERATE = "moderate"
    STRONG = "strong"
    VERY_STRONG = "very_strong"

class BeliefSource(Enum):
    """Sources of beliefs"""
    USER_STATEMENT = "user_statement"
    OBSERVATION = "observation"
    INFERENCE = "inference"
    EXTERNAL_INFORMATION = "external_information"
    REPETITION = "repetition"
    CONFIRMATION = "confirmation"

@dataclass
class BeliefInstance:
    """Individual instance of a belief"""
    instance_id: str
    content: str
    source: BeliefSource
    confidence: float
    timestamp: str
    context: str
    user_id: str
    supporting_evidence: List[str]

@dataclass
class RefinedBelief:
    """Refined belief with enhanced confidence"""
    belief_id: str
    original_content: str
    refined_content: str
    instances: List[BeliefInstance]
    strength: BeliefStrength
    confidence: float
    first_occurrence: str
    last_reinforcement: str
    reinforcement_count: int
    supporting_instances: int
    conflicting_instances: int
    consistency_score: float
    evidence_quality: float
    user_associations: List[str]
    contextual_variations: List[str]

class BeliefMemoryRefiner:
    """System for refining belief confidence through repetition and evidence"""
    
    def __init__(self, save_path: str = "belief_memory_refiner.json"):
        self.save_path = save_path
        self.belief_instances: List[BeliefInstance] = []
        self.refined_beliefs: Dict[str, RefinedBelief] = {}
        self.belief_clusters: Dict[str, List[str]] = {}  # Similar beliefs grouped
        self.load_refiner_data()
        
        # Configuration
        self.similarity_threshold = 0.75  # Threshold for belief similarity
        self.reinforcement_decay = 0.95  # Decay rate for old reinforcements
        self.min_instances_for_refinement = 2
        self.max_instances_per_belief = 50
        
        # Confidence adjustment parameters
        self.repetition_boost = 0.1  # Confidence boost per repetition
        self.consistency_weight = 0.3  # Weight of consistency in confidence
        self.evidence_quality_weight = 0.2  # Weight of evidence quality
        self.temporal_weight = 0.1  # Weight of temporal factors
    
    def process_belief(self, belief_content: str, user_id: str, context: str, source: BeliefSource = BeliefSource.USER_STATEMENT) -> str:
        """Process a new belief and update refinement"""
        try:
            # Create belief instance
            instance = BeliefInstance(
                instance_id=f"instance_{len(self.belief_instances)}",
                content=belief_content,
                source=source,
                confidence=self._calculate_initial_confidence(belief_content, source),
                timestamp=datetime.now().isoformat(),
                context=context,
                user_id=user_id,
                supporting_evidence=[]
            )
            
            self.belief_instances.append(instance)
            
            # Find similar beliefs
            similar_beliefs = self._find_similar_beliefs(belief_content)
            
            if similar_beliefs:
                # Reinforce existing belief
                belief_id = similar_beliefs[0]
                self._reinforce_belief(belief_id, instance)
                print(f"[BeliefMemoryRefiner] 🔄 Reinforced belief: {belief_id}")
            else:
                # Create new refined belief
                belief_id = self._create_refined_belief(instance)
                print(f"[BeliefMemoryRefiner] 🆕 Created new belief: {belief_id}")
            
            # Update belief clusters
            self._update_belief_clusters(belief_id, belief_content)
            
            self.save_refiner_data()
            return belief_id
            
        except Exception as e:
            print(f"[BeliefMemoryRefiner] ❌ Error processing belief: {e}")
            return f"error_{len(self.belief_instances)}"
    
    def _calculate_initial_confidence(self, belief_content: str, source: BeliefSource) -> float:
        """Calculate initial confidence for a belief"""
        base_confidence = 0.5
        
        # Adjust based on source
        source_adjustments = {
            BeliefSource.USER_STATEMENT: 0.7,
            BeliefSource.OBSERVATION: 0.6,
            BeliefSource.INFERENCE: 0.4,
            BeliefSource.EXTERNAL_INFORMATION: 0.8,
            BeliefSource.REPETITION: 0.6,
            BeliefSource.CONFIRMATION: 0.75
        }
        
        confidence = source_adjustments.get(source, base_confidence)
        
        # Adjust based on content characteristics
        content_lower = belief_content.lower()
        
        # Definitive language increases confidence
        if any(word in content_lower for word in ['definitely', 'certainly', 'always', 'never']):
            confidence += 0.1
        
        # Uncertain language decreases confidence
        if any(word in content_lower for word in ['maybe', 'possibly', 'might', 'could']):
            confidence -= 0.1
        
        # Specific information increases confidence
        if any(char.isdigit() for char in belief_content):
            confidence += 0.05
        
        # Emotional content might be less reliable
        if any(word in content_lower for word in ['love', 'hate', 'amazing', 'terrible']):
            confidence -= 0.05
        
        return max(0.1, min(0.9, confidence))
    
    def _find_similar_beliefs(self, belief_content: str) -> List[str]:
        """Find similar existing beliefs"""
        similar_beliefs = []
        
        for belief_id, refined_belief in self.refined_beliefs.items():
            similarity = self._calculate_similarity(belief_content, refined_belief.refined_content)
            if similarity >= self.similarity_threshold:
                similar_beliefs.append(belief_id)
        
        # Sort by similarity (most similar first)
        similar_beliefs.sort(key=lambda bid: self._calculate_similarity(belief_content, self.refined_beliefs[bid].refined_content), reverse=True)
        
        return similar_beliefs
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two belief texts"""
        # Simple word-based similarity
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        # Jaccard similarity
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        return intersection / union if union > 0 else 0.0
    
    def _create_refined_belief(self, instance: BeliefInstance) -> str:
        """Create a new refined belief"""
        belief_id = f"belief_{hashlib.md5(instance.content.encode()).hexdigest()[:8]}"
        
        refined_belief = RefinedBelief(
            belief_id=belief_id,
            original_content=instance.content,
            refined_content=instance.content,
            instances=[instance],
            strength=self._determine_strength(instance.confidence),
            confidence=instance.confidence,
            first_occurrence=instance.timestamp,
            last_reinforcement=instance.timestamp,
            reinforcement_count=1,
            supporting_instances=1,
            conflicting_instances=0,
            consistency_score=1.0,
            evidence_quality=self._evaluate_evidence_quality(instance),
            user_associations=[instance.user_id],
            contextual_variations=[instance.context]
        )
        
        self.refined_beliefs[belief_id] = refined_belief
        return belief_id
    
    def _reinforce_belief(self, belief_id: str, instance: BeliefInstance):
        """Reinforce an existing belief"""
        if belief_id not in self.refined_beliefs:
            return
        
        refined_belief = self.refined_beliefs[belief_id]
        
        # Add instance
        refined_belief.instances.append(instance)
        
        # Limit instances to prevent memory bloat
        if len(refined_belief.instances) > self.max_instances_per_belief:
            refined_belief.instances = refined_belief.instances[-self.max_instances_per_belief:]
        
        # Update reinforcement count
        refined_belief.reinforcement_count += 1
        refined_belief.last_reinforcement = instance.timestamp
        
        # Check if this is supporting or conflicting
        if self._is_supporting_instance(instance, refined_belief):
            refined_belief.supporting_instances += 1
        else:
            refined_belief.conflicting_instances += 1
        
        # Update user associations
        if instance.user_id not in refined_belief.user_associations:
            refined_belief.user_associations.append(instance.user_id)
        
        # Update contextual variations
        if instance.context not in refined_belief.contextual_variations:
            refined_belief.contextual_variations.append(instance.context)
        
        # Recalculate confidence and strength
        self._update_belief_confidence(belief_id)
        self._update_belief_strength(belief_id)
        
        # Update refined content if needed
        self._update_refined_content(belief_id)
    
    def _is_supporting_instance(self, instance: BeliefInstance, refined_belief: RefinedBelief) -> bool:
        """Check if instance supports the refined belief"""
        # Simple similarity check
        similarity = self._calculate_similarity(instance.content, refined_belief.refined_content)
        return similarity >= self.similarity_threshold
    
    def _update_belief_confidence(self, belief_id: str):
        """Update belief confidence based on reinforcement"""
        refined_belief = self.refined_beliefs[belief_id]
        
        # Base confidence from instances
        instance_confidences = [i.confidence for i in refined_belief.instances]
        base_confidence = statistics.mean(instance_confidences)
        
        # Repetition boost
        repetition_factor = min(1.0, refined_belief.reinforcement_count * self.repetition_boost)
        
        # Consistency factor
        consistency_factor = refined_belief.supporting_instances / max(1, refined_belief.supporting_instances + refined_belief.conflicting_instances)
        
        # Evidence quality factor
        evidence_factor = refined_belief.evidence_quality
        
        # Temporal factor (recent reinforcements are more valuable)
        temporal_factor = self._calculate_temporal_factor(refined_belief)
        
        # Combined confidence
        new_confidence = (
            base_confidence * (1 - self.consistency_weight - self.evidence_quality_weight - self.temporal_weight) +
            consistency_factor * self.consistency_weight +
            evidence_factor * self.evidence_quality_weight +
            temporal_factor * self.temporal_weight
        )
        
        # Apply repetition boost
        new_confidence += repetition_factor * 0.1
        
        refined_belief.confidence = max(0.1, min(0.95, new_confidence))
        refined_belief.consistency_score = consistency_factor
    
    def _update_belief_strength(self, belief_id: str):
        """Update belief strength based on confidence"""
        refined_belief = self.refined_beliefs[belief_id]
        refined_belief.strength = self._determine_strength(refined_belief.confidence)
    
    def _determine_strength(self, confidence: float) -> BeliefStrength:
        """Determine belief strength from confidence"""
        if confidence >= 0.8:
            return BeliefStrength.VERY_STRONG
        elif confidence >= 0.65:
            return BeliefStrength.STRONG
        elif confidence >= 0.5:
            return BeliefStrength.MODERATE
        elif confidence >= 0.35:
            return BeliefStrength.WEAK
        else:
            return BeliefStrength.VERY_WEAK
    
    def _evaluate_evidence_quality(self, instance: BeliefInstance) -> float:
        """Evaluate quality of evidence for an instance"""
        quality = 0.5  # Base quality
        
        # Source quality
        source_quality = {
            BeliefSource.EXTERNAL_INFORMATION: 0.8,
            BeliefSource.OBSERVATION: 0.7,
            BeliefSource.USER_STATEMENT: 0.6,
            BeliefSource.CONFIRMATION: 0.7,
            BeliefSource.REPETITION: 0.5,
            BeliefSource.INFERENCE: 0.4
        }
        
        quality = source_quality.get(instance.source, 0.5)
        
        # Content quality indicators
        content_lower = instance.content.lower()
        
        # Specific details increase quality
        if any(char.isdigit() for char in instance.content):
            quality += 0.1
        
        # Proper nouns increase quality
        if any(word[0].isupper() for word in instance.content.split()):
            quality += 0.05
        
        # Vague language decreases quality
        if any(word in content_lower for word in ['some', 'many', 'often', 'sometimes']):
            quality -= 0.05
        
        return max(0.1, min(0.9, quality))
    
    def _calculate_temporal_factor(self, refined_belief: RefinedBelief) -> float:
        """Calculate temporal factor for belief confidence"""
        try:
            # Get timestamps of recent instances
            recent_instances = [i for i in refined_belief.instances[-10:]]  # Last 10 instances
            
            if not recent_instances:
                return 0.5
            
            # Calculate average age of recent instances
            now = datetime.now()
            ages = []
            
            for instance in recent_instances:
                instance_time = datetime.fromisoformat(instance.timestamp)
                age_hours = (now - instance_time).total_seconds() / 3600
                ages.append(age_hours)
            
            avg_age_hours = statistics.mean(ages)
            
            # Recent reinforcements are more valuable
            temporal_factor = max(0.1, 1.0 - (avg_age_hours / (24 * 7)))  # Decay over a week
            
            return temporal_factor
            
        except Exception as e:
            print(f"[BeliefMemoryRefiner] ⚠️ Error calculating temporal factor: {e}")
            return 0.5
    
    def _update_refined_content(self, belief_id: str):
        """Update refined content based on instances"""
        refined_belief = self.refined_beliefs[belief_id]
        
        # For now, use the most recent high-confidence instance
        high_confidence_instances = [i for i in refined_belief.instances if i.confidence >= 0.7]
        
        if high_confidence_instances:
            # Use the most recent high-confidence instance
            latest_instance = max(high_confidence_instances, key=lambda i: i.timestamp)
            refined_belief.refined_content = latest_instance.content
        else:
            # Use the most recent instance
            if refined_belief.instances:
                latest_instance = max(refined_belief.instances, key=lambda i: i.timestamp)
                refined_belief.refined_content = latest_instance.content
    
    def _update_belief_clusters(self, belief_id: str, belief_content: str):
        """Update belief clusters for similar beliefs"""
        # Find cluster for this belief
        content_hash = hashlib.md5(belief_content.encode()).hexdigest()[:4]
        cluster_id = f"cluster_{content_hash}"
        
        if cluster_id not in self.belief_clusters:
            self.belief_clusters[cluster_id] = []
        
        if belief_id not in self.belief_clusters[cluster_id]:
            self.belief_clusters[cluster_id].append(belief_id)
    
    def get_refined_beliefs(self, user_id: Optional[str] = None, min_strength: BeliefStrength = BeliefStrength.WEAK) -> List[RefinedBelief]:
        """Get refined beliefs, optionally filtered by user and strength"""
        beliefs = []
        
        for refined_belief in self.refined_beliefs.values():
            # Filter by user
            if user_id and user_id not in refined_belief.user_associations:
                continue
            
            # Filter by strength
            strength_values = {
                BeliefStrength.VERY_WEAK: 1,
                BeliefStrength.WEAK: 2,
                BeliefStrength.MODERATE: 3,
                BeliefStrength.STRONG: 4,
                BeliefStrength.VERY_STRONG: 5
            }
            
            if strength_values[refined_belief.strength] < strength_values[min_strength]:
                continue
            
            beliefs.append(refined_belief)
        
        # Sort by confidence
        beliefs.sort(key=lambda b: b.confidence, reverse=True)
        return beliefs
    
    def get_belief_by_id(self, belief_id: str) -> Optional[RefinedBelief]:
        """Get a specific refined belief by ID"""
        return self.refined_beliefs.get(belief_id)
    
    def get_belief_statistics(self) -> Dict[str, Any]:
        """Get statistics about belief refinement"""
        if not self.refined_beliefs:
            return {'total_beliefs': 0, 'total_instances': 0}
        
        # Count by strength
        strength_counts = defaultdict(int)
        for belief in self.refined_beliefs.values():
            strength_counts[belief.strength.value] += 1
        
        # Calculate averages
        confidences = [b.confidence for b in self.refined_beliefs.values()]
        reinforcements = [b.reinforcement_count for b in self.refined_beliefs.values()]
        
        return {
            'total_beliefs': len(self.refined_beliefs),
            'total_instances': len(self.belief_instances),
            'strength_distribution': dict(strength_counts),
            'average_confidence': statistics.mean(confidences),
            'average_reinforcements': statistics.mean(reinforcements),
            'most_reinforced': max(self.refined_beliefs.values(), key=lambda b: b.reinforcement_count).belief_id,
            'highest_confidence': max(self.refined_beliefs.values(), key=lambda b: b.confidence).belief_id,
            'total_clusters': len(self.belief_clusters)
        }
    
    def consolidate_beliefs(self, similarity_threshold: Optional[float] = None) -> int:
        """Consolidate similar beliefs"""
        if similarity_threshold is None:
            similarity_threshold = self.similarity_threshold
        
        consolidated_count = 0
        beliefs_to_merge = []
        
        # Find beliefs to merge
        belief_ids = list(self.refined_beliefs.keys())
        
        for i, belief_id1 in enumerate(belief_ids):
            for belief_id2 in belief_ids[i+1:]:
                if belief_id1 in self.refined_beliefs and belief_id2 in self.refined_beliefs:
                    belief1 = self.refined_beliefs[belief_id1]
                    belief2 = self.refined_beliefs[belief_id2]
                    
                    similarity = self._calculate_similarity(belief1.refined_content, belief2.refined_content)
                    
                    if similarity >= similarity_threshold:
                        beliefs_to_merge.append((belief_id1, belief_id2, similarity))
        
        # Merge beliefs
        for belief_id1, belief_id2, similarity in beliefs_to_merge:
            if belief_id1 in self.refined_beliefs and belief_id2 in self.refined_beliefs:
                self._merge_beliefs(belief_id1, belief_id2)
                consolidated_count += 1
        
        print(f"[BeliefMemoryRefiner] 🔄 Consolidated {consolidated_count} beliefs")
        return consolidated_count
    
    def _merge_beliefs(self, belief_id1: str, belief_id2: str):
        """Merge two beliefs"""
        belief1 = self.refined_beliefs[belief_id1]
        belief2 = self.refined_beliefs[belief_id2]
        
        # Merge instances
        belief1.instances.extend(belief2.instances)
        
        # Update counts
        belief1.reinforcement_count += belief2.reinforcement_count
        belief1.supporting_instances += belief2.supporting_instances
        belief1.conflicting_instances += belief2.conflicting_instances
        
        # Update associations
        for user_id in belief2.user_associations:
            if user_id not in belief1.user_associations:
                belief1.user_associations.append(user_id)
        
        # Update contextual variations
        for context in belief2.contextual_variations:
            if context not in belief1.contextual_variations:
                belief1.contextual_variations.append(context)
        
        # Update timestamps
        if belief2.first_occurrence < belief1.first_occurrence:
            belief1.first_occurrence = belief2.first_occurrence
        
        if belief2.last_reinforcement > belief1.last_reinforcement:
            belief1.last_reinforcement = belief2.last_reinforcement
        
        # Recalculate confidence and strength
        self._update_belief_confidence(belief_id1)
        self._update_belief_strength(belief_id1)
        
        # Remove the merged belief
        del self.refined_beliefs[belief_id2]
    
    def prune_weak_beliefs(self, min_reinforcements: int = 1, min_confidence: float = 0.2) -> int:
        """Remove weak beliefs that haven't been reinforced"""
        pruned_count = 0
        beliefs_to_remove = []
        
        for belief_id, belief in self.refined_beliefs.items():
            if (belief.reinforcement_count < min_reinforcements or 
                belief.confidence < min_confidence):
                beliefs_to_remove.append(belief_id)
        
        for belief_id in beliefs_to_remove:
            del self.refined_beliefs[belief_id]
            pruned_count += 1
        
        print(f"[BeliefMemoryRefiner] 🧹 Pruned {pruned_count} weak beliefs")
        return pruned_count
    
    def load_refiner_data(self):
        """Load refiner data from file"""
        try:
            with open(self.save_path, 'r') as f:
                data = json.load(f)
            
            # Load instances
            for instance_data in data.get('instances', []):
                # Handle both old and new enum formats
                source_value = instance_data['source']
                if isinstance(source_value, str) and '.' in source_value:
                    # Handle old format like 'BeliefSource.USER_STATEMENT'
                    source_value = source_value.split('.')[-1].lower()
                
                try:
                    source = BeliefSource(source_value)
                except ValueError:
                    # Fallback to USER_STATEMENT if invalid
                    source = BeliefSource.USER_STATEMENT
                
                instance = BeliefInstance(
                    instance_id=instance_data['instance_id'],
                    content=instance_data['content'],
                    source=source,
                    confidence=instance_data['confidence'],
                    timestamp=instance_data['timestamp'],
                    context=instance_data['context'],
                    user_id=instance_data['user_id'],
                    supporting_evidence=instance_data.get('supporting_evidence', [])
                )
                self.belief_instances.append(instance)
            
            # Load refined beliefs
            for belief_data in data.get('refined_beliefs', []):
                # Load instances for this belief
                instances = []
                for instance_data in belief_data.get('instances', []):
                    # Handle both old and new enum formats
                    source_value = instance_data['source']
                    if isinstance(source_value, str) and '.' in source_value:
                        # Handle old format like 'BeliefSource.USER_STATEMENT'
                        source_value = source_value.split('.')[-1].lower()
                    
                    try:
                        source = BeliefSource(source_value)
                    except ValueError:
                        # Fallback to USER_STATEMENT if invalid
                        source = BeliefSource.USER_STATEMENT
                    
                    instance = BeliefInstance(
                        instance_id=instance_data['instance_id'],
                        content=instance_data['content'],
                        source=source,
                        confidence=instance_data['confidence'],
                        timestamp=instance_data['timestamp'],
                        context=instance_data['context'],
                        user_id=instance_data['user_id'],
                        supporting_evidence=instance_data.get('supporting_evidence', [])
                    )
                    instances.append(instance)
                
                # Handle both old and new enum formats for strength
                strength_value = belief_data['strength']
                if isinstance(strength_value, str) and '.' in strength_value:
                    # Handle old format like 'BeliefStrength.WEAK'
                    strength_value = strength_value.split('.')[-1].lower()
                
                try:
                    strength = BeliefStrength(strength_value)
                except ValueError:
                    # Fallback to WEAK if invalid
                    strength = BeliefStrength.WEAK
                
                refined_belief = RefinedBelief(
                    belief_id=belief_data['belief_id'],
                    original_content=belief_data['original_content'],
                    refined_content=belief_data['refined_content'],
                    instances=instances,
                    strength=strength,
                    confidence=belief_data['confidence'],
                    first_occurrence=belief_data['first_occurrence'],
                    last_reinforcement=belief_data['last_reinforcement'],
                    reinforcement_count=belief_data['reinforcement_count'],
                    supporting_instances=belief_data['supporting_instances'],
                    conflicting_instances=belief_data['conflicting_instances'],
                    consistency_score=belief_data['consistency_score'],
                    evidence_quality=belief_data['evidence_quality'],
                    user_associations=belief_data['user_associations'],
                    contextual_variations=belief_data['contextual_variations']
                )
                self.refined_beliefs[refined_belief.belief_id] = refined_belief
            
            # Load clusters
            self.belief_clusters = data.get('belief_clusters', {})
            
            print(f"[BeliefMemoryRefiner] 📄 Loaded {len(self.belief_instances)} instances, {len(self.refined_beliefs)} refined beliefs")
            
        except FileNotFoundError:
            print(f"[BeliefMemoryRefiner] 📄 No refiner data found, starting fresh")
        except Exception as e:
            print(f"[BeliefMemoryRefiner] ❌ Error loading refiner data: {e}")
    
    def save_refiner_data(self):
        """Save refiner data to file"""
        try:
            data = {
                'instances': [asdict(instance) for instance in self.belief_instances],
                'refined_beliefs': [asdict(belief) for belief in self.refined_beliefs.values()],
                'belief_clusters': self.belief_clusters,
                'last_updated': datetime.now().isoformat(),
                'total_instances': len(self.belief_instances),
                'total_refined_beliefs': len(self.refined_beliefs)
            }
            
            # Convert enum values to their string values for JSON serialization
            def convert_enums(obj):
                if hasattr(obj, '__dict__'):
                    # Handle dataclass objects
                    result = {}
                    for k, v in obj.__dict__.items():
                        if hasattr(v, 'value'):
                            result[k] = v.value
                        elif isinstance(v, datetime):
                            result[k] = v.isoformat()
                        elif isinstance(v, (list, dict)):
                            result[k] = v  # Let JSON handle these
                        else:
                            result[k] = v
                    return result
                elif isinstance(obj, dict):
                    return {k: (v.value if hasattr(v, 'value') else v) for k, v in obj.items()}
                elif hasattr(obj, 'value'):
                    return obj.value
                elif isinstance(obj, datetime):
                    return obj.isoformat()
                else:
                    return str(obj)
            
            with open(self.save_path, 'w') as f:
                json.dump(data, f, indent=2, default=convert_enums)
                
        except Exception as e:
            print(f"[BeliefMemoryRefiner] ❌ Error saving refiner data: {e}")

# Global instance
belief_memory_refiner = BeliefMemoryRefiner()

def refine_belief_from_repetition(belief_content: str, user_id: str, context: str, source: BeliefSource = BeliefSource.USER_STATEMENT) -> str:
    """Refine belief confidence from repetition - main API function"""
    return belief_memory_refiner.process_belief(belief_content, user_id, context, source)

def get_refined_beliefs(user_id: Optional[str] = None, min_strength: BeliefStrength = BeliefStrength.WEAK) -> List[Dict[str, Any]]:
    """Get refined beliefs"""
    beliefs = belief_memory_refiner.get_refined_beliefs(user_id, min_strength)
    return [asdict(belief) for belief in beliefs]

def get_belief_refinement_stats() -> Dict[str, Any]:
    """Get belief refinement statistics"""
    return belief_memory_refiner.get_belief_statistics()

def consolidate_similar_beliefs(similarity_threshold: Optional[float] = None) -> int:
    """Consolidate similar beliefs"""
    return belief_memory_refiner.consolidate_beliefs(similarity_threshold)

def prune_weak_beliefs(min_reinforcements: int = 1, min_confidence: float = 0.2) -> int:
    """Remove weak beliefs"""
    return belief_memory_refiner.prune_weak_beliefs(min_reinforcements, min_confidence)

def get_refined_belief_by_id(belief_id: str) -> Optional[Dict[str, Any]]:
    """Get specific refined belief"""
    belief = belief_memory_refiner.get_belief_by_id(belief_id)
    return asdict(belief) if belief else None