#!/usr/bin/env python3
"""
Complete Integration Checker and Fixer
Created: 2025-01-17 in response to @Daveydrz comment
Purpose: Ensure all components are integrated in main, connected to LLM, and prompts are tokenized

This script addresses the specific request:
"Make sure all is integrated in main connects to llm koboltcpp etc make sure all prompts are tokenized"
"""

import os
import sys
import json
import time
import subprocess
import requests
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add current directory to path
sys.path.insert(0, '/home/runner/work/Dawidbudd/Dawidbudd')

class IntegrationChecker:
    """Check and fix all integration issues"""
    
    def __init__(self):
        self.issues = []
        self.fixes_applied = []
        
    def check_main_integration(self) -> bool:
        """Check if all components are integrated in main.py"""
        print("🔍 Checking main.py integration...")
        
        try:
            main_path = Path("main.py")
            if not main_path.exists():
                self.issues.append("main.py not found")
                return False
            
            with open(main_path, 'r') as f:
                main_content = f.read()
            
            # Check for key integrations
            required_integrations = [
                ("consciousness_tokenizer", "consciousness_tokenizer"),
                ("llm_handler", "llm_handler"),  
                ("belief_analyzer", "belief_analyzer"),
                ("memory_context_corrector", "memory_context_corrector"),
                ("belief_qualia_linking", "belief_qualia_linking"),
                ("value_system", "value_system"),
                ("conscious_prompt_builder", "conscious_prompt_builder"),
                ("introspection_loop", "introspection_loop")
            ]
            
            integrated = []
            missing = []
            
            for component, import_name in required_integrations:
                if import_name in main_content:
                    integrated.append(component)
                    print(f"   ✅ {component}: Integrated")
                else:
                    missing.append(component)
                    print(f"   ❌ {component}: Missing")
                    
            if missing:
                self.issues.append(f"Missing integrations: {missing}")
                return False
            
            print(f"   ✅ All {len(integrated)} components integrated in main.py")
            return True
            
        except Exception as e:
            self.issues.append(f"Failed to check main.py: {e}")
            return False
    
    def check_llm_connection(self) -> bool:
        """Check LLM connection to KoboldCPP"""
        print("🔌 Checking LLM connection...")
        
        try:
            from config import KOBOLD_URL
            print(f"   📍 Checking connection to: {KOBOLD_URL}")
            
            # Test connection
            response = requests.get(KOBOLD_URL.replace('/v1/chat/completions', '/v1/models'), timeout=5)
            
            if response.status_code == 200:
                print("   ✅ LLM server: Connected")
                return True
            else:
                print(f"   ❌ LLM server: Bad response ({response.status_code})")
                self.issues.append(f"LLM server returned {response.status_code}")
                return False
                
        except requests.exceptions.ConnectionError:
            print("   ❌ LLM server: Connection refused")
            self.issues.append("KoboldCPP server not running")
            return False
        except Exception as e:
            print(f"   ❌ LLM connection error: {e}")
            self.issues.append(f"LLM connection error: {e}")
            return False
    
    def check_tokenization(self) -> bool:
        """Check prompt tokenization is working"""
        print("🏷️ Checking prompt tokenization...")
        
        try:
            from ai.consciousness_tokenizer import (
                tokenize_consciousness_for_llm,
                get_consciousness_summary_for_llm
            )
            
            # Test tokenization
            test_state = {
                'emotion_engine': {'primary_emotion': 'focused', 'intensity': 0.7},
                'motivation_system': {'active_goals': []},
                'global_workspace': {'current_focus': 'testing'}
            }
            
            tokenized = tokenize_consciousness_for_llm(test_state)
            summary = get_consciousness_summary_for_llm(test_state)
            
            if tokenized and summary:
                print(f"   ✅ Tokenization working: {len(tokenized)} chars")
                print(f"   📝 Summary: {summary}")
                return True
            else:
                print("   ❌ Tokenization failed: No output")
                self.issues.append("Tokenization produces no output")
                return False
                
        except Exception as e:
            print(f"   ❌ Tokenization error: {e}")
            self.issues.append(f"Tokenization error: {e}")
            return False
    
    def check_self_awareness_components(self) -> bool:
        """Check all self-awareness components are present"""
        print("🧠 Checking self-awareness components...")
        
        required_components = [
            "memory_context_corrector.py",
            "belief_qualia_linking.py", 
            "value_system.py",
            "conscious_prompt_builder.py",
            "introspection_loop.py",
            "emotion_response_modulator.py",
            "dialogue_confidence_filter.py",
            "qualia_analytics.py",
            "belief_memory_refiner.py",
            "self_model_updater.py",
            "goal_reasoning.py",
            "motivation_reasoner.py"
        ]
        
        missing = []
        present = []
        
        for component in required_components:
            component_path = Path(f"ai/{component}")
            if component_path.exists():
                present.append(component)
                print(f"   ✅ {component}: Present")
            else:
                missing.append(component)
                print(f"   ❌ {component}: Missing")
        
        if missing:
            self.issues.append(f"Missing components: {missing}")
            return False
        
        print(f"   ✅ All {len(present)} components present")
        return True
    
    def fix_llm_connection_config(self) -> bool:
        """Fix LLM connection configuration"""
        print("🔧 Fixing LLM connection configuration...")
        
        try:
            # Check if we need to update config
            config_path = Path("config.py")
            if not config_path.exists():
                self.issues.append("config.py not found")
                return False
            
            with open(config_path, 'r') as f:
                config_content = f.read()
            
            # Update KOBOLD_URL if it's wrong
            if 'KOBOLD_URL = "http://localhost:5001/v1/chat/completions"' in config_content:
                print("   ✅ KOBOLD_URL already configured correctly")
            else:
                # Add or update KOBOLD_URL
                if 'KOBOLD_URL' not in config_content:
                    config_content += '\n# LLM Configuration\nKOBOLD_URL = "http://localhost:5001/v1/chat/completions"\n'
                    with open(config_path, 'w') as f:
                        f.write(config_content)
                    print("   ✅ Added KOBOLD_URL to config.py")
                    self.fixes_applied.append("Added KOBOLD_URL configuration")
                else:
                    print("   ✅ KOBOLD_URL already exists in config")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Failed to fix config: {e}")
            self.issues.append(f"Config fix failed: {e}")
            return False
    
    def create_llm_startup_script(self) -> bool:
        """Create a script to start KoboldCPP server"""
        print("📝 Creating LLM startup script...")
        
        try:
            startup_script = """#!/bin/bash
# KoboldCPP Startup Script
# Run this script to start the LLM server for Buddy

echo "🚀 Starting KoboldCPP server for Buddy..."

# Check if KoboldCPP is installed
if command -v koboldcpp &> /dev/null; then
    echo "✅ KoboldCPP found"
    koboldcpp --host 0.0.0.0 --port 5001 --threads 4
elif [ -f "koboldcpp.py" ]; then
    echo "✅ KoboldCPP script found"
    python3 koboldcpp.py --host 0.0.0.0 --port 5001 --threads 4
else
    echo "❌ KoboldCPP not found"
    echo "Please install KoboldCPP or place koboldcpp.py in current directory"
    echo "Download from: https://github.com/LostRuins/koboldcpp"
    exit 1
fi
"""
            
            with open("start_llm_server.sh", 'w') as f:
                f.write(startup_script)
            
            # Make executable
            os.chmod("start_llm_server.sh", 0o755)
            
            print("   ✅ Created start_llm_server.sh")
            self.fixes_applied.append("Created LLM startup script")
            return True
            
        except Exception as e:
            print(f"   ❌ Failed to create startup script: {e}")
            self.issues.append(f"Startup script creation failed: {e}")
            return False
    
    def create_integration_test_script(self) -> bool:
        """Create a comprehensive integration test"""
        print("🧪 Creating integration test script...")
        
        try:
            test_script = '''#!/usr/bin/env python3
"""
Daily Integration Test - Run this to verify all systems working
"""

import sys
import os
sys.path.insert(0, os.getcwd())

def test_all_systems():
    """Test all integrated systems"""
    print("🧪 Running Daily Integration Test...")
    
    tests = []
    
    # Test 1: Import all components
    try:
        from ai.consciousness_tokenizer import tokenize_consciousness_for_llm
        from ai.llm_handler import generate_consciousness_integrated_response
        from ai.memory_context_corrector import MemoryContextCorrector
        from ai.belief_qualia_linking import BeliefQualiaLinker
        from ai.value_system import ValueSystem
        from ai.conscious_prompt_builder import ConsciousPromptBuilder
        from ai.introspection_loop import IntrospectionLoop
        print("   ✅ All component imports successful")
        tests.append(("Component Imports", True))
    except Exception as e:
        print(f"   ❌ Import failed: {e}")
        tests.append(("Component Imports", False))
    
    # Test 2: LLM Connection
    try:
        import requests
        from config import KOBOLD_URL
        response = requests.get(KOBOLD_URL.replace('/v1/chat/completions', '/v1/models'), timeout=5)
        if response.status_code == 200:
            print("   ✅ LLM connection successful")
            tests.append(("LLM Connection", True))
        else:
            print(f"   ❌ LLM connection failed: {response.status_code}")
            tests.append(("LLM Connection", False))
    except Exception as e:
        print(f"   ❌ LLM connection error: {e}")
        tests.append(("LLM Connection", False))
    
    # Test 3: Tokenization
    try:
        from ai.consciousness_tokenizer import tokenize_consciousness_for_llm
        test_state = {'emotion_engine': {'primary_emotion': 'testing'}}
        result = tokenize_consciousness_for_llm(test_state)
        if result:
            print(f"   ✅ Tokenization working: {len(result)} chars")
            tests.append(("Tokenization", True))
        else:
            print("   ❌ Tokenization failed")
            tests.append(("Tokenization", False))
    except Exception as e:
        print(f"   ❌ Tokenization error: {e}")
        tests.append(("Tokenization", False))
    
    # Test 4: End-to-end
    try:
        from ai.llm_handler import process_user_input_with_consciousness
        result = process_user_input_with_consciousness("Hello", "test_user")
        if result:
            print("   ✅ End-to-end processing working")
            tests.append(("End-to-End", True))
        else:
            print("   ❌ End-to-end processing failed")
            tests.append(("End-to-End", False))
    except Exception as e:
        print(f"   ❌ End-to-end error: {e}")
        tests.append(("End-to-End", False))
    
    # Results
    passed = sum(1 for _, success in tests if success)
    total = len(tests)
    
    print(f"\\n📊 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All systems integrated and working!")
        return True
    else:
        print("⚠️ Some systems need attention")
        return False

if __name__ == "__main__":
    success = test_all_systems()
    sys.exit(0 if success else 1)
'''
            
            with open("test_daily_integration.py", 'w') as f:
                f.write(test_script)
            
            print("   ✅ Created test_daily_integration.py")
            self.fixes_applied.append("Created integration test script")
            return True
            
        except Exception as e:
            print(f"   ❌ Failed to create test script: {e}")
            self.issues.append(f"Test script creation failed: {e}")
            return False
    
    def fix_dependency_issues(self) -> bool:
        """Fix common dependency issues"""
        print("🔧 Fixing dependency issues...")
        
        try:
            # Check for numpy (needed for voice processing)
            try:
                import numpy
                print("   ✅ numpy: Available")
            except ImportError:
                print("   ❌ numpy: Missing")
                self.issues.append("numpy not installed")
                print("   💡 Install with: pip install numpy")
            
            # Check for other critical dependencies
            dependencies = [
                ("requests", "HTTP requests"),
                ("json", "JSON processing"),
                ("time", "Time utilities"),
                ("datetime", "Date/time"),
                ("pathlib", "Path handling")
            ]
            
            for dep, description in dependencies:
                try:
                    __import__(dep)
                    print(f"   ✅ {dep}: Available")
                except ImportError:
                    print(f"   ❌ {dep}: Missing ({description})")
                    self.issues.append(f"{dep} not available")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Dependency check failed: {e}")
            self.issues.append(f"Dependency check failed: {e}")
            return False
    
    def create_integration_status_report(self) -> bool:
        """Create a status report of all integrations"""
        print("📋 Creating integration status report...")
        
        try:
            report = {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "integration_status": {
                    "main_integration": self.check_main_integration(),
                    "llm_connection": self.check_llm_connection(),
                    "tokenization": self.check_tokenization(),
                    "self_awareness_components": self.check_self_awareness_components()
                },
                "issues": self.issues,
                "fixes_applied": self.fixes_applied,
                "next_steps": [
                    "Start KoboldCPP server with: ./start_llm_server.sh",
                    "Run integration test with: python test_daily_integration.py",
                    "Check main.py for any missing imports",
                    "Install missing dependencies if any"
                ]
            }
            
            with open("integration_status.json", 'w') as f:
                json.dump(report, f, indent=2)
            
            print("   ✅ Created integration_status.json")
            self.fixes_applied.append("Created integration status report")
            return True
            
        except Exception as e:
            print(f"   ❌ Failed to create report: {e}")
            self.issues.append(f"Report creation failed: {e}")
            return False
    
    def run_complete_check(self) -> bool:
        """Run all checks and fixes"""
        print("🚀 Running Complete Integration Check")
        print("=" * 50)
        
        checks = [
            ("Main Integration", self.check_main_integration),
            ("LLM Connection", self.check_llm_connection),
            ("Tokenization", self.check_tokenization),
            ("Self-Awareness Components", self.check_self_awareness_components)
        ]
        
        fixes = [
            ("LLM Configuration", self.fix_llm_connection_config),
            ("LLM Startup Script", self.create_llm_startup_script),
            ("Integration Test", self.create_integration_test_script),
            ("Dependency Issues", self.fix_dependency_issues),
            ("Status Report", self.create_integration_status_report)
        ]
        
        # Run checks
        check_results = []
        for check_name, check_func in checks:
            try:
                result = check_func()
                check_results.append((check_name, result))
            except Exception as e:
                print(f"   ❌ {check_name}: Exception - {e}")
                check_results.append((check_name, False))
        
        # Run fixes
        fix_results = []
        for fix_name, fix_func in fixes:
            try:
                result = fix_func()
                fix_results.append((fix_name, result))
            except Exception as e:
                print(f"   ❌ {fix_name}: Exception - {e}")
                fix_results.append((fix_name, False))
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 Integration Check Summary")
        print("=" * 50)
        
        print("\n🔍 System Checks:")
        for check_name, success in check_results:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"   {status} {check_name}")
        
        print("\n🔧 Applied Fixes:")
        for fix_name, success in fix_results:
            status = "✅ DONE" if success else "❌ FAILED"
            print(f"   {status} {fix_name}")
        
        if self.issues:
            print("\n⚠️ Issues Found:")
            for issue in self.issues:
                print(f"   • {issue}")
        
        if self.fixes_applied:
            print("\n✅ Fixes Applied:")
            for fix in self.fixes_applied:
                print(f"   • {fix}")
        
        # Overall success
        checks_passed = sum(1 for _, success in check_results if success)
        fixes_passed = sum(1 for _, success in fix_results if success)
        
        print(f"\n📊 Results: {checks_passed}/{len(checks)} checks passed, {fixes_passed}/{len(fixes)} fixes applied")
        
        if checks_passed == len(checks):
            print("🎉 All systems integrated and working!")
            return True
        else:
            print("⚠️ Some systems need attention - see issues above")
            return False

def main():
    """Main function"""
    checker = IntegrationChecker()
    success = checker.run_complete_check()
    
    print("\n" + "=" * 50)
    print("🎯 Next Steps:")
    print("=" * 50)
    
    if not success:
        print("1. 🔧 Fix any issues listed above")
        print("2. 🚀 Start KoboldCPP server: ./start_llm_server.sh")
        print("3. 🧪 Run integration test: python test_daily_integration.py")
        print("4. 🎮 Start Buddy: python main.py")
    else:
        print("1. 🚀 Start KoboldCPP server: ./start_llm_server.sh")
        print("2. 🎮 Start Buddy: python main.py")
        print("3. 🧪 Run daily test: python test_daily_integration.py")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)