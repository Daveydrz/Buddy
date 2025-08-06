"""
Unified Memory Manager - Enterprise-Grade Memory Extraction System
Created: 2025-08-04
Updated: 2025-01-08 - Enhanced with enterprise-grade extraction coordination
Purpose: Eliminate duplicate memory extraction calls and provide unified memory access
         with enterprise-grade performance, reliability, and coordination.
"""

from ai.comprehensive_memory_extractor import ComprehensiveMemoryExtractor, ExtractionResult
from typing import Optional, Dict, Any
import os
import time

# Import enterprise-grade extraction coordinator
ENTERPRISE_EXTRACTION_AVAILABLE = False
try:
    from ai.memory_cache_manager import (
        get_memory_cache_manager,
        cache_memory_intelligent,
        get_cached_memory_intelligent,
        get_memory_cache_performance
    )
    ENTERPRISE_EXTRACTION_AVAILABLE = True
    print("[UnifiedMemory] 🏢 Enterprise-grade extraction coordination available")
except ImportError as e:
    print(f"[UnifiedMemory] ⚠️ Enterprise extraction not available: {e}")

# Delayed import of extraction coordinator to avoid circular imports
def _get_extraction_coordinator():
    """Lazy import of extraction coordinator to avoid circular imports"""
    try:
        from ai.extraction_coordinator import (
            get_extraction_coordinator, 
            extract_with_enterprise_coordination,
            ExtractionPriority, 
            InteractionType,
            get_extraction_performance_report
        )
        return (get_extraction_coordinator, extract_with_enterprise_coordination, 
                ExtractionPriority, InteractionType, get_extraction_performance_report)
    except ImportError as e:
        print(f"[UnifiedMemory] ⚠️ Extraction coordinator import failed: {e}")
        return None, None, None, None, None

# Global unified memory instances - shared across all modules
_unified_extractors = {}
_extraction_results_cache = {}

# Enterprise mode flag
ENTERPRISE_MODE = os.getenv('BUDDY_ENTERPRISE_MODE', 'true').lower() == 'true'

def get_unified_memory_extractor(username: str) -> ComprehensiveMemoryExtractor:
    """Get or create unified comprehensive memory extractor for user - shared across all systems"""
    if username not in _unified_extractors:
        _unified_extractors[username] = ComprehensiveMemoryExtractor(username)
        print(f"[UnifiedMemory] 🧠 Created comprehensive extractor for: {username}")
    return _unified_extractors[username]

