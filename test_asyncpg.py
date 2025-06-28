import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def test_connection():
    DATABASE_URL = os.getenv("DATABASE_URL")
    print(f"DATABASE_URL: {DATABASE_URL}")
    
    try:
        # Test 1: Direct connection
        print("\n1. Testing direct connection...")
        conn = await asyncpg.connect(DATABASE_URL)
        version = await conn.fetchval('SELECT version()')
        print(f"✅ Direct connection successful!")
        print(f"PostgreSQL: {version}")
        await conn.close()
        
        # Test 2: Pool connection (like the MCP server uses)
        print("\n2. Testing pool connection...")
        pool = await asyncpg.create_pool(DATABASE_URL, min_size=1, max_size=2)
        async with pool.acquire() as conn:
            result = await conn.fetchval('SELECT 1')
            print(f"✅ Pool connection successful! Result: {result}")
        await pool.close()
        
    except Exception as e:
        print(f"❌ Connection failed: {type(e).__name__}: {e}")
        
        # Try with explicit parameters
        print("\n3. Testing with explicit parameters...")
        try:
            conn = await asyncpg.connect(
                host='127.0.0.1',
                port=5432,
                user='cognitive',
                password='7HY25Pvj5FAW9sH8nJ8MNc4MRnwLnHIQppSFf7aH',
                database='cognitive'
            )
            print("✅ Explicit parameters work!")
            await conn.close()
        except Exception as e2:
            print(f"❌ Explicit parameters also failed: {e2}")

if __name__ == "__main__":
    asyncio.run(test_connection())
