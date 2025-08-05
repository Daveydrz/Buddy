"""
Belief Analyzer - Analyze and manage belief contradictions and consistency
Created: 2025-01-17
Purpose: Track beliefs, detect contradictions, and maintain belief consistency across conversations
"""

import json
import time
import os
from typing import Dict, List, Any, Optional, Set, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import re

class BeliefType(Enum):
    FACTUAL = "factual"
    PERSONAL = "personal"
    PREFERENCE = "preference"
    OPINION = "opinion"
    TEMPORAL = "temporal"
    RELATIONAL = "relational"

class BeliefCertainty(Enum):
    CERTAIN = "certain"
    CONFIDENT = "confident"
    MODERATE = "moderate"
    UNCERTAIN = "uncertain"
    SPECULATIVE = "speculative"

class ContradictionType(Enum):
    DIRECT = "direct"
    LOGICAL = "logical"
    TEMPORAL = "temporal"
    CONTEXTUAL = "contextual"

@dataclass
class Belief:
    """Represents a single belief with metadata"""
    id: str
    content: str
    belief_type: BeliefType
    certainty: BeliefCertainty
    source: str
    timestamp: str
    user: str
    context: Dict[str, Any]
    supporting_evidence: List[str]
    contradictions: List[str]
    confidence_score: float
    last_confirmed: str
    tags: List[str]
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()
        if not self.last_confirmed:
            self.last_confirmed = self.timestamp

@dataclass
class Contradiction:
    """Represents a contradiction between beliefs"""
    id: str
    belief_a_id: str
    belief_b_id: str
    contradiction_type: ContradictionType
    severity: float
    explanation: str
    detected_at: str
    resolved: bool
    resolution_strategy: str
    
    def __post_init__(self):
        if not self.detected_at:
            self.detected_at = datetime.now().isoformat()

