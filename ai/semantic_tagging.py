"""
Semantic Tagging - Semantic analysis and content tagging system
Created: 2025-01-17
Purpose: Analyze content for semantic meaning, intent, and context tagging
"""

import json
import re
import time
import os
from typing import Dict, List, Any, Optional, Set, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib

class SemanticCategory(Enum):
    QUESTION = "question"
    STATEMENT = "statement"
    REQUEST = "request"
    COMMAND = "command"
    GREETING = "greeting"
    FAREWELL = "farewell"
    EMOTION = "emotion"
    OPINION = "opinion"
    FACT = "fact"
    PERSONAL_INFO = "personal_info"
    TECHNICAL = "technical"
    CREATIVE = "creative"
    EDUCATIONAL = "educational"
    ENTERTAINMENT = "entertainment"
    PROBLEM_SOLVING = "problem_solving"

class IntentCategory(Enum):
    INFORMATION_SEEKING = "information_seeking"
    HELP_REQUEST = "help_request"
    CONVERSATION = "conversation"
    TASK_COMPLETION = "task_completion"
    LEARNING = "learning"
    ENTERTAINMENT = "entertainment"
    PROBLEM_REPORTING = "problem_reporting"
    FEEDBACK = "feedback"
    SOCIAL_INTERACTION = "social_interaction"
    PERSONAL_SHARING = "personal_sharing"

