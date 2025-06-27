# Claude Desktop Configuration

Add this to your `claude_desktop_config.json` file to enable the Tool Combo Chains MCP servers.

## Windows Location
`%APPDATA%\Claude\claude_desktop_config.json`

## macOS Location  
`~/Library/Application Support/Claude/claude_desktop_config.json`

## Linux Location
`~/.config/claude/claude_desktop_config.json`

## Configuration to Add

```json
{
  "mcpServers": {
    "hybrid-memory": {
      "command": "python",
      "args": ["-m", "tool_combo_chains.mcp_hybrid_memory"],
      "cwd": "C:\\Users\\SamuraiBuddha\\Documents\\GitHub\\tool-combo-chains",
      "env": {
        "DATABASE_URL": "postgresql://cognitive:cognitive_secure_password@localhost:5432/cognitive",
        "REDIS_URL": "redis://localhost:6379",
        "QDRANT_URL": "http://localhost:6333",
        "EMBEDDING_API_URL": "http://localhost:1234/v1/embeddings",
        "INSTANCE_ID": "Caspar-001",
        "LOG_LEVEL": "INFO"
      }
    },
    "pattern-analyzer": {
      "command": "python", 
      "args": ["-m", "tool_combo_chains.mcp_pattern_analyzer"],
      "cwd": "C:\\Users\\SamuraiBuddha\\Documents\\GitHub\\tool-combo-chains",
      "env": {
        "DATABASE_URL": "postgresql://cognitive:cognitive_secure_password@localhost:5432/cognitive",
        "QDRANT_URL": "http://localhost:6333"
      }
    },
    "cognitive-sandbox": {
      "command": "node",
      "args": ["C:\\Users\\SamuraiBuddha\\Documents\\GitHub\\tool-combo-chains\\servers\\cognitive-sandbox\\index.js"],
      "env": {
        "REDIS_URL": "redis://localhost:6379",
        "MAX_EXECUTION_TIME": "30000",
        "MEMORY_LIMIT": "512M"
      }
    }
  }
}
```

## For Multiple Claude Instances (MAGI)

### Melchior (CAD/3D Focus)
```json
"env": {
  "INSTANCE_ID": "Melchior-001",
  "INSTANCE_ROLE": "cad_specialist"
}
```

### Balthasar (AI/LLM Focus)  
```json
"env": {
  "INSTANCE_ID": "Balthasar-001", 
  "INSTANCE_ROLE": "ai_specialist"
}
```

### Caspar (Code/Data Focus)
```json
"env": {
  "INSTANCE_ID": "Caspar-001",
  "INSTANCE_ROLE": "code_specialist"
}
```

## Notes

1. **Update the paths** to match your actual installation location
2. **Update DATABASE_URL** with your actual PostgreSQL password
3. **Ensure services are running** before starting Claude:
   ```bash
   docker-compose up -d
   ```
4. **Install the Python package** first:
   ```bash
   cd tool-combo-chains
   pip install -e .
   ```
5. **Restart Claude Desktop** after editing the config

## Verification

After restarting Claude, you should see:
- "hybrid-memory" in the MCP tools list
- Ability to use tool combo chains
- Multi-tier memory operations

## Troubleshooting

If the MCP doesn't appear:
1. Check Claude's logs: `%APPDATA%\Claude\logs\`
2. Verify all services are running: `docker ps`
3. Test database connection: `psql -U cognitive -h localhost -d cognitive`
4. Ensure Python/Node are in PATH
