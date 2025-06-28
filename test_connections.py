import asyncio
import asyncpg
import socket

async def test_connection():
    password = '7HY25Pvj5FAW9sH8nJ8MNc4MRnwLnHIQppSFf7aH'
    
    # Test different connection methods
    configs = [
        {
            "name": "127.0.0.1 URL",
            "url": f"postgresql://cognitive:{password}@127.0.0.1:5432/cognitive"
        },
        {
            "name": "localhost URL", 
            "url": f"postgresql://cognitive:{password}@localhost:5432/cognitive"
        },
        {
            "name": "Docker IP",
            "url": f"postgresql://cognitive:{password}@host.docker.internal:5432/cognitive"
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
            conn = await asyncpg.connect(config['url'])
            version = await conn.fetchval('SELECT version()')
            print(f"✅ SUCCESS! Connected via {config['name']}")
            print(f"Version: {version}")
            await conn.close()
            break  # If one works, we found the solution
        except Exception as e:
            print(f"❌ Failed: {e}")
    
    # Test with explicit DSN parameters
    print("\n=== Testing explicit DSN ===")
    try:
        conn = await asyncpg.connect(
            dsn=f"postgresql://cognitive:{password}@127.0.0.1:5432/cognitive"
        )
        print("✅ DSN connection works!")
        await conn.close()
    except Exception as e:
        print(f"❌ DSN failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_connection())
