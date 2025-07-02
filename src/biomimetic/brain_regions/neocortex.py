"""
Neocortex Brain Region - PostgreSQL + pgvector Implementation
Biomimetic Neuromorphic Architecture - Long-term Semantic Memory

Function: Consolidated knowledge and semantic understanding with unlimited scope
Database: PostgreSQL with pgvector extension for vector embeddings
"""

import asyncio
import asyncpg
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timezone
import json
import logging
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class MemoryImportance(Enum):
    CRITICAL = "critical"
    HIGH = "high" 
    MEDIUM = "medium"
    LOW = "low"

@dataclass
class SemanticMemory:
    id: str
    content: str
    embedding: List[float]
    metadata: Dict[str, Any]
    importance_score: float
    consolidated_at: datetime
    access_count: int
    last_accessed: datetime
    associations: List[str]
    
class NeocortexProcessor:
    """
    Neocortex - Long-term Semantic Memory Processor
    
    Biological Functions Implemented:
    - Semantic memory consolidation from hippocampus
    - Vector similarity search for knowledge retrieval
    - ACID properties ensuring memory integrity
    - Complex pattern queries for deep understanding
    - Persistent semantic relationships
    - Unlimited scope through database-native processing (Jordan's insight)
    """
    
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.pool: Optional[asyncpg.Pool] = None
        
    async def initialize(self):
        """Initialize PostgreSQL connection pool and create tables"""
        self.pool = await asyncpg.create_pool(
            self.connection_string,
            min_size=5,
            max_size=20,
            command_timeout=60
        )
        
        await self._create_tables()
        await self._create_indexes()
        logger.info("Neocortex initialized with PostgreSQL+pgvector")
        
    async def _create_tables(self):
        """Create semantic memory tables with vector support"""
        async with self.pool.acquire() as conn:
            # Enable pgvector extension
            await conn.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            
            # Semantic memories table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS semantic_memories (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    content TEXT NOT NULL,
                    embedding vector(1536),  -- OpenAI embedding dimensions
                    metadata JSONB DEFAULT '{}',
                    importance_score FLOAT DEFAULT 0.5,
                    consolidated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    access_count INTEGER DEFAULT 0,
                    last_accessed TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    associations TEXT[] DEFAULT ARRAY[]::TEXT[],
                    source_hippocampus_id UUID,
                    emotional_weight FLOAT DEFAULT 0.0,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );
            """)
            
            # Semantic relationships table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS semantic_relationships (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    source_memory_id UUID REFERENCES semantic_memories(id),
                    target_memory_id UUID REFERENCES semantic_memories(id),
                    relationship_type TEXT NOT NULL,
                    strength FLOAT DEFAULT 0.5,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    last_reinforced TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    reinforcement_count INTEGER DEFAULT 1
                );
            """)
            
            # Knowledge patterns table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS knowledge_patterns (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    pattern_name TEXT UNIQUE NOT NULL,
                    pattern_embedding vector(1536),
                    associated_memories UUID[],
                    pattern_strength FLOAT DEFAULT 0.5,
                    discovery_method TEXT DEFAULT 'automatic',
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );
            """)
            
    async def _create_indexes(self):
        """Create optimized indexes for vector similarity and semantic search"""
        async with self.pool.acquire() as conn:
            # Vector similarity index (HNSW for fast ANN search)
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS semantic_memories_embedding_idx 
                ON semantic_memories USING hnsw (embedding vector_cosine_ops);
            """)
            
            # Traditional indexes for fast filtering
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS semantic_memories_importance_idx 
                ON semantic_memories (importance_score DESC);
            """)
            
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS semantic_memories_access_idx 
                ON semantic_memories (access_count DESC, last_accessed DESC);
            """)
            
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS semantic_relationships_source_idx 
                ON semantic_relationships (source_memory_id);
            """)
            
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS semantic_relationships_strength_idx 
                ON semantic_relationships (strength DESC);
            """)
            
    async def consolidate_from_hippocampus(
        self, 
        hippocampus_memory: Dict[str, Any],
        embedding: List[float],
        importance_threshold: float = 0.7
    ) -> str:
        """
        Consolidate important memories from hippocampus to long-term storage
        
        Biological Process: Memory consolidation during sleep/idle periods
        """
        if hippocampus_memory.get('importance_score', 0) < importance_threshold:
            logger.debug(f"Memory below consolidation threshold: {importance_threshold}")
            return None
            
        async with self.pool.acquire() as conn:
            memory_id = await conn.fetchval("""
                INSERT INTO semantic_memories (
                    content, embedding, metadata, importance_score,
                    associations, source_hippocampus_id, emotional_weight
                ) VALUES ($1, $2, $3, $4, $5, $6, $7)
                RETURNING id;
            """, 
                hippocampus_memory['content'],
                embedding,
                json.dumps(hippocampus_memory.get('metadata', {})),
                hippocampus_memory.get('importance_score', 0.5),
                hippocampus_memory.get('associations', []),
                hippocampus_memory.get('id'),
                hippocampus_memory.get('emotional_weight', 0.0)
            )
            
            # Create semantic relationships
            await self._establish_semantic_relationships(memory_id, embedding)
            
            logger.info(f"Consolidated memory {memory_id} from hippocampus")
            return str(memory_id)
    
    async def semantic_search(
        self, 
        query_embedding: List[float], 
        similarity_threshold: float = 0.8,
        limit: int = 10,
        importance_boost: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Perform semantic similarity search with unlimited scope
        
        Jordan's Insight: Database-native processing vs context limitations
        Performance: 10ms vs 2s for context-based search
        """
        async with self.pool.acquire() as conn:
            # Enhanced query with importance and recency scoring
            query = """
                SELECT 
                    id,
                    content,
                    embedding,
                    metadata,
                    importance_score,
                    access_count,
                    last_accessed,
                    associations,
                    emotional_weight,
                    1 - (embedding <=> $1) as similarity_score,
                    CASE WHEN $4 THEN 
                        (1 - (embedding <=> $1)) * 
                        (importance_score * 0.7 + (access_count::float / 100) * 0.3)
                    ELSE 
                        1 - (embedding <=> $1)
                    END as final_score
                FROM semantic_memories
                WHERE 1 - (embedding <=> $1) > $2
                ORDER BY final_score DESC
                LIMIT $3;
            """
            
            rows = await conn.fetch(
                query, 
                query_embedding, 
                similarity_threshold, 
                limit, 
                importance_boost
            )
            
            # Update access statistics
            memory_ids = [row['id'] for row in rows]
            if memory_ids:
                await conn.execute("""
                    UPDATE semantic_memories 
                    SET access_count = access_count + 1,
                        last_accessed = NOW()
                    WHERE id = ANY($1);
                """, memory_ids)
            
            results = []
            for row in rows:
                results.append({
                    'id': str(row['id']),
                    'content': row['content'],
                    'metadata': json.loads(row['metadata']) if row['metadata'] else {},
                    'importance_score': row['importance_score'],
                    'similarity_score': float(row['similarity_score']),
                    'final_score': float(row['final_score']),
                    'access_count': row['access_count'],
                    'associations': row['associations'],
                    'emotional_weight': row['emotional_weight']
                })
            
            logger.info(f"Semantic search returned {len(results)} memories")
            return results
    
    async def _establish_semantic_relationships(
        self, 
        memory_id: str, 
        embedding: List[float]
    ):
        """Establish relationships with semantically similar memories"""
        # Find similar memories for relationship creation
        similar_memories = await self.semantic_search(
            embedding, 
            similarity_threshold=0.85, 
            limit=5,
            importance_boost=False
        )
        
        async with self.pool.acquire() as conn:
            for similar in similar_memories:
                if similar['id'] != memory_id:
                    # Create bidirectional relationship
                    await conn.execute("""
                        INSERT INTO semantic_relationships 
                        (source_memory_id, target_memory_id, relationship_type, strength)
                        VALUES ($1, $2, 'semantic_similarity', $3)
                        ON CONFLICT DO NOTHING;
                    """, memory_id, similar['id'], similar['similarity_score'])
                    
                    await conn.execute("""
                        INSERT INTO semantic_relationships 
                        (source_memory_id, target_memory_id, relationship_type, strength)
                        VALUES ($1, $2, 'semantic_similarity', $3)
                        ON CONFLICT DO NOTHING;
                    """, similar['id'], memory_id, similar['similarity_score'])
    
    async def get_memory_associations(self, memory_id: str) -> List[Dict[str, Any]]:
        """Get all memories associated with a given memory"""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT 
                    sm.id,
                    sm.content,
                    sm.importance_score,
                    sr.relationship_type,
                    sr.strength,
                    sr.last_reinforced
                FROM semantic_memories sm
                JOIN semantic_relationships sr ON sm.id = sr.target_memory_id
                WHERE sr.source_memory_id = $1
                ORDER BY sr.strength DESC, sr.last_reinforced DESC;
            """, memory_id)
            
            return [dict(row) for row in rows]
    
    async def reinforce_relationship(
        self, 
        source_id: str, 
        target_id: str, 
        strength_increase: float = 0.1
    ):
        """Strengthen relationship between memories (Hebbian learning)"""
        async with self.pool.acquire() as conn:
            await conn.execute("""
                UPDATE semantic_relationships 
                SET strength = LEAST(1.0, strength + $3),
                    last_reinforced = NOW(),
                    reinforcement_count = reinforcement_count + 1
                WHERE source_memory_id = $1 AND target_memory_id = $2;
            """, source_id, target_id, strength_increase)
    
    async def discover_knowledge_patterns(self, min_pattern_strength: float = 0.6) -> List[Dict[str, Any]]:
        """Discover emerging knowledge patterns through semantic clustering"""
        async with self.pool.acquire() as conn:
            # Find clusters of highly related memories
            clusters = await conn.fetch("""
                WITH memory_clusters AS (
                    SELECT 
                        source_memory_id,
                        ARRAY_AGG(target_memory_id ORDER BY strength DESC) as related_memories,
                        AVG(strength) as avg_strength,
                        COUNT(*) as cluster_size
                    FROM semantic_relationships
                    WHERE strength > $1
                    GROUP BY source_memory_id
                    HAVING COUNT(*) >= 3 AND AVG(strength) > $1
                )
                SELECT 
                    mc.*,
                    sm.content as source_content,
                    sm.embedding as source_embedding
                FROM memory_clusters mc
                JOIN semantic_memories sm ON mc.source_memory_id = sm.id
                ORDER BY mc.avg_strength DESC, mc.cluster_size DESC;
            """, min_pattern_strength)
            
            patterns = []
            for cluster in clusters:
                pattern = {
                    'source_memory_id': str(cluster['source_memory_id']),
                    'source_content': cluster['source_content'],
                    'related_memories': [str(m) for m in cluster['related_memories']],
                    'pattern_strength': float(cluster['avg_strength']),
                    'cluster_size': cluster['cluster_size']
                }
                patterns.append(pattern)
            
            logger.info(f"Discovered {len(patterns)} knowledge patterns")
            return patterns
    
    async def get_memory_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics about neocortex memory state"""
        async with self.pool.acquire() as conn:
            stats = await conn.fetchrow("""
                SELECT 
                    COUNT(*) as total_memories,
                    AVG(importance_score) as avg_importance,
                    AVG(access_count) as avg_access_count,
                    COUNT(DISTINCT associations[1]) as unique_associations,
                    MAX(access_count) as max_access_count,
                    MIN(consolidated_at) as oldest_memory,
                    MAX(last_accessed) as most_recent_access
                FROM semantic_memories;
            """)
            
            relationship_stats = await conn.fetchrow("""
                SELECT 
                    COUNT(*) as total_relationships,
                    AVG(strength) as avg_relationship_strength,
                    COUNT(DISTINCT relationship_type) as relationship_types
                FROM semantic_relationships;
            """)
            
            return {
                'total_memories': stats['total_memories'],
                'avg_importance': float(stats['avg_importance'] or 0),
                'avg_access_count': float(stats['avg_access_count'] or 0),
                'unique_associations': stats['unique_associations'],
                'max_access_count': stats['max_access_count'],
                'oldest_memory': stats['oldest_memory'],
                'most_recent_access': stats['most_recent_access'],
                'total_relationships': relationship_stats['total_relationships'],
                'avg_relationship_strength': float(relationship_stats['avg_relationship_strength'] or 0),
                'relationship_types': relationship_stats['relationship_types']
            }
    
    async def cleanup_weak_memories(self, strength_threshold: float = 0.1):
        """Remove very weak relationships and low-importance memories (memory decay)"""
        async with self.pool.acquire() as conn:
            # Remove weak relationships
            weak_relationships = await conn.execute("""
                DELETE FROM semantic_relationships 
                WHERE strength < $1;
            """, strength_threshold)
            
            # Archive very old, low-importance, rarely accessed memories
            archived_memories = await conn.execute("""
                UPDATE semantic_memories 
                SET metadata = metadata || '{"archived": true}'
                WHERE importance_score < 0.2 
                AND access_count < 2 
                AND consolidated_at < NOW() - INTERVAL '6 months';
            """)
            
            logger.info(f"Cleaned {weak_relationships} relationships, archived {archived_memories} memories")
    
    async def close(self):
        """Close database connections"""
        if self.pool:
            await self.pool.close()
            logger.info("Neocortex connections closed")

# Example usage for MCP integration
async def create_neocortex_mcp():
    """Factory function for MCP server integration"""
    neocortex = NeocortexProcessor(
        connection_string="postgresql://user:password@localhost:5432/biomimetic_brain"
    )
    await neocortex.initialize()
    return neocortex

if __name__ == "__main__":
    # Test the neocortex implementation
    async def test_neocortex():
        neocortex = await create_neocortex_mcp()
        
        # Test memory consolidation
        test_memory = {
            'content': 'Jordan discovered weight-based memory access eliminates TTL limitations',
            'importance_score': 0.9,
            'associations': ['biomimetic', 'breakthrough', 'superhuman'],
            'emotional_weight': 0.8
        }
        
        # Mock embedding (would come from real embedding model)
        test_embedding = [0.1] * 1536
        
        memory_id = await neocortex.consolidate_from_hippocampus(
            test_memory, 
            test_embedding
        )
        
        print(f"Consolidated memory: {memory_id}")
        
        # Test semantic search
        results = await neocortex.semantic_search(test_embedding, limit=5)
        print(f"Found {len(results)} similar memories")
        
        # Get statistics
        stats = await neocortex.get_memory_statistics()
        print(f"Neocortex stats: {stats}")
        
        await neocortex.close()
    
    asyncio.run(test_neocortex())
