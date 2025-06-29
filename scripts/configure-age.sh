#!/bin/bash
# Fix AGE configuration in PostgreSQL

echo "🔧 Configuring PostgreSQL for Apache AGE..."

# Update postgresql.conf for AGE
docker exec cognitive-postgres sh -c "cat >> /var/lib/postgresql/data/postgresql.conf << 'EOL'

# Apache AGE Configuration
shared_preload_libraries = 'age'
search_path = '\"\$user\", public, ag_catalog'
EOL"

# Create a setup script that runs on every connection
docker exec cognitive-postgres psql -U cognitive -d cognitive << 'EOF'
-- Ensure AGE is loaded
CREATE EXTENSION IF NOT EXISTS age CASCADE;

-- Set default search path for the database
ALTER DATABASE cognitive SET search_path = "$user", public, ag_catalog;

-- Create the cognitive graph if it doesn't exist
DO $$
BEGIN
    PERFORM create_graph('cognitive_graph');
EXCEPTION
    WHEN duplicate_object THEN
        RAISE NOTICE 'Graph cognitive_graph already exists';
END
$$;

-- Verify setup
SELECT graphid, name FROM ag_catalog.ag_graph;
EOF

echo "✅ AGE configuration complete!"
echo ""
echo "🔄 Restarting PostgreSQL to apply settings..."
docker-compose restart postgres

echo ""
echo "⏳ Waiting for PostgreSQL to be ready..."
sleep 10

echo ""
echo "🧪 Testing AGE functionality..."
docker exec cognitive-postgres psql -U cognitive -d cognitive -c "SELECT * FROM ag_catalog.ag_graph;"

echo ""
echo "✅ Apache AGE is now configured and ready to use!"
