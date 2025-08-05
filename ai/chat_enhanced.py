# ai/chat_enhanced.py - Enhanced chat that integrates with your existing chat.py
import random
from ai.chat import generate_response_streaming, ask_kobold_streaming, get_current_brisbane_time
from ai.human_memory import HumanLikeMemory
from ai.memory import add_to_conversation_history

# Global human memory instances
human_memories = {}

def get_human_memory(username: str) -> HumanLikeMemory:
    """Get or create human memory for user"""
    if username not in human_memories:
        human_memories[username] = HumanLikeMemory(username)
    return human_memories[username]

def reset_session_for_user(username: str):
    """Reset session when conversation starts"""
    memory = get_human_memory(username)
    memory.reset_session_context()

def generate_response_with_human_memory(question, username, lang="en"):
    """Generate response with human-like memory integration"""
    try:
        print(f"[ChatEnhanced] 🧠 Starting human-like response for '{question}' from {username}")
        
        # Get human memory
        human_memory = get_human_memory(username)
        
        # Extract and store memories from user input
        human_memory.extract_and_store_human_memories(question)
        
        # Check for natural context response (only once per session)
        context_response = human_memory.check_for_natural_context_response()
        
        # Generate response chunks
        response_parts = []
        
        # If we have natural context, yield it first
        if context_response:
            print(f"[ChatEnhanced] 💭 Natural memory response: {context_response}")
            response_parts.append(context_response)
            
            # Add natural connector
            connectors = [" ", "Also, ", "And ", "By the way, ", "Oh, and "]
            response_parts.append(random.choice(connectors))
        
        # Use your existing streaming generation
        full_ai_response = ""
        for chunk in generate_response_streaming(question, username, lang):
            if chunk and chunk.strip():
                response_parts.append(chunk.strip())
                full_ai_response += chunk.strip() + " "
        
        # Combine all parts
        complete_response = "".join(response_parts)
        
        # Add to conversation history
        if complete_response.strip():
            add_to_conversation_history(username, question, complete_response.strip())
        
        return complete_response
        
    except Exception as e:
        print(f"[ChatEnhanced] ❌ Error: {e}")
        return "Sorry, I'm having trouble thinking right now."

def generate_response_streaming_with_human_memory(question, username, lang="en"):
    """Streaming version with human-like memory"""
    try:
        print(f"[ChatEnhanced] 🧠 Starting human-like streaming for '{question}' from {username}")
        
        # Get human memory
        human_memory = get_human_memory(username)
        
        # Extract and store memories from user input
        human_memory.extract_and_store_human_memories(question)
        
        # Check for natural context response
        context_response = human_memory.check_for_natural_context_response()
        
        # If we have natural context, yield it first
        if context_response:
            print(f"[ChatEnhanced] 💭 Natural memory response: {context_response}")
            yield context_response
            
            # Small pause for natural flow
            import time
            time.sleep(0.3)
            
            # Add natural connector
            connectors = [" ", "Also, ", "And ", "By the way, ", "Oh, and "]
            yield random.choice(connectors)
        
        # Use your existing streaming generation
        full_response = ""
        for chunk in generate_response_streaming(question, username, lang):
            if chunk and chunk.strip():
                full_response += chunk.strip() + " "
                yield chunk.strip()
        
        # Add to conversation history
        if full_response.strip():
            complete_response = context_response + " " + full_response if context_response else full_response
            add_to_conversation_history(username, question, complete_response.strip())
        
    except Exception as e:
        print(f"[ChatEnhanced] ❌ Error: {e}")
        yield "Sorry, I'm having trouble thinking right now."