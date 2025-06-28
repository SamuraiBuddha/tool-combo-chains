import asyncio
import asyncpg
import urllib.parse

async def debug_connection():
    password = '7HY25Pvj5FAW9sH8nJ8MNc4MRnwLnHIQppSFf7aH'
    
    print("=== Testing Different Connection Methods ===")
    
    # Method 1: Direct parameters (most reliable)
    print("\n1. Testing with direct parameters...")
    try:
        conn = await asyncpg.connect(
            host='127.0.0.1',
            port=5432,
            user='cognitive',
            password=password,
            database='cognitive'
        )
        version = await conn.fetchval('SELECT version()')
        print(f"✅ SUCCESS with direct parameters!")
        print(f"Version: {version}")
        await conn.close()
    except Exception as e:
        print(f"❌ Failed: {e}")
    
    # Method 2: URL with encoded password
    print("\n2. Testing with URL-encoded password...")
    encoded_password = urllib.parse.quote(password, safe='')
    url = f"postgresql://cognitive:{encoded_password}@127.0.0.1:5432/cognitive"
    print(f"URL: postgresql://cognitive:[HIDDEN]@127.0.0.1:5432/cognitive")
    try:
        conn = await asyncpg.connect(url)
        print("✅ SUCCESS with URL encoding!")
        await conn.close()
    except Exception as e:
        print(f"❌ Failed: {e}")
    
    # Method 3: DSN format
    print("\n3. Testing with DSN...")
    dsn = f"postgresql://cognitive:{password}@127.0.0.1:5432/cognitive"
    try:
        conn = await asyncpg.connect(dsn=dsn)
        print("✅ SUCCESS with DSN!")
        await conn.close()
    except Exception as e:
        print(f"❌ Failed: {e}")
    
    # Method 4: Check asyncpg version
    print("\n=== Environment Info ===")
    print(f"asyncpg version: {asyncpg.__version__}")

if __name__ == "__main__":
    asyncio.run(debug_connection())
