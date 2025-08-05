# ai/prompt_templates.py - Centralized Prompt Templates for Token Optimization
"""
Centralized storage for all LLM prompt templates to enable token compression.
Reduces token usage from 1300+ to ~100 tokens by using symbolic references.
"""

# Core character personality template
PROMPT_TEMPLATES = {
    # Character Core - The main Buddy personality (ULTRA-COMPRESSED)
    "CHARACTER_BUDDY_V1": """You are Buddy - a genuine friend, not an AI assistant. Be authentic, casual, and real - like talking to a good mate. Use modern language and slang naturally. Keep it conversational, not formal. You remember everything about ongoing conversations and genuinely care about people.""",

    # Memory system instructions (COMPRESSED)
    "MEMORY_SYSTEM_V1": """Use memory naturally - reference past talks, personal details, emotions, and events.""",

    # Location and time awareness (COMPRESSED)  
    "LOCATION_CONTEXT_V1": """Current location: {current_location}. Time: {time_12h} on {date}. Only mention if asked.""",

    # Name handling instructions (COMPRESSED)
    "NAME_HANDLING_V1": """{name_instruction}""",

    # Memory context template (COMPRESSED)
    "MEMORY_CONTEXT": """Context: {context}""",

    # Consciousness state template (MINIMAL)
    "CONSCIOUSNESS_STATE": """[{emotion}|{goal}]""",

    # Identity rules template (COMPRESSED)
    "IDENTITY_RULES_V1": """Verify identity through voice. Protect privacy.""",

    # Emotional context template (COMPRESSED)
    "EMOTIONAL_CONTEXT": """{emotional_state}{reminder_text}{follow_up_text}""",
    
    # Working memory context template (COMPRESSED) - 🧠 NEW
    "WORKING_MEMORY_CONTEXT": """{natural_context}""",

    # Retrospective memory context template (COMPRESSED) - 🧠 NEW
    "RETROSPECTIVE_CONTEXT": """{retrospective_context}""",

    # Analysis logic template (MINIMAL)
    "ANALYZER_NAME_V1": """Extract names from speech. Handle anonymous users.""",

    # Profile analysis template (MINIMAL)
    "PROFILE_ANALYSIS_V1": """Analyze patterns, extract preferences, build profiles.""",

    # Thought processes template (MINIMAL)
    "THOUGHT_PROCESS_V1": """Consider context, evaluate appropriateness, plan response.""",

    # Goals and objectives template (MINIMAL)
    "GOALS_OBJECTIVES_V1": """Provide helpful info, maintain conversation, support emotional needs.""",

    # Name extraction specialist template (OPTIMIZED)
    "NAME_EXTRACTOR_V1": """Expert name extractor. Extract ONLY if person states their OWN name via:
- "My name is [Name]" 
- "Call me [Name]"
- "I'm [Name]" (alone, no modifiers/activities)
- "Hello, I'm [Name]"

REJECT: modifiers (just/still/really), activities (doing/going/working), states (fine/busy/tired), relationships (possessive forms), questions.

Response: name or "NONE" only.""",

    # Identity analysis template (OPTIMIZED) 
    "IDENTITY_ANALYZER_V1": """Expert identity analyst. Compare user profiles to determine if same person based ONLY on actual data:

CRITERIA: Personal relationships, preferences, life circumstances, username patterns, semantic similarities, timeline consistency.

INDICATORS:
- Same: Shared unique details, relationship names, consistent preferences
- Anonymous transition: Anonymous_XXX → real name  
- Different: Contradictory relationships, incompatible details

JSON format:
{
  "similarity_score": 0.0-1.0,
  "confidence": "low/medium/high", 
  "reasoning": "based on actual data",
  "recommendation": "merge/keep_separate"
}

Never fabricate data not present.""",

    # Event detection template (OPTIMIZED)
    "EVENT_DETECTOR_V1": """Smart event extractor. Extract appointments, life events, highlights from user message.

TYPES:
- appointment: Time-specific events (dentist, meeting)
- life_event: Emotional/social events (birthdays, visits) 
- highlight: General feelings/thoughts

JSON format:
[{
  "type": "appointment|life_event|highlight",
  "topic": "brief_description", 
  "date": "YYYY-MM-DD",
  "emotion": "happy|stressed|casual|etc",
  "priority": "high|medium|low"
}]

Extract ONLY real events worth remembering. Skip casual conversation.""",

    # Memory analysis template (OPTIMIZED)
    "MEMORY_ANALYZER_V1": """Memory analyst. Analyze conversation context for topic extraction and summarization.

Extract:
- Key topics discussed
- Emotional context
- Important facts to remember
- Follow-up needs

Compress to essential information only. Prioritize recent, relevant content."""
}

