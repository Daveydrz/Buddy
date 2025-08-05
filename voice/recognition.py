# voice/recognition.py - Enhanced recognition with clustering and advanced AI
import numpy as np
import json  # ✅ ADDED: Missing import for export functions
from sklearn.metrics.pairwise import cosine_similarity
from config import DEBUG, SAMPLE_RATE, VOICE_CONFIDENCE_THRESHOLD
import time
from datetime import datetime
from voice.database import known_users, save_known_users, handle_same_name_collision

# Try enhanced modules first
try:
    from voice.speaker_profiles import enhanced_speaker_profiles
    from voice.voice_models import dual_voice_model_manager
    ENHANCED_AVAILABLE = True
    print("[Recognition] ✅ Enhanced modules available")
except ImportError:
    ENHANCED_AVAILABLE = False
    print("[Recognition] ⚠️ Using basic recognition")

# Fallback to basic resemblyzer
try:
    from resemblyzer import VoiceEncoder
    encoder = VoiceEncoder()
    RESEMBLYZER_AVAILABLE = True
except ImportError:
    RESEMBLYZER_AVAILABLE = False
    print("[Recognition] ⚠️ Resemblyzer not available")

def generate_voice_embedding(audio):
    """🎯 Enhanced voice embedding generation with clustering support"""
    if ENHANCED_AVAILABLE:
        # Use dual model system
        result = dual_voice_model_manager.generate_dual_embedding(audio)
        if result and 'resemblyzer' in result:
            return np.array(result['resemblyzer'])
        return None
    elif RESEMBLYZER_AVAILABLE:
        # Fallback to basic resemblyzer
        try:
            if len(audio) < SAMPLE_RATE:
                return None
            
            audio_float = audio.astype(np.float32)
            if np.max(np.abs(audio_float)) > 1.0:
                audio_float = audio_float / 32768.0
            
            embedding = encoder.embed_utterance(audio_float)
            return embedding if embedding is not None else None
        except Exception as e:
            if DEBUG:
                print(f"[Recognition] ❌ Basic embedding error: {e}")
            return None
    else:
        return None

def identify_speaker_with_confidence(audio):
    """Enhanced speaker identification that stores audio for later use"""
    try:
        # Store audio sample in voice manager
        if 'voice_manager' in globals():
            voice_manager.set_last_audio_sample(audio)
        
        # Existing identification logic
        if ENHANCED_AVAILABLE:
            identified_user, confidence, debug_info = enhanced_speaker_profiles.recognize_with_multiple_embeddings(audio)
        else:
            identified_user, confidence = basic_identify_speaker_with_confidence(audio)
        
        # Store the result for later retrieval
        if 'voice_manager' in globals():
            voice_manager.last_identified_user = identified_user if confidence > 0.7 else None
        
        return identified_user, confidence
        
    except Exception as e:
        print(f"[Recognition] ❌ Error in identification: {e}")
        return "Unknown", 0.0

def check_anonymous_clusters(audio):
    """🔍 Check audio against anonymous clusters"""
    try:
        if not ENHANCED_AVAILABLE:
            return "UNKNOWN", 0.0

        from voice.database import anonymous_clusters, find_similar_clusters, create_anonymous_cluster, save_known_users

        if not anonymous_clusters:
            # ✅ Nothing exists yet, create new cluster
            embedding = dual_voice_model_manager.generate_dual_embedding(audio)
            if embedding is not None:
                create_anonymous_cluster(embedding)
                save_known_users()
                print("[Recognition] ✅ Created new anonymous cluster")
            return "UNKNOWN", 0.0

        # Generate embedding for comparison
        embedding = dual_voice_model_manager.generate_dual_embedding(audio)
        if embedding is None:
            return "UNKNOWN", 0.0

        # Find similar clusters
        similar_clusters = find_similar_clusters(embedding, threshold=0.6)

        if similar_clusters:
            best_cluster = similar_clusters[0]
            cluster_id = best_cluster['cluster_id']
            confidence = best_cluster['similarity']

            print(f"[Recognition] 🔗 Anonymous cluster match: {cluster_id} ({confidence:.3f})")
            return cluster_id, confidence

        # ✅ If no match, create new cluster too
        create_anonymous_cluster(embedding)
        save_known_users()
        print("[Recognition] ✅ Created new anonymous cluster")

        return "UNKNOWN", 0.0

    except Exception as e:
        if DEBUG:
            print(f"[Recognition] ❌ Cluster check error: {e}")
        return "UNKNOWN", 0.0

