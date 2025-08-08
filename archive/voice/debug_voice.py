#!/usr/bin/env python3
# debug_voice.py - Debug voice database

from voice.database import load_known_users, known_users, debug_voice_database
from config import KNOWN_USERS_PATH
import os
import json

print("🔍 VOICE DATABASE DIAGNOSTIC")
print("=" * 40)

# Load and debug
load_known_users()
debug_voice_database()

print(f"\n📁 Database file path: {KNOWN_USERS_PATH}")
print(f"📁 File exists: {os.path.exists(KNOWN_USERS_PATH)}")

if os.path.exists(KNOWN_USERS_PATH):
    try:
        with open(KNOWN_USERS_PATH, 'r') as f:
            raw_data = json.load(f)
        
        print(f"\n📊 Raw database contents:")
        for name, data in raw_data.items():
            print(f"  👤 {name}:")
            if isinstance(data, dict):
                print(f"    - Type: dict")
                print(f"    - Keys: {list(data.keys())}")
                if 'embedding' in data:
                    embedding = data['embedding']
                    if isinstance(embedding, list):
                        print(f"    - Embedding: list with {len(embedding)} items")
                    else:
                        print(f"    - Embedding: {type(embedding)} (INVALID)")
                else:
                    print(f"    - No 'embedding' key (INVALID)")
            elif isinstance(data, list):
                print(f"    - Type: list with {len(data)} items (old format)")
            else:
                print(f"    - Type: {type(data)} (INVALID)")
    
    except Exception as e:
        print(f"❌ Error reading file: {e}")

print(f"\n🎯 RECOMMENDATION:")
if not known_users:
    print("  ➤ Database is empty - need to register your voice")
else:
    valid_count = 0
    for name, data in known_users.items():
        if isinstance(data, dict) and 'embedding' in data:
            if isinstance(data['embedding'], list) and len(data['embedding']) == 256:
                valid_count += 1
        elif isinstance(data, list) and len(data) == 256:
            valid_count += 1
    
    if valid_count == 0:
        print("  ➤ Database has corrupted embeddings - need to clean and re-register")
    else:
        print(f"  ➤ {valid_count} valid profiles found - should work!")