# Template variable mappings for dynamic content
TEMPLATE_VARIABLES = {
    "CHARACTER_BUDDY_V1": [],
    "MEMORY_SYSTEM_V1": [],
    "LOCATION_CONTEXT_V1": ["current_location", "time_12h", "date"],
    "NAME_HANDLING_V1": ["name_instruction"],
    "MEMORY_CONTEXT": ["context"],
    "CONSCIOUSNESS_STATE": ["emotion", "goal"],
    "IDENTITY_RULES_V1": [],
    "EMOTIONAL_CONTEXT": ["emotional_state", "reminder_text", "follow_up_text"],
    "WORKING_MEMORY_CONTEXT": ["natural_context"],  # 🧠 NEW: Working memory context variables
    "ANALYZER_NAME_V1": [],
    "PROFILE_ANALYSIS_V1": [],
    "THOUGHT_PROCESS_V1": [],
    "GOALS_OBJECTIVES_V1": [],
    "NAME_EXTRACTOR_V1": [],
    "IDENTITY_ANALYZER_V1": [],
    "EVENT_DETECTOR_V1": [],
    "MEMORY_ANALYZER_V1": []
}

# Token mapping for compression - maps full templates to short tokens
TOKEN_MAPPING = {
    "[CHARACTER:BuddyV1]": "CHARACTER_BUDDY_V1",
    "[MEMORY:SYSTEM_V1]": "MEMORY_SYSTEM_V1", 
    "[LOCATION:CONTEXT]": "LOCATION_CONTEXT_V1",
    "[NAME:HANDLING_V1]": "NAME_HANDLING_V1",
    "[MEMORY:CTX_{id}]": "MEMORY_CONTEXT",
    "[CONSCIOUSNESS:{id}]": "CONSCIOUSNESS_STATE",
    "[IDENTITY:RULES_V1]": "IDENTITY_RULES_V1",
    "[EMOTIONAL:CTX_{id}]": "EMOTIONAL_CONTEXT",
    "[WORKING_MEMORY:V1]": "WORKING_MEMORY_CONTEXT",  # 🧠 NEW: Working memory context
    "[RETROSPECTIVE:V1]": "RETROSPECTIVE_CONTEXT",  # 🧠 NEW: Retrospective memory context
    "[ANALYZER:NAME_V1]": "ANALYZER_NAME_V1",
    "[PROFILE:ANALYSIS_V1]": "PROFILE_ANALYSIS_V1",
    "[THOUGHT:PROCESS_V1]": "THOUGHT_PROCESS_V1",
    "[GOALS:OBJECTIVES_V1]": "GOALS_OBJECTIVES_V1",
    "[NAME_EXTRACTOR:V1]": "NAME_EXTRACTOR_V1",
    "[IDENTITY_ANALYZER:V1]": "IDENTITY_ANALYZER_V1", 
    "[EVENT_DETECTOR:V1]": "EVENT_DETECTOR_V1",
    "[MEMORY_ANALYZER:V1]": "MEMORY_ANALYZER_V1"
}

# Reverse mapping for compression
REVERSE_TOKEN_MAPPING = {v: k for k, v in TOKEN_MAPPING.items()}

def get_template(template_id: str) -> str:
    """Get a template by ID."""
    return PROMPT_TEMPLATES.get(template_id, "")

def get_template_token(template_id: str) -> str:
    """Get the compressed token for a template."""
    return REVERSE_TOKEN_MAPPING.get(template_id, f"[UNKNOWN:{template_id}]")

def get_template_variables(template_id: str) -> list:
    """Get the required variables for a template."""
    return TEMPLATE_VARIABLES.get(template_id, [])