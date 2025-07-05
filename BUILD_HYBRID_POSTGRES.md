# Building PostgreSQL with pgvector + Apache AGE

This guide shows how to build and use the full hybrid memory system with both vector search (pgvector) and graph capabilities (Apache AGE).

## 🚀 Quick Start

### 1. Pull the latest changes:
```bash
git pull
```

### 2. Stop and remove existing containers:
```bash
docker-compose down -v
```
**Note**: The `-v` flag removes volumes. This will delete existing data!

### 3. Build the custom PostgreSQL image:
```bash
docker-compose build postgres
```
This will:
- Build PostgreSQL 16 with pgvector extension
- Add Apache AGE graph extension
- Configure for hybrid memory operations

### 4. Start all services:
```bash
docker-compose up -d
```

### 5. Verify the build:
```bash
# Check if containers are running
docker ps

# Verify both extensions are installed
docker exec cognitive-postgres psql -U cognitive -d cognitive -c "\dx"
```

You should see both `vector` and `age` extensions listed!

### 6. Restart Claude Desktop
Close and reopen Claude Desktop to use the new hybrid memory system.

## 🧪 Testing the Hybrid System

Once everything is running, test both vector and graph features:

```bash
# Test vector extension
docker exec cognitive-postgres psql -U cognitive -d cognitive -c "\dx"

# Test AGE extension
docker exec cognitive-postgres psql -U cognitive -d cognitive -c "SELECT age_version();"
```

## 🎯 What You Get

With this custom build, you have:
- **Vector Search**: Semantic similarity search using pgvector
- **Graph Relationships**: Entity relationships using Apache AGE
- **Hybrid Queries**: Combine vector similarity with graph traversal
- **Full Tool-Combo-Chains**: Memory × Sequential × Sandbox with 100x amplification!

## 🔧 Troubleshooting

If the build fails:
1. Make sure Docker has enough resources (8GB RAM recommended)
2. Check Docker Desktop is running with Linux containers
3. Clear Docker cache: `docker system prune -a` (warning: removes all unused images)

## 📊 Build Time
The custom image build takes 5-10 minutes depending on your system. This is normal as it compiles both extensions from source.

## 🎉 Success!
Once built, you have the full cognitive amplification stack that Jordan envisioned!
