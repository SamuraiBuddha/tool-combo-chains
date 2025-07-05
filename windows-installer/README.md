# 🪟 Hybrid Memory Windows Installer

**One-click installer for the Hybrid Memory Cognitive Amplification Stack**

This Windows installer package allows you to easily install and run the Hybrid Memory system with all dependencies automatically managed.

## 🚀 What's Included

- **Hybrid Memory MCP Server** - Core cognitive amplification engine
- **Database Stack** - PostgreSQL + Redis + Qdrant (via Docker)
- **LM Studio Integration** - Uses Granite embeddings on localhost:1234
- **Auto-initialization** - Database schema and dependencies handled automatically
- **Desktop Shortcuts** - Easy access from desktop and Start Menu
- **Uninstaller** - Clean removal when needed

## 📋 Prerequisites

Before installing, make sure you have:

1. **Docker Desktop** - [Download here](https://www.docker.com/products/docker-desktop)
2. **Python 3.8+** - [Download here](https://www.python.org/downloads/)
3. **LM Studio** - [Download here](https://lmstudio.ai/) with Granite model loaded
4. **Git** (recommended) - [Download here](https://git-scm.com/downloads)

The installer will check for these dependencies and prompt you if any are missing.

## 🔧 Building the Installer

### Requirements
- **NSIS** (Nullsoft Scriptable Install System) - [Download here](https://nsis.sourceforge.io/Download)
- Windows 10/11 with PowerShell

### Build Steps

1. **Clone the repository:**
   ```bash
   git clone https://github.com/SamuraiBuddha/tool-combo-chains.git
   cd tool-combo-chains/windows-installer
   ```

2. **Install NSIS:**
   - Download and install NSIS
   - Add NSIS to your system PATH

3. **Build the installer:**
   ```cmd
   build_installer.bat
   ```

The build script will:
- ✅ Generate application icon
- ✅ Compile NSIS installer 
- ✅ Create `HybridMemory_Setup.exe`
- ✅ Optionally code-sign (if certificate available)

## 📦 Installation Process

1. **Run the installer:**
   ```cmd
   HybridMemory_Setup.exe
   ```

2. **Follow the installation wizard:**
   - Welcome screen
   - Choose installation directory
   - Dependency verification
   - File installation
   - Shortcut creation

3. **Launch Hybrid Memory:**
   - Use desktop shortcut, OR
   - Start Menu → Hybrid Memory Cognitive Stack
   - The launcher will automatically:
     - Start Docker containers
     - Initialize database schema
     - Launch MCP server
     - Open in your default browser

## 🎯 What Happens When You Launch

```
[1/5] Checking Docker status...
✓ Docker is running

[2/5] Cleaning up existing containers...  
✓ Cleaned up existing containers

[3/5] Starting database services...
✓ Database services started

[4/5] Waiting for services to initialize...
✓ Services ready

[5/5] Initializing database schema...
✓ Database schema initialized

========================================
  STARTING HYBRID MEMORY MCP SERVER
========================================

Server will start at: http://localhost:8080
Log files: logs/hybrid-memory.log

To stop: Press Ctrl+C or close this window
```

## 🔧 Configuration

### LM Studio Setup
1. Install and start LM Studio
2. Load the Granite embeddings model
3. Enable API server on port 1234
4. The installer automatically connects to `http://localhost:1234/v1/embeddings`

### Claude Desktop Integration
After installation, add to your Claude Desktop config:
```json
{
  "mcpServers": {
    "hybrid-memory": {
      "command": "python",
      "args": ["-m", "tool_combo_chains.mcp_hybrid_memory"],
      "cwd": "C:\\Program Files\\Hybrid Memory Cognitive Stack"
    }
  }
}
```

## 📂 Installation Structure

```
C:\Program Files\Hybrid Memory Cognitive Stack\
├── start_hybrid_memory.bat      # Main launcher
├── hybrid_memory_icon.ico       # Application icon
├── docker-compose.yml           # Container configuration
├── tool_combo_chains/           # Python package
│   └── mcp_hybrid_memory.py     # MCP server
├── docker/                      # Docker configurations
│   └── init-db.sql              # Database schema
├── logs/                        # Application logs
└── uninstall.exe               # Uninstaller
```

## 🗑️ Uninstalling

1. **Via Control Panel:**
   - Settings → Apps → Hybrid Memory Cognitive Stack → Uninstall

2. **Via Start Menu:**
   - Start Menu → Hybrid Memory Cognitive Stack → Uninstall

3. **Manual:**
   - Run `uninstall.exe` from installation directory

The uninstaller will:
- Stop all Docker containers
- Remove all files and shortcuts
- Clean registry entries
- Preserve Docker images (for faster reinstall)

## 🐛 Troubleshooting

### Common Issues

**"Docker is not running"**
- Start Docker Desktop
- Wait for it to fully initialize
- Try launching again

**"Python not found"**
- Install Python 3.8+ from python.org
- Ensure Python is added to PATH during installation

**"Database connection failed"**
- Check Docker containers: `docker ps`
- Restart Docker Desktop
- Run: `docker-compose down && docker-compose up -d`

**"LM Studio connection failed"**
- Start LM Studio
- Load Granite model
- Enable API server (port 1234)
- Check firewall settings

### Debug Mode
To run with detailed logging:
```cmd
cd "C:\Program Files\Hybrid Memory Cognitive Stack"
set DEBUG=1
start_hybrid_memory.bat
```

### Log Files
- Application logs: `logs/hybrid-memory.log`
- Docker logs: `docker-compose logs`

## 🔧 Advanced Configuration

### Environment Variables
Set these in your system environment:
- `DATABASE_URL` - Custom PostgreSQL connection
- `REDIS_URL` - Custom Redis connection  
- `QDRANT_URL` - Custom Qdrant connection
- `EMBEDDING_API_URL` - Custom embedding service

### Custom Docker Configuration
Edit `docker-compose.yml` to customize:
- Database passwords
- Port mappings
- Resource limits
- Volume mounts

## 🤝 Support

- **Issues:** [GitHub Issues](https://github.com/SamuraiBuddha/tool-combo-chains/issues)
- **Documentation:** [Full Documentation](https://github.com/SamuraiBuddha/tool-combo-chains)
- **Updates:** [Releases](https://github.com/SamuraiBuddha/tool-combo-chains/releases)

## 📜 License

MIT License - see LICENSE file for details.

---

**Built for MAGI Architecture by Jordan Ehrig**  
*Ehrig BIM & IT Consultation Inc*

🧠 **Ready for 100x cognitive amplification!**
