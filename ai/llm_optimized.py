# ai/llm_optimized.py - Token-Optimized LLM Functions
"""
Optimized LLM calling functions that use the token compression system
to reduce token usage from ~800 to ~50-100 tokens per call.
"""

import json
import re
from typing import Dict, List, Optional, Any
from ai.chat import ask_kobold
from ai.prompt_templates import get_template, get_template_token
from ai.prompt_compressor import PromptCompressor

# Global compressor instance
_compressor = PromptCompressor()

def ask_kobold_optimized(template_id: str, user_content: str, max_tokens: int = 200, context_data: Dict[str, Any] = None) -> str:
    """
    Optimized LLM call using compressed prompts.
    
    Args:
        template_id: Template ID (e.g., "NAME_EXTRACTOR_V1")
        user_content: User message content
        max_tokens: Maximum tokens for response
        context_data: Optional context data for template variables
        
    Returns:
        LLM response string
    """
    if context_data is None:
        context_data = {}
    
    # Get the template
    system_template = get_template(template_id)
    if not system_template:
        raise ValueError(f"Template not found: {template_id}")
    
    # Create compressed token reference
    compressed_token = get_template_token(template_id)
    
    # Expand for actual LLM call
    expanded_system = get_template(template_id)
    if not expanded_system:
        raise ValueError(f"Failed to expand template: {template_id}")
    
    # Fill in any template variables if the template has them
    try:
        # Some templates might have variables to fill
        expanded_system = expanded_system.format(**context_data)
    except KeyError:
        # Template doesn't use variables, use as-is
        pass
    except Exception as e:
        print(f"[LLMOptimized] ⚠️ Template formatting error: {e}")
        # Use template as-is
    
    # Create messages
    messages = [
        {"role": "system", "content": expanded_system},
        {"role": "user", "content": user_content}
    ]
    
    print(f"[LLMOptimized] 📤 Template: {template_id} → {len(compressed_token)} chars → {len(expanded_system)} chars")
    
    # Call LLM
    return ask_kobold(messages, max_tokens)

def extract_name_optimized(text: str) -> Optional[str]:
    """
    Optimized name extraction using token compression.
    
    Args:
        text: User input text to analyze
        
    Returns:
        Extracted name or None
    """
    print(f"[NameExtractorOptimized] 🔍 Analyzing: '{text}'")
    
    try:
        # Use optimized prompt
        response = ask_kobold_optimized(
            template_id="NAME_EXTRACTOR_V1",
            user_content=f'Text: "{text}"\n\nExtract name if person is introducing themselves, or respond "NONE":',
            max_tokens=20
        )
        
        # Clean response
        cleaned = response.strip().upper()
        if cleaned == "NONE" or not cleaned:
            return None
            
        # Extract first word only
        potential_name = response.strip().split()[0]
        
        # Validate it's a reasonable name
        if potential_name and potential_name.isalpha() and len(potential_name) >= 2 and len(potential_name) <= 20:
            name = potential_name.title()
            print(f"[NameExtractorOptimized] ✅ Extracted: {name}")
            return name
        
        print(f"[NameExtractorOptimized] ❌ Invalid name: {potential_name}")
        return None
        
    except Exception as e:
        print(f"[NameExtractorOptimized] ❌ Error: {e}")
        return None

def analyze_user_similarity_optimized(user1_profile: str, user2_profile: str) -> tuple[float, str]:
    """
    Optimized user similarity analysis using token compression.
    
    Args:
        user1_profile: First user's profile data
        user2_profile: Second user's profile data
        
    Returns:
        Tuple of (similarity_score, reasoning)
    """
    print(f"[IdentityAnalyzerOptimized] 🔍 Analyzing user similarity...")
    
    try:
        # Create analysis prompt
        analysis_content = f"""User Profile 1:
{user1_profile}

User Profile 2:
{user2_profile}

Analyze if these profiles belong to the same person based on the data provided."""
        
        # Use optimized prompt
        response = ask_kobold_optimized(
            template_id="IDENTITY_ANALYZER_V1",
            user_content=analysis_content,
            max_tokens=200
        )
        
        # Extract JSON response
        json_match = re.search(r'\{.*?\}', response, re.DOTALL)
        if json_match:
            try:
                analysis = json.loads(json_match.group(0))
                similarity = float(analysis.get("similarity_score", 0.0))
                reasoning = analysis.get("reasoning", "LLM analysis")
                
                print(f"[IdentityAnalyzerOptimized] 📊 Similarity: {similarity:.2f}")
                print(f"[IdentityAnalyzerOptimized] 💭 Reasoning: {reasoning}")
                
                return similarity, reasoning
                
            except (json.JSONDecodeError, ValueError) as e:
                print(f"[IdentityAnalyzerOptimized] ❌ JSON parse error: {e}")
        
        # Fallback
        print(f"[IdentityAnalyzerOptimized] ⚠️ Using fallback analysis")
        return 0.1, "Fallback analysis - LLM response parsing failed"
        
    except Exception as e:
        print(f"[IdentityAnalyzerOptimized] ❌ Error: {e}")
        return 0.0, f"Analysis error: {e}"

