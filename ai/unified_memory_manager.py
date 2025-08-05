"""
Unified Memory Manager - Single memory extraction system with context-aware threading
Created: 2025-08-04
Updated: 2025-01-22 - Added comprehensive extraction and conversation threading
Updated: 2025-01-22 - Integrated extraction coordinator for optimization
Purpose: Eliminate duplicate memory extraction calls and provide unified memory access
"""

from ai.comprehensive_memory_extractor import ComprehensiveMemoryExtractor, ExtractionResult
from typing import Optional, Dict, Any

# Import the new extraction coordinator
try:
    from ai.extraction_coordinator import (
        extract_with_coordination, 
        ExtractionType, 
        ExtractionPriority,
        get_extraction_coordinator
    )
    COORDINATOR_AVAILABLE = True
    print("[UnifiedMemory] ✅ Extraction coordinator integrated")
except ImportError as e:
    COORDINATOR_AVAILABLE = False
    print(f"[UnifiedMemory] ⚠️ Extraction coordinator not available: {e}")

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
    
    Now optimized with central coordinator for:
    - Context-aware prioritization  
    - Result sharing between components
    - Efficient KoboldCPP connection management
    - Redundancy elimination
    """
    
    # Use coordinator if available for optimization
    if COORDINATOR_AVAILABLE:
        try:
            # Extract with full coordination and optimization
            response = extract_with_coordination(
                username=username,
                text=text,
                extraction_type=ExtractionType.USER_INPUT,
                priority=None,  # Auto-determined based on context
                context={'conversation_context': conversation_context}
            )
            
            # Cache result for other modules that might need it
            text_hash = hash(text.lower().strip())
            _extraction_results_cache[text_hash] = response.result
            
            print(f"[UnifiedMemory] ✅ Coordinated extraction: {len(response.result.memory_events)} events, "
                  f"intent={response.result.intent_classification}, "
                  f"emotion={response.result.emotional_state.get('primary_emotion', 'unknown')}, "
                  f"tier={response.tier_used}, cache_hit={response.cache_hit}")
            
            return response.result
            
        except Exception as e:
            print(f"[UnifiedMemory] ⚠️ Coordinator extraction failed: {e}")
            print("[UnifiedMemory] 🔄 Falling back to direct extraction")
            # Fall through to original method
    
    # Fallback to original extraction method
    extractor = get_unified_memory_extractor(username)
    result = extractor.extract_all_from_text(text, conversation_context)
    
    # Cache result for other modules that might need it
    text_hash = hash(text.lower().strip())
    _extraction_results_cache[text_hash] = result
    
    print(f"[UnifiedMemory] ✅ Direct extraction: {len(result.memory_events)} events, intent={result.intent_classification}, emotion={result.emotional_state.get('primary_emotion', 'unknown')}")
    return result

def get_cached_extraction_result(text: str) -> Optional[ExtractionResult]:
    """Get cached extraction result to avoid duplicate processing"""
    text_hash = hash(text.lower().strip())
    return _extraction_results_cache.get(text_hash)

def extract_for_consciousness(username: str, text: str, module_name: str = "consciousness") -> ExtractionResult:
    """
    🧠 Optimized extraction for consciousness modules
    Uses coordinator with HIGH priority and consciousness-specific context
    """
    if COORDINATOR_AVAILABLE:
        try:
            response = extract_with_coordination(
                username=username,
                text=text,
                extraction_type=ExtractionType.CONSCIOUSNESS,
                priority=ExtractionPriority.HIGH,
                context={'module': module_name, 'consciousness_request': True}
            )
            
            print(f"[UnifiedMemory] 🧠 Consciousness extraction for {module_name}: "
                  f"tier={response.tier_used}, cache_hit={response.cache_hit}")
            
            return response.result
        except Exception as e:
            print(f"[UnifiedMemory] ⚠️ Consciousness extraction failed: {e}")
    
    # Fallback to regular extraction
    return extract_all_from_text(username, text)

def extract_for_memory_fusion(username1: str, username2: str, context: str) -> ExtractionResult:
    """
    🔗 Optimized extraction for memory fusion operations
    Uses coordinator with MEDIUM priority and fusion-specific context
    """
    if COORDINATOR_AVAILABLE:
        try:
            response = extract_with_coordination(
                username=username1,
                text=context,
                extraction_type=ExtractionType.MEMORY_FUSION,
                priority=ExtractionPriority.MEDIUM,
                context={'fusion_target': username2, 'memory_fusion': True}
            )
            
            print(f"[UnifiedMemory] 🔗 Memory fusion extraction: "
                  f"tier={response.tier_used}, cache_hit={response.cache_hit}")
            
            return response.result
        except Exception as e:
            print(f"[UnifiedMemory] ⚠️ Memory fusion extraction failed: {e}")
    
    # Fallback to regular extraction
    return extract_all_from_text(username1, context)

def extract_background(username: str, text: str, task_type: str = "background") -> ExtractionResult:
    """
    🔄 Optimized extraction for background processing
    Uses coordinator with LOW priority for non-urgent tasks
    """
    if COORDINATOR_AVAILABLE:
        try:
            response = extract_with_coordination(
                username=username,
                text=text,
                extraction_type=ExtractionType.BACKGROUND,
                priority=ExtractionPriority.LOW,
                context={'task_type': task_type, 'background_task': True}
            )
            
            print(f"[UnifiedMemory] 🔄 Background extraction for {task_type}: "
                  f"tier={response.tier_used}, cache_hit={response.cache_hit}")
            
            return response.result
        except Exception as e:
            print(f"[UnifiedMemory] ⚠️ Background extraction failed: {e}")
    
    # Fallback to regular extraction
    return extract_all_from_text(username, text)

def get_memory_stats() -> dict:
    """Get statistics about memory usage"""
    stats = {
        "active_users": len(_unified_extractors),
        "user_list": list(_unified_extractors.keys()),
        "cached_extractions": len(_extraction_results_cache)
    }
    
    # Add coordinator metrics if available
    if COORDINATOR_AVAILABLE:
        try:
            coordinator = get_extraction_coordinator()
            stats.update({
                "coordinator_metrics": coordinator.get_performance_metrics(),
                "coordinator_status": coordinator.get_system_status()
            })
        except Exception as e:
            print(f"[UnifiedMemory] ⚠️ Could not get coordinator stats: {e}")
    
    return stats

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