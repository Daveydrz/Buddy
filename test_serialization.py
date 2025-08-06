#!/usr/bin/env python3
"""
Test serialization fixes for MemoryCacheManager
"""

def test_serialization():
    """Test that MemoryCacheManager can be serialized"""
    print("🧪 Testing MemoryCacheManager serialization...")
    
    try:
        from ai.memory_cache_manager import get_memory_cache_manager
        import pickle
        
        # Get manager instance
        manager = get_memory_cache_manager()
        
        # Test serialization
        serialized_data = pickle.dumps(manager)
        print("✅ MemoryCacheManager serialization successful")
        
        # Test deserialization
        deserialized_manager = pickle.loads(serialized_data)
        print("✅ MemoryCacheManager deserialization successful")
        
        # Test that deserialized manager still works
        test_data = {"test": "data"}
        success = deserialized_manager.cache_memory_data("test_key", test_data)
        if success:
            print("✅ Deserialized manager functionality test passed")
        else:
            print("❌ Deserialized manager functionality test failed")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Serialization test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Test serialization fixes"""
    print("🔍 Testing Serialization Fixes")
    print("=" * 40)
    
    if test_serialization():
        print("\n✅ Serialization fixes working correctly!")
        return 0
    else:
        print("\n❌ Serialization fixes failed")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())