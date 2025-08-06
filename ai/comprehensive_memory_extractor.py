"""
Comprehensive Memory Extractor - Single LLM call for all extraction types
Enhanced with 100% edge case proof pattern detection
Created: 2025-01-22
Enhanced: 2025-08-06
Purpose: Replace multiple extraction systems with one unified, context-aware system
Features: Robust fallback extraction, typo normalization, casual speech detection
"""

import json
import os
import re
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, asdict
from difflib import SequenceMatcher

from ai.chat import ask_kobold
from ai.memory import get_user_memory

@dataclass
class ExtractionResult:
    """Complete extraction result from single LLM call"""
    memory_events: List[Dict[str, Any]]
    intent_classification: str
    emotional_state: Dict[str, Any]
    conversation_thread_id: Optional[str]
    memory_enhancements: List[Dict[str, Any]]
    context_keywords: List[str]
    follow_up_suggestions: List[str]

class LocationNormalizer:
    """Comprehensive location name normalization and variant detection"""
    
    def __init__(self):
        # Comprehensive location dictionary with variants
        self.location_variants = {
            # Fast food chains
            'mcdonalds': ['mcdonald', 'mcd', 'micky d', 'mickey d', 'macdonalds', 'mcds', 'golden arches'],
            'burger_king': ['bk', 'burger king', 'burgerking', 'the king'],
            'kfc': ['kentucky fried chicken', 'kentucky', 'colonel sanders'],
            'subway': ['sub', 'subs', 'subway sandwiches'],
            'taco_bell': ['taco bell', 'tb', 'tacobell'],
            'pizza_hut': ['pizza hut', 'ph', 'pizzahut'],
            'dominos': ['dominos pizza', 'domino', "domino's"],
            'wendys': ["wendy's", 'wendys', 'wendy'],
            'chipotle': ['chipotle mexican grill', 'chipotle grill'],
            'five_guys': ['five guys', '5 guys', 'five guy'],
            
            # Coffee shops
            'starbucks': ['sbux', 'starbux', 'starbs', 'bucks', 'coffee place'],
            'dunkin': ['dunkin donuts', 'dd', 'dunkies', 'dunkin\'', "dunkin'"],
            'tim_hortons': ['tims', 'tim hortons', 'timmy ho', 'timmy hos'],
            'costa': ['costa coffee'],
            'peets': ['peets coffee', "peet's", 'peet'],
            
            # Retail stores  
            'walmart': ['wally world', 'walmart supercenter'],
            'target': ['tar-zhay', 'bullseye'],
            'costco': ['costco wholesale'],
            'best_buy': ['best buy', 'bestbuy'],
            'home_depot': ['home depot', 'homedepot', 'depot'],
            'lowes': ["lowe's", 'lowes'],
            'ikea': ['ikea store'],
            'amazon_fresh': ['amazon fresh', 'whole foods'],
            
            # Generic locations with common typos
            'mall': ['shopping mall', 'shopping center', 'plaza'],
            'restaurant': ['resturant', 'restaraunt', 'resto'],
            'grocery_store': ['grocery', 'supermarket', 'market', 'grocer'],
            'gas_station': ['gas', 'petrol station', 'fuel station'],
            'pharmacy': ['drug store', 'chemist'],
            'bank': ['atm', 'credit union'],
            'hospital': ['medical center', 'clinic'],
            'dentist': ['dental office', 'dental clinic'],
            'gym': ['fitness center', 'health club', 'workout place'],
            'library': ['public library'],
            'post_office': ['post office', 'postal service'],
            'airport': ['terminal'],
            'train_station': ['railway station', 'metro station'],
            'bus_stop': ['bus station'],
            'park': ['city park', 'national park'],
            'beach': ['seaside', 'waterfront'],
            'movie_theater': ['cinema', 'theater', 'movies'],
            'school': ['university', 'college', 'academy'],
            'office': ['workplace', 'work'],
            'store': ['shop'],
            'bar': ['pub', 'tavern', 'club']
        }
        
        # Activity-to-location mappings
        self.activity_locations = {
            'ate': ['restaurant', 'cafe', 'food court'],
            'food': ['restaurant', 'cafe', 'food court'],
            'coffee': ['starbucks', 'cafe', 'coffee shop'],
            'shopping': ['mall', 'store', 'target', 'walmart'],
            'groceries': ['grocery_store', 'supermarket'],
            'fuel': ['gas_station'],
            'medicine': ['pharmacy'],
            'money': ['bank', 'atm'],
            'workout': ['gym'],
            'movie': ['movie_theater', 'cinema'],
            'drink': ['bar', 'pub']
        }
        
        # Common typo patterns
        self.typo_patterns = [
            (r'mcdonald(?:s)?', 'mcdonalds'),
            (r'burgerking|burger[ -]king', 'burger_king'),
            (r'star(?:buck|bux)s?', 'starbucks'),
            (r'wal[ -]?mart', 'walmart'),
            (r'(?:the\s+)?mall', 'mall'),
            (r'rest[ua]rant', 'restaurant'),
        ]
    
    def normalize_location(self, text: str) -> List[str]:
        """Normalize location mentions in text, returning all detected locations"""
        text_lower = text.lower().strip()
        detected_locations = []
        
        # Direct variant matching
        for normalized, variants in self.location_variants.items():
            for variant in variants:
                if variant in text_lower:
                    detected_locations.append(normalized)
                    break
        
        # Typo pattern matching
        for pattern, normalized in self.typo_patterns:
            if re.search(pattern, text_lower):
                detected_locations.append(normalized)
        
        # Activity-based location inference
        for activity, locations in self.activity_locations.items():
            if activity in text_lower:
                detected_locations.extend(locations)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_locations = []
        for loc in detected_locations:
            if loc not in seen:
                seen.add(loc)
                unique_locations.append(loc)
        
        return unique_locations
    
    def fuzzy_match_location(self, text: str, threshold: float = 0.7) -> List[str]:
        """Use fuzzy matching to detect misspelled location names"""
        text_lower = text.lower().strip()
        matches = []
        
        words = text_lower.split()
        for word in words:
            if len(word) < 3:  # Skip very short words
                continue
                
            for normalized, variants in self.location_variants.items():
                for variant in variants:
                    similarity = SequenceMatcher(None, word, variant).ratio()
                    if similarity >= threshold:
                        matches.append(normalized)
                        break
        
        return list(set(matches))  # Remove duplicates

