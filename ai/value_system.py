"""
Value System - Moral compass driving goals and priorities
Provides ethical decision-making framework and value-based reasoning
"""

import json
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum

class ValuePriority(Enum):
    """Priority levels for values"""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4
    CONTEXTUAL = 5

@dataclass
class ValueDecision:
    """Records a value-based decision"""
    decision_id: str
    context: str
    values_applied: List[str]
    primary_value: str
    reasoning: str
    outcome: Optional[str]
    satisfaction_score: float
    timestamp: str
    learned_insights: List[str]

@dataclass
class ValueConflict:
    """Represents a conflict between values"""
    conflict_id: str
    conflicting_values: List[str]
    context: str
    resolution_approach: str
    chosen_value: str
    reasoning: str
    confidence: float
    timestamp: str

class ValueSystem:
    """Core value system for ethical decision-making"""
    
    def __init__(self, values_file: str = "ai/core_values.json"):
        self.values_file = values_file
        self.core_values: Dict[str, Dict[str, Any]] = {}
        self.value_relationships: Dict[str, Any] = {}
        self.decision_frameworks: Dict[str, Dict[str, Any]] = {}
        self.contextual_applications: Dict[str, Dict[str, Any]] = {}
        self.value_decisions: List[ValueDecision] = []
        self.value_conflicts: List[ValueConflict] = []
        self.active_values: Dict[str, float] = {}  # value -> activation_strength
        self.load_values()
    
    def load_values(self):
        """Load core values from configuration"""
        try:
            with open(self.values_file, 'r') as f:
                data = json.load(f)
                
            self.core_values = data.get('core_values', {})
            self.value_relationships = data.get('value_relationships', {})
            self.decision_frameworks = data.get('decision_frameworks', {})
            self.contextual_applications = data.get('contextual_applications', {})
            
            # Initialize active values with their base weights
            for value_name, value_data in self.core_values.items():
                self.active_values[value_name] = value_data.get('weight', 0.5)
            
            print(f"[ValueSystem] 📚 Loaded {len(self.core_values)} core values")
            
        except FileNotFoundError:
            print(f"[ValueSystem] ❌ Values file not found: {self.values_file}")
            self._initialize_default_values()
        except Exception as e:
            print(f"[ValueSystem] ❌ Error loading values: {e}")
            self._initialize_default_values()
    
    def _initialize_default_values(self):
        """Initialize minimal default values"""
        self.core_values = {
            'helpfulness': {'weight': 0.9, 'priority': 1, 'description': 'Being helpful to users'},
            'honesty': {'weight': 0.9, 'priority': 1, 'description': 'Being truthful and transparent'},
            'safety': {'weight': 0.95, 'priority': 1, 'description': 'Ensuring user safety and wellbeing'},
            'respect': {'weight': 0.85, 'priority': 2, 'description': 'Treating all users with respect'}
        }
        
        for value_name, value_data in self.core_values.items():
            self.active_values[value_name] = value_data.get('weight', 0.5)
    
    def evaluate_decision(self, 
                         context: str, 
                         options: List[str],
                         user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Evaluate decision options against core values"""
        try:
            # Identify relevant values for this context
            relevant_values = self._identify_relevant_values(context, user_context)
            
            # Score each option against relevant values
            option_scores = {}
            for option in options:
                option_scores[option] = self._score_option_against_values(
                    option, relevant_values, context
                )
            
            # Find best option
            best_option = max(option_scores.items(), key=lambda x: x[1]['total_score'])
            
            # Check for value conflicts
            conflicts = self._detect_value_conflicts(best_option[0], relevant_values, context)
            
            # Generate reasoning
            reasoning = self._generate_value_reasoning(
                best_option[0], best_option[1], relevant_values, conflicts
            )
            
            decision_result = {
                'recommended_option': best_option[0],
                'confidence': best_option[1]['total_score'],
                'relevant_values': list(relevant_values.keys()),
                'primary_value': best_option[1]['primary_value'],
                'reasoning': reasoning,
                'value_conflicts': conflicts,
                'all_scores': option_scores
            }
            
            # Record decision
            self._record_decision(decision_result, context)
            
            return decision_result
            
        except Exception as e:
            print(f"[ValueSystem] ❌ Error evaluating decision: {e}")
            return {
                'recommended_option': options[0] if options else None,
                'confidence': 0.5,
                'reasoning': 'Error in value evaluation',
                'value_conflicts': []
            }
    
    def _identify_relevant_values(self, context: str, user_context: Optional[Dict[str, Any]] = None) -> Dict[str, float]:
        """Identify values relevant to the current context"""
        relevant_values = {}
        context_lower = context.lower()
        
        # Check contextual applications
        for app_name, app_data in self.contextual_applications.items():
            if any(keyword in context_lower for keyword in app_name.split('_')):
                primary_values = app_data.get('primary_values', [])
                for value in primary_values:
                    if value in self.core_values:
                        weight = self.core_values[value].get('weight', 0.5)
                        relevant_values[value] = weight * 1.2  # Boost contextually relevant values
        
        # Always include high-priority values
        for value_name, value_data in self.core_values.items():
            if value_data.get('priority', 5) <= 2:  # High priority values
                current_weight = relevant_values.get(value_name, 0)
                base_weight = value_data.get('weight', 0.5)
                relevant_values[value_name] = max(current_weight, base_weight)
        
        # Context-specific value activation
        if 'help' in context_lower or 'assist' in context_lower:
            relevant_values['helpfulness'] = self.active_values.get('helpfulness', 0.9)
        
        if 'question' in context_lower or 'information' in context_lower:
            relevant_values['honesty'] = self.active_values.get('honesty', 0.9)
        
        if 'emotional' in context_lower or 'feeling' in context_lower:
            relevant_values['empathy'] = self.active_values.get('empathy', 0.85)
        
        if 'learn' in context_lower or 'understand' in context_lower:
            relevant_values['learning'] = self.active_values.get('learning', 0.8)
        
        return relevant_values
    
    def _score_option_against_values(self, option: str, relevant_values: Dict[str, float], context: str) -> Dict[str, Any]:
        """Score an option against relevant values"""
        value_scores = {}
        total_score = 0
        
        for value_name, value_weight in relevant_values.items():
            score = self._calculate_value_alignment(option, value_name, context)
            weighted_score = score * value_weight
            value_scores[value_name] = {
                'raw_score': score,
                'weighted_score': weighted_score,
                'weight': value_weight
            }
            total_score += weighted_score
        
        # Find primary value (highest weighted score)
        primary_value = max(value_scores.items(), key=lambda x: x[1]['weighted_score'])[0] if value_scores else None
        
        return {
            'total_score': total_score,
            'primary_value': primary_value,
            'value_scores': value_scores,
            'normalized_score': total_score / len(relevant_values) if relevant_values else 0
        }
    
    def _calculate_value_alignment(self, option: str, value_name: str, context: str) -> float:
        """Calculate how well an option aligns with a specific value"""
        option_lower = option.lower()
        value_data = self.core_values.get(value_name, {})
        manifestations = value_data.get('manifestations', [])
        
        alignment_score = 0.5  # Base score
        
        # Check manifestations
        for manifestation in manifestations:
            manifestation_lower = manifestation.lower()
            if any(word in option_lower for word in manifestation_lower.split()):
                alignment_score += 0.1
        
        # Value-specific alignment checks
        if value_name == 'helpfulness':
            if any(word in option_lower for word in ['help', 'assist', 'support', 'provide', 'offer']):
                alignment_score += 0.3
        
        elif value_name == 'honesty':
            if any(word in option_lower for word in ['accurate', 'truthful', 'admit', 'acknowledge']):
                alignment_score += 0.3
            if any(word in option_lower for word in ['lie', 'deceive', 'mislead']):
                alignment_score -= 0.5
        
        elif value_name == 'empathy':
            if any(word in option_lower for word in ['understand', 'feel', 'care', 'support']):
                alignment_score += 0.3
        
        elif value_name == 'safety':
            if any(word in option_lower for word in ['safe', 'secure', 'protect', 'warn']):
                alignment_score += 0.3
            if any(word in option_lower for word in ['risk', 'danger', 'harm']):
                alignment_score -= 0.3
        
        elif value_name == 'respect':
            if any(word in option_lower for word in ['respectful', 'dignified', 'appropriate']):
                alignment_score += 0.3
            if any(word in option_lower for word in ['disrespect', 'rude', 'inappropriate']):
                alignment_score -= 0.5
        
        return max(0.0, min(1.0, alignment_score))
    
    def _detect_value_conflicts(self, chosen_option: str, relevant_values: Dict[str, float], context: str) -> List[ValueConflict]:
        """Detect potential conflicts between values"""
        conflicts = []
        
        # Check predefined potential tensions
        potential_tensions = self.value_relationships.get('potential_tensions', [])
        
        for tension_pair in potential_tensions:
            if len(tension_pair) == 2:
                value1, value2 = tension_pair
                if value1 in relevant_values and value2 in relevant_values:
                    # Check if these values might conflict in this context
                    score1 = self._calculate_value_alignment(chosen_option, value1, context)
                    score2 = self._calculate_value_alignment(chosen_option, value2, context)
                    
                    # If one value is highly satisfied and the other is poorly satisfied
                    if abs(score1 - score2) > 0.4:
                        conflict = ValueConflict(
                            conflict_id=f"conflict_{len(self.value_conflicts)}",
                            conflicting_values=[value1, value2],
                            context=context,
                            resolution_approach="prioritization",
                            chosen_value=value1 if score1 > score2 else value2,
                            reasoning=f"Prioritized {value1 if score1 > score2 else value2} over {value2 if score1 > score2 else value1}",
                            confidence=abs(score1 - score2),
                            timestamp=datetime.now().isoformat()
                        )
                        conflicts.append(conflict)
        
        return conflicts
    
    def _generate_value_reasoning(self, chosen_option: str, option_score: Dict[str, Any], relevant_values: Dict[str, float], conflicts: List[ValueConflict]) -> str:
        """Generate human-readable reasoning for value-based decision"""
        primary_value = option_score.get('primary_value', 'helpfulness')
        confidence = option_score.get('normalized_score', 0.5)
        
        reasoning = f"I chose '{chosen_option}' primarily because it aligns with my core value of {primary_value}"
        
        # Add confidence level
        if confidence > 0.8:
            reasoning += " with high confidence"
        elif confidence > 0.6:
            reasoning += " with moderate confidence"
        else:
            reasoning += " though with some uncertainty"
        
        # Add value details
        value_scores = option_score.get('value_scores', {})
        strong_values = [v for v, s in value_scores.items() if s['weighted_score'] > 0.7]
        
        if strong_values:
            reasoning += f". This option strongly supports: {', '.join(strong_values)}"
        
        # Add conflict information
        if conflicts:
            reasoning += f". There were {len(conflicts)} value conflicts that needed resolution"
        
        reasoning += "."
        
        return reasoning
    
    def _record_decision(self, decision_result: Dict[str, Any], context: str):
        """Record a value-based decision for learning"""
        decision = ValueDecision(
            decision_id=f"decision_{len(self.value_decisions)}",
            context=context,
            values_applied=decision_result.get('relevant_values', []),
            primary_value=decision_result.get('primary_value', ''),
            reasoning=decision_result.get('reasoning', ''),
            outcome=None,  # To be filled later
            satisfaction_score=decision_result.get('confidence', 0.5),
            timestamp=datetime.now().isoformat(),
            learned_insights=[]
        )
        
        self.value_decisions.append(decision)
        
        # Add conflicts to conflicts list
        conflicts = decision_result.get('value_conflicts', [])
        self.value_conflicts.extend(conflicts)
    
    def get_value_priorities(self, context: Optional[str] = None) -> List[Tuple[str, float]]:
        """Get current value priorities, optionally for a specific context"""
        if context:
            relevant_values = self._identify_relevant_values(context)
            return sorted(relevant_values.items(), key=lambda x: x[1], reverse=True)
        else:
            return sorted(self.active_values.items(), key=lambda x: x[1], reverse=True)
    
    def get_value_description(self, value_name: str) -> Optional[str]:
        """Get description of a specific value"""
        return self.core_values.get(value_name, {}).get('description')
    
    def get_value_manifestations(self, value_name: str) -> List[str]:
        """Get how a value manifests in behavior"""
        return self.core_values.get(value_name, {}).get('manifestations', [])
    
    def adjust_value_weight(self, value_name: str, adjustment: float, reason: str):
        """Adjust the weight of a value based on experience"""
        if value_name in self.active_values:
            old_weight = self.active_values[value_name]
            new_weight = max(0.1, min(1.0, old_weight + adjustment))
            self.active_values[value_name] = new_weight
            
            print(f"[ValueSystem] ⚖️ Adjusted {value_name}: {old_weight:.2f} → {new_weight:.2f} ({reason})")
    
    def get_value_conflicts_summary(self) -> Dict[str, Any]:
        """Get summary of value conflicts encountered"""
        if not self.value_conflicts:
            return {'total_conflicts': 0, 'common_conflicts': [], 'resolution_strategies': []}
        
        # Count conflict types
        conflict_pairs = {}
        for conflict in self.value_conflicts:
            pair = tuple(sorted(conflict.conflicting_values))
            conflict_pairs[pair] = conflict_pairs.get(pair, 0) + 1
        
        # Common resolution strategies
        resolution_strategies = {}
        for conflict in self.value_conflicts:
            strategy = conflict.resolution_approach
            resolution_strategies[strategy] = resolution_strategies.get(strategy, 0) + 1
        
        return {
            'total_conflicts': len(self.value_conflicts),
            'common_conflicts': sorted(conflict_pairs.items(), key=lambda x: x[1], reverse=True)[:5],
            'resolution_strategies': resolution_strategies,
            'recent_conflicts': [c.conflicting_values for c in self.value_conflicts[-3:]]
        }
    
    def get_value_system_summary(self) -> Dict[str, Any]:
        """Get comprehensive summary of value system state"""
        return {
            'total_values': len(self.core_values),
            'active_values': len(self.active_values),
            'value_priorities': self.get_value_priorities()[:5],
            'decisions_made': len(self.value_decisions),
            'conflicts_encountered': len(self.value_conflicts),
            'top_values': [name for name, _ in self.get_value_priorities()[:3]],
            'recent_decisions': [d.primary_value for d in self.value_decisions[-5:]],
            'value_stability': self._calculate_value_stability()
        }
    
    def _calculate_value_stability(self) -> float:
        """Calculate how stable the value system is"""
        if len(self.value_decisions) < 2:
            return 1.0
        
        # Compare recent decisions with earlier ones
        recent_decisions = self.value_decisions[-5:]
        earlier_decisions = self.value_decisions[-10:-5] if len(self.value_decisions) >= 10 else self.value_decisions[:-5]
        
        if not earlier_decisions:
            return 1.0
        
        recent_values = [d.primary_value for d in recent_decisions]
        earlier_values = [d.primary_value for d in earlier_decisions]
        
        # Calculate overlap
        common_values = set(recent_values) & set(earlier_values)
        total_values = set(recent_values) | set(earlier_values)
        
        return len(common_values) / len(total_values) if total_values else 1.0

# Global instance
value_system = ValueSystem()

def evaluate_value_based_decision(context: str, options: List[str], user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Evaluate options based on core values - main API function"""
    return value_system.evaluate_decision(context, options, user_context)

def get_current_value_priorities(context: Optional[str] = None) -> List[Tuple[str, float]]:
    """Get current value priorities"""
    return value_system.get_value_priorities(context)

def get_value_guidance(value_name: str) -> Dict[str, Any]:
    """Get guidance on how to apply a specific value"""
    return {
        'description': value_system.get_value_description(value_name),
        'manifestations': value_system.get_value_manifestations(value_name),
        'current_weight': value_system.active_values.get(value_name, 0.5)
    }

def get_value_system_status() -> Dict[str, Any]:
    """Get current status of the value system"""
    return value_system.get_value_system_summary()

def adjust_value_importance(value_name: str, adjustment: float, reason: str):
    """Adjust the importance of a value based on experience"""
    value_system.adjust_value_weight(value_name, adjustment, reason)