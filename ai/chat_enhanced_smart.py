# ai/chat_enhanced_smart.py - Smart LLM-based chat integration with unified memory extraction
import random
from ai.chat import generate_response_streaming, ask_kobold_streaming, get_current_brisbane_time
from ai.memory import add_to_conversation_history
from ai.unified_memory_manager import extract_all_from_text, get_cached_extraction_result, check_conversation_threading

def reset_session_for_user_smart(username: str):
    """Reset session when conversation starts"""
    print(f"[SmartChat] 🔄 Session reset for {username}")

def generate_response_streaming_with_smart_memory(question, username, lang="en", context=None):
    """Streaming version with unified memory extraction + 8k context window management"""
    try:
        print(f"[SmartChat] 🧠 Starting unified extraction streaming for '{question}' from {username}")
        
        # Check context window limits before processing (8k token management)
        try:
            from ai.context_window_manager import check_context_window_rollover, create_context_snapshot_for_user
            
            # Build current context from previous conversation if available
            current_context = context.get("current_context", "") if context else ""
            if not current_context:
                # Build minimal context for new conversations
                current_context = f"System: You are Buddy, an AI assistant.\nUser: {question}"
            
            needs_rollover, fresh_context = check_context_window_rollover(username, current_context, question)
            
            if needs_rollover:
                print(f"[SmartChat] 🔄 Context window rollover triggered for {username}")
                
                # Create snapshot to preserve memory context
                conversation_history = context.get("conversation_history", []) if context else []
                working_memory = context.get("working_memory", {}) if context else {}
                
                snapshot_created = create_context_snapshot_for_user(
                    username, current_context, working_memory, conversation_history
                )
                
                if snapshot_created:
                    print(f"[SmartChat] 📸 Context snapshot created - memories preserved across 8k limit")
                    # Update context to use fresh compressed context with memory injection
                    if context:
                        context["current_context"] = fresh_context
                        context["context_rollover_occurred"] = True
                    else:
                        context = {"current_context": fresh_context, "context_rollover_occurred": True}
                else:
                    print(f"[SmartChat] ⚠️ Context snapshot failed - using standard compression")
            
        except ImportError:
            print(f"[SmartChat] ⚠️ Context window manager not available - using standard processing")
        
        # ✅ UNIFIED MEMORY EXTRACTION - Single LLM call for all extraction types
        conversation_context = context.get("current_context", "") if context else ""
        extraction_result = extract_all_from_text(username, question, conversation_context)
        
        # Check if this is a conversation threading scenario (McDonald's → McFlurry example)
        if extraction_result.memory_enhancements or extraction_result.conversation_thread_id:
            print(f"[SmartChat] 🔗 Conversation threading detected: {extraction_result.conversation_thread_id}")
        
        # Handle different intent types appropriately
        if extraction_result.intent_classification == "memory_recall":
            print(f"[SmartChat] 🧠 Memory recall intent detected")
        elif extraction_result.intent_classification == "memory_enhancement":
            print(f"[SmartChat] 🔗 Memory enhancement intent detected")
        
        # 🧠 NEW: Check for retrospective memory (Buddy's past advice)
        past_advice_context = None
        try:
            from ai.retrospective_memory import get_past_advice_context, search_buddy_past_advice
            
            # Check if user is asking about something Buddy said before
            retrospective_keywords = [
                'what did you say', 'you mentioned', 'you told me', 'you said',
                'earlier you', 'before you', 'repeat what', 'you advised',
                'your advice', 'remember when you', 'recall what'
            ]
            
            is_retrospective_query = any(keyword in question.lower() for keyword in retrospective_keywords)
            
            if is_retrospective_query:
                # Direct search for past advice
                past_advice_results = search_buddy_past_advice(username, question)
                if past_advice_results:
                    print(f"[SmartChat] 🧠 Found {len(past_advice_results)} past advice matches")
                    # Return the past advice directly
                    for advice in past_advice_results:
                        yield advice + " "
                    return
            else:
                # Get context for similar topics
                past_advice_context = get_past_advice_context(username, question)
                if past_advice_context:
                    print(f"[SmartChat] 🧠 Injecting past advice context for similar topic")
        except Exception as retro_error:
            print(f"[SmartChat] ⚠️ Retrospective memory error: {retro_error}")
        
        # Check for natural context response based on extracted memory events
        context_response = None
        if extraction_result.memory_events:
            # Generate natural context based on recent memory events
            recent_events = extraction_result.memory_events[-3:]  # Last 3 events
            if recent_events:
                event_topics = [event.get('topic', '') for event in recent_events]
                if any(topic for topic in event_topics):
                    context_response = f"Speaking of {', '.join([t for t in event_topics if t])}, "
        
        # If we have natural context, yield it first
        if context_response:
            print(f"[SmartChat] 💭 Context response from unified extraction: {context_response}")
            yield context_response
            
            import time
            time.sleep(0.3)
            
            connectors = [" ", "Also, ", "And ", "By the way, ", "Oh, and "]
            yield random.choice(connectors)
        
        # Add emotional context to response if available
        enhanced_question = question
        if extraction_result.emotional_state.get('primary_emotion') not in ['neutral', 'casual']:
            emotion = extraction_result.emotional_state['primary_emotion']
            enhanced_question = f"[User emotion: {emotion}] {question}"
            print(f"[SmartChat] 😊 Enhanced question with emotion: {emotion}")
        
        # Use existing streaming generation with enhanced context
        full_response = ""
        for chunk in generate_response_streaming(enhanced_question, username, lang):
            if chunk and chunk.strip():
                full_response += chunk.strip() + " "
                yield chunk.strip()
        
        # ✅ Store Buddy's response for retrospective memory
        try:
            from ai.retrospective_memory import RetrospectiveMemoryManager
            retro_manager = RetrospectiveMemoryManager(username)
            retro_manager.store_buddy_response(question, full_response.strip())
        except Exception as retro_store_error:
            print(f"[SmartChat] ⚠️ Retrospective storage error: {retro_store_error}")
        
        # Add to conversation history
        if full_response.strip():
            complete_response = context_response + " " + full_response if context_response else full_response
            add_to_conversation_history(username, question, complete_response.strip())
        
    except Exception as e:
        print(f"[SmartChat] ❌ Error: {e}")
        yield "Sorry, I'm having trouble thinking right now."