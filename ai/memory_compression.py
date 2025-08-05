"""
Memory Compression Engine
Created: 2025-01-17
Purpose: Compress verbose memory entries when token budget is exceeded
         Works with existing memory fusion system to prioritize and compress memories
"""

import json
import time
import math
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import re

class MemoryCompressionEngine:
    """
    Compress verbose memory entries when token budget is exceeded
    Integrates with existing memory fusion system
    """
    
    def __init__(self):
        self.compression_levels = {
            'high_significance': {
                'threshold': 0.8,
                'token_prefix': 'mem1',
                'content_length': 50,
                'preserve_details': True
            },
            'medium_significance': {
                'threshold': 0.5,
                'token_prefix': 'mem2', 
                'content_length': 30,
                'preserve_details': False
            },
            'low_significance': {
                'threshold': 0.0,
                'token_prefix': 'mem3',
                'content_length': 15,
                'preserve_details': False
            }
        }
        
        # Priority keywords for preserving important information
        self.priority_keywords = {
            'personal': ['name', 'job', 'family', 'relationship', 'career', 'work'],
            'emotional': ['sad', 'happy', 'angry', 'excited', 'worried', 'love', 'hate'],
            'temporal': ['today', 'yesterday', 'tomorrow', 'recently', 'soon', 'never'],
            'critical': ['emergency', 'urgent', 'important', 'critical', 'deadline'],
            'relationships': ['friend', 'colleague', 'boss', 'partner', 'spouse', 'child']
        }
        
        # Compression strategies
        self.compression_strategies = {
            'keyword_extraction': self._extract_keywords,
            'entity_preservation': self._preserve_entities,
            'temporal_compression': self._compress_temporal_info,
            'emotional_preservation': self._preserve_emotional_content,
            'fact_distillation': self._distill_facts
        }
        
        print("[MemoryCompression] 🧠 Memory compression engine initialized")
    
    def compress_memory_entry(self, memory_entry: Dict[str, Any], max_tokens: int = 50) -> str:
        """
        Compress memory entry when token budget is exceeded
        Compatible with existing memory fusion patterns
        
        Args:
            memory_entry: Memory data to compress
            max_tokens: Maximum token budget
            
        Returns:
            Compressed memory with symbolic tokens like <mem1>, <mem2>, <mem3>
        """
        try:
            if not memory_entry:
                return "<mem_empty>"
            
            # Extract key information
            content = memory_entry.get('content', '')
            significance = memory_entry.get('significance', 0.5)
            memory_type = memory_entry.get('type', 'general')
            timestamp = memory_entry.get('timestamp', '')
            emotional_weight = memory_entry.get('emotional_weight', 0.0)
            
            # Determine compression level based on significance
            compression_level = self._determine_compression_level(significance)
            config = self.compression_levels[compression_level]
            
            # Apply compression strategies
            compressed_content = self._apply_compression_strategies(
                content, config['content_length'], memory_type, emotional_weight
            )
            
            # Create symbolic token as specified in requirements
            token_prefix = config['token_prefix']
            symbolic_token = f"<{token_prefix}:{memory_type}:{significance:.2f}>"
            
            # Combine token with compressed content
            result = f"{symbolic_token} {compressed_content}"
            
            # Ensure we don't exceed token budget
            words = result.split()
            if len(words) > max_tokens:
                # Preserve symbolic token, trim content
                token_words = symbolic_token.split()
                content_budget = max_tokens - len(token_words)
                if content_budget > 0:
                    content_words = compressed_content.split()[:content_budget]
                    result = f"{symbolic_token} {' '.join(content_words)}..."
                else:
                    result = symbolic_token
            
            print(f"[MemoryCompression] 🗜️ Compressed memory ({significance:.2f}) to {len(result.split())} tokens")
            return result
            
        except Exception as e:
            print(f"[MemoryCompression] ❌ Error compressing memory: {e}")
            return "<mem_error>"
    
    def compress_memory_collection(self, memories: List[Dict[str, Any]], 
                                 total_budget: int) -> List[str]:
        """
        Compress a collection of memories to fit within total budget
        Prioritizes recent and high emotional significance
        
        Args:
            memories: List of memory entries
            total_budget: Total token budget for all memories
            
        Returns:
            List of compressed memory strings
        """
        try:
            if not memories:
                return []
            
            # Sort memories by priority (significance + recency + emotion)
            prioritized_memories = self._prioritize_memories(memories)
            
            compressed_memories = []
            tokens_used = 0
            
            for memory in prioritized_memories:
                # Calculate remaining budget
                remaining_budget = total_budget - tokens_used
                if remaining_budget <= 5:  # Reserve minimum space
                    break
                
                # Compress individual memory
                memory_budget = min(remaining_budget // 2, 20)  # Reasonable per-memory budget
                compressed = self.compress_memory_entry(memory, memory_budget)
                
                # Check if it fits
                memory_tokens = len(compressed.split())
                if tokens_used + memory_tokens <= total_budget:
                    compressed_memories.append(compressed)
                    tokens_used += memory_tokens
                else:
                    # Try with minimal compression
                    minimal_compressed = self.compress_memory_entry(memory, 5)
                    minimal_tokens = len(minimal_compressed.split())
                    if tokens_used + minimal_tokens <= total_budget:
                        compressed_memories.append(minimal_compressed)
                        tokens_used += minimal_tokens
                    # Otherwise skip this memory
            
            print(f"[MemoryCompression] 📦 Compressed {len(compressed_memories)}/{len(memories)} memories using {tokens_used}/{total_budget} tokens")
            return compressed_memories
            
        except Exception as e:
            print(f"[MemoryCompression] ❌ Error compressing memory collection: {e}")
            return ["<mem_collection_error>"]
    
    def preserve_critical_information(self, memory_entries: List[Dict[str, Any]], 
                                    critical_budget: int) -> List[str]:
        """
        Preserve critical relationship information and belief consistency
        
        Args:
            memory_entries: Memory entries to analyze
            critical_budget: Budget reserved for critical information
            
        Returns:
            List of critical information tokens
        """
        try:
            critical_memories = []
            
            for memory in memory_entries:
                # Check for critical indicators
                content = memory.get('content', '').lower()
                significance = memory.get('significance', 0.0)
                
                is_critical = (
                    significance > 0.9 or
                    any(keyword in content for category in ['critical', 'relationships', 'personal'] 
                        for keyword in self.priority_keywords[category]) or
                    memory.get('type') in ['relationship', 'belief', 'identity', 'emergency']
                )
                
                if is_critical:
                    # Use minimal compression for critical info
                    compressed = self.compress_memory_entry(memory, 15)
                    critical_memories.append(compressed)
            
            # Trim to budget
            if critical_memories:
                total_tokens = sum(len(mem.split()) for mem in critical_memories)
                if total_tokens > critical_budget:
                    # Keep most critical
                    critical_memories = critical_memories[:critical_budget // 10]
            
            print(f"[MemoryCompression] 🚨 Preserved {len(critical_memories)} critical memories")
            return critical_memories
            
        except Exception as e:
            print(f"[MemoryCompression] ❌ Error preserving critical info: {e}")
            return ["<critical_error>"]
    
    def _determine_compression_level(self, significance: float) -> str:
        """Determine compression level based on significance"""
        if significance >= 0.8:
            return 'high_significance'
        elif significance >= 0.5:
            return 'medium_significance'
        else:
            return 'low_significance'
    
    def _apply_compression_strategies(self, content: str, max_length: int, 
                                    memory_type: str, emotional_weight: float) -> str:
        """Apply multiple compression strategies"""
        try:
            if len(content) <= max_length:
                return content
            
            # Start with original content
            compressed = content
            
            # Apply strategies in order of priority
            if emotional_weight > 0.3:
                compressed = self._preserve_emotional_content(compressed, max_length)
            
            if memory_type in ['personal', 'relationship', 'identity']:
                compressed = self._preserve_entities(compressed, max_length)
            
            # Extract keywords as fallback
            if len(compressed) > max_length:
                compressed = self._extract_keywords(compressed, max_length)
            
            # Final truncation if needed
            if len(compressed) > max_length:
                compressed = compressed[:max_length] + "..."
            
            return compressed
            
        except Exception as e:
            print(f"[MemoryCompression] ❌ Error in compression strategies: {e}")
            return content[:max_length] + "..."
    
    def _extract_keywords(self, content: str, max_length: int) -> str:
        """Extract important keywords from content"""
        try:
            words = content.split()
            
            # Priority keywords get preserved
            priority_words = []
            for category, keywords in self.priority_keywords.items():
                for word in words:
                    if word.lower() in keywords and word not in priority_words:
                        priority_words.append(word)
            
            # Add other significant words
            other_words = [w for w in words if w not in priority_words and len(w) > 3]
            
            # Combine and trim
            combined = priority_words + other_words
            result = " ".join(combined)
            
            if len(result) > max_length:
                # Keep priority words, trim others
                priority_text = " ".join(priority_words)
                if len(priority_text) <= max_length:
                    remaining = max_length - len(priority_text) - 1
                    other_text = " ".join(other_words)
                    if remaining > 0:
                        result = priority_text + " " + other_text[:remaining]
                    else:
                        result = priority_text
                else:
                    result = priority_text[:max_length]
            
            return result
            
        except Exception as e:
            return content[:max_length]
    
    def _preserve_entities(self, content: str, max_length: int) -> str:
        """Preserve named entities and important nouns"""
        try:
            words = content.split()
            
            # Simple entity detection (capitalized words, numbers, etc.)
            entities = []
            for word in words:
                if (word[0].isupper() and len(word) > 1) or word.isdigit():
                    entities.append(word)
            
            # Preserve entities and context
            preserved = entities.copy()
            
            # Add context words
            for i, word in enumerate(words):
                if word in entities:
                    # Add surrounding context
                    if i > 0:
                        preserved.append(words[i-1])
                    if i < len(words) - 1:
                        preserved.append(words[i+1])
            
            # Remove duplicates while preserving order
            seen = set()
            result_words = []
            for word in preserved:
                if word not in seen:
                    seen.add(word)
                    result_words.append(word)
            
            result = " ".join(result_words)
            if len(result) > max_length:
                result = result[:max_length] + "..."
            
            return result
            
        except Exception as e:
            return content[:max_length]
    
    def _compress_temporal_info(self, content: str, max_length: int) -> str:
        """Compress temporal information"""
        try:
            # Simple temporal compression - keep dates and time references
            words = content.split()
            temporal_words = []
            
            for word in words:
                # Keep dates, times, temporal keywords
                if (any(t in word.lower() for t in ['today', 'yesterday', 'tomorrow', 'recently', 'ago', 'day', 'week', 'month', 'year']) or
                    re.match(r'\d{1,2}[/-]\d{1,2}', word) or
                    re.match(r'\d{4}', word)):
                    temporal_words.append(word)
            
            # Add some context
            if temporal_words:
                result = " ".join(temporal_words)
            else:
                result = " ".join(words[:max_length//6])  # Fallback
            
            if len(result) > max_length:
                result = result[:max_length] + "..."
                
            return result
            
        except Exception as e:
            return content[:max_length]
    
    def _preserve_emotional_content(self, content: str, max_length: int) -> str:
        """Preserve emotional content and sentiment"""
        try:
            words = content.split()
            emotional_words = []
            
            # Find emotional keywords
            for word in words:
                if any(emotion in word.lower() for emotion_list in self.priority_keywords['emotional'] for emotion in [emotion_list]):
                    emotional_words.append(word)
            
            # Add context around emotional words
            for i, word in enumerate(words):
                if word in emotional_words:
                    # Add context
                    start = max(0, i-2)
                    end = min(len(words), i+3)
                    emotional_words.extend(words[start:end])
            
            # Remove duplicates
            seen = set()
            result_words = []
            for word in emotional_words:
                if word not in seen:
                    seen.add(word)
                    result_words.append(word)
            
            result = " ".join(result_words)
            if len(result) > max_length:
                result = result[:max_length] + "..."
            
            return result
            
        except Exception as e:
            return content[:max_length]
    
    def _distill_facts(self, content: str, max_length: int) -> str:
        """Distill content to core facts"""
        try:
            # Simple fact extraction - keep nouns, verbs, numbers
            words = content.split()
            fact_words = []
            
            for word in words:
                # Keep words that look like facts
                if (len(word) > 2 and 
                    (word.isdigit() or 
                     word[0].isupper() or 
                     len(word) > 4)):
                    fact_words.append(word)
            
            result = " ".join(fact_words)
            if len(result) > max_length:
                result = result[:max_length] + "..."
            elif not result.strip():
                result = " ".join(words[:max_length//6])  # Fallback
            
            return result
            
        except Exception as e:
            return content[:max_length]
    
    def _prioritize_memories(self, memories: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Prioritize memories based on significance, recency, and emotional impact
        Maintains belief consistency
        """
        try:
            scored_memories = []
            
            for memory in memories:
                significance = memory.get('significance', 0.5)
                emotional_weight = memory.get('emotional_weight', 0.0)
                memory_type = memory.get('type', 'general')
                timestamp = memory.get('timestamp', '')
                
                # Calculate recency score
                recency_score = self._calculate_recency_score(timestamp)
                
                # Calculate type priority
                type_priorities = {
                    'relationship': 0.9,
                    'belief': 0.8,
                    'identity': 0.8,
                    'personal': 0.7,
                    'emotional': 0.6,
                    'factual': 0.5,
                    'general': 0.3
                }
                type_score = type_priorities.get(memory_type, 0.3)
                
                # Combined priority score
                priority_score = (
                    significance * 0.4 +
                    emotional_weight * 0.3 +
                    recency_score * 0.2 +
                    type_score * 0.1
                )
                
                scored_memories.append((priority_score, memory))
            
            # Sort by priority (descending)
            scored_memories.sort(key=lambda x: x[0], reverse=True)
            
            return [memory for score, memory in scored_memories]
            
        except Exception as e:
            print(f"[MemoryCompression] ❌ Error prioritizing memories: {e}")
            return memories
    
    def _calculate_recency_score(self, timestamp: str) -> float:
        """Calculate recency score (1.0 = very recent, 0.0 = very old)"""
        try:
            if not timestamp:
                return 0.5  # Default for unknown timestamps
            
            # Parse timestamp
            if isinstance(timestamp, str):
                try:
                    mem_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                except:
                    return 0.5
            else:
                return 0.5
            
            # Calculate time difference
            now = datetime.now(mem_time.tzinfo) if mem_time.tzinfo else datetime.now()
            time_diff = now - mem_time
            
            # Convert to recency score
            days_ago = time_diff.total_seconds() / (24 * 3600)
            
            if days_ago < 1:
                return 1.0  # Today
            elif days_ago < 7:
                return 0.8  # This week
            elif days_ago < 30:
                return 0.6  # This month
            elif days_ago < 90:
                return 0.4  # This quarter
            else:
                return 0.2  # Older
                
        except Exception as e:
            return 0.5

# Global instance
memory_compression_engine = MemoryCompressionEngine()

def compress_memory_entry(memory_entry: Dict[str, Any], max_tokens: int = 50) -> str:
    """
    Main function to compress memory entry
    Compatible with existing consciousness_tokenizer interface
    """
    return memory_compression_engine.compress_memory_entry(memory_entry, max_tokens)

def compress_memory_collection(memories: List[Dict[str, Any]], total_budget: int) -> List[str]:
    """
    Compress collection of memories to fit within budget
    """
    return memory_compression_engine.compress_memory_collection(memories, total_budget)

def preserve_critical_memories(memory_entries: List[Dict[str, Any]], 
                             critical_budget: int) -> List[str]:
    """
    Preserve critical relationship information and belief consistency
    """
    return memory_compression_engine.preserve_critical_information(memory_entries, critical_budget)

if __name__ == "__main__":
    # Test the memory compression engine
    print("🧪 Testing Memory Compression Engine")
    
    # Test single memory compression
    test_memory = {
        'content': 'User mentioned they work as a software engineer at a tech company in Brisbane and really enjoy Python programming',
        'significance': 0.8,
        'type': 'personal',
        'timestamp': datetime.now().isoformat(),
        'emotional_weight': 0.6
    }
    
    compressed = compress_memory_entry(test_memory, 20)
    print(f"✅ Compressed memory: {compressed}")
    
    # Test memory collection compression
    test_memories = [
        {
            'content': 'User has a pet dog named Buddy who is very friendly',
            'significance': 0.7,
            'type': 'personal',
            'timestamp': datetime.now().isoformat(),
            'emotional_weight': 0.8
        },
        {
            'content': 'User mentioned their job involves machine learning',
            'significance': 0.6,
            'type': 'factual',
            'timestamp': (datetime.now() - timedelta(days=1)).isoformat(),
            'emotional_weight': 0.3
        },
        {
            'content': 'User seemed excited about a new project',
            'significance': 0.5,
            'type': 'emotional',
            'timestamp': datetime.now().isoformat(),
            'emotional_weight': 0.9
        }
    ]
    
    compressed_collection = compress_memory_collection(test_memories, 40)
    print(f"✅ Compressed collection: {compressed_collection}")