import psycopg2

password = '7HY25Pvj5FAW9sH8nJ8MNc4MRnwLnHIQppSFf7aH'

print("Testing with psycopg2 (synchronous)...")

try:
    # Test with connection string
    conn_string = f"postgresql://cognitive:{password}@127.0.0.1:5432/cognitive"
    print(f"Connection string: {conn_string}")
    
    conn = psycopg2.connect(conn_string)
    cur = conn.cursor()
    cur.execute("SELECT version()")
    version = cur.fetchone()[0]
    print(f"✅ SUCCESS with psycopg2!")
    print(f"Version: {version}")
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"❌ psycopg2 failed: {e}")
    
    # Try with explicit parameters
    print("\nTrying with explicit parameters...")
    try:
        conn = psycopg2.connect(
            host="127.0.0.1",
            port=5432,
            database="cognitive",
            user="cognitive",
            password=password
        )
        print("✅ Explicit parameters work with psycopg2!")
        conn.close()
    except Exception as e2:
        print(f"❌ Explicit parameters also failed: {e2}")
