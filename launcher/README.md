# Tool-Combo-Chains Desktop Launcher

## 🚀 Quick Start
1. **Copy the launcher folder** to your tool-combo-chains directory
2. **Create a shortcut** to `Start-HybridMemory.bat` on your desktop
3. **Double-click** the shortcut to launch everything!

## 📁 Creating Desktop Shortcuts

### For Start Launcher:
1. Navigate to `tool-combo-chains/launcher/`
2. Right-click on `Start-HybridMemory.bat`
3. Select "Create shortcut"
4. Move the shortcut to your Desktop
5. Rename to "🚀 Start Hybrid Memory"

### For Stop Launcher:
1. Same process with `Stop-HybridMemory.bat`
2. Rename to "🛑 Stop Hybrid Memory"

## 🎨 Customizing Icons
1. Right-click the shortcut
2. Select Properties
3. Click "Change Icon"
4. Browse to a nice .ico file or select from system icons

## ⚙️ What It Does

The **Start** launcher:
- ✅ Checks if Docker Desktop is running (starts it if not)
- ✅ Navigates to your tool-combo-chains directory
- ✅ Runs `docker-compose up -d` to start containers
- ✅ Verifies each container is healthy
- ✅ Shows connection info for all services
- ✅ Optionally launches Claude Desktop

The **Stop** launcher:
- 🛑 Gracefully stops all containers
- 🛑 Preserves your data (volumes remain intact)

## 📊 Services Started
- **cognitive-postgres** - PostgreSQL with pgvector + Apache AGE
- **cognitive-redis** - Redis caching layer
- **cognitive-qdrant** - Vector database

## 🔧 Troubleshooting

If containers don't start:
1. Make sure Docker Desktop is installed
2. Check that you're in the right directory
3. Run `docker-compose ps` to see status
4. Check `docker-compose logs` for errors

## 🎯 Pro Tips
- The containers will keep running even after closing the PowerShell window
- Use the Stop launcher to cleanly shut down when done
- Your data is preserved between restarts

Remember: **Memory × Sequential × Sandbox = 100x!** 🚀