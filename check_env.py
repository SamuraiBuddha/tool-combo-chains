import sys
import importlib.util

print(f"Python executable: {sys.executable}")
print(f"Python version: {sys.version}")
print(f"Python path: {sys.path[0]}")

# Check if we're in a venv
print(f"\nVirtual environment: {sys.prefix != sys.base_prefix}")
if sys.prefix != sys.base_prefix:
    print(f"Venv location: {sys.prefix}")

# Check for asyncpg
spec = importlib.util.find_spec("asyncpg")
if spec:
    import asyncpg
    print(f"\nasyncpg found: {spec.origin}")
    print(f"asyncpg version: {asyncpg.__version__}")
else:
    print("\n❌ asyncpg NOT FOUND! Install with: pip install asyncpg")

# Check other dependencies
for pkg in ["dotenv", "redis", "qdrant_client", "httpx", "structlog"]:
    spec = importlib.util.find_spec(pkg)
    print(f"{pkg}: {'✅ Found' if spec else '❌ NOT FOUND'}")
