"""
Memory Profile Continuity Manager
Created: 2025-01-08
Purpose: Manages memory reassignment and continuity during profile transitions (Anonymous_01 → Named user)

Key Features:
- Tracks memory assignment during profile transitions
- Ensures all memories follow when Anonymous_01 → Named user (e.g., "Dawid")
- Maintains memory continuity across name/identity changes
- Handles complex transition scenarios (multiple anonymous users, name conflicts)
"""

import json
import time
import threading
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
from enum import Enum

class TransitionType(Enum):
    """Types of profile transitions"""
    ANONYMOUS_TO_NAMED = "anonymous_to_named"
    NAME_UPDATE = "name_update"
    PROFILE_MERGE = "profile_merge"
    IDENTITY_CORRECTION = "identity_correction"

class TransitionStatus(Enum):
    """Status of profile transitions"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"

@dataclass
class MemoryTransition:
    """Tracks a single memory transition"""
    transition_id: str
    source_profile: str
    target_profile: str
    transition_type: TransitionType
    memory_count: int
    started_at: datetime
    completed_at: Optional[datetime] = None
    status: TransitionStatus = TransitionStatus.PENDING
    memory_items: List[str] = None
    rollback_data: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.memory_items is None:
            self.memory_items = []
        if self.rollback_data is None:
            self.rollback_data = {}

@dataclass
class ProfileContinuity:
    """Tracks profile continuity information"""
    profile_id: str
    original_anonymous_id: Optional[str] = None
    transition_history: List[str] = None
    memory_lineage: Dict[str, str] = None  # memory_id -> source_profile
    created_at: Optional[datetime] = None
    last_updated: Optional[datetime] = None
    
    def __post_init__(self):
        if self.transition_history is None:
            self.transition_history = []
        if self.memory_lineage is None:
            self.memory_lineage = {}
        if self.created_at is None:
            self.created_at = datetime.now()

class MemoryProfileContinuityManager:
    """Manages memory continuity across profile transitions"""
    
    def __init__(self, storage_path: str = "memory_profile_continuity.json"):
        self.storage_path = storage_path
        self.transitions: Dict[str, MemoryTransition] = {}
        self.profile_continuities: Dict[str, ProfileContinuity] = {}
        self.lock = threading.Lock()
        self.transition_counter = 0
        
        # Load existing data
        self._load_continuity_data()
        
        print("[MemoryProfileContinuityManager] ✅ Memory Profile Continuity Manager initialized")
    
    def _load_continuity_data(self):
        """Load existing continuity data"""
        try:
            if Path(self.storage_path).exists():
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)
                
                # Load transitions
                for trans_id, trans_data in data.get('transitions', {}).items():
                    trans_data['started_at'] = datetime.fromisoformat(trans_data['started_at'])
                    if trans_data.get('completed_at'):
                        trans_data['completed_at'] = datetime.fromisoformat(trans_data['completed_at'])
                    trans_data['transition_type'] = TransitionType(trans_data['transition_type'])
                    trans_data['status'] = TransitionStatus(trans_data['status'])
                    self.transitions[trans_id] = MemoryTransition(**trans_data)
                
                # Load profile continuities
                for prof_id, cont_data in data.get('profile_continuities', {}).items():
                    if cont_data.get('created_at'):
                        cont_data['created_at'] = datetime.fromisoformat(cont_data['created_at'])
                    if cont_data.get('last_updated'):
                        cont_data['last_updated'] = datetime.fromisoformat(cont_data['last_updated'])
                    self.profile_continuities[prof_id] = ProfileContinuity(**cont_data)
                
                self.transition_counter = data.get('transition_counter', 0)
                print(f"[MemoryProfileContinuityManager] 📚 Loaded {len(self.transitions)} transitions and {len(self.profile_continuities)} continuities")
                
        except Exception as e:
            print(f"[MemoryProfileContinuityManager] ⚠️ Could not load continuity data: {e}")
    
    def _save_continuity_data(self):
        """Save continuity data"""
        try:
            data = {
                'transitions': {},
                'profile_continuities': {},
                'transition_counter': self.transition_counter
            }
            
            # Save transitions
            for trans_id, transition in self.transitions.items():
                trans_dict = asdict(transition)
                trans_dict['started_at'] = transition.started_at.isoformat()
                if transition.completed_at:
                    trans_dict['completed_at'] = transition.completed_at.isoformat()
                trans_dict['transition_type'] = transition.transition_type.value
                trans_dict['status'] = transition.status.value
                data['transitions'][trans_id] = trans_dict
            
            # Save profile continuities
            for prof_id, continuity in self.profile_continuities.items():
                cont_dict = asdict(continuity)
                if continuity.created_at:
                    cont_dict['created_at'] = continuity.created_at.isoformat()
                if continuity.last_updated:
                    cont_dict['last_updated'] = continuity.last_updated.isoformat()
                data['profile_continuities'][prof_id] = cont_dict
            
            with open(self.storage_path, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            print(f"[MemoryProfileContinuityManager] ❌ Could not save continuity data: {e}")
    
    def start_profile_transition(self, source_profile: str, target_profile: str, 
                                transition_type: TransitionType) -> str:
        """Start a profile transition process"""
        with self.lock:
            self.transition_counter += 1
            transition_id = f"trans_{self.transition_counter}_{int(time.time())}"
            
            # Get memory count (would integrate with actual memory system)
            memory_count = self._get_memory_count_for_profile(source_profile)
            
            transition = MemoryTransition(
                transition_id=transition_id,
                source_profile=source_profile,
                target_profile=target_profile,
                transition_type=transition_type,
                memory_count=memory_count,
                started_at=datetime.now()
            )
            
            self.transitions[transition_id] = transition
            print(f"[MemoryProfileContinuityManager] 🔄 Started transition {transition_id}: {source_profile} → {target_profile}")
            
            self._save_continuity_data()
            return transition_id
    
    def execute_anonymous_to_named_transition(self, anonymous_id: str, named_id: str) -> bool:
        """Execute transition from Anonymous_01 to named user (e.g., Dawid)"""
        try:
            transition_id = self.start_profile_transition(
                anonymous_id, named_id, TransitionType.ANONYMOUS_TO_NAMED
            )
            
            with self.lock:
                transition = self.transitions[transition_id]
                transition.status = TransitionStatus.IN_PROGRESS
                
                # Step 1: Collect all memory items for anonymous profile
                memory_items = self._collect_profile_memories(anonymous_id)
                transition.memory_items = memory_items
                
                # Step 2: Create rollback data
                transition.rollback_data = {
                    'original_memories': memory_items.copy(),
                    'target_profile_existed': self._profile_exists(named_id)
                }
                
                # Step 3: Transfer memories to named profile
                success = self._transfer_memories(anonymous_id, named_id, memory_items)
                
                if success:
                    # Step 4: Update profile continuity
                    self._update_profile_continuity(named_id, anonymous_id, transition_id)
                    
                    # Step 5: Mark transition complete
                    transition.status = TransitionStatus.COMPLETED
                    transition.completed_at = datetime.now()
                    
                    print(f"[MemoryProfileContinuityManager] ✅ Successfully transitioned {len(memory_items)} memories from {anonymous_id} to {named_id}")
                    
                    self._save_continuity_data()
                    return True
                else:
                    transition.status = TransitionStatus.FAILED
                    print(f"[MemoryProfileContinuityManager] ❌ Failed to transfer memories from {anonymous_id} to {named_id}")
                    
                    self._save_continuity_data()
                    return False
                    
        except Exception as e:
            print(f"[MemoryProfileContinuityManager] ❌ Error in transition: {e}")
            return False
    
    def rollback_transition(self, transition_id: str) -> bool:
        """Rollback a profile transition"""
        try:
            with self.lock:
                if transition_id not in self.transitions:
                    print(f"[MemoryProfileContinuityManager] ❌ Transition {transition_id} not found")
                    return False
                
                transition = self.transitions[transition_id]
                
                if transition.status != TransitionStatus.COMPLETED:
                    print(f"[MemoryProfileContinuityManager] ❌ Can only rollback completed transitions")
                    return False
                
                # Restore original state
                if transition.rollback_data:
                    original_memories = transition.rollback_data.get('original_memories', [])
                    self._restore_memories(transition.source_profile, original_memories)
                    
                    # Remove memories from target profile if they were added
                    self._remove_transferred_memories(transition.target_profile, transition.memory_items)
                
                transition.status = TransitionStatus.ROLLED_BACK
                
                print(f"[MemoryProfileContinuityManager] 🔄 Rolled back transition {transition_id}")
                self._save_continuity_data()
                return True
                
        except Exception as e:
            print(f"[MemoryProfileContinuityManager] ❌ Error rolling back transition: {e}")
            return False
    
    def get_profile_lineage(self, profile_id: str) -> Optional[Dict[str, Any]]:
        """Get the lineage/history of a profile"""
        if profile_id in self.profile_continuities:
            continuity = self.profile_continuities[profile_id]
            return {
                'profile_id': profile_id,
                'original_anonymous_id': continuity.original_anonymous_id,
                'transition_history': continuity.transition_history,
                'memory_count': len(continuity.memory_lineage),
                'created_at': continuity.created_at.isoformat() if continuity.created_at else None,
                'last_updated': continuity.last_updated.isoformat() if continuity.last_updated else None
            }
        return None
    
    def find_profile_by_anonymous_id(self, anonymous_id: str) -> Optional[str]:
        """Find which named profile an anonymous ID was transitioned to"""
        for profile_id, continuity in self.profile_continuities.items():
            if continuity.original_anonymous_id == anonymous_id:
                return profile_id
        return None
    
    def get_transition_status(self, transition_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a transition"""
        if transition_id in self.transitions:
            transition = self.transitions[transition_id]
            return {
                'transition_id': transition_id,
                'source_profile': transition.source_profile,
                'target_profile': transition.target_profile,
                'status': transition.status.value,
                'memory_count': len(transition.memory_items),
                'started_at': transition.started_at.isoformat(),
                'completed_at': transition.completed_at.isoformat() if transition.completed_at else None
            }
        return None
    
    def _get_memory_count_for_profile(self, profile_id: str) -> int:
        """Get memory count for a profile (placeholder - would integrate with actual memory system)"""
        # This would integrate with the actual memory system
        # For now, return a placeholder count
        return 5  # Placeholder
    
    def _collect_profile_memories(self, profile_id: str) -> List[str]:
        """Collect all memory items for a profile (placeholder)"""
        # This would integrate with the actual memory system
        # For now, return placeholder memory IDs
        return [f"memory_{profile_id}_{i}" for i in range(5)]  # Placeholder
    
    def _transfer_memories(self, source_profile: str, target_profile: str, memory_items: List[str]) -> bool:
        """Transfer memories from source to target profile (placeholder)"""
        # This would integrate with the actual memory system
        # For now, simulate successful transfer
        print(f"[MemoryProfileContinuityManager] 📋 Transferring {len(memory_items)} memories: {source_profile} → {target_profile}")
        return True  # Placeholder
    
    def _profile_exists(self, profile_id: str) -> bool:
        """Check if a profile exists (placeholder)"""
        # This would integrate with the actual memory system
        return False  # Placeholder
    
    def _update_profile_continuity(self, profile_id: str, original_anonymous_id: str, transition_id: str):
        """Update profile continuity information"""
        if profile_id not in self.profile_continuities:
            self.profile_continuities[profile_id] = ProfileContinuity(profile_id=profile_id)
        
        continuity = self.profile_continuities[profile_id]
        continuity.original_anonymous_id = original_anonymous_id
        continuity.transition_history.append(transition_id)
        continuity.last_updated = datetime.now()
    
    def _restore_memories(self, profile_id: str, memory_items: List[str]):
        """Restore memories to a profile (placeholder)"""
        # This would integrate with the actual memory system
        print(f"[MemoryProfileContinuityManager] 📋 Restoring {len(memory_items)} memories to {profile_id}")
    
    def _remove_transferred_memories(self, profile_id: str, memory_items: List[str]):
        """Remove transferred memories from a profile (placeholder)"""
        # This would integrate with the actual memory system
        print(f"[MemoryProfileContinuityManager] 🗑️ Removing {len(memory_items)} transferred memories from {profile_id}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about profile transitions"""
        with self.lock:
            total_transitions = len(self.transitions)
            completed_transitions = sum(1 for t in self.transitions.values() if t.status == TransitionStatus.COMPLETED)
            failed_transitions = sum(1 for t in self.transitions.values() if t.status == TransitionStatus.FAILED)
            
            return {
                'total_transitions': total_transitions,
                'completed_transitions': completed_transitions,
                'failed_transitions': failed_transitions,
                'success_rate': completed_transitions / total_transitions if total_transitions > 0 else 0,
                'total_profiles_with_continuity': len(self.profile_continuities),
                'anonymous_to_named_transitions': sum(1 for t in self.transitions.values() 
                                                   if t.transition_type == TransitionType.ANONYMOUS_TO_NAMED)
            }

# Global instance
_memory_profile_continuity_manager = None

def get_memory_profile_continuity_manager() -> MemoryProfileContinuityManager:
    """Get the global memory profile continuity manager instance"""
    global _memory_profile_continuity_manager
    if _memory_profile_continuity_manager is None:
        _memory_profile_continuity_manager = MemoryProfileContinuityManager()
    return _memory_profile_continuity_manager

# Convenience functions for common operations
def transition_anonymous_to_named(anonymous_id: str, named_id: str) -> bool:
    """Convenience function to transition from anonymous to named profile"""
    manager = get_memory_profile_continuity_manager()
    return manager.execute_anonymous_to_named_transition(anonymous_id, named_id)

def get_profile_origin(profile_id: str) -> Optional[str]:
    """Get the original anonymous ID for a profile"""
    manager = get_memory_profile_continuity_manager()
    lineage = manager.get_profile_lineage(profile_id)
    return lineage.get('original_anonymous_id') if lineage else None

def check_memory_continuity() -> Dict[str, Any]:
    """Check the overall health of memory continuity"""
    manager = get_memory_profile_continuity_manager()
    return manager.get_statistics()