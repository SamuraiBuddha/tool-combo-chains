"""
Enhanced Hippocampus Memory Implementation (Superhuman Eidetic Memory)
Redis-based working memory with weight decay instead of TTL deletion
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import uuid
import redis.asyncio as redis
import math

logger = logging.getLogger(__name__)

class SuperhumanHippocampus:
    """
    Enhanced Hippocampus implementation with superhuman eidetic memory capabilities.
    
    KEY PARADIGM SHIFT:
    - NO TTL DELETION (human limitation)
    - WEIGHT DECAY (superhuman capability)
    - EIDETIC MEMORY (everything preserved)
    - SUBCONSCIOUS ARCHIVE (zero-weight but accessible)
    
    Features:
    - Dynamic weight-based access instead of artificial forgetting
    - Subconscious memory archive with zero weights
    - Hypnotic/trauma-like deep access methods
    - Hebbian learning through weight reinforcement
    - Perfect recall capability while maintaining performance
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.redis_client = None
        self.stats = {
            'stores': 0,
            'retrievals': 0,
            'weight_decays': 0,
            'weight_boosts': 0,
            'subconscious_access': 0,
            'eidetic_recalls': 0
        }
        
        # Superhuman memory parameters
        self.max_working_items = config.get('max_working_items', 7)  # Miller's 7±2 for conscious access
        self.weight_decay_rate = config.get('weight_decay_rate', 0.95)  # Daily decay factor
        self.min_weight = config.get('min_weight', 0.001)  # Minimum weight before dormant
        self.boost_factor = config.get('boost_factor', 1.2)  # Weight boost on access
        
        # Weight thresholds for different access levels
        self.CONSCIOUS_THRESHOLD = 0.8      # Immediate conscious access
        self.EASY_RECALL_THRESHOLD = 0.5    # Easy recall with minimal effort  
        self.EFFORT_THRESHOLD = 0.2         # Requires focused effort
        self.SUBCONSCIOUS_THRESHOLD = 0.05  # Subconscious, needs triggers
        self.DORMANT_THRESHOLD = 0.001      # Deep archive, special access
        
        # Redis key prefixes
        self.memory_prefix = "superhuman:memory:"
        self.weight_prefix = "superhuman:weight:"
        self.archive_prefix = "superhuman:archive:"
        self.context_prefix = "superhuman:context:"
        
    async def initialize(self):
        """Initialize Redis connection for superhuman memory"""
        redis_url = self.config.get('url', 'redis://localhost:6379')
        self.redis_client = redis.from_url(redis_url, decode_responses=True)
        
        # Test connection
        await self.redis_client.ping()
        
        # Initialize superhuman memory space
        await self._initialize_eidetic_space()
        
        # Start background weight decay process
        asyncio.create_task(self._weight_decay_loop())
        
        logger.info("Superhuman Hippocampus (eidetic memory) initialized")
    
    async def _initialize_eidetic_space(self):
        """Set up the eidetic memory environment"""
        # Initialize memory tracking
        await self.redis_client.set("superhuman:initialized", datetime.utcnow().isoformat())
        
        # Create weight index for efficient access
        await self.redis_client.zadd("superhuman:weight_index", {})
    
    async def store_memory(self, content: str, context: Dict[str, Any], 
                          metadata: Dict[str, Any], initial_weight: float = 1.0) -> str:
        """
        Store memory with initial weight - NO DELETION, EVER.
        
        This implements superhuman eidetic memory - everything is preserved
        but accessed through dynamic weight-based prioritization.
        """
        self.stats['stores'] += 1
        
        memory_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        
        # Calculate initial weight based on multiple factors
        computed_weight = await self._calculate_initial_weight(
            content, context, metadata, initial_weight
        )
        
        # Create eidetic memory entry
        memory_entry = {
            'id': memory_id,
            'content': content,
            'context': context,
            'metadata': metadata,
            'timestamp': timestamp,
            'access_count': 1,
            'last_access': timestamp,
            'weight': computed_weight,
            'original_weight': computed_weight,
            'weight_history': [computed_weight],
            'boost_count': 0
        }
        
        # Store memory (NEVER expires - eidetic storage)
        memory_key = f"{self.memory_prefix}{memory_id}"
        await self.redis_client.set(memory_key, json.dumps(memory_entry))
        
        # Store weight for efficient access
        weight_key = f"{self.weight_prefix}{memory_id}"
        await self.redis_client.set(weight_key, str(computed_weight))
        
        # Add to weight-sorted index for efficient retrieval
        await self.redis_client.zadd("superhuman:weight_index", {memory_id: computed_weight})
        
        # Update working memory if weight is high enough
        if computed_weight >= self.CONSCIOUS_THRESHOLD:
            await self._update_working_memory(memory_id, computed_weight)
        
        logger.debug(f"Stored eidetic memory: {memory_id} (weight: {computed_weight:.3f})")
        return memory_id
    
    async def recall_memory(self, memory_id: str, boost_weight: bool = True) -> Optional[Dict[str, Any]]:
        """
        Recall specific memory and optionally boost its weight (Hebbian learning).
        
        This implements reconsolidation - memories change when recalled.
        """
        memory_key = f"{self.memory_prefix}{memory_id}"
        
        memory_data = await self.redis_client.get(memory_key)
        if not memory_data:
            return None
        
        self.stats['retrievals'] += 1
        
        memory = json.loads(memory_data)
        
        # Update access pattern
        memory['access_count'] += 1
        memory['last_access'] = datetime.utcnow().isoformat()
        
        # Hebbian learning - boost weight on access
        if boost_weight:
            old_weight = memory['weight']
            new_weight = min(1.0, old_weight * self.boost_factor)
            memory['weight'] = new_weight
            memory['boost_count'] += 1
            memory['weight_history'].append(new_weight)
            
            # Update weight tracking
            await self._update_weight_tracking(memory_id, new_weight)
            
            self.stats['weight_boosts'] += 1
            logger.debug(f"Boosted memory weight: {memory_id} ({old_weight:.3f} → {new_weight:.3f})")
        
        # Update stored memory
        await self.redis_client.set(memory_key, json.dumps(memory))
        
        return memory
    
    async def search_by_weight(self, min_weight: float = 0.5, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search memories by weight threshold for conscious access.
        
        This implements the weight-based access system that replaces
        artificial TTL deletion with natural prioritization.
        """
        # Get memories above weight threshold
        memory_ids = await self.redis_client.zrevrangebyscore(
            "superhuman:weight_index", 
            max=1.0, 
            min=min_weight,
            start=0,
            num=max_results
        )
        
        results = []
        for memory_id in memory_ids:
            memory = await self.recall_memory(memory_id, boost_weight=False)
            if memory:
                results.append({
                    'memory_id': memory['id'],
                    'content': memory['content'],
                    'weight': memory['weight'],
                    'access_count': memory['access_count'],
                    'timestamp': memory['timestamp'],
                    'context': memory['context'],
                    'source': 'conscious_access'
                })
        
        return results
    
    async def subconscious_search(self, query: str, context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Search subconscious memories (low weight but preserved).
        
        This accesses the zero-weight archive that represents the subconscious
        - memories that are there but not easily accessible.
        """
        self.stats['subconscious_access'] += 1
        
        # Search low-weight memories (subconscious range)
        memory_ids = await self.redis_client.zrevrangebyscore(
            "superhuman:weight_index",
            max=self.SUBCONSCIOUS_THRESHOLD,
            min=0.0,
            start=0,
            num=50  # Search more deeply in subconscious
        )
        
        results = []
        for memory_id in memory_ids:
            memory_key = f"{self.memory_prefix}{memory_id}"
            memory_data = await self.redis_client.get(memory_key)
            
            if memory_data:
                memory = json.loads(memory_data)
                
                # Simple relevance check for subconscious memories
                relevance = self._calculate_subconscious_relevance(memory, query, context)
                
                if relevance > 0.3:  # Subconscious relevance threshold
                    results.append({
                        'memory_id': memory['id'],
                        'content': memory['content'],
                        'weight': memory['weight'],
                        'relevance': relevance,
                        'access_count': memory['access_count'],
                        'timestamp': memory['timestamp'],
                        'source': 'subconscious'
                    })
        
        # Sort by relevance
        results.sort(key=lambda x: x['relevance'], reverse=True)
        
        return results[:10]  # Return top 10 subconscious matches
    
    async def eidetic_recall(self, pattern: str, deep_search: bool = False) -> List[Dict[str, Any]]:
        """
        Eidetic memory access - perfect recall capability.
        
        This is the superhuman capability that searches ALL memories
        regardless of weight, providing perfect recall.
        """
        self.stats['eidetic_recalls'] += 1
        
        # Get ALL memory IDs (eidetic capability)
        all_memory_ids = await self.redis_client.zrange("superhuman:weight_index", 0, -1)
        
        if deep_search:
            # Deep search mode - examine every memory
            search_limit = len(all_memory_ids)
        else:
            # Standard eidetic search - sample across weight spectrum
            search_limit = min(100, len(all_memory_ids))
        
        results = []
        for memory_id in all_memory_ids[:search_limit]:
            memory_key = f"{self.memory_prefix}{memory_id}"
            memory_data = await self.redis_client.get(memory_key)
            
            if memory_data:
                memory = json.loads(memory_data)
                
                # Pattern matching for eidetic recall
                if self._matches_eidetic_pattern(memory, pattern):
                    results.append({
                        'memory_id': memory['id'],
                        'content': memory['content'],
                        'weight': memory['weight'],
                        'access_count': memory['access_count'],
                        'timestamp': memory['timestamp'],
                        'context': memory['context'],
                        'source': 'eidetic_recall',
                        'weight_category': self._categorize_weight(memory['weight'])
                    })
        
        # Sort by original relevance, then by weight
        results.sort(key=lambda x: (x['weight'], x['timestamp']), reverse=True)
        
        logger.info(f"Eidetic recall found {len(results)} matches for pattern: {pattern}")
        return results
    
    async def _calculate_initial_weight(self, content: str, context: Dict[str, Any], 
                                      metadata: Dict[str, Any], hint: float) -> float:
        """Calculate initial memory weight based on multiple factors"""
        base_weight = hint
        
        # Emotional significance boost
        importance = metadata.get('importance', 0.5)
        emotional_boost = importance * 0.3
        
        # Context relevance boost
        context_boost = 0.0
        if context.get('critical') or context.get('urgent'):
            context_boost = 0.2
        
        # Content length factor (longer content might be more important)
        length_factor = min(0.1, len(content) / 1000)
        
        final_weight = min(1.0, base_weight + emotional_boost + context_boost + length_factor)
        return final_weight
    
    async def _update_weight_tracking(self, memory_id: str, new_weight: float):
        """Update weight tracking systems"""
        # Update weight value
        weight_key = f"{self.weight_prefix}{memory_id}"
        await self.redis_client.set(weight_key, str(new_weight))
        
        # Update weight index
        await self.redis_client.zadd("superhuman:weight_index", {memory_id: new_weight})
    
    async def _weight_decay_loop(self):
        """
        Background weight decay process (replaces TTL deletion).
        
        This implements natural forgetting through weight decay
        while preserving all memories for eidetic access.
        """
        while True:
            try:
                await asyncio.sleep(3600)  # Run every hour
                
                # Get all memories
                all_memory_ids = await self.redis_client.zrange("superhuman:weight_index", 0, -1)
                
                for memory_id in all_memory_ids:
                    memory_key = f"{self.memory_prefix}{memory_id}"
                    memory_data = await self.redis_client.get(memory_key)
                    
                    if memory_data:
                        memory = json.loads(memory_data)
                        
                        # Calculate decay based on last access
                        last_access = datetime.fromisoformat(memory['last_access'])
                        hours_since_access = (datetime.utcnow() - last_access).total_seconds() / 3600
                        
                        # Decay weight (but never delete)
                        if hours_since_access > 1:  # Only decay if not recently accessed
                            old_weight = memory['weight']
                            decay_factor = self.weight_decay_rate ** (hours_since_access / 24)  # Daily decay
                            new_weight = max(self.min_weight, old_weight * decay_factor)
                            
                            if new_weight != old_weight:
                                memory['weight'] = new_weight
                                memory['weight_history'].append(new_weight)
                                
                                # Update memory
                                await self.redis_client.set(memory_key, json.dumps(memory))
                                
                                # Update weight tracking
                                await self._update_weight_tracking(memory_id, new_weight)
                                
                                self.stats['weight_decays'] += 1
                
                logger.debug(f"Weight decay cycle completed - decayed {self.stats['weight_decays']} memories")
                
            except Exception as e:
                logger.error(f"Weight decay cycle failed: {str(e)}")
                await asyncio.sleep(300)  # Retry in 5 minutes
    
    async def _update_working_memory(self, memory_id: str, weight: float):
        """Update working memory with high-weight items"""
        # Add to working memory set if weight is high enough
        if weight >= self.CONSCIOUS_THRESHOLD:
            await self.redis_client.zadd("superhuman:working_memory", {memory_id: weight})
            
            # Maintain working memory capacity (Miller's 7±2)
            working_count = await self.redis_client.zcard("superhuman:working_memory")
            if working_count > self.max_working_items:
                # Remove lowest weight item from working memory (but keep in archive)
                await self.redis_client.zremrangebyrank("superhuman:working_memory", 0, 0)
    
    def _calculate_subconscious_relevance(self, memory: Dict[str, Any], query: str, 
                                        context: Dict[str, Any] = None) -> float:
        """Calculate relevance for subconscious memory search"""
        content = memory['content'].lower()
        query_lower = query.lower()
        
        # Basic pattern matching for subconscious
        base_score = 0.0
        if query_lower in content:
            base_score = 0.7
        else:
            query_words = query_lower.split()
            matches = sum(1 for word in query_words if word in content)
            base_score = matches / len(query_words) if query_words else 0
        
        # Context association boost
        context_boost = 0.0
        if context and memory.get('context'):
            shared_keys = set(context.keys()) & set(memory['context'].keys())
            context_boost = len(shared_keys) * 0.1
        
        return min(1.0, base_score + context_boost)
    
    def _matches_eidetic_pattern(self, memory: Dict[str, Any], pattern: str) -> bool:
        """Check if memory matches eidetic recall pattern"""
        content = memory['content'].lower()
        context_str = json.dumps(memory.get('context', {})).lower()
        metadata_str = json.dumps(memory.get('metadata', {})).lower()
        
        pattern_lower = pattern.lower()
        
        return (pattern_lower in content or 
                pattern_lower in context_str or 
                pattern_lower in metadata_str)
    
    def _categorize_weight(self, weight: float) -> str:
        """Categorize memory weight for analysis"""
        if weight >= self.CONSCIOUS_THRESHOLD:
            return "conscious"
        elif weight >= self.EASY_RECALL_THRESHOLD:
            return "easy_recall"
        elif weight >= self.EFFORT_THRESHOLD:
            return "effort_required"
        elif weight >= self.SUBCONSCIOUS_THRESHOLD:
            return "subconscious"
        else:
            return "deep_archive"
    
    async def get_memory_distribution(self) -> Dict[str, int]:
        """Get distribution of memories across weight categories"""
        all_weights = await self.redis_client.zrange("superhuman:weight_index", 0, -1, withscores=True)
        
        distribution = {
            "conscious": 0,
            "easy_recall": 0, 
            "effort_required": 0,
            "subconscious": 0,
            "deep_archive": 0
        }
        
        for memory_id, weight in all_weights:
            category = self._categorize_weight(weight)
            distribution[category] += 1
        
        return distribution
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get superhuman hippocampus statistics"""
        total_memories = await self.redis_client.zcard("superhuman:weight_index")
        working_memories = await self.redis_client.zcard("superhuman:working_memory")
        distribution = await self.get_memory_distribution()
        
        return {
            **self.stats,
            'total_memories': total_memories,
            'working_memories': working_memories,
            'memory_distribution': distribution,
            'eidetic_capability': True,
            'weight_decay_rate': self.weight_decay_rate,
            'superhuman_features': [
                'eidetic_memory',
                'weight_based_access',
                'subconscious_archive',
                'no_deletion_ever',
                'perfect_recall'
            ],
            'status': 'superhuman_active'
        }
    
    async def shutdown(self):
        """Gracefully shutdown superhuman hippocampus"""
        if self.redis_client:
            await self.redis_client.close()
        logger.info("Superhuman Hippocampus (eidetic memory) shutdown")

# Enhanced tool combo integration
async def superhuman_memory_decorator(memory_router):
    """Decorator for superhuman memory-enhanced tool combos"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Store execution context with high initial weight
            context = {
                'function': func.__name__,
                'args': str(args)[:200],
                'timestamp': datetime.utcnow().isoformat(),
                'superhuman': True
            }
            
            # Store in superhuman memory (never deleted)
            await memory_router.hippocampus.store_memory(
                content=f"Executing superhuman tool combo: {func.__name__}",
                context=context,
                metadata={'type': 'tool_execution', 'importance': 0.8},
                initial_weight=0.9  # High weight for tool executions
            )
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Store result with weight based on success
            if result:
                await memory_router.hippocampus.store_memory(
                    content=f"Successfully completed: {func.__name__}",
                    context=context,
                    metadata={
                        'type': 'success', 
                        'result_summary': str(result)[:500],
                        'importance': 0.9
                    },
                    initial_weight=0.85  # High weight for successful executions
                )
            
            return result
        return wrapper
    return decorator
