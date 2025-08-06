"""
Pattern-First Memory Extractor
Created: 2025-01-22
Purpose: Handle simple memory extraction using pattern recognition before falling back to LLM
"""

import re
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

@dataclass
class PatternExtractionResult:
    """Result from pattern-based extraction"""
    matched: bool
    memory_events: List[Dict[str, Any]]
    intent_classification: str
    emotional_state: Dict[str, Any]
    context_keywords: List[str]
    confidence: float

class PatternMemoryExtractor:
    """Pattern-first memory extraction for common use cases"""
    
    def __init__(self):
        self.location_patterns = [
            # McDonald's specific patterns
            (r'(?:i\s+)?went\s+to\s+mcdonald\'?s?(?:\s+earlier|\s+today)?', self._extract_mcdonalds_visit),
            (r'(?:i\s+)?been\s+to\s+mcdonald\'?s?(?:\s+earlier|\s+today)?', self._extract_mcdonalds_visit),
            (r'(?:i\s+)?visited\s+mcdonald\'?s?(?:\s+earlier|\s+today)?', self._extract_mcdonalds_visit),
            
            # General location patterns
            (r'(?:i\s+)?went\s+to\s+(\w+)(?:\s+earlier|\s+today)?', self._extract_location_visit),
            (r'(?:i\s+)?been\s+to\s+(\w+)(?:\s+earlier|\s+today)?', self._extract_location_visit),
            (r'(?:i\s+)?visited\s+(\w+)(?:\s+earlier|\s+today)?', self._extract_location_visit),
        ]
        
        self.reading_patterns = [
            (r'(?:i\'?ve\s+)?read\s+(?:a\s+)?(\w+)', self._extract_reading_activity),
            (r'(?:i\'?ve\s+)?been\s+reading\s+(?:a\s+)?(\w+)', self._extract_ongoing_reading),
            (r'(?:i\'?m\s+)?reading\s+(?:a\s+)?(\w+)', self._extract_ongoing_reading),
        ]
        
        self.learning_patterns = [
            (r'(?:i\'?m\s+)?learning\s+(\w+)', self._extract_learning_activity),
            (r'(?:i\'?m\s+)?studying\s+(\w+)', self._extract_learning_activity),
        ]
        
        self.planning_patterns = [
            (r'(?:we\'?re\s+)?planning\s+to\s+(?:go\s+on\s+)?(\w+)\s+(next\s+\w+)', self._extract_future_plan),
            (r'(?:we\'?re\s+)?going\s+to\s+(\w+)\s+(next\s+\w+)', self._extract_future_plan),
        ]
    
    def extract_if_pattern_matches(self, text: str) -> Optional[PatternExtractionResult]:
        """Try to extract using patterns first, return None if no pattern matches"""
        text_lower = text.lower().strip()
        
        # Try each pattern type in order of simplicity
        all_patterns = [
            *self.location_patterns,
            *self.reading_patterns, 
            *self.learning_patterns,
            *self.planning_patterns
        ]
        
        for pattern, extractor_func in all_patterns:
            match = re.search(pattern, text_lower)
            if match:
                try:
                    result = extractor_func(text, match)
                    if result.matched:
                        print(f"[PatternExtractor] ✅ Pattern matched: {pattern}")
                        return result
                except Exception as e:
                    print(f"[PatternExtractor] ⚠️ Pattern extraction error: {e}")
                    continue
        
        return None
    
    def _extract_mcdonalds_visit(self, text: str, match: re.Match) -> PatternExtractionResult:
        """Extract McDonald's visit specifically"""
        return PatternExtractionResult(
            matched=True,
            memory_events=[{
                "type": "life_event",
                "topic": "McDonald's visit",
                "date": datetime.now().strftime('%Y-%m-%d'),
                "time": None,
                "emotion": "casual",
                "priority": "medium",
                "people": [],  # No people unless explicitly mentioned
                "location": "McDonald's",
                "details": "visited restaurant",
                "original_text": text,
                "status": "past"
            }],
            intent_classification="statement",
            emotional_state={"primary_emotion": "casual", "confidence": 0.8},
            context_keywords=["mcdonald", "visit", "restaurant"],
            confidence=0.9
        )
    
    def _extract_location_visit(self, text: str, match: re.Match) -> PatternExtractionResult:
        """Extract general location visit"""
        location = match.group(1).capitalize()
        
        return PatternExtractionResult(
            matched=True,
            memory_events=[{
                "type": "life_event", 
                "topic": f"{location} visit",
                "date": datetime.now().strftime('%Y-%m-%d'),
                "time": None,
                "emotion": "casual",
                "priority": "medium",
                "people": [],
                "location": location,
                "details": "visited location",
                "original_text": text,
                "status": "past"
            }],
            intent_classification="statement",
            emotional_state={"primary_emotion": "casual", "confidence": 0.8},
            context_keywords=[location.lower(), "visit"],
            confidence=0.8
        )
    
    def _extract_reading_activity(self, text: str, match: re.Match) -> PatternExtractionResult:
        """Extract reading activity"""
        item = match.group(1)
        
        return PatternExtractionResult(
            matched=True,
            memory_events=[{
                "type": "highlight",
                "topic": f"read {item}",
                "date": datetime.now().strftime('%Y-%m-%d'),
                "time": None,
                "emotion": "casual",
                "priority": "medium",
                "people": [],
                "location": None,
                "details": f"finished reading {item}",
                "original_text": text,
                "status": "past"
            }],
            intent_classification="statement",
            emotional_state={"primary_emotion": "casual", "confidence": 0.8},
            context_keywords=["reading", item],
            confidence=0.9
        )
    
    def _extract_ongoing_reading(self, text: str, match: re.Match) -> PatternExtractionResult:
        """Extract ongoing reading activity"""
        item = match.group(1)
        
        return PatternExtractionResult(
            matched=True,
            memory_events=[{
                "type": "highlight",
                "topic": f"reading {item}",
                "date": datetime.now().strftime('%Y-%m-%d'),
                "time": None,
                "emotion": "casual",
                "priority": "medium",
                "people": [],
                "location": None,
                "details": f"currently reading {item}",
                "original_text": text,
                "status": "current"
            }],
            intent_classification="statement",
            emotional_state={"primary_emotion": "casual", "confidence": 0.8},
            context_keywords=["reading", item],
            confidence=0.9
        )
    
    def _extract_learning_activity(self, text: str, match: re.Match) -> PatternExtractionResult:
        """Extract learning/studying activity"""
        subject = match.group(1)
        
        return PatternExtractionResult(
            matched=True,
            memory_events=[{
                "type": "highlight",
                "topic": f"learning {subject}",
                "date": datetime.now().strftime('%Y-%m-%d'),
                "time": None,
                "emotion": "casual",
                "priority": "medium", 
                "people": [],
                "location": None,
                "details": f"studying {subject}",
                "original_text": text,
                "status": "current"
            }],
            intent_classification="statement",
            emotional_state={"primary_emotion": "casual", "confidence": 0.8},
            context_keywords=["learning", subject],
            confidence=0.9
        )
    
    def _extract_future_plan(self, text: str, match: re.Match) -> PatternExtractionResult:
        """Extract future planning activity"""
        activity = match.group(1)
        time_ref = match.group(2)
        
        return PatternExtractionResult(
            matched=True,
            memory_events=[{
                "type": "appointment",
                "topic": f"{activity} plan",
                "date": datetime.now().strftime('%Y-%m-%d'),
                "time": time_ref,
                "emotion": "excited",
                "priority": "medium",
                "people": [],  # Could be extracted from "we" but keeping simple
                "location": None,
                "details": f"planning to {activity}",
                "original_text": text,
                "status": "future"
            }],
            intent_classification="statement",
            emotional_state={"primary_emotion": "excited", "confidence": 0.8},
            context_keywords=[activity, "planning", time_ref.replace(" ", "_")],
            confidence=0.8
        )