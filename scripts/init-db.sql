-- Tool Combo Chains: Cognitive Database Initialization
-- PostgreSQL 16 with pgvector + Apache AGE

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS age;
CREATE EXTENSION IF NOT EXISTS pg_trgm; -- For text similarity
CREATE EXTENSION IF NOT EXISTS btree_gin; -- For composite indexes

-- Create the cognitive graph
SELECT age_create_graph('cognitive_graph');

-- Main hybrid memory table
CREATE TABLE memory_entities (
    id BIGSERIAL PRIMARY KEY,
    entity_type VARCHAR(100) NOT NULL,
    name VARCHAR(255) NOT NULL,
    content TEXT,
    embedding vector(768), -- For semantic similarity
    metadata JSONB DEFAULT '{}',
    importance_score FLOAT DEFAULT 0.5,
    access_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    created_by VARCHAR(50), -- Which Claude instance
    CONSTRAINT unique_entity_name UNIQUE (entity_type, name)
);

-- Observations table (append-only for temporal integrity)
CREATE TABLE observations (
    id BIGSERIAL PRIMARY KEY,
    entity_id BIGINT REFERENCES memory_entities(id) ON DELETE CASCADE,
    observation TEXT NOT NULL,
    embedding vector(768),
    timestamp TIMESTAMP DEFAULT NOW(),
    source VARCHAR(50), -- Which Claude instance or tool
    confidence FLOAT DEFAULT 1.0
);

-- Relationships table (for quick access without Cypher)
CREATE TABLE relationships (
    id BIGSERIAL PRIMARY KEY,
    from_entity_id BIGINT REFERENCES memory_entities(id) ON DELETE CASCADE,
    to_entity_id BIGINT REFERENCES memory_entities(id) ON DELETE CASCADE,
    relationship_type VARCHAR(100) NOT NULL,
    properties JSONB DEFAULT '{}',
    strength FLOAT DEFAULT 1.0,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Cached computations table
CREATE TABLE computation_cache (
    id BIGSERIAL PRIMARY KEY,
    computation_type VARCHAR(100) NOT NULL,
    input_hash VARCHAR(64) NOT NULL, -- SHA256 of input
    result JSONB NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP,
    CONSTRAINT unique_computation UNIQUE (computation_type, input_hash)
);

-- Multi-Claude consensus table
CREATE TABLE consensus_log (
    id BIGSERIAL PRIMARY KEY,
    operation_id VARCHAR(64) NOT NULL, -- UUID for the operation
    instance_id VARCHAR(50) NOT NULL, -- Melchior-001, etc
    vote VARCHAR(20) NOT NULL, -- APPROVE, REJECT, ABSTAIN
    reasoning TEXT,
    timestamp TIMESTAMP DEFAULT NOW(),
    CONSTRAINT unique_instance_vote UNIQUE (operation_id, instance_id)
);

-- Create indexes for performance
CREATE INDEX idx_entities_embedding ON memory_entities USING hnsw (embedding vector_cosine_ops);
CREATE INDEX idx_entities_type ON memory_entities(entity_type);
CREATE INDEX idx_entities_metadata ON memory_entities USING gin (metadata);
CREATE INDEX idx_entities_importance ON memory_entities(importance_score DESC);

CREATE INDEX idx_observations_entity ON observations(entity_id);
CREATE INDEX idx_observations_embedding ON observations USING hnsw (embedding vector_cosine_ops);
CREATE INDEX idx_observations_timestamp ON observations(timestamp DESC);

CREATE INDEX idx_relationships_from ON relationships(from_entity_id);
CREATE INDEX idx_relationships_to ON relationships(to_entity_id);
CREATE INDEX idx_relationships_type ON relationships(relationship_type);

CREATE INDEX idx_cache_lookup ON computation_cache(computation_type, input_hash);
CREATE INDEX idx_cache_expiry ON computation_cache(expires_at) WHERE expires_at IS NOT NULL;

-- Hybrid search function
CREATE OR REPLACE FUNCTION find_related_memories(
    query_embedding vector(768),
    similarity_threshold FLOAT DEFAULT 0.7,
    max_results INTEGER DEFAULT 20,
    include_graph_expansion BOOLEAN DEFAULT TRUE
) RETURNS TABLE (
    entity_id BIGINT,
    entity_type VARCHAR,
    name VARCHAR,
    content TEXT,
    similarity FLOAT,
    match_type VARCHAR,
    path_length INTEGER
) AS $$
BEGIN
    RETURN QUERY
    WITH vector_matches AS (
        -- First: Find semantically similar entities
        SELECT 
            e.id,
            e.entity_type,
            e.name,
            e.content,
            1 - (e.embedding <=> query_embedding) as similarity,
            'direct' as match_type,
            0 as path_length
        FROM memory_entities e
        WHERE e.embedding IS NOT NULL
        AND 1 - (e.embedding <=> query_embedding) > similarity_threshold
        ORDER BY similarity DESC
        LIMIT max_results
    ),
    graph_expansion AS (
        -- Then: Expand through graph relationships if requested
        SELECT DISTINCT
            e2.id,
            e2.entity_type,
            e2.name,
            e2.content,
            vm.similarity * r.strength * 0.8 as similarity, -- Decay factor
            'related' as match_type,
            1 as path_length
        FROM vector_matches vm
        JOIN relationships r ON vm.id = r.from_entity_id
        JOIN memory_entities e2 ON r.to_entity_id = e2.id
        WHERE include_graph_expansion = TRUE
        AND r.strength > 0.5
    )
    -- Combine and rank results
    SELECT * FROM (
        SELECT * FROM vector_matches
        UNION ALL
        SELECT * FROM graph_expansion
    ) combined
    ORDER BY similarity DESC, path_length ASC
    LIMIT max_results;
END;
$$ LANGUAGE plpgsql;

-- Semantic deduplication function
CREATE OR REPLACE FUNCTION find_duplicate_memories(
    similarity_threshold FLOAT DEFAULT 0.95
) RETURNS TABLE (
    entity1_id BIGINT,
    entity2_id BIGINT,
    similarity FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        e1.id as entity1_id,
        e2.id as entity2_id,
        1 - (e1.embedding <=> e2.embedding) as similarity
    FROM memory_entities e1
    JOIN memory_entities e2 ON e1.id < e2.id
    WHERE e1.embedding IS NOT NULL 
    AND e2.embedding IS NOT NULL
    AND 1 - (e1.embedding <=> e2.embedding) > similarity_threshold
    AND e1.entity_type = e2.entity_type
    ORDER BY similarity DESC;
END;
$$ LANGUAGE plpgsql;

-- Update timestamp trigger
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_entities_updated_at
    BEFORE UPDATE ON memory_entities
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

-- Access tracking function
CREATE OR REPLACE FUNCTION track_access(entity_id BIGINT)
RETURNS VOID AS $$
BEGIN
    UPDATE memory_entities 
    SET access_count = access_count + 1
    WHERE id = entity_id;
END;
$$ LANGUAGE plpgsql;

-- Initial data: System entities
INSERT INTO memory_entities (entity_type, name, content, created_by) VALUES
('System_Protocol', 'Tool_Combo_Chain_Protocol', 
 'Core protocol for cognitive amplification using hybrid vector-graph memory', 
 'System'),
('System_Info', 'Database_Version', 
 '{"version": "1.0.0", "schema_date": "2025-06-26", "extensions": ["vector", "age", "pg_trgm", "btree_gin"]}', 
 'System');

-- Grant permissions (adjust as needed)
GRANT ALL ON ALL TABLES IN SCHEMA public TO cognitive;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO cognitive;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO cognitive;
