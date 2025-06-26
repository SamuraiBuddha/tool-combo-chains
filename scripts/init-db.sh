#!/bin/bash
# Initialize the Tool Combo Chains database

set -e

echo "🚀 Tool Combo Chains Database Initialization"
echo "=========================================="

# Check if docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if postgres container is running
if [ ! "$(docker ps -q -f name=cognitive-postgres)" ]; then
    echo "⚠️  PostgreSQL container not running. Starting it..."
    docker-compose up -d postgres
    echo "⏳ Waiting for PostgreSQL to be ready..."
    sleep 5
fi

# Wait for postgres to be healthy
echo "🔍 Checking PostgreSQL health..."
timeout=30
while [ $timeout -gt 0 ]; do
    if docker exec cognitive-postgres pg_isready -U cognitive > /dev/null 2>&1; then
        echo "✅ PostgreSQL is ready!"
        break
    fi
    echo "⏳ Waiting for PostgreSQL... ($timeout seconds remaining)"
    sleep 1
    timeout=$((timeout - 1))
done

if [ $timeout -eq 0 ]; then
    echo "❌ PostgreSQL failed to start in time"
    exit 1
fi

# The init-db.sql is automatically run by PostgreSQL on first startup
# But we'll check if extensions are installed to verify
echo "🔍 Verifying database extensions..."
docker exec cognitive-postgres psql -U cognitive -d cognitive -c "SELECT extname FROM pg_extension WHERE extname IN ('vector', 'age');" | grep -E "(vector|age)" > /dev/null

if [ $? -eq 0 ]; then
    echo "✅ Database extensions installed successfully!"
else
    echo "⚠️  Extensions not found. Running manual initialization..."
    docker exec -i cognitive-postgres psql -U cognitive -d cognitive < scripts/init-db.sql
fi

echo ""
echo "🎉 Database initialization complete!"
echo ""
echo "📊 Database Info:"
echo "  Host: localhost"
echo "  Port: 5432"
echo "  Database: cognitive"
echo "  User: cognitive"
echo "  Password: (see .env file)"
echo ""
echo "🔗 Connection string:"
echo "  postgresql://cognitive:password@localhost:5432/cognitive"
echo ""
echo "Next steps:"
echo "  1. Copy .env.example to .env and update values"
echo "  2. Install MCP servers: ./scripts/install-mcps.sh"
echo "  3. Start using hybrid memory!"
