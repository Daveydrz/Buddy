#!/usr/bin/env python3
"""
Simple test for critical missing functions without full system startup
"""

def test_missing_functions():
    """Test for missing functions"""
    issues = []
    
    # Test get_latency_stats
    try:
        from ai.latency_optimizer import get_latency_stats
        print("✅ get_latency_stats found")
    except ImportError:
        issues.append("❌ get_latency_stats missing from latency_optimizer.py")
    
    # Test get_belief_tracker
    try:
        from ai.belief_evolution_tracker import get_belief_tracker
        print("✅ get_belief_tracker found")
    except ImportError:
        issues.append("❌ get_belief_tracker missing from belief_evolution_tracker.py")
    
    return issues

def main():
    print("🔍 Testing Missing Functions")
    issues = test_missing_functions()
    
    if issues:
        print("\n❌ Issues found:")
        for issue in issues:
            print(f"  {issue}")
        return 1
    else:
        print("\n✅ All functions found!")
        return 0

if __name__ == "__main__":
    main()