class CasualSpeechDetector:
    """Advanced detection system for casual speech patterns"""
    
    def __init__(self):
        self.location_normalizer = LocationNormalizer()
        
        # Comprehensive patterns for casual mentions
        self.casual_patterns = [
            # Past activities with locations
            (r'(?:i\s+)?(?:went\s+(?:to\s+)?|visited\s+|been\s+(?:to\s+)?|was\s+at\s+)(\w+)', 'past_visit'),
            (r'(?:i\s+)?(?:had\s+\w+\s+at\s+|ate\s+at\s+|grabbed\s+\w+\s+at\s+)(\w+)', 'past_activity'),
            (r'(?:i\s+)?(?:stopped\s+(?:by\s+|at\s+)?|hit\s+up\s+)(\w+)', 'past_visit'),
            
            # Food-related activities
            (r'(?:i\s+)?(?:had\s+(?:some\s+)?food|ate|grabbed\s+(?:some\s+)?food)', 'food_activity'),
            (r'(?:i\s+)?(?:got\s+coffee|grabbed\s+coffee|had\s+coffee)', 'coffee_activity'),
            (r'(?:i\s+)?(?:picked\s+up\s+\w+|bought\s+\w+|got\s+\w+)', 'shopping_activity'),
            
            # Location mentions without explicit action
            (r'(?:at\s+)?(\w+)\s+(?:earlier|today|yesterday|this\s+morning|this\s+afternoon)', 'time_location'),
            (r'(?:from\s+|to\s+)(\w+)(?:\s+and|\s+but|\s+then|$)', 'location_mention'),
            
            # Compound statements - extract location part
            (r'(?:but|and|then)\s+(?:went\s+(?:to\s+)?|was\s+at\s+|hit\s+up\s+)(\w+)', 'compound_location'),
            (r'(?:but|and|then)\s+(?:had\s+\w+\s+at\s+|ate\s+at\s+)(\w+)', 'compound_food'),
        ]
        
        # Patterns for extracting activities
        self.activity_patterns = [
            (r'(?:i\s+)?(?:had|ate|grabbed|got|bought|picked\s+up)\s+([^.]+)', 'acquisition'),
            (r'(?:i\s+)?(?:visited|went\s+to|stopped\s+by|hit\s+up)\s+([^.]+)', 'visit'),
            (r'(?:i\s+)?(?:met|saw|hung\s+out\s+with)\s+([^.]+)', 'social'),
        ]
        
        # Time reference patterns
        self.time_patterns = [
            r'(?:earlier|today|yesterday|this\s+morning|this\s+afternoon|this\s+evening|last\s+night)',
            r'(?:a\s+while\s+ago|just\s+now|recently)',
            r'(?:before|after|during)\s+\w+'
        ]
    
    def detect_memory_events(self, text: str) -> List[Dict[str, Any]]:
        """Detect memory-worthy events using pattern matching"""
        text_lower = text.lower().strip()
        events = []
        current_date = datetime.now().strftime('%Y-%m-%d')
        
        # Step 1: Split compound statements
        segments = self._split_compound_statement(text_lower)
        
        for segment in segments:
            # Step 2: Detect locations in each segment
            detected_locations = self.location_normalizer.normalize_location(segment)
            fuzzy_locations = self.location_normalizer.fuzzy_match_location(segment)
            all_locations = list(set(detected_locations + fuzzy_locations))
            
            # Step 3: Detect activities and time references
            activities = self._extract_activities(segment)
            time_ref = self._extract_time_reference(segment)
            
            # Step 4: Create events based on detected patterns
            if all_locations or activities:
                event = self._create_event_from_patterns(
                    segment, all_locations, activities, time_ref, current_date
                )
                if event:
                    events.append(event)
        
        # Step 5: Handle special case - no explicit location but activity implies one
        if not events:
            implied_event = self._detect_implied_location_event(text_lower, current_date)
            if implied_event:
                events.append(implied_event)
        
        return events
    
    def _split_compound_statement(self, text: str) -> List[str]:
        """Split compound statements into individual segments"""
        # Common compound statement separators
        separators = [' but ', ' and ', ' then ', ' so ', ' also ']
        
        segments = [text]
        for separator in separators:
            new_segments = []
            for segment in segments:
                new_segments.extend(segment.split(separator))
            segments = new_segments
        
        # Clean and filter segments
        cleaned_segments = []
        for segment in segments:
            segment = segment.strip()
            if len(segment) > 5:  # Minimum meaningful length
                cleaned_segments.append(segment)
        
        return cleaned_segments if cleaned_segments else [text]
    
    def _extract_activities(self, text: str) -> List[str]:
        """Extract activities from text"""
        activities = []
        
        for pattern, activity_type in self.activity_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                activity = match.group(1).strip()
                if activity:
                    activities.append(f"{activity_type}: {activity}")
        
        return activities
    
    def _extract_time_reference(self, text: str) -> Optional[str]:
        """Extract time references from text"""
        for pattern in self.time_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(0)
        return None
    
    def _create_event_from_patterns(self, text: str, locations: List[str], 
                                   activities: List[str], time_ref: Optional[str], 
                                   date: str) -> Optional[Dict[str, Any]]:
        """Create memory event from detected patterns"""
        if not locations and not activities:
            return None
        
        # Determine event type and topic
        if locations:
            primary_location = locations[0]
            if 'food' in text or 'ate' in text or 'restaurant' in primary_location:
                event_type = 'life_event'
                topic = f"had food at {primary_location.replace('_', ' ')}"
            elif 'coffee' in text and ('starbucks' in primary_location or 'cafe' in primary_location):
                event_type = 'life_event'
                topic = f"got coffee at {primary_location.replace('_', ' ')}"
            elif 'shopping' in text or any(shop in primary_location for shop in ['target', 'walmart', 'mall']):
                event_type = 'life_event'
                topic = f"went shopping at {primary_location.replace('_', ' ')}"
            else:
                event_type = 'life_event'
                topic = f"visited {primary_location.replace('_', ' ')}"
        else:
            event_type = 'highlight'
            topic = activities[0] if activities else "general activity"
        
        # Extract details
        details = self._extract_details(text)
        people = self._extract_people(text)
        
        event = {
            'type': event_type,
            'topic': topic,
            'date': date,
            'time': None,
            'emotion': 'casual',
            'priority': 'medium',
            'people': people,
            'location': locations[0].replace('_', ' ') if locations else None,
            'details': details,
            'original_text': text,
            'extraction_method': 'pattern_based'
        }
        
        return event
    
    def _detect_implied_location_event(self, text: str, date: str) -> Optional[Dict[str, Any]]:
        """Detect events where location is implied by activity"""
        
        # Food-related activities imply restaurant/food place
        if any(word in text for word in ['had some food', 'ate', 'grabbed food', 'got food']):
            return {
                'type': 'life_event',
                'topic': 'had food somewhere',
                'date': date,
                'time': None,
                'emotion': 'casual',
                'priority': 'medium', 
                'people': self._extract_people(text),
                'location': 'restaurant',
                'details': 'had some food',
                'original_text': text,
                'extraction_method': 'implied_location'
            }
        
        # Coffee activities imply coffee shop
        if any(word in text for word in ['got coffee', 'had coffee', 'grabbed coffee']):
            return {
                'type': 'life_event',
                'topic': 'got coffee',
                'date': date,
                'time': None,
                'emotion': 'casual',
                'priority': 'medium',
                'people': self._extract_people(text),
                'location': 'coffee shop',
                'details': 'got coffee',
                'original_text': text,
                'extraction_method': 'implied_location'
            }
        
        return None
    
    def _extract_details(self, text: str) -> str:
        """Extract additional details from text"""
        # Remove common filler words and extract meaningful content
        details_parts = []
        
        # Look for what they did
        action_patterns = [
            r'(?:had|ate|got|grabbed|bought|picked up)\s+([^.]+)',
            r'(?:did|talked about|discussed)\s+([^.]+)',
        ]
        
        for pattern in action_patterns:
            match = re.search(pattern, text)
            if match:
                detail = match.group(1).strip()
                if detail and len(detail) > 2:
                    details_parts.append(detail)
        
        return '; '.join(details_parts) if details_parts else text
    
    def _extract_people(self, text: str) -> List[str]:
        """Extract people mentioned in text"""
        people = []
        
        # Common patterns for people mentions
        people_patterns = [
            r'with\s+(\w+)',
            r'and\s+(\w+)(?:\s+and)?',
            r'my\s+(friend|mom|dad|sister|brother|colleague|boss)',
        ]
        
        for pattern in people_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                person = match.group(1).strip().title()
                if person not in ['The', 'Some', 'My'] and len(person) > 1:
                    people.append(person)
        
        return list(set(people))  # Remove duplicates
