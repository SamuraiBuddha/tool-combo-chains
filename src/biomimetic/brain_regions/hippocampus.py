"""
Hippocampus Memory Implementation (Working Memory)
Redis-based temporary memory with natural forgetting mechanisms
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import uuid
import redis.asyncio as redis

logger = logging.getLogger(__name__)

class HippocampusMemory:
    """
    Hippocampus-like working memory implementation using Redis.
    
    Features:
    - TTL-based natural forgetting (5-30 seconds typical)
    - Stream processing for sequential events
    - Fast context switching between tasks
    - Pattern buffer for immediate associations
    - Working memory consolidation triggers
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.redis_client = None
        self.stats = {
            'stores': 0,
            'retrievals': 0,
            'natural_forgetting': 0,
            'context_switches': 0
        }
        
        # Working memory parameters (biomimetic)
        self.default_ttl = config.get('default_ttl', 30)  # 30 seconds
        self.max_working_items = config.get('max_working_items', 7)  # Miller's 7±2 rule
        self.context_prefix = "hippocampus:context:"
        self.working_prefix = "hippocampus:working:"
        self.stream_prefix = "hippocampus:stream:"
        
    async def initialize(self):
        """Initialize Redis connection for working memory"""
        redis_url = self.config.get('url', 'redis://localhost:6379')
        self.redis_client = redis.from_url(redis_url, decode_responses=True)
        
        # Test connection
        await self.redis_client.ping()
        
        # Initialize working memory space
        await self._initialize_working_space()
        
        logger.info("Hippocampus (working memory) initialized")
    
    async def _initialize_working_space(self):
        """Set up the working memory environment"""
        # Create working memory stream for sequential processing
        stream_key = f"{self.stream_prefix}events"
        
        try:
            # Create stream if it doesn't exist
            await self.redis_client.xadd(stream_key, {"init": "hippocampus_started"})
        except:
            pass  # Stream already exists
    
    async def store_immediate(self, content: str, context: Dict[str, Any], 
                            metadata: Dict[str, Any], ttl: int = None) -> str:
        """
        Store immediate working memory with natural forgetting.
        
        This simulates the hippocampus's role in holding temporary information
        while it's being actively processed or waiting for consolidation.
        """
        self.stats['stores'] += 1
        
        if ttl is None:
            ttl = self.default_ttl
        
        memory_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        
        # Create working memory entry
        working_memory = {
            'id': memory_id,
            'content': content,
            'context': context,
            'metadata': metadata,
            'timestamp': timestamp,
            'access_count': 1,
            'last_access': timestamp
        }
        
        key = f"{self.working_prefix}{memory_id}"
        
        # Store with TTL (natural forgetting)
        await self.redis_client.setex(
            key, 
            ttl, 
            json.dumps(working_memory)
        )
        
        # Add to working memory stream for sequential processing
        stream_key = f"{self.stream_prefix}events"
        await self.redis_client.xadd(stream_key, {
            "type": "store",
            "memory_id": memory_id,
            "content_preview": content[:100],
            "ttl": str(ttl)
        })
        
        # Maintain working memory capacity (Miller's 7±2 rule)
        await self._maintain_working_capacity()
        
        logger.debug(f"Stored working memory: {memory_id} (TTL: {ttl}s)")
        return memory_id
    
    async def get_immediate(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve working memory item and update access pattern"""
        key = f"{self.working_prefix}{memory_id}"
        
        memory_data = await self.redis_client.get(key)
        if not memory_data:
            return None
        
        self.stats['retrievals'] += 1
        
        memory = json.loads(memory_data)
        
        # Update access pattern (Hebbian-like strengthening)
        memory['access_count'] += 1
        memory['last_access'] = datetime.utcnow().isoformat()
        
        # Extend TTL for frequently accessed items (attention effect)
        if memory['access_count'] > 3:
            current_ttl = await self.redis_client.ttl(key)
            if current_ttl > 0:
                new_ttl = min(current_ttl + 10, 60)  # Max 1 minute extension
                await self.redis_client.expire(key, new_ttl)
        
        # Update stored version
        await self.redis_client.setex(
            key,
            await self.redis_client.ttl(key),
            json.dumps(memory)
        )
        
        return memory
    
    async def search_working_memory(self, query: str, context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Search current working memory for relevant items.
        
        This implements the hippocampus's role in rapid associative recall
        of recently active information.
        """
        pattern = f"{self.working_prefix}*"
        keys = await self.redis_client.keys(pattern)
        
        results = []
        
        for key in keys:
            memory_data = await self.redis_client.get(key)
            if memory_data:
                memory = json.loads(memory_data)
                
                # Simple relevance scoring (would use embeddings in production)
                relevance = self._calculate_relevance(memory, query, context)
                
                if relevance > 0.3:  # Working memory relevance threshold
                    results.append({
                        'content': memory['content'],
                        'confidence': relevance,
                        'memory_id': memory['id'],
                        'context': memory['context'],
                        'timestamp': memory['timestamp'],
                        'source': 'hippocampus',
                        'emotional_weight': memory.get('emotional_weight', 0.5),
                        'procedural_relevance': memory.get('procedural_relevance', 0.3)
                    })
        
        # Sort by relevance and recency
        results.sort(key=lambda x: (x['confidence'], x['timestamp']), reverse=True)
        
        return results[:5]  # Return top 5 working memory matches
    
    async def get_current_context(self) -> Dict[str, Any]:
        """
        Get the current working memory context.
        
        This represents what the hippocampus currently has "active"
        and can inform other brain regions about ongoing processing.
        """
        # Get most recent working memory items
        pattern = f"{self.working_prefix}*"
        keys = await self.redis_client.keys(pattern)
        
        active_memories = []
        
        for key in keys:
            memory_data = await self.redis_client.get(key)
            if memory_data:
                memory = json.loads(memory_data)
                active_memories.append(memory)
        
        # Sort by last access time
        active_memories.sort(key=lambda x: x['last_access'], reverse=True)
        
        # Build context from most active items
        context = {
            'active_count': len(active_memories),
            'current_focus': active_memories[0]['content'][:200] if active_memories else '',
            'recent_contexts': [m['context'] for m in active_memories[:3]],
            'working_capacity': f"{len(active_memories)}/{self.max_working_items}",
            'most_accessed': max(active_memories, key=lambda x: x['access_count']) if active_memories else None
        }
        
        return context
    
    async def update_context(self, context_name: str, context_data: Dict[str, Any]):
        """Update current context in working memory"""
        self.stats['context_switches'] += 1
        
        context_key = f"{self.context_prefix}{context_name}"
        
        context_entry = {
            'name': context_name,
            'data': context_data,
            'timestamp': datetime.utcnow().isoformat(),
            'switches': self.stats['context_switches']
        }
        
        # Store context with shorter TTL (contexts change frequently)
        await self.redis_client.setex(
            context_key,
            self.default_ttl // 2,  # Half the normal TTL
            json.dumps(context_entry)
        )
    
    async def get_recent_active(self) -> List[Dict[str, Any]]:
        """
        Get recently active memories for consolidation.
        
        This simulates the hippocampus providing information to other
        brain regions during memory consolidation (like during sleep).
        """
        # Get stream of recent events
        stream_key = f"{self.stream_prefix}events"
        
        # Get events from last 5 minutes
        five_minutes_ago = int((datetime.utcnow() - timedelta(minutes=5)).timestamp() * 1000)
        
        events = await self.redis_client.xrange(stream_key, min=five_minutes_ago)
        
        # Get associated memory items that are still active
        active_memories = []
        
        for event_id, event_data in events:
            memory_id = event_data.get('memory_id')
            if memory_id:
                memory = await self.get_immediate(memory_id)
                if memory and memory['access_count'] > 1:  # Has been accessed multiple times
                    active_memories.append(memory)
        
        return active_memories
    
    async def archive(self, memory_id: str):
        """
        Archive working memory item (simulate transfer to long-term storage).
        
        This removes the item from working memory after it's been
        consolidated to long-term storage in other brain regions.
        """
        key = f"{self.working_prefix}{memory_id}"
        
        # Get final state before archiving
        memory_data = await self.redis_client.get(key)
        if memory_data:
            memory = json.loads(memory_data)
            
            # Log archival in stream
            stream_key = f"{self.stream_prefix}events"
            await self.redis_client.xadd(stream_key, {
                "type": "archive",
                "memory_id": memory_id,
                "access_count": str(memory['access_count']),
                "final_content": memory['content'][:100]
            })
            
            # Remove from working memory
            await self.redis_client.delete(key)
            
            logger.debug(f"Archived working memory: {memory_id}")
    
    async def _maintain_working_capacity(self):
        """
        Maintain working memory capacity following Miller's 7±2 rule.
        
        This implements the biological constraint that working memory
        can only hold a limited number of items simultaneously.
        """
        pattern = f"{self.working_prefix}*"
        keys = await self.redis_client.keys(pattern)
        
        if len(keys) > self.max_working_items:
            # Get all working memories with their access patterns
            memories_with_access = []
            
            for key in keys:
                memory_data = await self.redis_client.get(key)
                if memory_data:
                    memory = json.loads(memory_data)
                    memories_with_access.append((key, memory))
            
            # Sort by access count and recency (keep most important)
            memories_with_access.sort(
                key=lambda x: (x[1]['access_count'], x[1]['last_access']),
                reverse=True
            )
            
            # Remove least important items
            items_to_remove = len(keys) - self.max_working_items
            for i in range(items_to_remove):
                key_to_remove, memory_to_remove = memories_with_access[-(i+1)]
                
                await self.redis_client.delete(key_to_remove)
                self.stats['natural_forgetting'] += 1
                
                logger.debug(f"Natural forgetting (capacity): {memory_to_remove['id']}")
    
    def _calculate_relevance(self, memory: Dict[str, Any], query: str, context: Dict[str, Any] = None) -> float:
        """
        Calculate relevance score for working memory search.
        
        In production, this would use semantic embeddings,
        but for now we use simple keyword matching.
        """
        content = memory['content'].lower()
        query_lower = query.lower()
        
        # Basic keyword matching
        base_score = 0.0
        if query_lower in content:
            base_score = 0.8
        else:
            # Check for partial matches
            query_words = query_lower.split()
            matches = sum(1 for word in query_words if word in content)
            base_score = matches / len(query_words) if query_words else 0
        
        # Boost for recent access
        recency_boost = min(0.2, memory['access_count'] * 0.05)
        
        # Context boost
        context_boost = 0.0
        if context and memory.get('context'):
            # Simple context matching (would be more sophisticated in production)
            if any(key in memory['context'] for key in context.keys()):
                context_boost = 0.1
        
        return min(1.0, base_score + recency_boost + context_boost)
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get hippocampus performance statistics"""
        # Count current working memory items
        pattern = f"{self.working_prefix}*"
        current_items = len(await self.redis_client.keys(pattern))
        
        # Get stream length
        stream_key = f"{self.stream_prefix}events"
        try:
            stream_info = await self.redis_client.xinfo_stream(stream_key)
            stream_length = stream_info['length']
        except:
            stream_length = 0
        
        return {
            **self.stats,
            'current_working_items': current_items,
            'max_capacity': self.max_working_items,
            'capacity_utilization': f"{current_items}/{self.max_working_items}",
            'stream_events': stream_length,
            'default_ttl': self.default_ttl,
            'status': 'active'
        }
    
    async def shutdown(self):
        """Gracefully shutdown hippocampus connections"""
        if self.redis_client:
            await self.redis_client.close()
        logger.info("Hippocampus (working memory) shutdown")

# Helper functions for tool combo integration
async def get_working_context() -> Dict[str, Any]:
    """Helper to get current working memory context"""
    # This would be injected with the actual hippocampus instance
    pass

async def store_working_memory(content: str, ttl: int = 30) -> str:
    """Helper to store immediate working memory"""
    # This would be injected with the actual hippocampus instance
    pass