class BeliefAnalyzer:
    """Analyze and manage beliefs, detect contradictions"""
    
    def __init__(self, belief_store_file: str = "belief_store.json"):
        self.belief_store_file = belief_store_file
        self.beliefs: Dict[str, Belief] = {}
        self.contradictions: Dict[str, Contradiction] = {}
        
        # Patterns for extracting beliefs from text
        self.belief_patterns = {
            BeliefType.FACTUAL: [
                r"(.+) is (.+)",
                r"(.+) are (.+)",
                r"(.+) has (.+)",
                r"(.+) was (.+)",
                r"(.+) will be (.+)",
                r"the fact that (.+)",
                r"it's true that (.+)",
            ],
            BeliefType.PERSONAL: [
                r"I am (.+)",
                r"I have (.+)",
                r"I live (.+)",
                r"I work (.+)",
                r"my (.+) is (.+)",
                r"I was (.+)",
                r"I will (.+)",
            ],
            BeliefType.PREFERENCE: [
                r"I like (.+)",
                r"I prefer (.+)",
                r"I enjoy (.+)",
                r"I love (.+)",
                r"I hate (.+)",
                r"I don't like (.+)",
                r"my favorite (.+) is (.+)",
            ],
            BeliefType.OPINION: [
                r"I think (.+)",
                r"I believe (.+)",
                r"I feel that (.+)",
                r"in my opinion (.+)",
                r"I consider (.+)",
                r"it seems to me (.+)",
            ]
        }
        
        # Keywords that indicate certainty levels
        self.certainty_indicators = {
            BeliefCertainty.CERTAIN: ["definitely", "certainly", "absolutely", "without doubt", "completely sure"],
            BeliefCertainty.CONFIDENT: ["pretty sure", "confident", "quite certain", "very likely"],
            BeliefCertainty.MODERATE: ["think", "believe", "probably", "likely"],
            BeliefCertainty.UNCERTAIN: ["maybe", "perhaps", "might", "could be", "not sure"],
            BeliefCertainty.SPECULATIVE: ["wonder if", "possibly", "speculation", "guess"]
        }
        
        self.load_beliefs()
        
        print(f"[BeliefAnalyzer] 🧠 Initialized with {len(self.beliefs)} beliefs")
        
    def load_beliefs(self):
        """Load beliefs from storage"""
        try:
            if os.path.exists(self.belief_store_file):
                with open(self.belief_store_file, 'r') as f:
                    data = json.load(f)
                    
                # Load beliefs
                for belief_data in data.get('beliefs', []):
                    if isinstance(belief_data, dict):
                        # Handle enum conversion - support both old format and new format
                        belief_type_str = belief_data.get('belief_type', 'factual')
                        if belief_type_str.startswith('BeliefType.'):
                            belief_type_str = belief_type_str.split('.')[1].lower()
                        
                        certainty_str = belief_data.get('certainty', 'moderate')
                        if certainty_str.startswith('BeliefCertainty.'):
                            certainty_str = certainty_str.split('.')[1].lower()
                        
                        belief = Belief(
                            id=belief_data.get('id', ''),
                            content=belief_data.get('content', ''),
                            belief_type=BeliefType(belief_type_str),
                            certainty=BeliefCertainty(certainty_str),
                            source=belief_data.get('source', ''),
                            timestamp=belief_data.get('timestamp', ''),
                            user=belief_data.get('user', ''),
                            context=belief_data.get('context', {}),
                            supporting_evidence=belief_data.get('supporting_evidence', []),
                            contradictions=belief_data.get('contradictions', []),
                            confidence_score=belief_data.get('confidence_score', 0.5),
                            last_confirmed=belief_data.get('last_confirmed', ''),
                            tags=belief_data.get('tags', [])
                        )
                        self.beliefs[belief.id] = belief
                        
                # Load contradictions
                for contradiction_data in data.get('contradictions', []):
                    if isinstance(contradiction_data, dict):
                        # Handle enum conversion - support both old format and new format
                        contradiction_type_str = contradiction_data.get('contradiction_type', 'direct')
                        if contradiction_type_str.startswith('ContradictionType.'):
                            contradiction_type_str = contradiction_type_str.split('.')[1].lower()
                        
                        contradiction = Contradiction(
                            id=contradiction_data.get('id', ''),
                            belief_a_id=contradiction_data.get('belief_a_id', ''),
                            belief_b_id=contradiction_data.get('belief_b_id', ''),
                            contradiction_type=ContradictionType(contradiction_type_str),
                            severity=contradiction_data.get('severity', 0.5),
                            explanation=contradiction_data.get('explanation', ''),
                            detected_at=contradiction_data.get('detected_at', ''),
                            resolved=contradiction_data.get('resolved', False),
                            resolution_strategy=contradiction_data.get('resolution_strategy', '')
                        )
                        self.contradictions[contradiction.id] = contradiction
                        
                print(f"[BeliefAnalyzer] ✅ Loaded {len(self.beliefs)} beliefs, {len(self.contradictions)} contradictions")
            else:
                print(f"[BeliefAnalyzer] 📄 No existing belief store found")
                
        except Exception as e:
            print(f"[BeliefAnalyzer] ❌ Error loading beliefs: {e}")
            
    def save_beliefs(self):
        """Save beliefs to storage"""
        try:
            # Convert beliefs to JSON-serializable format
            beliefs_data = []
            for belief in self.beliefs.values():
                belief_dict = asdict(belief)
                # Convert enums to their values
                belief_dict['belief_type'] = belief.belief_type.value
                belief_dict['certainty'] = belief.certainty.value
                beliefs_data.append(belief_dict)
            
            # Convert contradictions to JSON-serializable format
            contradictions_data = []
            for contradiction in self.contradictions.values():
                contradiction_dict = asdict(contradiction)
                # Convert enums to their values
                contradiction_dict['contradiction_type'] = contradiction.contradiction_type.value
                contradictions_data.append(contradiction_dict)
            
            data = {
                'beliefs': beliefs_data,
                'contradictions': contradictions_data,
                'last_updated': datetime.now().isoformat(),
                'metadata': {
                    'total_beliefs': len(self.beliefs),
                    'total_contradictions': len(self.contradictions),
                    'unresolved_contradictions': len([c for c in self.contradictions.values() if not c.resolved])
                }
            }
            
            with open(self.belief_store_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            print(f"[BeliefAnalyzer] ❌ Error saving beliefs: {e}")
            
    def extract_beliefs_from_text(self, text: str, user: str, context: Dict[str, Any] = None) -> List[Belief]:
        """Extract beliefs from natural language text"""
        extracted_beliefs = []
        
        try:
            text_lower = text.lower()
            
            for belief_type, patterns in self.belief_patterns.items():
                for pattern in patterns:
                    matches = re.findall(pattern, text_lower, re.IGNORECASE)
                    
                    for match in matches:
                        if isinstance(match, tuple):
                            content = " ".join(match)
                        else:
                            content = match
                            
                        if len(content.strip()) > 3:  # Filter out very short matches
                            # Determine certainty from text
                            certainty = self._determine_certainty(text_lower)
                            
                            # Generate unique ID
                            belief_id = f"belief_{int(time.time() * 1000)}_{len(extracted_beliefs)}"
                            
                            belief = Belief(
                                id=belief_id,
                                content=content.strip(),
                                belief_type=belief_type,
                                certainty=certainty,
                                source="text_extraction",
                                timestamp=datetime.now().isoformat(),
                                user=user,
                                context=context or {},
                                supporting_evidence=[text],
                                contradictions=[],
                                confidence_score=self._calculate_confidence_score(content, certainty),
                                last_confirmed=datetime.now().isoformat(),
                                tags=self._generate_tags(content, belief_type)
                            )
                            
                            extracted_beliefs.append(belief)
                            
        except Exception as e:
            print(f"[BeliefAnalyzer] ❌ Error extracting beliefs: {e}")
            
        return extracted_beliefs
        
    def _determine_certainty(self, text: str) -> BeliefCertainty:
        """Determine certainty level from text indicators"""
        text_lower = text.lower()
        
        for certainty, indicators in self.certainty_indicators.items():
            for indicator in indicators:
                if indicator in text_lower:
                    return certainty
                    
        return BeliefCertainty.MODERATE  # Default
        
    def _calculate_confidence_score(self, content: str, certainty: BeliefCertainty) -> float:
        """Calculate confidence score for a belief"""
        base_score = {
            BeliefCertainty.CERTAIN: 0.95,
            BeliefCertainty.CONFIDENT: 0.8,
            BeliefCertainty.MODERATE: 0.6,
            BeliefCertainty.UNCERTAIN: 0.4,
            BeliefCertainty.SPECULATIVE: 0.2
        }[certainty]
        
        # Adjust based on content specificity
        if len(content.split()) > 3:
            base_score += 0.1  # More specific beliefs are more confident
            
        return min(1.0, base_score)
        
    def _generate_tags(self, content: str, belief_type: BeliefType) -> List[str]:
        """Generate tags for a belief"""
        tags = [belief_type.value]
        
        # Add content-based tags
        words = content.lower().split()
        
        # Common tag categories
        tag_categories = {
            'location': ['live', 'located', 'from', 'city', 'country', 'place'],
            'work': ['work', 'job', 'career', 'company', 'profession'],
            'family': ['family', 'mother', 'father', 'sister', 'brother', 'parent'],
            'hobby': ['hobby', 'enjoy', 'play', 'sport', 'activity'],
            'food': ['food', 'eat', 'cook', 'restaurant', 'meal'],
            'technology': ['computer', 'software', 'internet', 'phone', 'app']
        }
        
        for category, keywords in tag_categories.items():
            if any(keyword in words for keyword in keywords):
                tags.append(category)
                
        return tags
        
    def add_belief(self, belief: Belief) -> bool:
        """Add a new belief and check for contradictions"""
        try:
            # Check for existing similar beliefs
            similar_beliefs = self._find_similar_beliefs(belief)
            
            if similar_beliefs:
                print(f"[BeliefAnalyzer] 🔍 Found {len(similar_beliefs)} similar beliefs")
                
                # Check for contradictions with similar beliefs
                for similar_belief in similar_beliefs:
                    contradiction = self._detect_contradiction(belief, similar_belief)
                    if contradiction:
                        self.contradictions[contradiction.id] = contradiction
                        belief.contradictions.append(contradiction.id)
                        similar_belief.contradictions.append(contradiction.id)
                        print(f"[BeliefAnalyzer] ⚠️ Detected contradiction: {contradiction.explanation}")
            
            # Add the belief
            self.beliefs[belief.id] = belief
            
            # Save to storage
            self.save_beliefs()
            
            print(f"[BeliefAnalyzer] ✅ Added belief: {belief.content[:50]}...")
            return True
            
        except Exception as e:
            print(f"[BeliefAnalyzer] ❌ Error adding belief: {e}")
            return False
            
    def _find_similar_beliefs(self, belief: Belief) -> List[Belief]:
        """Find beliefs similar to the given belief"""
        similar_beliefs = []
        
        try:
            belief_words = set(belief.content.lower().split())
            
            for existing_belief in self.beliefs.values():
                # Skip if same user and same type
                if (existing_belief.user == belief.user and 
                    existing_belief.belief_type == belief.belief_type):
                    
                    existing_words = set(existing_belief.content.lower().split())
                    
                    # Calculate similarity (Jaccard index)
                    intersection = belief_words.intersection(existing_words)
                    union = belief_words.union(existing_words)
                    
                    if union:
                        similarity = len(intersection) / len(union)
                        
                        if similarity > 0.3:  # 30% similarity threshold
                            similar_beliefs.append(existing_belief)
                            
        except Exception as e:
            print(f"[BeliefAnalyzer] ❌ Error finding similar beliefs: {e}")
            
        return similar_beliefs
        
    def _detect_contradiction(self, belief_a: Belief, belief_b: Belief) -> Optional[Contradiction]:
        """Detect if two beliefs contradict each other"""
        try:
            # Direct contradictions (negation patterns)
            content_a = belief_a.content.lower()
            content_b = belief_b.content.lower()
            
            # Simple negation detection
            negation_patterns = [
                ("not", ""),
                ("don't", ""),
                ("doesn't", ""),
                ("isn't", "is"),
                ("aren't", "are"),
                ("wasn't", "was"),
                ("won't", "will")
            ]
            
            for neg, pos in negation_patterns:
                if neg in content_a and pos in content_b:
                    # Found potential direct contradiction
                    contradiction_id = f"contradiction_{int(time.time() * 1000)}"
                    
                    return Contradiction(
                        id=contradiction_id,
                        belief_a_id=belief_a.id,
                        belief_b_id=belief_b.id,
                        contradiction_type=ContradictionType.DIRECT,
                        severity=0.8,
                        explanation=f"Direct contradiction: '{belief_a.content}' vs '{belief_b.content}'",
                        detected_at=datetime.now().isoformat(),
                        resolved=False,
                        resolution_strategy=""
                    )
                    
            # Temporal contradictions
            if belief_a.belief_type == BeliefType.TEMPORAL or belief_b.belief_type == BeliefType.TEMPORAL:
                temporal_contradiction = self._check_temporal_contradiction(belief_a, belief_b)
                if temporal_contradiction:
                    return temporal_contradiction
                    
        except Exception as e:
            print(f"[BeliefAnalyzer] ❌ Error detecting contradiction: {e}")
            
        return None
        
    def _check_temporal_contradiction(self, belief_a: Belief, belief_b: Belief) -> Optional[Contradiction]:
        """Check for temporal contradictions"""
        try:
            # Simple temporal contradiction detection
            content_a = belief_a.content.lower()
            content_b = belief_b.content.lower()
            
            # Look for conflicting time references
            time_conflicts = [
                ("past", "future"),
                ("was", "will be"),
                ("used to", "now"),
                ("before", "after")
            ]
            
            for past_indicator, future_indicator in time_conflicts:
                if past_indicator in content_a and future_indicator in content_b:
                    contradiction_id = f"temporal_contradiction_{int(time.time() * 1000)}"
                    
                    return Contradiction(
                        id=contradiction_id,
                        belief_a_id=belief_a.id,
                        belief_b_id=belief_b.id,
                        contradiction_type=ContradictionType.TEMPORAL,
                        severity=0.6,
                        explanation=f"Temporal contradiction: '{belief_a.content}' vs '{belief_b.content}'",
                        detected_at=datetime.now().isoformat(),
                        resolved=False,
                        resolution_strategy=""
                    )
                    
        except Exception as e:
            print(f"[BeliefAnalyzer] ❌ Error checking temporal contradiction: {e}")
            
        return None
        
    def get_active_contradictions(self) -> List[Contradiction]:
        """Get all unresolved contradictions"""
        return [c for c in self.contradictions.values() if not c.resolved]
        
    def get_beliefs_for_user(self, user: str) -> List[Belief]:
        """Get all beliefs for a specific user"""
        return [b for b in self.beliefs.values() if b.user == user]
        
    def get_beliefs_by_type(self, belief_type: BeliefType) -> List[Belief]:
        """Get all beliefs of a specific type"""
        return [b for b in self.beliefs.values() if b.belief_type == belief_type]
        
    def resolve_contradiction(self, contradiction_id: str, strategy: str, keep_belief_id: str = None):
        """Resolve a contradiction with a specific strategy"""
        try:
            if contradiction_id in self.contradictions:
                contradiction = self.contradictions[contradiction_id]
                contradiction.resolved = True
                contradiction.resolution_strategy = strategy
                
                if keep_belief_id:
                    # Remove the other belief
                    other_belief_id = (contradiction.belief_b_id 
                                     if keep_belief_id == contradiction.belief_a_id 
                                     else contradiction.belief_a_id)
                    
                    if other_belief_id in self.beliefs:
                        del self.beliefs[other_belief_id]
                        
                self.save_beliefs()
                print(f"[BeliefAnalyzer] ✅ Resolved contradiction {contradiction_id} with strategy: {strategy}")
                
        except Exception as e:
            print(f"[BeliefAnalyzer] ❌ Error resolving contradiction: {e}")
            
    def analyze_text_for_beliefs(self, text: str, user: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analyze text and extract/add beliefs, return analysis"""
        analysis = {
            "extracted_beliefs": [],
            "new_contradictions": [],
            "confirmed_beliefs": [],
            "belief_updates": []
        }
        
        try:
            # Extract beliefs from text
            extracted_beliefs = self.extract_beliefs_from_text(text, user, context)
            
            for belief in extracted_beliefs:
                # Add belief and check for contradictions
                success = self.add_belief(belief)
                if success:
                    analysis["extracted_beliefs"].append(belief.content)
                    
                    # Check if any new contradictions were created
                    if belief.contradictions:
                        for contradiction_id in belief.contradictions:
                            if contradiction_id in self.contradictions:
                                contradiction = self.contradictions[contradiction_id]
                                analysis["new_contradictions"].append(contradiction.explanation)
                                
        except Exception as e:
            print(f"[BeliefAnalyzer] ❌ Error analyzing text: {e}")
            analysis["error"] = str(e)
            
        return analysis
        
    def get_belief_summary_for_user(self, user: str) -> Dict[str, Any]:
        """Get a summary of beliefs for a user"""
        user_beliefs = self.get_beliefs_for_user(user)
        
        if not user_beliefs:
            return {"message": "No beliefs recorded for this user"}
            
        # Group by type
        beliefs_by_type = {}
        for belief in user_beliefs:
            belief_type = belief.belief_type.value
            if belief_type not in beliefs_by_type:
                beliefs_by_type[belief_type] = []
            beliefs_by_type[belief_type].append(belief.content)
            
        # Get contradictions
        user_contradictions = []
        for contradiction in self.get_active_contradictions():
            belief_a = self.beliefs.get(contradiction.belief_a_id)
            belief_b = self.beliefs.get(contradiction.belief_b_id)
            
            if belief_a and belief_b and (belief_a.user == user or belief_b.user == user):
                user_contradictions.append(contradiction.explanation)
                
        return {
            "total_beliefs": len(user_beliefs),
            "beliefs_by_type": beliefs_by_type,
            "active_contradictions": user_contradictions,
            "last_updated": max((b.last_confirmed for b in user_beliefs), default="N/A")
        }

# Global belief analyzer instance
belief_analyzer = BeliefAnalyzer()

def analyze_user_text_for_beliefs(text: str, user: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Analyze user text for beliefs and contradictions"""
    return belief_analyzer.analyze_text_for_beliefs(text, user, context)

def get_user_belief_summary(user: str) -> Dict[str, Any]:
    """Get belief summary for a user"""
    return belief_analyzer.get_belief_summary_for_user(user)

def get_active_belief_contradictions(user_id: str = None) -> List[Dict[str, Any]]:
    """Get all active contradictions"""
    contradictions = belief_analyzer.get_active_contradictions()
    return [
        {
            "id": c.id,
            "type": c.contradiction_type.value,
            "severity": c.severity,
            "explanation": c.explanation,
            "detected_at": c.detected_at
        }
        for c in contradictions
    ]

def resolve_belief_contradiction(contradiction_id: str, strategy: str, keep_belief_id: str = None):
    """Resolve a belief contradiction"""
    belief_analyzer.resolve_contradiction(contradiction_id, strategy, keep_belief_id)

if __name__ == "__main__":
    # Test the belief analyzer
    print("Testing Belief Analyzer")
    
    # Test belief extraction
    test_text = "I am a software developer. I live in Brisbane. I like Python programming."
    analysis = analyze_user_text_for_beliefs(test_text, "test_user")
    print(f"Extracted beliefs: {analysis['extracted_beliefs']}")
    
    # Test contradiction
    contradictory_text = "I don't like Python programming."
    analysis2 = analyze_user_text_for_beliefs(contradictory_text, "test_user")
    print(f"New contradictions: {analysis2['new_contradictions']}")
    
    # Get summary
    summary = get_user_belief_summary("test_user")
    print(f"User belief summary: {summary}")