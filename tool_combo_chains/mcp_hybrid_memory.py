"""
MCP Hybrid Memory Server
Cognitive Amplification Stack - 3-tier memory architecture
"""
import os
import json
import asyncio
import hashlib
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path

import asyncpg
import redis.asyncio as redis
import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import httpx
from pydantic import BaseModel
import structlog
from dotenv import load_dotenv

from mcp.server import Server
from mcp.server.models import InitializationOptions, ServerCapabilities
import mcp.server.stdio
import mcp.types as types

# Load environment variables - fix path issue
env_path = Path(__file__).parent.parent / '.env'
if env_path.exists():
    load_dotenv(env_path)
else:
    load_dotenv()  # Try default location

# Configure structured logging
logger = structlog.get_logger()

# Configuration - Updated with correct password fallback
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://cognitive:7HY25Pvj5FAW9sH8nJ8MNc4MRnwLnHIQppSFf7aH@127.0.0.1:5432/cognitive")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
EMBEDDING_API_URL = os.getenv("EMBEDDING_API_URL", "http://localhost:1234/v1/embeddings")
INSTANCE_ID = os.getenv("INSTANCE_ID", "Melchior-001")
INSTANCE_ROLE = os.getenv("INSTANCE_ROLE", "primary")

# Constants
VECTOR_DIM = 768  # Granite embeddings
COLLECTION_NAME = "cognitive_memory"
CACHE_TTL = int(os.getenv("CACHE_TTL", "3600"))
SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.7"))

# Debug: Print what we loaded
logger.info("Environment loaded", 
    database_url_set=bool(os.getenv("DATABASE_URL")),
    postgres_password_set=bool(os.getenv("POSTGRES_PASSWORD")),
    env_path=str(env_path),
    env_exists=env_path.exists()
)

class MemoryEntity(BaseModel):
    """Memory entity structure"""
    entity_type: str
    name: str
    content: str
    metadata: Dict[str, Any] = {}
    observations: List[str] = []

