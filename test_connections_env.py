import asyncio
import asyncpg
import socket
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

async def test_connection():
    # Get password from environment or use the known password
    password = os.getenv('POSTGRES_PASSWORD', '7HY25Pvj5FAW9sH8nJ8MNc4MRnwLnHIQppSFf7aH')
    
    print(f"Using password from env: {'YES' if os.getenv('POSTGRES_PASSWORD') else 'NO (using default)'}")
    
    # Test different connection methods
    configs = [
        {
            "name": "127.0.0.1 Direct Parameters",
            "method": "params",
            "params": {
                "host": "127.0.0.1",
                "port": 5432,
                "user": "cognitive",
                "password": password,
                "database": "cognitive"
            }
        },
        {
            "name": "localhost Direct Parameters", 
            "method": "params",
            "params": {
                "host": "localhost",
                "port": 5432,
                "user": "cognitive",
                "password": password,
                "database": "cognitive"
            }
        },
        {
            "name": "DATABASE_URL from env",
            "method": "url",
            "url": os.getenv('DATABASE_URL', f'postgresql://cognitive:{password}@127.0.0.1:5432/cognitive')
        }
    ]
    
    # Test hostname resolution
    print("=== Hostname Resolution ===")
    try:
        print(f"localhost resolves to: {socket.gethostbyname('localhost')}")
        print(f"127.0.0.1 resolves to: {socket.gethostbyname('127.0.0.1')}")
    except Exception as e:
        print(f"Resolution error: {e}")
    
    print("\n=== Connection Tests ===")
    for config in configs:
        print(f"\nTesting {config['name']}...")
        try:
            if config['method'] == 'params':
                conn = await asyncpg.connect(**config['params'])
            else:
                conn = await asyncpg.connect(config['url'])
            
            version = await conn.fetchval('SELECT version()')
            print(f"✅ SUCCESS! Connected via {config['name']}")
            print(f"Version: {version}")
            
            # Test a simple query
            result = await conn.fetchval('SELECT current_user')
            print(f"Current user: {result}")
            
            await conn.close()
            break  # If one works, we found the solution
        except Exception as e:
            print(f"❌ Failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_connection())