def basic_identify_speaker_with_confidence(audio):
    """🔄 Basic speaker identification fallback"""
    try:
        from voice.database import known_users, anonymous_clusters
        
        # Check known users first
        if known_users:
            result = check_known_users(audio)
            if result[0] != "UNKNOWN":
                return result
        
        # Check anonymous clusters
        if anonymous_clusters:
            result = check_anonymous_clusters_basic(audio)
            if result[0] != "UNKNOWN":
                return result
        
        return "UNKNOWN", 0.0
        
    except Exception as e:
        if DEBUG:
            print(f"[Recognition] ❌ Basic recognition error: {e}")
        return "UNKNOWN", 0.0

def check_known_users(audio):
    """👤 Check against known users"""
    try:
        from voice.database import known_users
        
        embedding = generate_voice_embedding(audio)
        if embedding is None:
            return "UNKNOWN", 0.0
        
        best_match = None
        best_score = 0.0
        
        for name, user_data in known_users.items():
            try:
                # Handle different data formats
                if isinstance(user_data, dict):
                    # Multiple embeddings format
                    if 'embeddings' in user_data:
                        embeddings = user_data['embeddings']
                        scores = []
                        
                        for stored_embedding in embeddings:
                            if isinstance(stored_embedding, dict) and 'resemblyzer' in stored_embedding:
                                stored_emb = stored_embedding['resemblyzer']
                            else:
                                stored_emb = stored_embedding
                            
                            if isinstance(stored_emb, list) and len(stored_emb) == 256:
                                similarity = cosine_similarity([embedding], [stored_emb])[0][0]
                                scores.append(similarity)
                        
                        if scores:
                            # Use best score from multiple embeddings
                            user_score = max(scores)
                            if user_score > best_score:
                                best_match = name
                                best_score = user_score
                    
                    # Single embedding format
                    elif 'embedding' in user_data:
                        stored_embedding = user_data['embedding']
                        if isinstance(stored_embedding, list) and len(stored_embedding) == 256:
                            similarity = cosine_similarity([embedding], [stored_embedding])[0][0]
                            if similarity > best_score:
                                best_match = name
                                best_score = similarity
                
                # Legacy format
                elif isinstance(user_data, list) and len(user_data) == 256:
                    similarity = cosine_similarity([embedding], [user_data])[0][0]
                    if similarity > best_score:
                        best_match = name
                        best_score = similarity
                        
            except Exception as e:
                if DEBUG:
                    print(f"[Recognition] ❌ Error processing user {name}: {e}")
                continue
        
        return best_match or "UNKNOWN", best_score
        
    except Exception as e:
        if DEBUG:
            print(f"[Recognition] ❌ Known users check error: {e}")
        return "UNKNOWN", 0.0

def check_anonymous_clusters_basic(audio):
    """🔍 Basic anonymous cluster checking"""
    try:
        from voice.database import anonymous_clusters
        
        embedding = generate_voice_embedding(audio)
        if embedding is None:
            return "UNKNOWN", 0.0
        
        best_cluster = None
        best_score = 0.0
        
        for cluster_id, cluster_data in anonymous_clusters.items():
            try:
                cluster_embeddings = cluster_data.get('embeddings', [])
                
                for stored_embedding in cluster_embeddings:
                    if isinstance(stored_embedding, dict) and 'resemblyzer' in stored_embedding:
                        stored_emb = stored_embedding['resemblyzer']
                    else:
                        stored_emb = stored_embedding
                    
                    if isinstance(stored_emb, list) and len(stored_emb) == 256:
                        similarity = cosine_similarity([embedding], [stored_emb])[0][0]
                        if similarity > best_score:
                            best_cluster = cluster_id
                            best_score = similarity
                            
            except Exception as e:
                if DEBUG:
                    print(f"[Recognition] ❌ Error processing cluster {cluster_id}: {e}")
                continue
        
        return best_cluster or "UNKNOWN", best_score
        
    except Exception as e:
        if DEBUG:
            print(f"[Recognition] ❌ Anonymous cluster check error: {e}")
        return "UNKNOWN", 0.0

def identify_speaker(audio):
    """🎯 Simple speaker identification (for backward compatibility)"""
    identified_user, confidence = identify_speaker_with_confidence(audio)
    if identified_user != "UNKNOWN" and confidence >= VOICE_CONFIDENCE_THRESHOLD:
        return identified_user
    return None

