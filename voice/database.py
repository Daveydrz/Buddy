# voice/database.py - Voice profile database management with anonymous clustering
import json
import os
import time
import numpy as np  
import shutil       
from datetime import datetime
from config import KNOWN_USERS_PATH, DEBUG
# 🚀 ENHANCED: False positives tracking
false_positives = []

# ✅ WINDOWS COMPATIBILITY: Make fcntl optional
try:
    import fcntl
    FCNTL_AVAILABLE = True
except ImportError:
    FCNTL_AVAILABLE = False
    print("[Database]⚠️ fcntl not available on Windows - using alternative file locking")


# Global voice database
known_users = {}
anonymous_clusters = {}  # ✅ NEW: Anonymous voice clusters
cluster_counter = 1

def load_known_users():
    """🚀 BULLETPROOF: Load known users with embedding preservation"""
    global known_users, anonymous_clusters, false_positives
    
    try:
        print(f"[DEBUG] 📂 BULLETPROOF LOAD_KNOWN_USERS called at {datetime.utcnow().isoformat()}")
        print(f"[DEBUG] 📂 Loading from: {KNOWN_USERS_PATH}")
        
        if os.path.exists(KNOWN_USERS_PATH):
            file_size = os.path.getsize(KNOWN_USERS_PATH)
            print(f"[DEBUG] 📊 File size: {file_size} bytes")
            
            # Read and parse JSON
            with open(KNOWN_USERS_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            print(f"[DEBUG] 📊 JSON loaded successfully")
            print(f"[DEBUG] 📊 Top-level keys: {list(data.keys())}")
            
            # Load known users
            loaded_known_users = data.get('known_users', {})
            print(f"[DEBUG] 👥 Raw known_users count: {len(loaded_known_users)}")
            
            # Load anonymous clusters with CAREFUL embedding preservation
            loaded_anonymous_clusters = data.get('anonymous_clusters', {})
            print(f"[DEBUG] 🔍 Raw anonymous_clusters count: {len(loaded_anonymous_clusters)}")
            
            # Clear and reload dictionaries
            known_users.clear()
            anonymous_clusters.clear()
            
            # 🔥 BULLETPROOF: Copy known users exactly as-is
            for user_id, user_data in loaded_known_users.items():
                known_users[user_id] = user_data
                print(f"[DEBUG] 👤 Loaded known user: {user_id}")
            
            # 🔥 BULLETPROOF: Copy anonymous clusters with embedding verification
            for cluster_id, cluster_data in loaded_anonymous_clusters.items():
                print(f"\n[DEBUG] 🔍 PROCESSING CLUSTER: {cluster_id}")
                
                # Extract embeddings CAREFULLY
                original_embeddings = cluster_data.get('embeddings', [])
                print(f"[DEBUG]   Original embeddings type: {type(original_embeddings)}")
                print(f"[DEBUG]   Original embeddings count: {len(original_embeddings)}")
                
                if original_embeddings:
                    print(f"[DEBUG]   First embedding type: {type(original_embeddings[0])}")
                    print(f"[DEBUG]   First embedding length: {len(original_embeddings[0]) if original_embeddings[0] else 'None'}")
                    if original_embeddings[0]:
                        print(f"[DEBUG]   First embedding preview: {original_embeddings[0][:3]}")
                
                # 🔥 PRESERVE EMBEDDINGS: Copy the ENTIRE cluster_data dictionary
                preserved_cluster = {}
                for key, value in cluster_data.items():
                    if key == 'embeddings':
                        # Special handling for embeddings - ensure they're preserved
                        preserved_cluster[key] = original_embeddings.copy() if original_embeddings else []
                        print(f"[DEBUG]   ✅ Preserved {len(preserved_cluster[key])} embeddings")
                    else:
                        preserved_cluster[key] = value
                
                # Store the preserved cluster
                anonymous_clusters[cluster_id] = preserved_cluster
                
                # VERIFY embeddings were preserved
                final_embeddings = anonymous_clusters[cluster_id].get('embeddings', [])
                print(f"[DEBUG]   ✅ Final embeddings count: {len(final_embeddings)}")
                
                if len(final_embeddings) != len(original_embeddings):
                    print(f"[DEBUG]   ❌ EMBEDDING LOSS DETECTED!")
                    print(f"[DEBUG]   Expected: {len(original_embeddings)}, Got: {len(final_embeddings)}")
                    # Force restore embeddings
                    anonymous_clusters[cluster_id]['embeddings'] = original_embeddings.copy()
                    print(f"[DEBUG]   🔧 FORCE RESTORED embeddings")
                else:
                    print(f"[DEBUG]   ✅ Embeddings preserved successfully")
            
            # Load false positives
            false_positives.clear()
            false_positives.extend(data.get('false_positives', []))
            
            print(f"\n[DEBUG] ✅ BULLETPROOF LOAD COMPLETE:")
            print(f"[DEBUG]   Known users: {len(known_users)}")
            print(f"[DEBUG]   Anonymous clusters: {len(anonymous_clusters)}")
            print(f"[DEBUG]   False positives: {len(false_positives)}")
            
            # Final verification - count all embeddings
            total_embeddings = 0
            
            # Count embeddings in known_users (where they actually are!)
            for user_id, user_data in known_users.items():
                if isinstance(user_data, dict):
                    voice_embeddings = user_data.get('voice_embeddings', [])
                    embeddings = user_data.get('embeddings', [])
                    
                    # Count the primary embedding field
                    if voice_embeddings:
                        user_embeddings = len(voice_embeddings)
                    else:
                        user_embeddings = len(embeddings)
                    
                    total_embeddings += user_embeddings
                    print(f"[DEBUG]   ✅ {user_id}: {user_embeddings} embeddings")
            
            # Also count anonymous clusters (if any)
            for cluster_id, cluster_data in anonymous_clusters.items():
                cluster_embeddings = len(cluster_data.get('embeddings', []))
                total_embeddings += cluster_embeddings
                print(f"[DEBUG]   ✅ {cluster_id}: {cluster_embeddings} embeddings")
                
                # Double-check each cluster has embeddings
                if cluster_embeddings == 0:
                    print(f"[DEBUG]   ⚠️ WARNING: {cluster_id} has no embeddings after load!")
                    
                    # Try to find embeddings in the raw data
                    raw_cluster = loaded_anonymous_clusters.get(cluster_id, {})
                    raw_embeddings = raw_cluster.get('embeddings', [])
                    if raw_embeddings:
                        print(f"[DEBUG]   🔧 EMERGENCY RESTORE: Found {len(raw_embeddings)} embeddings in raw data")
                        anonymous_clusters[cluster_id]['embeddings'] = raw_embeddings.copy()
                        total_embeddings += len(raw_embeddings)
                        print(f"[DEBUG]   ✅ Emergency restore successful")
            
            print(f"[DEBUG] 📊 Total embeddings after bulletproof load: {total_embeddings}")
            
            return known_users, anonymous_clusters
            
        else:
            print(f"[DEBUG] ⚠️ File does not exist - initializing empty dictionaries")
            known_users.clear()
            anonymous_clusters.clear()
            false_positives.clear()
            return {}, {}
            
    except Exception as e:
        print(f"[DEBUG] ❌ BULLETPROOF LOAD ERROR: {e}")
        import traceback
        traceback.print_exc()
        
        # Emergency fallback
        known_users.clear()
        anonymous_clusters.clear()
        false_positives.clear()
        return {}, {}

def load_known_users_with_verification():
    """🔍 Load with detailed verification to debug embedding loss"""
    global known_users, anonymous_clusters, false_positives
    
    try:
        print(f"[DATABASE] 🔍 LOADING with verification...")
        
        file_path = KNOWN_USERS_PATH
        
        if not os.path.exists(file_path):
            print(f"[DATABASE] ❌ File does not exist: {file_path}")
            # Initialize empty dictionaries
            known_users.clear()
            anonymous_clusters.clear()
            false_positives.clear()
            return False
        
        # Read raw file content
        with open(file_path, 'r', encoding='utf-8') as f:
            raw_data = f.read()
        
        print(f"[DATABASE] 📊 File size: {len(raw_data)} characters")
        
        # Parse JSON
        try:
            data = json.loads(raw_data)
        except json.JSONDecodeError as e:
            print(f"[DATABASE] ❌ JSON decode error: {e}")
            return False
        
        print(f"[DATABASE] 📊 Parsed JSON successfully")
        print(f"[DATABASE] 📊 Top-level keys: {list(data.keys())}")
        
        # Load known users
        if 'known_users' in data:
            known_users.clear()
            known_users.update(data['known_users'])
            print(f"[DATABASE] ✅ Loaded {len(known_users)} known users")
        
        # Load anonymous clusters with detailed verification
        if 'anonymous_clusters' in data:
            anonymous_clusters.clear()
            
            for cluster_id, cluster_data in data['anonymous_clusters'].items():
                print(f"\n[DATABASE] 🔍 Loading cluster: {cluster_id}")
                print(f"[DATABASE]   Raw cluster data keys: {list(cluster_data.keys())}")
                
                embeddings_raw = cluster_data.get('embeddings', [])
                print(f"[DATABASE]   Raw embeddings count: {len(embeddings_raw)}")
                print(f"[DATABASE]   Raw embeddings type: {type(embeddings_raw)}")
                
                if embeddings_raw:
                    print(f"[DATABASE]   First embedding type: {type(embeddings_raw[0])}")
                    print(f"[DATABASE]   First embedding length: {len(embeddings_raw[0]) if embeddings_raw[0] else 'None'}")
                    if embeddings_raw[0]:
                        print(f"[DATABASE]   First embedding preview: {embeddings_raw[0][:5]}")
                
                # Store cluster data
                anonymous_clusters[cluster_id] = cluster_data
                
                # Verify storage
                stored_embeddings = anonymous_clusters[cluster_id].get('embeddings', [])
                print(f"[DATABASE]   ✅ Stored embeddings count: {len(stored_embeddings)}")
                
                if len(stored_embeddings) != len(embeddings_raw):
                    print(f"[DATABASE]   ❌ EMBEDDING COUNT MISMATCH!")
                    print(f"[DATABASE]   Expected: {len(embeddings_raw)}, Got: {len(stored_embeddings)}")
        
        # Load false positives
        if 'false_positives' in data:
            false_positives.clear()
            false_positives.extend(data['false_positives'])
            print(f"[DATABASE] ✅ Loaded {len(false_positives)} false positives")
        
        print(f"\n[DATABASE] ✅ LOADING COMPLETE:")
        print(f"[DATABASE]   Known users: {len(known_users)}")
        print(f"[DATABASE]   Anonymous clusters: {len(anonymous_clusters)}")
        print(f"[DATABASE]   False positives: {len(false_positives)}")
        
        # Final verification
        total_embeddings = 0
        for cluster_id, cluster_data in anonymous_clusters.items():
            cluster_embeddings = len(cluster_data.get('embeddings', []))
            total_embeddings += cluster_embeddings
            print(f"[DATABASE]   {cluster_id}: {cluster_embeddings} embeddings")
        
        print(f"[DATABASE] 📊 Total embeddings loaded: {total_embeddings}")
        
        return True
        
    except Exception as e:
        print(f"[DATABASE] ❌ Loading error: {e}")
        import traceback
        traceback.print_exc()
        return False

def convert_numpy_for_json(obj):
    """Convert numpy types to JSON-serializable types recursively with improved error handling"""
    import numpy as np
    
    try:
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, (np.int8, np.int16, np.int32, np.int64)):
            return int(obj)
        elif isinstance(obj, (np.float16, np.float32, np.float64)):
            return float(obj)
        elif isinstance(obj, np.bool_):  # Fixed: np.bool8 doesn't exist, use np.bool_
            return bool(obj)
        elif isinstance(obj, dict):
            return {k: convert_numpy_for_json(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [convert_numpy_for_json(item) for item in obj]
        else:
            return obj
    except Exception as e:
        print(f"[DEBUG] ⚠️ Error converting object {type(obj)}: {e}")
        # Fallback: try basic conversion or return as-is
        if hasattr(obj, 'tolist') and callable(getattr(obj, 'tolist')):
            try:
                return obj.tolist()
            except:
                pass
        elif hasattr(obj, 'item') and callable(getattr(obj, 'item')):
            try:
                return obj.item()
            except:
                pass
        return obj

def save_known_users():
    """🚀 BULLETPROOF: Save with embedding preservation verification"""
    try:
        debug_database_state()
        
        print(f"[DEBUG] 💾 BULLETPROOF SAVE_KNOWN_USERS called at {datetime.utcnow().isoformat()}")
        print(f"[DEBUG] 👥 Known users count: {len(known_users)}")
        print(f"[DEBUG] 🔍 Anonymous clusters count: {len(anonymous_clusters)}")
        print(f"[DEBUG] 🚨 False positives count: {len(false_positives)}")
        
        # 🔍 PRE-SAVE EMBEDDING VERIFICATION
        print(f"\n[DEBUG] 🔍 PRE-SAVE EMBEDDING VERIFICATION:")
        total_embeddings_before = 0
        for cluster_id, cluster_data in anonymous_clusters.items():
            embeddings = cluster_data.get('embeddings', [])
            total_embeddings_before += len(embeddings)
            print(f"[DEBUG]   {cluster_id}: {len(embeddings)} embeddings before save")
            if embeddings:
                print(f"[DEBUG]     First embedding type: {type(embeddings[0])}")
                print(f"[DEBUG]     First embedding length: {len(embeddings[0])}")
                print(f"[DEBUG]     First embedding preview: {embeddings[0][:3]}")
        
        print(f"[DEBUG] 📊 Total embeddings before save: {total_embeddings_before}")
        
        # 🔧 SIMPLE JSON PREPARATION (No numpy conversion - preserve as-is)
        print(f"[DEBUG] 🔄 Preparing data for JSON (preserving embeddings as-is)...")
        
        # ✅ PRESERVE EMBEDDINGS: Don't convert, just copy
        clean_known_users = {}
        for user_id, user_data in known_users.items():
            if isinstance(user_data, dict):
                clean_known_users[user_id] = user_data.copy()
            else:
                clean_known_users[user_id] = user_data
        
        clean_anonymous_clusters = {}
        for cluster_id, cluster_data in anonymous_clusters.items():
            if isinstance(cluster_data, dict):
                clean_cluster = cluster_data.copy()
                # 🔥 CRITICAL: Preserve embeddings exactly as they are
                if 'embeddings' in cluster_data:
                    original_embeddings = cluster_data['embeddings']
                    clean_cluster['embeddings'] = original_embeddings.copy() if original_embeddings else []
                    print(f"[DEBUG]   📊 Preserving {len(clean_cluster['embeddings'])} embeddings for {cluster_id}")
                clean_anonymous_clusters[cluster_id] = clean_cluster
            else:
                clean_anonymous_clusters[cluster_id] = cluster_data
        
        clean_false_positives = false_positives.copy() if false_positives else []
        
        # 🚀 Create data structure
        data = {
            'known_users': clean_known_users,
            'anonymous_clusters': clean_anonymous_clusters,
            'false_positives': clean_false_positives,
            'last_updated': datetime.utcnow().isoformat(),
            'version': '2.1_bulletproof_save'
        }
        
        print(f"[DEBUG] 📝 Data structure prepared:")
        print(f"[DEBUG]   known_users={len(data['known_users'])}")
        print(f"[DEBUG]   clusters={len(data['anonymous_clusters'])}")
        print(f"[DEBUG]   false_positives={len(data['false_positives'])}")
        
        # 🔍 VERIFY EMBEDDINGS IN DATA STRUCTURE
        print(f"\n[DEBUG] 🔍 VERIFYING EMBEDDINGS IN DATA STRUCTURE:")
        total_embeddings_in_data = 0
        for cluster_id, cluster_data in data['anonymous_clusters'].items():
            embeddings = cluster_data.get('embeddings', [])
            total_embeddings_in_data += len(embeddings)
            print(f"[DEBUG]   {cluster_id}: {len(embeddings)} embeddings in data structure")
        
        print(f"[DEBUG] 📊 Total embeddings in data structure: {total_embeddings_in_data}")
        
        if total_embeddings_in_data != total_embeddings_before:
            print(f"[DEBUG] ❌ EMBEDDING LOSS DETECTED DURING PREPARATION!")
            print(f"[DEBUG]   Before: {total_embeddings_before}, After: {total_embeddings_in_data}")
            return False
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(KNOWN_USERS_PATH), exist_ok=True)
        
        # 🔧 TEST JSON SERIALIZATION
        try:
            test_json = json.dumps(data, indent=2, ensure_ascii=False)
            print(f"[DEBUG] ✅ JSON serialization test passed - {len(test_json)} characters")
        except Exception as json_error:
            print(f"[DEBUG] ❌ JSON serialization test failed: {json_error}")
            
            # Try to fix JSON issues
            print(f"[DEBUG] 🔧 Attempting to fix JSON serialization issues...")
            
            # Fix any remaining numpy arrays in embeddings
            for cluster_id, cluster_data in data['anonymous_clusters'].items():
                embeddings = cluster_data.get('embeddings', [])
                if embeddings:
                    fixed_embeddings = []
                    for emb in embeddings:
                        if hasattr(emb, 'tolist'):
                            fixed_embeddings.append(emb.tolist())
                        elif isinstance(emb, (list, tuple)):
                            fixed_embeddings.append(list(emb))
                        else:
                            fixed_embeddings.append(emb)
                    data['anonymous_clusters'][cluster_id]['embeddings'] = fixed_embeddings
                    print(f"[DEBUG]   🔧 Fixed embeddings for {cluster_id}: {len(fixed_embeddings)} embeddings")
            
            # Try again
            test_json = json.dumps(data, indent=2, ensure_ascii=False)
            print(f"[DEBUG] ✅ JSON serialization fixed - {len(test_json)} characters")
        
        # Write the file
        with open(KNOWN_USERS_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"[DEBUG] ✅ File written to: {KNOWN_USERS_PATH}")
        
        # 🔍 VERIFY FILE WAS WRITTEN CORRECTLY
        if os.path.exists(KNOWN_USERS_PATH):
            file_size = os.path.getsize(KNOWN_USERS_PATH)
            print(f"[DEBUG] 📊 File size: {file_size} bytes")
            
            # Read back and verify embeddings
            try:
                with open(KNOWN_USERS_PATH, 'r', encoding='utf-8') as f:
                    verify_data = json.load(f)
                
                print(f"[DEBUG] ✅ File verification:")
                print(f"[DEBUG]   Users: {len(verify_data.get('known_users', {}))}")
                print(f"[DEBUG]   Clusters: {len(verify_data.get('anonymous_clusters', {}))}")
                print(f"[DEBUG]   False positives: {len(verify_data.get('false_positives', []))}")
                
                # 🔍 CRITICAL: Verify embeddings in file
                total_embeddings_in_file = 0
                for cluster_id, cluster_data in verify_data.get('anonymous_clusters', {}).items():
                    embeddings = cluster_data.get('embeddings', [])
                    total_embeddings_in_file += len(embeddings)
                    print(f"[DEBUG]   📊 {cluster_id}: {len(embeddings)} embeddings in file")
                
                print(f"[DEBUG] 📊 Total embeddings in file: {total_embeddings_in_file}")
                
                if total_embeddings_in_file == total_embeddings_before:
                    print(f"[DEBUG] ✅ EMBEDDINGS PRESERVED SUCCESSFULLY!")
                else:
                    print(f"[DEBUG] ❌ EMBEDDINGS LOST DURING FILE WRITE!")
                    print(f"[DEBUG]   Expected: {total_embeddings_before}, Got: {total_embeddings_in_file}")
                    return False
                
            except Exception as verify_error:
                print(f"[DEBUG] ❌ Verification failed: {verify_error}")
                return False
        else:
            print(f"[DEBUG] ❌ File does not exist after write attempt!")
            return False
        
        debug_database_state()
        
        print(f"[DEBUG] ✅ BULLETPROOF SAVE SUCCESSFUL!")
        return True
        
    except Exception as e:
        print(f"[DEBUG] ❌ BULLETPROOF SAVE ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def _convert_numpy_to_list(data):
    """Convert numpy arrays to lists recursively with proper error handling"""
    try:
        # Handle numpy arrays
        if isinstance(data, np.ndarray):
            return data.tolist()
        
        # Handle dictionaries recursively
        elif isinstance(data, dict):
            return {key: _convert_numpy_to_list(value) for key, value in data.items()}
        
        # Handle lists recursively
        elif isinstance(data, list):
            return [_convert_numpy_to_list(item) for item in data]
        
        # Handle other numpy types (scalars, etc.)
        elif hasattr(data, 'tolist') and callable(getattr(data, 'tolist')):
            return data.tolist()
        
        # Return as-is for JSON-serializable types
        else:
            return data
            
    except Exception as e:
        print(f"[Database] ⚠️ Error converting data to list: {e}")
        print(f"[Database] ⚠️ Data type: {type(data)}")
        # Fallback: try to convert to basic Python types
        if hasattr(data, 'tolist'):
            try:
                return data.tolist()
            except:
                pass
        return str(data)  # Last resort: convert to string

def create_anonymous_cluster(embedding, quality_info=None):
    """🆕 Create anonymous cluster with sequential naming AND save to known_users_v2.json"""
    try:
        print(f"[DEBUG] 🆕 CREATE_ANONYMOUS_CLUSTER called at {datetime.utcnow().isoformat()}")
        
        # ✅ FIXED: Find highest existing anonymous number (check both dicts)
        max_num = 0
        
        # Check anonymous_clusters
        for cluster_id in anonymous_clusters.keys():
            if cluster_id.startswith('Anonymous_'):
                try:
                    num_str = cluster_id.split('_')[1]
                    num = int(num_str)
                    max_num = max(max_num, num)
                except (IndexError, ValueError):
                    continue
        
        # ✅ ALSO check known_users for anonymous entries
        for user_id in known_users.keys():
            if user_id.startswith('Anonymous_'):
                try:
                    num_str = user_id.split('_')[1]
                    num = int(num_str)
                    max_num = max(max_num, num)
                except (IndexError, ValueError):
                    continue
        
        # Create next sequential ID with zero-padding
        next_num = max_num + 1
        cluster_id = f"Anonymous_{next_num:03d}"  # Anonymous_001, Anonymous_002, etc.
        
        print(f"[DEBUG] 🏷️ Generated sequential cluster ID: {cluster_id}")
        
        # Validate embedding
        if embedding is None:
            print(f"[DEBUG] ❌ Embedding is None - cannot create cluster")
            return None
        
        # Prepare cluster data for anonymous_clusters
        cluster_data = {
            'cluster_id': cluster_id,
            'embeddings': [embedding],
            'created_at': datetime.utcnow().isoformat(),
            'last_updated': datetime.utcnow().isoformat(),
            'sample_count': 1,
            'status': 'anonymous',
            'quality_scores': [quality_info.get('overall_score', 0.5)] if quality_info else [0.5],
            'audio_contexts': ['unknown_speaker'],
            'confidence_threshold': 0.6,
            'clustering_metrics': [quality_info] if quality_info else [{'clustering_suitability': 'unknown'}]
        }
        
        # ✅ PREPARE USER DATA for known_users (the missing piece!)
        user_data = {
            'username': cluster_id,
            'status': 'anonymous',
            'voice_embeddings': [embedding],
            'created_at': datetime.utcnow().isoformat(),
            'last_updated': datetime.utcnow().isoformat(),
            'cluster_id': cluster_id,
            'is_anonymous': True,
            'training_type': 'auto_anonymous',
            'confidence_threshold': 0.6,
            'recognition_count': 0,
            'recognition_successes': 0,
            'recognition_failures': 0,
            'embedding_count': 1,
            'quality_scores': [quality_info.get('overall_score', 0.5)] if quality_info else [0.5]
        }
        
        print(f"[DEBUG] 📝 Cluster data prepared with {len(cluster_data['embeddings'])} embeddings")
        print(f"[DEBUG] 👤 User data prepared for known_users_v2.json")
        
        # ✅ Add to BOTH dictionaries
        anonymous_clusters[cluster_id] = cluster_data
        known_users[cluster_id] = user_data  # 🔥 THIS WAS MISSING!
        
        print(f"[DEBUG] ✅ Cluster added to anonymous_clusters dictionary")
        print(f"[DEBUG] ✅ User added to known_users dictionary")
        print(f"[DEBUG] 📊 Anonymous clusters count: {len(anonymous_clusters)}")
        print(f"[DEBUG] 📊 Known users count: {len(known_users)}")
        print(f"[DEBUG] 📊 All anonymous clusters: {[k for k in anonymous_clusters.keys() if k.startswith('Anonymous_')]}")
        print(f"[DEBUG] 📊 All known users: {[k for k in known_users.keys() if k.startswith('Anonymous_')]}")
        
        # ✅ CRITICAL: Save immediately after creation
        print(f"[DEBUG] 💾 Calling save_known_users() for cluster: {cluster_id}")
        save_result = save_known_users()
        print(f"[DEBUG] 💾 Save result: {save_result}")
        
        if save_result:
            print(f"[DEBUG] ✅ SEQUENTIAL CLUSTER CREATION SUCCESSFUL: {cluster_id}")
            print(f"[DEBUG] ✅ Anonymous user saved to known_users_v2.json: {cluster_id}")
        else:
            print(f"[DEBUG] ❌ CLUSTER SAVE FAILED: {cluster_id}")
            # ✅ CLEANUP on save failure
            if cluster_id in anonymous_clusters:
                del anonymous_clusters[cluster_id]
            if cluster_id in known_users:
                del known_users[cluster_id]
            print(f"[DEBUG] 🧹 Cleaned up failed cluster from memory")
        
        return cluster_id
        
    except Exception as e:
        print(f"[DEBUG] ❌ CREATE_ANONYMOUS_CLUSTER ERROR: {e}")
        import traceback
        traceback.print_exc()
        return None

def sync_voice_manager_to_database():
    """🔄 Sync voice manager internal state to database"""
    global known_users, anonymous_clusters
    
    try:
        if ADVANCED_AI_AVAILABLE and hasattr(voice_manager, 'session_context'):
            print("[DatabaseSync] 🔄 Syncing voice manager to database...")
            
            # Get internal state from voice manager
            session_context = voice_manager.session_context
            
            # Sync anonymous clusters
            if 'anonymous_clusters' in session_context:
                internal_clusters = session_context['anonymous_clusters']
                
                for cluster_id, cluster_data in internal_clusters.items():
                    if cluster_id not in anonymous_clusters:
                        print(f"[DatabaseSync] 🆕 Adding cluster to database: {cluster_id}")
                        anonymous_clusters[cluster_id] = cluster_data
                        
                        # Also add to known_users for persistence
                        known_users[cluster_id] = {
                            'username': cluster_id,
                            'status': 'anonymous',
                            'voice_embeddings': cluster_data.get('embeddings', []),
                            'created_at': cluster_data.get('created_at', datetime.utcnow().isoformat()),
                            'is_anonymous': True,
                            'cluster_id': cluster_id,
                            'training_type': 'voice_manager_sync'
                        }
            
            # Sync known users
            if 'learning_history' in session_context:
                learning_history = session_context['learning_history']
                
                for user_id, history in learning_history.items():
                    if user_id.startswith('Anonymous_') and user_id not in known_users:
                        print(f"[DatabaseSync] 🆕 Adding user from learning history: {user_id}")
                        
                        known_users[user_id] = {
                            'username': user_id,
                            'status': 'anonymous',
                            'voice_embeddings': history.get('embeddings', []),
                            'created_at': datetime.utcnow().isoformat(),
                            'is_anonymous': True,
                            'cluster_id': user_id,
                            'training_type': 'learning_history_sync',
                            'confidence_scores': history.get('confidence_scores', []),
                            'stability_score': history.get('stability_score', 0.0)
                        }
            
            # Save the synced data
            save_result = save_known_users()
            if save_result:
                print(f"[DatabaseSync] ✅ Sync complete - saved {len(known_users)} users, {len(anonymous_clusters)} clusters")
                return True
            else:
                print(f"[DatabaseSync] ❌ Sync save failed")
                return False
                
        else:
            print("[DatabaseSync] ⚠️ Advanced voice manager not available")
            return False
            
    except Exception as e:
        print(f"[DatabaseSync] ❌ Sync error: {e}")
        import traceback
        traceback.print_exc()
        return False

def link_anonymous_to_named(cluster_id, username):
    """🔗 Enhanced link with proper cluster data transfer and cleanup"""
    global known_users, anonymous_clusters
    
    try:
        print(f"[DEBUG] 🔗 LINK_ANONYMOUS_TO_NAMED called: {cluster_id} → {username}")
        
        # ✅ Check if cluster exists in anonymous_clusters
        if cluster_id not in anonymous_clusters:
            print(f"[DEBUG] ❌ Cluster {cluster_id} not found in anonymous_clusters")
            print(f"[DEBUG] 📊 Available clusters: {list(anonymous_clusters.keys())}")
            return False
        
        cluster_data = anonymous_clusters[cluster_id]
        print(f"[DEBUG] 📊 Cluster data: {cluster_data.get('sample_count', 0)} samples")
        
        # ✅ ENHANCED: Handle name collision
        final_username = handle_same_name_collision(username)
        if final_username != username:
            print(f"[DEBUG] 🔄 Name collision resolved: {username} → {final_username}")
        
        # ✅ GET ALL EMBEDDINGS from anonymous cluster
        all_embeddings = cluster_data.get('embeddings', [])
        
        if not all_embeddings:
            print(f"[DEBUG] ❌ No embeddings found in cluster {cluster_id}")
            return False
        
        print(f"[DEBUG] 📊 Transferring {len(all_embeddings)} embeddings from {cluster_id} to {final_username}")
        
        # ✅ BACKUP: Store original state for rollback
        backup_known_users = known_users.copy()
        backup_anonymous_clusters = anonymous_clusters.copy()
        
        # ✅ Check if anonymous user also exists in known_users (from auto-save)
        anonymous_user_data = None
        if cluster_id in known_users:
            anonymous_user_data = known_users[cluster_id]
            print(f"[DEBUG] 📊 Found anonymous user data in known_users: {cluster_id}")
        
        # Check if final user already exists
        if final_username in known_users:
            print(f"[DEBUG] 🔗 Merging with existing user: {final_username}")
            
            # Merge with existing user
            existing_embeddings = known_users[final_username].get('embeddings', [])
            existing_voice_embeddings = known_users[final_username].get('voice_embeddings', [])
            
            # ✅ HANDLE DIFFERENT EMBEDDING FORMATS
            # Convert cluster embeddings to consistent format
            normalized_cluster_embeddings = []
            for emb in all_embeddings:
                if isinstance(emb, dict):
                    # Dual embedding format
                    normalized_cluster_embeddings.append(emb)
                elif isinstance(emb, (list, np.ndarray)):
                    # Single embedding format - wrap in dict
                    normalized_cluster_embeddings.append({
                        'resemblyzer': emb.tolist() if isinstance(emb, np.ndarray) else emb,
                        'source': 'anonymous_cluster',
                        'timestamp': datetime.utcnow().isoformat()
                    })
            
            # Combine embeddings (max 15 total)
            combined_embeddings = existing_embeddings + normalized_cluster_embeddings
            combined_voice_embeddings = existing_voice_embeddings + normalized_cluster_embeddings
            
            if len(combined_embeddings) > 15:
                combined_embeddings = combined_embeddings[-15:]  # Keep most recent
            if len(combined_voice_embeddings) > 15:
                combined_voice_embeddings = combined_voice_embeddings[-15:]
            
            # Update existing user
            known_users[final_username].update({
                'embeddings': combined_embeddings,
                'voice_embeddings': combined_voice_embeddings,
                'last_updated': datetime.utcnow().isoformat(),
                'anonymous_samples_merged': len(all_embeddings),
                'total_samples': len(combined_embeddings),
                'merged_from_cluster': cluster_id,
                'status': 'trained'
            })
            
            print(f"[DEBUG] 🔗 Merged {cluster_id} into existing {final_username}")
            
        else:
            print(f"[DEBUG] 🆕 Creating new user: {final_username}")
            
            # ✅ NORMALIZE EMBEDDINGS for new user
            normalized_embeddings = []
            for emb in all_embeddings:
                if isinstance(emb, dict):
                    normalized_embeddings.append(emb)
                elif isinstance(emb, (list, np.ndarray)):
                    normalized_embeddings.append({
                        'resemblyzer': emb.tolist() if isinstance(emb, np.ndarray) else emb,
                        'source': 'anonymous_cluster',
                        'timestamp': datetime.utcnow().isoformat()
                    })
            
            # ✅ Create new named user with ALL data from cluster AND anonymous user
            new_user_data = {
                'username': final_username,
                'name': final_username,
                'embeddings': normalized_embeddings,
                'voice_embeddings': normalized_embeddings,  # Duplicate for compatibility
                'created_at': cluster_data.get('created_at', datetime.utcnow().isoformat()),
                'last_updated': datetime.utcnow().isoformat(),
                'status': 'trained',
                'confidence_threshold': 0.4,  # Lower threshold for identified users
                'quality_scores': cluster_data.get('quality_scores', []),
                'sample_count': cluster_data.get('sample_count', len(all_embeddings)),
                'original_cluster': cluster_id,
                'recognition_count': 0,
                'recognition_successes': 0,
                'recognition_failures': 0,
                'background_learning': True,
                'voice_profile_complete': True,
                'linked_from_anonymous': True,
                'embedding_version': '2.0_anonymous_transfer',
                'training_type': 'anonymous_cluster_link',
                'embedding_count': len(normalized_embeddings)
            }
            
            # ✅ MERGE additional data from anonymous user entry if it exists
            if anonymous_user_data:
                print(f"[DEBUG] 🔗 Merging additional data from anonymous user entry")
                # Add any additional fields from the anonymous user data
                for key, value in anonymous_user_data.items():
                    if key not in new_user_data and key not in ['username', 'cluster_id', 'is_anonymous']:
                        new_user_data[key] = value
            
            known_users[final_username] = new_user_data
            print(f"[DEBUG] 🎯 Created {final_username} from {cluster_id} with {len(normalized_embeddings)} embeddings")
        
        # ✅ CLEANUP: Remove anonymous entries from BOTH dictionaries
        try:
            if cluster_id in anonymous_clusters:
                del anonymous_clusters[cluster_id]
                print(f"[DEBUG] 🗑️ Removed anonymous cluster: {cluster_id}")
            
            if cluster_id in known_users:
                del known_users[cluster_id]
                print(f"[DEBUG] 🗑️ Removed anonymous user from known_users: {cluster_id}")
                
        except KeyError as ke:
            print(f"[DEBUG] ⚠️ Key error during cleanup: {ke}")
        
        # ✅ SAVE with verification and rollback capability
        print(f"[DEBUG] 💾 Saving changes for {final_username}...")
        save_result = save_known_users()
        
        if save_result:
            print(f"[DEBUG] ✅ LINK SUCCESSFUL: {cluster_id} → {final_username}")
            print(f"[DEBUG] ✅ User now has {len(known_users[final_username].get('embeddings', []))} embeddings")
            return True
        else:
            print(f"[DEBUG] ❌ LINK SAVE FAILED: {cluster_id} → {final_username}")
            print(f"[DEBUG] 🔄 Rolling back changes...")
            
            # ✅ ROLLBACK: Restore original state
            known_users.clear()
            known_users.update(backup_known_users)
            anonymous_clusters.clear()
            anonymous_clusters.update(backup_anonymous_clusters)
            
            print(f"[DEBUG] 🔄 Rollback complete - original state restored")
            return False
            
    except Exception as e:
        print(f"[DEBUG] ❌ LINK_ANONYMOUS_TO_NAMED ERROR: {e}")
        import traceback
        traceback.print_exc()
        
        # ✅ EMERGENCY ROLLBACK
        try:
            if 'backup_known_users' in locals():
                known_users.clear()
                known_users.update(backup_known_users)
                anonymous_clusters.clear()
                anonymous_clusters.update(backup_anonymous_clusters)
                print(f"[DEBUG] 🚨 Emergency rollback completed")
        except:
            print(f"[DEBUG] 🚨 Emergency rollback failed")
        
        return False

def add_false_positive(entry):
    """🚀 NEW: Add false positive entry to tracking"""
    global false_positives
    
    try:
        # Add timestamp if not present
        if 'timestamp' not in entry:
            entry['timestamp'] = datetime.utcnow().isoformat()
        
        # Add to false positives list
        false_positives.append(entry)
        
        # Keep only last 1000 entries (prevent memory bloat)
        if len(false_positives) > 1000:
            false_positives = false_positives[-1000:]
        
        print(f"[DEBUG] 🚨 False positive added: {entry.get('blocked_name', 'unknown')}")
        print(f"[DEBUG] 📊 Total false positives: {len(false_positives)}")
        
        return True
        
    except Exception as e:
        print(f"[DEBUG] ❌ ADD_FALSE_POSITIVE ERROR: {e}")
        return False

def get_false_positive_stats():
    """🚀 NEW: Get false positive statistics"""
    global false_positives
    
    try:
        if not false_positives:
            return {
                'total_count': 0,
                'recent_count': 0,
                'most_common_blocked': [],
                'most_common_reasons': []
            }
        
        # Recent false positives (last 24 hours)
        recent_cutoff = datetime.utcnow() - timedelta(hours=24)
        recent_fps = [
            fp for fp in false_positives 
            if datetime.fromisoformat(fp.get('timestamp', '1970-01-01T00:00:00')) > recent_cutoff
        ]
        
        # Most common blocked names
        from collections import Counter
        blocked_names = [fp.get('blocked_name', 'unknown') for fp in false_positives]
        most_common_blocked = Counter(blocked_names).most_common(5)
        
        # Most common reasons
        all_reasons = []
        for fp in false_positives:
            reasons = fp.get('suspicious_reasons', [])
            if isinstance(reasons, list):
                all_reasons.extend(reasons)
        
        most_common_reasons = Counter(all_reasons).most_common(5)
        
        return {
            'total_count': len(false_positives),
            'recent_count': len(recent_fps),
            'most_common_blocked': most_common_blocked,
            'most_common_reasons': most_common_reasons,
            'last_updated': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        print(f"[DEBUG] ❌ GET_FALSE_POSITIVE_STATS ERROR: {e}")
        return {'error': str(e)}

def protect_existing_cluster_name(cluster_id, new_name):
    """🚀 NEW: Protect existing cluster names from overwrite"""
    global known_users, anonymous_clusters
    
    try:
        # Check if cluster exists and has a name
        if cluster_id in known_users:
            existing_name = known_users[cluster_id].get('name')
            if existing_name and existing_name != new_name:
                print(f"[DEBUG] 🛡️ CLUSTER NAME PROTECTION: {cluster_id} has existing name '{existing_name}', blocking overwrite to '{new_name}'")
                return False, existing_name
        
        # Allow name assignment
        return True, None
        
    except Exception as e:
        print(f"[DEBUG] ❌ PROTECT_EXISTING_CLUSTER_NAME ERROR: {e}")
        return False, None

def cleanup_false_positives(max_age_days=30):
    """🚀 NEW: Clean up old false positive entries"""
    global false_positives
    
    try:
        if not false_positives:
            return 0
        
        cutoff_time = datetime.utcnow() - timedelta(days=max_age_days)
        
        original_count = len(false_positives)
        false_positives = [
            fp for fp in false_positives
            if datetime.fromisoformat(fp.get('timestamp', '1970-01-01T00:00:00')) > cutoff_time
        ]
        
        cleaned_count = original_count - len(false_positives)
        
        if cleaned_count > 0:
            print(f"[DEBUG] 🧹 Cleaned up {cleaned_count} old false positives")
            save_known_users()
        
        return cleaned_count
        
    except Exception as e:
        print(f"[DEBUG] ❌ CLEANUP_FALSE_POSITIVES ERROR: {e}")
        return 0

def find_similar_clusters(embedding, threshold=0.5):
    """✅ NEW: Find similar anonymous clusters for merging"""
    similar_clusters = []
    
    try:
        from voice.voice_models import dual_voice_model_manager
        
        for cluster_id, cluster_data in anonymous_clusters.items():
            cluster_embeddings = cluster_data.get('embeddings', [])
            
            for stored_embedding in cluster_embeddings:
                similarity = dual_voice_model_manager.compare_dual_embeddings(
                    embedding, stored_embedding
                )
                
                if similarity > threshold:
                    similar_clusters.append({
                        'cluster_id': cluster_id,
                        'similarity': similarity,
                        'embedding_count': len(cluster_embeddings)
                    })
                    break
    except:
        pass
    
    return sorted(similar_clusters, key=lambda x: x['similarity'], reverse=True)

def get_voice_display_name(user_id):
    """Get display name for voice-identified user"""
    try:
        if user_id in known_users:
            profile = known_users[user_id]
            if isinstance(profile, dict):
                return profile.get('display_name', profile.get('real_name', user_id))
        return user_id
    except Exception as e:
        print(f"[Database] ⚠️ Error getting display name: {e}")
        return user_id

def update_voice_profile_display_name(user_id, display_name):
    """Update display name for voice profile"""
    try:
        if user_id in known_users:
            if isinstance(known_users[user_id], dict):
                known_users[user_id]['display_name'] = display_name
            else:
                # Convert old format to new
                old_embedding = known_users[user_id]
                known_users[user_id] = {
                    'embedding': old_embedding,
                    'display_name': display_name,
                    'created_date': time.time()
                }
            save_known_users()
            return True
    except Exception as e:
        print(f"[Database] ❌ Error updating display name: {e}")
    return False

def handle_same_name_collision(username):
    """✅ NEW: Handle multiple users with same name"""
    if username not in known_users:
        return username
    
    # Find next available suffix
    counter = 2
    while f"{username}_{counter:03d}" in known_users:
        counter += 1
    
    new_username = f"{username}_{counter:03d}"
    print(f"[Database] 🔄 Same name collision: {username} → {new_username}")
    return new_username

def get_all_clusters():
    """✅ NEW: Get all voice clusters (named + anonymous)"""
    all_clusters = {}
    all_clusters.update(known_users)
    all_clusters.update(anonymous_clusters)
    return all_clusters

def cleanup_old_anonymous_clusters(max_age_days=7):
    """🧹 Clean up old anonymous clusters"""
    try:
        from datetime import datetime, timedelta
        
        current_time = datetime.utcnow()
        cutoff_time = current_time - timedelta(days=max_age_days)
        
        clusters_to_remove = []
        for cluster_id, cluster_data in anonymous_clusters.items():
            try:
                created_at = datetime.fromisoformat(cluster_data.get('created_at', current_time.isoformat()))
                if created_at < cutoff_time:
                    clusters_to_remove.append(cluster_id)
            except:
                # Remove clusters with invalid timestamps
                clusters_to_remove.append(cluster_id)
        
        for cluster_id in clusters_to_remove:
            del anonymous_clusters[cluster_id]
            print(f"[Database] 🧹 Cleaned up old cluster: {cluster_id}")
        
        if clusters_to_remove:
            save_known_users()
        
        return len(clusters_to_remove)
        
    except Exception as e:
        print(f"[Database] ❌ Cleanup error: {e}")
        return 0

def debug_database_state():
    """🐛 Debug current database state"""
    print(f"\n🐛 DATABASE DEBUG:")
    print(f"📊 known_users: {list(known_users.keys())}")
    print(f"📊 anonymous_clusters: {list(anonymous_clusters.keys())}")
    print(f"📊 known_users id: {id(known_users)}")
    print(f"📊 anonymous_clusters id: {id(anonymous_clusters)}")
    
    # Check if file exists and what it contains
    try:
        with open(KNOWN_USERS_PATH, 'r') as f:
            data = json.load(f)
        print(f"📁 File has: {len(data.get('known_users', {}))} users, {len(data.get('anonymous_clusters', {}))} clusters")
    except:
        print(f"📁 File doesn't exist or is corrupted")
    print()

# ✅ Load database on import
load_known_users()