#!/usr/bin/env bash
# Initialise (idempotently) the Tool‑Combo‑Chains PostgreSQL instance.
# --------------------------------------------------------------------
# Spins up/wakes up the Postgres container, waits for readiness, creates
# required extensions, and writes a full transcript to logs/<timestamp>_init.log
#
# The script is intentionally parameter‑driven so it can be reused across CI,
# dev laptops, and remote VMs without modification.

set -Eeuo pipefail

# ── USER‑TUNABLE DEFAULTS ─────────────────────────────────────────────
: "${PG_SERVICE:=cognitive-postgres}"     # Docker container / service name
: "${PG_USER:=cognitive}"
: "${PG_DB:=cognitive}"
: "${REQUIRED_EXTENSIONS:=vector age}"    # Space‑delimited list
: "${TIMEOUT:=45}"                        # Seconds to wait for pg_isready

# ── DISCOVER THE DOCKER COMPOSE CLI ───────────────────────────────────
if command -v docker-compose &>/dev/null; then
    DC="docker-compose"
else
    DC="docker compose"
fi

# ── PREPARE LOGGING ───────────────────────────────────────────────────
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="${SCRIPT_DIR}/logs"
mkdir -p "${LOG_DIR}"

LOG_FILE="${LOG_DIR}/$(date '+%Y%m%d_%H%M%S')_init.log"
exec > >(tee -a "${LOG_FILE}") 2>&1

echo "📜  Writing full transcript to ${LOG_FILE}"

# ── START / ATTACH TO THE CONTAINER ───────────────────────────────────
ALREADY_RUNNING=true
if ! docker ps -q -f name="^/${PG_SERVICE}$" | grep -q .; then
    ALREADY_RUNNING=false
    echo "🚀  ${PG_SERVICE} not running — starting via ${DC} up -d postgres"
    ${DC} up -d postgres
fi

# Ensure we clean up if the user hits Ctrl‑C *and* we were the ones who started it
cleanup() {
    if [[ "${ALREADY_RUNNING}" == false ]]; then
        echo "🧹  Stopping ${PG_SERVICE} (was started by this script)"
        docker stop "${PG_SERVICE}" >/dev/null
    fi
}
trap cleanup INT

# ── WAIT FOR HEALTHY STATUS ───────────────────────────────────────────
echo "⏳  Waiting up to ${TIMEOUT}s for PostgreSQL to accept connections …"
until docker exec "${PG_SERVICE}" pg_isready -U "${PG_USER}" -d "${PG_DB}" >/dev/null 2>&1; do
    (( TIMEOUT-- )) || {
        echo "❌  PostgreSQL failed to become ready in time."
        exit 1
    }
    sleep 1
_done

echo "✅  PostgreSQL is ready"

# ── CREATE REQUIRED EXTENSIONS (idempotent) ───────────────────────────
for EXT in ${REQUIRED_EXTENSIONS}; do
    echo "🔧  Ensuring extension '${EXT}' exists …"
    docker exec -i "${PG_SERVICE}" psql -U "${PG_USER}" -d "${PG_DB}" -c "CREATE EXTENSION IF NOT EXISTS \"${EXT}\";" >/dev/null
_done
echo "🎉  All extensions present"

# ── FIGURE OUT THE HOST‑MAPPED PORT ───────────────────────────────────
HOST_PORT=$(docker inspect -f '{{ (index .NetworkSettings.Ports "5432/tcp" 0).HostPort }}' "${PG_SERVICE}" 2>/dev/null || echo 5432)

# ── FINAL SUMMARY ─────────────────────────────────────────────────────

echo "\n🔗  Connection string (§ dev only — no password shown):"
echo "    postgresql://${PG_USER}@localhost:${HOST_PORT}/${PG_DB}"

echo "\nNext steps:"
echo "  1. cp .env.example .env && edit credentials"
echo "  2. ./scripts/install-mcps.sh"
echo "  3. Run migrations / seed data"

echo "\n🟢  Database initialisation complete!"

# ── KEEP TERMINAL OPEN IF NON‑INTERACTIVE ─────────────────────────────
if [[ $- != *i* && -t 1 ]]; then
    read -n 1 -s -r -p "Press any key to close …"
fi
