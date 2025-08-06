"""
Template Sanitization & Validation System
Created: 2025-01-08
Purpose: Removes specific example data from templates and validates extracted content relevance

Key Features:
- Removes specific example data from templates (McDonald's/Francesco memories)
- Verifies extracted content actually relates to conversation
- Adds runtime validation of memory relevance
- Prevents hallucinated or template-contaminated memories
"""

import re
import json
import time
import hashlib
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

@dataclass
class ValidationResult:
    """Result of template validation"""
    is_valid: bool
    confidence_score: float
    issues_found: List[str]
    sanitized_content: str
    validation_metadata: Dict[str, Any]

class TemplatePatternDetector:
    """Detects template patterns and example data contamination"""
    
    def __init__(self):
        # Common template patterns to detect and remove
        self.template_patterns = {
            'restaurant_examples': [
                r'\bmcdonald\'?s\b',
                r'\bbig mac\b',
                r'\bhappy meal\b',
                r'\bmcflurry\b',
                r'\bfrench fries from mcdonald\'?s\b'
            ],
            'person_examples': [
                r'\bfrancesco\b',
                r'\bmario rossi\b',
                r'\bjohn doe\b',
                r'\bjane smith\b',
                r'\bexample user\b'
            ],
            'template_phrases': [
                r'for example',
                r'such as',
                r'like when',
                r'example:',
                r'e\.g\.',
                r'i\.e\.',
                r'\[example\]',
                r'\[placeholder\]',
                r'\{.*?\}',  # Template variables
                r'sample conversation',
                r'template response'
            ],
            'generic_memories': [
                r'user mentioned (they|their|that they)',
                r'user said (they|their|that they)',
                r'user told me (they|their|that they)',
                r'the user (likes|prefers|wants|needs)',
                r'user has (a|an|the|some)',
                r'user is (a|an|the)',
                r'user does (like|prefer|want|need)'
            ]
        }
        
        # Compile regex patterns for efficiency
        self.compiled_patterns = {}
        for category, patterns in self.template_patterns.items():
            self.compiled_patterns[category] = [re.compile(pattern, re.IGNORECASE) for pattern in patterns]
        
        print("[TemplatePatternDetector] 🔍 Template pattern detector initialized")
        print(f"[TemplatePatternDetector] 📋 Monitoring {sum(len(p) for p in self.template_patterns.values())} template patterns")
    
    def detect_template_contamination(self, content: str) -> Dict[str, Any]:
        """Detect template contamination in content"""
        contamination_score = 0
        detected_patterns = []
        pattern_counts = {}
        
        for category, patterns in self.compiled_patterns.items():
            category_matches = 0
            for pattern in patterns:
                matches = pattern.findall(content)
                if matches:
                    category_matches += len(matches)
                    detected_patterns.extend(matches)
                    contamination_score += len(matches) * self._get_pattern_weight(category)
            
            if category_matches > 0:
                pattern_counts[category] = category_matches
        
        # Normalize contamination score (0-1)
        max_possible_score = len(content.split()) * 0.5  # Rough estimate
        normalized_score = min(contamination_score / max_possible_score, 1.0) if max_possible_score > 0 else 0
        
        return {
            'contamination_score': normalized_score,
            'detected_patterns': detected_patterns,
            'pattern_counts': pattern_counts,
            'is_contaminated': normalized_score > 0.3,  # Threshold for contamination
            'confidence': 1.0 - normalized_score
        }
    
    def _get_pattern_weight(self, category: str) -> float:
        """Get weight for different pattern categories"""
        weights = {
            'restaurant_examples': 2.0,  # High weight for specific examples
            'person_examples': 2.0,      # High weight for example names
            'template_phrases': 1.0,     # Medium weight for template language
            'generic_memories': 1.5      # Higher weight for generic patterns
        }
        return weights.get(category, 1.0)