def register_voice(audio, username):
    """🎯 Register voice using enhanced clustering system with multi-cluster matching"""
    try:
        print(f"[Recognition] 🎯 Registering voice for: {username}")
        
        # ✅ ENHANCED SAME NAME COLLISION WITH SIMILARITY MATCHING
        from voice.database import handle_same_name_collision
        final_username = handle_same_name_collision(username)
        
        # ✅ CHECK ALL EXISTING CLUSTERS FOR THIS USERNAME
        existing_variants = [k for k in known_users.keys() if k.startswith(username)]
        
        if existing_variants:
            print(f"[Recognition] 🔍 Found existing variants: {existing_variants}")
            
            # Test similarity against all variants
            best_match = None
            best_similarity = 0.0
            
            embedding = generate_voice_embedding(audio)
            if embedding is not None:
                for variant in existing_variants:
                    variant_profile = known_users[variant]
                    if isinstance(variant_profile, dict) and 'embeddings' in variant_profile:
                        # Compare against all embeddings in this variant
                        for stored_embedding in variant_profile['embeddings']:
                            try:
                                if isinstance(stored_embedding, dict) and 'resemblyzer' in stored_embedding:
                                    stored_emb = stored_embedding['resemblyzer']
                                else:
                                    stored_emb = stored_embedding
                                
                                similarity = cosine_similarity([embedding], [stored_emb])[0][0]
                                if similarity > best_similarity:
                                    best_similarity = similarity
                                    best_match = variant
                            except:
                                continue
                
                # ✅ MERGE IF SIMILARITY > 0.5
                if best_match and best_similarity > 0.5:
                    print(f"[Recognition] 🔗 Merging into existing {best_match} (similarity: {best_similarity:.3f})")
                    
                    # Add to existing profile
                    profile = known_users[best_match]
                    profile['embeddings'].append(embedding.tolist())
                    profile['last_updated'] = datetime.utcnow().isoformat()
                    profile['merged_samples'] = profile.get('merged_samples', 0) + 1
                    
                    # Keep only best embeddings
                    if len(profile['embeddings']) > 15:
                        profile['embeddings'] = profile['embeddings'][-15:]
                    
                    save_known_users()
                    return True
        
        # ✅ CREATE NEW PROFILE if no similar match found
        if ENHANCED_AVAILABLE:
            success = enhanced_speaker_profiles.create_enhanced_profile(
                username=final_username,
                audio_samples=[audio],
                training_type='register_with_similarity_check'
            )
            
            if success:
                print(f"[Recognition] ✅ Enhanced profile created for: {final_username}")
                return True
            else:
                print(f"[Recognition] ❌ Enhanced profile creation failed for: {final_username}")
                return False
        else:
            # Basic registration fallback
            return basic_register_voice(audio, final_username)
            
    except Exception as e:
        print(f"[Recognition] ❌ Voice registration error: {e}")
        return False

