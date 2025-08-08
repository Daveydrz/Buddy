"""
Memory Prioritization & Compression - Intelligent Context Management

This module implements smart memory management for cognitive context:
- Intelligent selection of beliefs, goals, and experiences for LLM calls
- Context overflow prevention with essential memory preservation
- Smart truncation maintaining personality and memory continuity
- Token-aware memory compression and prioritization
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import json

# Import cognitive modules
try:
    from .self_model import persistent_self_model
    from .goal_bank import goal_bank
    from .experience_bank import experience_bank
    COGNITIVE_MODULES_AVAILABLE = True
except ImportError:
    COGNITIVE_MODULES_AVAILABLE = False
    logging.warning("Cognitive modules not available for memory prioritization")

@dataclass
class MemoryPriorityConfig:
    """Configuration for memory prioritization"""
    max_total_tokens: int = 1000  # Maximum tokens for cognitive context
    self_model_weight: float = 0.3  # 30% of tokens for self-model
    goals_weight: float = 0.25     # 25% for goals
    experiences_weight: float = 0.35  # 35% for experiences
    metadata_weight: float = 0.1   # 10% for metadata
    
    # Minimum allocations (emergency fallback)
    min_self_tokens: int = 100
    min_goals_tokens: int = 80
    min_experiences_tokens: int = 120

class MemoryPrioritizer:
    """
    Intelligent memory prioritization system for cognitive context management.
    
    Features:
    - Token-aware content selection
    - Priority-based memory compression
    - Essential personality preservation
    - Context overflow prevention
    - Adaptive memory allocation
    """
    
    def __init__(self, config: MemoryPriorityConfig = None):
        self.config = config or MemoryPriorityConfig()
        
        # Estimation constants (rough token estimates)
        self.tokens_per_char = 0.25  # Rough estimate for English text
        self.tokens_per_word = 1.3   # Average tokens per word
        
        # Priority thresholds
        self.high_priority_threshold = 0.8
        self.medium_priority_threshold = 0.5
        self.low_priority_threshold = 0.2
        
        logging.info("[MemoryPrioritizer] Initialized with token budget: {}".format(
            self.config.max_total_tokens))
    
    def estimate_tokens(self, text: str) -> int:
        """Estimate token count for text"""
        if not text:
            return 0
        
        # Simple estimation based on character count and word count
        char_estimate = len(text) * self.tokens_per_char
        word_estimate = len(text.split()) * self.tokens_per_word
        
        # Use the average as our estimate
        return int((char_estimate + word_estimate) / 2)
    
    def estimate_json_tokens(self, data: Any) -> int:
        """Estimate tokens for JSON data"""
        json_str = json.dumps(data, separators=(',', ':'))
        return self.estimate_tokens(json_str)
    
    def prioritize_cognitive_context(self, user: str = None, 
                                   current_context: str = "",
                                   context_priority: str = "balanced") -> Dict[str, Any]:
        """
        Create prioritized cognitive context for LLM injection.
        
        Args:
            user: Current user for personalized context
            current_context: Current conversation context
            context_priority: "personality", "goals", "experiences", or "balanced"
        
        Returns:
            Optimized cognitive context dictionary
        """
        if not COGNITIVE_MODULES_AVAILABLE:
            return {"error": "Cognitive modules not available"}
        
        # Analyze current context for relevance hints
        context_keywords = self._extract_context_keywords(current_context)
        
        # Get raw cognitive data
        self_data = persistent_self_model.get_cognitive_injection_data()
        goals_data = goal_bank.get_cognitive_injection_data()
        experiences_data = experience_bank.get_cognitive_injection_data(user)
        
        # Calculate token allocations based on priority
        allocations = self._calculate_token_allocations(context_priority)
        
        # Prioritize and compress each component
        optimized_self = self._prioritize_self_model_data(
            self_data, allocations['self_model'], context_keywords)
        
        optimized_goals = self._prioritize_goals_data(
            goals_data, allocations['goals'], context_keywords)
        
        optimized_experiences = self._prioritize_experiences_data(
            experiences_data, allocations['experiences'], context_keywords, user)
        
        # Create metadata with remaining tokens
        metadata = self._create_metadata(allocations['metadata'])
        
        # Combine into final context
        cognitive_context = {
            "self_model": optimized_self,
            "goals": optimized_goals,
            "experiences": optimized_experiences,
            "meta": metadata,
            "context_priority": context_priority,
            "token_usage": {
                "estimated_total": (
                    self.estimate_json_tokens(optimized_self) +
                    self.estimate_json_tokens(optimized_goals) +
                    self.estimate_json_tokens(optimized_experiences) +
                    self.estimate_json_tokens(metadata)
                ),
                "budget": self.config.max_total_tokens
            }
        }
        
        # Final validation and emergency compression if needed
        actual_tokens = self.estimate_json_tokens(cognitive_context)
        if actual_tokens > self.config.max_total_tokens * 1.1:  # 10% tolerance
            cognitive_context = self._emergency_compress(cognitive_context)
        
        logging.debug(f"[MemoryPrioritizer] Generated cognitive context: {actual_tokens} tokens")
        return cognitive_context
    
    def _extract_context_keywords(self, context: str) -> List[str]:
        """Extract keywords from current context for relevance matching"""
        if not context:
            return []
        
        words = context.lower().split()
        
        # Filter meaningful keywords
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        keywords = [word for word in words if len(word) > 3 and word not in stop_words]
        
        return keywords[:10]  # Limit to most relevant
    
    def _calculate_token_allocations(self, priority: str) -> Dict[str, int]:
        """Calculate token allocations based on priority mode"""
        total_tokens = self.config.max_total_tokens
        
        if priority == "personality":
            # Emphasize self-model
            return {
                "self_model": int(total_tokens * 0.5),
                "goals": int(total_tokens * 0.2),
                "experiences": int(total_tokens * 0.2),
                "metadata": int(total_tokens * 0.1)
            }
        elif priority == "goals":
            # Emphasize goals
            return {
                "self_model": int(total_tokens * 0.2),
                "goals": int(total_tokens * 0.5),
                "experiences": int(total_tokens * 0.2),
                "metadata": int(total_tokens * 0.1)
            }
        elif priority == "experiences":
            # Emphasize experiences
            return {
                "self_model": int(total_tokens * 0.2),
                "goals": int(total_tokens * 0.2),
                "experiences": int(total_tokens * 0.5),
                "metadata": int(total_tokens * 0.1)
            }
        else:  # balanced
            return {
                "self_model": int(total_tokens * self.config.self_model_weight),
                "goals": int(total_tokens * self.config.goals_weight),
                "experiences": int(total_tokens * self.config.experiences_weight),
                "metadata": int(total_tokens * self.config.metadata_weight)
            }
    
    def _prioritize_self_model_data(self, self_data: Dict[str, Any], 
                                  token_budget: int, keywords: List[str]) -> Dict[str, Any]:
        """Prioritize and compress self-model data"""
        if not self_data:
            return {}
        
        # Always include core identity (highest priority)
        core_self = {
            "identity": self_data.get("self_identity", {}),
            "baseline_emotion": self_data.get("emotional_baseline", "curious")
        }
        
        # Calculate remaining budget after core identity
        core_tokens = self.estimate_json_tokens(core_self)
        remaining_budget = max(0, token_budget - core_tokens)
        
        # Add traits based on priority and relevance
        traits = self_data.get("self_traits", {})
        if traits and remaining_budget > 20:
            # Sort traits by value (strength) and keyword relevance
            trait_scores = []
            for trait, value in traits.items():
                relevance = 1.0
                if keywords:
                    relevance = 1.2 if any(keyword in trait.lower() for keyword in keywords) else 0.8
                
                score = value * relevance
                trait_scores.append((score, trait, value))
            
            # Select top traits within budget
            selected_traits = {}
            trait_scores.sort(reverse=True)
            
            for score, trait, value in trait_scores:
                trait_entry = {trait: value}
                trait_tokens = self.estimate_json_tokens(trait_entry)
                
                if remaining_budget >= trait_tokens:
                    selected_traits[trait] = value
                    remaining_budget -= trait_tokens
                else:
                    break
            
            if selected_traits:
                core_self["key_traits"] = selected_traits
        
        # Add beliefs if space allows
        beliefs = self_data.get("core_beliefs", {})
        if beliefs and remaining_budget > 30:
            # Select most relevant beliefs
            selected_beliefs = {}
            for belief_key, belief_text in beliefs.items():
                belief_entry = {belief_key: belief_text}
                belief_tokens = self.estimate_json_tokens(belief_entry)
                
                if remaining_budget >= belief_tokens:
                    selected_beliefs[belief_key] = belief_text
                    remaining_budget -= belief_tokens
                
                if len(selected_beliefs) >= 3:  # Limit beliefs
                    break
            
            if selected_beliefs:
                core_self["beliefs"] = selected_beliefs
        
        return core_self
    
    def _prioritize_goals_data(self, goals_data: Dict[str, Any], 
                             token_budget: int, keywords: List[str]) -> Dict[str, Any]:
        """Prioritize and compress goals data"""
        if not goals_data:
            return {}
        
        buddy_goals = goals_data.get("buddy_active_goals", [])
        user_goals = goals_data.get("user_active_goals", [])
        
        # Prioritize goals by relevance and importance
        all_goals = []
        
        # Add Buddy goals with higher base priority
        for goal in buddy_goals:
            relevance = self._calculate_goal_relevance(goal, keywords)
            priority_score = goal.get("priority", 0.5) * 1.2 + relevance  # Boost Buddy goals
            all_goals.append((priority_score, goal, "buddy"))
        
        # Add user goals
        for goal in user_goals:
            relevance = self._calculate_goal_relevance(goal, keywords)
            priority_score = goal.get("priority", 0.5) + relevance
            all_goals.append((priority_score, goal, "user"))
        
        # Sort by priority and select within budget
        all_goals.sort(key=lambda x: x[0], reverse=True)  # Sort by priority score
        
        selected_goals = {"buddy": [], "user": []}
        remaining_budget = token_budget
        
        for priority_score, goal, owner in all_goals:
            # Create compact goal representation
            compact_goal = {
                "title": goal["title"][:50],  # Truncate title
                "priority": goal.get("priority", 0.5),
                "progress": goal.get("progress", 0.0)
            }
            
            # Add description only for high-priority goals
            if priority_score > 1.0 and remaining_budget > 50:
                compact_goal["description"] = goal.get("description", "")[:100]
            
            goal_tokens = self.estimate_json_tokens(compact_goal)
            
            if remaining_budget >= goal_tokens:
                selected_goals[owner].append(compact_goal)
                remaining_budget -= goal_tokens
            
            # Limit total goals
            if len(selected_goals["buddy"]) + len(selected_goals["user"]) >= 8:
                break
        
        # Include goal stats if space allows
        result = selected_goals
        stats = goals_data.get("goal_stats", {})
        if stats and remaining_budget > 20:
            result["stats"] = {
                "active_count": stats.get("active_count", 0),
                "completed": stats.get("total_completed", 0)
            }
        
        return result
    
    def _calculate_goal_relevance(self, goal: Dict[str, Any], keywords: List[str]) -> float:
        """Calculate goal relevance to current context"""
        if not keywords:
            return 0.0
        
        goal_text = (goal.get("title", "") + " " + goal.get("description", "")).lower()
        
        matches = sum(1 for keyword in keywords if keyword in goal_text)
        return min(1.0, matches / len(keywords))
    
    def _prioritize_experiences_data(self, exp_data: Dict[str, Any], 
                                   token_budget: int, keywords: List[str], 
                                   user: str = None) -> Dict[str, Any]:
        """Prioritize and compress experiences data"""
        if not exp_data:
            return {}
        
        priority_exp = exp_data.get("priority_experiences", [])
        recent_exp = exp_data.get("recent_experiences", [])
        emotional_exp = exp_data.get("emotional_sample", [])
        
        # Combine and score all experiences
        all_experiences = []
        
        # Priority experiences get highest base score
        for exp in priority_exp:
            relevance = self._calculate_experience_relevance(exp, keywords, user)
            score = exp.get("importance", 0.5) * 2.0 + relevance  # High boost for important
            all_experiences.append((score, exp, "priority"))
        
        # Recent experiences get recency boost
        for exp in recent_exp:
            relevance = self._calculate_experience_relevance(exp, keywords, user)
            recency_boost = 1.5 if self._is_very_recent(exp) else 1.0
            score = exp.get("importance", 0.5) * recency_boost + relevance
            all_experiences.append((score, exp, "recent"))
        
        # Emotional experiences for context
        for exp in emotional_exp:
            relevance = self._calculate_experience_relevance(exp, keywords, user)
            score = exp.get("importance", 0.5) * 0.8 + relevance  # Lower priority
            all_experiences.append((score, exp, "emotional"))
        
        # Remove duplicates and sort
        seen_events = set()
        unique_experiences = []
        for score, exp, category in all_experiences:
            event_key = exp.get("event", "")[:50]  # Use truncated event as key
            if event_key not in seen_events:
                seen_events.add(event_key)
                unique_experiences.append((score, exp, category))
        
        unique_experiences.sort(key=lambda x: x[0], reverse=True)  # Sort by score
        
        # Select experiences within budget
        selected_experiences = []
        remaining_budget = token_budget
        
        for score, exp, category in unique_experiences:
            # Create compact experience representation
            compact_exp = {
                "event": exp.get("event", "")[:80],  # Truncate event
                "emotion": exp.get("emotion", "neutral"),
                "importance": exp.get("importance", 0.5)
            }
            
            # Add timestamp for recent experiences
            if category == "recent" and remaining_budget > 30:
                compact_exp["when"] = exp.get("timestamp", "")
            
            exp_tokens = self.estimate_json_tokens(compact_exp)
            
            if remaining_budget >= exp_tokens:
                selected_experiences.append(compact_exp)
                remaining_budget -= exp_tokens
            
            # Limit total experiences
            if len(selected_experiences) >= 10:
                break
        
        result = {"experiences": selected_experiences}
        
        # Add stats if space allows
        stats = exp_data.get("experience_stats", {})
        if stats and remaining_budget > 15:
            result["stats"] = {
                "total": stats.get("total_experiences", 0),
                "common_emotion": stats.get("most_common_emotion", "neutral")
            }
        
        return result
    
    def _calculate_experience_relevance(self, exp: Dict[str, Any], 
                                      keywords: List[str], user: str = None) -> float:
        """Calculate experience relevance to current context"""
        if not keywords:
            return 0.0
        
        exp_text = exp.get("event", "").lower()
        
        matches = sum(1 for keyword in keywords if keyword in exp_text)
        relevance = matches / len(keywords)
        
        # Boost relevance for user-specific experiences
        if user and exp.get("user") == user:
            relevance *= 1.3
        
        return min(1.0, relevance)
    
    def _is_very_recent(self, exp: Dict[str, Any]) -> bool:
        """Check if experience is very recent (within last hour)"""
        timestamp_str = exp.get("timestamp", "")
        if not timestamp_str:
            return False
        
        try:
            exp_time = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
            age = datetime.now() - exp_time.replace(tzinfo=None)
            return age < timedelta(hours=1)
        except:
            return False
    
    def _create_metadata(self, token_budget: int) -> Dict[str, Any]:
        """Create system metadata within token budget"""
        metadata = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "cognitive_modules": "active"
        }
        
        # Only add extended metadata if budget allows
        if token_budget > 30:
            metadata.update({
                "memory_system": "prioritized",
                "session_continuity": True
            })
        
        return metadata
    
    def _emergency_compress(self, cognitive_context: Dict[str, Any]) -> Dict[str, Any]:
        """Emergency compression when context exceeds budget"""
        logging.warning("[MemoryPrioritizer] Emergency compression triggered")
        
        # Aggressive truncation strategy
        compressed = {}
        
        # Keep minimal self-model
        self_model = cognitive_context.get("self_model", {})
        compressed["self_model"] = {
            "identity": self_model.get("identity", {}).get("name", "Buddy"),
            "baseline_emotion": self_model.get("baseline_emotion", "curious"),
            "key_traits": dict(list(self_model.get("key_traits", {}).items())[:3])
        }
        
        # Keep top goals only
        goals = cognitive_context.get("goals", {})
        compressed["goals"] = {
            "buddy": goals.get("buddy", [])[:2],
            "user": goals.get("user", [])[:1]
        }
        
        # Keep top experiences only
        experiences = cognitive_context.get("experiences", {})
        exp_list = experiences.get("experiences", [])
        compressed["experiences"] = {"experiences": exp_list[:3]}
        
        # Minimal metadata
        compressed["meta"] = {"timestamp": datetime.now().strftime("%H:%M")}
        compressed["compressed"] = True
        
        return compressed

# Global instance
memory_prioritizer = MemoryPrioritizer()