class ContentRelevanceValidator:
    """Validates that extracted content actually relates to the conversation"""
    
    def __init__(self):
        self.relevance_threshold = 0.6
        self.semantic_keywords_cache = {}
        
        print("[ContentRelevanceValidator] 🎯 Content relevance validator initialized")
    
    def validate_relevance(self, extracted_content: str, conversation_text: str, 
                          conversation_context: str = "") -> Dict[str, Any]:
        """Validate that extracted content is relevant to the conversation"""
        
        # Extract keywords from conversation
        conversation_keywords = self._extract_keywords(conversation_text)
        context_keywords = self._extract_keywords(conversation_context) if conversation_context else set()
        all_conversation_keywords = conversation_keywords.union(context_keywords)
        
        # Extract keywords from extracted content
        content_keywords = self._extract_keywords(extracted_content)
        
        # Calculate relevance metrics
        keyword_overlap = len(content_keywords.intersection(all_conversation_keywords))
        total_content_keywords = len(content_keywords)
        total_conversation_keywords = len(all_conversation_keywords)
        
        # Calculate relevance scores
        if total_content_keywords == 0:
            keyword_relevance = 0.0
        else:
            keyword_relevance = keyword_overlap / total_content_keywords
        
        # Semantic similarity (simplified - could be enhanced with embeddings)
        semantic_relevance = self._calculate_semantic_similarity(extracted_content, conversation_text)
        
        # Combined relevance score
        relevance_score = (keyword_relevance * 0.6) + (semantic_relevance * 0.4)
        
        # Check for off-topic indicators
        off_topic_indicators = self._detect_off_topic_content(extracted_content, conversation_text)
        
        return {
            'relevance_score': relevance_score,
            'keyword_relevance': keyword_relevance,
            'semantic_relevance': semantic_relevance,
            'keyword_overlap': keyword_overlap,
            'total_content_keywords': total_content_keywords,
            'shared_keywords': list(content_keywords.intersection(all_conversation_keywords)),
            'is_relevant': relevance_score >= self.relevance_threshold and not off_topic_indicators,
            'off_topic_indicators': off_topic_indicators,
            'confidence': min(relevance_score * 1.2, 1.0)  # Slight confidence boost
        }
    
    def _extract_keywords(self, text: str) -> Set[str]:
        """Extract meaningful keywords from text"""
        if not text:
            return set()
        
        # Simple keyword extraction (could be enhanced with NLP libraries)
        words = re.findall(r'\b\w+\b', text.lower())
        
        # Filter out common stop words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
            'by', 'from', 'up', 'about', 'into', 'through', 'during', 'before', 'after',
            'above', 'below', 'up', 'down', 'out', 'off', 'over', 'under', 'again', 'further',
            'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any',
            'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor',
            'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 'can', 'will',
            'just', 'don', 'should', 'now', 'i', 'me', 'my', 'myself', 'we', 'our', 'ours',
            'ourselves', 'you', 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his',
            'himself', 'she', 'her', 'hers', 'herself', 'it', 'its', 'itself', 'they', 'them',
            'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that',
            'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'would', 'could',
            'should', 'may', 'might', 'must', 'shall', 'will', 'user', 'said', 'mentioned'
        }
        
        meaningful_words = {word for word in words if len(word) > 2 and word not in stop_words}
        return meaningful_words
    
    def _calculate_semantic_similarity(self, text1: str, text2: str) -> float:
        """Calculate semantic similarity between two texts (simplified)"""
        # This is a simplified approach - could be enhanced with word embeddings
        words1 = self._extract_keywords(text1)
        words2 = self._extract_keywords(text2)
        
        if not words1 or not words2:
            return 0.0
        
        # Jaccard similarity
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0
    
    def _detect_off_topic_content(self, extracted_content: str, conversation_text: str) -> List[str]:
        """Detect if extracted content is off-topic"""
        indicators = []
        
        # Check for completely unrelated topics
        content_lower = extracted_content.lower()
        conversation_lower = conversation_text.lower()
        
        # Common off-topic indicators
        off_topic_patterns = [
            r'\b(completely different|unrelated|random|out of nowhere)\b',
            r'\b(suddenly|meanwhile|in other news|by the way)\b',
            r'\b(example|sample|template|placeholder)\b'
        ]
        
        for pattern in off_topic_patterns:
            if re.search(pattern, content_lower):
                indicators.append(f"Off-topic pattern detected: {pattern}")
        
        # Check if content references things not mentioned in conversation
        content_keywords = self._extract_keywords(extracted_content)
        conversation_keywords = self._extract_keywords(conversation_text)
        
        # Look for major content keywords that have no relation to conversation
        unrelated_keywords = content_keywords - conversation_keywords
        if len(unrelated_keywords) > len(content_keywords) * 0.7:  # More than 70% unrelated
            indicators.append("High percentage of unrelated keywords")
        
        return indicators

