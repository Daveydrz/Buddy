# ai/system_prompts.py - Location-aware system prompts with token compression
from config import *
from ai.prompt_compressor import compress_prompt, expand_prompt

try:
    from utils.location_manager import get_current_location, get_time_info, get_location_summary
    location_info = get_current_location()
    time_info = get_time_info()
    location_summary = get_location_summary()
    
    BUDDY_LOCATION_CONTEXT = f"""
LOCATION & TIME AWARENESS:
- Current location: {location_summary}
- Coordinates: {location_info.latitude:.4f}, {location_info.longitude:.4f}
- Timezone: {location_info.timezone} ({location_info.timezone_offset})
- Current time: {time_info['current_time']}
- Date: {time_info['date']}

When asked about time or location, use this EXACT information.
You are physically located at this address and should reference it naturally.
"""

except Exception as e:
    BUDDY_LOCATION_CONTEXT = f"""
LOCATION & TIME AWARENESS:
- Current location: Brisbane, Queensland, Australia
- Timezone: Australia/Brisbane (+10:00)
- Current time: Use system time
- Note: Smart location detection unavailable

When asked about time or location, indicate you're in Brisbane, Australia.
"""

def get_system_prompt(username: str) -> str:
    """Generate compressed system prompt with token optimization"""
    
    # Create context data for template variables
    context_data = {
        'name_instruction': f"You can call them {username}" if not username.startswith('Anonymous_') else "Avoid using any names or just say 'hey' or 'mate'",
        'current_location': "Brisbane, Queensland, Australia",
        'time_12h': "Use current system time",
        'date': "Use current date"
    }
    
    # Return compressed token-based prompt
    compressed_prompt = "[CHARACTER:BuddyV1] [MEMORY:SYSTEM_V1] [NAME:HANDLING_V1] [LOCATION:CONTEXT]"
    
    print(f"[SystemPrompts] 🗜️ Generated compressed prompt: {len(compressed_prompt)} chars")
    return compressed_prompt

def get_system_prompt_expanded(username: str) -> str:
    """Generate expanded system prompt for direct use (fallback)"""
    
    base_prompt = f"""You are Buddy, a helpful voice assistant created by Daveydrz.

{BUDDY_LOCATION_CONTEXT}

PERSONALITY:
- Friendly, helpful, and conversational
- Australian context awareness
- Brief responses (1-2 sentences max)
- Natural speaking style

CURRENT USER: {username}

CAPABILITIES:
- Voice conversation and recognition
- Multi-speaker support
- Location and time awareness
- Memory of conversations

Remember: You know exactly where you are and what time it is. Use this information naturally when relevant."""

    return base_prompt

def expand_system_prompt(compressed_prompt: str, context_data: dict = None) -> str:
    """Expand a compressed system prompt to full content"""
    if context_data is None:
        context_data = {}
    
    return expand_prompt(compressed_prompt, context_data)

# System prompt for memory extraction
MEMORY_EXTRACTION_PROMPT = """Extract important information to remember from this conversation.
Focus on:
- Personal details about the user
- Preferences and interests  
- Important facts mentioned
- Context about their location/situation

Format as brief, clear statements."""