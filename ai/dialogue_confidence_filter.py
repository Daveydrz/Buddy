"""
Dialogue Confidence Filter - Uncertainty detection and clarification system
Provides intelligent uncertainty handling and clarification requests
"""

import re
import json
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
import random

class UncertaintyType(Enum):
    """Types of uncertainty"""
    KNOWLEDGE_GAP = "knowledge_gap"
    AMBIGUOUS_QUERY = "ambiguous_query"
    CONFLICTING_INFORMATION = "conflicting_information"
    INSUFFICIENT_CONTEXT = "insufficient_context"
    MULTIPLE_INTERPRETATIONS = "multiple_interpretations"
    TECHNICAL_COMPLEXITY = "technical_complexity"
    SUBJECTIVE_MATTER = "subjective_matter"
    OUTDATED_INFORMATION = "outdated_information"

class ClarificationStrategy(Enum):
    """Strategies for handling uncertainty"""
    ASK_DIRECT_QUESTION = "ask_direct_question"
    PROVIDE_OPTIONS = "provide_options"
    REQUEST_MORE_CONTEXT = "request_more_context"
    EXPLAIN_UNCERTAINTY = "explain_uncertainty"
    OFFER_PARTIAL_ANSWER = "offer_partial_answer"
    SUGGEST_ALTERNATIVE = "suggest_alternative"
    ACKNOWLEDGE_LIMITATION = "acknowledge_limitation"

@dataclass
class UncertaintyInstance:
    """Represents a detected uncertainty"""
    instance_id: str
    uncertainty_type: UncertaintyType
    confidence_score: float  # 0.0 to 1.0
    context: str
    query: str
    detected_indicators: List[str]
    suggested_strategy: ClarificationStrategy
    clarification_text: str
    timestamp: str
    resolved: bool = False

