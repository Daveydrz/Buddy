"""
User Profile Manager - Memory leak prevention and cleanup
Created: 2025-08-05
Purpose: Manage user profile lifecycle to prevent accumulation and memory leaks
"""

import json
import os
import time
import threading
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict

class UserProfileManager:
    """Manages user profile lifecycle and prevents memory accumulation"""
    
    def __init__(self, max_users: int = 10, cleanup_interval: int = 3600):
        self.max_users = max_users
        self.cleanup_interval = cleanup_interval  # seconds
        self.last_cleanup = time.time()
        self.user_activity: Dict[str, float] = {}  # Track last activity per user
        self.user_metadata: Dict[str, Dict] = {}   # Track user metadata
        self.lock = threading.Lock()
        
        # Configuration
        self.inactive_threshold = 24 * 3600  # 24 hours
        self.emergency_cleanup_threshold = 50  # Force cleanup if > 50 users
        
        print("[UserProfileManager] ✅ User profile management initialized")
    
    def register_user_activity(self, user_id: str, activity_type: str = "interaction"):
        """Register user activity to track active users"""
        with self.lock:
            current_time = time.time()
            self.user_activity[user_id] = current_time
            
            if user_id not in self.user_metadata:
                self.user_metadata[user_id] = {
                    'first_seen': current_time,
                    'interaction_count': 0,
                    'last_activity_type': activity_type
                }
            
            self.user_metadata[user_id]['interaction_count'] += 1
            self.user_metadata[user_id]['last_activity_type'] = activity_type
            
            # Check if cleanup is needed
            if self._should_run_cleanup():
                self._run_cleanup()
    
    def _should_run_cleanup(self) -> bool:
        """Determine if cleanup should be run"""
        current_time = time.time()
        
        # Regular interval cleanup
        if current_time - self.last_cleanup > self.cleanup_interval:
            return True
        
        # Emergency cleanup if too many users
        if len(self.user_activity) > self.emergency_cleanup_threshold:
            print(f"[UserProfileManager] ⚠️ Emergency cleanup triggered - {len(self.user_activity)} users")
            return True
        
        return False
    
    def _run_cleanup(self):
        """Run user profile cleanup"""
        current_time = time.time()
        
        # Find inactive users
        inactive_users = []
        for user_id, last_activity in self.user_activity.items():
            if current_time - last_activity > self.inactive_threshold:
                inactive_users.append(user_id)
        
        # If we have too many users, remove the oldest ones
        if len(self.user_activity) > self.max_users:
            # Sort by last activity time and remove oldest
            sorted_users = sorted(self.user_activity.items(), key=lambda x: x[1])
            users_to_remove = len(sorted_users) - self.max_users
            
            for i in range(users_to_remove):
                user_id = sorted_users[i][0]
                if user_id not in inactive_users:
                    inactive_users.append(user_id)
        
        # Clean up inactive users
        if inactive_users:
            self._cleanup_users(inactive_users)
        
        self.last_cleanup = current_time
        print(f"[UserProfileManager] ✅ Cleanup completed - {len(inactive_users)} users cleaned")
    
    def _cleanup_users(self, user_ids: List[str]):
        """Clean up specific users from all systems"""
        for user_id in user_ids:
            try:
                self._cleanup_user_from_voice_system(user_id)
                self._cleanup_user_from_memory_system(user_id)
                self._cleanup_user_from_consciousness_system(user_id)
                
                # Remove from tracking
                self.user_activity.pop(user_id, None)
                self.user_metadata.pop(user_id, None)
                
                print(f"[UserProfileManager] 🧹 Cleaned up user: {user_id}")
                
            except Exception as e:
                print(f"[UserProfileManager] ❌ Error cleaning user {user_id}: {e}")
    
    def _cleanup_user_from_voice_system(self, user_id: str):
        """Clean user from voice recognition system"""
        try:
            from voice.database import known_users, anonymous_clusters, save_known_users
            
            # Remove from known users
            if user_id in known_users:
                del known_users[user_id]
                print(f"[UserProfileManager] 🎤 Removed {user_id} from voice system")
            
            # Clean from anonymous clusters (remove low-confidence clusters)
            clusters_to_remove = []
            for cluster_id, cluster_data in anonymous_clusters.items():
                if user_id in cluster_data.get('associated_users', []):
                    clusters_to_remove.append(cluster_id)
            
            for cluster_id in clusters_to_remove:
                del anonymous_clusters[cluster_id]
                print(f"[UserProfileManager] 🎤 Removed cluster {cluster_id} for {user_id}")
            
            # Save changes
            save_known_users()
            
        except ImportError:
            print("[UserProfileManager] ⚠️ Voice system not available for cleanup")
        except Exception as e:
            print(f"[UserProfileManager] ❌ Voice cleanup error: {e}")
    
    def _cleanup_user_from_memory_system(self, user_id: str):
        """Clean user from memory system"""
        try:
            # Clear conversation history files
            memory_files = [
                f"conversation_history_{user_id}.json",
                f"user_memory_{user_id}.json",
                f"working_memory_{user_id}.json"
            ]
            
            for filename in memory_files:
                if os.path.exists(filename):
                    os.remove(filename)
                    print(f"[UserProfileManager] 💾 Removed memory file: {filename}")
            
        except Exception as e:
            print(f"[UserProfileManager] ❌ Memory cleanup error: {e}")
    
    def _cleanup_user_from_consciousness_system(self, user_id: str):
        """Clean user from consciousness modules"""
        try:
            # Clean user-specific goal files
            goal_files = [
                f"goals/{user_id}_goals.json",
                f"beliefs/{user_id}_beliefs.json"
            ]
            
            for filename in goal_files:
                if os.path.exists(filename):
                    os.remove(filename)
                    print(f"[UserProfileManager] 🧠 Removed consciousness file: {filename}")
            
        except Exception as e:
            print(f"[UserProfileManager] ❌ Consciousness cleanup error: {e}")
    
    def force_cleanup(self):
        """Force immediate cleanup"""
        with self.lock:
            print("[UserProfileManager] 🧹 Force cleanup initiated")
            self._run_cleanup()
    
    def get_user_stats(self) -> Dict[str, Any]:
        """Get user management statistics"""
        with self.lock:
            current_time = time.time()
            
            active_users = []
            inactive_users = []
            
            for user_id, last_activity in self.user_activity.items():
                if current_time - last_activity > self.inactive_threshold:
                    inactive_users.append(user_id)
                else:
                    active_users.append(user_id)
            
            return {
                'total_users': len(self.user_activity),
                'active_users': len(active_users),
                'inactive_users': len(inactive_users),
                'max_users': self.max_users,
                'last_cleanup': self.last_cleanup,
                'time_since_cleanup': current_time - self.last_cleanup,
                'cleanup_threshold': self.cleanup_interval,
                'memory_usage_status': 'healthy' if len(self.user_activity) <= self.max_users else 'elevated'
            }
    
    def get_user_info(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific user"""
        with self.lock:
            if user_id not in self.user_activity:
                return None
            
            current_time = time.time()
            last_activity = self.user_activity[user_id]
            metadata = self.user_metadata.get(user_id, {})
            
            return {
                'user_id': user_id,
                'last_activity': last_activity,
                'time_since_activity': current_time - last_activity,
                'is_active': (current_time - last_activity) <= self.inactive_threshold,
                'metadata': metadata
            }

# Global user profile manager
user_profile_manager = UserProfileManager()

def register_user_activity(user_id: str, activity_type: str = "interaction"):
    """Convenience function to register user activity"""
    user_profile_manager.register_user_activity(user_id, activity_type)

def cleanup_inactive_users():
    """Convenience function to force cleanup"""
    user_profile_manager.force_cleanup()

print("[UserProfileManager] ✅ User profile management system ready")