def extract_all_from_text(username: str, text: str, conversation_context: str = "", 
                         interaction_type: str = "text_chat", priority: str = "normal") -> ExtractionResult:
    """
    🎯 ENTERPRISE-GRADE MEMORY EXTRACTION - Single point for all extraction operations
    
    Uses enterprise-grade coordination when available for:
    - Context-aware prioritization
    - Smart request batching and result sharing  
    - Connection pooling and circuit breaking
    - Progressive resolution strategies
    - Intelligent caching and preloading
    """
    
    if ENTERPRISE_EXTRACTION_AVAILABLE and ENTERPRISE_MODE:
        # Use enterprise-grade extraction coordination with lazy import
        coordinator_imports = _get_extraction_coordinator()
        get_extraction_coordinator, extract_with_enterprise_coordination, ExtractionPriority, InteractionType, get_extraction_performance_report = coordinator_imports
        
        if extract_with_enterprise_coordination:
            # Map string parameters to enums
            interaction_type_mapping = {
                "voice_to_speech": InteractionType.VOICE_TO_SPEECH,
                "text_chat": InteractionType.TEXT_CHAT,
                "background": InteractionType.BACKGROUND_PROCESSING,
                "batch": InteractionType.BATCH_OPERATION,
                "consciousness": InteractionType.CONSCIOUSNESS_UPDATE
            }
            
            priority_mapping = {
                "critical": ExtractionPriority.CRITICAL,
                "high": ExtractionPriority.HIGH,
                "normal": ExtractionPriority.NORMAL,
                "low": ExtractionPriority.LOW
            }
            
            mapped_interaction_type = interaction_type_mapping.get(interaction_type, InteractionType.TEXT_CHAT)
            mapped_priority = priority_mapping.get(priority, ExtractionPriority.NORMAL)
            
            # Check intelligent cache first
            cache_key = f"extract_{username}_{hash(text + conversation_context)}"
            cached_result = get_cached_memory_intelligent(
                cache_key, 
                context_tags={username, interaction_type, "extraction"}
            )
            
            if cached_result:
                print(f"[UnifiedMemory] 🚀 Enterprise cache hit: {text[:30]}...")
                return cached_result
            
            # Use enterprise extraction coordination
            future_result = extract_with_enterprise_coordination(
                username=username,
                text=text,
                interaction_type=mapped_interaction_type,
                priority=mapped_priority,
                conversation_context=conversation_context,
                timeout_seconds=30 if mapped_interaction_type == InteractionType.VOICE_TO_SPEECH else 60
            )
            
            # Get the actual result from the Future
            try:
                result = future_result.result(timeout=60)  # Wait up to 60 seconds for result
            except Exception as e:
                print(f"[UnifiedMemory] ❌ Enterprise extraction failed: {e}")
                # Fallback to standard extraction
                extractor = get_unified_memory_extractor(username)
                result = extractor.extract_all_from_text(text, conversation_context)
                print(f"[UnifiedMemory] 🔄 Fallback to standard extraction completed")
                return result
            
            # Cache result intelligently
            cache_memory_intelligent(
                cache_key,
                result,
                context_tags={username, interaction_type, "extraction", "enterprise"},
                invalidation_triggers={"user_logout", "context_change", "system_restart"}
            )
            
            print(f"[UnifiedMemory] 🏢 Enterprise extraction: {len(result.memory_events)} events, "
                  f"intent={result.intent_classification}")
            
            return result
        else:
            print(f"[UnifiedMemory] ⚠️ Enterprise coordinator not available, falling back to standard")
    
    # Fallback to standard extraction
    extractor = get_unified_memory_extractor(username)
    result = extractor.extract_all_from_text(text, conversation_context)
    
    # Cache result for other modules that might need it
    text_hash = hash(text.lower().strip())
    _extraction_results_cache[text_hash] = result
    
    print(f"[UnifiedMemory] ✅ Standard extraction: {len(result.memory_events)} events, "
          f"intent={result.intent_classification}, emotion={result.emotional_state.get('primary_emotion', 'unknown')}")
    return result

def extract_for_voice_interaction(username: str, text: str, conversation_context: str = "") -> ExtractionResult:
    """Optimized extraction for voice-to-speech interactions with critical priority"""
    return extract_all_from_text(
        username=username,
        text=text,
        conversation_context=conversation_context,
        interaction_type="voice_to_speech",
        priority="critical"
    )

def extract_for_background_processing(username: str, text: str, conversation_context: str = "") -> ExtractionResult:
    """Extraction for background processing with comprehensive analysis"""
    return extract_all_from_text(
        username=username,
        text=text,
        conversation_context=conversation_context,
        interaction_type="background",
        priority="low"
    )

def extract_for_consciousness_update(username: str, text: str, conversation_context: str = "") -> ExtractionResult:
    """Extraction for consciousness system updates"""
    return extract_all_from_text(
        username=username,
        text=text,
        conversation_context=conversation_context,
        interaction_type="consciousness",
        priority="high"
    )

def get_cached_extraction_result(text: str) -> Optional[ExtractionResult]:
    """Get cached extraction result to avoid duplicate processing"""
    text_hash = hash(text.lower().strip())
    return _extraction_results_cache.get(text_hash)

def get_memory_stats() -> dict:
    """Get comprehensive statistics about memory usage"""
    basic_stats = {
        "active_users": len(_unified_extractors),
        "user_list": list(_unified_extractors.keys()),
        "cached_extractions": len(_extraction_results_cache),
        "enterprise_mode": ENTERPRISE_MODE,
        "enterprise_available": ENTERPRISE_EXTRACTION_AVAILABLE
    }
    
    if ENTERPRISE_EXTRACTION_AVAILABLE:
        try:
            # Add enterprise performance metrics with lazy import
            coordinator_imports = _get_extraction_coordinator()
            get_extraction_coordinator, extract_with_enterprise_coordination, ExtractionPriority, InteractionType, get_extraction_performance_report = coordinator_imports
            
            if get_extraction_performance_report:
                enterprise_metrics = get_extraction_performance_report()
                cache_metrics = get_memory_cache_performance()
                
                basic_stats.update({
                    "enterprise_extraction": enterprise_metrics,
                    "intelligent_cache": cache_metrics
                })
        except Exception as e:
            print(f"[UnifiedMemory] ⚠️ Could not get enterprise metrics: {e}")
    
    return basic_stats