class MemoryContentValidator:
    """Validates memory content for accuracy and removes hallucinations"""
    
    def __init__(self):
        self.hallucination_patterns = [
            r'user definitely',
            r'user always',
            r'user never',
            r'user absolutely',
            r'user obviously',
            r'user clearly stated',
            r'user explicitly said',
            r'it is certain that',
            r'without a doubt',
            r'user must have',
            r'user probably',
            r'user likely',
            r'user seems to',
            r'user appears to'
        ]
        
        self.compiled_hallucination_patterns = [re.compile(pattern, re.IGNORECASE) 
                                              for pattern in self.hallucination_patterns]
        
        print("[MemoryContentValidator] 🛡️ Memory content validator initialized")
    
    def validate_memory_content(self, memory_content: str, source_text: str) -> Dict[str, Any]:
        """Validate memory content against source text"""
        
        # Check for hallucination patterns
        hallucination_score = self._detect_hallucinations(memory_content)
        
        # Check for factual consistency
        factual_consistency = self._check_factual_consistency(memory_content, source_text)
        
        # Check for appropriate uncertainty language
        uncertainty_appropriateness = self._check_uncertainty_language(memory_content, source_text)
        
        # Overall validation score
        validation_score = (
            (1.0 - hallucination_score) * 0.4 +
            factual_consistency * 0.4 +
            uncertainty_appropriateness * 0.2
        )
        
        return {
            'validation_score': validation_score,
            'hallucination_score': hallucination_score,
            'factual_consistency': factual_consistency,
            'uncertainty_appropriateness': uncertainty_appropriateness,
            'is_valid': validation_score >= 0.7,
            'confidence': validation_score
        }
    
    def _detect_hallucinations(self, content: str) -> float:
        """Detect hallucination patterns in content"""
        hallucination_count = 0
        total_words = len(content.split())
        
        for pattern in self.compiled_hallucination_patterns:
            matches = pattern.findall(content)
            hallucination_count += len(matches)
        
        # Normalize score
        return min(hallucination_count / max(total_words * 0.1, 1), 1.0)
    
    def _check_factual_consistency(self, memory_content: str, source_text: str) -> float:
        """Check if memory content is factually consistent with source"""
        # Extract factual claims from memory content
        memory_claims = self._extract_factual_claims(memory_content)
        source_claims = self._extract_factual_claims(source_text)
        
        if not memory_claims:
            return 1.0  # No claims to verify
        
        consistent_claims = 0
        for claim in memory_claims:
            if any(self._claims_are_consistent(claim, source_claim) for source_claim in source_claims):
                consistent_claims += 1
        
        return consistent_claims / len(memory_claims)
    
    def _extract_factual_claims(self, text: str) -> List[str]:
        """Extract factual claims from text"""
        # Simple claim extraction - could be enhanced with NLP
        sentences = re.split(r'[.!?]', text)
        claims = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 10 and not sentence.lower().startswith(('i think', 'maybe', 'perhaps')):
                claims.append(sentence)
        
        return claims
    
    def _claims_are_consistent(self, claim1: str, claim2: str) -> bool:
        """Check if two claims are consistent"""
        # Simplified consistency check
        keywords1 = self._extract_keywords(claim1)
        keywords2 = self._extract_keywords(claim2)
        
        overlap = len(keywords1.intersection(keywords2))
        min_keywords = min(len(keywords1), len(keywords2))
        
        return overlap / min_keywords >= 0.5 if min_keywords > 0 else False
    
    def _extract_keywords(self, text: str) -> Set[str]:
        """Extract keywords (reuse from ContentRelevanceValidator)"""
        words = re.findall(r'\b\w+\b', text.lower())
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with'}
        return {word for word in words if len(word) > 2 and word not in stop_words}
    
    def _check_uncertainty_language(self, memory_content: str, source_text: str) -> float:
        """Check if uncertainty language is appropriate"""
        memory_lower = memory_content.lower()
        source_lower = source_text.lower()
        
        # Indicators of uncertainty in source
        uncertainty_indicators = ['maybe', 'perhaps', 'might', 'could', 'possibly', 'probably', 'think', 'guess']
        source_uncertainty = sum(1 for indicator in uncertainty_indicators if indicator in source_lower)
        
        # Certainty language in memory
        certainty_language = ['definitely', 'certainly', 'absolutely', 'clearly', 'obviously']
        memory_certainty = sum(1 for lang in certainty_language if lang in memory_lower)
        
        # If source is uncertain but memory is certain, that's problematic
        if source_uncertainty > 0 and memory_certainty > 0:
            return 0.3  # Low score for inappropriate certainty
        elif source_uncertainty > 0 and memory_certainty == 0:
            return 1.0  # Good - appropriate uncertainty preservation
        else:
            return 0.8  # Neutral