class HybridMemoryServer:
    """Three-tier cognitive memory system"""
    
    def __init__(self):
        self.db_pool: Optional[asyncpg.Pool] = None
        self.redis_client: Optional[redis.Redis] = None
        self.qdrant_client: Optional[QdrantClient] = None
        self.http_client: Optional[httpx.AsyncClient] = None
        # Create server with proper initialization
        self.server = Server("hybrid-memory")
        self.setup_tools()
    
    def setup_tools(self):
        """Register MCP tools"""
        
        @self.server.list_tools()
        async def list_tools() -> List[types.Tool]:
            return [
                types.Tool(
                    name="store_memory",
                    description="Store a memory entity with vector embedding and graph relationships",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "entity_type": {"type": "string"},
                            "name": {"type": "string"},
                            "content": {"type": "string"},
                            "metadata": {"type": "object"},
                            "observations": {
                                "type": "array",
                                "items": {"type": "string"}
                            }
                        },
                        "required": ["entity_type", "name", "content"]
                    }
                ),
                types.Tool(
                    name="recall_memory",
                    description="Recall memories using hybrid vector-graph search",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {"type": "string"},
                            "entity_type": {"type": "string"},
                            "include_graph": {"type": "boolean", "default": True},
                            "max_results": {"type": "integer", "default": 20}
                        },
                        "required": ["query"]
                    }
                ),
                types.Tool(
                    name="add_observations",
                    description="Add observations to an existing memory entity",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "entity_name": {"type": "string"},
                            "observations": {
                                "type": "array",
                                "items": {"type": "string"}
                            }
                        },
                        "required": ["entity_name", "observations"]
                    }
                ),
                types.Tool(
                    name="create_relationship",
                    description="Create a relationship between two memory entities",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "from_entity": {"type": "string"},
                            "to_entity": {"type": "string"},
                            "relationship_type": {"type": "string"},
                            "properties": {"type": "object"}
                        },
                        "required": ["from_entity", "to_entity", "relationship_type"]
                    }
                ),
                types.Tool(
                    name="find_patterns",
                    description="Find patterns across memories using clustering",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "entity_type": {"type": "string"},
                            "min_cluster_size": {"type": "integer", "default": 3}
                        }
                    }
                ),
                types.Tool(
                    name="get_memory_stats",
                    description="Get statistics about the memory system",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                )
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
            try:
                logger.info(f"Tool called: {name}", instance=INSTANCE_ID, args=arguments)
                
                if name == "store_memory":
                    result = await self.store_memory(**arguments)
                elif name == "recall_memory":
                    result = await self.recall_memory(**arguments)
                elif name == "add_observations":
                    result = await self.add_observations(**arguments)
                elif name == "create_relationship":
                    result = await self.create_relationship(**arguments)
                elif name == "find_patterns":
                    result = await self.find_patterns(**arguments)
                elif name == "get_memory_stats":
                    result = await self.get_memory_stats()
                else:
                    result = {"error": f"Unknown tool: {name}"}
                
                return [types.TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )]
                
            except Exception as e:
                logger.error(f"Tool error: {name}", error=str(e), instance=INSTANCE_ID)
                return [types.TextContent(
                    type="text",
                    text=json.dumps({"error": str(e)})
                )]
    
    async def initialize(self):
        """Initialize all connections"""
        try:
            # PostgreSQL connection pool
            logger.info("Connecting to PostgreSQL", url=DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'unknown')
            self.db_pool = await asyncpg.create_pool(DATABASE_URL, min_size=5, max_size=20)
            
            # Redis connection
            self.redis_client = await redis.from_url(REDIS_URL, decode_responses=True)
            
            # Qdrant client
            self.qdrant_client = QdrantClient(url=QDRANT_URL)
            
            # Create Qdrant collection if it doesn't exist
            try:
                self.qdrant_client.get_collection(COLLECTION_NAME)
            except:
                self.qdrant_client.create_collection(
                    collection_name=COLLECTION_NAME,
                    vectors_config=VectorParams(size=VECTOR_DIM, distance=Distance.COSINE)
                )
            
            # HTTP client for embeddings
            self.http_client = httpx.AsyncClient(timeout=30.0)
            
            logger.info("Hybrid Memory Server initialized", 
                        instance=INSTANCE_ID, 
                        role=INSTANCE_ROLE,
                        postgres="connected",
                        redis="connected", 
                        qdrant="connected")
            
        except Exception as e:
            logger.error("Failed to initialize", error=str(e))
            raise
    
    async def cleanup(self):
        """Clean up connections"""
        if self.db_pool:
            await self.db_pool.close()
        if self.redis_client:
            await self.redis_client.close()
        if self.http_client:
            await self.http_client.aclose()
    
    async def get_embedding(self, text: str) -> List[float]:
        """Get embedding from LM Studio or cache"""
        # Check cache first
        cache_key = f"emb:{hashlib.sha256(text.encode()).hexdigest()[:16]}"
        cached = await self.redis_client.get(cache_key)
        if cached:
            return json.loads(cached)
        
        # Call embedding API
        response = await self.http_client.post(
            EMBEDDING_API_URL,
            json={"input": text, "model": "granite"}
        )
        data = response.json()
        embedding = data["data"][0]["embedding"]
        
        # Cache for future use
        await self.redis_client.setex(cache_key, CACHE_TTL, json.dumps(embedding))
        
        return embedding
    
    async def store_memory(self, entity_type: str, name: str, content: str, 
                          metadata: Dict = None, observations: List[str] = None) -> Dict:
        """Store memory in all three tiers"""
        metadata = metadata or {}
        observations = observations or []
        
        # Get embedding
        embedding = await self.get_embedding(content)
        async def store_memory(self, entity_type: str, name: str, content: str,
                       metadata: Dict = None, observations: List[str] = None) -> Dict:
    """Store memory in all three tiers"""
    metadata = metadata or {}
    observations = observations or []
    
    # Get embedding
    embedding = await self.get_embedding(content)
    
    # Convert embedding list to pgvector string format
    embedding_str = f"[{','.join(map(str, embedding))}]"
    
    async with self.db_pool.acquire() as conn:
        # Store in PostgreSQL
        entity_id = await conn.fetchval("""
            INSERT INTO memory_entities (entity_type, name, content, embedding, metadata, created_by)
            VALUES ($1, $2, $3, $4, $5, $6)
            ON CONFLICT (entity_type, name) 
            DO UPDATE SET content = $3, embedding = $4, metadata = $5, updated_at = NOW()
            RETURNING id
        """, entity_type, name, content, embedding_str, json.dumps(metadata), INSTANCE_ID)
        
        # Add observations
        for obs in observations:
            obs_embedding = await self.get_embedding(obs)
            obs_embedding_str = f"[{','.join(map(str, obs_embedding))}]"
            await conn.execute("""
                INSERT INTO observations (entity_id, observation, embedding, source)
                VALUES ($1, $2, $3, $4)
            """, entity_id, obs, obs_embedding_str, INSTANCE_ID)
        async with self.db_pool.acquire() as conn:
            # Store in PostgreSQL
            entity_id = await conn.fetchval("""
                INSERT INTO memory_entities (entity_type, name, content, embedding, metadata, created_by)
                VALUES ($1, $2, $3, $4, $5, $6)
                ON CONFLICT (entity_type, name) 
                DO UPDATE SET content = $3, embedding = $4, metadata = $5, updated_at = NOW()
                RETURNING id
            """, entity_type, name, content, embedding, json.dumps(metadata), INSTANCE_ID)
            
            # Add observations
            for obs in observations:
                obs_embedding = await self.get_embedding(obs)
                await conn.execute("""
                    INSERT INTO observations (entity_id, observation, embedding, source)
                    VALUES ($1, $2, $3, $4)
                """, entity_id, obs, obs_embedding, INSTANCE_ID)
        
        # Store in Qdrant for fast vector search
        self.qdrant_client.upsert(
            collection_name=COLLECTION_NAME,
            points=[PointStruct(
                id=entity_id,
                vector=embedding,
                payload={
                    "entity_type": entity_type,
                    "name": name,
                    "created_by": INSTANCE_ID,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )]
        )
        
        # Invalidate related caches
        await self.redis_client.delete(f"recall:{entity_type}:*")
        
        return {
            "entity_id": entity_id,
            "entity_type": entity_type,
            "name": name,
            "stored_by": INSTANCE_ID,
            "vector_indexed": True,
            "graph_stored": True
        }
    
    async def recall_memory(self, query: str, entity_type: str = None, 
                           include_graph: bool = True, max_results: int = 20) -> Dict:
        """Hybrid vector-graph memory recall"""
        # Check cache
        cache_key = f"recall:{entity_type or 'all'}:{hashlib.sha256(query.encode()).hexdigest()[:16]}"
        cached = await self.redis_client.get(cache_key)
        if cached:
            return json.loads(cached)
        
        # Get query embedding
        query_embedding = await self.get_embedding(query)
        
        # 1. Vector search in Qdrant (fast)
        search_filter = {"entity_type": entity_type} if entity_type else None
        vector_results = self.qdrant_client.search(
            collection_name=COLLECTION_NAME,
            query_vector=query_embedding,
            query_filter=search_filter,
            limit=max_results
        )
        
        # Extract entity IDs and scores
        vector_matches = {
            point.id: {
                "score": point.score,
                "payload": point.payload
            } for point in vector_results
        }
        
        if not vector_matches:
            return {"results": [], "source": "none"}
        
        # 2. Enhance with PostgreSQL data and graph expansion
        async with self.db_pool.acquire() as conn:
            # Get full entity data
            entity_ids = list(vector_matches.keys())
            entities = await conn.fetch("""
                SELECT id, entity_type, name, content, metadata, importance_score
                FROM memory_entities
                WHERE id = ANY($1)
            """, entity_ids)
            
            # Build results
            results = []
            for entity in entities:
                result = {
                    "entity_id": entity["id"],
                    "entity_type": entity["entity_type"],
                    "name": entity["name"],
                    "content": entity["content"],
                    "metadata": json.loads(entity["metadata"]) if entity["metadata"] else {},
                    "similarity": vector_matches[entity["id"]]["score"],
                    "importance": entity["importance_score"],
                    "match_type": "direct"
                }
                
                # Get observations
                observations = await conn.fetch("""
                    SELECT observation, timestamp, source
                    FROM observations
                    WHERE entity_id = $1
                    ORDER BY timestamp DESC
                    LIMIT 10
                """, entity["id"])
                
                result["observations"] = [
                    {
                        "text": obs["observation"],
                        "timestamp": obs["timestamp"].isoformat(),
                        "source": obs["source"]
                    } for obs in observations
                ]
                
                results.append(result)
            
            # 3. Graph expansion if requested
            if include_graph and entity_ids:
                related = await conn.fetch("""
                    SELECT DISTINCT e2.*, r.relationship_type, r.strength
                    FROM relationships r
                    JOIN memory_entities e2 ON r.to_entity_id = e2.id
                    WHERE r.from_entity_id = ANY($1)
                    AND r.strength > 0.5
                    ORDER BY r.strength DESC
                    LIMIT $2
                """, entity_ids, max_results // 2)
                
                for rel in related:
                    if rel["id"] not in vector_matches:
                        results.append({
                            "entity_id": rel["id"],
                            "entity_type": rel["entity_type"],
                            "name": rel["name"],
                            "content": rel["content"],
                            "metadata": json.loads(rel["metadata"]) if rel["metadata"] else {},
                            "similarity": 0.0,  # No direct similarity
                            "importance": rel["importance_score"],
                            "match_type": "related",
                            "relationship": rel["relationship_type"],
                            "relationship_strength": float(rel["strength"])
                        })
        
        # Sort by combined score
        results.sort(key=lambda x: x["similarity"] * 0.7 + x["importance"] * 0.3, reverse=True)
        
        # Cache the results
        response = {
            "query": query,
            "results": results[:max_results],
            "total_found": len(results),
            "search_method": "hybrid",
            "instance": INSTANCE_ID
        }
        await self.redis_client.setex(cache_key, CACHE_TTL // 2, json.dumps(response))
        
        return response
    
    async def add_observations(self, entity_name: str, observations: List[str]) -> Dict:
        """Add observations to existing entity"""
        async with self.db_pool.acquire() as conn:
            # Find entity
            entity = await conn.fetchrow("""
                SELECT id FROM memory_entities WHERE name = $1
            """, entity_name)
            
            if not entity:
                return {"error": f"Entity '{entity_name}' not found"}
            
            # Add observations
            added = []
            for obs in observations:
                obs_embedding = await self.get_embedding(obs)
                await conn.execute("""
                    INSERT INTO observations (entity_id, observation, embedding, source)
                    VALUES ($1, $2, $3, $4)
                """, entity["id"], obs, obs_embedding, INSTANCE_ID)
                added.append(obs)
            
            # Update access count
            await conn.execute("""
                UPDATE memory_entities 
                SET access_count = access_count + 1 
                WHERE id = $1
            """, entity["id"])
        
        # Invalidate caches
        await self.redis_client.delete(f"recall:*{entity_name}*")
        
        return {
            "entity_name": entity_name,
            "observations_added": len(added),
            "source": INSTANCE_ID
        }
    
    async def create_relationship(self, from_entity: str, to_entity: str, 
                                 relationship_type: str, properties: Dict = None) -> Dict:
        """Create relationship between entities"""
        properties = properties or {}
        
        async with self.db_pool.acquire() as conn:
            # Find entities
            from_id = await conn.fetchval("""
                SELECT id FROM memory_entities WHERE name = $1
            """, from_entity)
            
            to_id = await conn.fetchval("""
                SELECT id FROM memory_entities WHERE name = $1
            """, to_entity)
            
            if not from_id or not to_id:
                return {"error": "One or both entities not found"}
            
            # Create relationship
            rel_id = await conn.fetchval("""
                INSERT INTO relationships (from_entity_id, to_entity_id, relationship_type, properties)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT DO NOTHING
                RETURNING id
            """, from_id, to_id, relationship_type, json.dumps(properties))
        
        return {
            "relationship_id": rel_id,
            "from": from_entity,
            "to": to_entity,
            "type": relationship_type,
            "created_by": INSTANCE_ID
        }
    
    async def find_patterns(self, entity_type: str = None, min_cluster_size: int = 3) -> Dict:
        """Find patterns using vector clustering"""
        # This is a simplified version - in production you'd use proper clustering
        filter_cond = {"entity_type": entity_type} if entity_type else None
        
        # Get all vectors from Qdrant
        all_points = self.qdrant_client.scroll(
            collection_name=COLLECTION_NAME,
            scroll_filter=filter_cond,
            limit=1000
        )[0]
        
        if len(all_points) < min_cluster_size:
            return {"patterns": [], "message": "Not enough data for pattern analysis"}
        
        # Simple clustering by similarity
        clusters = []
        used_ids = set()
        
        for point in all_points:
            if point.id in used_ids:
                continue
                
            # Find similar points
            similar = self.qdrant_client.search(
                collection_name=COLLECTION_NAME,
                query_vector=point.vector,
                query_filter=filter_cond,
                limit=min_cluster_size * 2
            )
            
            cluster = []
            for sim_point in similar:
                if sim_point.score > 0.85 and sim_point.id not in used_ids:
                    cluster.append({
                        "id": sim_point.id,
                        "name": sim_point.payload.get("name"),
                        "score": sim_point.score
                    })
                    used_ids.add(sim_point.id)
            
            if len(cluster) >= min_cluster_size:
                clusters.append(cluster)
        
        return {
            "patterns_found": len(clusters),
            "clusters": clusters[:10],  # Top 10 clusters
            "analysis_by": INSTANCE_ID
        }
    
    async def get_memory_stats(self) -> Dict:
        """Get system statistics"""
        async with self.db_pool.acquire() as conn:
            stats = await conn.fetchrow("""
                SELECT 
                    COUNT(*) as total_entities,
                    COUNT(DISTINCT entity_type) as entity_types,
                    AVG(access_count) as avg_access_count,
                    MAX(access_count) as max_access_count
                FROM memory_entities
            """)
            
            obs_count = await conn.fetchval("""
                SELECT COUNT(*) FROM observations
            """)
            
            rel_count = await conn.fetchval("""
                SELECT COUNT(*) FROM relationships
            """)
        
        # Get Qdrant stats
        qdrant_info = self.qdrant_client.get_collection(COLLECTION_NAME)
        
        # Get Redis info
        redis_info = await self.redis_client.info()
        
        return {
            "postgres": {
                "total_entities": stats["total_entities"],
                "entity_types": stats["entity_types"],
                "total_observations": obs_count,
                "total_relationships": rel_count,
                "avg_access_count": float(stats["avg_access_count"] or 0),
                "max_access_count": stats["max_access_count"]
            },
            "qdrant": {
                "vectors_count": qdrant_info.points_count,
                "indexed_vectors": qdrant_info.indexed_vectors_count
            },
            "redis": {
                "used_memory": redis_info["used_memory_human"],
                "connected_clients": redis_info["connected_clients"],
                "total_commands_processed": redis_info["total_commands_processed"]
            },
            "instance": {
                "id": INSTANCE_ID,
                "role": INSTANCE_ROLE
            }
        }

async def main():
    """Main entry point"""
    server = HybridMemoryServer()
    
    try:
        await server.initialize()
        logger.info("Starting Hybrid Memory MCP Server", instance=INSTANCE_ID)
        
        # Initialize options
        init_options = InitializationOptions(
            server_name="hybrid-memory",
            server_version="0.1.0",
            capabilities=ServerCapabilities()
        )
        
        # Run the server
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await server.server.run(
                read_stream, 
                write_stream,
                init_options
            )
            
    except KeyboardInterrupt:
        logger.info("Shutting down gracefully")
    except Exception as e:
        logger.error("Server error", error=str(e))
        raise
    finally:
        await server.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
