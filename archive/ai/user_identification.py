# ai/user_identification.py - Handle user identification and name processing
from ai.speech import identify_user, extract_spoken_name, get_display_name

def process_user_input(spoken_text: str, system_username: str) -> tuple[str, str]:
    """
    Process user input and handle identification
    
    Returns:
        (actual_username, display_name)
    """
    
    try:
        from ai.speech import identify_user, extract_spoken_name, get_display_name
        
        # Check if user is introducing themselves
        identified_username = identify_user(spoken_text, system_username)
        
        # Get display name
        display_name = get_display_name(identified_username)
        
        return identified_username, display_name
        
    except ImportError as e:
        print(f"[UserIdentification] ⚠️ Speech module not available: {e}")
        return system_username, system_username
    except Exception as e:
        print(f"[UserIdentification] ❌ Error processing user input: {e}")
        return system_username, system_username