def detect_events_optimized(text: str, current_date: str) -> List[Dict]:
    """
    Optimized event detection using token compression.
    
    Args:
        text: User message text
        current_date: Current date in YYYY-MM-DD format
        
    Returns:
        List of detected events
    """
    print(f"[EventDetectorOptimized] 🔍 Analyzing: '{text}'")
    
    try:
        # Create detection prompt
        detection_content = f"""Current date: {current_date}
User message: "{text}"

Detect any events worth remembering:"""
        
        # Use optimized prompt
        response = ask_kobold_optimized(
            template_id="EVENT_DETECTOR_V1",
            user_content=detection_content,
            max_tokens=300
        )
        
        # Extract JSON array
        json_match = re.search(r'\[.*?\]', response, re.DOTALL)
        if json_match:
            try:
                events = json.loads(json_match.group(0))
                print(f"[EventDetectorOptimized] 📅 Detected {len(events)} events")
                return events
                
            except json.JSONDecodeError as e:
                print(f"[EventDetectorOptimized] ❌ JSON parse error: {e}")
        
        # Try individual JSON objects
        obj_matches = re.findall(r'\{.*?\}', response, re.DOTALL)
        if obj_matches:
            try:
                events = [json.loads(obj) for obj in obj_matches]
                print(f"[EventDetectorOptimized] 📅 Detected {len(events)} events (individual objects)")
                return events
            except json.JSONDecodeError:
                pass
        
        print(f"[EventDetectorOptimized] ❌ No valid events detected")
        return []
        
    except Exception as e:
        print(f"[EventDetectorOptimized] ❌ Error: {e}")
        return []

def analyze_memory_context_optimized(conversation_text: str, memory_context: str) -> str:
    """
    Optimized memory context analysis using token compression.
    
    Args:
        conversation_text: Recent conversation content
        memory_context: Existing memory context
        
    Returns:
        Analyzed and compressed memory context
    """
    print(f"[MemoryAnalyzerOptimized] 🧠 Analyzing memory context...")
    
    try:
        # Create analysis prompt
        analysis_content = f"""Recent conversation:
{conversation_text}

Existing memory context:
{memory_context}

Extract key information to remember:"""
        
        # Use optimized prompt
        response = ask_kobold_optimized(
            template_id="MEMORY_ANALYZER_V1",
            user_content=analysis_content,
            max_tokens=250
        )
        
        print(f"[MemoryAnalyzerOptimized] 📝 Analysis complete")
        return response.strip()
        
    except Exception as e:
        print(f"[MemoryAnalyzerOptimized] ❌ Error: {e}")
        return memory_context  # Fallback to original

# Utility function for token counting
def estimate_token_savings(original_prompt: str, template_id: str) -> Dict[str, int]:
    """
    Estimate token savings from using optimized prompts.
    
    Args:
        original_prompt: The original full prompt
        template_id: The optimized template ID
        
    Returns:
        Dictionary with token counts and savings
    """
    from ai.prompt_compressor import estimate_tokens
    
    # Original tokens
    original_tokens = estimate_tokens(original_prompt)
    
    # Optimized tokens (template + typical user content)
    template = get_template(template_id)
    optimized_tokens = estimate_tokens(template) + 50  # Estimate for user content
    
    # Savings
    savings = original_tokens - optimized_tokens
    savings_percent = (savings / original_tokens) * 100 if original_tokens > 0 else 0
    
    return {
        "original_tokens": original_tokens,
        "optimized_tokens": optimized_tokens,
        "savings_tokens": savings,
        "savings_percent": savings_percent
    }

# Export optimized functions
__all__ = [
    'ask_kobold_optimized',
    'extract_name_optimized', 
    'analyze_user_similarity_optimized',
    'detect_events_optimized',
    'analyze_memory_context_optimized',
    'estimate_token_savings'
]