def basic_register_voice(audio, username):
    """🔄 Basic voice registration fallback"""
    try:
        embedding = generate_voice_embedding(audio)
        if embedding is None:
            print(f"[Recognition] ❌ Failed to generate embedding for: {username}")
            return False
        
        from voice.database import known_users, save_known_users
        
        # Create basic profile
        profile_data = {
            'username': username,
            'embedding': embedding.tolist(),
            'created_at': datetime.utcnow().isoformat(),
            'confidence_threshold': VOICE_CONFIDENCE_THRESHOLD,
            'status': 'registered',
            'training_type': 'quick_register_basic',
            'registration_date': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        known_users[username] = profile_data
        save_known_users()
        
        print(f"[Recognition] ✅ Basic profile created for: {username}")
        return True
        
    except Exception as e:
        print(f"[Recognition] ❌ Basic registration error: {e}")
        return False

def update_voice_profile(username, new_audio):
    """🔄 Update existing voice profile with new audio"""
    try:
        if ENHANCED_AVAILABLE:
            # Use enhanced passive learning
            return enhanced_speaker_profiles.add_passive_sample(username, new_audio, 0.8)
        else:
            # Basic profile update
            return basic_update_voice_profile(username, new_audio)
            
    except Exception as e:
        print(f"[Recognition] ❌ Profile update error: {e}")
        return False

def basic_update_voice_profile(username, new_audio):
    """🔄 Basic voice profile update"""
    try:
        from voice.database import known_users, save_known_users
        
        if username not in known_users:
            return False
        
        new_embedding = generate_voice_embedding(new_audio)
        if new_embedding is None:
            return False
        
        profile = known_users[username]
        
        # If profile has multiple embeddings, add to list
        if 'embeddings' in profile:
            profile['embeddings'].append(new_embedding.tolist())
            # Keep only last 10 embeddings
            if len(profile['embeddings']) > 10:
                profile['embeddings'] = profile['embeddings'][-10:]
        else:
            # Convert single embedding to multiple
            old_embedding = profile.get('embedding', [])
            profile['embeddings'] = [old_embedding, new_embedding.tolist()]
            if 'embedding' in profile:
                del profile['embedding']
        
        profile['last_updated'] = datetime.utcnow().isoformat()
        profile['update_count'] = profile.get('update_count', 0) + 1
        
        save_known_users()
        print(f"[Recognition] ✅ Profile updated for: {username}")
        return True
        
    except Exception as e:
        print(f"[Recognition] ❌ Basic profile update error: {e}")
        return False

def get_voice_profile_info(username):
    """📊 Get voice profile information"""
    try:
        from voice.database import known_users
        
        if username not in known_users:
            return None
        
        profile = known_users[username]
        
        # Extract profile information
        info = {
            'username': username,
            'status': profile.get('status', 'unknown'),
            'created_at': profile.get('created_at', profile.get('created_date', 'unknown')),
            'last_updated': profile.get('last_updated', 'unknown'),
            'training_type': profile.get('training_type', 'unknown'),
            'confidence_threshold': profile.get('confidence_threshold', VOICE_CONFIDENCE_THRESHOLD),
            'recognition_count': profile.get('recognition_count', 0),
            'update_count': profile.get('update_count', 0)
        }
        
        # Count embeddings
        if 'embeddings' in profile:
            info['embedding_count'] = len(profile['embeddings'])
        elif 'embedding' in profile:
            info['embedding_count'] = 1
        else:
            info['embedding_count'] = 0
        
        return info
        
    except Exception as e:
        print(f"[Recognition] ❌ Profile info error: {e}")
        return None

def list_voice_profiles():
    """📋 List all voice profiles"""
    try:
        from voice.database import known_users, anonymous_clusters
        
        profiles = []
        
        # Known users
        for username, profile in known_users.items():
            info = get_voice_profile_info(username)
            if info:
                info['type'] = 'known_user'
                profiles.append(info)
        
        # Anonymous clusters
        for cluster_id, cluster_data in anonymous_clusters.items():
            info = {
                'username': cluster_id,
                'type': 'anonymous_cluster',
                'status': cluster_data.get('status', 'anonymous'),
                'created_at': cluster_data.get('created_at', 'unknown'),
                'last_updated': cluster_data.get('last_updated', 'unknown'),
                'sample_count': cluster_data.get('sample_count', 0),
                'embedding_count': len(cluster_data.get('embeddings', [])),
                'confidence_threshold': cluster_data.get('confidence_threshold', 0.6)
            }
            profiles.append(info)
        
        return profiles
        
    except Exception as e:
        print(f"[Recognition] ❌ Profile listing error: {e}")
        return []

def delete_voice_profile(username):
    """🗑️ Delete voice profile"""
    try:
        from voice.database import known_users, anonymous_clusters, save_known_users
        
        deleted = False
        
        # Check known users
        if username in known_users:
            del known_users[username]
            deleted = True
            print(f"[Recognition] 🗑️ Deleted known user: {username}")
        
        # Check anonymous clusters
        if username in anonymous_clusters:
            del anonymous_clusters[username]
            deleted = True
            print(f"[Recognition] 🗑️ Deleted anonymous cluster: {username}")
        
        if deleted:
            save_known_users()
            return True
        else:
            print(f"[Recognition] ❌ Profile not found: {username}")
            return False
            
    except Exception as e:
        print(f"[Recognition] ❌ Profile deletion error: {e}")
        return False

def cleanup_old_profiles(max_age_days=30):
    """🧹 Cleanup old voice profiles"""
    try:
        from voice.database import known_users, anonymous_clusters, save_known_users
        
        current_time = datetime.utcnow()
        cleaned_count = 0
        
        # Cleanup anonymous clusters
        clusters_to_remove = []
        for cluster_id, cluster_data in anonymous_clusters.items():
            try:
                created_at = datetime.fromisoformat(cluster_data.get('created_at', current_time.isoformat()))
                age_days = (current_time - created_at).days
                
                if age_days > max_age_days:
                    clusters_to_remove.append(cluster_id)
            except:
                # Remove clusters with invalid timestamps
                clusters_to_remove.append(cluster_id)
        
        for cluster_id in clusters_to_remove:
            del anonymous_clusters[cluster_id]
            cleaned_count += 1
            print(f"[Recognition] 🧹 Cleaned up old cluster: {cluster_id}")
        
        if cleaned_count > 0:
            save_known_users()
            print(f"[Recognition] ✅ Cleaned up {cleaned_count} old profiles")
        
        return cleaned_count
        
    except Exception as e:
        print(f"[Recognition] ❌ Cleanup error: {e}")
        return 0

def optimize_voice_database():
    """⚡ Optimize voice database performance"""
    try:
        from voice.database import known_users, anonymous_clusters, save_known_users
        
        optimized_count = 0
        
        # Optimize known users - remove duplicate embeddings
        for username, profile in known_users.items():
            if 'embeddings' in profile:
                embeddings = profile['embeddings']
                unique_embeddings = []
                
                for embedding in embeddings:
                    # Simple duplicate detection
                    is_duplicate = False
                    for existing in unique_embeddings:
                        if isinstance(embedding, list) and isinstance(existing, list):
                            if len(embedding) == len(existing):
                                similarity = cosine_similarity([embedding], [existing])[0][0]
                                if similarity > 0.98:  # Very similar embeddings
                                    is_duplicate = True
                                    break
                    
                    if not is_duplicate:
                        unique_embeddings.append(embedding)
                
                if len(unique_embeddings) != len(embeddings):
                    profile['embeddings'] = unique_embeddings
                    optimized_count += 1
                    print(f"[Recognition] ⚡ Optimized {username}: {len(embeddings)} → {len(unique_embeddings)} embeddings")
        
        if optimized_count > 0:
            save_known_users()
            print(f"[Recognition] ✅ Optimized {optimized_count} profiles")
        
        return optimized_count
        
    except Exception as e:
        print(f"[Recognition] ❌ Optimization error: {e}")
        return 0

# ✅ ADVANCED FEATURES

def analyze_voice_patterns():
    """📊 Analyze voice patterns across all profiles"""
    try:
        from voice.database import known_users, anonymous_clusters
        
        analysis = {
            'total_known_users': len(known_users),
            'total_anonymous_clusters': len(anonymous_clusters),
            'total_embeddings': 0,
            'average_embeddings_per_user': 0,
            'quality_distribution': {'high': 0, 'medium': 0, 'low': 0},
            'training_types': {},
            'recent_activity': {'last_24h': 0, 'last_week': 0, 'last_month': 0}
        }
        
        current_time = datetime.utcnow()
        
        # Analyze known users
        for username, profile in known_users.items():
            embedding_count = len(profile.get('embeddings', [profile.get('embedding', [])]))
            analysis['total_embeddings'] += embedding_count
            
            # Training type analysis
            training_type = profile.get('training_type', 'unknown')
            analysis['training_types'][training_type] = analysis['training_types'].get(training_type, 0) + 1
            
            # Recent activity
            try:
                last_updated = datetime.fromisoformat(profile.get('last_updated', profile.get('created_at', current_time.isoformat())))
                time_diff = (current_time - last_updated).total_seconds()
                
                if time_diff < 86400:  # 24 hours
                    analysis['recent_activity']['last_24h'] += 1
                elif time_diff < 604800:  # 1 week
                    analysis['recent_activity']['last_week'] += 1
                elif time_diff < 2592000:  # 30 days
                    analysis['recent_activity']['last_month'] += 1
            except:
                pass
        
        # Analyze anonymous clusters
        for cluster_id, cluster_data in anonymous_clusters.items():
            embedding_count = len(cluster_data.get('embeddings', []))
            analysis['total_embeddings'] += embedding_count
            
            # Quality analysis
            quality_scores = cluster_data.get('quality_scores', [])
            if quality_scores:
                avg_quality = sum(quality_scores) / len(quality_scores)
                if avg_quality > 0.7:
                    analysis['quality_distribution']['high'] += 1
                elif avg_quality > 0.5:
                    analysis['quality_distribution']['medium'] += 1
                else:
                    analysis['quality_distribution']['low'] += 1
        
        # Calculate averages
        total_profiles = analysis['total_known_users'] + analysis['total_anonymous_clusters']
        if total_profiles > 0:
            analysis['average_embeddings_per_user'] = analysis['total_embeddings'] / total_profiles
        
        return analysis
        
    except Exception as e:
        print(f"[Recognition] ❌ Pattern analysis error: {e}")
        return {}

def get_voice_recognition_stats():
    """📈 Get voice recognition statistics"""
    try:
        from voice.database import known_users, anonymous_clusters
        
        stats = {
            'recognition_attempts': 0,
            'recognition_successes': 0,
            'recognition_failures': 0,
            'average_confidence': 0.0,
            'top_recognized_users': [],
            'cluster_activity': {},
            'confidence_distribution': {'high': 0, 'medium': 0, 'low': 0}
        }
        
        total_confidence = 0.0
        confidence_count = 0
        user_recognition_counts = {}
        
        # Analyze known users
        for username, profile in known_users.items():
            recognition_count = profile.get('recognition_count', 0)
            recognition_successes = profile.get('recognition_successes', 0)
            recognition_failures = profile.get('recognition_failures', 0)
            
            stats['recognition_attempts'] += recognition_count
            stats['recognition_successes'] += recognition_successes
            stats['recognition_failures'] += recognition_failures
            
            if recognition_count > 0:
                user_recognition_counts[username] = recognition_count
            
            # Analyze recognition history for confidence
            recognition_history = profile.get('recognition_history', [])
            for entry in recognition_history:
                confidence = entry.get('confidence', 0.0)
                if confidence > 0:
                    total_confidence += confidence
                    confidence_count += 1
                    
                    if confidence > 0.8:
                        stats['confidence_distribution']['high'] += 1
                    elif confidence > 0.5:
                        stats['confidence_distribution']['medium'] += 1
                    else:
                        stats['confidence_distribution']['low'] += 1
        
        # Calculate average confidence
        if confidence_count > 0:
            stats['average_confidence'] = total_confidence / confidence_count
        
        # Top recognized users
        stats['top_recognized_users'] = sorted(
            user_recognition_counts.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:10]
        
        # Cluster activity
        for cluster_id, cluster_data in anonymous_clusters.items():
            sample_count = cluster_data.get('sample_count', 0)
            if sample_count > 0:
                stats['cluster_activity'][cluster_id] = sample_count
        
        return stats
        
    except Exception as e:
        print(f"[Recognition] ❌ Stats error: {e}")
        return {}

def merge_similar_clusters(similarity_threshold=0.85):
    """🔗 Merge similar anonymous clusters"""
    try:
        from voice.database import anonymous_clusters, save_known_users
        
        if not ENHANCED_AVAILABLE:
            print("[Recognition] ⚠️ Enhanced modules required for cluster merging")
            return 0
        
        cluster_ids = list(anonymous_clusters.keys())
        merged_count = 0
        clusters_to_remove = set()
        
        for i, cluster_id1 in enumerate(cluster_ids):
            if cluster_id1 in clusters_to_remove:
                continue
                
            cluster1_data = anonymous_clusters[cluster_id1]
            cluster1_embeddings = cluster1_data.get('embeddings', [])
            
            if not cluster1_embeddings:
                continue
            
            for j, cluster_id2 in enumerate(cluster_ids[i+1:], i+1):
                if cluster_id2 in clusters_to_remove:
                    continue
                    
                cluster2_data = anonymous_clusters[cluster_id2]
                cluster2_embeddings = cluster2_data.get('embeddings', [])
                
                if not cluster2_embeddings:
                    continue
                
                # Compare embeddings between clusters
                max_similarity = 0.0
                
                for emb1 in cluster1_embeddings:
                    for emb2 in cluster2_embeddings:
                        try:
                            similarity = dual_voice_model_manager.compare_dual_embeddings(emb1, emb2)
                            max_similarity = max(max_similarity, similarity)
                        except:
                            continue
                
                # Merge if similarity is high enough
                if max_similarity > similarity_threshold:
                    print(f"[Recognition] 🔗 Merging {cluster_id2} into {cluster_id1} (similarity: {max_similarity:.3f})")
                    
                    # Merge cluster2 into cluster1
                    cluster1_data['embeddings'].extend(cluster2_embeddings)
                    cluster1_data['sample_count'] += cluster2_data.get('sample_count', 0)
                    cluster1_data['quality_scores'].extend(cluster2_data.get('quality_scores', []))
                    cluster1_data['audio_contexts'].extend(cluster2_data.get('audio_contexts', []))
                    cluster1_data['last_updated'] = datetime.utcnow().isoformat()
                    
                    # Keep only best embeddings (max 10)
                    if len(cluster1_data['embeddings']) > 10:
                        # Sort by quality and keep best ones
                        quality_scores = cluster1_data.get('quality_scores', [])
                        if len(quality_scores) == len(cluster1_data['embeddings']):
                            combined = list(zip(cluster1_data['embeddings'], quality_scores))
                            combined.sort(key=lambda x: x[1], reverse=True)
                            cluster1_data['embeddings'] = [x[0] for x in combined[:10]]
                            cluster1_data['quality_scores'] = [x[1] for x in combined[:10]]
                        else:
                            cluster1_data['embeddings'] = cluster1_data['embeddings'][-10:]
                    
                    # Mark cluster2 for removal
                    clusters_to_remove.add(cluster_id2)
                    merged_count += 1
        
        # Remove merged clusters
        for cluster_id in clusters_to_remove:
            del anonymous_clusters[cluster_id]
        
        if merged_count > 0:
            save_known_users()
            print(f"[Recognition] ✅ Merged {merged_count} similar clusters")
        
        return merged_count
        
    except Exception as e:
        print(f"[Recognition] ❌ Cluster merging error: {e}")
        return 0

def adaptive_threshold_tuning():
    """🎯 Adaptive threshold tuning for all users"""
    try:
        if not ENHANCED_AVAILABLE:
            print("[Recognition] ⚠️ Enhanced modules required for adaptive tuning")
            return 0
        
        from voice.database import known_users
        
        tuned_count = 0
        
        for username in known_users.keys():
            try:
                old_threshold = known_users[username].get('confidence_threshold', VOICE_CONFIDENCE_THRESHOLD)
                new_threshold = enhanced_speaker_profiles.tune_threshold_for_user(username)
                
                if abs(new_threshold - old_threshold) > 0.05:  # Significant change
                    print(f"[Recognition] 🎯 Tuned threshold for {username}: {old_threshold:.3f} → {new_threshold:.3f}")
                    tuned_count += 1
            except Exception as e:
                print(f"[Recognition] ❌ Threshold tuning error for {username}: {e}")
                continue
        
        print(f"[Recognition] ✅ Tuned thresholds for {tuned_count} users")
        return tuned_count
        
    except Exception as e:
        print(f"[Recognition] ❌ Adaptive tuning error: {e}")
        return 0

def export_voice_data(export_path="voice_export.json"):
    """📤 Export voice data for backup or analysis"""
    try:
        from voice.database import known_users, anonymous_clusters
        
        export_data = {
            'export_timestamp': datetime.utcnow().isoformat(),
            'export_version': '2.0_advanced',
            'known_users': {},
            'anonymous_clusters': {},
            'statistics': get_voice_recognition_stats(),
            'patterns': analyze_voice_patterns()
        }
        
        # Export known users (excluding raw embeddings for privacy)
        for username, profile in known_users.items():
            export_data['known_users'][username] = {
                'username': profile.get('username', username),
                'status': profile.get('status', 'unknown'),
                'created_at': profile.get('created_at', 'unknown'),
                'last_updated': profile.get('last_updated', 'unknown'),
                'training_type': profile.get('training_type', 'unknown'),
                'confidence_threshold': profile.get('confidence_threshold', VOICE_CONFIDENCE_THRESHOLD),
                'recognition_count': profile.get('recognition_count', 0),
                'recognition_successes': profile.get('recognition_successes', 0),
                'recognition_failures': profile.get('recognition_failures', 0),
                'embedding_count': len(profile.get('embeddings', [profile.get('embedding', [])])),
                'quality_scores': profile.get('quality_scores', []),
                'previous_names': profile.get('previous_names', [])
            }
        
        # Export anonymous clusters (metadata only)
        for cluster_id, cluster_data in anonymous_clusters.items():
            export_data['anonymous_clusters'][cluster_id] = {
                'cluster_id': cluster_id,
                'status': cluster_data.get('status', 'anonymous'),
                'created_at': cluster_data.get('created_at', 'unknown'),
                'last_updated': cluster_data.get('last_updated', 'unknown'),
                'sample_count': cluster_data.get('sample_count', 0),
                'embedding_count': len(cluster_data.get('embeddings', [])),
                'confidence_threshold': cluster_data.get('confidence_threshold', 0.6),
                'quality_scores': cluster_data.get('quality_scores', []),
                'audio_contexts': cluster_data.get('audio_contexts', [])
            }
        
        # Write export file
        with open(export_path, 'w') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        print(f"[Recognition] 📤 Voice data exported to: {export_path}")
        return True
        
    except Exception as e:
        print(f"[Recognition] ❌ Export error: {e}")
        return False

def import_voice_data(import_path="voice_export.json"):
    """📥 Import voice data from backup"""
    try:
        from voice.database import save_known_users
        
        with open(import_path, 'r') as f:
            import_data = json.load(f)
        
        print(f"[Recognition] 📥 Import would restore {len(import_data.get('known_users', {}))} users and {len(import_data.get('anonymous_clusters', {}))} clusters")
        print(f"[Recognition] ⚠️ Full embedding import not implemented for security")
        
        return True
        
    except Exception as e:
        print(f"[Recognition] ❌ Import error: {e}")
        return False

def diagnose_recognition_issues():
    """🔧 Diagnose common recognition issues"""
    try:
        from voice.database import known_users, anonymous_clusters
        
        issues = []
        recommendations = []
        
        # Check for users with low recognition success rates
        for username, profile in known_users.items():
            recognition_count = profile.get('recognition_count', 0)
            recognition_successes = profile.get('recognition_successes', 0)
            
            if recognition_count > 10:  # Only check users with significant attempts
                success_rate = recognition_successes / recognition_count
                if success_rate < 0.7:  # Less than 70% success rate
                    issues.append(f"Low recognition success rate for {username}: {success_rate:.1%}")
                    recommendations.append(f"Consider retraining {username} or adjusting threshold")
        
        # Check for too many anonymous clusters
        if len(anonymous_clusters) > 10:
            issues.append(f"High number of anonymous clusters: {len(anonymous_clusters)}")
            recommendations.append("Consider merging similar clusters or cleaning up old ones")
        
        # Check for users with very high/low thresholds
        for username, profile in known_users.items():
            threshold = profile.get('confidence_threshold', VOICE_CONFIDENCE_THRESHOLD)
            if threshold > 0.9:
                issues.append(f"Very high threshold for {username}: {threshold:.3f}")
                recommendations.append(f"Consider lowering threshold for {username} or adding more training data")
            elif threshold < 0.3:
                issues.append(f"Very low threshold for {username}: {threshold:.3f}")
                recommendations.append(f"Consider raising threshold for {username} to reduce false positives")
        
        # Check for users with insufficient embeddings
        for username, profile in known_users.items():
            embedding_count = len(profile.get('embeddings', [profile.get('embedding', [])]))
            if embedding_count < 3:
                issues.append(f"Insufficient embeddings for {username}: {embedding_count}")
                recommendations.append(f"Add more training samples for {username}")
        
        diagnosis = {
            'issues_found': len(issues),
            'issues': issues,
            'recommendations': recommendations,
            'overall_health': 'good' if len(issues) == 0 else 'fair' if len(issues) < 5 else 'poor'
        }
        
        return diagnosis
        
    except Exception as e:
        print(f"[Recognition] ❌ Diagnosis error: {e}")
        return {'issues_found': 0, 'issues': [], 'recommendations': [], 'overall_health': 'unknown'}

# ✅ MAINTENANCE FUNCTIONS

def run_maintenance():
    """🔧 Run comprehensive voice system maintenance"""
    try:
        print("[Recognition] 🔧 Starting voice system maintenance...")
        
        results = {
            'cleanup_count': 0,
            'optimization_count': 0,
            'merged_clusters': 0,
            'tuned_thresholds': 0,
            'diagnosis': {}
        }
        
        # 1. Cleanup old profiles
        results['cleanup_count'] = cleanup_old_profiles(max_age_days=30)
        
        # 2. Optimize database
        results['optimization_count'] = optimize_voice_database()
        
        # 3. Merge similar clusters
        results['merged_clusters'] = merge_similar_clusters(similarity_threshold=0.85)
        
        # 4. Adaptive threshold tuning
        results['tuned_thresholds'] = adaptive_threshold_tuning()
        
        # 5. Diagnose issues
        results['diagnosis'] = diagnose_recognition_issues()
        
        print(f"[Recognition] ✅ Maintenance complete:")
        print(f"  - Cleaned up: {results['cleanup_count']} profiles")
        print(f"  - Optimized: {results['optimization_count']} profiles")
        print(f"  - Merged: {results['merged_clusters']} clusters")
        print(f"  - Tuned: {results['tuned_thresholds']} thresholds")
        print(f"  - Health: {results['diagnosis']['overall_health']}")
        
        return results
        
    except Exception as e:
        print(f"[Recognition] ❌ Maintenance error: {e}")
        return {}

# Initialize enhanced recognition system
if ENHANCED_AVAILABLE:
    print("[Recognition] 🚀 Advanced recognition system initialized")
    # Run initial maintenance on startup
    # run_maintenance()  # Uncomment to run maintenance on startup
else:
    print("[Recognition] 🔄 Basic recognition system initialized")