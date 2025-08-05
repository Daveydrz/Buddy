#!/bin/bash
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
