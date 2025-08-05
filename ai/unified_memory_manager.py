"""
Unified Memory Manager - Single memory extraction system with context-aware threading
Created: 2025-08-04
Updated: 2025-01-22 - Added comprehensive extraction and conversation threading
Purpose: Eliminate duplicate memory extraction calls and provide unified memory access
"""

from ai.comprehensive_memory_extractor import ComprehensiveMemoryExtractor, ExtractionResult
from typing import Optional, Dict, Any

# Global unified memory instances - shared across all modules
_unified_extractors = {}
_extraction_results_cache = {}

def get_unified_memory_extractor(username: str) -> ComprehensiveMemoryExtractor:
    """Get or create unified comprehensive memory extractor for user - shared across all systems"""
    if username not in _unified_extractors:
        _unified_extractors[username] = ComprehensiveMemoryExtractor(username)
        print(f"[UnifiedMemory] 🧠 Created comprehensive extractor for: {username}")
    return _unified_extractors[username]

def extract_all_from_text(username: str, text: str, conversation_context: str = "") -> ExtractionResult:
    """
    🎯 SINGLE POINT OF MEMORY EXTRACTION - all modules use this
    Extracts memory, intent, emotion, threading in ONE LLM call
    """
    extractor = get_unified_memory_extractor(username)
    result = extractor.extract_all_from_text(text, conversation_context)
    
    # Cache result for other modules that might need it
    text_hash = hash(text.lower().strip())
    _extraction_results_cache[text_hash] = result
    
    print(f"[UnifiedMemory] ✅ Extracted: {len(result.memory_events)} events, intent={result.intent_classification}, emotion={result.emotional_state.get('primary_emotion', 'unknown')}")
    return result

def get_cached_extraction_result(text: str) -> Optional[ExtractionResult]:
    """Get cached extraction result to avoid duplicate processing"""
    text_hash = hash(text.lower().strip())
    return _extraction_results_cache.get(text_hash)

def get_memory_stats() -> dict:
    """Get statistics about memory usage"""
    return {
        "active_users": len(_unified_extractors),
        "user_list": list(_unified_extractors.keys()),
        "cached_extractions": len(_extraction_results_cache)
    }

def clear_memory_cache():
    """Clear all memory instances (for testing)"""
    global _unified_extractors, _extraction_results_cache
    _unified_extractors.clear()
    _extraction_results_cache.clear()
    print("[UnifiedMemory] 🧹 Memory cache cleared")

def check_conversation_threading(username: str, text: str) -> Optional[Dict[str, Any]]:
    """Check if text is part of ongoing conversation thread"""
    extractor = get_unified_memory_extractor(username)
    return extractor._check_memory_enhancement(text)