#!/usr/bin/env python3
"""
Simplified Test for Reactive Neural Architecture

Tests basic functionality to verify the implementation works
"""

import os
import sys
import asyncio
import time
import threading

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_basic_functionality():
    """Test basic functionality of reactive neural architecture"""
    print("🧪 Testing Reactive Neural Architecture Basic Functionality")
    print("="*60)
    
    # Test 1: Event Bus
    print("\n1️⃣ Testing Event Bus...")
    try:
        from ai.reactive_neural_architecture import EventBus, NeuralEvent, EventType, EventPriority
        
        event_bus = EventBus()
        received_events = []
        
        def test_subscriber(event):
            received_events.append(event)
            print(f"   📥 Received: {event.type.name}")
        
        event_bus.subscribe("USER_INPUT", test_subscriber)
        
        test_event = NeuralEvent(
            type=EventType.USER_INPUT,
            priority=EventPriority.HIGH,
            source="test",
            data={'text': 'Hello!'}
        )
        
        event_bus.publish_sync(test_event)
        time.sleep(0.1)
        
        assert len(received_events) == 1
        print("   ✅ Event Bus working correctly")
        
    except Exception as e:
        print(f"   ❌ Event Bus failed: {e}")
        return False
    
    # Test 2: Async Neural Pathways
    print("\n2️⃣ Testing Async Neural Pathways...")
    try:
        from ai.reactive_neural_architecture import AsyncNeuralPathways
        
        async def test_async():
            pathways = AsyncNeuralPathways(max_concurrent=2)
            
            def simple_operation(x):
                time.sleep(0.01)
                return x * 2
            
            result = await pathways.execute_compute_operation("test_op", simple_operation, 5)
            assert result == 10
            return True
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(test_async())
        loop.close()
        
        assert result == True
        print("   ✅ Async Neural Pathways working correctly")
        
    except Exception as e:
        print(f"   ❌ Async Neural Pathways failed: {e}")
        return False
    
    # Test 3: Work-Stealing Thread Pool
    print("\n3️⃣ Testing Work-Stealing Thread Pool...")
    try:
        from ai.reactive_neural_architecture import WorkStealingThreadPool
        
        pool = WorkStealingThreadPool(num_workers=2)
        
        def cpu_task(n):
            return sum(range(n))
        
        events = []
        for i in range(3):
            event = pool.submit(cpu_task, 100 + i)
            events.append(event)
        
        for event in events:
            event.wait(timeout=2.0)
        
        stats = pool.get_stats()
        assert stats['tasks_completed'] >= 3
        
        pool.shutdown(wait=True)
        print("   ✅ Work-Stealing Thread Pool working correctly")
        
    except Exception as e:
        print(f"   ❌ Work-Stealing Thread Pool failed: {e}")
        return False
    
    # Test 4: Memory Manager
    print("\n4️⃣ Testing Optimized Memory Manager...")
    try:
        from ai.reactive_neural_architecture import OptimizedMemoryManager
        
        memory_manager = OptimizedMemoryManager()
        
        # Test object pooling
        def create_obj():
            return {'data': [1, 2, 3]}
        
        obj1 = memory_manager.get_pooled_object("test_pool", create_obj)
        assert obj1 is not None
        assert obj1['data'] == [1, 2, 3]
        
        # Test COW
        cow_id = memory_manager.create_cow_object("test_cow", {'shared': 'data'})
        cow_obj, cow_id_returned = memory_manager.get_cow_object(cow_id, copy_on_write=False)
        assert cow_obj['shared'] == 'data'
        
        if cow_id_returned:
            memory_manager.release_cow_object(cow_id_returned)
        
        print("   ✅ Optimized Memory Manager working correctly")
        
    except Exception as e:
        print(f"   ❌ Optimized Memory Manager failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 5: Integration Layer
    print("\n5️⃣ Testing Integration Layer...")
    try:
        from ai.hybrid_consciousness_integration import ReactiveIntegrationLayer, ProcessingMode
        
        async def test_integration():
            integration = ReactiveIntegrationLayer(num_workers=1)
            await integration.initialize()
            
            result = await integration.process_user_input(
                text="Test input",
                user="test_user",
                processing_mode=ProcessingMode.HYBRID_BALANCED
            )
            
            await integration.shutdown()
            return result.success
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        success = loop.run_until_complete(test_integration())
        loop.close()
        
        assert success == True
        print("   ✅ Integration Layer working correctly")
        
    except Exception as e:
        print(f"   ❌ Integration Layer failed: {e}")
        return False
    
    print("\n🎉 All basic tests passed! Reactive Neural Architecture is functional.")
    return True

if __name__ == "__main__":
    success = test_basic_functionality()
    if success:
        print("\n✅ Reactive Neural Architecture implementation is working correctly!")
        exit(0)
    else:
        print("\n❌ Some tests failed. Please check the implementation.")
        exit(1)