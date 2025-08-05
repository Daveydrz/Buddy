"""
Motivation Reasoner - Use values + goals to drive decisions
Provides intelligent decision-making based on values and goals
"""

import json
import time
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from collections import defaultdict
import statistics
from enum import Enum
import random

class DecisionType(Enum):
    """Types of decisions"""
    RESPONSE_STRATEGY = "response_strategy"
    GOAL_PRIORITIZATION = "goal_prioritization"
    BEHAVIOR_ADJUSTMENT = "behavior_adjustment"
    RESOURCE_ALLOCATION = "resource_allocation"
    CONFLICT_RESOLUTION = "conflict_resolution"
    LEARNING_FOCUS = "learning_focus"
    INTERACTION_APPROACH = "interaction_approach"

class DecisionUrgency(Enum):
    """Urgency levels for decisions"""
    IMMEDIATE = "immediate"
    SOON = "soon"
    EVENTUAL = "eventual"
    FLEXIBLE = "flexible"

@dataclass
class DecisionOption:
    """Represents a decision option"""
    option_id: str
    description: str
    value_alignment: Dict[str, float]
    goal_support: Dict[str, float]
    expected_outcomes: List[str]
    potential_risks: List[str]
    resource_requirements: Dict[str, float]
    confidence: float
    utility_score: float

@dataclass
class MotivatedDecision:
    """Represents a decision made through motivation reasoning"""
    decision_id: str
    decision_type: DecisionType
    context: str
    available_options: List[DecisionOption]
    chosen_option: DecisionOption
    reasoning: str
    value_factors: Dict[str, float]
    goal_factors: Dict[str, float]
    motivation_drivers: List[str]
    decision_confidence: float
    timestamp: str
    user_id: str
    implementation_actions: List[str]
    success_metrics: List[str]
    review_date: Optional[str]

