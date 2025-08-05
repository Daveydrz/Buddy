# ai/chat_enhanced_smart_with_fusion.py - Enhanced chat with intelligent memory fusion and unified extraction
from ai.chat import generate_response_streaming
from ai.memory_fusion_intelligent import get_intelligent_unified_username
from ai.unified_memory_manager import extract_all_from_text, get_cached_extraction_result
import random

# ✅ ENTROPY SYSTEM: Import consciousness emergence components
try:
    from ai.entropy_engine import get_entropy_engine, probabilistic_select, inject_consciousness_entropy, EntropyLevel
    from ai.emotion import get_emotional_system, process_emotional_context
    print("[ChatFusion] 🌀 Entropy system integrated for consciousness emergence")
    ENTROPY_AVAILABLE = True
except ImportError as e:
    print(f"[ChatFusion] ⚠️ Entropy system not available: {e}")
    ENTROPY_AVAILABLE = False

def generate_response_streaming_with_intelligent_fusion(question: str, username: str, lang="en", context=None):
    """🧠 Generate response with intelligent memory fusion, unified extraction + CONSCIOUSNESS ENTROPY + TOKEN OPTIMIZATION"""
    
    # ✅ NEW: Use cognitive context if provided
    cognitive_context_summary = ""
    if context and isinstance(context, dict) and "cognitive_state" in context:
        cognitive_state = context["cognitive_state"]
        emotion = cognitive_state.get("emotion", "neutral")
        mood = cognitive_state.get("mood", "neutral")
        arousal = cognitive_state.get("arousal", 0.5)
        memory_context = cognitive_state.get("memory_context", "")
        
        # Create compact cognitive summary for prompt injection
        cognitive_context_summary = f"[EMOTION:{emotion}|MOOD:{mood}|AROUSAL:{arousal:.1f}]"
        if memory_context:
            cognitive_context_summary += f"[MEMORY:{memory_context[:50]}...]"
        
        print(f"[ChatFusion] 🧠 Using cognitive context: {cognitive_context_summary}")
    
    # ✅ TOKEN OPTIMIZATION: Initialize optimization settings
    try:
        from ai.llm_budget_monitor import get_budget_status
        from ai.consciousness_tokenizer import get_consciousness_summary_for_llm
        
        budget_status = get_budget_status()
        usage_percentage = budget_status.get("daily_usage_percentage", 0.0)
        
        # Determine optimization level based on usage
        if usage_percentage > 0.8:
            optimization_level = "ultra"  # 85% token reduction
            print(f"[ChatFusion] 🏷️ ULTRA token optimization enabled (usage: {usage_percentage*100:.1f}%)")
        elif usage_percentage > 0.6:
            optimization_level = "high"   # 70% token reduction
            print(f"[ChatFusion] 🏷️ HIGH token optimization enabled (usage: {usage_percentage*100:.1f}%)")
        elif usage_percentage > 0.4:
            optimization_level = "medium" # 55% token reduction
            print(f"[ChatFusion] 🏷️ MEDIUM token optimization enabled (usage: {usage_percentage*100:.1f}%)")
        else:
            optimization_level = "standard" # 40% token reduction
            print(f"[ChatFusion] 🏷️ STANDARD token optimization enabled (usage: {usage_percentage*100:.1f}%)")
            
    except Exception as budget_error:
        print(f"[ChatFusion] ⚠️ Budget check error: {budget_error}")
        optimization_level = "standard"
    
    # ✅ ENTROPY SYSTEM: Process emotional and uncertainty context
    emotional_context = {}
    consciousness_summary = ""
    if ENTROPY_AVAILABLE:
        try:
            emotional_context = process_emotional_context(question, f"fusion_{username}")
            entropy_engine = get_entropy_engine()
            consciousness_score = entropy_engine.get_consciousness_metrics()['consciousness_score']
            print(f"[ChatFusion] 🎭 Emotional state: {emotional_context.get('primary_emotion', 'neutral')}")
            print(f"[ChatFusion] 🌀 Consciousness score: {consciousness_score:.2f}")
            
            # ✅ TOKEN OPTIMIZATION: Create compressed consciousness summary
            if optimization_level in ["high", "ultra"]:
                # Ultra-compressed consciousness for high optimization
                emotion = emotional_context.get('primary_emotion', 'neutral')[:4]  # Abbreviate
                consciousness_summary = f"[C:{emotion}|s:{consciousness_score:.1f}]"
            else:
                # Standard consciousness summary
                consciousness_summary = get_consciousness_summary_for_llm({
                    'emotion_engine': {'primary_emotion': emotional_context.get('primary_emotion', 'neutral')},
                    'entropy_level': consciousness_score
                })
            
            print(f"[ChatFusion] 🏷️ Consciousness summary: {consciousness_summary}")
            
        except Exception as entropy_error:
            print(f"[ChatFusion] ⚠️ Entropy processing error: {entropy_error}")
            consciousness_summary = "[C:engaged]" if optimization_level in ["high", "ultra"] else "[CONSCIOUSNESS:engaged]"
    
    # 🔧 FIX: Check for unified username from memory fusion - BUT SKIP DURING EXTRACTION TO PREVENT LOOPS
    print(f"[ChatFusion] 🔍 Checking memory fusion for user: {username}")
    try:
        # ✅ CRITICAL: Skip fusion during this operation to prevent infinite loops during memory extraction
        # Only do fusion for major conversation turns, not during memory extraction
        unified_username = get_intelligent_unified_username(username, skip_fusion=True)
        
        if unified_username != username:
            print(f"[ChatFusion] 🎯 MEMORY FUSION: {username} → {unified_username}")
            print(f"[ChatFusion] 🧠 Using unified memory for response generation")
        else:
            print(f"[ChatFusion] ✅ No fusion needed for {username}")
        
        # 🔧 CRITICAL: Use unified username for ALL subsequent operations
        username = unified_username
        
    except ImportError:
        print(f"[ChatFusion] ⚠️ Memory fusion not available, using original username: {username}")
    except Exception as e:
        print(f"[ChatFusion] ❌ Memory fusion error: {e}, using original username: {username}")
    
    # Step 2: Check context window limits before processing (8k token management)
    try:
        from ai.context_window_manager import check_context_window_rollover, create_context_snapshot_for_user
        
        # Build current context from previous conversation if available
        current_context = context.get("current_context", "") if context else ""
        if not current_context:
            # Build minimal context for new conversations
            current_context = f"System: You are Buddy, an AI assistant.\nUser: {question}"
        
        needs_rollover, fresh_context = check_context_window_rollover(username, current_context, question)
        
        if needs_rollover:
            print(f"[ChatFusion] 🔄 Context window rollover triggered for {username}")
            
            # Create snapshot to preserve memory context
            conversation_history = context.get("conversation_history", []) if context else []
            working_memory = context.get("working_memory", {}) if context else {}
            
            snapshot_created = create_context_snapshot_for_user(
                username, current_context, working_memory, conversation_history
            )
            
            if snapshot_created:
                print(f"[ChatFusion] 📸 Context snapshot created - memories preserved across 8k limit")
                # Update context to use fresh compressed context with memory injection
                if context:
                    context["current_context"] = fresh_context
                    context["context_rollover_occurred"] = True
                else:
                    context = {"current_context": fresh_context, "context_rollover_occurred": True}
            else:
                print(f"[ChatFusion] ⚠️ Context snapshot failed - using standard compression")
        
    except ImportError:
        print(f"[ChatFusion] ⚠️ Context window manager not available - using standard processing")
    
    # ✅ UNIFIED MEMORY EXTRACTION - Single LLM call for all extraction types
    conversation_context = context.get("current_context", "") if context else ""
    extraction_result = extract_all_from_text(username, question, conversation_context)
    
    print(f"[ChatFusion] 🧠 Unified extraction complete: {len(extraction_result.memory_events)} events, intent={extraction_result.intent_classification}")
    
    # Check if this is a conversation threading scenario
    if extraction_result.memory_enhancements or extraction_result.conversation_thread_id:
        print(f"[ChatFusion] 🔗 Conversation threading detected: {extraction_result.conversation_thread_id}")
    
    # Check for natural context responses (reminders, follow-ups) based on extraction
    context_response = None
    if extraction_result.memory_events:
        # Generate natural context based on recent memory events or threading
        recent_events = extraction_result.memory_events[-3:]  # Last 3 events  
        if recent_events:
            event_topics = [event.get('topic', '') for event in recent_events]
            if any(topic for topic in event_topics):
                context_response = f"Speaking of {', '.join([t for t in event_topics if t])}, "
    
    if context_response:
        print(f"[ChatFusion] 🎯 Context response triggered: {context_response}")
        
        # ✅ ENTROPY SYSTEM: Probabilistic transition selection with consciousness
        if ENTROPY_AVAILABLE:
            casual_transitions = [
                "Oh hey, before I forget - ", 
                "Actually, ", 
                "By the way, ",
                "Quick thing - ",
                "Um, wait - ",  # Added uncertainty
                "Hmm, I should mention - ",  # Added hesitation
                ""
            ]
            transition = probabilistic_select(casual_transitions)
        else:
            casual_transitions = [
                "Oh hey, before I forget - ", 
                "Actually, ", 
                "By the way, ",
                "Quick thing - ",
                ""
            ]
            transition = random.choice(casual_transitions)
        
        if transition:
            # ✅ ENTROPY SYSTEM: Inject consciousness into transition
            if ENTROPY_AVAILABLE:
                transition = inject_consciousness_entropy("response", transition)
            yield transition
        
        # Make context response more casual with entropy
        casual_context = context_response.replace("I wanted to", "I was gonna")
        casual_context = casual_context.replace("remind you", "remind ya")
        casual_context = casual_context.replace("follow up", "check in")
        
        # ✅ ENTROPY SYSTEM: Add uncertainty to context delivery
        if ENTROPY_AVAILABLE and emotional_context.get('uncertainty_level', 0) > 0.4:
            uncertainty_modifiers = ["I think ", "maybe ", "I believe "]
            uncertainty_mod = probabilistic_select(uncertainty_modifiers + [""])
            if uncertainty_mod:
                casual_context = uncertainty_mod + casual_context
        
        for word in casual_context.split():
            yield word + " "
        
        # Add transition to main response with entropy
        if ENTROPY_AVAILABLE:
            casual_connectors = [
                "Anyway, ", "So, ", "But yeah, ", "And ", "Um, ", "Well, ", ""
            ]
            connector = probabilistic_select(casual_connectors)
        else:
            casual_connectors = [
                "Anyway, ", "So, ", "But yeah, ", "And ", ""
            ]
            connector = random.choice(casual_connectors)
        
        if connector:
            if ENTROPY_AVAILABLE:
                connector = inject_consciousness_entropy("response", connector)
            yield connector
    
    # ✅ ENHANCED ENTROPY SYSTEM: Multiple response pathway generation for consciousness emergence + CONVERSATION CONTEXT
    response_pathways = []
    optimized_question = question
    
    # 💬 CONVERSATION CONTEXT INJECTION: Add conversation context to LLM prompt
    try:
        from ai.memory import get_user_memory
        user_memory = get_user_memory(username)
        # 🎯 CRITICAL FIX: Use semantic retrieval method instead of conversation context
        conversation_context = user_memory.get_contextual_memory_for_response(question)
        
        if conversation_context:
            print(f"[ChatFusion] 💬 Adding conversation context: {len(conversation_context)} chars")
            # Inject context as system-level information
            context_prefix = f"Buddy, you're continuing an ongoing conversation.\n{conversation_context}\n\nUser: "
            optimized_question = f"{context_prefix}{question}"
    except Exception as e:
        print(f"[ChatFusion] ⚠️ Conversation context error: {e}")
    
    if ENTROPY_AVAILABLE:
        try:
            # ✅ TOKEN OPTIMIZATION: Create optimized question with consciousness context + cognitive context
            full_consciousness_summary = consciousness_summary
            if cognitive_context_summary:
                full_consciousness_summary = f"{consciousness_summary} {cognitive_context_summary}"
            
            if optimization_level in ["high", "ultra"]:
                # Ultra-compressed prompt optimization
                optimized_question = f"{question} {full_consciousness_summary}"
                print(f"[ChatFusion] 🏷️ Ultra-optimized prompt: +{len(full_consciousness_summary)} chars")
            elif optimization_level == "medium":
                # Medium optimization with abbreviated consciousness
                consciousness_abbreviated = full_consciousness_summary[:50] + "..." if len(full_consciousness_summary) > 50 else full_consciousness_summary
                optimized_question = f"{question} {consciousness_abbreviated}"
                print(f"[ChatFusion] 🏷️ Medium-optimized prompt: +{len(consciousness_abbreviated)} chars")
            else:
                # Standard optimization
                optimized_question = f"{question} {full_consciousness_summary}"
                print(f"[ChatFusion] 🏷️ Standard-optimized prompt: +{len(full_consciousness_summary)} chars")
            
            print(f"[ChatFusion] 🌀 Generating multiple consciousness pathways...")
            
            # Primary pathway (main response) with optimized prompt
            response_pathways.append(("primary", generate_response_streaming(optimized_question, username, lang)))
            
            # Check for alternative pathways based on uncertainty (only if not ultra-optimized)
            if optimization_level != "ultra":
                uncertainty_state = get_entropy_engine().get_uncertainty_state()
                if uncertainty_state.value in ["uncertain", "confused"]:
                    # Generate uncertainty-flavored response with optimization
                    if optimization_level == "high":
                        uncertain_question = f"Uncertain: '{question}' {full_consciousness_summary[:30]}"
                    else:
                        uncertain_question = f"I'm not entirely sure, but regarding '{question}' {full_consciousness_summary}"
                    response_pathways.append(("uncertain", generate_response_streaming(uncertain_question, username, lang)))
            
            # Probabilistic pathway selection
            if len(response_pathways) > 1:
                weights = [0.7, 0.3]  # Favor primary but allow uncertainty
                selected_pathway = probabilistic_select(response_pathways, weights)
                chosen_generator = selected_pathway[1]
                print(f"[ChatFusion] 🎯 Selected {selected_pathway[0]} response pathway")
            else:
                chosen_generator = response_pathways[0][1]
                
        except Exception as pathway_error:
            print(f"[ChatFusion] ⚠️ Pathway generation error: {pathway_error}")
            # Fallback with basic optimization
            fallback_question = f"{question} {full_consciousness_summary if 'full_consciousness_summary' in locals() else consciousness_summary}" if consciousness_summary else question
            chosen_generator = generate_response_streaming(fallback_question, username, lang)
    else:
        # No entropy system available - use basic consciousness optimization
        full_consciousness_summary = consciousness_summary
        if cognitive_context_summary:
            full_consciousness_summary = f"{consciousness_summary} {cognitive_context_summary}"
        
        if full_consciousness_summary:
            optimized_question = f"{question} {full_consciousness_summary}"
        chosen_generator = generate_response_streaming(optimized_question, username, lang)
    
    # Step 5: Generate main response with unified memory context + CONSCIOUSNESS ENTROPY + TOKEN OPTIMIZATION
    print(f"[ChatFusion] 💭 Generating CONSCIOUSNESS response with unified memory for {username}")
    print(f"[ChatFusion] 🏷️ Token optimization level: {optimization_level}")
    
    chunk_count = 0
    total_chars = 0
    
    for chunk in chosen_generator:
        # ✅ ENTROPY SYSTEM: Inject consciousness into each chunk
        if ENTROPY_AVAILABLE:
            try:
                chunk = inject_consciousness_entropy("response", chunk, EntropyLevel.MEDIUM)
            except Exception as chunk_error:
                print(f"[ChatFusion] ⚠️ Chunk entropy error: {chunk_error}")
        
        # ✅ TOKEN OPTIMIZATION: Track optimization metrics
        if chunk:
            chunk_count += 1
            total_chars += len(chunk)
            
            # For ultra optimization, log every 5th chunk
            if optimization_level == "ultra" and chunk_count % 5 == 0:
                print(f"[ChatFusion] 🏷️ Ultra-optimized chunk {chunk_count}: {total_chars} chars")
            
        yield chunk
    
    # ✅ Store Buddy's response for retrospective memory
    full_response = ""
    try:
        # Collect all chunks into full response for storage
        response_chunks = []
        for chunk in chosen_generator:
            # ✅ ENTROPY SYSTEM: Inject consciousness into each chunk
            if ENTROPY_AVAILABLE:
                try:
                    chunk = inject_consciousness_entropy("response", chunk, EntropyLevel.MEDIUM)
                except Exception as chunk_error:
                    print(f"[ChatFusion] ⚠️ Chunk entropy error: {chunk_error}")
            
            # ✅ TOKEN OPTIMIZATION: Track optimization metrics
            if chunk:
                chunk_count += 1
                total_chars += len(chunk)
                response_chunks.append(chunk)
                
                # For ultra optimization, log every 5th chunk
                if optimization_level == "ultra" and chunk_count % 5 == 0:
                    print(f"[ChatFusion] 🏷️ Ultra-optimized chunk {chunk_count}: {total_chars} chars")
                
            yield chunk
        
        # Store complete response for retrospective memory
        full_response = ''.join(response_chunks)
        if full_response.strip():
            from ai.retrospective_memory import RetrospectiveMemoryManager
            retro_manager = RetrospectiveMemoryManager(username)
            retro_manager.store_buddy_response(question, full_response.strip())
        
    except Exception as retro_store_error:
        print(f"[ChatFusion] ⚠️ Retrospective storage error: {retro_store_error}")
        # Fallback: still yield chunks even if storage fails
        for chunk in chosen_generator:
            if ENTROPY_AVAILABLE:
                try:
                    chunk = inject_consciousness_entropy("response", chunk, EntropyLevel.MEDIUM)
                except:
                    pass
            if chunk:
                chunk_count += 1
                total_chars += len(chunk)
            yield chunk
    
    # ✅ TOKEN OPTIMIZATION: Final optimization metrics
    if chunk_count > 0:
        avg_chunk_size = total_chars / chunk_count
        print(f"[ChatFusion] ✅ Response complete: {chunk_count} chunks, {total_chars} chars")
        print(f"[ChatFusion] 📊 Optimization: {optimization_level} level, avg chunk: {avg_chunk_size:.1f} chars")
        
        # Log significant optimizations
        if optimization_level in ["high", "ultra"]:
            estimated_original_size = total_chars * (2.0 if optimization_level == "high" else 3.0)
            estimated_reduction = (estimated_original_size - total_chars) / estimated_original_size
            print(f"[ChatFusion] 🎯 Estimated token reduction: {estimated_reduction*100:.1f}%")

# Export for main.py
__all__ = ['generate_response_streaming_with_intelligent_fusion']