class EmotionalTone(Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    EXCITED = "excited"
    FRUSTRATED = "frustrated"
    CURIOUS = "curious"
    CONCERNED = "concerned"
    HUMOROUS = "humorous"
    SERIOUS = "serious"
    FRIENDLY = "friendly"

class ComplexityLevel(Enum):
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    ADVANCED = "advanced"

@dataclass
class SemanticTag:
    """Individual semantic tag with confidence score"""
    tag: str
    category: str
    confidence: float
    source: str
    context: Dict[str, Any]
    timestamp: str
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()

@dataclass
class SemanticAnalysis:
    """Complete semantic analysis of content"""
    content_id: str
    original_text: str
    semantic_categories: List[SemanticCategory]
    intent_categories: List[IntentCategory]
    emotional_tone: EmotionalTone
    complexity_level: ComplexityLevel
    key_concepts: List[str]
    entities: Dict[str, List[str]]
    semantic_tags: List[SemanticTag]
    confidence_score: float
    processing_time: float
    timestamp: str
    user: str
    context: Dict[str, Any]
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()
        if not self.content_id:
            self.content_id = hashlib.md5(self.original_text.encode()).hexdigest()[:16]

class SemanticTagger:
    """Semantic analysis and tagging system"""
    
    def __init__(self, tag_cache_file: str = "semantic_tags_cache.json"):
        self.tag_cache_file = tag_cache_file
        self.tag_cache: Dict[str, SemanticAnalysis] = {}
        
        # Pattern libraries for semantic analysis
        self.question_patterns = [
            r'\bwhat\b.*\?', r'\bhow\b.*\?', r'\bwhen\b.*\?', r'\bwhere\b.*\?', 
            r'\bwhy\b.*\?', r'\bwho\b.*\?', r'\bwhich\b.*\?', r'\bcan you\b.*\?',
            r'\bcould you\b.*\?', r'\bwould you\b.*\?', r'\bis it\b.*\?', r'\bare you\b.*\?'
        ]
        
        self.request_patterns = [
            r'\bplease\b.*', r'\bcan you\b.*', r'\bcould you\b.*', r'\bwould you\b.*',
            r'\bhelp me\b.*', r'\bi need\b.*', r'\bi want\b.*', r'\bi\'d like\b.*'
        ]
        
        self.command_patterns = [
            r'^\b(tell|show|explain|describe|list|find|get|create|make|do|run|execute)\b',
            r'^\b(start|stop|pause|resume|continue|finish|complete)\b'
        ]
        
        self.greeting_patterns = [
            r'\b(hello|hi|hey|greetings|good morning|good afternoon|good evening)\b',
            r'\bhow are you\b', r'\bnice to meet\b'
        ]
        
        self.farewell_patterns = [
            r'\b(goodbye|bye|farewell|see you|talk to you|catch you)\b',
            r'\bgood night\b', r'\btake care\b', r'\buntil next time\b'
        ]
        
        self.emotion_indicators = {
            EmotionalTone.POSITIVE: ['happy', 'great', 'awesome', 'excellent', 'wonderful', 'amazing', 'fantastic', 'love', 'enjoy'],
            EmotionalTone.NEGATIVE: ['sad', 'angry', 'frustrated', 'annoyed', 'disappointed', 'terrible', 'awful', 'hate', 'dislike'],
            EmotionalTone.EXCITED: ['excited', 'thrilled', 'pumped', 'energetic', 'enthusiastic', '!', 'wow', 'incredible'],
            EmotionalTone.FRUSTRATED: ['frustrated', 'annoying', 'difficult', 'hard', 'challenging', 'confusing', 'stuck'],
            EmotionalTone.CURIOUS: ['curious', 'wondering', 'interested', 'intrigued', 'fascinating', 'how does', 'why does'],
            EmotionalTone.HUMOROUS: ['funny', 'hilarious', 'joke', 'laugh', 'amusing', 'witty', 'haha', 'lol'],
            EmotionalTone.FRIENDLY: ['friend', 'buddy', 'pal', 'nice', 'kind', 'pleasant', 'warm']
        }
        
        self.complexity_indicators = {
            ComplexityLevel.SIMPLE: ['what', 'how', 'basic', 'simple', 'easy', 'quick'],
            ComplexityLevel.MODERATE: ['explain', 'understand', 'learn', 'compare', 'analyze'],
            ComplexityLevel.COMPLEX: ['comprehensive', 'detailed', 'thorough', 'advanced', 'complex', 'intricate'],
            ComplexityLevel.ADVANCED: ['expert', 'professional', 'sophisticated', 'technical', 'specialized', 'in-depth']
        }
        
        self.topic_keywords = {
            'technology': ['computer', 'software', 'programming', 'code', 'algorithm', 'data', 'AI', 'machine learning', 'internet'],
            'science': ['research', 'experiment', 'theory', 'hypothesis', 'study', 'analysis', 'scientific', 'physics', 'chemistry'],
            'health': ['health', 'medical', 'doctor', 'medicine', 'symptom', 'treatment', 'wellness', 'fitness', 'nutrition'],
            'education': ['learn', 'study', 'school', 'university', 'course', 'lesson', 'teach', 'education', 'knowledge'],
            'business': ['business', 'company', 'market', 'profit', 'strategy', 'management', 'finance', 'investment'],
            'entertainment': ['movie', 'music', 'game', 'book', 'show', 'entertainment', 'fun', 'hobby', 'leisure'],
            'personal': ['family', 'friend', 'relationship', 'personal', 'life', 'experience', 'feeling', 'emotion'],
            'travel': ['travel', 'trip', 'vacation', 'country', 'city', 'location', 'journey', 'destination'],
            'food': ['food', 'eat', 'cook', 'recipe', 'restaurant', 'meal', 'cuisine', 'ingredient'],
            'sports': ['sport', 'game', 'team', 'player', 'competition', 'exercise', 'fitness', 'athletics']
        }
        
        self.entity_patterns = {
            'person': r'\b([A-Z][a-z]+ [A-Z][a-z]+)\b',
            'place': r'\b(in|at|from|to) ([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b',
            'organization': r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*(?:\s+(?:Inc|Corp|Ltd|LLC|Company))?)\b',
            'date': r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}[/-]\d{1,2}[/-]\d{1,2})\b',
            'time': r'\b(\d{1,2}:\d{2}(?:\s*(?:AM|PM))?)\b',
            'number': r'\b(\d+(?:\.\d+)?)\b',
            'email': r'\b([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\b',
            'url': r'\b(https?://[^\s]+)\b'
        }
        
        self.load_tag_cache()
        
        print(f"[SemanticTagger] 🏷️ Initialized with {len(self.tag_cache)} cached analyses")
        
    def load_tag_cache(self):
        """Load cached semantic analyses"""
        try:
            if os.path.exists(self.tag_cache_file):
                with open(self.tag_cache_file, 'r') as f:
                    data = json.load(f)
                    
                for analysis_data in data.get('analyses', []):
                    if isinstance(analysis_data, dict):
                        # Reconstruct SemanticAnalysis object
                        analysis = SemanticAnalysis(
                            content_id=analysis_data.get('content_id', ''),
                            original_text=analysis_data.get('original_text', ''),
                            semantic_categories=[SemanticCategory(cat) for cat in analysis_data.get('semantic_categories', [])],
                            intent_categories=[IntentCategory(cat) for cat in analysis_data.get('intent_categories', [])],
                            emotional_tone=EmotionalTone(analysis_data.get('emotional_tone', 'neutral')),
                            complexity_level=ComplexityLevel(analysis_data.get('complexity_level', 'moderate')),
                            key_concepts=analysis_data.get('key_concepts', []),
                            entities=analysis_data.get('entities', {}),
                            semantic_tags=[
                                SemanticTag(**tag_data) for tag_data in analysis_data.get('semantic_tags', [])
                            ],
                            confidence_score=analysis_data.get('confidence_score', 0.5),
                            processing_time=analysis_data.get('processing_time', 0.0),
                            timestamp=analysis_data.get('timestamp', ''),
                            user=analysis_data.get('user', ''),
                            context=analysis_data.get('context', {})
                        )
                        self.tag_cache[analysis.content_id] = analysis
                        
                print(f"[SemanticTagger] ✅ Loaded semantic tag cache")
            else:
                print(f"[SemanticTagger] 📄 No existing tag cache found")
                
        except Exception as e:
            print(f"[SemanticTagger] ❌ Error loading tag cache: {e}")
            
    def save_tag_cache(self):
        """Save semantic analyses to cache"""
        try:
            analyses_data = []
            for analysis in self.tag_cache.values():
                analysis_data = asdict(analysis)
                # Convert enums to values for serialization
                analysis_data['semantic_categories'] = [cat.value for cat in analysis.semantic_categories]
                analysis_data['intent_categories'] = [cat.value for cat in analysis.intent_categories]
                analysis_data['emotional_tone'] = analysis.emotional_tone.value
                analysis_data['complexity_level'] = analysis.complexity_level.value
                analyses_data.append(analysis_data)
                
            data = {
                'analyses': analyses_data,
                'last_updated': datetime.now().isoformat(),
                'metadata': {
                    'total_analyses': len(self.tag_cache),
                    'cache_size_mb': len(json.dumps(analyses_data)) / (1024 * 1024)
                }
            }
            
            with open(self.tag_cache_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
                
        except Exception as e:
            print(f"[SemanticTagger] ❌ Error saving tag cache: {e}")
            
    def analyze_content(self, text: str, user: str = "", context: Dict[str, Any] = None) -> SemanticAnalysis:
        """Perform comprehensive semantic analysis of content"""
        start_time = time.time()
        
        try:
            content_id = hashlib.md5(text.encode()).hexdigest()[:16]
            
            # Check cache first
            if content_id in self.tag_cache:
                cached_analysis = self.tag_cache[content_id]
                print(f"[SemanticTagger] 💾 Using cached analysis for content")
                return cached_analysis
            
            text_lower = text.lower()
            
            # Analyze semantic categories
            semantic_categories = self._analyze_semantic_categories(text, text_lower)
            
            # Analyze intent
            intent_categories = self._analyze_intent(text, text_lower)
            
            # Analyze emotional tone
            emotional_tone = self._analyze_emotional_tone(text_lower)
            
            # Analyze complexity
            complexity_level = self._analyze_complexity(text_lower)
            
            # Extract key concepts
            key_concepts = self._extract_key_concepts(text_lower)
            
            # Extract entities
            entities = self._extract_entities(text)
            
            # Generate semantic tags
            semantic_tags = self._generate_semantic_tags(text, semantic_categories, intent_categories, emotional_tone)
            
            # Calculate overall confidence
            confidence_score = self._calculate_confidence_score(text, semantic_categories, intent_categories)
            
            processing_time = time.time() - start_time
            
            analysis = SemanticAnalysis(
                content_id=content_id,
                original_text=text,
                semantic_categories=semantic_categories,
                intent_categories=intent_categories,
                emotional_tone=emotional_tone,
                complexity_level=complexity_level,
                key_concepts=key_concepts,
                entities=entities,
                semantic_tags=semantic_tags,
                confidence_score=confidence_score,
                processing_time=processing_time,
                timestamp=datetime.now().isoformat(),
                user=user,
                context=context or {}
            )
            
            # Cache the analysis
            self.tag_cache[content_id] = analysis
            
            # Save cache periodically
            if len(self.tag_cache) % 10 == 0:
                self.save_tag_cache()
            
            print(f"[SemanticTagger] ✅ Analyzed content: {len(semantic_categories)} categories, {len(semantic_tags)} tags")
            
            return analysis
            
        except Exception as e:
            print(f"[SemanticTagger] ❌ Error analyzing content: {e}")
            # Return minimal analysis
            return SemanticAnalysis(
                content_id="error",
                original_text=text,
                semantic_categories=[SemanticCategory.STATEMENT],
                intent_categories=[IntentCategory.CONVERSATION],
                emotional_tone=EmotionalTone.NEUTRAL,
                complexity_level=ComplexityLevel.MODERATE,
                key_concepts=[],
                entities={},
                semantic_tags=[],
                confidence_score=0.1,
                processing_time=0.0,
                timestamp=datetime.now().isoformat(),
                user=user,
                context=context or {}
            )
            
    def _analyze_semantic_categories(self, text: str, text_lower: str) -> List[SemanticCategory]:
        """Analyze semantic categories of the text"""
        categories = []
        
        # Question detection
        if any(re.search(pattern, text_lower) for pattern in self.question_patterns) or text.endswith('?'):
            categories.append(SemanticCategory.QUESTION)
            
        # Request detection
        if any(re.search(pattern, text_lower) for pattern in self.request_patterns):
            categories.append(SemanticCategory.REQUEST)
            
        # Command detection
        if any(re.search(pattern, text_lower) for pattern in self.command_patterns):
            categories.append(SemanticCategory.COMMAND)
            
        # Greeting detection
        if any(re.search(pattern, text_lower) for pattern in self.greeting_patterns):
            categories.append(SemanticCategory.GREETING)
            
        # Farewell detection
        if any(re.search(pattern, text_lower) for pattern in self.farewell_patterns):
            categories.append(SemanticCategory.FAREWELL)
            
        # Personal information detection
        if any(phrase in text_lower for phrase in ['i am', 'i live', 'my name', 'i work', 'i like', 'i have']):
            categories.append(SemanticCategory.PERSONAL_INFO)
            
        # Opinion detection
        if any(phrase in text_lower for phrase in ['i think', 'i believe', 'in my opinion', 'i feel that']):
            categories.append(SemanticCategory.OPINION)
            
        # Emotion detection
        if any(word in text_lower for emotion_words in self.emotion_indicators.values() for word in emotion_words):
            categories.append(SemanticCategory.EMOTION)
            
        # Technical content detection
        if any(word in text_lower for word in self.topic_keywords.get('technology', [])):
            categories.append(SemanticCategory.TECHNICAL)
            
        # Default to statement if no specific category found
        if not categories:
            categories.append(SemanticCategory.STATEMENT)
            
        return categories
        
    def _analyze_intent(self, text: str, text_lower: str) -> List[IntentCategory]:
        """Analyze intent categories"""
        intents = []
        
        # Information seeking
        if any(word in text_lower for word in ['what', 'how', 'when', 'where', 'why', 'explain', 'tell me']):
            intents.append(IntentCategory.INFORMATION_SEEKING)
            
        # Help request
        if any(phrase in text_lower for phrase in ['help', 'assist', 'support', 'guide', 'stuck', 'problem']):
            intents.append(IntentCategory.HELP_REQUEST)
            
        # Learning
        if any(word in text_lower for word in ['learn', 'understand', 'teach', 'study', 'explain']):
            intents.append(IntentCategory.LEARNING)
            
        # Entertainment
        if any(word in text_lower for word in ['fun', 'game', 'joke', 'story', 'entertainment']):
            intents.append(IntentCategory.ENTERTAINMENT)
            
        # Personal sharing
        if any(phrase in text_lower for phrase in ['i am', 'my life', 'i feel', 'personally', 'i experienced']):
            intents.append(IntentCategory.PERSONAL_SHARING)
            
        # Feedback
        if any(word in text_lower for word in ['thanks', 'feedback', 'good', 'bad', 'excellent', 'terrible']):
            intents.append(IntentCategory.FEEDBACK)
            
        # Default to conversation
        if not intents:
            intents.append(IntentCategory.CONVERSATION)
            
        return intents
        
    def _analyze_emotional_tone(self, text_lower: str) -> EmotionalTone:
        """Analyze emotional tone of the text"""
        emotion_scores = {}
        
        for emotion, indicators in self.emotion_indicators.items():
            score = sum(1 for indicator in indicators if indicator in text_lower)
            if score > 0:
                emotion_scores[emotion] = score
                
        if emotion_scores:
            return max(emotion_scores, key=emotion_scores.get)
        else:
            return EmotionalTone.NEUTRAL
            
    def _analyze_complexity(self, text_lower: str) -> ComplexityLevel:
        """Analyze complexity level of the text"""
        complexity_scores = {}
        
        for level, indicators in self.complexity_indicators.items():
            score = sum(1 for indicator in indicators if indicator in text_lower)
            if score > 0:
                complexity_scores[level] = score
                
        # Also consider text length and vocabulary
        word_count = len(text_lower.split())
        unique_words = len(set(text_lower.split()))
        
        if word_count > 50 or unique_words > 30:
            complexity_scores[ComplexityLevel.COMPLEX] = complexity_scores.get(ComplexityLevel.COMPLEX, 0) + 1
        elif word_count > 20 or unique_words > 15:
            complexity_scores[ComplexityLevel.MODERATE] = complexity_scores.get(ComplexityLevel.MODERATE, 0) + 1
        else:
            complexity_scores[ComplexityLevel.SIMPLE] = complexity_scores.get(ComplexityLevel.SIMPLE, 0) + 1
            
        if complexity_scores:
            return max(complexity_scores, key=complexity_scores.get)
        else:
            return ComplexityLevel.MODERATE
            
    def _extract_key_concepts(self, text_lower: str) -> List[str]:
        """Extract key concepts from text"""
        concepts = []
        
        # Find topic-related concepts
        for topic, keywords in self.topic_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                concepts.append(topic)
                
        # Extract important nouns (simplified approach)
        words = text_lower.split()
        important_words = [word for word in words if len(word) > 4 and word.isalpha()]
        
        # Remove common words
        common_words = {'this', 'that', 'with', 'have', 'will', 'from', 'they', 'been', 'have', 'their', 'would', 'could', 'should'}
        important_words = [word for word in important_words if word not in common_words]
        
        concepts.extend(important_words[:5])  # Top 5 important words
        
        return list(set(concepts))  # Remove duplicates
        
    def _extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract named entities from text"""
        entities = {}
        
        for entity_type, pattern in self.entity_patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                if isinstance(matches[0], tuple):
                    # For patterns with groups, extract the relevant group
                    entities[entity_type] = [match[-1] for match in matches]
                else:
                    entities[entity_type] = list(matches)
                    
        return entities
        
    def _generate_semantic_tags(self, text: str, semantic_categories: List[SemanticCategory], 
                               intent_categories: List[IntentCategory], emotional_tone: EmotionalTone) -> List[SemanticTag]:
        """Generate semantic tags based on analysis"""
        tags = []
        
        # Category-based tags
        for category in semantic_categories:
            tags.append(SemanticTag(
                tag=category.value,
                category="semantic",
                confidence=0.8,
                source="category_analysis",
                context={"analysis_type": "semantic_category"},
                timestamp=datetime.now().isoformat()
            ))
            
        # Intent-based tags
        for intent in intent_categories:
            tags.append(SemanticTag(
                tag=intent.value,
                category="intent",
                confidence=0.7,
                source="intent_analysis",
                context={"analysis_type": "intent_category"},
                timestamp=datetime.now().isoformat()
            ))
            
        # Emotional tone tag
        tags.append(SemanticTag(
            tag=emotional_tone.value,
            category="emotion",
            confidence=0.6,
            source="emotion_analysis",
            context={"analysis_type": "emotional_tone"},
            timestamp=datetime.now().isoformat()
        ))
        
        return tags
        
    def _calculate_confidence_score(self, text: str, semantic_categories: List[SemanticCategory], 
                                  intent_categories: List[IntentCategory]) -> float:
        """Calculate overall confidence score for the analysis"""
        base_score = 0.5
        
        # Increase confidence based on text length
        word_count = len(text.split())
        if word_count > 5:
            base_score += 0.1
        if word_count > 15:
            base_score += 0.1
            
        # Increase confidence based on number of detected categories
        if len(semantic_categories) > 1:
            base_score += 0.1
        if len(intent_categories) > 1:
            base_score += 0.1
            
        # Increase confidence for clear patterns
        if any(category in [SemanticCategory.QUESTION, SemanticCategory.GREETING, SemanticCategory.FAREWELL] 
               for category in semantic_categories):
            base_score += 0.2
            
        return min(1.0, base_score)
        
    def get_semantic_summary(self, text: str, user: str = "") -> Dict[str, Any]:
        """Get a summary of semantic analysis"""
        analysis = self.analyze_content(text, user)
        
        return {
            "content_id": analysis.content_id,
            "semantic_categories": [cat.value for cat in analysis.semantic_categories],
            "intent_categories": [cat.value for cat in analysis.intent_categories],
            "emotional_tone": analysis.emotional_tone.value,
            "complexity_level": analysis.complexity_level.value,
            "key_concepts": analysis.key_concepts,
            "entities": analysis.entities,
            "confidence_score": analysis.confidence_score,
            "processing_time": analysis.processing_time
        }
        
    def get_tags_for_llm_context(self, text: str, user: str = "") -> str:
        """Get semantic tags formatted for LLM context"""
        analysis = self.analyze_content(text, user)
        
        tag_strings = []
        
        # Add primary categories
        if analysis.semantic_categories:
            tag_strings.append(f"SEMANTIC:{','.join([cat.value for cat in analysis.semantic_categories])}")
            
        if analysis.intent_categories:
            tag_strings.append(f"INTENT:{','.join([cat.value for cat in analysis.intent_categories])}")
            
        tag_strings.append(f"TONE:{analysis.emotional_tone.value}")
        tag_strings.append(f"COMPLEXITY:{analysis.complexity_level.value}")
        
        if analysis.key_concepts:
            tag_strings.append(f"CONCEPTS:{','.join(analysis.key_concepts[:3])}")  # Top 3 concepts
            
        return f"[{' | '.join(tag_strings)}]"

# Global semantic tagger instance
semantic_tagger = SemanticTagger()

def analyze_content_semantics(text: str, user: str = "") -> Dict[str, Any]:
    """Analyze content for semantic meaning and tags"""
    return semantic_tagger.get_semantic_summary(text, user)

def get_semantic_tags_for_llm(text: str, user: str = "") -> str:
    """Get semantic tags for LLM context integration"""
    return semantic_tagger.get_tags_for_llm_context(text, user)

def analyze_text_semantic_full(text: str, user: str = "", context: Dict[str, Any] = None) -> SemanticAnalysis:
    """Get full semantic analysis object"""
    return semantic_tagger.analyze_content(text, user, context)

if __name__ == "__main__":
    # Test the semantic tagger
    print("Testing Semantic Tagger")
    
    test_texts = [
        "Hello! How are you doing today?",
        "Can you please help me understand how machine learning works?",
        "I'm feeling really frustrated with this programming problem.",
        "What's the weather like in Brisbane?",
        "Thanks! That was really helpful and exactly what I needed."
    ]
    
    for text in test_texts:
        print(f"\nAnalyzing: '{text}'")
        summary = analyze_content_semantics(text, "test_user")
        print(f"Categories: {summary['semantic_categories']}")
        print(f"Intent: {summary['intent_categories']}")
        print(f"Tone: {summary['emotional_tone']}")
        print(f"Complexity: {summary['complexity_level']}")
        
        llm_tags = get_semantic_tags_for_llm(text, "test_user")
        print(f"LLM Tags: {llm_tags}")