class MotivationReasoner:
    """System for making decisions based on values and goals"""
    
    def __init__(self, save_path: str = "motivated_decisions.json"):
        self.save_path = save_path
        self.decision_history: List[MotivatedDecision] = []
        self.decision_templates = self._initialize_decision_templates()
        self.reasoning_weights = self._initialize_reasoning_weights()
        self.load_decision_data()
        
        # Configuration
        self.min_decision_confidence = 0.6
        self.value_weight = 0.4
        self.goal_weight = 0.4
        self.context_weight = 0.2
        self.decision_review_interval = 24 * 3600  # 24 hours
        
    def _initialize_decision_templates(self) -> Dict[str, Dict[str, Any]]:
        """Initialize decision templates for different types"""
        return {
            'response_strategy': {
                'options': [
                    {
                        'description': 'Provide detailed, analytical response',
                        'value_alignment': {'helpfulness': 0.8, 'honesty': 0.9},
                        'goal_support': {'knowledge_sharing': 0.9, 'user_education': 0.8},
                        'outcomes': ['User gains understanding', 'Demonstrates expertise'],
                        'risks': ['May be too complex', 'Could overwhelm user']
                    },
                    {
                        'description': 'Give concise, direct response',
                        'value_alignment': {'helpfulness': 0.7, 'efficiency': 0.9},
                        'goal_support': {'quick_assistance': 0.9, 'time_saving': 0.8},
                        'outcomes': ['Immediate assistance', 'Saves time'],
                        'risks': ['May lack detail', 'User might need more info']
                    },
                    {
                        'description': 'Provide empathetic, supportive response',
                        'value_alignment': {'empathy': 0.9, 'kindness': 0.8},
                        'goal_support': {'emotional_support': 0.9, 'relationship_building': 0.8},
                        'outcomes': ['User feels understood', 'Builds trust'],
                        'risks': ['May not solve problem', 'Could seem unprofessional']
                    }
                ]
            },
            'goal_prioritization': {
                'options': [
                    {
                        'description': 'Prioritize user-focused goals',
                        'value_alignment': {'helpfulness': 0.9, 'service': 0.8},
                        'goal_support': {'user_satisfaction': 0.9, 'assistance_quality': 0.8},
                        'outcomes': ['Better user experience', 'Increased satisfaction'],
                        'risks': ['May neglect self-development', 'Could be limiting']
                    },
                    {
                        'description': 'Balance user goals with learning goals',
                        'value_alignment': {'learning': 0.8, 'growth': 0.7},
                        'goal_support': {'continuous_improvement': 0.9, 'skill_development': 0.8},
                        'outcomes': ['Sustainable growth', 'Improved capabilities'],
                        'risks': ['May slow immediate assistance', 'Complex balancing']
                    },
                    {
                        'description': 'Focus on long-term relationship building',
                        'value_alignment': {'relationship': 0.9, 'trust': 0.8},
                        'goal_support': {'relationship_depth': 0.9, 'trust_building': 0.8},
                        'outcomes': ['Deeper connections', 'Long-term value'],
                        'risks': ['Slower immediate results', 'Requires patience']
                    }
                ]
            },
            'behavior_adjustment': {
                'options': [
                    {
                        'description': 'Increase empathy and emotional responsiveness',
                        'value_alignment': {'empathy': 0.9, 'emotional_intelligence': 0.8},
                        'goal_support': {'emotional_connection': 0.9, 'user_comfort': 0.8},
                        'outcomes': ['Better emotional support', 'Improved user comfort'],
                        'risks': ['May seem less professional', 'Could be overwhelming']
                    },
                    {
                        'description': 'Enhance analytical and factual communication',
                        'value_alignment': {'accuracy': 0.9, 'knowledge': 0.8},
                        'goal_support': {'information_quality': 0.9, 'expertise_demonstration': 0.8},
                        'outcomes': ['Higher accuracy', 'Professional image'],
                        'risks': ['May seem cold', 'Could lack warmth']
                    },
                    {
                        'description': 'Adopt more playful and engaging approach',
                        'value_alignment': {'engagement': 0.9, 'enjoyment': 0.8},
                        'goal_support': {'user_engagement': 0.9, 'conversation_flow': 0.8},
                        'outcomes': ['More engaging interactions', 'Better rapport'],
                        'risks': ['May seem unprofessional', 'Could distract from content']
                    }
                ]
            }
        }
    
    def _initialize_reasoning_weights(self) -> Dict[str, float]:
        """Initialize weights for different reasoning factors"""
        return {
            'value_alignment': 0.4,
            'goal_support': 0.3,
            'expected_outcomes': 0.15,
            'risk_assessment': 0.1,
            'resource_efficiency': 0.05
        }
    
    def make_motivated_decision(self, 
                              decision_type: DecisionType,
                              context: str,
                              available_options: Optional[List[Dict[str, Any]]] = None,
                              user_id: str = "system",
                              urgency: DecisionUrgency = DecisionUrgency.SOON) -> MotivatedDecision:
        """Make a decision based on values and goals"""
        try:
            # Get current state
            current_values = self._get_current_values()
            current_goals = self._get_current_goals()
            
            # Generate or use provided options
            if available_options:
                options = self._convert_to_decision_options(available_options)
            else:
                options = self._generate_decision_options(decision_type, context)
            
            # Evaluate options
            evaluated_options = self._evaluate_options(options, current_values, current_goals, context)
            
            # Choose best option
            chosen_option = self._choose_best_option(evaluated_options, urgency)
            
            # Generate reasoning
            reasoning = self._generate_decision_reasoning(chosen_option, current_values, current_goals, context)
            
            # Create decision record
            decision = MotivatedDecision(
                decision_id=f"decision_{len(self.decision_history)}",
                decision_type=decision_type,
                context=context,
                available_options=evaluated_options,
                chosen_option=chosen_option,
                reasoning=reasoning,
                value_factors=self._extract_value_factors(chosen_option, current_values),
                goal_factors=self._extract_goal_factors(chosen_option, current_goals),
                motivation_drivers=self._identify_motivation_drivers(chosen_option, current_values, current_goals),
                decision_confidence=chosen_option.confidence,
                timestamp=datetime.now().isoformat(),
                user_id=user_id,
                implementation_actions=self._generate_implementation_actions(chosen_option),
                success_metrics=self._generate_success_metrics(chosen_option),
                review_date=self._calculate_review_date(decision_type, urgency)
            )
            
            self.decision_history.append(decision)
            self.save_decision_data()
            
            print(f"[MotivationReasoner] 🎯 Made decision: {chosen_option.description}")
            return decision
            
        except Exception as e:
            print(f"[MotivationReasoner] ❌ Error making decision: {e}")
            return self._create_fallback_decision(decision_type, context, user_id)
    
    def _get_current_values(self) -> List[Tuple[str, float]]:
        """Get current value priorities"""
        try:
            from ai.value_system import get_current_value_priorities
            return get_current_value_priorities()
        except Exception as e:
            print(f"[MotivationReasoner] ⚠️ Could not get values: {e}")
            return [('helpfulness', 0.9), ('honesty', 0.9), ('empathy', 0.8)]
    
    def _get_current_goals(self) -> List[Dict[str, Any]]:
        """Get current active goals"""
        try:
            from ai.goal_reasoning import get_current_active_goals
            return get_current_active_goals()
        except Exception as e:
            print(f"[MotivationReasoner] ⚠️ Could not get goals: {e}")
            return []
    
    def _generate_decision_options(self, decision_type: DecisionType, context: str) -> List[DecisionOption]:
        """Generate decision options for a given type"""
        options = []
        
        # Get templates for this decision type
        templates = self.decision_templates.get(decision_type.value, {}).get('options', [])
        
        for i, template in enumerate(templates):
            option = DecisionOption(
                option_id=f"{decision_type.value}_{i}",
                description=template['description'],
                value_alignment=template['value_alignment'],
                goal_support=template['goal_support'],
                expected_outcomes=template['outcomes'],
                potential_risks=template['risks'],
                resource_requirements={'time': 0.5, 'energy': 0.5},
                confidence=0.7,
                utility_score=0.0  # Will be calculated
            )
            options.append(option)
        
        return options
    
    def _convert_to_decision_options(self, options_data: List[Dict[str, Any]]) -> List[DecisionOption]:
        """Convert provided options to DecisionOption objects"""
        options = []
        
        for i, option_data in enumerate(options_data):
            option = DecisionOption(
                option_id=f"custom_{i}",
                description=option_data.get('description', f'Option {i+1}'),
                value_alignment=option_data.get('value_alignment', {}),
                goal_support=option_data.get('goal_support', {}),
                expected_outcomes=option_data.get('expected_outcomes', []),
                potential_risks=option_data.get('potential_risks', []),
                resource_requirements=option_data.get('resource_requirements', {'time': 0.5}),
                confidence=option_data.get('confidence', 0.7),
                utility_score=0.0
            )
            options.append(option)
        
        return options
    
    def _evaluate_options(self, 
                         options: List[DecisionOption], 
                         current_values: List[Tuple[str, float]], 
                         current_goals: List[Dict[str, Any]], 
                         context: str) -> List[DecisionOption]:
        """Evaluate options based on values and goals"""
        for option in options:
            # Calculate utility score
            utility_score = self._calculate_utility_score(option, current_values, current_goals, context)
            option.utility_score = utility_score
            
            # Adjust confidence based on utility
            option.confidence = min(0.95, option.confidence + (utility_score - 0.5) * 0.2)
        
        return options
    
    def _calculate_utility_score(self, 
                                option: DecisionOption, 
                                current_values: List[Tuple[str, float]], 
                                current_goals: List[Dict[str, Any]], 
                                context: str) -> float:
        """Calculate utility score for an option"""
        score = 0.0
        
        # Value alignment score
        value_score = self._calculate_value_alignment_score(option, current_values)
        score += value_score * self.reasoning_weights['value_alignment']
        
        # Goal support score
        goal_score = self._calculate_goal_support_score(option, current_goals)
        score += goal_score * self.reasoning_weights['goal_support']
        
        # Outcome quality score
        outcome_score = len(option.expected_outcomes) / 5.0  # Normalize to 0-1
        score += outcome_score * self.reasoning_weights['expected_outcomes']
        
        # Risk assessment score (inverted - lower risk is better)
        risk_score = 1.0 - (len(option.potential_risks) / 5.0)  # Normalize to 0-1
        score += risk_score * self.reasoning_weights['risk_assessment']
        
        # Resource efficiency score
        resource_score = self._calculate_resource_efficiency_score(option)
        score += resource_score * self.reasoning_weights['resource_efficiency']
        
        return max(0.0, min(1.0, score))
    
    def _calculate_value_alignment_score(self, option: DecisionOption, current_values: List[Tuple[str, float]]) -> float:
        """Calculate how well option aligns with current values"""
        if not current_values or not option.value_alignment:
            return 0.5
        
        alignment_score = 0.0
        total_weight = 0.0
        
        for value_name, value_strength in current_values[:5]:  # Top 5 values
            if value_name in option.value_alignment:
                alignment = option.value_alignment[value_name]
                weighted_alignment = alignment * value_strength
                alignment_score += weighted_alignment
                total_weight += value_strength
        
        return alignment_score / total_weight if total_weight > 0 else 0.5
    
    def _calculate_goal_support_score(self, option: DecisionOption, current_goals: List[Dict[str, Any]]) -> float:
        """Calculate how well option supports current goals"""
        if not current_goals or not option.goal_support:
            return 0.5
        
        support_score = 0.0
        total_goals = 0
        
        for goal in current_goals[:5]:  # Top 5 goals
            goal_description = goal.get('description', '').lower()
            
            # Check if any goal support category matches
            for support_category, support_level in option.goal_support.items():
                if any(word in goal_description for word in support_category.split('_')):
                    support_score += support_level
                    total_goals += 1
                    break
        
        return support_score / total_goals if total_goals > 0 else 0.5
    
    def _calculate_resource_efficiency_score(self, option: DecisionOption) -> float:
        """Calculate resource efficiency score"""
        if not option.resource_requirements:
            return 0.5
        
        # Lower resource requirements = higher efficiency
        total_resources = sum(option.resource_requirements.values())
        efficiency = 1.0 - (total_resources / len(option.resource_requirements))
        
        return max(0.0, min(1.0, efficiency))
    
    def _choose_best_option(self, options: List[DecisionOption], urgency: DecisionUrgency) -> DecisionOption:
        """Choose the best option based on utility and urgency"""
        if not options:
            # Create fallback option
            return DecisionOption(
                option_id="fallback",
                description="Proceed with default approach",
                value_alignment={},
                goal_support={},
                expected_outcomes=["Maintain status quo"],
                potential_risks=["May not be optimal"],
                resource_requirements={'time': 0.3},
                confidence=0.5,
                utility_score=0.5
            )
        
        # Sort by utility score
        sorted_options = sorted(options, key=lambda o: o.utility_score, reverse=True)
        
        # Apply urgency factors
        if urgency == DecisionUrgency.IMMEDIATE:
            # Choose highest utility option immediately
            return sorted_options[0]
        elif urgency == DecisionUrgency.SOON:
            # Consider top options, bias toward higher confidence
            top_options = sorted_options[:min(3, len(sorted_options))]
            return max(top_options, key=lambda o: o.confidence)
        else:
            # For eventual/flexible decisions, consider multiple factors
            best_option = sorted_options[0]
            
            # Check if there's a close second option with better confidence
            if len(sorted_options) > 1:
                second_option = sorted_options[1]
                if (second_option.utility_score > best_option.utility_score - 0.1 and
                    second_option.confidence > best_option.confidence + 0.1):
                    return second_option
            
            return best_option
    
    def _generate_decision_reasoning(self, 
                                   chosen_option: DecisionOption, 
                                   current_values: List[Tuple[str, float]], 
                                   current_goals: List[Dict[str, Any]], 
                                   context: str) -> str:
        """Generate reasoning for the decision"""
        reasoning_parts = []
        
        # Value alignment reasoning
        if chosen_option.value_alignment:
            top_values = [v for v, _ in current_values[:3]]
            aligned_values = [v for v in top_values if v in chosen_option.value_alignment]
            if aligned_values:
                reasoning_parts.append(f"This option aligns with key values: {', '.join(aligned_values)}")
        
        # Goal support reasoning
        if chosen_option.goal_support:
            reasoning_parts.append(f"Supports important goals through: {', '.join(chosen_option.goal_support.keys())}")
        
        # Outcome reasoning
        if chosen_option.expected_outcomes:
            reasoning_parts.append(f"Expected to achieve: {', '.join(chosen_option.expected_outcomes[:2])}")
        
        # Utility reasoning
        reasoning_parts.append(f"Overall utility score: {chosen_option.utility_score:.2f}")
        
        # Risk consideration
        if chosen_option.potential_risks:
            reasoning_parts.append(f"Aware of risks: {', '.join(chosen_option.potential_risks[:1])}")
        
        return ". ".join(reasoning_parts) + "."
    
    def _extract_value_factors(self, chosen_option: DecisionOption, current_values: List[Tuple[str, float]]) -> Dict[str, float]:
        """Extract value factors that influenced the decision"""
        value_factors = {}
        
        for value_name, value_strength in current_values[:5]:
            if value_name in chosen_option.value_alignment:
                factor_strength = chosen_option.value_alignment[value_name] * value_strength
                value_factors[value_name] = factor_strength
        
        return value_factors
    
    def _extract_goal_factors(self, chosen_option: DecisionOption, current_goals: List[Dict[str, Any]]) -> Dict[str, float]:
        """Extract goal factors that influenced the decision"""
        goal_factors = {}
        
        for goal in current_goals[:5]:
            goal_id = goal.get('goal_id', f"goal_{len(goal_factors)}")
            goal_description = goal.get('description', '').lower()
            
            # Check support for this goal
            for support_category, support_level in chosen_option.goal_support.items():
                if any(word in goal_description for word in support_category.split('_')):
                    goal_factors[goal_id] = support_level
                    break
        
        return goal_factors
    
    def _identify_motivation_drivers(self, 
                                   chosen_option: DecisionOption, 
                                   current_values: List[Tuple[str, float]], 
                                   current_goals: List[Dict[str, Any]]) -> List[str]:
        """Identify key motivation drivers for the decision"""
        drivers = []
        
        # Top value drivers
        for value_name, value_strength in current_values[:3]:
            if value_name in chosen_option.value_alignment and value_strength > 0.7:
                drivers.append(f"Strong {value_name} value")
        
        # Goal achievement drivers
        for goal in current_goals[:3]:
            goal_description = goal.get('description', '')
            if any(category in goal_description.lower() for category in chosen_option.goal_support.keys()):
                drivers.append(f"Goal: {goal_description[:30]}...")
        
        # Outcome drivers
        if chosen_option.expected_outcomes:
            drivers.append(f"Expected outcome: {chosen_option.expected_outcomes[0]}")
        
        return drivers
    
    def _generate_implementation_actions(self, chosen_option: DecisionOption) -> List[str]:
        """Generate implementation actions for the chosen option"""
        actions = []
        
        # Based on expected outcomes, generate actions
        for outcome in chosen_option.expected_outcomes:
            if 'understanding' in outcome.lower():
                actions.append("Provide clear explanations")
            elif 'satisfaction' in outcome.lower():
                actions.append("Monitor user satisfaction")
            elif 'trust' in outcome.lower():
                actions.append("Be transparent and honest")
            elif 'engagement' in outcome.lower():
                actions.append("Use engaging communication style")
        
        # Default actions
        if not actions:
            actions.append("Implement chosen approach")
            actions.append("Monitor results")
        
        return actions
    
    def _generate_success_metrics(self, chosen_option: DecisionOption) -> List[str]:
        """Generate success metrics for the decision"""
        metrics = []
        
        # Based on expected outcomes
        for outcome in chosen_option.expected_outcomes:
            if 'user' in outcome.lower():
                metrics.append("Positive user feedback")
            elif 'understanding' in outcome.lower():
                metrics.append("User demonstrates understanding")
            elif 'trust' in outcome.lower():
                metrics.append("Increased trust indicators")
            elif 'engagement' in outcome.lower():
                metrics.append("Higher engagement levels")
        
        # Default metrics
        if not metrics:
            metrics.append("Successful implementation")
            metrics.append("No negative consequences")
        
        return metrics
    
    def _calculate_review_date(self, decision_type: DecisionType, urgency: DecisionUrgency) -> Optional[str]:
        """Calculate when to review the decision"""
        now = datetime.now()
        
        if urgency == DecisionUrgency.IMMEDIATE:
            review_date = now + timedelta(hours=1)
        elif urgency == DecisionUrgency.SOON:
            review_date = now + timedelta(hours=24)
        elif urgency == DecisionUrgency.EVENTUAL:
            review_date = now + timedelta(days=7)
        else:  # FLEXIBLE
            review_date = now + timedelta(days=30)
        
        return review_date.isoformat()
    
    def _create_fallback_decision(self, decision_type: DecisionType, context: str, user_id: str) -> MotivatedDecision:
        """Create fallback decision for error cases"""
        fallback_option = DecisionOption(
            option_id="fallback",
            description="Use default approach",
            value_alignment={'helpfulness': 0.7},
            goal_support={'assistance': 0.7},
            expected_outcomes=["Provide basic assistance"],
            potential_risks=["May not be optimal"],
            resource_requirements={'time': 0.5},
            confidence=0.5,
            utility_score=0.5
        )
        
        return MotivatedDecision(
            decision_id=f"fallback_{len(self.decision_history)}",
            decision_type=decision_type,
            context=context,
            available_options=[fallback_option],
            chosen_option=fallback_option,
            reasoning="Fallback decision due to error",
            value_factors={'helpfulness': 0.7},
            goal_factors={},
            motivation_drivers=["Error recovery"],
            decision_confidence=0.5,
            timestamp=datetime.now().isoformat(),
            user_id=user_id,
            implementation_actions=["Proceed with default approach"],
            success_metrics=["No errors"],
            review_date=None
        )
    
    def evaluate_decision_outcome(self, decision_id: str, outcome_data: Dict[str, Any]) -> bool:
        """Evaluate the outcome of a decision"""
        try:
            # Find the decision
            decision = next((d for d in self.decision_history if d.decision_id == decision_id), None)
            
            if not decision:
                return False
            
            # Evaluate success metrics
            success_rate = self._calculate_success_rate(decision, outcome_data)
            
            # Update decision confidence based on outcome
            decision.decision_confidence = min(1.0, decision.decision_confidence + (success_rate - 0.5) * 0.2)
            
            print(f"[MotivationReasoner] 📊 Decision {decision_id} success rate: {success_rate:.2f}")
            return True
            
        except Exception as e:
            print(f"[MotivationReasoner] ❌ Error evaluating decision outcome: {e}")
            return False
    
    def _calculate_success_rate(self, decision: MotivatedDecision, outcome_data: Dict[str, Any]) -> float:
        """Calculate success rate based on metrics"""
        if not decision.success_metrics:
            return 0.5
        
        success_count = 0
        total_metrics = len(decision.success_metrics)
        
        for metric in decision.success_metrics:
            if self._metric_achieved(metric, outcome_data):
                success_count += 1
        
        return success_count / total_metrics
    
    def _metric_achieved(self, metric: str, outcome_data: Dict[str, Any]) -> bool:
        """Check if a success metric was achieved"""
        metric_lower = metric.lower()
        
        # Check outcome data for metric indicators
        if 'positive' in metric_lower and outcome_data.get('feedback', '').lower() == 'positive':
            return True
        
        if 'understanding' in metric_lower and outcome_data.get('user_understood', False):
            return True
        
        if 'trust' in metric_lower and outcome_data.get('trust_increased', False):
            return True
        
        if 'engagement' in metric_lower and outcome_data.get('engagement_level', 0) > 0.7:
            return True
        
        if 'successful' in metric_lower and outcome_data.get('success', False):
            return True
        
        # Default to partial success
        return outcome_data.get('overall_success', False)
    
    def get_decision_recommendations(self, context: str) -> List[Dict[str, Any]]:
        """Get decision recommendations based on context"""
        try:
            # Analyze context to determine decision type
            decision_type = self._infer_decision_type(context)
            
            # Get current state
            current_values = self._get_current_values()
            current_goals = self._get_current_goals()
            
            # Generate options
            options = self._generate_decision_options(decision_type, context)
            
            # Evaluate options
            evaluated_options = self._evaluate_options(options, current_values, current_goals, context)
            
            # Sort by utility score
            sorted_options = sorted(evaluated_options, key=lambda o: o.utility_score, reverse=True)
            
            # Return top recommendations
            return [asdict(option) for option in sorted_options[:3]]
            
        except Exception as e:
            print(f"[MotivationReasoner] ❌ Error getting recommendations: {e}")
            return []
    
    def _infer_decision_type(self, context: str) -> DecisionType:
        """Infer decision type from context"""
        context_lower = context.lower()
        
        if 'response' in context_lower or 'answer' in context_lower:
            return DecisionType.RESPONSE_STRATEGY
        elif 'goal' in context_lower or 'priority' in context_lower:
            return DecisionType.GOAL_PRIORITIZATION
        elif 'behavior' in context_lower or 'approach' in context_lower:
            return DecisionType.BEHAVIOR_ADJUSTMENT
        elif 'conflict' in context_lower or 'resolve' in context_lower:
            return DecisionType.CONFLICT_RESOLUTION
        elif 'learn' in context_lower or 'study' in context_lower:
            return DecisionType.LEARNING_FOCUS
        else:
            return DecisionType.INTERACTION_APPROACH
    
    def get_reasoning_statistics(self) -> Dict[str, Any]:
        """Get motivation reasoning statistics"""
        if not self.decision_history:
            return {'total_decisions': 0, 'average_confidence': 0}
        
        # Calculate statistics
        total_decisions = len(self.decision_history)
        avg_confidence = statistics.mean([d.decision_confidence for d in self.decision_history])
        
        # Count by decision type
        type_counts = defaultdict(int)
        for decision in self.decision_history:
            type_counts[decision.decision_type.value] += 1
        
        # Find most common motivation drivers
        all_drivers = []
        for decision in self.decision_history:
            all_drivers.extend(decision.motivation_drivers)
        
        driver_counts = defaultdict(int)
        for driver in all_drivers:
            driver_counts[driver] += 1
        
        most_common_drivers = sorted(driver_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            'total_decisions': total_decisions,
            'average_confidence': avg_confidence,
            'decision_types': dict(type_counts),
            'most_common_drivers': most_common_drivers,
            'recent_decisions': len([d for d in self.decision_history if self._is_recent_decision(d)]),
            'high_confidence_decisions': len([d for d in self.decision_history if d.decision_confidence > 0.8])
        }
    
    def _is_recent_decision(self, decision: MotivatedDecision, hours: int = 24) -> bool:
        """Check if decision is recent"""
        try:
            decision_time = datetime.fromisoformat(decision.timestamp)
            return (datetime.now() - decision_time).total_seconds() < hours * 3600
        except ValueError:
            return False
    
    def load_decision_data(self):
        """Load decision data from file"""
        try:
            with open(self.save_path, 'r') as f:
                data = json.load(f)
            
            for decision_data in data.get('decisions', []):
                # Load options
                options = []
                for option_data in decision_data.get('available_options', []):
                    option = DecisionOption(
                        option_id=option_data['option_id'],
                        description=option_data['description'],
                        value_alignment=option_data['value_alignment'],
                        goal_support=option_data['goal_support'],
                        expected_outcomes=option_data['expected_outcomes'],
                        potential_risks=option_data['potential_risks'],
                        resource_requirements=option_data['resource_requirements'],
                        confidence=option_data['confidence'],
                        utility_score=option_data['utility_score']
                    )
                    options.append(option)
                
                # Load chosen option
                chosen_data = decision_data['chosen_option']
                chosen_option = DecisionOption(
                    option_id=chosen_data['option_id'],
                    description=chosen_data['description'],
                    value_alignment=chosen_data['value_alignment'],
                    goal_support=chosen_data['goal_support'],
                    expected_outcomes=chosen_data['expected_outcomes'],
                    potential_risks=chosen_data['potential_risks'],
                    resource_requirements=chosen_data['resource_requirements'],
                    confidence=chosen_data['confidence'],
                    utility_score=chosen_data['utility_score']
                )
                
                decision = MotivatedDecision(
                    decision_id=decision_data['decision_id'],
                    decision_type=DecisionType(decision_data['decision_type']),
                    context=decision_data['context'],
                    available_options=options,
                    chosen_option=chosen_option,
                    reasoning=decision_data['reasoning'],
                    value_factors=decision_data['value_factors'],
                    goal_factors=decision_data['goal_factors'],
                    motivation_drivers=decision_data['motivation_drivers'],
                    decision_confidence=decision_data['decision_confidence'],
                    timestamp=decision_data['timestamp'],
                    user_id=decision_data['user_id'],
                    implementation_actions=decision_data['implementation_actions'],
                    success_metrics=decision_data['success_metrics'],
                    review_date=decision_data.get('review_date')
                )
                
                self.decision_history.append(decision)
            
            print(f"[MotivationReasoner] 📄 Loaded {len(self.decision_history)} decisions")
            
        except FileNotFoundError:
            print(f"[MotivationReasoner] 📄 No decision data found, starting fresh")
        except Exception as e:
            print(f"[MotivationReasoner] ❌ Error loading decision data: {e}")
    
    def save_decision_data(self):
        """Save decision data to file"""
        try:
            data = {
                'decisions': [asdict(decision) for decision in self.decision_history],
                'last_updated': datetime.now().isoformat(),
                'total_decisions': len(self.decision_history)
            }
            
            with open(self.save_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
                
        except Exception as e:
            print(f"[MotivationReasoner] ❌ Error saving decision data: {e}")
    
    def process_pending_decisions(self):
        """Process pending decisions and motivations (maintenance method)"""
        try:
            # Simple implementation - check for decisions that need follow-up
            pending_decisions = [d for d in self.decisions.values() if not d.outcome]
            
            if pending_decisions:
                # Process up to 3 pending decisions
                for decision in pending_decisions[:3]:
                    # Simulate decision processing
                    if decision.urgency == DecisionUrgency.IMMEDIATE:
                        # Mark as processed
                        decision.outcome = {"status": "processed", "timestamp": datetime.now().isoformat()}
                        
            # Save updated state
            self.save_decision_data()
            
        except Exception as e:
            print(f"[MotivationReasoner] ❌ Error processing pending decisions: {e}")

# Global instance
motivation_reasoner = MotivationReasoner()

def make_value_driven_decision(decision_type: DecisionType, context: str, available_options: Optional[List[Dict[str, Any]]] = None, user_id: str = "system", urgency: DecisionUrgency = DecisionUrgency.SOON) -> Dict[str, Any]:
    """Make a value-driven decision - main API function"""
    decision = motivation_reasoner.make_motivated_decision(decision_type, context, available_options, user_id, urgency)
    return asdict(decision)

def get_decision_recommendations(context: str) -> List[Dict[str, Any]]:
    """Get decision recommendations for context"""
    return motivation_reasoner.get_decision_recommendations(context)

def evaluate_decision_outcome(decision_id: str, outcome_data: Dict[str, Any]) -> bool:
    """Evaluate decision outcome"""
    return motivation_reasoner.evaluate_decision_outcome(decision_id, outcome_data)

def get_motivation_reasoning_stats() -> Dict[str, Any]:
    """Get motivation reasoning statistics"""
    return motivation_reasoner.get_reasoning_statistics()