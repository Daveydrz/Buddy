"""
Retrospective Memory System - Remember Buddy's own advice and responses
Created: 2025-01-21
Purpose: Store and retrieve Buddy's past advice/responses for later recall
"""

import json
import os
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict

@dataclass
class BuddyAdviceMemory:
    """Store Buddy's advice/response with searchable metadata"""
    memory_id: str
    timestamp: str
    user_question: str
    buddy_response: str
    topic: str
    advice_type: str  # "advice", "information", "suggestion", "explanation"
    priority: str     # "high", "medium", "low"
    keywords: List[str]
    advice_summary: str  # Compressed version for context injection

class RetrospectiveMemoryManager:
    """
    Manage Buddy's own response memories for future recall
    """
    
    def __init__(self, username: str):
        self.username = username
        self.memory_dir = f"memory/{username}"
        os.makedirs(self.memory_dir, exist_ok=True)
        
        # Load existing retrospective memories
        self.advice_memories = self.load_advice_memories()
        self.next_memory_id = len(self.advice_memories) + 1
        
        print(f"[RetrospectiveMemory] 🧠 Initialized for {username} with {len(self.advice_memories)} stored responses")
    
    def load_advice_memories(self) -> List[BuddyAdviceMemory]:
        """Load saved advice memories from disk"""
        memory_file = os.path.join(self.memory_dir, 'buddy_advice_memories.json')
        
        if not os.path.exists(memory_file):
            return []
        
        try:
            with open(memory_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return [BuddyAdviceMemory(**item) for item in data]
        except Exception as e:
            print(f"[RetrospectiveMemory] ⚠️ Error loading memories: {e}")
            return []
    
    def save_advice_memories(self):
        """Save advice memories to disk"""
        memory_file = os.path.join(self.memory_dir, 'buddy_advice_memories.json')
        
        try:
            data = [asdict(memory) for memory in self.advice_memories]
            with open(memory_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[RetrospectiveMemory] ⚠️ Error saving memories: {e}")
    
    def extract_advice_from_response(self, user_question: str, buddy_response: str) -> Optional[BuddyAdviceMemory]:
        """
        Extract and categorize advice/information from Buddy's response
        Uses LLM to determine if response contains meaningful advice worth remembering
        """
        try:
            # Use the existing LLM connection
            from ai.chat import ask_kobold
            
            # Smart extraction prompt - determine if response contains advice worth remembering
            extraction_prompt = f"""Smart advice extractor. Analyze Buddy's response to determine if it contains advice, suggestions, or meaningful information worth remembering.

RESPONSE TYPES:
- advice: Direct suggestions/recommendations ("cats prefer routine", "try setting reminders")
- information: Factual explanations ("cats are territorial animals")  
- suggestion: Ideas/options ("you could try...", "maybe consider...")
- explanation: How-to or reasoning ("here's why that happens...")

JSON format:
{{
  "contains_advice": true/false,
  "advice_type": "advice|information|suggestion|explanation",
  "topic": "main_topic_discussed",
  "priority": "high|medium|low",
  "keywords": ["keyword1", "keyword2"],
  "advice_summary": "brief_summary_for_recall"
}}

Return contains_advice: false for casual responses, greetings, or non-informational content.

User Question: "{user_question}"
Buddy Response: "{buddy_response}"

Extract advice/information:"""

            response = ask_kobold([
                {"role": "system", "content": extraction_prompt}
            ], max_tokens=150)
            
            if not response:
                return None
            
            # Parse JSON response
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if not json_match:
                return None
            
            advice_data = json.loads(json_match.group())
            
            # Only create memory if response contains meaningful advice
            if not advice_data.get('contains_advice', False):
                return None
            
            # Create advice memory
            memory_id = f"advice_{self.next_memory_id:04d}"
            self.next_memory_id += 1
            
            advice_memory = BuddyAdviceMemory(
                memory_id=memory_id,
                timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                user_question=user_question,
                buddy_response=buddy_response,
                topic=advice_data.get('topic', 'general'),
                advice_type=advice_data.get('advice_type', 'advice'),
                priority=advice_data.get('priority', 'medium'),
                keywords=advice_data.get('keywords', []),
                advice_summary=advice_data.get('advice_summary', buddy_response[:100] + "...")
            )
            
            print(f"[RetrospectiveMemory] 📝 Extracted {advice_memory.advice_type} about '{advice_memory.topic}'")
            return advice_memory
            
        except Exception as e:
            print(f"[RetrospectiveMemory] ⚠️ Error extracting advice: {e}")
            return None
    
    def store_buddy_response(self, user_question: str, buddy_response: str):
        """
        Process and store Buddy's response if it contains advice/information
        """
        # Extract advice from response
        advice_memory = self.extract_advice_from_response(user_question, buddy_response)
        
        if advice_memory:
            # Store the memory
            self.advice_memories.append(advice_memory)
            self.save_advice_memories()
            
            print(f"[RetrospectiveMemory] ✅ Stored {advice_memory.advice_type}: {advice_memory.memory_id}")
            return True
        
        return False
    
    def search_past_advice(self, query: str, max_results: int = 3) -> List[BuddyAdviceMemory]:
        """
        Search for past advice/responses relevant to current query
        """
        if not self.advice_memories:
            return []
        
        query_lower = query.lower()
        scored_memories = []
        
        for memory in self.advice_memories:
            score = 0.0
            
            # Keyword matching
            for keyword in memory.keywords:
                if keyword.lower() in query_lower:
                    score += 2.0
            
            # Topic matching
            if memory.topic.lower() in query_lower:
                score += 3.0
            
            # Content matching
            if any(word in memory.buddy_response.lower() for word in query_lower.split()):
                score += 1.0
            
            # Summary matching
            if any(word in memory.advice_summary.lower() for word in query_lower.split()):
                score += 1.5
            
            # Time decay (recent advice gets slight boost)
            try:
                memory_time = datetime.strptime(memory.timestamp, '%Y-%m-%d %H:%M:%S')
                hours_ago = (datetime.now() - memory_time).total_seconds() / 3600
                if hours_ago < 24:  # Last 24 hours get boost
                    score += 0.5
            except:
                pass
            
            if score > 0.5:  # Minimum relevance threshold
                scored_memories.append((score, memory))
        
        # Sort by relevance score and return top results
        scored_memories.sort(key=lambda x: x[0], reverse=True)
        return [memory for score, memory in scored_memories[:max_results]]
    
    def get_advice_context_injection(self, query: str) -> Optional[str]:
        """
        Get relevant past advice for context injection when answering similar questions
        """
        relevant_memories = self.search_past_advice(query, max_results=2)
        
        if not relevant_memories:
            return None
        
        # Build context injection
        context_parts = []
        for memory in relevant_memories:
            age = self._get_time_description(memory.timestamp)
            context_parts.append(f"Previously ({age}): {memory.advice_summary}")
        
        context_injection = "PAST ADVICE CONTEXT:\n" + "\n".join(context_parts)
        return context_injection
    
    def _get_time_description(self, timestamp_str: str) -> str:
        """Convert timestamp to human readable time description"""
        try:
            memory_time = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
            time_diff = datetime.now() - memory_time
            
            if time_diff.days > 0:
                return f"{time_diff.days} days ago"
            elif time_diff.seconds > 3600:
                hours = time_diff.seconds // 3600
                return f"{hours} hours ago"
            else:
                minutes = time_diff.seconds // 60
                return f"{minutes} minutes ago"
        except:
            return "earlier"

# Global manager instances
_retrospective_managers = {}

def get_retrospective_memory_manager(username: str) -> RetrospectiveMemoryManager:
    """Get or create retrospective memory manager for user"""
    if username not in _retrospective_managers:
        _retrospective_managers[username] = RetrospectiveMemoryManager(username)
    return _retrospective_managers[username]

def store_buddy_advice(username: str, user_question: str, buddy_response: str):
    """Store Buddy's response for future retrospective recall"""
    manager = get_retrospective_memory_manager(username)
    return manager.store_buddy_response(user_question, buddy_response)

def search_buddy_past_advice(username: str, query: str) -> List[str]:
    """Search for Buddy's past advice relevant to current query"""
    manager = get_retrospective_memory_manager(username)
    memories = manager.search_past_advice(query)
    
    # Return formatted results
    results = []
    for memory in memories:
        age = manager._get_time_description(memory.timestamp)
        results.append(f"Earlier ({age}) I mentioned: {memory.advice_summary}")
    
    return results

def get_past_advice_context(username: str, query: str) -> Optional[str]:
    """Get context injection of past advice for current response"""
    manager = get_retrospective_memory_manager(username)
    return manager.get_advice_context_injection(query)