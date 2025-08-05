# ai/human_memory_smart.py - Smart LLM-based life event detection
import json
import os
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import re
from ai.memory import get_user_memory, add_to_conversation_history
from ai.chat import ask_kobold  # Use your existing LLM connection

class SmartHumanLikeMemory:
    """🧠 Smart human-like memory using LLM for event detection"""
    
    def __init__(self, username: str):
        self.username = username
        self.memory_dir = f"memory/{username}"
        os.makedirs(self.memory_dir, exist_ok=True)
        
        # Get the existing MEGA-INTELLIGENT memory system
        self.mega_memory = get_user_memory(username)
        
        # Smart memory storage
        self.appointments = self.load_memory('smart_appointments.json')
        self.life_events = self.load_memory('smart_life_events.json') 
        self.conversation_highlights = self.load_memory('smart_highlights.json')
        
        # ✅ NEW: Conversation threading for memory integration
        self.conversation_threads = self.load_memory('conversation_threads.json')
        self.memory_enhancements = self.load_memory('memory_enhancements.json')
        
        # Session tracking
        self.context_used_this_session = set()
        
        # ✅ FIX: Deduplication cache to prevent duplicate extractions
        self.extraction_cache = {}  # text_hash -> timestamp
        self.cache_timeout = 30  # seconds - prevent same text extraction within 30 seconds
        
        print(f"[SmartMemory] 🧠 Smart LLM-based memory initialized for {username}")
    
    def extract_and_store_human_memories(self, text: str):
        """🎯 Smart LLM-based memory extraction with BULLETPROOF filtering"""
        
        # ✅ FIX: Check for duplicate extraction within cache timeout
        text_hash = hash(text.lower().strip())
        current_time = datetime.now().timestamp()
        
        # Clean old cache entries
        self._clean_extraction_cache(current_time)
        
        # Check if we've recently processed this exact text
        if text_hash in self.extraction_cache:
            last_extraction_time = self.extraction_cache[text_hash]
            time_since_last = current_time - last_extraction_time
            if time_since_last < self.cache_timeout:
                print(f"[SmartMemory] 🔄 SKIPPING duplicate extraction for: '{text[:50]}...' (processed {time_since_last:.1f}s ago)")
                return
        
        # Mark this text as being processed
        self.extraction_cache[text_hash] = current_time
        print(f"[SmartMemory] 🧠 Starting memory extraction for: '{text[:50]}...'")
        
        # ✅ NEW: Check for memory enhancements before extraction
        enhancement_result = self._check_for_memory_enhancement(text)
        if enhancement_result:
            print(f"[SmartMemory] 🔗 Enhanced existing memory: {enhancement_result}")
            return
        # Also use the existing MEGA-INTELLIGENT extraction
        self.mega_memory.extract_memories_from_text(text)
        
        # Use LLM to intelligently detect events (only if passes all filters)
        detected_events = self._smart_detect_events(text)
        
        # Store detected events
        for event in detected_events:
            if event['type'] == 'appointment':
                self.appointments.append(event)
                print(f"[SmartMemory] 📅 Smart appointment: {event['topic']} on {event['date']}")
                # CRITICAL: Also add to regular memory system for retrieval
                self._add_to_regular_memory(event)
                
            elif event['type'] == 'life_event':
                self.life_events.append(event)
                print(f"[SmartMemory] 📝 Smart life event: {event['topic']} on {event['date']} ({event['emotion']})")
                # CRITICAL: Also add to regular memory system for retrieval
                self._add_to_regular_memory(event)
                
            elif event['type'] == 'highlight':
                self.conversation_highlights.append(event)
                print(f"[SmartMemory] 💬 Smart highlight: {event['topic']}")
        
        # Save memories
        if detected_events:  # Only save if we actually found events
            self.save_memory(self.appointments, 'smart_appointments.json')
            self.save_memory(self.life_events, 'smart_life_events.json')
            self.save_memory(self.conversation_highlights, 'smart_highlights.json')
    
    def _clean_extraction_cache(self, current_time: float):
        """Clean old entries from extraction cache"""
        expired_hashes = []
        for text_hash, timestamp in self.extraction_cache.items():
            if current_time - timestamp > self.cache_timeout:
                expired_hashes.append(text_hash)
        
        for text_hash in expired_hashes:
            del self.extraction_cache[text_hash]
        
        if expired_hashes:
            print(f"[SmartMemory] 🧹 Cleaned {len(expired_hashes)} expired cache entries")
    
    def _add_to_regular_memory(self, event: Dict):
        """Add detected event to regular memory system for retrieval"""
        try:
            # Create a memory fact from the event
            fact_key = event['topic'].replace(' ', '_').lower()
            fact_value = self._create_readable_memory_value(event)
            
            # Add to personal facts with correct PersonalFact constructor
            from ai.memory import PersonalFact
            fact = PersonalFact(
                key=fact_key,
                value=fact_value,
                date_learned=event.get('date', event.get('created', '')),
                confidence=0.9
            )
            
            # Set additional attributes after construction
            fact.emotional_significance = 0.7 if event.get('emotion') in ['happy', 'excited'] else 0.3
            fact.source_context = event.get('original_text', '')
            
            self.mega_memory.personal_facts[fact_key] = fact
            print(f"[SmartMemory] ➕ Added to regular memory: {fact_key} = {fact_value}")
            
        except Exception as e:
            print(f"[SmartMemory] ⚠️ Error adding to regular memory: {e}")
            # Fallback: add directly to working memory
            try:
                fact_key = event['topic'].replace(' ', '_').lower()
                fact_value = self._create_readable_memory_value(event)
                self.mega_memory.working_memory.last_action = f"{fact_key}: {fact_value}"
                print(f"[SmartMemory] 🔄 Added to working memory instead: {fact_key}")
            except Exception as e2:
                print(f"[SmartMemory] ❌ Fallback also failed: {e2}")
    
    def _create_readable_memory_value(self, event: Dict) -> str:
        """Create a readable memory value from an event"""
        topic = event.get('topic', '').replace('_', ' ')
        date = event.get('date', '')
        emotion = event.get('emotion', '')
        original_text = event.get('original_text', '')
        
        # Extract key information based on event type
        if event.get('type') == 'appointment':
            return f"{topic} scheduled for {date}"
        elif event.get('type') == 'life_event':
            # For life events, try to extract more context
            if 'mcdonalds' in topic.lower() or 'mcdonald' in topic.lower():
                if 'with_' in topic:
                    companion = topic.split('with_')[-1].replace('_', ' ')
                    return f"mcdonalds with {companion}"
                return "mcdonalds"
            elif 'birthday' in topic.lower():
                if '_' in topic:
                    person = topic.split('_')[0]
                    return f"{person} birthday on {date}"
                return f"birthday on {date}"
            elif 'met_' in topic:
                parts = topic.replace('met_', '').split('_at_')
                if len(parts) == 2:
                    person, place = parts
                    return f"met {person.replace('_', ' ')} at {place.replace('_', ' ')}"
            return topic.replace('_', ' ')
        else:
            return topic.replace('_', ' ')
    
    def _is_casual_conversation(self, text: str) -> bool:
        """🛡️ PROGRESSIVE filter - less restrictive for better extraction rate"""
        text_lower = text.lower().strip()
        
        # Only block PURE casual conversation (no memory content)
        pure_casual_patterns = [
            r'^(hi|hello|hey)\s*$',                    # Pure greetings only
            r'^(thanks?|thank\s+you)\s*$',            # Pure thanks only
            r'^(bye|goodbye)\s*$',                    # Pure goodbyes only
            r'^(yes|yeah|yep|no|nope)\s*$',          # Pure yes/no only
            r'^(okay|ok|alright)\s*$',               # Pure acknowledgments only
            r'^i.+m.+(fine|good|okay)\s*$',          # Pure status responses only
            r'^nothing.+much\s*$',                   # Pure "nothing much" only
            r'^not.+much\s*$',                       # Pure "not much" only
        ]
        
        # Check for pure casual patterns
        for pattern in pure_casual_patterns:
            if re.search(pattern, text_lower):
                print(f"[SmartMemory] 🛡️ BLOCKED pure casual: '{text}'")
                return True
        
        # RELAXED: Allow questions that might contain memory content
        # Only block questions about Buddy, not about user activities
        buddy_question_patterns = [
            r'how.+are.+you',           # "How are you?"
            r'what.+about.+you',        # "What about you?"
            r'what.+your.+plan',        # "What's your plan?"
            r'what.+you.+think',        # "What do you think?"
            r'where.+are.+you',         # "Where are you?"
        ]
        
        # Check if it's a question about Buddy (still block these)
        for pattern in buddy_question_patterns:
            if re.search(pattern, text_lower):
                print(f"[SmartMemory] 🛡️ BLOCKED Buddy question: '{text}'")
                return True
        
        # RELAXED: Reduce minimum word count from 6 to 4
        if len(text.split()) < 4:
            print(f"[SmartMemory] 🛡️ BLOCKED too short ({len(text.split())} words): '{text}'")
            return True
        
        # RELAXED: Allow questions that contain memory-worthy information
        # Check if question contains memory indicators despite having "?"
        if '?' in text:
            memory_question_indicators = [
                'where did i', 'what did i', 'when did i', 'who did i',
                'where was i', 'what was i', 'who was i with',
                'where am i going', 'what do i have', 'when is my',
                'what am i', 'where are we', 'what are we doing'
            ]
            
            # Allow memory-related questions
            if any(indicator in text_lower for indicator in memory_question_indicators):
                print(f"[SmartMemory] ✅ ALLOWED memory question: '{text}'")
                return False
            else:
                print(f"[SmartMemory] 🛡️ BLOCKED non-memory question: '{text}'")
                return True
        
        print(f"[SmartMemory] ✅ PASSED casual filter: '{text}'")
        return False
    
    def _calculate_memory_score(self, text: str) -> int:
        """🎯 PROGRESSIVE SCORING: Calculate memory worthiness score for better extraction rate"""
        text_lower = text.lower()
        score = 0
        
        # TIME INDICATORS (3 points) - EXPANDED for casual expressions
        time_indicators = [
            # Explicit time references
            'tomorrow', 'today', 'tonight', 'this week', 'next week', 'this weekend',
            'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday',
            'this morning', 'this afternoon', 'this evening', 'later today',
            'in an hour', 'in a few hours', 'at ', 'o\'clock',
            'earlier today', 'earlier', 'just now', 'a while ago', 
            'last night', 'yesterday', 'last week', 'recently', 'just',
            'before', 'after lunch', 'after work', 'next month',
            # ENHANCED: Casual time expressions
            'a bit ago', 'the other day', 'a while back', 'some time ago',
            'a few days ago', 'couple days ago', 'few weeks ago', 'last time',
            'when I was', 'during', 'while I was', 'after I', 'before I',
            'on my way', 'heading', 'going', 'coming back from',
            # Future references  
            'next week wednesday', 'next wednesday', 'tomorrow afternoon',
            'later this week', 'end of week', 'weekend', 'soon', 'upcoming', 'planned',
            'in a few days', 'in a week', '3pm', '3 pm', 'at 3', 'morning', 'afternoon', 'evening'
        ]
        
        if any(indicator in text_lower for indicator in time_indicators):
            score += 3
            print(f"[SmartMemory] ⏰ +3 time indicators")
        
        # LOCATION CONTEXT (2 points) - High-value for memory
        location_keywords = [
            # Specific places
            'mcdonalds', 'mcdonald', 'starbucks', 'walmart', 'target', 'costco',
            'restaurant', 'cafe', 'shop', 'store', 'mall', 'park', 'beach', 'gym',
            'library', 'bank', 'church', 'supermarket', 'grocery', 'pharmacy',
            'gas station', 'cinema', 'theater', 'museum', 'zoo', 'hospital',
            'clinic', 'office', 'school', 'work', 'home', 'house',
            # Location indicators
            'at the', 'was at', 'went to', 'been to', 'visited', 'stopped by',
            'at my', 'to my', 'from the', 'from my'
        ]
        
        if any(keyword in text_lower for keyword in location_keywords):
            score += 2
            print(f"[SmartMemory] 📍 +2 location context")
        
        # EVENT KEYWORDS (2 points) - Social and personal events
        event_keywords = [
            # Appointments & meetings
            'appointment', 'meeting', 'dentist', 'doctor', 'surgery', 'interview',
            'class', 'lesson', 'session', 'therapy', 'vet', 'haircut',
            # Social events
            'birthday', 'party', 'wedding', 'funeral', 'visit', 'visiting',
            'dinner', 'lunch', 'breakfast', 'coffee', 'movie', 'concert',
            'date', 'hang out', 'play date', 'sleepover',
            # People
            'niece', 'nephew', 'cousin', 'friend', 'friends', 'family',
            'mom', 'dad', 'sister', 'brother', 'girlfriend', 'boyfriend',
            # Activities  
            'grabbed food', 'got food', 'ate at', 'had lunch', 'had dinner',
            'picked up', 'dropped off', 'met with', 'talked to', 'saw',
            'bought', 'shopping', 'trip', 'vacation', 'flight'
        ]
        
        if any(keyword in text_lower for keyword in event_keywords):
            score += 2
            print(f"[SmartMemory] 🎯 +2 event keywords")
        
        # ACTION VERBS (1 point) - Actions and activities
        action_verbs = [
            'went', 'go', 'going', 'been', 'was', 'visited', 'stopped',
            'ate', 'had', 'bought', 'got', 'picked', 'dropped', 'met', 'saw',
            'grabbed', 'discussed', 'talked', 'planning', 'scheduled',
            'have', 'seeing', 'visiting', 'meeting', 'starting', 'finishing',
            'attending', 'off', 'heading', 'booked', 'arranging'
        ]
        
        if any(verb in text_lower for verb in action_verbs):
            score += 1
            print(f"[SmartMemory] ⚡ +1 action verbs")
        
        # EMOTIONAL CONTEXT (1 point) - Emotional significance
        emotional_keywords = [
            'nervous', 'excited', 'worried', 'happy', 'sad', 'stressed',
            'anxious', 'thrilled', 'disappointed', 'frustrated', 'relieved',
            'looking forward', 'can\'t wait', 'dreading', 'love', 'hate'
        ]
        
        if any(emotion in text_lower for emotion in emotional_keywords):
            score += 1
            print(f"[SmartMemory] 😊 +1 emotional context")
        
        # CONVERSATIONAL CUES (1 point) - Memory references
        conversation_cues = [
            'remember', 'told you', 'mentioned', 'said', 'like I said',
            'as I mentioned', 'you know', 'oh yeah', 'by the way',
            'speaking of', 'that reminds me'
        ]
        
        if any(cue in text_lower for cue in conversation_cues):
            score += 1
            print(f"[SmartMemory] 💬 +1 conversation cues")
        
        print(f"[SmartMemory] 📊 Total score: {score}/9 for '{text[:50]}...'")
        return score
    
    def _likely_contains_events(self, text: str) -> bool:
        """🎯 PROGRESSIVE FILTERING: Use scoring system for better extraction rate"""
        text_lower = text.lower()
        
        # Calculate memory score
        memory_score = self._calculate_memory_score(text)
        
        # Progressive thresholds for different pass levels
        strict_threshold = 6  # Original high standard
        relaxed_threshold = 4  # Balanced threshold  
        permissive_threshold = 3  # Catch edge cases
        
        # Check which threshold to use based on text characteristics
        word_count = len(text.split())
        has_question = '?' in text
        
        if word_count >= 6 and not has_question:
            # Use strict threshold for longer, declarative statements
            threshold = strict_threshold
            print(f"[SmartMemory] 🎯 Using STRICT threshold ({threshold}) for formal statement")
        elif word_count >= 4:
            # Use relaxed threshold for shorter statements
            threshold = relaxed_threshold
            print(f"[SmartMemory] 🔄 Using RELAXED threshold ({threshold}) for shorter text")
        else:
            # Use permissive threshold for very short but potentially valuable text
            threshold = permissive_threshold
            print(f"[SmartMemory] 💡 Using PERMISSIVE threshold ({threshold}) for edge case")
        
        if memory_score >= threshold:
            print(f"[SmartMemory] ✅ PASSED progressive filter: score {memory_score}/{threshold}")
            return True
        else:
            print(f"[SmartMemory] ❌ FAILED progressive filter: score {memory_score}/{threshold}")
            return False
    
    def _contains_emotional_state(self, text: str) -> bool:
        """🎯 Check for emotional states worth remembering"""
        text_lower = text.lower()
        
        emotion_keywords = [
            'stressed', 'worried', 'anxious', 'nervous', 'scared', 'upset',
            'excited', 'thrilled', 'happy', 'glad', 'pleased', 'proud',
            'sad', 'depressed', 'down', 'frustrated', 'angry', 'annoyed',
            'tired', 'exhausted', 'overwhelmed', 'confused', 'lost',
            'hopeful', 'optimistic', 'confident', 'motivated', 'inspired'
        ]
        
    def _extract_high_value_patterns(self, text: str) -> List[Dict]:
        """🚀 EDGE CASE EXTRACTION: High-value patterns for missed opportunities"""
        events = []
        text_lower = text.lower()
        current_date = datetime.now().strftime('%Y-%m-%d')
        current_time = datetime.now().isoformat()
        
        # HIGH-VALUE PATTERN 1: Any mention of specific restaurants/places
        place_only_patterns = [
            r'\b(mcdonalds?|mcdonald\'?s?|starbucks|walmart|target|costco)\b',
            r'\b(restaurant|cafe|shop|store|mall|park|beach|gym|library|bank)\b',
            r'\b(hospital|clinic|office|school|work|home)\b'
        ]
        
        for pattern in place_only_patterns:
            match = re.search(pattern, text_lower)
            if match:
                place = match.group(1)
                place_clean = place.replace("'", "").lower()
                events.append({
                    'type': 'life_event',
                    'topic': f'mentioned_{place_clean}',
                    'date': current_date,
                    'emotion': 'casual',
                    'status': 'pending',
                    'created': current_time,
                    'original_text': text,
                    'detected_by': 'high_value_place_pattern',
                    'confidence': 0.7
                })
                print(f"[SmartMemory] 🏢 High-value place: {place}")
        
        # HIGH-VALUE PATTERN 2: People mentions (family, friends)
        people_patterns = [
            r'\b(niece|nephew|cousin|sister|brother|mom|dad|mother|father)\b',
            r'\b(friend|friends|girlfriend|boyfriend|wife|husband)\b',
            r'\bwith\s+(\w+)\b'  # "with [person]"
        ]
        
        for pattern in people_patterns:
            match = re.search(pattern, text_lower)
            if match:
                person = match.group(1)
                if person not in ['with']:  # Skip preposition
                    events.append({
                        'type': 'life_event',
                        'topic': f'mentioned_{person.lower()}',
                        'date': current_date,
                        'emotion': 'casual',
                        'status': 'pending',
                        'created': current_time,
                        'original_text': text,
                        'detected_by': 'high_value_people_pattern',
                        'confidence': 0.6
                    })
                    print(f"[SmartMemory] 👥 High-value person: {person}")
        
        # HIGH-VALUE PATTERN 3: Activity mentions (even without time)
        activity_patterns = [
            r'\b(grabbed|got|had|ate|bought|picked|dropped|met|saw|visited)\b',
            r'\b(going|planning|scheduled|booked|arranged)\b',
            r'\b(nervous|excited|worried|happy|stressed)\s+about\b'
        ]
        
        for pattern in activity_patterns:
            if re.search(pattern, text_lower):
                # Extract the activity context
                words = text.split()
                if len(words) >= 3:  # Has some context
                    events.append({
                        'type': 'highlight',
                        'topic': f'activity_mention',
                        'date': current_date,
                        'emotion': 'casual',
                        'status': 'pending',
                        'created': current_time,
                        'original_text': text,
                        'detected_by': 'high_value_activity_pattern',
                        'confidence': 0.5
                    })
                    print(f"[SmartMemory] ⚡ High-value activity detected")
                break
        
        # HIGH-VALUE PATTERN 4: Conversational memory cues
        memory_cue_patterns = [
            r'\b(remember|mentioned|told\s+you|said)\b',
            r'\b(like\s+i\s+said|as\s+i\s+mentioned)\b',
            r'\b(oh\s+yeah|by\s+the\s+way|speaking\s+of)\b'
        ]
        
        for pattern in memory_cue_patterns:
            if re.search(pattern, text_lower):
                events.append({
                    'type': 'highlight',
                    'topic': 'conversation_reference',
                    'date': current_date,
                    'emotion': 'casual',
                    'status': 'pending',
                    'created': current_time,
                    'original_text': text,
                    'detected_by': 'high_value_memory_cue',
                    'confidence': 0.8
                })
                print(f"[SmartMemory] 💭 High-value memory cue")
                break
        
        # HIGH-VALUE PATTERN 5: Location + context combinations
        location_context_patterns = [
            r'\bat\s+(the\s+)?(\w+)',                    # "at the store"
            r'\bfrom\s+(the\s+)?(\w+)',                  # "from the office"  
            r'\bwent\s+to\s+(\w+)',                      # "went to work"
            r'\bwas\s+at\s+(\w+)',                       # "was at home"
        ]
        
        for pattern in location_context_patterns:
            match = re.search(pattern, text_lower)
            if match:
                # Safely get the first captured group
                location = match.group(1) if len(match.groups()) >= 1 else match.group(0)
                if location and len(location) > 2:  # Valid location
                    events.append({
                        'type': 'life_event',
                        'topic': f'location_context_{location.lower()}',
                        'date': current_date,
                        'emotion': 'casual',
                        'status': 'pending',
                        'created': current_time,
                        'original_text': text,
                        'detected_by': 'high_value_location_context',
                        'confidence': 0.6
                    })
                    print(f"[SmartMemory] 📍 High-value location context: {location}")
                    break
        
        return events
    
    def _contains_emotional_state(self, text: str) -> bool:
        """🎯 Check for emotional states worth remembering"""
        text_lower = text.lower()
        
        emotion_keywords = [
            'stressed', 'worried', 'anxious', 'nervous', 'scared', 'upset',
            'excited', 'thrilled', 'happy', 'glad', 'pleased', 'proud',
            'sad', 'depressed', 'down', 'frustrated', 'angry', 'annoyed',
            'tired', 'exhausted', 'overwhelmed', 'confused', 'lost',
            'hopeful', 'optimistic', 'confident', 'motivated', 'inspired'
        ]
        
        has_emotion = any(emotion in text_lower for emotion in emotion_keywords)
        if has_emotion:
            print(f"[SmartMemory] 😊 Emotional content detected")
        
        return has_emotion
    
    def _micro_pattern_extraction(self, text: str, current_date: str) -> List[Dict]:
        """🔬 MICRO-PATTERNS: Ultra-sensitive extraction for smallest edge cases"""
        events = []
        text_lower = text.lower().strip()
        current_time = datetime.now().isoformat()
        
        print(f"[MicroPatterns] 🔬 Ultra-sensitive analysis: '{text}'")
        
        # MICRO 1: Single words with high memory value
        high_value_single_words = [
            'mcdonalds', 'mcdonald', 'starbucks', 'walmart', 'target',
            'dentist', 'doctor', 'hospital', 'appointment',
            'birthday', 'party', 'wedding', 'funeral',
            'nervous', 'excited', 'worried', 'stressed'
        ]
        
        for word in high_value_single_words:
            if word in text_lower:
                events.append({
                    'type': 'highlight',
                    'topic': f'mentioned_{word}',
                    'date': current_date,
                    'emotion': 'casual',
                    'status': 'pending',
                    'created': current_time,
                    'original_text': text,
                    'detected_by': 'micro_single_word',
                    'confidence': 0.4
                })
                print(f"[MicroPatterns] 📍 Single word: {word}")
                break
        
        # MICRO 2: Two-word combinations
        micro_patterns = [
            r'\bat\s+mcdonalds?\b',        # "at mcdonalds" 
            r'\bwith\s+friends?\b',        # "with friends"
            r'\bmy\s+niece\b',             # "my niece"
            r'\bnext\s+week\b',            # "next week"
            r'\byesterday\s+\w+',          # "yesterday [anything]"
            r'\btoday\s+\w+',              # "today [anything]"
            r'\btomorrow\s+\w+',           # "tomorrow [anything]"
            r'\bwent\s+\w+',               # "went [anywhere]"
            r'\bhad\s+\w+',                # "had [anything]"
            r'\bmet\s+\w+',                # "met [anyone]"
            r'\bsaw\s+\w+',                # "saw [anyone]"
            r'\bbought\s+\w+',             # "bought [anything]"
            r'\bvisited\s+\w+',            # "visited [anywhere]"
        ]
        
        for pattern in micro_patterns:
            match = re.search(pattern, text_lower)
            if match:
                matched_text = match.group(0)
                events.append({
                    'type': 'highlight',
                    'topic': f'micro_pattern_{matched_text.replace(" ", "_")}',
                    'date': current_date,
                    'emotion': 'casual',
                    'status': 'pending',
                    'created': current_time,
                    'original_text': text,
                    'detected_by': 'micro_two_word_pattern',
                    'confidence': 0.5
                })
                print(f"[MicroPatterns] 🔗 Two-word pattern: {matched_text}")
                break
        
        # MICRO 3: Context-free emotional expressions
        if not events:  # Only if nothing else found
            emotion_context_patterns = [
                r'\b(nervous|excited|worried|happy|sad|stressed)\s+(about|for)\b',
                r'\b(looking\s+forward|can\'t\s+wait|dreading)\b',
                r'\b(love|hate|enjoy|dislike)\s+\w+',
                r'\b(remember|forgot|mentioned)\b'
            ]
            
            for pattern in emotion_context_patterns:
                if re.search(pattern, text_lower):
                    events.append({
                        'type': 'highlight',
                        'topic': 'emotional_context',
                        'date': current_date,
                        'emotion': 'emotional',
                        'status': 'pending',
                        'created': current_time,
                        'original_text': text,
                        'detected_by': 'micro_emotion_context',
                        'confidence': 0.6
                    })
                    print(f"[MicroPatterns] 😊 Emotional context")
                    break
        
        # MICRO 4: Question-based memory extraction (override question blocking)
        if '?' in text_lower and not events:
            memory_question_indicators = [
                'where did i', 'what did i', 'when did i', 'who did i',
                'where was i', 'what was i', 'who was i with',
                'where am i going', 'what do i have', 'when is my',
                'what am i', 'where are we', 'what are we doing'
            ]
            
            for indicator in memory_question_indicators:
                if indicator in text_lower:
                    events.append({
                        'type': 'highlight',
                        'topic': 'memory_question',
                        'date': current_date,
                        'emotion': 'casual',
                        'status': 'pending',
                        'created': current_time,
                        'original_text': text,
                        'detected_by': 'micro_memory_question',
                        'confidence': 0.7
                    })
                    print(f"[MicroPatterns] ❓ Memory question: {indicator}")
                    break
        
        # MICRO 5: Any time reference + any noun (last resort)
        if not events and len(text.split()) >= 3:
            time_refs = ['today', 'yesterday', 'tomorrow', 'earlier', 'later', 'morning', 'afternoon', 'evening']
            words = text_lower.split()
            
            has_time_ref = any(time_ref in words for time_ref in time_refs)
            has_noun = len([w for w in words if len(w) > 3 and w.isalpha()]) >= 1
            
            if has_time_ref and has_noun:
                events.append({
                    'type': 'highlight',
                    'topic': 'time_plus_context',
                    'date': current_date,
                    'emotion': 'casual',
                    'status': 'pending',
                    'created': current_time,
                    'original_text': text,
                    'detected_by': 'micro_time_plus_noun',
                    'confidence': 0.3
                })
                print(f"[MicroPatterns] ⏰ Time + context detected")
        
        print(f"[MicroPatterns] 🔬 Found {len(events)} micro-pattern events")
        return events
    
    def _try_llm_extraction(self, text: str, current_date: str, current_time: str) -> List[Dict]:
        """Try LLM-based extraction (factored out for multi-pass approach)"""
        detection_prompt = f"""You are a smart memory assistant. Analyze this user message and extract any events, appointments, or life situations that should be remembered.

Current date: {current_date}
Current time: {current_time}
User message: "{text}"

Extract events in this exact JSON format (return empty array if no events):
[
  {{
    "type": "appointment|life_event|highlight",
    "topic": "brief_description",
    "date": "YYYY-MM-DD",
    "time": "HH:MM" or null,
    "emotion": "happy|excited|stressful|sensitive|casual|supportive",
    "priority": "high|medium|low",
    "original_text": "{text}"
  }}
]

Guidelines:
- "appointment": Time-specific events (dentist, meeting, class)
- "life_event": Emotional/social events (birthdays, visits, funerals)  
- "highlight": General feelings/thoughts to remember
- Calculate dates: tomorrow = {(datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')}
- Be smart about natural language: "going to Emily's tomorrow, it's her birthday" = birthday visit
- Emotion should match the event type
- Priority: high=urgent/sensitive, medium=social/fun, low=routine
- ONLY extract if it's a REAL event or emotional state worth remembering
- DO NOT extract casual conversation, greetings, or questions

Examples:
"I have dentist tomorrow at 2PM" → appointment, dentist, tomorrow, 14:00, stressful, medium
"Going to Emily's tomorrow, it's her birthday" → life_event, Emily's birthday visit, tomorrow, happy, medium
"I'm really stressed about work" → highlight, work stress, today, supportive, low

Return only valid JSON array:"""

        try:
            # ✅ TOKEN OPTIMIZATION: Use optimized event detection
            from ai.llm_optimized import detect_events_optimized
            
            events = detect_events_optimized(text, current_date)
            
            # Validate and enhance events
            validated_events = []
            for event in events:
                if self._validate_event(event):
                    enhanced_event = self._enhance_event(event)
                    validated_events.append(enhanced_event)
            
            return validated_events
            
        except ImportError:
            print(f"[SmartMemory] ⚠️ Optimized detection not available, using fallback")
            return self._detect_events_fallback(text, current_date)
        except Exception as e:
            print(f"[SmartMemory] ❌ Optimized detection error: {e}")
            return self._detect_events_fallback(text, current_date)
    
    def _smart_detect_events(self, text: str) -> List[Dict]:
        """🧠 Use Hermes 3 Pro Mistral to intelligently detect events - BULLETPROOF FILTERED"""
        
        # ✅ PROGRESSIVE FILTERING SYSTEM - OPTIMIZED FOR 80-90% EXTRACTION!
        
        # Filter 1: Block pure casual conversation (more permissive now)
        if self._is_casual_conversation(text):
            return []
        
        # Filter 2: Progressive scoring system (replaces triple requirement)
        has_events = self._likely_contains_events(text)
        has_emotions = self._contains_emotional_state(text)
        
        # Use multi-pass approach
        if not has_events and not has_emotions:
            # Try high-value pattern extraction as fallback
            print(f"[SmartMemory] 🔄 Trying high-value pattern extraction for: '{text}'")
            high_value_events = self._extract_high_value_patterns(text)
            if high_value_events:
                print(f"[SmartMemory] ✅ High-value patterns detected {len(high_value_events)} events")
                return high_value_events
            else:
                print(f"[SmartMemory] ❌ No events, emotions, or high-value patterns: '{text}'")
                return []
        
        # If we get here, try the comprehensive multi-pass approach
        print(f"[SmartMemory] 🔄 Trying multi-pass extraction for: '{text}'")
        
        current_date = datetime.now().strftime('%Y-%m-%d')
        current_time = datetime.now().strftime('%H:%M')
        
        # PASS 1: Standard extraction (already tried above)
        pass1_events = []
        if has_events or has_emotions:
            pass1_events = self._try_llm_extraction(text, current_date, current_time)
            if pass1_events:
                print(f"[SmartMemory] ✅ Pass 1 (LLM) detected {len(pass1_events)} events")
                return pass1_events
        
        # PASS 2: High-value pattern extraction
        pass2_events = self._extract_high_value_patterns(text)
        if pass2_events:
            print(f"[SmartMemory] ✅ Pass 2 (high-value patterns) detected {len(pass2_events)} events")
            return pass2_events
        
        # PASS 3: Comprehensive fallback patterns
        pass3_events = self._fallback_detection(current_date, text)
        if pass3_events:
            print(f"[SmartMemory] ✅ Pass 3 (comprehensive fallback) detected {len(pass3_events)} events")
            return pass3_events
        
        # PASS 4: Micro-pattern extraction (last resort for edge cases)
        pass4_events = self._micro_pattern_extraction(text, current_date)
        if pass4_events:
            print(f"[SmartMemory] ✅ Pass 4 (micro-patterns) detected {len(pass4_events)} events")
            return pass4_events
        
        # Final fallback: If absolutely nothing found, return empty
        print(f"[SmartMemory] ❌ All extraction passes failed for: '{text}'")
        return []
    
    def _detect_events_fallback(self, text: str, current_date: str) -> List[Dict]:
        """Fallback to original LLM event detection"""
        
        current_time = datetime.now().strftime('%H:%M')
        
        # Smart prompt for event detection (original)
        detection_prompt = f"""You are a smart memory assistant. Analyze this user message and extract any events, appointments, or life situations that should be remembered.

Current date: {current_date}
Current time: {current_time}
User message: "{text}"

Extract events in this exact JSON format (return empty array if no events):
[
  {{
    "type": "appointment|life_event|highlight",
    "topic": "brief_description",
    "date": "YYYY-MM-DD",
    "time": "HH:MM" or null,
    "emotion": "happy|excited|stressful|sensitive|casual|supportive",
    "priority": "high|medium|low",
    "original_text": "{text}"
  }}
.]

Guidelines:
- "appointment": Time-specific events (dentist, meeting, class)
- "life_event": Emotional/social events (birthdays, visits, funerals)  
- "highlight": General feelings/thoughts to remember
- Calculate dates: tomorrow = {(datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')}
- Be smart about natural language: "going to Emily's tomorrow, it's her birthday" = birthday visit
- Emotion should match the event type
- Priority: high=urgent/sensitive, medium=social/fun, low=routine
- ONLY extract if it's a REAL event or emotional state worth remembering
- DO NOT extract casual conversation, greetings, or questions

Examples:
"I have dentist tomorrow at 2PM" → appointment, dentist, tomorrow, 14:00, stressful, medium
"Going to Emily's tomorrow, it's her birthday" → life_event, Emily's birthday visit, tomorrow, happy, medium
"I'm really stressed about work" → highlight, work stress, today, supportive, low

Return only valid JSON array:"""

        try:
            # ✅ TOKEN OPTIMIZATION: Use tiered extraction based on complexity
            token_limit, optimized_prompt = self._get_optimized_extraction_prompt(text, detection_prompt)
            
            # Get LLM response with optimized token usage
            messages = [
                {"role": "system", "content": "Extract events as JSON array. Simple events need brief descriptions."},
                {"role": "user", "content": optimized_prompt}
            ]
            
            llm_response = ask_kobold(messages, max_tokens=token_limit)
            
            # Clean and parse JSON response
            json_text = self._extract_json_from_response(llm_response)
            
            if json_text:
                events = json.loads(json_text)
                
                # Validate and enhance events
                validated_events = []
                for event in events:
                    if self._validate_event(event):
                        enhanced_event = self._enhance_event(event)
                        validated_events.append(enhanced_event)
                
                print(f"[SmartMemory] 🧠 Fallback detected {len(validated_events)} events from: '{text}'")
                return validated_events
            
        except Exception as e:
            print(f"[SmartMemory] ❌ Fallback analysis error: {e}")
        
        # Enhanced fallback to regex patterns for edge cases
        return self._fallback_detection(current_date, text)
    
    def _extract_json_from_response(self, response: str) -> Optional[str]:
        """Extract JSON array from LLM response"""
        try:
            # Look for JSON array in response
            import re
            
            # Find JSON array pattern
            json_match = re.search(r'\[.*?\]', response, re.DOTALL)
            if json_match:
                return json_match.group(0)
            
            # Look for individual JSON objects and wrap in array
            obj_matches = re.findall(r'\{.*?\}', response, re.DOTALL)
            if obj_matches:
                return '[' + ','.join(obj_matches) + ']'
            
        except Exception as e:
            print(f"[SmartMemory] JSON extraction error: {e}")
        
        return None
    
    def _validate_event(self, event: Dict) -> bool:
        """Validate event has required fields"""
        required_fields = ['type', 'topic', 'date', 'emotion']
        return all(field in event for field in required_fields)
    
    def _enhance_event(self, event: Dict) -> Dict:
        """Enhance event with additional fields"""
        current_time = datetime.now().isoformat()
        
        enhanced = {
            'topic': event['topic'],
            'date': event['date'],
            'time': event.get('time'),
            'emotion': event['emotion'],
            'status': 'pending',
            'type': event['type'],
            'priority': event.get('priority', 'medium'),
            'created': current_time,
            'original_text': event.get('original_text', ''),
            'detected_by': 'llm'
        }
        
        return enhanced
    
    def _fallback_detection(self, current_date: str, text: str) -> List[Dict]:
        """🚀 COMPREHENSIVE FALLBACK: Enhanced pattern detection for 80-90% extraction rate"""
        events = []
        text_lower = text.lower()
        tomorrow_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        next_week_dates = [(datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(7, 14)]
        current_time = datetime.now().isoformat()
        
        print(f"[FallbackDetection] 🔍 Analyzing: '{text}'")
        
        # 1. RESTAURANTS & FOOD (Major category)
        food_patterns = [
            # McDonald's specific patterns 
            r"(i\s+)?went\s+to\s+mcdonald'?s?\s+(earlier|today|yesterday|this\s+morning)",
            r"(i\s+)?had\s+(dinner|lunch|breakfast|food)\s+at\s+(mcdonald'?s?|kfc|starbucks)",
            r"grabbed\s+(some\s+)?food\s+at\s+(\w+)",
            r"(ate|had|got|grabbed)\s+(lunch|dinner|breakfast|food).+at\s+(\w+)",
            r"went\s+to\s+(\w+)\s+(restaurant|cafe)",
            r"(dinner|lunch|breakfast)\s+at\s+(\w+)",
            # With companions
            r"went\s+to\s+(\w+).+with\s+(\w+)",
            r"had\s+(lunch|dinner).+with\s+(\w+)\s+at\s+(\w+)",
            r"(grabbed|got|ate)\s+food.+with\s+(friends|family|\w+)",
        ]
        
        for pattern in food_patterns:
            match = re.search(pattern, text_lower)
            if match:
                # Extract place and companion info
                groups = match.groups()
                place = None
                companion = None
                
                if 'mcdonald' in text_lower:
                    place = 'mcdonalds'
                elif 'kfc' in text_lower:
                    place = 'kfc'
                elif 'starbucks' in text_lower:
                    place = 'starbucks'
                else:
                    # Try to find place in groups
                    for group in groups:
                        if group and group not in ['i', 'some', 'dinner', 'lunch', 'breakfast', 'food', 'earlier', 'today', 'yesterday', 'this', 'morning', 'grabbed', 'got', 'ate', 'had']:
                            if not place:
                                place = group
                            elif not companion and group not in ['restaurant', 'cafe']:
                                companion = group
                
                if place:
                    topic = f'visited_{place.lower()}'
                    if companion and companion not in ['friends', 'family']:
                        topic += f'_with_{companion.lower()}'
                    elif 'friends' in text_lower:
                        topic += '_with_friends'
                    elif 'family' in text_lower:
                        topic += '_with_family'
                    
                    event_date = current_date
                    if 'yesterday' in text_lower:
                        event_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
                    
                    events.append({
                        'type': 'life_event',
                        'topic': topic,
                        'date': event_date,
                        'emotion': 'casual',
                        'status': 'pending',
                        'created': current_time,
                        'original_text': text,
                        'detected_by': 'comprehensive_food_pattern'
                    })
                    print(f"[FallbackDetection] 🍽️ Food event: {place}")
                    break
        
        # 2. APPOINTMENTS & MEDICAL  
        appointment_patterns = [
            r"(dentist|doctor|vet)\s+appointment.+(tomorrow|today|next\s+week)",
            r"(appointment|meeting).+(dentist|doctor|vet)",
            r"(dentist|doctor|vet).+(tomorrow|today|at\s+\d)",
            r"(nervous|worried|scared).+(dentist|doctor|appointment)",
            r"(interview|meeting).+(tomorrow|today|next\s+week)",
        ]
        
        for pattern in appointment_patterns:
            match = re.search(pattern, text_lower)
            if match:
                appointment_type = 'appointment'
                if 'dentist' in text_lower:
                    appointment_type = 'dentist_appointment'
                elif 'doctor' in text_lower:
                    appointment_type = 'doctor_appointment'
                elif 'interview' in text_lower:
                    appointment_type = 'job_interview'
                
                event_date = current_date
                if 'tomorrow' in text_lower:
                    event_date = tomorrow_date
                elif 'next week' in text_lower:
                    event_date = next_week_dates[0]
                
                emotion = 'casual'
                if any(word in text_lower for word in ['nervous', 'worried', 'scared', 'anxious']):
                    emotion = 'stressful'
                elif any(word in text_lower for word in ['excited', 'looking forward']):
                    emotion = 'happy'
                
                events.append({
                    'type': 'appointment',
                    'topic': appointment_type,
                    'date': event_date,
                    'emotion': emotion,
                    'status': 'pending',
                    'created': current_time,
                    'original_text': text,
                    'detected_by': 'comprehensive_appointment_pattern'
                })
                print(f"[FallbackDetection] 📅 Appointment: {appointment_type}")
                break
        
        # 3. SOCIAL EVENTS & PEOPLE
        social_patterns = [
            r"(my\s+)?(niece|nephew|cousin|sister|brother|mom|dad)('s)?\s+(birthday|party)",
            r"(off\s+to|going\s+to).+(birthday|party|wedding)",
            r"(visited|saw|met)\s+(my\s+)?(\w+).+(yesterday|today|this\s+morning)",
            r"(met|meeting)\s+(\w+)\s+at\s+(\w+)",
            r"with\s+(friends|family|my\s+\w+)",
            r"(parents|family)\s+(visited|came)",
            r"(birthday|party|wedding|celebration)",
        ]
        
        for pattern in social_patterns:
            match = re.search(pattern, text_lower)
            if match:
                groups = match.groups()
                event_type = 'social_event'
                person = None
                
                if 'birthday' in text_lower:
                    event_type = 'birthday_event'
                    # Try to find person
                    for group in groups:
                        if group and group not in ['my', "'s", 'off', 'to', 'going', 'birthday', 'party', 'yesterday', 'today', 'this', 'morning']:
                            person = group
                            break
                
                elif 'met' in text_lower or 'visited' in text_lower:
                    event_type = 'meeting_event'
                    for group in groups:
                        if group and group not in ['met', 'meeting', 'visited', 'saw', 'my', 'at', 'yesterday', 'today', 'this', 'morning']:
                            person = group
                            break
                
                topic = event_type
                if person:
                    topic = f'{event_type}_{person.lower()}'
                
                event_date = current_date
                if 'yesterday' in text_lower:
                    event_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
                elif 'next week' in text_lower:
                    event_date = next_week_dates[0]
                    if 'wednesday' in text_lower:
                        event_date = next_week_dates[2]
                
                events.append({
                    'type': 'life_event',
                    'topic': topic,
                    'date': event_date,
                    'emotion': 'happy',
                    'status': 'pending',
                    'created': current_time,
                    'original_text': text,
                    'detected_by': 'comprehensive_social_pattern'
                })
                print(f"[FallbackDetection] 👥 Social event: {topic}")
                break
        
        # 4. ACTIVITIES & HOBBIES
        activity_patterns = [
            r"(played|watched|went).+(basketball|football|cinema|movie|concert)",
            r"(shopping|bought|purchased).+(yesterday|today|earlier)",
            r"(traveled|flew|drove|trip)\s+to\s+(\w+)",
            r"(cleaned|organized|repaired|fixed)",
            r"(jogging|running|exercise|gym)",
            r"(reading|finished).+(book|novel)",
            r"(camping|hiking|beach)",
        ]
        
        for pattern in activity_patterns:
            if re.search(pattern, text_lower):
                activity = 'general_activity'
                
                if 'basketball' in text_lower:
                    activity = 'played_basketball'
                elif 'cinema' in text_lower or 'movie' in text_lower:
                    activity = 'watched_movie'
                elif 'concert' in text_lower:
                    activity = 'attended_concert'
                elif 'shopping' in text_lower:
                    activity = 'went_shopping'
                elif 'travel' in text_lower or 'trip' in text_lower:
                    activity = 'traveled'
                elif 'jogging' in text_lower or 'running' in text_lower:
                    activity = 'went_jogging'
                elif 'reading' in text_lower:
                    activity = 'reading_book'
                elif 'beach' in text_lower:
                    activity = 'went_to_beach'
                elif 'camping' in text_lower:
                    activity = 'went_camping'
                
                event_date = current_date
                if 'yesterday' in text_lower:
                    event_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
                elif 'last weekend' in text_lower:
                    event_date = (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d')
                
                events.append({
                    'type': 'life_event',
                    'topic': activity,
                    'date': event_date,
                    'emotion': 'casual',
                    'status': 'pending',
                    'created': current_time,
                    'original_text': text,
                    'detected_by': 'comprehensive_activity_pattern'
                })
                print(f"[FallbackDetection] ⚡ Activity: {activity}")
                break
        
        # 5. LOCATION-ONLY PATTERNS (High-value edge cases)
        location_patterns = [
            r"\bat\s+(mcdonald'?s?|starbucks|walmart|target|costco|mall|shop|store|office|work|home|hospital|clinic)\b",
            r"\bwent\s+to\s+(the\s+)?(\w+)",
            r"\bwas\s+at\s+(the\s+)?(\w+)",
            r"\bfrom\s+(the\s+)?(\w+)",
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, text_lower)
            if match:
                groups = match.groups()
                location = None
                
                for group in groups:
                    if group and group not in ['the', 'at', 'went', 'to', 'was', 'from']:
                        location = group.replace("'", "").replace("s", "")
                        break
                
                if location and len(location) > 2:
                    events.append({
                        'type': 'life_event',
                        'topic': f'location_mention_{location.lower()}',
                        'date': current_date,
                        'emotion': 'casual',
                        'status': 'pending',
                        'created': current_time,
                        'original_text': text,
                        'detected_by': 'comprehensive_location_pattern',
                        'confidence': 0.6
                    })
                    print(f"[FallbackDetection] 📍 Location: {location}")
                    break
        
        # 6. EMOTIONAL STATES (Even without events)
        if not events:  # Only if no other events found
            emotion_patterns = [
                r"\b(nervous|excited|worried|happy|stressed|anxious|thrilled)\s+about\b",
                r"\b(looking\s+forward|can't\s+wait|dreading)\b",
            ]
            
            for pattern in emotion_patterns:
                if re.search(pattern, text_lower):
                    events.append({
                        'type': 'highlight',
                        'topic': 'emotional_state',
                        'date': current_date,
                        'emotion': 'emotional',
                        'status': 'pending',
                        'created': current_time,
                        'original_text': text,
                        'detected_by': 'comprehensive_emotion_pattern',
                        'confidence': 0.7
                    })
                    print(f"[FallbackDetection] 😊 Emotional state detected")
                    break
        
        print(f"[FallbackDetection] ✅ Found {len(events)} events with comprehensive patterns")
        return events
    
    def load_memory(self, filename: str) -> List[Dict]:
        """Load memory file"""
        file_path = os.path.join(self.memory_dir, filename)
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    return json.load(f)
            return []
        except Exception as e:
            print(f"[SmartMemory] ⚠️ Error loading {filename}: {e}")
            return []
    
    def save_memory(self, data: List[Dict], filename: str):
        """Save memory file"""
        file_path = os.path.join(self.memory_dir, filename)
        try:
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"[SmartMemory] ❌ Error saving {filename}: {e}")
    
    def check_for_natural_context_response(self) -> Optional[str]:
        """🎯 Check if we should naturally bring up memories"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Check appointments first (time-sensitive)
        response = self._check_smart_appointments(today)
        if response:
            return response
        
        # Check life events 
        response = self._check_smart_life_events(today)
        if response:
            return response
        
        # Check conversation highlights (occasionally)
        if random.random() < 0.2:  # 20% chance
            response = self._check_smart_highlights()
            if response:
                return response
        
        return None
    
    def _check_smart_appointments(self, today: str) -> Optional[str]:
        """📅 Check smart appointments"""
        for appointment in self.appointments:
            if appointment['date'] == today and appointment['status'] == 'pending':
                topic = appointment['topic']
                time_str = appointment.get('time', '')
                
                context_key = f"appointment_{appointment['date']}_{topic}"
                if context_key in self.context_used_this_session:
                    continue
                
                self.context_used_this_session.add(context_key)
                
                if time_str:
                    if 'dentist' in topic.lower():
                        responses = [
                            f"Yo! Just a heads up — {topic} at {time_str}. You ready for the drill?",
                            f"Hey, don't forget your {topic} at {time_str}! Try not to chicken out"
                        ]
                    else:
                        responses = [
                            f"Heads up — {topic} at {time_str} today. You got this!",
                            f"Don't forget your {topic} at {time_str}!"
                        ]
                else:
                    responses = [
                        f"Hey, you've got {topic} today. How you feeling about it?",
                        f"Don't forget about {topic} today!"
                    ]
                
                appointment['status'] = 'reminded'
                self.save_memory(self.appointments, 'smart_appointments.json')
                
                return random.choice(responses)
        
        return None
    
    def _check_smart_life_events(self, today: str) -> Optional[str]:
        """📝 Check smart life events"""
        for event in self.life_events:
            if event['date'] == today and event['status'] == 'pending':
                topic = event['topic']
                emotion = event['emotion']
                
                context_key = f"life_event_{event['date']}_{topic}"
                if context_key in self.context_used_this_session:
                    continue
                
                self.context_used_this_session.add(context_key)
                
                if emotion == 'sensitive':
                    responses = [
                        f"Hey, how'd the {topic} go? You alright?",
                        f"Just checking — how was the {topic}? You doing okay?"
                    ]
                elif emotion in ['happy', 'excited']:
                    responses = [
                        f"Yooo! How was the {topic}? Tell me everything!",
                        f"How'd the {topic} go?! Was it awesome?"
                    ]
                elif emotion == 'stressful':
                    responses = [
                        f"So how'd the {topic} go? You survive?",
                        f"How was the {topic}? Hope it went better than expected!"
                    ]
                else:
                    responses = [
                        f"How'd the {topic} go?",
                        f"So, how was your {topic}?"
                    ]
                
                event['status'] = 'followed_up'
                self.save_memory(self.life_events, 'smart_life_events.json')
                
                return random.choice(responses)
        
        return None
    
    def _check_smart_highlights(self) -> Optional[str]:
        """💬 Check smart conversation highlights"""
        recent_highlights = []
        cutoff_date = datetime.now() - timedelta(days=3)
        
        for highlight in self.conversation_highlights:
            created = datetime.fromisoformat(highlight['created'])
            if created >= cutoff_date and highlight['status'] == 'pending':
                context_key = f"highlight_{highlight['topic']}_{highlight['created'][:10]}"
                if context_key not in self.context_used_this_session:
                    recent_highlights.append(highlight)
        
        if recent_highlights:
            highlight = random.choice(recent_highlights)
            topic = highlight['topic']
            
            context_key = f"highlight_{topic}_{highlight['created'][:10]}"
            self.context_used_this_session.add(context_key)
            
            responses = [
                f"Hey, how's that {topic} situation going?",
                f"Any updates on {topic}?"
            ]
            
            highlight['status'] = 'followed_up'
            self.save_memory(self.conversation_highlights, 'smart_highlights.json')
            
            return random.choice(responses)
        
        return None
    
    def reset_session_context(self):
        """Reset session context"""
        self.context_used_this_session.clear()
        print(f"[SmartMemory] 🔄 Session context reset for {self.username}")
    
    def _check_for_memory_enhancement(self, text: str) -> Optional[str]:
        """🔗 Check if this text enhances existing memories (e.g., McDonald's -> McFlurry details)"""
        text_lower = text.lower().strip()
        
        # Look for food/drink details that could enhance restaurant visits
        food_enhancement_patterns = [
            (r'(mcflurry|big mac|quarter pounder|fries|nuggets|shake)', r'mcdonalds?|mcdonald'),
            (r'(whopper|chicken fries|onion rings)', r'burger king'),
            (r'(frappuccino|latte|coffee|tea)', r'starbucks'),
            (r'(pizza|pepperoni|margherita)', r'pizza|dominos|papa johns'),
            (r'(sushi|salmon|tuna|rolls)', r'sushi|japanese'),
            (r'(burger|cheese|bacon)', r'restaurant|cafe|diner')
        ]
        
        today = datetime.now().strftime('%Y-%m-%d')
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        
        for food_pattern, location_pattern in food_enhancement_patterns:
            food_match = re.search(food_pattern, text_lower)
            if food_match:
                food_item = food_match.group(1)
                
                # Search for recent memories that could be enhanced
                recent_memories = self._find_recent_location_memories(location_pattern, [today, yesterday])
                
                if recent_memories:
                    # Enhance the memory with food details
                    for memory in recent_memories:
                        self._enhance_memory_with_details(memory, text, food_item)
                    
                    return f"Added {food_item} details to {len(recent_memories)} recent memory(ies)"
        
        # Look for activity details that could enhance previous events
        activity_enhancement_patterns = [
            (r'(bought|purchased|got|picked up) (.+)', r'shopping|store|mall'),
            (r'(watched|saw) (.+)', r'cinema|theater|movie|netflix'),
            (r'(played|game of) (.+)', r'park|friends|family')
        ]
        
        for activity_pattern, context_pattern in activity_enhancement_patterns:
            activity_match = re.search(activity_pattern, text_lower)
            if activity_match:
                activity_detail = activity_match.group(2)
                
                recent_memories = self._find_recent_context_memories(context_pattern, [today, yesterday])
                
                if recent_memories:
                    for memory in recent_memories:
                        self._enhance_memory_with_details(memory, text, activity_detail)
                    
                    return f"Added {activity_detail} details to {len(recent_memories)} recent memory(ies)"
        
        return None
    
    def _find_recent_location_memories(self, location_pattern: str, dates: List[str]) -> List[Dict]:
        """Find recent memories matching location pattern"""
        matching_memories = []
        
        # Search life events
        for event in self.life_events:
            if event['date'] in dates:
                topic_lower = event['topic'].lower()
                original_lower = event.get('original_text', '').lower()
                
                if re.search(location_pattern, topic_lower) or re.search(location_pattern, original_lower):
                    matching_memories.append(event)
        
        # Search highlights
        for highlight in self.conversation_highlights:
            if highlight['date'] in dates:
                topic_lower = highlight['topic'].lower()
                original_lower = highlight.get('original_text', '').lower()
                
                if re.search(location_pattern, topic_lower) or re.search(location_pattern, original_lower):
                    matching_memories.append(highlight)
        
        return matching_memories
    
    def _find_recent_context_memories(self, context_pattern: str, dates: List[str]) -> List[Dict]:
        """Find recent memories matching context pattern"""
        matching_memories = []
        
        # Search life events
        for event in self.life_events:
            if event['date'] in dates:
                topic_lower = event['topic'].lower()
                original_lower = event.get('original_text', '').lower()
                
                if re.search(context_pattern, topic_lower) or re.search(context_pattern, original_lower):
                    matching_memories.append(event)
        
        return matching_memories
    
    def _enhance_memory_with_details(self, memory: Dict, enhancement_text: str, detail: str):
        """🔗 Enhance existing memory with additional details"""
        # Create enhancement record
        enhancement = {
            'original_memory_id': id(memory),
            'enhancement_text': enhancement_text,
            'detail_added': detail,
            'timestamp': datetime.now().isoformat(),
            'date': memory['date']
        }
        
        # Add to enhancements
        self.memory_enhancements.append(enhancement)
        
        # Update memory topic to include detail
        if 'enhanced_details' not in memory:
            memory['enhanced_details'] = []
        
        memory['enhanced_details'].append({
            'detail': detail,
            'from_text': enhancement_text,
            'timestamp': datetime.now().isoformat()
        })
        
        # Update topic to be more descriptive
        current_topic = memory['topic']
        if detail not in current_topic.lower():
            memory['topic'] = f"{current_topic} (with {detail})"
        
        # Save updated memories
        if memory in self.life_events:
            self.save_memory(self.life_events, 'smart_life_events.json')
        elif memory in self.conversation_highlights:
            self.save_memory(self.conversation_highlights, 'smart_highlights.json')
        
        self.save_memory(self.memory_enhancements, 'memory_enhancements.json')
        
        # Also update the regular memory system
        self._add_to_regular_memory(memory)
        
        print(f"[SmartMemory] 🔗 Enhanced memory '{current_topic}' with detail: {detail}")
    
    def get_enhanced_memories_for_query(self, query: str) -> List[Dict]:
        """🎯 Get memories with all enhancements for better context retrieval"""
        query_lower = query.lower()
        relevant_memories = []
        
        # Search all memory types with enhancements
        all_memories = self.life_events + self.conversation_highlights + self.appointments
        
        for memory in all_memories:
            # Check base memory
            topic_lower = memory['topic'].lower()
            original_lower = memory.get('original_text', '').lower()
            
            relevance_score = 0
            
            # Direct topic match
            if any(word in topic_lower for word in query_lower.split()):
                relevance_score += 0.8
            
            # Original text match
            if any(word in original_lower for word in query_lower.split()):
                relevance_score += 0.6
            
            # Enhanced details match
            if 'enhanced_details' in memory:
                for detail in memory['enhanced_details']:
                    detail_text = detail['detail'].lower()
                    if any(word in detail_text for word in query_lower.split()):
                        relevance_score += 0.9  # Enhanced details are highly relevant
            
            if relevance_score > 0.5:
                memory_copy = memory.copy()
                memory_copy['relevance_score'] = relevance_score
                relevant_memories.append(memory_copy)
        
        # Sort by relevance score
        relevant_memories.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        return relevant_memories[:5]  # Return top 5 most relevant
    
    def _get_optimized_extraction_prompt(self, text: str, full_prompt: str) -> tuple[int, str]:
        """🚀 Get optimized prompt and token limit based on text complexity"""
        text_lower = text.lower().strip()
        word_count = len(text.split())
        
        # Determine complexity level
        complexity_score = 0
        
        # Simple location mentions (low complexity)
        simple_patterns = [
            r'went to \w+', r'at \w+', r'visited \w+', r'from \w+',
            r'mcdonalds?', r'starbucks', r'walmart', r'target'
        ]
        
        # Complex patterns (high complexity)
        complex_patterns = [
            r'(nervous|worried|excited|stressed)', r'appointment', r'meeting',
            r'birthday', r'family', r'friends', r'tomorrow', r'next week'
        ]
        
        # Emotional patterns (medium complexity)  
        emotional_patterns = [
            r'(happy|sad|frustrated|relieved|anxious)', r'feeling', r'about'
        ]
        
        # Score complexity
        for pattern in simple_patterns:
            if re.search(pattern, text_lower):
                complexity_score += 1
        
        for pattern in emotional_patterns:
            if re.search(pattern, text_lower):
                complexity_score += 2
                
        for pattern in complex_patterns:
            if re.search(pattern, text_lower):
                complexity_score += 3
        
        # Determine tier based on complexity and word count
        if complexity_score <= 2 and word_count <= 8:
            # TIER 1: Simple extraction (50 tokens)
            token_limit = 50
            prompt = f"""Extract events from: "{text}"
Current date: {datetime.now().strftime('%Y-%m-%d')}

Return JSON: [{{"type": "highlight|life_event", "topic": "brief", "date": "YYYY-MM-DD", "emotion": "casual"}}]"""
            
            print(f"[SmartMemory] ⚡ TIER 1 extraction (50 tokens) for: '{text}'")
            
        elif complexity_score <= 5 and word_count <= 15:
            # TIER 2: Medium extraction (100 tokens)
            token_limit = 100
            prompt = f"""Smart event extractor. Extract appointments, life events, highlights from user message.

TYPES:
- appointment: Time-specific events (dentist, meeting)
- life_event: Emotional/social events (birthdays, visits) 
- highlight: General feelings/thoughts

JSON format:
[{{"type": "appointment|life_event|highlight", "topic": "brief_description", "date": "YYYY-MM-DD", "emotion": "happy|stressed|casual|etc", "priority": "high|medium|low"}}]

Extract ONLY real events worth remembering. Skip casual conversation.

Current date: {datetime.now().strftime('%Y-%m-%d')}
User message: "{text}"

Detect any events worth remembering:"""
            
            print(f"[SmartMemory] ⚡ TIER 2 extraction (100 tokens) for: '{text}'")
            
        else:
            # TIER 3: Complex extraction (200 tokens - reduced from 300)
            token_limit = 200
            prompt = full_prompt
            
            print(f"[SmartMemory] ⚡ TIER 3 extraction (200 tokens) for: '{text}'")
        
        return token_limit, prompt