def clear_memory_cache():
    """Clear all memory instances (for testing)"""
    global _unified_extractors, _extraction_results_cache
    _unified_extractors.clear()
    _extraction_results_cache.clear()
    
    if ENTERPRISE_EXTRACTION_AVAILABLE:
        try:
            # Clear enterprise caches as well
            from ai.memory_cache_manager import get_memory_cache_manager
            cache_manager = get_memory_cache_manager()
            cache_manager.invalidate_cache("cache_clear")
        except Exception as e:
            print(f"[UnifiedMemory] ⚠️ Could not clear enterprise cache: {e}")
    
    print("[UnifiedMemory] 🧹 Memory cache cleared")

def check_conversation_threading(username: str, text: str) -> Optional[Dict[str, Any]]:
    """Check if text is part of ongoing conversation thread"""
    extractor = get_unified_memory_extractor(username)
    return extractor._check_memory_enhancement(text)

def optimize_memory_operations(username: str, operations: list, operation_type: str = "read") -> str:
    """Batch multiple memory operations for efficiency"""
    if ENTERPRISE_EXTRACTION_AVAILABLE:
        try:
            from ai.memory_cache_manager import batch_memory_operations
            return batch_memory_operations(operations, operation_type, username)
        except Exception as e:
            print(f"[UnifiedMemory] ⚠️ Could not batch operations: {e}")
    
    # Fallback to individual operations
    for operation in operations:
        if operation_type == "extract" and "text" in operation:
            extract_all_from_text(username, operation["text"])
    
    return f"fallback_batch_{int(time.time())}"

def preload_contextual_memory(username: str, context_pattern: str):
    """Preload memory based on predicted context patterns"""
    if ENTERPRISE_EXTRACTION_AVAILABLE:
        try:
            from ai.memory_cache_manager import preload_memory_contextual
            preload_memory_contextual(context_pattern, username)
        except Exception as e:
            print(f"[UnifiedMemory] ⚠️ Could not preload memory: {e}")

def get_enterprise_performance_summary() -> Dict[str, Any]:
    """Get comprehensive enterprise performance summary"""
    if not ENTERPRISE_EXTRACTION_AVAILABLE:
        return {"error": "Enterprise features not available"}
    
    try:
        coordinator_imports = _get_extraction_coordinator()
        get_extraction_coordinator, extract_with_enterprise_coordination, ExtractionPriority, InteractionType, get_extraction_performance_report = coordinator_imports
        
        if not get_extraction_performance_report:
            return {"error": "Enterprise coordinator not available"}
            
        extraction_metrics = get_extraction_performance_report()
        cache_metrics = get_memory_cache_performance()
        memory_stats = get_memory_stats()
        
        return {
            "extraction_coordination": extraction_metrics,
            "intelligent_caching": cache_metrics,
            "unified_memory": memory_stats,
            "enterprise_mode": ENTERPRISE_MODE,
            "summary": {
                "total_requests": extraction_metrics.get("extraction_metrics", {}).get("total_requests", 0),
                "cache_hit_rate": cache_metrics.get("cache_stats", {}).get("hit_rate_percent", 0),
                "active_users": len(_unified_extractors),
                "status": "Enterprise-grade optimization active"
            }
        }
    except Exception as e:
        return {"error": f"Could not generate performance summary: {e}"}

# Auto-initialize enterprise mode message
if ENTERPRISE_EXTRACTION_AVAILABLE and ENTERPRISE_MODE:
    print("[UnifiedMemory] 🏢 Enterprise-grade extraction coordination ENABLED")
    print("[UnifiedMemory] 🚀 Advanced features: Context-aware prioritization, intelligent caching, connection pooling")
else:
    print("[UnifiedMemory] 📊 Standard extraction mode (set BUDDY_ENTERPRISE_MODE=true for enterprise features)")