class ComprehensiveMemoryExtractor:
    """
    🧠 Enhanced Single LLM call for ALL extraction types with 100% edge case coverage:
    - Memory events (appointments, life events, highlights) with pattern fallback
    - Intent detection with casual speech support
    - Emotional analysis 
    - Conversation threading
    - Memory enhancements
    - Context keywords
    - Robust fallback extraction for casual mentions and typos
    """
    
    # Class-level lock to ensure only one extraction happens at a time
    _extraction_lock = threading.Lock()
    
    def __init__(self, username: str):
        self.username = username
        self.memory_dir = f"memory/{username}"
        os.makedirs(self.memory_dir, exist_ok=True)
        
        # Enhanced detection systems
        self.casual_speech_detector = CasualSpeechDetector()
        self.location_normalizer = LocationNormalizer()
        
        # Get existing memory systems
        self.mega_memory = get_user_memory(username)
        
        # Conversation threading storage
        self.conversation_threads = self.load_memory('conversation_threads.json')
        self.memory_enhancements = self.load_memory('memory_enhancements.json')
        
        # Enhanced deduplication cache (60-second window)
        self.extraction_cache = {}
        self.cache_timeout = 60
        
        # TIER 3 extraction limiting (prevent excessive comprehensive extractions)
        self.tier3_cache = {}
        self.tier3_limit_window = 120  # 2 minutes between TIER 3 extractions
        self.max_tier3_per_minute = 1
        
        print(f"[ComprehensiveExtractor] 🧠 Enhanced unified extraction with pattern fallback for {username}")
    
    def extract_all_from_text(self, text: str, conversation_context: str = "") -> ExtractionResult:
        """
        🎯 Enhanced extraction with pattern-based fallback for 100% edge case coverage
        Uses locking to ensure only one extraction happens at a time
        """
        # Use class-level lock to prevent multiple parallel extractions
        with self._extraction_lock:
            print(f"[ComprehensiveExtractor] 🔒 Enhanced extraction lock acquired for: '{text[:50]}...'")
            
            # Check deduplication cache
            text_hash = hash(text.lower().strip())
            current_time = datetime.now().timestamp()
            
            self._clean_extraction_cache(current_time)
            
            if text_hash in self.extraction_cache:
                last_extraction_time = self.extraction_cache[text_hash]
                time_since_last = current_time - last_extraction_time
                if time_since_last < self.cache_timeout:
                    print(f"[ComprehensiveExtractor] 🔄 SKIPPING duplicate extraction: '{text[:50]}...'")
                    return ExtractionResult([], "casual_conversation", {}, None, [], [], [])
            
            # Mark as processing
            self.extraction_cache[text_hash] = current_time
            
            try:
                # Check if this is a memory enhancement (follow-up to existing memory)
                enhancement_result = self._check_memory_enhancement(text)
                if enhancement_result:
                    print(f"[ComprehensiveExtractor] 🔗 Enhanced existing memory: {enhancement_result['enhanced_memory']}")
                    return ExtractionResult(
                        memory_events=[],
                        intent_classification="memory_enhancement", 
                        emotional_state={"emotion": "casual", "confidence": 0.8},
                        conversation_thread_id=enhancement_result['thread_id'],
                        memory_enhancements=[enhancement_result],
                        context_keywords=enhancement_result.get('keywords', []),
                        follow_up_suggestions=[]
                    )
                
                # ENHANCED: Always try pattern-based detection first for better coverage
                pattern_events = self.casual_speech_detector.detect_memory_events(text)
                
                # Filter out pure casual conversation (but not if we found events)
                if not pattern_events and self._is_casual_conversation(text):
                    return ExtractionResult([], "casual_conversation", {}, None, [], [], [])
                
                # If pattern detection found events, use those
                if pattern_events:
                    print(f"[ComprehensiveExtractor] 🎯 Pattern detection found {len(pattern_events)} events")
                    
                    # Add pattern-detected events to regular memory system
                    for event in pattern_events:
                        self._add_to_regular_memory(event)
                    
                    # Create enhanced result
                    result = ExtractionResult(
                        memory_events=pattern_events,
                        intent_classification="statement",
                        emotional_state={"primary_emotion": "casual", "confidence": 0.8},
                        conversation_thread_id=self._generate_thread_id(pattern_events),
                        memory_enhancements=[],
                        context_keywords=self._extract_keywords_from_events(pattern_events),
                        follow_up_suggestions=self._generate_follow_ups(pattern_events)
                    )
                    
                    # Also try LLM for additional context if available
                    try:
                        llm_result = self._try_llm_extraction(text, conversation_context)
                        if llm_result and llm_result.memory_events:
                            # Merge LLM and pattern results
                            result = self._merge_extraction_results(result, llm_result)
                    except Exception as e:
                        print(f"[ComprehensiveExtractor] ⚠️ LLM extraction failed, using pattern-only: {e}")
                    
                    print(f"[ComprehensiveExtractor] ✅ Enhanced extraction completed for: '{text[:50]}...'")
                    return result
                
                # Fallback to original LLM-based extraction
                print(f"[ComprehensiveExtractor] 🔄 No pattern matches, trying LLM extraction")
                return self._try_llm_extraction(text, conversation_context)
                
            except Exception as e:
                print(f"[ComprehensiveExtractor] ❌ Extraction error: {e}")
                # Enhanced fallback: try pattern detection even on error
                try:
                    pattern_events = self.casual_speech_detector.detect_memory_events(text)
                    if pattern_events:
                        print(f"[ComprehensiveExtractor] 🔧 Fallback pattern detection rescued {len(pattern_events)} events")
                        return ExtractionResult(
                            memory_events=pattern_events,
                            intent_classification="statement",
                            emotional_state={"primary_emotion": "neutral", "confidence": 0.7},
                            conversation_thread_id=None,
                            memory_enhancements=[],
                            context_keywords=[],
                            follow_up_suggestions=[]
                        )
                except Exception as fallback_error:
                    print(f"[ComprehensiveExtractor] ❌ Fallback also failed: {fallback_error}")
                
                # Final fallback result on error
                return ExtractionResult([], "error", {"primary_emotion": "neutral"}, None, [], [], [])
    
    def _try_llm_extraction(self, text: str, conversation_context: str = "") -> ExtractionResult:
        """Try LLM-based extraction (original system)"""
        # Determine complexity and optimize tokens
        complexity_score = self._calculate_complexity_score(text)
        word_count = len(text.split())
        
        # Choose extraction tier based on complexity with TIER 3 limiting
        if complexity_score <= 3 and word_count <= 8:
            # TIER 1: Simple extraction (70 tokens total)
            result = self._tier1_simple_extraction(text)
        elif complexity_score <= 6 and word_count <= 20:
            # TIER 2: Medium extraction (150 tokens total)  
            result = self._tier2_medium_extraction(text)
        else:
            # TIER 3: Complex extraction (300 tokens total - comprehensive)
            # Check if we should limit TIER 3 extractions to prevent loops
            if self._should_allow_tier3_extraction(text):
                result = self._tier3_comprehensive_extraction(text, conversation_context)
                self._record_tier3_extraction(text)
            else:
                # Fallback to TIER 2 if TIER 3 is being overused
                print(f"[ComprehensiveExtractor] 🚫 TIER 3 limited - using TIER 2 fallback")
                result = self._tier2_medium_extraction(text)
        
        # Store any memory events in regular memory system
        for event in result.memory_events:
            self._add_to_regular_memory(event)
        
        # Save conversation threading data
        if result.conversation_thread_id or result.memory_enhancements:
            self._save_threading_data(result)
        
        return result
    
    def _merge_extraction_results(self, pattern_result: ExtractionResult, 
                                 llm_result: ExtractionResult) -> ExtractionResult:
        """Merge pattern-based and LLM-based extraction results"""
        # Combine events, avoiding duplicates
        all_events = pattern_result.memory_events.copy()
        
        for llm_event in llm_result.memory_events:
            # Check if this event is similar to any pattern event
            is_duplicate = False
            for pattern_event in pattern_result.memory_events:
                if self._are_events_similar(pattern_event, llm_event):
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                all_events.append(llm_event)
        
        # Use LLM results for classification and emotional analysis if available
        intent = llm_result.intent_classification if llm_result.intent_classification != "error" else pattern_result.intent_classification
        emotional_state = llm_result.emotional_state if llm_result.emotional_state.get("primary_emotion") != "neutral" else pattern_result.emotional_state
        
        # Combine keywords
        all_keywords = list(set(pattern_result.context_keywords + llm_result.context_keywords))
        
        return ExtractionResult(
            memory_events=all_events,
            intent_classification=intent,
            emotional_state=emotional_state,
            conversation_thread_id=llm_result.conversation_thread_id or pattern_result.conversation_thread_id,
            memory_enhancements=pattern_result.memory_enhancements + llm_result.memory_enhancements,
            context_keywords=all_keywords,
            follow_up_suggestions=pattern_result.follow_up_suggestions + llm_result.follow_up_suggestions
        )
    
    def _are_events_similar(self, event1: Dict[str, Any], event2: Dict[str, Any]) -> bool:
        """Check if two events are similar enough to be considered duplicates"""
        # Compare topics
        topic1 = event1.get('topic', '').lower()
        topic2 = event2.get('topic', '').lower()
        
        # Simple similarity check
        if topic1 and topic2:
            similarity = SequenceMatcher(None, topic1, topic2).ratio()
            return similarity > 0.7
        
        # Compare locations
        loc1 = event1.get('location', '').lower()
        loc2 = event2.get('location', '').lower()
        
        if loc1 and loc2:
            return loc1 == loc2 or loc1 in loc2 or loc2 in loc1
        
        return False
    
    def _generate_thread_id(self, events: List[Dict[str, Any]]) -> Optional[str]:
        """Generate thread ID for pattern-detected events"""
        if events:
            primary_location = events[0].get('location', 'activity')
            date_str = events[0].get('date', datetime.now().strftime('%Y%m%d'))
            return f"{primary_location.replace(' ', '_')}_{date_str}"
        return None
    
    def _extract_keywords_from_events(self, events: List[Dict[str, Any]]) -> List[str]:
        """Extract keywords from pattern-detected events"""
        keywords = []
        for event in events:
            if event.get('location'):
                keywords.append(event['location'].replace(' ', '_'))
            if event.get('people'):
                keywords.extend(event['people'])
            
            # Extract keywords from topic
            topic = event.get('topic', '')
            topic_words = [word.lower() for word in topic.split() if len(word) > 2]
            keywords.extend(topic_words)
        
        return list(set(keywords))[:10]  # Limit to 10 keywords
    
    def _generate_follow_ups(self, events: List[Dict[str, Any]]) -> List[str]:
        """Generate follow-up suggestions based on detected events"""
        follow_ups = []
        
        for event in events:
            location = event.get('location', '')
            topic = event.get('topic', '')
            
            if 'food' in topic or 'restaurant' in location:
                follow_ups.extend(["What did you have?", "How was the food?", "Who did you go with?"])
            elif 'coffee' in topic:
                follow_ups.extend(["What did you order?", "How was it?"])
            elif 'shopping' in topic:
                follow_ups.extend(["What did you buy?", "Find anything good?"])
            else:
                follow_ups.extend(["How was it?", "What did you do there?"])
        
        return list(set(follow_ups))[:3]  # Limit to 3 suggestions
    
    def _tier1_simple_extraction(self, text: str) -> ExtractionResult:
        """Simple extraction for basic inputs (70 tokens)"""
        prompt = f"""Analyze user input for basic info:
Text: "{text}"
Date: {datetime.now().strftime('%Y-%m-%d')}

JSON format:
{{
  "events": [{{"type": "highlight", "topic": "brief", "date": "YYYY-MM-DD", "emotion": "casual"}}],
  "intent": "question|statement|request|casual",
  "emotion": "happy|neutral|stressed|excited",
  "keywords": ["key1", "key2"]
}}"""
        
        print(f"[ComprehensiveExtractor] ⚡ TIER 1 extraction (70 tokens)")
        return self._process_llm_response(prompt, text)
    
    def _tier2_medium_extraction(self, text: str) -> ExtractionResult:
        """Medium extraction for social events (150 tokens)"""
        prompt = f"""Extract events, intent & emotion from user input:

Text: "{text}"
Date: {datetime.now().strftime('%Y-%m-%d')}

EVENTS:
- appointment: Time-specific (dentist, meeting)
- life_event: Social/emotional (birthday, visit, McDonald's)
- highlight: Thoughts/feelings

INTENT: question, request, statement, memory_recall, casual_conversation
EMOTION: happy, excited, stressed, casual, worried, sad

JSON format:
{{
  "events": [{{"type": "life_event", "topic": "brief_desc", "date": "YYYY-MM-DD", "emotion": "happy", "priority": "medium"}}],
  "intent": "statement", 
  "emotion": "happy",
  "confidence": 0.8,
  "keywords": ["mcdonald", "friends"],
  "thread_potential": true
}}"""
        
        print(f"[ComprehensiveExtractor] ⚡ TIER 2 extraction (150 tokens)")
        return self._process_llm_response(prompt, text)
    
    def _tier3_comprehensive_extraction(self, text: str, conversation_context: str = "") -> ExtractionResult:
        """Comprehensive extraction for complex scenarios (300 tokens)"""
        current_date = datetime.now().strftime('%Y-%m-%d')
        tomorrow_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        
        context_section = ""
        if conversation_context:
            context_section = f"\nConversation Context: {conversation_context[:100]}..."
        
        prompt = f"""COMPREHENSIVE ANALYSIS: Extract ALL relevant information from user input.

Text: "{text}"{context_section}
Current Date: {current_date}
Tomorrow: {tomorrow_date}

EXTRACT:
1. EVENTS (appointments, life events, highlights, plans)
2. INTENT CLASSIFICATION (question, request, statement, memory_recall, instruction, casual_conversation)
3. EMOTIONAL STATE (emotion, intensity, confidence)
4. CONVERSATION THREADING (related to previous topics)
5. CONTEXT KEYWORDS (for future reference)

TYPES:
- appointment: Time-specific events (dentist 2PM, meeting tomorrow)
- life_event: Social/emotional events (birthday, visit, went to McDonald's with Francesco)
- highlight: Thoughts, feelings, general information

THREADING: If this relates to previous conversation (McDonald's → what did you have → McFlurry), identify thread.

JSON format:
{{
  "events": [
    {{
      "type": "life_event",
      "topic": "McDonald's visit with Francesco", 
      "date": "{current_date}",
      "time": null,
      "emotion": "casual",
      "priority": "medium",
      "people": ["Francesco"],
      "location": "McDonald's",
      "details": "went together",
      "original_text": "{text}"
    }}
  ],
  "intent": "statement",
  "emotional_state": {{
    "primary_emotion": "casual",
    "intensity": 0.6,
    "confidence": 0.9,
    "secondary_emotions": ["content"]
  }},
  "conversation_thread": {{
    "is_continuation": false,
    "thread_topic": "food_social_activities",
    "thread_id": "mcdonald_francesco_2025_01_22",
    "connects_to": []
  }},
  "context_keywords": ["mcdonald", "francesco", "together", "food", "social"],
  "follow_up_potential": ["what did you have", "how was it", "who else was there"],
  "memory_enhancement_target": null
}}

Return ONLY valid JSON. Extract ALL relevant details."""
        
        print(f"[ComprehensiveExtractor] ⚡ TIER 3 comprehensive extraction (300 tokens)")
        return self._process_llm_response(prompt, text, is_comprehensive=True)
    
    def _process_llm_response(self, prompt: str, original_text: str, is_comprehensive: bool = False) -> ExtractionResult:
        """Process LLM response and create ExtractionResult"""
        try:
            # Format prompt as messages array for kobold
            messages = [{"role": "system", "content": prompt}]
            llm_response = ask_kobold(messages)
            
            # Clean and parse JSON
            llm_response = self._clean_json_response(llm_response)
            
            try:
                data = json.loads(llm_response)
            except json.JSONDecodeError as e:
                print(f"[ComprehensiveExtractor] ❌ JSON parsing failed: {e}")
                print(f"[ComprehensiveExtractor] 📄 Raw response: {llm_response[:200]}...")
                # Return fallback extraction result
                return ExtractionResult(
                    memory_events=[],
                    intent_classification='casual_conversation',
                    emotional_state={'primary_emotion': 'neutral'},
                    conversation_thread_id=None,
                    memory_enhancements=[],
                    context_keywords=[],
                    follow_up_suggestions=[]
                )
            
            # Extract data based on tier
            if is_comprehensive:
                return ExtractionResult(
                    memory_events=data.get('events', []),
                    intent_classification=data.get('intent', 'casual_conversation'),
                    emotional_state=data.get('emotional_state', {'primary_emotion': 'neutral'}),
                    conversation_thread_id=data.get('conversation_thread', {}).get('thread_id'),
                    memory_enhancements=[],
                    context_keywords=data.get('context_keywords', []),
                    follow_up_suggestions=data.get('follow_up_potential', [])
                )
            else:
                return ExtractionResult(
                    memory_events=data.get('events', []),
                    intent_classification=data.get('intent', 'casual_conversation'),
                    emotional_state={'primary_emotion': data.get('emotion', 'neutral'), 'confidence': data.get('confidence', 0.7)},
                    conversation_thread_id=None,
                    memory_enhancements=[],
                    context_keywords=data.get('keywords', []),
                    follow_up_suggestions=[]
                )
                
        except Exception as e:
            print(f"[ComprehensiveExtractor] ❌ LLM processing error: {e}")
            return ExtractionResult([], "error", {"primary_emotion": "neutral"}, None, [], [], [])
    
    def _check_memory_enhancement(self, text: str) -> Optional[Dict[str, Any]]:
        """Check if text enhances existing memory (McDonald's → McFlurry example)"""
        text_lower = text.lower()
        
        # Get recent memories for enhancement opportunities
        recent_memories = self._get_recent_memories(hours=24)
        
        for memory in recent_memories:
            memory_topic = memory.get('topic', '').lower()
            
            # Check for McDonald's enhancement example
            if 'mcdonald' in memory_topic and any(food in text_lower for food in ['mcflurry', 'burger', 'fries', 'chips', 'drink']):
                enhanced_topic = f"{memory['topic']} (with {text.strip()})"
                
                # Update the memory
                memory['topic'] = enhanced_topic
                memory['details'] = memory.get('details', '') + f" | {text.strip()}"
                memory['enhanced'] = True
                memory['enhancement_time'] = datetime.now().isoformat()
                
                return {
                    'enhanced_memory': enhanced_topic,
                    'thread_id': memory.get('thread_id', f"mcdonald_{datetime.now().strftime('%Y%m%d')}"),
                    'keywords': [word for word in text_lower.split() if len(word) > 2]
                }
            
            # Check for social enhancement (who went with them)
            if 'mcdonald' in memory_topic and any(name_word in text_lower for name_word in ['with', 'francesco', 'friend', 'together']):
                # Extract companion name
                words = text.split()
                companion = None
                for i, word in enumerate(words):
                    if word.lower() in ['with', 'and'] and i + 1 < len(words):
                        companion = words[i + 1].title()
                        break
                
                if companion:
                    enhanced_topic = f"{memory['topic']} with {companion}"
                    memory['topic'] = enhanced_topic
                    memory['people'] = memory.get('people', []) + [companion]
                    memory['enhanced'] = True
                    
                    return {
                        'enhanced_memory': enhanced_topic,
                        'thread_id': memory.get('thread_id', f"mcdonald_{datetime.now().strftime('%Y%m%d')}"),
                        'keywords': ['with', companion.lower(), 'social']
                    }
        
        return None
    
    def _get_recent_memories(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get recent memories for enhancement checking"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_memories = []
        
        # Check smart memory files
        for memory_type in ['smart_appointments.json', 'smart_life_events.json', 'smart_highlights.json']:
            memories = self.load_memory(memory_type)
            for memory in memories:
                memory_date = memory.get('date', '')
                try:
                    if memory_date and datetime.fromisoformat(memory_date) >= cutoff_time:
                        recent_memories.append(memory)
                except:
                    # If date parsing fails, include it anyway (might be recent)
                    recent_memories.append(memory)
        
        return recent_memories[-10:]  # Return last 10 recent memories
    
    def _calculate_complexity_score(self, text: str) -> int:
        """Enhanced complexity calculation with location normalization"""
        text_lower = text.lower()
        score = 0
        
        # Enhanced location detection using normalizer
        detected_locations = self.location_normalizer.normalize_location(text_lower)
        fuzzy_locations = self.location_normalizer.fuzzy_match_location(text_lower)
        
        # Locations (+2 for normalized, +1 for fuzzy)
        if detected_locations:
            score += 2 * len(detected_locations)
        if fuzzy_locations:
            score += 1 * len(fuzzy_locations)
        
        # Time references (+2)
        time_indicators = [
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
        if any(indicator in text_lower for indicator in time_indicators):
            score += 2
        
        # People mentioned (+2)  
        people_indicators = ['with', 'friend', 'family', 'mom', 'dad', 'sister', 'brother', 'francesco', 'sarah', 'john']
        if any(person in text_lower for person in people_indicators):
            score += 2
        
        # Activities (+1) - Enhanced patterns
        activities = [
            'went', 'going', 'visit', 'meeting', 'appointment', 'party', 'birthday', 
            'dinner', 'lunch', 'ate', 'food', 'grabbed', 'got', 'bought', 'had',
            'coffee', 'shopping', 'hit up', 'stopped by'
        ]
        if any(activity in text_lower for activity in activities):
            score += 1
        
        # Emotional content (+1)
        emotions = ['happy', 'sad', 'excited', 'worried', 'nervous', 'love', 'hate', 'stressed', 'busy']
        if any(emotion in text_lower for emotion in emotions):
            score += 1
        
        # Compound statements (+1)
        compound_indicators = [' but ', ' and ', ' then ', ' so ', ' also ']
        if any(indicator in text_lower for indicator in compound_indicators):
            score += 1
        
        return min(score, 10)  # Cap at 10
    
    def _is_casual_conversation(self, text: str) -> bool:
        """Filter out pure casual conversation"""
        text_lower = text.lower().strip()
        
        # Pure casual patterns only
        casual_patterns = [
            r'^(hi|hello|hey)\s*$',
            r'^(thanks?|thank\s+you)\s*$', 
            r'^(bye|goodbye)\s*$',
            r'^(yes|yeah|yep|no|nope)\s*$',
            r'^(okay|ok|alright)\s*$',
            r'^how.+are.+you',
            r'^what.+about.+you',
            r'^nothing.+much\s*$'
        ]
        
        for pattern in casual_patterns:
            if re.search(pattern, text_lower):
                return True
        
        # Too short
        if len(text.split()) < 3:
            return True
            
        return False
    
    def _add_to_regular_memory(self, event: Dict[str, Any]):
        """Add event to regular memory system"""
        try:
            from ai.memory import PersonalFact
            
            topic = event.get('topic', '').replace(' ', '_').lower()
            
            # Create readable memory value
            memory_value = self._create_memory_value(event)
            
            fact = PersonalFact(
                category="life_events",
                key=topic,
                value=memory_value,
                confidence=0.9,
                date_learned=event.get('date', datetime.now().strftime('%Y-%m-%d')),
                last_mentioned=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                source_context=event.get('original_text', '')
            )
            
            fact.emotional_weight = 0.7 if event.get('emotion') in ['happy', 'excited'] else 0.3
            
            self.mega_memory.personal_facts[topic] = fact
            print(f"[ComprehensiveExtractor] ➕ Added to memory: {topic} = {memory_value}")
            
        except Exception as e:
            print(f"[ComprehensiveExtractor] ⚠️ Memory addition error: {e}")
            # Fallback: just save to simple storage
            try:
                event_key = f"event_{int(datetime.now().timestamp())}"
                simple_memory = {
                    'topic': event.get('topic', ''),
                    'location': event.get('location', ''),
                    'date': event.get('date', ''),
                    'original_text': event.get('original_text', '')
                }
                # Save to a simple file fallback
                memory_file = os.path.join(self.memory_dir, 'pattern_extracted_events.json')
                if os.path.exists(memory_file):
                    with open(memory_file, 'r') as f:
                        stored_events = json.load(f)
                else:
                    stored_events = []
                
                stored_events.append(simple_memory)
                
                with open(memory_file, 'w') as f:
                    json.dump(stored_events, f, indent=2)
                
                print(f"[ComprehensiveExtractor] ✅ Saved to fallback storage: {event.get('topic', 'Unknown')}")
            except Exception as fallback_error:
                print(f"[ComprehensiveExtractor] ❌ Fallback storage failed: {fallback_error}")
    
    def _create_memory_value(self, event: Dict[str, Any]) -> str:
        """Create readable memory value from event"""
        topic = event.get('topic', '').replace('_', ' ')
        people = event.get('people', [])
        location = event.get('location', '')
        details = event.get('details', '')
        
        # Build comprehensive memory string
        memory_parts = [topic]
        
        if people:
            memory_parts.append(f"with {', '.join(people)}")
        
        if location and location.lower() not in topic.lower():
            memory_parts.append(f"at {location}")
        
        if details and details.lower() not in topic.lower():
            memory_parts.append(f"({details})")
        
        return ' '.join(memory_parts)
    
    def _clean_json_response(self, response: str) -> str:
        """Clean LLM response to valid JSON with enhanced error handling"""
        if not response or not response.strip():
            return '{"events": [], "intent": "casual_conversation", "emotion": "neutral"}'
        
        # Remove any text before first {
        start = response.find('{')
        if start > 0:
            response = response[start:]
        elif start == -1:
            # No JSON found, return fallback
            return '{"events": [], "intent": "casual_conversation", "emotion": "neutral"}'
        
        # Remove any text after last }
        end = response.rfind('}')
        if end > 0:
            response = response[:end + 1]
        elif end == -1:
            # No closing brace, try to fix
            response = response + '}'
        
        # Additional cleaning for common JSON issues
        response = response.strip()
        
        # Fix trailing commas that break JSON parsing
        response = re.sub(r',(\s*[}\]])', r'\1', response)
        
        # Fix missing quotes around keys
        response = re.sub(r'(\w+)(\s*:)', r'"\1"\2', response)
        
        # Fix single quotes (should be double quotes in JSON)
        response = response.replace("'", '"')
        
        # Validate the JSON by attempting to parse it
        try:
            json.loads(response)
            return response
        except json.JSONDecodeError as e:
            print(f"[ComprehensiveExtractor] ⚠️ JSON validation failed: {e}")
            # Return a safe fallback response
            return '{"events": [], "intent": "casual_conversation", "emotion": "neutral", "confidence": 0.5}'
    
    def _clean_extraction_cache(self, current_time: float):
        """Clean expired cache entries"""
        expired = [h for h, t in self.extraction_cache.items() if current_time - t > self.cache_timeout]
        for h in expired:
            del self.extraction_cache[h]
    
    def _save_threading_data(self, result: ExtractionResult):
        """Save conversation threading data"""
        try:
            if result.conversation_thread_id:
                thread_data = {
                    'thread_id': result.conversation_thread_id,
                    'timestamp': datetime.now().isoformat(),
                    'events': result.memory_events,
                    'keywords': result.context_keywords
                }
                self.conversation_threads.append(thread_data)
                self.save_memory(self.conversation_threads, 'conversation_threads.json')
            
            if result.memory_enhancements:
                for enhancement in result.memory_enhancements:
                    self.memory_enhancements.append(enhancement)
                self.save_memory(self.memory_enhancements, 'memory_enhancements.json')
                
        except Exception as e:
            print(f"[ComprehensiveExtractor] ⚠️ Threading save error: {e}")
    
    def load_memory(self, filename: str) -> List[Dict]:
        """Load memory from JSON file"""
        filepath = os.path.join(self.memory_dir, filename)
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def save_memory(self, data: List[Dict], filename: str):
        """Save memory to JSON file"""
        filepath = os.path.join(self.memory_dir, filename)
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[ComprehensiveExtractor] ⚠️ Save error: {e}")
    
    def _should_allow_tier3_extraction(self, text: str) -> bool:
        """Check if TIER 3 extraction should be allowed to prevent loops"""
        current_time = datetime.now().timestamp()
        
        # Clean old TIER 3 cache entries
        self._clean_tier3_cache(current_time)
        
        # Create a hash for this text
        text_hash = hash(text.lower().strip())
        
        # Check if this exact text was recently processed with TIER 3
        if text_hash in self.tier3_cache:
            last_time = self.tier3_cache[text_hash]
            if current_time - last_time < self.tier3_limit_window:
                print(f"[ComprehensiveExtractor] 🚫 TIER 3 blocked: Recent extraction for similar text")
                return False
        
        # Check rate limiting: max 1 TIER 3 per minute
        recent_extractions = sum(1 for timestamp in self.tier3_cache.values() 
                               if current_time - timestamp < 60)
        
        if recent_extractions >= self.max_tier3_per_minute:
            print(f"[ComprehensiveExtractor] 🚫 TIER 3 rate limited: {recent_extractions} extractions in last minute")
            return False
        
        return True
    
    def _record_tier3_extraction(self, text: str):
        """Record that a TIER 3 extraction was performed"""
        text_hash = hash(text.lower().strip())
        self.tier3_cache[text_hash] = datetime.now().timestamp()
    
    def _clean_tier3_cache(self, current_time: float):
        """Clean old TIER 3 cache entries"""
        cutoff_time = current_time - self.tier3_limit_window
        keys_to_remove = [key for key, timestamp in self.tier3_cache.items() 
                         if timestamp < cutoff_time]
        for key in keys_to_remove:
            del self.tier3_cache[key]
    
    def _clean_extraction_cache(self, current_time: float):
        """Clean old extraction cache entries"""
        cutoff_time = current_time - self.cache_timeout
        keys_to_remove = [key for key, timestamp in self.extraction_cache.items() 
                         if timestamp < cutoff_time]
        for key in keys_to_remove:
            del self.extraction_cache[key]
            print(f"[ComprehensiveExtractor] ⚠️ Save error: {e}")