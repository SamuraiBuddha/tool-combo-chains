#!/usr/bin/env bash
# Install and configure MCP servers for Tool-Combo-Chains
# ----------------------------------------------------------------------
# Sets up the MCP (Model Context Protocol) servers required for the
# hybrid memory and tool combo chain functionality.

set -Eeuo pipefail

echo "🚀  Installing MCP servers for Tool-Combo-Chains..."

# ── PREPARE LOGGING ─────────────────────────────────────────────────────
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="${SCRIPT_DIR}/logs"
mkdir -p "${LOG_DIR}"

LOG_FILE="${LOG_DIR}/$(date '+%Y%m%d_%H%M%S')_install_mcps.log"
exec > >(tee -a "${LOG_FILE}") 2>&1

echo "📜  Writing full transcript to ${LOG_FILE}"

# ── CHECK ENVIRONMENT ──────────────────────────────────────────────────
if [[ ! -f .env ]]; then
    echo "❌  .env file not found. Please run:"
    echo "    cp .env.example .env && edit .env"
    exit 1
fi

echo "✅  Environment file found"

# ── INSTALL PYTHON DEPENDENCIES ───────────────────────────────────────
echo "🔧  Installing Python package..."
if command -v pip &>/dev/null; then
    pip install -e .
elif command -v pip3 &>/dev/null; then
    pip3 install -e .
else
    echo "❌  pip not found. Please install Python and pip first."
    exit 1
fi

echo "✅  Python package installed"

# ── START REQUIRED SERVICES ───────────────────────────────────────────
echo "🔧  Ensuring required services are running..."

# Check if docker compose is available
if command -v docker-compose &>/dev/null; then
    DC="docker-compose"
else
    DC="docker compose"
fi

# Start all services
echo "🚀  Starting PostgreSQL, Redis, and Qdrant..."
${DC} up -d

echo "⏳  Waiting for services to be ready..."
sleep 10

# Test connections
echo "🔍  Testing service connections..."

# Test PostgreSQL
if docker exec cognitive-postgres pg_isready -U cognitive >/dev/null 2>&1; then
    echo "✅  PostgreSQL is ready"
else
    echo "❌  PostgreSQL connection failed"
    exit 1
fi

# Test Redis
if docker exec cognitive-redis redis-cli ping >/dev/null 2>&1; then
    echo "✅  Redis is ready"
else
    echo "❌  Redis connection failed"
    exit 1
fi

# Test Qdrant
if curl -s http://localhost:6333/health >/dev/null 2>&1; then
    echo "✅  Qdrant is ready"
else
    echo "❌  Qdrant connection failed"
    exit 1
fi

# ── VERIFY ENVIRONMENT VARIABLES ──────────────────────────────────────
echo "🔍  Verifying environment configuration..."

source .env

if [[ -z "${DATABASE_URL:-}" ]]; then
    echo "❌  DATABASE_URL not set in .env"
    exit 1
fi

if [[ -z "${INSTANCE_ID:-}" ]]; then
    echo "❌  INSTANCE_ID not set in .env"
    exit 1
fi

if [[ -z "${EMBEDDING_API_URL:-}" ]]; then
    echo "❌  EMBEDDING_API_URL not set in .env"
    exit 1
fi

echo "✅  Environment variables verified"

# ── FINAL STATUS ───────────────────────────────────────────────────────
echo ""
echo "🎉  MCP servers installation complete!"
echo ""
echo "📊  Service Status:"
echo "   • PostgreSQL: Running (port 5432)"
echo "   • Redis: Running (port 6379)" 
echo "   • Qdrant: Running (ports 6333, 6334)"
echo ""
echo "🔗  Connection Details:"
echo "   • Database: ${DATABASE_URL}"
echo "   • Instance: ${INSTANCE_ID} (${INSTANCE_ROLE:-primary})"
echo "   • Embeddings: ${EMBEDDING_API_URL}"
echo ""
echo "📝  Next Steps:"
echo "   1. Configure your Claude Desktop with the provided config"
echo "   2. Test hybrid memory functionality"
echo "   3. Begin using tool combo chains!"
echo ""
echo "🏁  Setup complete - ready for 100x productivity amplification!"

# ── KEEP TERMINAL OPEN IF NON–INTERACTIVE ──────────────────────────────
if [[ $- != *i* && -t 1 ]]; then
    read -n 1 -s -r -p "Press any key to close …"
fi