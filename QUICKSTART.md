# Quick Start Guide

## Prerequisites
- Python 3.8+
- Docker Desktop
- LM Studio (for embeddings) or OpenAI API key
- Git

## Installation (5 minutes)

1. **Clone the repository**
   ```bash
   git clone https://github.com/SamuraiBuddha/tool-combo-chains.git
   cd tool-combo-chains
   ```

2. **Run the installer** (Windows)
   ```bash
   install.bat
   ```
   
   Or manually:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   # source venv/bin/activate  # On Mac/Linux
   pip install -e .
   ```

3. **Configure environment**
   ```bash
   copy .env.example .env
   # Edit .env with your settings
   ```

4. **Start the services**
   ```bash
   docker-compose up -d
   ```

5. **Initialize the database**
   ```bash
   scripts\init-db.sh  # On Windows, use Git Bash
   ```

## Claude Desktop Configuration

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "hybrid-memory": {
      "command": "python",
      "args": ["-m", "tool_combo_chains"],
      "cwd": "C:\\Users\\jordanehrig\\Documents\\GitHub\\tool-combo-chains",
      "env": {
        "DATABASE_URL": "postgresql://cognitive:cognitive_secure_password@localhost:5432/cognitive",
        "REDIS_URL": "redis://localhost:6379",
        "QDRANT_URL": "http://localhost:6333",
        "EMBEDDING_API_URL": "http://localhost:1234/v1/embeddings",
        "INSTANCE_ID": "Melchior-001"
      }
    }
  }
}
```

## Test the System

1. **Restart Claude Desktop**

2. **Check if the tool is available**
   - Look for "hybrid-memory" in your MCP tools

3. **Test basic operations**
   ```
   Store a memory: "Remember that Jordan is building Tool Combo Chains"
   Recall memory: "What is Jordan building?"
   ```

## Architecture Overview

```
Your Query
    ↓
Redis Cache (0.1ms)
    ↓ (cache miss)
Qdrant Vector Search (5ms)
    ↓
PostgreSQL Graph Expansion (10ms)
    ↓
Redis Cache Write
    ↓
Response
```

## Available Tools

- **store_memory**: Store entities with embeddings and relationships
- **recall_memory**: Hybrid vector-graph search
- **add_observations**: Append to existing memories
- **create_relationship**: Link entities together
- **find_patterns**: Discover clusters in your data
- **get_memory_stats**: System health and statistics

## Performance Tips

1. **Embeddings**: Keep LM Studio running for best performance
2. **Cache**: Redis handles repeated queries instantly
3. **Batch operations**: Store related memories together
4. **Graph depth**: Limit expansion for faster queries

## Troubleshooting

### MCP not appearing in Claude
- Check logs: `%APPDATA%\Claude\logs\`
- Verify Python path is correct
- Ensure all services are running: `docker ps`

### Connection errors
- Test PostgreSQL: `psql -U cognitive -h localhost`
- Check Redis: `docker exec cognitive-redis redis-cli ping`
- Verify Qdrant: http://localhost:6333/dashboard

### Slow embeddings
- Ensure LM Studio is running
- Check model is loaded (Granite recommended)
- Verify API endpoint: http://localhost:1234/v1/embeddings

## Next Steps

1. **Explore the architecture**: Read the full README
2. **Build more MCPs**: Pattern analyzer, consensus validator
3. **Integrate with existing tools**: MCP Orchestrator compatibility
4. **Scale up**: Multi-instance MAGI coordination

## Support

- Issues: https://github.com/SamuraiBuddha/tool-combo-chains/issues
- Discussions: Start a discussion in the repo
- Direct: Jordan Ehrig (jordan@ebicinc.com)

---

*"We spent weeks inventing PostgreSQL!"* - But now we have something better: Tool Combo Chains! 🚀
