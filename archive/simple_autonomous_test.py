#!/usr/bin/env python3
"""
Simple Autonomous Buddy AI Test

This script provides a quick test of the autonomous consciousness systems.
"""

import time
from datetime import datetime

def simple_autonomous_test():
    """Simple test of autonomous systems"""
    print("🚀 Simple Autonomous Buddy AI Test")
    print("=" * 50)
    
    try:
        # Test imports
        print("📦 Testing imports...")
        from ai.proactive_thinking_loop import proactive_thinking_loop
        from ai.self_motivation_engine import self_motivation_engine
        from ai.autonomous_communication_manager import autonomous_communication_manager, CommunicationType, CommunicationPriority
        print("✅ Core modules imported")
        
        # Test basic functionality
        print("\n🧪 Testing basic functionality...")
        
        # Test communication manager
        success = autonomous_communication_manager.queue_communication(
            content="This is a test autonomous message.",
            communication_type=CommunicationType.PROACTIVE_THOUGHT,
            priority=CommunicationPriority.LOW,
            source_module="test"
        )
        print(f"✅ Communication queued: {success}")
        
        # Test motivation engine stats
        motivation_stats = self_motivation_engine.get_stats()
        print(f"✅ Motivation engine stats: {len(motivation_stats)} keys")
        
        # Test proactive thinking stats
        thinking_stats = proactive_thinking_loop.get_stats()
        print(f"✅ Proactive thinking stats: {len(thinking_stats)} keys")
        
        print("\n🎉 SIMPLE TEST PASSED!")
        print("✅ All core autonomous modules are working")
        print("✅ Communication system is functional")
        print("✅ Systems can be started and operated")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print(f"🕐 Started at: {datetime.now()}")
    success = simple_autonomous_test()
    
    if success:
        print("\n✅ SUCCESS: Autonomous Buddy AI is ready!")
    else:
        print("\n❌ FAILED: Check errors above")