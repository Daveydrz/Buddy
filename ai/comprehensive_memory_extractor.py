"""
Comprehensive Memory Extractor - Pattern-first approach with LLM fallback
Created: 2025-01-22  
Purpose: Replace multiple extraction systems with unified, pattern-first system
"""

import json
import os
import re
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict

from ai.chat import ask_kobold
from ai.memory import get_user_memory
from ai.pattern_memory_extractor import PatternMemoryExtractor

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

class ComprehensiveMemoryExtractor:
    """
    🧠 Pattern-first extraction with LLM fallback:
    1. Try pattern recognition for common cases (fast, accurate)
    2. Fall back to LLM only when needed (context-aware tiers)
    3. Single extraction lock to prevent redundancy
    """
    
    # Class-level lock to ensure only one extraction happens at a time
    _extraction_lock = threading.Lock()
    
    def __init__(self, username: str):
        self.username = username
        self.memory_dir = f"memory/{username}"
        os.makedirs(self.memory_dir, exist_ok=True)
        
        # Get existing memory systems
        self.mega_memory = get_user_memory(username)
        
        # Initialize pattern-first extractor
        self.pattern_extractor = PatternMemoryExtractor()
        
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
        
        print(f"[ComprehensiveExtractor] 🧠 Initialized pattern-first extraction for {username}")
    
    def extract_all_from_text(self, text: str, conversation_context: str = "") -> ExtractionResult:
        """
        🎯 Pattern-first extraction with LLM fallback
        1. Try pattern recognition first (fast, no LLM call)
        2. Use LLM only when pattern matching fails
        3. Locking to ensure only one extraction at a time
        """
        # Use class-level lock to prevent multiple parallel extractions
        with self._extraction_lock:
            print(f"[ComprehensiveExtractor] 🔒 Extraction lock acquired for: '{text[:50]}...'")
            
            # Check deduplication cache first
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
                # Check if this is a memory enhancement first
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
                
                # Filter out pure casual conversation
                if self._is_casual_conversation(text):
                    print(f"[ComprehensiveExtractor] 💬 Pure casual conversation detected")
                    return ExtractionResult([], "casual_conversation", {}, None, [], [], [])
                
                # TRY PATTERN-FIRST APPROACH
                pattern_result = self.pattern_extractor.extract_if_pattern_matches(text)
                if pattern_result and pattern_result.matched:
                    print(f"[ComprehensiveExtractor] ⚡ Pattern extraction successful (no LLM needed)")
                    
                    # Convert pattern result to ExtractionResult format
                    extraction_result = ExtractionResult(
                        memory_events=pattern_result.memory_events,
                        intent_classification=pattern_result.intent_classification,
                        emotional_state=pattern_result.emotional_state,
                        conversation_thread_id=None,
                        memory_enhancements=[],
                        context_keywords=pattern_result.context_keywords,
                        follow_up_suggestions=[]
                    )
                    
                    # Store memory events
                    for event in extraction_result.memory_events:
                        self._add_to_regular_memory(event)
                        self._save_to_smart_memory_files(event)
                    
                    return extraction_result
                
                # FALLBACK TO LLM if patterns don't match
                print(f"[ComprehensiveExtractor] 🤖 Falling back to LLM extraction")
                
                # Determine complexity for LLM extraction
                complexity_score = self._calculate_complexity_score(text)
                word_count = len(text.split())
                
                # Simplified tier selection - prefer lower tiers
                if complexity_score <= 2 and word_count <= 8:
                    # TIER 1: Simple extraction (minimal tokens)
                    result = self._tier1_simple_extraction(text)
                elif complexity_score <= 5 and word_count <= 20:
                    # TIER 2: Medium extraction (reduced tokens)
                    result = self._tier2_medium_extraction(text)
                else:
                    # TIER 3: Complex extraction (only when absolutely needed)
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
                    self._save_to_smart_memory_files(event)
                
                # Save conversation threading data
                if result.conversation_thread_id or result.memory_enhancements:
                    self._save_threading_data(result)
                
                print(f"[ComprehensiveExtractor] ✅ Extraction completed for: '{text[:50]}...'")
                return result
                
            except Exception as e:
                print(f"[ComprehensiveExtractor] ❌ Extraction error: {e}")
                # Return fallback result on error
                return ExtractionResult([], "error", {"primary_emotion": "neutral"}, None, [], [], [])
    
    def _tier1_simple_extraction(self, text: str) -> ExtractionResult:
        """Simple extraction for basic inputs (minimal tokens)"""
        prompt = f"""Extract basic info from: "{text}"
Date: {datetime.now().strftime('%Y-%m-%d')}

JSON format:
{{"events": [{{"type": "highlight", "topic": "brief_desc", "date": "YYYY-MM-DD", "emotion": "neutral"}}], "intent": "statement", "emotion": "neutral", "keywords": ["key1"]}}"""
        
        print(f"[ComprehensiveExtractor] ⚡ TIER 1 extraction (minimal tokens)")
        return self._process_llm_response(prompt, text)
    
    def _tier2_medium_extraction(self, text: str) -> ExtractionResult:
        """Medium extraction for social events (reduced tokens)"""
        prompt = f"""Extract from: "{text}"
Date: {datetime.now().strftime('%Y-%m-%d')}

Types: appointment, life_event, highlight
Intent: statement, question, request
Emotion: happy, neutral, stressed, excited

JSON format:
{{"events": [{{"type": "life_event", "topic": "brief_desc", "date": "YYYY-MM-DD", "emotion": "neutral", "priority": "medium"}}], "intent": "statement", "emotion": "neutral", "keywords": ["key1", "key2"]}}"""
        
        print(f"[ComprehensiveExtractor] ⚡ TIER 2 extraction (reduced tokens)")
        return self._process_llm_response(prompt, text)
    
    def _tier3_comprehensive_extraction(self, text: str, conversation_context: str = "") -> ExtractionResult:
        """Comprehensive extraction for complex scenarios (reduced tokens, no examples)"""
        current_date = datetime.now().strftime('%Y-%m-%d')
        
        context_section = ""
        if conversation_context:
            context_section = f"\nContext: {conversation_context[:100]}..."
        
        prompt = f"""COMPREHENSIVE ANALYSIS: "{text}"{context_section}
Date: {current_date}

Extract ALL relevant information:
1. EVENTS (appointments, life_events, highlights, plans)
2. INTENT (question, request, statement, memory_recall, instruction)
3. EMOTIONAL STATE (emotion, intensity, confidence)
4. CONTEXT KEYWORDS

Types:
- appointment: Time-specific events
- life_event: Social/emotional events  
- highlight: Thoughts, feelings, information

JSON format:
{{
  "events": [{{
    "type": "life_event",
    "topic": "activity_description", 
    "date": "{current_date}",
    "time": null,
    "emotion": "neutral",
    "priority": "medium",
    "people": [],
    "location": "location_if_mentioned",
    "details": "additional_info",
    "original_text": "{text}"
  }}],
  "intent": "statement",
  "emotional_state": {{
    "primary_emotion": "neutral",
    "intensity": 0.5,
    "confidence": 0.8
  }},
  "context_keywords": ["keyword1", "keyword2"],
  "follow_up_potential": []
}}

Return ONLY valid JSON."""
        
        print(f"[ComprehensiveExtractor] ⚡ TIER 3 comprehensive extraction (reduced tokens)")
        return self._process_llm_response(prompt, text, is_comprehensive=True)
    
    def _process_llm_response(self, prompt: str, original_text: str, is_comprehensive: bool = False) -> ExtractionResult:
        """Process LLM response with improved JSON validation and error handling"""
        try:
            # Format prompt as messages array for kobold
            messages = [{"role": "system", "content": prompt}]
            llm_response = ask_kobold(messages)
            
            # Clean and parse JSON with improved validation
            llm_response = self._clean_json_response(llm_response)
            
            # Multiple JSON parsing attempts with fallbacks
            data = self._parse_json_with_fallbacks(llm_response, original_text)
            if not data:
                return self._create_fallback_result(original_text)
            
            # Validate and extract data based on tier
            if is_comprehensive:
                return self._extract_comprehensive_data(data, original_text)
            else:
                return self._extract_simple_data(data, original_text)
                
        except Exception as e:
            print(f"[ComprehensiveExtractor] ❌ LLM processing error: {e}")
            return self._create_fallback_result(original_text)
    
    def _parse_json_with_fallbacks(self, response: str, original_text: str) -> Optional[Dict]:
        """Parse JSON with multiple fallback strategies"""
        # Attempt 1: Direct parsing
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            pass
        
        # Attempt 2: Extract JSON from markdown code blocks
        try:
            json_match = re.search(r'```(?:json)?\s*(\{.*\})\s*```', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass
        
        # Attempt 3: Find first JSON object in response
        try:
            start = response.find('{')
            end = response.rfind('}') + 1
            if start >= 0 and end > start:
                return json.loads(response[start:end])
        except json.JSONDecodeError:
            pass
        
        # Attempt 4: Clean and retry
        try:
            cleaned = re.sub(r'[^\x20-\x7E]', '', response)  # Remove non-printable chars
            return json.loads(cleaned)
        except json.JSONDecodeError:
            pass
        
        print(f"[ComprehensiveExtractor] ❌ All JSON parsing attempts failed")
        print(f"[ComprehensiveExtractor] 📄 Raw response: {response[:200]}...")
        return None
    
    def _extract_comprehensive_data(self, data: Dict, original_text: str) -> ExtractionResult:
        """Extract data from comprehensive tier response"""
        return ExtractionResult(
            memory_events=data.get('events', []),
            intent_classification=data.get('intent', 'casual_conversation'),
            emotional_state=data.get('emotional_state', {'primary_emotion': 'neutral'}),
            conversation_thread_id=data.get('conversation_thread', {}).get('thread_id'),
            memory_enhancements=[],
            context_keywords=data.get('context_keywords', []),
            follow_up_suggestions=data.get('follow_up_potential', [])
        )
    
    def _extract_simple_data(self, data: Dict, original_text: str) -> ExtractionResult:
        """Extract data from simple tier response"""
        return ExtractionResult(
            memory_events=data.get('events', []),
            intent_classification=data.get('intent', 'casual_conversation'),
            emotional_state={'primary_emotion': data.get('emotion', 'neutral'), 'confidence': data.get('confidence', 0.7)},
            conversation_thread_id=None,
            memory_enhancements=[],
            context_keywords=data.get('keywords', []),
            follow_up_suggestions=[]
        )
    
    def _create_fallback_result(self, original_text: str) -> ExtractionResult:
        """Create fallback result when JSON parsing fails"""
        return ExtractionResult(
            memory_events=[],
            intent_classification='casual_conversation',
            emotional_state={'primary_emotion': 'neutral', 'confidence': 0.5},
            conversation_thread_id=None,
            memory_enhancements=[],
            context_keywords=original_text.lower().split()[:3],  # Basic keywords from input
            follow_up_suggestions=[]
        )
    
    def _check_memory_enhancement(self, text: str) -> Optional[Dict[str, Any]]:
        """Check if text enhances existing memory (location → food example)"""
        text_lower = text.lower()
        
        # Get recent memories for enhancement opportunities
        recent_memories = self._get_recent_memories(hours=24)
        
        for memory in recent_memories:
            memory_topic = memory.get('topic', '').lower()
            
            # Check for restaurant enhancement example
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
        """
        Calculate text complexity for tier selection
        Enhanced to properly detect activity types and complexity
        """
        text_lower = text.lower()
        score = 0
        
        # Time references (+3) - High complexity
        time_indicators = ['tomorrow', 'today', 'yesterday', 'next week', 'next weekend', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday', 'at ', 'pm', 'am', 'o\'clock', 'later', 'earlier']
        if any(indicator in text_lower for indicator in time_indicators):
            score += 3
        
        # People mentioned (+3) - High complexity  
        people_indicators = ['with', 'friend', 'family', 'mom', 'dad', 'sister', 'brother', 'francesco', 'sarah', 'john', 'we', 'us', 'them']
        if any(person in text_lower for person in people_indicators):
            score += 3
        
        # Planning/Future activities (+2) - Medium-high complexity
        planning_indicators = ['planning', 'will', 'going to', 'next', 'plan to', 'want to', 'thinking about']
        if any(plan in text_lower for plan in planning_indicators):
            score += 2
        
        # Ongoing activities (+2) - Medium-high complexity
        ongoing_indicators = ['been reading', 'been learning', 'been studying', 'currently', 'still', 'continuing']
        if any(ongoing in text_lower for ongoing in ongoing_indicators):
            score += 2
        
        # Locations (+2) - Medium complexity
        locations = ['mcdonald', 'restaurant', 'store', 'work', 'home', 'school', 'park', 'mall', 'place']
        if any(location in text_lower for location in locations):
            score += 2
        
        # Past activities (+1) - Basic complexity
        past_activities = ['went', 'visited', 'read', 'finished', 'completed', 'did']
        if any(activity in text_lower for activity in past_activities):
            score += 1
        
        # Current states (+1) - Basic complexity
        current_states = ['learning', 'studying', 'working', 'doing']
        if any(state in text_lower for state in current_states):
            score += 1
        
        # Emotional content (+1) - Basic complexity
        emotions = ['happy', 'sad', 'excited', 'worried', 'nervous', 'love', 'hate', 'stressed', 'enjoy', 'like']
        if any(emotion in text_lower for emotion in emotions):
            score += 1
        
        return min(score, 10)  # Cap at 10 for very complex scenarios
    
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
                category="activities",  # Default category
                key=topic,
                value=memory_value,
                confidence=0.9,
                date_learned=event.get('date', datetime.now().strftime('%Y-%m-%d')),
                last_mentioned=datetime.now().strftime('%Y-%m-%d'),
                source_context=event.get('original_text', '')
            )
            
            fact.emotional_significance = 0.7 if event.get('emotion') in ['happy', 'excited'] else 0.3
            
            self.mega_memory.personal_facts[topic] = fact
            print(f"[ComprehensiveExtractor] ➕ Added to memory: {topic} = {memory_value}")
            
        except Exception as e:
            print(f"[ComprehensiveExtractor] ⚠️ Memory addition error: {e}")
    
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
    
    def _save_to_smart_memory_files(self, event: Dict[str, Any]):
        """Save event to appropriate smart memory file based on type"""
        try:
            event_type = event.get('type', 'unknown').lower()
            
            # Determine which file to save to based on event type and properties
            if 'appointment' in event_type or event.get('time'):
                filename = 'smart_appointments.json'
            elif any(keyword in event_type for keyword in ['plan', 'future', 'will']) or event.get('status') == 'future':
                filename = 'smart_life_events.json'
            elif any(keyword in event_type for keyword in ['visit', 'location', 'went', 'been']):
                filename = 'smart_life_events.json'
            else:
                filename = 'smart_highlights.json'
            
            # Load existing data
            existing_events = self.load_memory(filename)
            
            # Add timestamp if missing
            if 'timestamp' not in event:
                event['timestamp'] = datetime.now().isoformat()
            
            # Add unique ID if missing
            if 'id' not in event:
                event['id'] = f"{event_type}_{int(datetime.now().timestamp())}"
            
            # Add to existing events
            existing_events.append(event)
            
            # Save back to file
            self.save_memory(existing_events, filename)
            
            print(f"[ComprehensiveExtractor] 💾 Saved to {filename}: {event.get('topic', 'unknown')}")
            
        except Exception as e:
            print(f"[ComprehensiveExtractor] ⚠️ Smart memory save error: {e}")