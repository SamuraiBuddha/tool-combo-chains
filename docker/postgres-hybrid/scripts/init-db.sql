-- Hybrid Memory System Database Initialization
-- PostgreSQL 16 with pgvector and Apache AGE
-- Created: 2025-07-05 for hybrid memory system

-- Create the database if it doesn't exist
-- (PostgreSQL will create 'cognitive' database from environment variables)

-- Connect to the cognitive database
\c cognitive;

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS age;

-- Load AGE into the current session
LOAD 'age';
SET search_path = ag_catalog, "$user", public;

-- Create AGE graph for memory relationships
SELECT create_graph('memory_graph');

-- Memory entities table with vector embeddings
CREATE TABLE IF NOT EXISTS memory_entities (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    entity_type VARCHAR(100) NOT NULL,
    content TEXT,
    embedding vector(1536), -- OpenAI embeddings size
    importance_weight FLOAT DEFAULT 1.0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Memory observations table
CREATE TABLE IF NOT EXISTS memory_observations (
    id SERIAL PRIMARY KEY,
    entity_id INTEGER REFERENCES memory_entities(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    embedding vector(1536),
    timestamp TIMESTAMP DEFAULT NOW(),
    source VARCHAR(100),
    confidence FLOAT DEFAULT 1.0
);

-- Memory relations table for graph relationships
CREATE TABLE IF NOT EXISTS memory_relations (
    id SERIAL PRIMARY KEY,
    from_entity_id INTEGER REFERENCES memory_entities(id) ON DELETE CASCADE,
    to_entity_id INTEGER REFERENCES memory_entities(id) ON DELETE CASCADE,
    relation_type VARCHAR(100) NOT NULL,
    weight FLOAT DEFAULT 1.0,
    created_at TIMESTAMP DEFAULT NOW(),
    properties JSONB DEFAULT '{}'::jsonb,
    UNIQUE(from_entity_id, to_entity_id, relation_type)
);

-- Memory stats table for system metrics
CREATE TABLE IF NOT EXISTS memory_stats (
    id SERIAL PRIMARY KEY,
    stat_name VARCHAR(100) UNIQUE NOT NULL,
    stat_value JSONB,
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_memory_entities_type ON memory_entities(entity_type);
CREATE INDEX IF NOT EXISTS idx_memory_entities_embedding ON memory_entities USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX IF NOT EXISTS idx_memory_entities_name ON memory_entities(name);
CREATE INDEX IF NOT EXISTS idx_memory_observations_entity ON memory_observations(entity_id);
CREATE INDEX IF NOT EXISTS idx_memory_observations_embedding ON memory_observations USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX IF NOT EXISTS idx_memory_relations_from ON memory_relations(from_entity_id);
CREATE INDEX IF NOT EXISTS idx_memory_relations_to ON memory_relations(to_entity_id);
CREATE INDEX IF NOT EXISTS idx_memory_relations_type ON memory_relations(relation_type);

-- Insert initial stats
INSERT INTO memory_stats (stat_name, stat_value) VALUES 
('system_initialized', '{"timestamp": "' || NOW() || '", "version": "1.0"}'),
('total_entities', '0'),
('total_observations', '0'),
('total_relations', '0')
ON CONFLICT (stat_name) DO UPDATE SET 
    stat_value = EXCLUDED.stat_value,
    updated_at = NOW();

-- Create update trigger for timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply triggers
CREATE TRIGGER update_memory_entities_updated_at BEFORE UPDATE ON memory_entities FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Grant permissions to cognitive user
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO cognitive;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO cognitive;
GRANT USAGE ON SCHEMA ag_catalog TO cognitive;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA ag_catalog TO cognitive;

-- Log initialization completion
INSERT INTO memory_stats (stat_name, stat_value) VALUES 
('last_initialization', '{"timestamp": "' || NOW() || '", "status": "completed"}')
ON CONFLICT (stat_name) DO UPDATE SET 
    stat_value = EXCLUDED.stat_value,
    updated_at = NOW();

\echo 'Hybrid Memory Database initialization completed successfully!'
