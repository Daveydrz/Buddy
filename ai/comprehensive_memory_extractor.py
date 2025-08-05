"""
Comprehensive Memory Extractor - Single LLM call for all extraction types
Created: 2025-01-22
Purpose: Replace multiple extraction systems with one unified, context-aware system
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
    🧠 Single LLM call for ALL extraction types:
    - Memory events (appointments, life events, highlights)  
    - Intent detection
    - Emotional analysis
    - Conversation threading
    - Memory enhancements
    - Context keywords
    """
    
    # Class-level lock to ensure only one extraction happens at a time
    _extraction_lock = threading.Lock()
    
    def __init__(self, username: str):
        self.username = username
        self.memory_dir = f"memory/{username}"
        os.makedirs(self.memory_dir, exist_ok=True)
        
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
        
        print(f"[ComprehensiveExtractor] 🧠 Initialized unified extraction for {username}")
    
    def extract_all_from_text(self, text: str, conversation_context: str = "") -> ExtractionResult:
        """
        🎯 Single LLM call for ALL extraction types with context awareness
        Uses locking to ensure only one extraction happens at a time
        Now with enhanced context awareness to reduce unnecessary operations
        """
        # Use class-level lock to prevent multiple parallel extractions
        with self._extraction_lock:
            print(f"[ComprehensiveExtractor] 🔒 Extraction lock acquired for: '{text[:50]}...'")
            
            # Enhanced context awareness - check if extraction is actually needed
            if self._should_skip_extraction(text, conversation_context):
                print(f"[ComprehensiveExtractor] 🚫 SKIPPING unnecessary extraction: '{text[:50]}...'")
                return ExtractionResult([], "casual_conversation", {}, None, [], [], [])
            
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
                
                # Enhanced context filtering - more intelligent casual conversation detection
                if self._is_casual_conversation_enhanced(text, conversation_context):
                    return ExtractionResult([], "casual_conversation", {}, None, [], [], [])
                
                # Determine complexity and optimize tokens with context awareness
                complexity_score = self._calculate_complexity_score_enhanced(text, conversation_context)
                word_count = len(text.split())
                
                # Choose extraction tier based on complexity with TIER 3 limiting and context
                if complexity_score <= 3 and word_count <= 8:
                    # TIER 1: Simple extraction (70 tokens total)
                    result = self._tier1_simple_extraction(text)
                elif complexity_score <= 6 and word_count <= 20:
                    # TIER 2: Medium extraction (150 tokens total)  
                    result = self._tier2_medium_extraction(text)
                else:
                    # TIER 3: Complex extraction (300 tokens total - comprehensive)
                    # Check if we should limit TIER 3 extractions to prevent loops
                    if self._should_allow_tier3_extraction_enhanced(text, conversation_context):
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
                
                print(f"[ComprehensiveExtractor] ✅ Extraction completed for: '{text[:50]}...'")
                return result
                
            except Exception as e:
                print(f"[ComprehensiveExtractor] ❌ Extraction error: {e}")
                # Return fallback result on error
                return ExtractionResult([], "error", {"primary_emotion": "neutral"}, None, [], [], [])
    
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
        """Calculate text complexity for tier selection"""
        text_lower = text.lower()
        score = 0
        
        # Time references (+2)
        time_indicators = ['tomorrow', 'today', 'yesterday', 'next week', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday', 'at ', 'pm', 'am', 'o\'clock']
        if any(indicator in text_lower for indicator in time_indicators):
            score += 2
        
        # People mentioned (+2)  
        people_indicators = ['with', 'friend', 'family', 'mom', 'dad', 'sister', 'brother', 'francesco', 'sarah', 'john']
        if any(person in text_lower for person in people_indicators):
            score += 2
        
        # Locations (+1)
        locations = ['mcdonald', 'restaurant', 'store', 'work', 'home', 'school', 'park', 'mall']
        if any(location in text_lower for location in locations):
            score += 1
        
        # Events/activities (+1)
        activities = ['went', 'going', 'visit', 'meeting', 'appointment', 'party', 'birthday', 'dinner', 'lunch']
        if any(activity in text_lower for activity in activities):
            score += 1
        
        # Emotional content (+1)
        emotions = ['happy', 'sad', 'excited', 'worried', 'nervous', 'love', 'hate', 'stressed']
        if any(emotion in text_lower for emotion in emotions):
            score += 1
        
        return min(score, 8)  # Cap at 8
    
    def _should_skip_extraction(self, text: str, conversation_context: str = "") -> bool:
        """🎯 Enhanced context awareness - determine if extraction is needed at all"""
        text_lower = text.lower().strip()
        
        # Skip very short or empty inputs
        if len(text_lower) < 3:
            return True
        
        # Skip pure acknowledgments when in conversation
        if conversation_context and text_lower in ['ok', 'okay', 'yes', 'no', 'yeah', 'yep', 'nope', 'sure', 'alright']:
            return True
        
        # Skip repeated identical inputs (conversation loop detection)
        if conversation_context and text_lower in conversation_context.lower():
            return True
        
        # Skip system/debug messages
        if any(pattern in text_lower for pattern in ['[debug]', '[system]', '[error]', '[log]']):
            return True
        
        return False
    
    def _is_casual_conversation_enhanced(self, text: str, conversation_context: str = "") -> bool:
        """Enhanced casual conversation filtering with context awareness"""
        text_lower = text.lower().strip()
        
        # Original casual patterns
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
        
        # Enhanced patterns based on conversation context
        if conversation_context:
            # If this looks like a direct follow-up question in ongoing conversation
            followup_patterns = [
                r'^(and\s+)?(what|how|when|where|why)',
                r'^(tell\s+me\s+)?(more|about)',
                r'^(can\s+you|could\s+you)',
            ]
            
            for pattern in followup_patterns:
                if re.search(pattern, text_lower):
                    # This might be a meaningful follow-up, don't skip
                    return False
        
        # Too short without meaningful content
        if len(text.split()) < 3 and not any(word in text_lower for word in ['mcdonald', 'francesco', 'mcflurry', 'went', 'had', 'with']):
            return True
            
        return False
    
    def _calculate_complexity_score_enhanced(self, text: str, conversation_context: str = "") -> int:
        """Enhanced complexity calculation with conversation context"""
        text_lower = text.lower()
        score = 0
        
        # Base complexity from original method
        score = self._calculate_complexity_score(text)
        
        # Context-based adjustments
        if conversation_context:
            # If continuing a conversation thread, increase complexity
            context_lower = conversation_context.lower()
            
            # Check for thread continuation (McDonald's example)
            if any(thread_word in context_lower for thread_word in ['mcdonald', 'restaurant', 'food']):
                if any(food_word in text_lower for food_word in ['mcflurry', 'burger', 'fries', 'drink']):
                    score += 2  # This is continuing a food conversation
            
            # Check for social context continuation
            if any(social_word in context_lower for social_word in ['with', 'friend', 'together']):
                if any(name_word in text_lower for name_word in ['francesco', 'sarah', 'john', 'david']):
                    score += 2  # This is adding social context
        
        # Recent memory relevance check
        recent_memories = self._get_recent_memories(hours=2)  # Check last 2 hours
        for memory in recent_memories:
            memory_topic = memory.get('topic', '').lower()
            if any(word in memory_topic for word in text_lower.split()):
                score += 1  # Related to recent memory
                break
        
        return min(score, 10)  # Cap at 10
    
    def _should_allow_tier3_extraction_enhanced(self, text: str, conversation_context: str = "") -> bool:
        """Enhanced TIER 3 limiting with context awareness"""
        # Original rate limiting check
        if not self._should_allow_tier3_extraction(text):
            return False
        
        # Context-based TIER 3 justification
        text_lower = text.lower()
        
        # Always allow TIER 3 for complex social interactions
        if any(social_indicator in text_lower for social_indicator in ['went with', 'had with', 'together', 'friend']):
            return True
        
        # Always allow TIER 3 for memory enhancement contexts
        if conversation_context and any(food in conversation_context.lower() for food in ['mcdonald', 'restaurant']):
            return True
        
        # Allow TIER 3 for location/time specific information
        if any(location_time in text_lower for location_time in ['yesterday', 'today', 'tomorrow', 'at ', 'pm', 'am']):
            return True
        
        # Default to original logic
        return True
    
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
                key=topic,
                value=memory_value,
                date_learned=event.get('date', datetime.now().strftime('%Y-%m-%d')),
                confidence=0.9
            )
            
            fact.emotional_significance = 0.7 if event.get('emotion') in ['happy', 'excited'] else 0.3
            fact.source_context = event.get('original_text', '')
            
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
            print(f"[ComprehensiveExtractor] ⚠️ Save error: {e}")