import asyncio
import asyncpg
import os
import sys
from dotenv import load_dotenv

load_dotenv()

async def test_detailed():
    print("=== Environment Check ===")
    print(f"Python: {sys.version}")
    print(f"asyncpg: {asyncpg.__version__}")
    
    DATABASE_URL = os.getenv("DATABASE_URL")
    print(f"\nDATABASE_URL: {DATABASE_URL}")
    
    # Test 1: Try with DSN
    print("\n=== Test 1: DSN Connection ===")
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        print("✅ DSN connection successful!")
        await conn.close()
    except Exception as e:
        print(f"❌ DSN failed: {e}")
        print(f"Error type: {type(e)}")
        
    # Test 2: Try with individual parameters
    print("\n=== Test 2: Individual Parameters ===")
    try:
        conn = await asyncpg.connect(
            host='127.0.0.1',
            port=5432,
            user='cognitive',
            password='7HY25Pvj5FAW9sH8nJ8MNc4MRnwLnHIQppSFf7aH',
            database='cognitive'
        )
        print("✅ Individual parameters successful!")
        await conn.close()
    except Exception as e:
        print(f"❌ Individual parameters failed: {e}")
        
    # Test 3: Try different SSL modes
    print("\n=== Test 3: SSL Mode Tests ===")
    for ssl_mode in ['disable', 'prefer', 'require']:
        try:
            dsn = f"{DATABASE_URL}?sslmode={ssl_mode}"
            conn = await asyncpg.connect(dsn)
            print(f"✅ SSL mode '{ssl_mode}' successful!")
            await conn.close()
            break
        except Exception as e:
            print(f"❌ SSL mode '{ssl_mode}' failed: {e}")
            
    # Test 4: Try with server_settings
    print("\n=== Test 4: Server Settings ===")
    try:
        conn = await asyncpg.connect(
            host='127.0.0.1',
            port=5432,
            user='cognitive',
            password='7HY25Pvj5FAW9sH8nJ8MNc4MRnwLnHIQppSFf7aH',
            database='cognitive',
            server_settings={'client_encoding': 'UTF8'}
        )
        print("✅ Server settings successful!")
        await conn.close()
    except Exception as e:
        print(f"❌ Server settings failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_detailed())