class DialogueConfidenceFilter:
    """Filter for detecting and handling uncertainty in dialogue"""
    
    def __init__(self, save_path: str = "dialogue_confidence_log.json"):
        self.save_path = save_path
        self.uncertainty_instances: List[UncertaintyInstance] = []
        self.uncertainty_indicators = self._initialize_uncertainty_indicators()
        self.clarification_templates = self._initialize_clarification_templates()
        self.confidence_thresholds = self._initialize_confidence_thresholds()
        self.load_uncertainty_history()
        
        # Configuration
        self.uncertainty_threshold = 0.7  # Threshold for triggering clarification
        self.enable_proactive_clarification = True
        self.max_clarification_attempts = 3
        self.clarification_history = {}  # Track clarification attempts per user
    
    def _initialize_uncertainty_indicators(self) -> Dict[str, List[str]]:
        """Initialize patterns that indicate uncertainty"""
        return {
            'knowledge_gap': [
                "I don't know", "I'm not sure", "I'm uncertain",
                "I have no information", "I lack knowledge about",
                "I'm unfamiliar with", "I don't have data on",
                "I can't find information", "I'm not aware of",
                "I don't understand", "I'm confused about"
            ],
            'ambiguous_query': [
                "what do you mean", "can you clarify", "that's unclear",
                "I need more details", "what exactly", "which one",
                "what type of", "what kind of", "what aspect",
                "be more specific", "unclear request"
            ],
            'conflicting_information': [
                "there are different views", "sources disagree",
                "conflicting information", "mixed opinions",
                "some say", "others claim", "however", "on the other hand",
                "conflicting evidence", "disputed", "controversial"
            ],
            'insufficient_context': [
                "I need more context", "depends on", "it varies",
                "without more information", "need to know more",
                "context matters", "depends on the situation",
                "more details needed", "incomplete information"
            ],
            'multiple_interpretations': [
                "could mean", "might refer to", "several possibilities",
                "different interpretations", "various meanings",
                "could be interpreted as", "multiple ways to understand",
                "different perspectives", "various approaches"
            ],
            'technical_complexity': [
                "complex topic", "technical details", "specialized knowledge",
                "advanced concept", "requires expertise", "complicated",
                "intricate", "sophisticated", "detailed analysis needed"
            ],
            'subjective_matter': [
                "matter of opinion", "subjective", "personal preference",
                "depends on individual", "varies by person",
                "personal choice", "individual experience",
                "subjective judgment", "personal perspective"
            ],
            'confidence_expressions': [
                "I think", "I believe", "I suspect", "I assume",
                "probably", "likely", "possibly", "perhaps",
                "might be", "could be", "seems like", "appears to be",
                "I'm fairly sure", "I'm somewhat confident"
            ]
        }
    
    def _initialize_clarification_templates(self) -> Dict[str, List[str]]:
        """Initialize templates for clarification responses"""
        return {
            'ask_direct_question': [
                "Could you clarify what you mean by '{query}'?",
                "I want to make sure I understand - are you asking about {topic}?",
                "To help you better, could you be more specific about {aspect}?",
                "What exactly would you like to know about {subject}?",
                "Can you provide more details about {context}?"
            ],
            'provide_options': [
                "Are you asking about {option1}, {option2}, or something else?",
                "I can help with several aspects of this: {options}. Which interests you most?",
                "This could refer to {possibilities}. Which one did you have in mind?",
                "There are different ways to approach this: {approaches}. Which would you prefer?",
                "Would you like information about {alternative1} or {alternative2}?"
            ],
            'request_more_context': [
                "Could you provide more context about {situation}?",
                "To give you the most relevant information, could you tell me more about {background}?",
                "Understanding your specific situation would help me assist you better. Could you share more details?",
                "The answer depends on your specific circumstances. Could you elaborate on {context}?",
                "More context would help me provide a better response. What's the background here?"
            ],
            'explain_uncertainty': [
                "I'm not entirely certain about this because {reason}.",
                "I want to be honest - I have some uncertainty about {aspect} because {explanation}.",
                "I'm not completely sure about this, as {uncertainty_reason}.",
                "I should mention that I'm not fully confident about {topic} because {limitation}.",
                "I'm experiencing some uncertainty here because {cause}."
            ],
            'offer_partial_answer': [
                "While I can't provide a complete answer, I can tell you that {partial_info}.",
                "I don't have all the details, but I can share what I know: {known_info}.",
                "I can provide some information, though it's not complete: {available_info}.",
                "Here's what I can tell you, though it's partial: {partial_answer}.",
                "I don't have the full picture, but here's what I do know: {known_facts}."
            ],
            'suggest_alternative': [
                "Instead of {original_request}, might I suggest {alternative}?",
                "Would {suggestion} be helpful as an alternative approach?",
                "Perhaps we could approach this differently: {alternative_approach}?",
                "If I can't answer that directly, would information about {related_topic} be useful?",
                "As an alternative, I could help you with {substitute_option}."
            ],
            'acknowledge_limitation': [
                "I need to be honest that I don't have reliable information about {topic}.",
                "I should acknowledge that this is outside my area of confidence.",
                "I want to be transparent - I don't have sufficient knowledge about {subject}.",
                "I should admit that I'm not the best source for information about {area}.",
                "I need to be upfront that I lack expertise in {domain}."
            ]
        }
    
    def _initialize_confidence_thresholds(self) -> Dict[str, float]:
        """Initialize confidence thresholds for different scenarios"""
        return {
            'factual_information': 0.8,
            'technical_advice': 0.85,
            'medical_information': 0.9,
            'legal_advice': 0.9,
            'financial_advice': 0.85,
            'personal_guidance': 0.7,
            'general_conversation': 0.6,
            'creative_tasks': 0.5,
            'opinion_based': 0.4
        }
    
    def analyze_response_confidence(self, 
                                  response: str, 
                                  query: str, 
                                  context: str,
                                  user_id: str) -> Tuple[float, Optional[UncertaintyInstance]]:
        """Analyze confidence level of a response"""
        try:
            # Calculate base confidence
            base_confidence = self._calculate_base_confidence(response, query, context)
            
            # Detect uncertainty indicators
            uncertainty_indicators = self._detect_uncertainty_indicators(response)
            
            # Calculate uncertainty impact
            uncertainty_impact = self._calculate_uncertainty_impact(uncertainty_indicators)
            
            # Adjust confidence based on uncertainty
            adjusted_confidence = base_confidence * (1 - uncertainty_impact)
            
            # Determine if clarification is needed
            clarification_needed = adjusted_confidence < self.uncertainty_threshold
            
            uncertainty_instance = None
            if clarification_needed:
                uncertainty_instance = self._create_uncertainty_instance(
                    query, context, response, uncertainty_indicators, adjusted_confidence
                )
            
            return adjusted_confidence, uncertainty_instance
            
        except Exception as e:
            print(f"[DialogueConfidenceFilter] ❌ Error analyzing confidence: {e}")
            return 0.5, None
    
    def _calculate_base_confidence(self, response: str, query: str, context: str) -> float:
        """Calculate base confidence score"""
        confidence = 0.5  # Start with neutral confidence
        
        # Length and detail indicators
        if len(response) > 100:
            confidence += 0.1  # Longer responses often indicate more knowledge
        
        if len(response) > 300:
            confidence += 0.1  # Very detailed responses
        
        # Specific information indicators
        if re.search(r'\d+', response):  # Contains numbers
            confidence += 0.05
        
        if re.search(r'[A-Z][a-z]+ [A-Z][a-z]+', response):  # Contains proper nouns
            confidence += 0.05
        
        # Technical terms (simplified detection)
        technical_terms = ['algorithm', 'system', 'process', 'method', 'technique', 'approach']
        if any(term in response.lower() for term in technical_terms):
            confidence += 0.05
        
        # Definitive language
        definitive_words = ['definitely', 'certainly', 'clearly', 'obviously', 'absolutely']
        if any(word in response.lower() for word in definitive_words):
            confidence += 0.1
        
        # Hedging language (reduces confidence)
        hedging_words = ['maybe', 'perhaps', 'possibly', 'might', 'could', 'seems']
        hedging_count = sum(1 for word in hedging_words if word in response.lower())
        confidence -= hedging_count * 0.05
        
        return max(0.0, min(1.0, confidence))
    
    def _detect_uncertainty_indicators(self, response: str) -> List[str]:
        """Detect uncertainty indicators in response"""
        detected_indicators = []
        response_lower = response.lower()
        
        for category, indicators in self.uncertainty_indicators.items():
            for indicator in indicators:
                if indicator in response_lower:
                    detected_indicators.append(f"{category}: {indicator}")
        
        return detected_indicators
    
    def _calculate_uncertainty_impact(self, uncertainty_indicators: List[str]) -> float:
        """Calculate impact of uncertainty indicators"""
        if not uncertainty_indicators:
            return 0.0
        
        # Weight different types of uncertainty
        weights = {
            'knowledge_gap': 0.3,
            'ambiguous_query': 0.2,
            'conflicting_information': 0.25,
            'insufficient_context': 0.2,
            'multiple_interpretations': 0.15,
            'technical_complexity': 0.1,
            'subjective_matter': 0.1,
            'confidence_expressions': 0.05
        }
        
        total_impact = 0.0
        for indicator in uncertainty_indicators:
            category = indicator.split(':')[0]
            weight = weights.get(category, 0.1)
            total_impact += weight
        
        return min(0.8, total_impact)  # Cap at 80% impact
    
    def _create_uncertainty_instance(self, 
                                   query: str, 
                                   context: str, 
                                   response: str,
                                   indicators: List[str],
                                   confidence: float) -> UncertaintyInstance:
        """Create uncertainty instance"""
        # Determine uncertainty type
        uncertainty_type = self._determine_uncertainty_type(indicators)
        
        # Determine strategy
        strategy = self._determine_clarification_strategy(uncertainty_type, confidence)
        
        # Generate clarification text
        clarification_text = self._generate_clarification_text(
            query, context, uncertainty_type, strategy
        )
        
        instance = UncertaintyInstance(
            instance_id=f"uncertainty_{len(self.uncertainty_instances)}",
            uncertainty_type=uncertainty_type,
            confidence_score=confidence,
            context=context,
            query=query,
            detected_indicators=indicators,
            suggested_strategy=strategy,
            clarification_text=clarification_text,
            timestamp=datetime.now().isoformat()
        )
        
        self.uncertainty_instances.append(instance)
        self.save_uncertainty_history()
        
        return instance
    
    def _determine_uncertainty_type(self, indicators: List[str]) -> UncertaintyType:
        """Determine primary uncertainty type"""
        if not indicators:
            return UncertaintyType.KNOWLEDGE_GAP
        
        # Count categories
        category_counts = {}
        for indicator in indicators:
            category = indicator.split(':')[0]
            category_counts[category] = category_counts.get(category, 0) + 1
        
        # Find most common category
        most_common = max(category_counts.items(), key=lambda x: x[1])[0]
        
        # Map to uncertainty type
        type_mapping = {
            'knowledge_gap': UncertaintyType.KNOWLEDGE_GAP,
            'ambiguous_query': UncertaintyType.AMBIGUOUS_QUERY,
            'conflicting_information': UncertaintyType.CONFLICTING_INFORMATION,
            'insufficient_context': UncertaintyType.INSUFFICIENT_CONTEXT,
            'multiple_interpretations': UncertaintyType.MULTIPLE_INTERPRETATIONS,
            'technical_complexity': UncertaintyType.TECHNICAL_COMPLEXITY,
            'subjective_matter': UncertaintyType.SUBJECTIVE_MATTER
        }
        
        return type_mapping.get(most_common, UncertaintyType.KNOWLEDGE_GAP)
    
    def _determine_clarification_strategy(self, uncertainty_type: UncertaintyType, confidence: float) -> ClarificationStrategy:
        """Determine appropriate clarification strategy"""
        if uncertainty_type == UncertaintyType.AMBIGUOUS_QUERY:
            return ClarificationStrategy.ASK_DIRECT_QUESTION
        elif uncertainty_type == UncertaintyType.MULTIPLE_INTERPRETATIONS:
            return ClarificationStrategy.PROVIDE_OPTIONS
        elif uncertainty_type == UncertaintyType.INSUFFICIENT_CONTEXT:
            return ClarificationStrategy.REQUEST_MORE_CONTEXT
        elif uncertainty_type == UncertaintyType.KNOWLEDGE_GAP:
            if confidence < 0.3:
                return ClarificationStrategy.ACKNOWLEDGE_LIMITATION
            else:
                return ClarificationStrategy.OFFER_PARTIAL_ANSWER
        elif uncertainty_type == UncertaintyType.CONFLICTING_INFORMATION:
            return ClarificationStrategy.EXPLAIN_UNCERTAINTY
        elif uncertainty_type == UncertaintyType.TECHNICAL_COMPLEXITY:
            return ClarificationStrategy.SUGGEST_ALTERNATIVE
        else:
            return ClarificationStrategy.ASK_DIRECT_QUESTION
    
    def _generate_clarification_text(self, 
                                   query: str, 
                                   context: str, 
                                   uncertainty_type: UncertaintyType,
                                   strategy: ClarificationStrategy) -> str:
        """Generate clarification text"""
        try:
            templates = self.clarification_templates.get(strategy.value, [])
            if not templates:
                return "I need some clarification to help you better."
            
            template = random.choice(templates)
            
            # Extract key terms from query for substitution
            key_terms = self._extract_key_terms(query)
            
            # Perform substitutions
            substitutions = {
                'query': query[:50],
                'topic': key_terms[0] if key_terms else 'this topic',
                'subject': key_terms[0] if key_terms else 'this subject',
                'aspect': 'this aspect',
                'context': context[:50] if context else 'your situation',
                'situation': context[:50] if context else 'this situation',
                'background': 'the background',
                'reason': 'there are multiple perspectives on this',
                'explanation': 'the information varies depending on context',
                'uncertainty_reason': 'this topic has multiple valid interpretations',
                'limitation': 'this falls outside my area of expertise',
                'cause': 'the available information is incomplete'
            }
            
            # Apply substitutions
            for key, value in substitutions.items():
                template = template.replace(f'{{{key}}}', str(value))
            
            return template
            
        except Exception as e:
            print(f"[DialogueConfidenceFilter] ❌ Error generating clarification: {e}")
            return "I need some clarification to help you better."
    
    def _extract_key_terms(self, query: str) -> List[str]:
        """Extract key terms from query"""
        # Simple keyword extraction
        words = re.findall(r'\b[a-zA-Z]{3,}\b', query.lower())
        
        # Filter out common words
        stop_words = {'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'how', 'man', 'new', 'now', 'old', 'see', 'two', 'way', 'who', 'boy', 'did', 'its', 'let', 'put', 'say', 'she', 'too', 'use'}
        
        key_terms = [word for word in words if word not in stop_words]
        return key_terms[:3]  # Return top 3 key terms
    
    def should_request_clarification(self, 
                                   response: str, 
                                   query: str, 
                                   context: str,
                                   user_id: str) -> Tuple[bool, Optional[str]]:
        """Determine if clarification should be requested"""
        confidence, uncertainty_instance = self.analyze_response_confidence(
            response, query, context, user_id
        )
        
        if uncertainty_instance and self.enable_proactive_clarification:
            # Check clarification history to avoid over-clarifying
            attempts = self.clarification_history.get(user_id, 0)
            if attempts < self.max_clarification_attempts:
                self.clarification_history[user_id] = attempts + 1
                return True, uncertainty_instance.clarification_text
        
        return False, None
    
    def filter_response_with_confidence(self, 
                                      response: str, 
                                      query: str, 
                                      context: str,
                                      user_id: str) -> Tuple[str, Dict[str, Any]]:
        """Filter response and add confidence handling"""
        try:
            # Analyze confidence
            confidence, uncertainty_instance = self.analyze_response_confidence(
                response, query, context, user_id
            )
            
            # Determine if clarification is needed
            needs_clarification, clarification_text = self.should_request_clarification(
                response, query, context, user_id
            )
            
            # Modify response if needed
            if needs_clarification and clarification_text:
                # Add clarification to response
                modified_response = f"{response}\n\n{clarification_text}"
            else:
                modified_response = response
            
            # Add confidence indicator if confidence is low
            if confidence < 0.6:
                confidence_statement = self._generate_confidence_statement(confidence)
                modified_response = f"{confidence_statement} {modified_response}"
            
            # Create metadata
            metadata = {
                'original_confidence': confidence,
                'needs_clarification': needs_clarification,
                'uncertainty_type': uncertainty_instance.uncertainty_type.value if uncertainty_instance else None,
                'clarification_strategy': uncertainty_instance.suggested_strategy.value if uncertainty_instance else None,
                'confidence_level': self._categorize_confidence(confidence)
            }
            
            return modified_response, metadata
            
        except Exception as e:
            print(f"[DialogueConfidenceFilter] ❌ Error filtering response: {e}")
            return response, {'error': str(e)}
    
    def _generate_confidence_statement(self, confidence: float) -> str:
        """Generate confidence statement"""
        if confidence < 0.3:
            return "I'm not very confident about this, but"
        elif confidence < 0.5:
            return "I'm somewhat uncertain, but"
        elif confidence < 0.7:
            return "I think"
        else:
            return "I believe"
    
    def _categorize_confidence(self, confidence: float) -> str:
        """Categorize confidence level"""
        if confidence >= 0.8:
            return "high"
        elif confidence >= 0.6:
            return "medium"
        elif confidence >= 0.4:
            return "low"
        else:
            return "very_low"
    
    def reset_clarification_history(self, user_id: str):
        """Reset clarification history for a user"""
        self.clarification_history[user_id] = 0
    
    def set_uncertainty_threshold(self, threshold: float):
        """Set uncertainty threshold"""
        self.uncertainty_threshold = max(0.0, min(1.0, threshold))
    
    def load_uncertainty_history(self):
        """Load uncertainty history from file"""
        try:
            with open(self.save_path, 'r') as f:
                data = json.load(f)
                
            for instance_data in data.get('instances', []):
                # Handle both old and new enum formats
                uncertainty_type_value = instance_data['uncertainty_type']
                if isinstance(uncertainty_type_value, str) and '.' in uncertainty_type_value:
                    uncertainty_type_value = uncertainty_type_value.split('.')[-1].lower()
                
                strategy_value = instance_data['suggested_strategy']
                if isinstance(strategy_value, str) and '.' in strategy_value:
                    strategy_value = strategy_value.split('.')[-1].lower()
                
                try:
                    uncertainty_type = UncertaintyType(uncertainty_type_value)
                    strategy = ClarificationStrategy(strategy_value)
                except ValueError as e:
                    # Fallback values if enum conversion fails
                    uncertainty_type = UncertaintyType.KNOWLEDGE_GAP
                    strategy = ClarificationStrategy.ASK_DIRECT_QUESTION
                    print(f"[DialogueConfidenceFilter] ⚠️ Enum conversion error: {e}, using fallback values")
                
                instance = UncertaintyInstance(
                    instance_id=instance_data['instance_id'],
                    uncertainty_type=uncertainty_type,
                    confidence_score=instance_data['confidence_score'],
                    context=instance_data['context'],
                    query=instance_data['query'],
                    detected_indicators=instance_data['detected_indicators'],
                    suggested_strategy=strategy,
                    clarification_text=instance_data['clarification_text'],
                    timestamp=instance_data['timestamp'],
                    resolved=instance_data.get('resolved', False)
                )
                self.uncertainty_instances.append(instance)
            
            print(f"[DialogueConfidenceFilter] 📄 Loaded {len(self.uncertainty_instances)} uncertainty instances")
            
        except FileNotFoundError:
            print(f"[DialogueConfidenceFilter] 📄 No uncertainty history found")
        except Exception as e:
            print(f"[DialogueConfidenceFilter] ❌ Error loading uncertainty history: {e}")
    
    def save_uncertainty_history(self):
        """Save uncertainty history to file"""
        try:
            data = {
                'instances': [asdict(instance) for instance in self.uncertainty_instances],
                'last_updated': datetime.now().isoformat(),
                'total_instances': len(self.uncertainty_instances)
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
            print(f"[DialogueConfidenceFilter] ❌ Error saving uncertainty history: {e}")
    
    def get_confidence_stats(self) -> Dict[str, Any]:
        """Get confidence filter statistics"""
        if not self.uncertainty_instances:
            return {'total_instances': 0, 'common_types': [], 'average_confidence': 0}
        
        # Count uncertainty types
        type_counts = {}
        total_confidence = 0
        
        for instance in self.uncertainty_instances:
            uncertainty_type = instance.uncertainty_type.value
            type_counts[uncertainty_type] = type_counts.get(uncertainty_type, 0) + 1
            total_confidence += instance.confidence_score
        
        return {
            'total_instances': len(self.uncertainty_instances),
            'common_types': sorted(type_counts.items(), key=lambda x: x[1], reverse=True)[:5],
            'average_confidence': total_confidence / len(self.uncertainty_instances),
            'uncertainty_threshold': self.uncertainty_threshold,
            'clarification_attempts': sum(self.clarification_history.values())
        }

# Global instance
dialogue_confidence_filter = DialogueConfidenceFilter()

def filter_response_confidence(response: str, query: str, context: str, user_id: str) -> Tuple[str, Dict[str, Any]]:
    """Filter response with confidence analysis - main API function"""
    return dialogue_confidence_filter.filter_response_with_confidence(response, query, context, user_id)

def analyze_response_confidence(response: str, query: str, context: str, user_id: str) -> Tuple[float, Optional[Dict[str, Any]]]:
    """Analyze confidence of response"""
    confidence, uncertainty_instance = dialogue_confidence_filter.analyze_response_confidence(
        response, query, context, user_id
    )
    uncertainty_data = asdict(uncertainty_instance) if uncertainty_instance else None
    return confidence, uncertainty_data

def should_request_clarification(response: str, query: str, context: str, user_id: str) -> Tuple[bool, Optional[str]]:
    """Check if clarification should be requested"""
    return dialogue_confidence_filter.should_request_clarification(response, query, context, user_id)

def reset_user_clarification_history(user_id: str):
    """Reset clarification history for user"""
    dialogue_confidence_filter.reset_clarification_history(user_id)

def set_confidence_threshold(threshold: float):
    """Set confidence threshold for clarification"""
    dialogue_confidence_filter.set_uncertainty_threshold(threshold)

def get_confidence_filter_stats() -> Dict[str, Any]:
    """Get confidence filter statistics"""
    return dialogue_confidence_filter.get_confidence_stats()