class TemplateSanitizationValidator:
    """Main class that coordinates template sanitization and validation"""
    
    def __init__(self, storage_path: str = "template_validation_log.json"):
        self.storage_path = storage_path
        self.pattern_detector = TemplatePatternDetector()
        self.relevance_validator = ContentRelevanceValidator()
        self.memory_validator = MemoryContentValidator()
        self.validation_log = []
        
        self._load_validation_log()
        
        print("[TemplateSanitizationValidator] 🔧 Template Sanitization & Validation System initialized")
    
    def validate_and_sanitize(self, content: str, conversation_text: str, 
                             conversation_context: str = "", content_type: str = "memory") -> ValidationResult:
        """Main validation and sanitization method"""
        start_time = time.time()
        
        # Step 1: Detect template contamination
        contamination_result = self.pattern_detector.detect_template_contamination(content)
        
        # Step 2: Validate content relevance
        relevance_result = self.relevance_validator.validate_relevance(
            content, conversation_text, conversation_context
        )
        
        # Step 3: Validate memory content (if applicable)
        memory_validation = {}
        if content_type == "memory":
            memory_validation = self.memory_validator.validate_memory_content(content, conversation_text)
        
        # Step 4: Sanitize content
        sanitized_content = self._sanitize_content(content, contamination_result)
        
        # Step 5: Calculate overall validation
        overall_score = self._calculate_overall_score(contamination_result, relevance_result, memory_validation)
        
        # Determine if content is valid
        is_valid = (
            not contamination_result['is_contaminated'] and
            relevance_result['is_relevant'] and
            (memory_validation.get('is_valid', True))
        )
        
        # Collect issues
        issues = []
        if contamination_result['is_contaminated']:
            issues.append(f"Template contamination detected (score: {contamination_result['contamination_score']:.2f})")
        if not relevance_result['is_relevant']:
            issues.append(f"Content not relevant to conversation (score: {relevance_result['relevance_score']:.2f})")
        if memory_validation and not memory_validation.get('is_valid', True):
            issues.append(f"Memory validation failed (score: {memory_validation['validation_score']:.2f})")
        
        # Create validation result
        result = ValidationResult(
            is_valid=is_valid,
            confidence_score=overall_score,
            issues_found=issues,
            sanitized_content=sanitized_content,
            validation_metadata={
                'contamination_result': contamination_result,
                'relevance_result': relevance_result,
                'memory_validation': memory_validation,
                'processing_time': time.time() - start_time,
                'timestamp': datetime.now().isoformat()
            }
        )
        
        # Log validation
        self._log_validation(content, result)
        
        return result
    
    def _sanitize_content(self, content: str, contamination_result: Dict[str, Any]) -> str:
        """Sanitize content by removing template patterns"""
        sanitized = content
        
        # Remove detected template patterns
        for category, patterns in self.pattern_detector.compiled_patterns.items():
            for pattern in patterns:
                sanitized = pattern.sub('[REMOVED]', sanitized)
        
        # Clean up multiple spaces and empty brackets
        sanitized = re.sub(r'\s+', ' ', sanitized)
        sanitized = re.sub(r'\[REMOVED\]\s*', '', sanitized)
        sanitized = sanitized.strip()
        
        return sanitized
    
    def _calculate_overall_score(self, contamination_result: Dict[str, Any], 
                               relevance_result: Dict[str, Any], 
                               memory_validation: Dict[str, Any]) -> float:
        """Calculate overall validation score"""
        contamination_score = 1.0 - contamination_result['contamination_score']
        relevance_score = relevance_result['relevance_score']
        memory_score = memory_validation.get('validation_score', 1.0)
        
        # Weighted average
        overall = (contamination_score * 0.3 + relevance_score * 0.4 + memory_score * 0.3)
        return min(max(overall, 0.0), 1.0)
    
    def _log_validation(self, content: str, result: ValidationResult):
        """Log validation results for analysis"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'content_hash': hashlib.md5(content.encode()).hexdigest(),
            'is_valid': result.is_valid,
            'confidence_score': result.confidence_score,
            'issues_count': len(result.issues_found),
            'issues': result.issues_found
        }
        
        self.validation_log.append(log_entry)
        
        # Keep only last 1000 entries
        if len(self.validation_log) > 1000:
            self.validation_log = self.validation_log[-1000:]
        
        self._save_validation_log()
    
    def _load_validation_log(self):
        """Load validation log from disk"""
        try:
            if Path(self.storage_path).exists():
                with open(self.storage_path, 'r') as f:
                    self.validation_log = json.load(f)
                print(f"[TemplateSanitizationValidator] 📚 Loaded {len(self.validation_log)} validation log entries")
        except Exception as e:
            print(f"[TemplateSanitizationValidator] ⚠️ Could not load validation log: {e}")
    
    def _save_validation_log(self):
        """Save validation log to disk"""
        try:
            with open(self.storage_path, 'w') as f:
                json.dump(self.validation_log, f, indent=2)
        except Exception as e:
            print(f"[TemplateSanitizationValidator] ❌ Could not save validation log: {e}")
    
    def get_validation_statistics(self) -> Dict[str, Any]:
        """Get validation statistics"""
        if not self.validation_log:
            return {}
        
        total_validations = len(self.validation_log)
        valid_count = sum(1 for entry in self.validation_log if entry['is_valid'])
        
        # Calculate average scores and common issues
        avg_confidence = sum(entry['confidence_score'] for entry in self.validation_log) / total_validations
        
        # Common issues
        issue_counts = {}
        for entry in self.validation_log:
            for issue in entry['issues']:
                issue_type = issue.split('(')[0].strip()  # Extract issue type
                issue_counts[issue_type] = issue_counts.get(issue_type, 0) + 1
        
        return {
            'total_validations': total_validations,
            'valid_count': valid_count,
            'invalid_count': total_validations - valid_count,
            'validation_rate': valid_count / total_validations,
            'average_confidence': avg_confidence,
            'common_issues': issue_counts
        }

# Global instance
_template_sanitization_validator = None

def get_template_sanitization_validator() -> TemplateSanitizationValidator:
    """Get the global template sanitization validator instance"""
    global _template_sanitization_validator
    if _template_sanitization_validator is None:
        _template_sanitization_validator = TemplateSanitizationValidator()
    return _template_sanitization_validator

# Convenience functions
def validate_memory_content(content: str, conversation_text: str, conversation_context: str = "") -> ValidationResult:
    """Convenience function to validate memory content"""
    validator = get_template_sanitization_validator()
    return validator.validate_and_sanitize(content, conversation_text, conversation_context, "memory")

def sanitize_template_content(content: str) -> str:
    """Convenience function to sanitize content by removing template patterns"""
    validator = get_template_sanitization_validator()
    result = validator.validate_and_sanitize(content, "", "", "template")
    return result.sanitized_content

def check_content_relevance(content: str, conversation_text: str) -> bool:
    """Convenience function to check if content is relevant to conversation"""
    validator = get_template_sanitization_validator()
    result = validator.validate_and_sanitize(content, conversation_text, "", "general")
    return result.is_valid