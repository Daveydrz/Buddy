"""
Unified Memory Manager - Enterprise-Grade Memory Extraction System
Created: 2025-08-04
Updated: 2025-01-08 - Enhanced with enterprise-grade extraction coordination
Purpose: Eliminate duplicate memory extraction calls and provide unified memory access
         with enterprise-grade performance, reliability, and coordination.
"""

from ai.comprehensive_memory_extractor import ComprehensiveMemoryExtractor, ExtractionResult
from typing import Optional, Dict, Any, List
import os
import time

# Import memory system for retrieval functions
try:
    from ai.memory import get_user_memory
    MEMORY_SYSTEM_AVAILABLE = True
except ImportError as e:
    print(f"[UnifiedMemory] ⚠️ Memory system not available for retrieval: {e}")
    MEMORY_SYSTEM_AVAILABLE = False

# Import enterprise-grade extraction coordinator
ENTERPRISE_EXTRACTION_AVAILABLE = False
try:
    from ai.extraction_coordinator import (
        get_extraction_coordinator, 
        extract_with_enterprise_coordination,
        ExtractionPriority, 
        InteractionType,
        get_extraction_performance_report
    )
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
        # Use enterprise-grade extraction coordination
        
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

def get_all_activities(username: str, activity_type: str = None, sort_by_recency: bool = True) -> List[Dict[str, Any]]:
    """
    Comprehensive retrieval: Get all activities with optional type filtering
    Sorted by recency for immediate access with error handling
    """
    try:
        extractor = get_unified_memory_extractor(username)
        memory = get_user_memory(username)
        
        all_activities = []
        
        # Get activities from different memory stores
        activity_files = [
            'smart_appointments.json',
            'smart_life_events.json', 
            'smart_highlights.json',
            'conversation_threads.json'
        ]
        
        for filename in activity_files:
            activities = extractor.load_memory(filename)
            for activity in activities:
                # Standardize activity format
                standardized = {
                    "type": activity.get("type", "unknown"),
                    "topic": activity.get("topic", ""),
                    "date": activity.get("date", ""),
                    "time": activity.get("time"),
                    "location": activity.get("location"),
                    "people": activity.get("people", []),
                    "details": activity.get("details", ""),
                    "emotion": activity.get("emotion", "neutral"),
                    "priority": activity.get("priority", "medium"),
                    "status": activity.get("status", "unknown"),
                    "category": activity.get("category", "activities"),
                    "original_text": activity.get("original_text", ""),
                    "source": filename.replace('.json', '')
                }
                
                # Apply type filter if specified
                if activity_type is None or standardized["type"] == activity_type:
                    all_activities.append(standardized)
        
        # Add personal facts that are activities
        if hasattr(memory, 'personal_facts'):
            for fact_key, fact in memory.personal_facts.items():
                if fact.category in ['activities', 'plans', 'states']:
                    standardized = {
                        "type": fact.category,
                        "topic": fact.key.replace('_', ' '),
                        "date": fact.date_learned.split()[0] if ' ' in fact.date_learned else fact.date_learned,
                        "time": None,
                        "location": None,
                        "people": fact.related_entities if hasattr(fact, 'related_entities') else [],
                        "details": fact.value,
                        "emotion": "neutral",
                        "priority": "medium",
                        "status": fact.current_status.value if hasattr(fact.current_status, 'value') else str(fact.current_status),
                        "category": fact.category,
                        "original_text": fact.source_context if hasattr(fact, 'source_context') else "",
                        "source": "personal_facts"
                    }
                    
                    # Apply type filter if specified
                    if activity_type is None or standardized["category"] == activity_type:
                        all_activities.append(standardized)
        
        # Sort by recency if requested
        if sort_by_recency:
            all_activities.sort(key=lambda x: x.get("date", ""), reverse=True)
        
        print(f"[UnifiedMemory] 📋 Retrieved {len(all_activities)} activities for {username}"
              f"{f' (filtered by {activity_type})' if activity_type else ''}")
        
        return all_activities
        
    except Exception as e:
        print(f"[UnifiedMemory] ❌ Failed to retrieve activities: {e}")
        return []

def get_activities_by_type(username: str) -> Dict[str, List[Dict[str, Any]]]:
    """Get activities grouped by type for easier access"""
    try:
        all_activities = get_all_activities(username, sort_by_recency=True)
        
        grouped = {
            "location_visits": [],
            "reading_activities": [],
            "learning_states": [],
            "future_plans": [],
            "current_activities": [],
            "other": []
        }
        
        for activity in all_activities:
            activity_type = activity.get("type", "").lower()
            
            if "visit" in activity_type or activity.get("location"):
                grouped["location_visits"].append(activity)
            elif "read" in activity_type:
                grouped["reading_activities"].append(activity)
            elif "learn" in activity_type or "study" in activity_type:
                grouped["learning_states"].append(activity)
            elif activity.get("status") == "future" or "plan" in activity_type:
                grouped["future_plans"].append(activity)
            elif activity.get("status") == "current":
                grouped["current_activities"].append(activity)
            else:
                grouped["other"].append(activity)
        
        return grouped
        
    except Exception as e:
        print(f"[UnifiedMemory] ❌ Failed to group activities: {e}")
        return {}

def search_activities(username: str, query: str) -> List[Dict[str, Any]]:
    """Search activities by text query across all fields"""
    try:
        all_activities = get_all_activities(username)
        query_lower = query.lower()
        
        matching_activities = []
        
        for activity in all_activities:
            # Check if query matches any field
            searchable_text = " ".join([
                str(activity.get("topic", "")),
                str(activity.get("details", "")),
                str(activity.get("location", "")),
                " ".join(activity.get("people", [])),
                str(activity.get("original_text", ""))
            ]).lower()
            
            if query_lower in searchable_text:
                # Add relevance score
                activity["relevance_score"] = searchable_text.count(query_lower)
                matching_activities.append(activity)
        
        # Sort by relevance score (descending) then by recency
        matching_activities.sort(key=lambda x: (x.get("relevance_score", 0), x.get("date", "")), reverse=True)
        
        print(f"[UnifiedMemory] 🔍 Found {len(matching_activities)} activities matching '{query}'")
        
        return matching_activities
        
    except Exception as e:
        print(f"[UnifiedMemory] ❌ Search failed: {e}")
        return []

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
            # Add enterprise performance metrics
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